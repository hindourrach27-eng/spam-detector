"""
Étape 3 : Analyse des critères spam
Vérifier chaque email pour détecter les indicateurs de spam
"""

import csv
import json
import re
import socket
from pathlib import Path

# 3F - Mots suspects dans l'objet
MOTS_SUSPECTS = [
    'gagner', 'gagnez', 'prix', 'gratuit', 'urgent', 'action requise',
    'cliquez', 'confirmer', 'vérifier', 'compte', 'carte bancaire',
    'paypal', 'amazon', 'apple', 'microsoft', 'gouvernement',
    'impôts', 'remboursement', 'urgent', 'immédiat', 'limité',
    'promotion', 'offre spéciale', 'dernier jour', 'expire', 'bientôt',
    'cliquez ici', 'réclame', 'argent', 'bitcoin', 'crypto',
    'travail à domicile', 'revenu rapide', 'enrichissez-vous',
    're:', 'fwd:', 'you have', 'click here', 'verify account',
    'update payment', 'suspended', 'locked', 'compromised'
]

# 3G - Domaines suspects (blacklistés connus)
DOMAINES_SUSPECTS = [
    'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'buff.ly',
    'is.gd', 'short.link', '000webhostapp.com',
    'github.io', 'blogspot.com', 'wordpress.com'
]

class SpamAnalyzer:
    """Analyseur de spam pour les emails"""
    
    def __init__(self):
        self.spamhaus_ips = self._load_known_spam_ips()
    
    def _load_known_spam_ips(self):
        """Charger une liste de base d'IPs connues comme spam"""
        # IPs de test/exemples connus
        return [
            '127.0.0.2', '127.0.0.3', '127.0.0.4',  # Spamhaus test IPs
            '192.0.2.1', '198.51.100.1', '203.0.113.1',  # Documentation IPs
        ]
    
    def check_ip_blacklisted(self, ip):
        """3B - Vérifier si l'IP est blacklistée"""
        if not ip:
            return False, 'IP manquante'
        
        # Vérification avec la liste locale
        if ip in self.spamhaus_ips:
            return True, 'IP dans la liste noire'
        
        # Essayer une vérification DNSBL simple (Spamhaus)
        try:
            # Format: lookup.spamhaus.org = X.X.X.{2-3}
            # Exemple: check 192.168.1.1 against Spamhaus
            octets = ip.split('.')
            if len(octets) != 4:
                return False, 'IP invalide'
            
            # Inverse l'IP
            reversed_ip = '.'.join(reversed(octets))
            query = f"{reversed_ip}.zen.spamhaus.org"
            
            try:
                socket.gethostbyname(query)
                return True, 'Détecté par Spamhaus'
            except socket.gaierror:
                # IP non trouvée dans Spamhaus = pas de problème
                return False, 'OK (Spamhaus)'
        except Exception as e:
            return False, f'Vérification échouée ({str(e)[:30]})'
    
    def check_spf_valid(self, spf_status):
        """3C - Vérifier si SPF est valide"""
        if not spf_status or spf_status == 'Unknown':
            return False, 'SPF absent ou invalide'
        
        if spf_status == 'pass':
            return True, 'SPF valide'
        elif spf_status in ['fail', 'softfail', 'neutral']:
            return False, f'SPF échoué ({spf_status})'
        else:
            return False, f'SPF inconnu ({spf_status})'
    
    def check_dkim_valid(self, dkim_status):
        """3D - Vérifier si DKIM est valide"""
        if not dkim_status or dkim_status == 'Unknown':
            return False, 'DKIM absent ou invalide'
        
        if dkim_status == 'pass':
            return True, 'DKIM valide'
        elif dkim_status == 'fail':
            return False, 'DKIM échoué'
        else:
            return False, f'DKIM inconnu ({dkim_status})'
    
    def check_dmarc_valid(self, dmarc_status=''):
        """3E - Vérifier si DMARC est valide"""
        if not dmarc_status:
            return False, 'DMARC absent'
        
        if 'pass' in dmarc_status.lower():
            return True, 'DMARC valide'
        elif 'fail' in dmarc_status.lower():
            return False, 'DMARC échoué'
        else:
            return False, 'DMARC absent ou invalide'
    
    def check_subject_spam_words(self, subject):
        """3F - Analyser l'objet du mail pour les mots suspects"""
        if not subject:
            return [], 0
        
        subject_lower = subject.lower()
        mots_trouves = []
        
        for mot in MOTS_SUSPECTS:
            if mot.lower() in subject_lower:
                mots_trouves.append(mot)
        
        # Score: 1 point par mot suspect trouvé
        score = len(mots_trouves)
        
        return mots_trouves, score
    
    def check_links_suspicious(self, liens_str):
        """3G - Analyser les liens pour détecter les domaines suspects"""
        if not liens_str:
            return [], 0
        
        liens = [l.strip() for l in liens_str.split(';') if l.strip()]
        liens_suspects = []
        score = 0
        
        for lien in liens:
            # Extraire le domaine
            try:
                # Supprimer https:// ou http://
                url = lien.replace('https://', '').replace('http://', '').split('/')[0]
                
                # Vérifier les domaines suspects
                for domaine_suspect in DOMAINES_SUSPECTS:
                    if domaine_suspect in url:
                        liens_suspects.append(lien[:50])
                        score += 1
                        break
            except:
                pass
        
        return liens_suspects, score
    
    def calculate_spam_score(self, email_data, analysis_results):
        """Calculer un score de spam global (0-100)"""
        score = 0
        
        # IP blacklistée: +30 points
        if analysis_results['ip_blacklistee']:
            score += 30
        
        # SPF non valide: +20 points
        if not analysis_results['spf_valide']:
            score += 20
        
        # DKIM non valide: +20 points
        if not analysis_results['dkim_valide']:
            score += 20
        
        # DMARC non valide: +15 points
        if not analysis_results['dmarc_valide']:
            score += 15
        
        # Mots suspects: +5 points par mot
        score += analysis_results['score_mots_suspects'] * 5
        
        # Liens suspects: +10 points par lien
        score += analysis_results['score_liens_suspects'] * 10
        
        # Limiter à 100
        score = min(score, 100)
        
        return score
    
    def analyze_email(self, email_data):
        """Analyser un email complet"""
        results = {
            'id': email_data['id'],
            'label': email_data['label'],
            
            # 3B - IP blacklistée
            'ip_blacklistee': False,
            'raison_ip': 'OK',
            
            # 3C - SPF
            'spf_valide': False,
            'raison_spf': 'SPF absent',
            
            # 3D - DKIM
            'dkim_valide': False,
            'raison_dkim': 'DKIM absent',
            
            # 3E - DMARC
            'dmarc_valide': False,
            'raison_dmarc': 'DMARC absent',
            
            # 3F - Mots suspects
            'mots_suspects': [],
            'score_mots_suspects': 0,
            
            # 3G - Liens suspects
            'liens_suspects': [],
            'score_liens_suspects': 0,
        }
        
        # 3B - IP
        is_blacklisted, reason = self.check_ip_blacklisted(email_data.get('ip', ''))
        results['ip_blacklistee'] = is_blacklisted
        results['raison_ip'] = reason
        
        # 3C - SPF
        spf_valid, reason = self.check_spf_valid(email_data.get('spf', 'Unknown'))
        results['spf_valide'] = spf_valid
        results['raison_spf'] = reason
        
        # 3D - DKIM
        dkim_valid, reason = self.check_dkim_valid(email_data.get('dkim', 'Unknown'))
        results['dkim_valide'] = dkim_valid
        results['raison_dkim'] = reason
        
        # 3E - DMARC (généralement pas dans les headers, donc toujours absent)
        dmarc_valid, reason = self.check_dmarc_valid('')
        results['dmarc_valide'] = dmarc_valid
        results['raison_dmarc'] = reason
        
        # 3F - Mots suspects dans l'objet
        mots, score = self.check_subject_spam_words(email_data.get('objet', ''))
        results['mots_suspects'] = ', '.join(mots) if mots else ''
        results['score_mots_suspects'] = score
        
        # 3G - Liens suspects
        liens, score = self.check_links_suspicious(email_data.get('liens', ''))
        results['liens_suspects'] = ', '.join(liens) if liens else ''
        results['score_liens_suspects'] = score
        
        # Calculer le score de spam
        results['score_spam'] = self.calculate_spam_score(email_data, results)
        
        # Classification
        if results['score_spam'] >= 70:
            results['classification'] = 'SPAM'
        elif results['score_spam'] >= 40:
            results['classification'] = 'SUSPECT'
        else:
            results['classification'] = 'LEGITIME'
        
        return results


