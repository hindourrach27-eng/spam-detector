"""
gmail_service.py — Logique de collecte des emails
"""

import base64
import re
from googleapiclient.discovery import build
from gmail_utils import get_gmail_service, refresh_credentials


def get_header_value(headers, field_name):
    for header in headers:
        if header['name'] == field_name:
            return header['value']
    return ''



def extract_ip_from_received(received_header):
    if not received_header:
        return ''

    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    toutes_les_ips = re.findall(ip_pattern, received_header)

    if not toutes_les_ips:
        return ''

    # Plages privees/internes a eviter si possible
    def est_ip_privee(ip):
        return (
            ip.startswith('10.') or
            ip.startswith('127.') or
            ip.startswith('192.168.') or
            ip.startswith('172.16.') or ip.startswith('172.17.') or
            ip.startswith('172.18.') or ip.startswith('172.19.') or
            ip.startswith('172.2') or ip.startswith('172.30.') or ip.startswith('172.31.')
        )

    ips_publiques = [ip for ip in toutes_les_ips if not est_ip_privee(ip)]

    if ips_publiques:
        return ips_publiques[0]

    return toutes_les_ips[0]


def extract_spf_from_header(arc_authentication_results=''):
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
    if not arc_authentication_results:
        return 'Unknown'
    if 'dkim=pass' in arc_authentication_results.lower():
        return 'pass'
    elif 'dkim=fail' in arc_authentication_results.lower():
        return 'fail'
    else:
        return 'Unknown'


def extract_dmarc_from_header(arc_authentication_results=''):
    if not arc_authentication_results:
        return 'Unknown'
    if 'dmarc=pass' in arc_authentication_results.lower():
        return 'pass'
    elif 'dmarc=fail' in arc_authentication_results.lower():
        return 'fail'
    else:
        return 'Unknown'


def extract_body_from_payload(payload):
    """Extraire le corps texte de l'email"""
    try:
        body_text = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
            # Si pas de text/plain, prendre text/html
            if not body_text:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        data = part['body'].get('data', '')
                        if data:
                            body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            break
        else:
            data = payload['body'].get('data', '')
            if data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        # Limiter à 5000 caractères
        return body_text[:5000]
    except:
        return ''


def extract_links_from_body(payload):
    """Extraire les liens (URLs) du corps de l'email"""
    try:
        body_text = extract_body_from_payload(payload)
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(url_pattern, body_text)
        links = links[:3] if links else []
        return '; '.join(links)
    except:
        return ''


def fetch_gmail_labels(service):
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        label_dict = {}
        for label in labels:
            label_dict[label['name']] = label['id']
        return label_dict
    except Exception as e:
        print(f"❌ Erreur fetch_gmail_labels : {e}")
        return {}


def fetch_emails_list(service, label_id, max_results=20):
    try:
        results = service.users().messages().list(
            userId='me',
            labelIds=[label_id],
            maxResults=max_results
        ).execute()
        messages = results.get('messages', [])
        return [msg['id'] for msg in messages]
    except Exception as e:
        print(f"❌ Erreur fetch_emails_list : {e}")
        return []


def extract_email_data(service, msg_id, label_name):
    try:
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()

        headers = msg['payload']['headers']

        from_email = get_header_value(headers, 'From')
        subject = get_header_value(headers, 'Subject')
        # Prendre tous les headers Received et chercher une IP dans chacun
        received_headers = [h['value'] for h in headers if h['name'] == 'Received']
        received = ' '.join(received_headers)


        auth_results = get_all_header_values(headers, 'Authentication-Results')

        ip = extract_ip_from_received(received)
        spf = extract_spf_from_header(auth_results)
        dkim = extract_dkim_from_header(auth_results)
        dmarc = extract_dmarc_from_header(auth_results)
        liens = extract_links_from_body(msg['payload'])
        body = extract_body_from_payload(msg['payload'])
        return {
            'msg_id': msg_id,
            'label': label_name,
            'expediteur': from_email,
            'objet': subject,
            'ip': ip,
            'spf': spf,
            'dkim': dkim,
            'dmarc': dmarc,
            'liens': liens,
            'body': body
        }
    except Exception as e:
        print(f"❌ Erreur extract_email_data : {e}")
        return None


def collect_emails_from_gmail(creds, message_ids, label_name):
    creds = refresh_credentials(creds)
    service = get_gmail_service(creds)
    if not service:
        return []
    emails_data = []
    for idx, msg_id in enumerate(message_ids, 1):
        email_data = extract_email_data(service, msg_id, label_name)
        if email_data:
            emails_data.append(email_data)
    return emails_data

def get_all_header_values(headers, field_name):
    """Recupere et combine TOUS les headers ayant ce nom (pas juste le premier)"""
    values = [h['value'] for h in headers if h['name'] == field_name]
    return ' '.join(values)