"""
Étape 2 : Création du dataset — Collecter les emails Gmail
Extrait 20 emails de INBOX et 20 de SPAM avec analyse des headers
"""

import os.path
import pickle
import csv
import json
import base64
import re
from datetime import datetime
from urllib.parse import urlparse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def load_credentials():
    """Charger les credentials depuis token.json"""
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_header_value(headers, field_name):
    """Récupérer la valeur d'un header"""
    for header in headers:
        if header['name'] == field_name:
            return header['value']
    return ''

def extract_ip_from_received(received_header):
    """Extraire l'IP depuis le header Received"""
    if not received_header:
        return ''
    
    # Chercher les patterns IP
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    match = re.search(ip_pattern, received_header)
    if match:
        return match.group(0)
    return ''

def extract_spf_from_header(arc_authentication_results=''):
    """Extraire le statut SPF du header Authentication-Results"""
    if not arc_authentication_results:
        return 'Unknown'
    
    if 'spf=pass' in arc_authentication_results.lower():
        return 'pass'
    elif 'spf=fail' in arc_authentication_results.lower():
        return 'fail'
    elif 'spf=softfail' in arc_authentication_results.lower():
        return 'softfail'
    elif 'spf=neutral' in arc_authentication_results.lower():
        return 'neutral'
    else:
        return 'Unknown'

def extract_dkim_from_header(arc_authentication_results=''):
    """Extraire le statut DKIM du header Authentication-Results"""
    if not arc_authentication_results:
        return 'Unknown'
    
    if 'dkim=pass' in arc_authentication_results.lower():
        return 'pass'
    elif 'dkim=fail' in arc_authentication_results.lower():
        return 'fail'
    else:
        return 'Unknown'

def extract_links_from_body(payload):
    """Extraire les liens (URLs) du corps de l'email"""
    try:
        body_text = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            data = payload['body'].get('data', '')
            if data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        # Trouver les URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(url_pattern, body_text)
        
        # Limiter à 3 premiers liens
        links = links[:3] if links else []
        
        return '; '.join(links)
    except:
        return ''

def collect_emails_from_label(service, label_name, label_id, max_results=20):
    """Collecter les emails d'un label"""
    emails_data = []
    
    print(f"\n📧 Lecture du dossier '{label_name}' (max {max_results})...")
    
    try:
        # Récupérer les IDs des messages
        results = service.users().messages().list(
            userId='me',
            labelIds=[label_id],
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        total = len(messages)
        print(f"   Trouvé {total} emails")
        
        for idx, message in enumerate(messages, 1):
            msg_id = message['id']
            
            # Récupérer les détails complets
            msg = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            
            # Extraire les informations
            from_email = get_header_value(headers, 'From')
            subject = get_header_value(headers, 'Subject')
            received = get_header_value(headers, 'Received')
            auth_results = get_header_value(headers, 'Authentication-Results')
            
            # Traiter les données
            ip = extract_ip_from_received(received)
            spf = extract_spf_from_header(auth_results)
            dkim = extract_dkim_from_header(auth_results)
            liens = extract_links_from_body(msg['payload'])
            
            emails_data.append({
                'id': msg_id,
                'label': label_name,
                'expediteur': from_email,
                'objet': subject,
                'ip': ip,
                'spf': spf,
                'dkim': dkim,
                'liens': liens
            })
            
            print(f"   [{idx}/{total}] {from_email[:40]}")
        
        print(f"   ✅ {total} emails collectés")
        return emails_data
        
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return []

def save_to_csv(data, filename='dataset_emails.csv'):
    """Sauvegarder en CSV"""
    print(f"\n💾 Sauvegarde en CSV ({filename})...")
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'label', 'expediteur', 'objet', 'ip', 'spf', 'dkim', 'liens']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        
        print(f"   ✅ {filename} créé avec {len(data)} emails")
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def save_to_json(data, filename='dataset_emails.json'):
    """Sauvegarder en JSON"""
    print(f"\n💾 Sauvegarde en JSON ({filename})...")
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"   ✅ {filename} créé avec {len(data)} emails")
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("📊 Création du dataset - Étape 2")
    print("=" * 70)
    
    try:
        # Charger les credentials
        print("\n⏳ Chargement des credentials...")
        creds = load_credentials()
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Credentials chargés")
        
        # Obtenir les labels
        print("\n⏳ Récupération des labels...")
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        inbox_id = None
        spam_id = None
        
        for label in labels:
            if label['name'] == 'INBOX':
                inbox_id = label['id']
            elif label['name'] == 'SPAM':
                spam_id = label['id']
        
        if not inbox_id:
            print("❌ Le label INBOX n'a pas été trouvé")
            exit(1)
        
        print(f"✅ Labels trouvés")
        
        # Collecter les emails
        all_emails = []
        
        # 2B - INBOX (20 emails)
        inbox_emails = collect_emails_from_label(service, 'INBOX', inbox_id, max_results=20)
        all_emails.extend(inbox_emails)
        
        # 2C - SPAM (20 emails) si le label existe
        spam_emails = []
        if spam_id:
            spam_emails = collect_emails_from_label(service, 'SPAM', spam_id, max_results=20)
            all_emails.extend(spam_emails)
        
        # 2E - Sauvegarder en CSV
        csv_ok = save_to_csv(all_emails)
        
        # 2F - Sauvegarder en JSON
        json_ok = save_to_json(all_emails)
        
        # Résumé
        if csv_ok and json_ok:
            print("\n" + "=" * 70)
            print("✨ Étape 2 réussie !")
            print(f"📊 Dataset créé avec {len(all_emails)} emails")
            print(f"   - INBOX: {len(inbox_emails)} emails")
            if spam_emails:
                print(f"   - SPAM: {len(spam_emails)} emails")
            print("\n📁 Fichiers générés :")
            print("   • dataset_emails.csv")
            print("   • dataset_emails.json")
            print("\n2G - Ouvrez 'dataset_emails.csv' dans Excel pour vérifier !")
            print("=" * 70)
        else:
            print("\n❌ Erreur lors de la sauvegarde")
            exit(1)
            
    except FileNotFoundError:
        print("❌ ERREUR : credentials.json ou token.json introuvable")
        exit(1)
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        exit(1)