def analyze_dataset(input_file='dataset_emails.csv', output_csv='dataset_analyse.csv', output_json='dataset_analyse.json'):
    """3H - Analyser le dataset complet"""
    print("=" * 70)
    print("🔍 Analyse des critères spam - Étape 3")
    print("=" * 70)
    
    analyzer = SpamAnalyzer()
    analyzed_emails = []
    
    try:
        # Lire le dataset
        print(f"\n📖 Lecture de {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            emails = list(reader)
        
        print(f"   ✅ {len(emails)} emails trouvés")
        
        # Analyser chaque email
        print(f"\n🔍 Analyse en cours...")
        for idx, email in enumerate(emails, 1):
            result = analyzer.analyze_email(email)
            analyzed_emails.append(result)
            
            if idx % 5 == 0:
                print(f"   [{idx}/{len(emails)}] emails analysés...")
        
        print(f"   ✅ Analyse complétée")
        
        # Statistiques
        spam_count = sum(1 for e in analyzed_emails if e['classification'] == 'SPAM')
        suspect_count = sum(1 for e in analyzed_emails if e['classification'] == 'SUSPECT')
        legit_count = sum(1 for e in analyzed_emails if e['classification'] == 'LEGITIME')
        
        print(f"\n📊 Résultats :")
        print(f"   - SPAM: {spam_count}")
        print(f"   - SUSPECT: {suspect_count}")
        print(f"   - LÉGITIME: {legit_count}")
        
        # Sauvegarder en CSV
        print(f"\n💾 Sauvegarde en CSV ({output_csv})...")
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'label', 'classification', 'score_spam',
                'ip_blacklistee', 'raison_ip',
                'spf_valide', 'raison_spf',
                'dkim_valide', 'raison_dkim',
                'dmarc_valide', 'raison_dmarc',
                'mots_suspects', 'score_mots_suspects',
                'liens_suspects', 'score_liens_suspects'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analyzed_emails)
        
        print(f"   ✅ {output_csv} créé")
        
        # Sauvegarder en JSON
        print(f"\n💾 Sauvegarde en JSON ({output_json})...")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(analyzed_emails, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ {output_json} créé")
        
        print("\n" + "=" * 70)
        print("✨ Étape 3 réussie !")
        print("=" * 70)
        print(f"\n📁 Fichiers générés :")
        print(f"   • {output_csv}")
        print(f"   • {output_json}")
        print(f"\n📊 Ouvrez '{output_csv}' dans Excel pour voir les résultats !")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ ERREUR : {input_file} introuvable")
        print("   Assurez-vous que l'Étape 2 a été exécutée !")
        return False
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # 3A - Créer le script
    # 3B à 3G - Implémenté dans les méthodes
    # 3H - Analyser et sauvegarder
    
    success = analyze_dataset()
    exit(0 if success else 1)
