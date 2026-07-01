"""
spam_analyzer.py — Analyse des criteres spam (utilise par l'application Flask)
Logique reprise de scripts_origine/step3_analyse.py, avec detection de patterns suspects
"""

import socket
import re

MOTS_SUSPECTS = [
    'gagner', 'gagnez', 'prix', 'gratuit', 'urgent', 'action requise',
    'cliquez', 'confirmer', 'vérifier', 'compte', 'carte bancaire',
    'paypal', 'amazon', 'apple', 'microsoft', 'gouvernement',
    'impôts', 'remboursement', 'urgent', 'immédiat', 'limité',
    'promotion', 'offre spéciale', 'dernier jour', 'expire', 'bientôt',
    'cliquez ici', 'réclame', 'argent', 'bitcoin', 'crypto',
    'travail à domicile', 'revenu rapide', 'enrichissez-vous',
    're:', 'fwd:', 'you have', 'click here', 'verify account',
    'update payment', 'suspended', 'locked', 'compromised',
    'spam', 'loterie', 'héritage', 'gagnant', 'félicitations'
]

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
        return [
            '127.0.0.2', '127.0.0.3', '127.0.0.4',
            '192.0.2.1', '198.51.100.1', '203.0.113.1',
        ]

    def check_ip_blacklisted(self, ip):
        if not ip:
            return False, 'IP manquante'

        if ip in self.spamhaus_ips:
            return True, 'IP dans la liste noire'

        try:
            octets = ip.split('.')
            if len(octets) != 4:
                return False, 'IP invalide'

            reversed_ip = '.'.join(reversed(octets))
            query = f"{reversed_ip}.zen.spamhaus.org"

            try:
                socket.gethostbyname(query)
                return True, 'Détecté par Spamhaus'
            except socket.gaierror:
                return False, 'OK (Spamhaus)'
        except Exception as e:
            return False, f'Vérification échouée ({str(e)[:30]})'

    def check_spf_valid(self, spf_status):
        if not spf_status or spf_status == 'Unknown':
            return False, 'SPF absent ou invalide'

        if spf_status == 'pass':
            return True, 'SPF valide'
        elif spf_status in ['fail', 'softfail', 'neutral']:
            return False, f'SPF échoué ({spf_status})'
        else:
            return False, f'SPF inconnu ({spf_status})'

    def check_dkim_valid(self, dkim_status):
        if not dkim_status or dkim_status == 'Unknown':
            return False, 'DKIM absent ou invalide'

        if dkim_status == 'pass':
            return True, 'DKIM valide'
        elif dkim_status == 'fail':
            return False, 'DKIM échoué'
        else:
            return False, f'DKIM inconnu ({dkim_status})'

    def check_dmarc_valid(self, dmarc_status=''):
        if not dmarc_status:
            return False, 'DMARC absent'

        if 'pass' in dmarc_status.lower():
            return True, 'DMARC valide'
        elif 'fail' in dmarc_status.lower():
            return False, 'DMARC échoué'
        else:
            return False, 'DMARC absent ou invalide'

    def check_subject_spam_words(self, subject):
        """Detecte les mots-cles connus ET les patterns suspects (obfuscation, chiffres, majuscules, ponctuation)"""
        if not subject:
            return [], 0

        indices_trouves = []
        score = 0

        # 1. Mots-cles connus
        subject_lower = subject.lower()
        for mot in MOTS_SUSPECTS:
            if mot.lower() in subject_lower:
                indices_trouves.append(f"mot-cle: {mot}")
                score += 1

        # 2. Caracteres speciaux meles a des lettres (obfuscation, ex: Sp@am)
        if re.search(r'[a-zA-Z]+[@$!*]+[a-zA-Z]+', subject):
            indices_trouves.append("caracteres speciaux meles aux lettres")
            score += 2

        # 3. Chiffres meles aux lettres dans un mot (ex: gagn3z, v1agra)
        if re.search(r'\b[a-zA-Z]+\d+[a-zA-Z]*\b|\b[a-zA-Z]*\d+[a-zA-Z]+\b', subject):
            indices_trouves.append("chiffres meles a des lettres")
            score += 2

        # 4. Majuscules excessives (plus de 50% du texte en majuscules, sur au moins 5 lettres)
        lettres = [c for c in subject if c.isalpha()]
        if len(lettres) >= 5:
            majuscules = sum(1 for c in lettres if c.isupper())
            if majuscules / len(lettres) > 0.5:
                indices_trouves.append("majuscules excessives")
                score += 1

        # 5. Ponctuation repetee (ex: !!!, ???)
        if re.search(r'[!?]{2,}', subject):
            indices_trouves.append("ponctuation repetee")
            score += 1

        # Plafonner le score a 5 pour rester proportionne aux autres criteres
        score = min(score, 5)

        return indices_trouves, score

    def check_links_suspicious(self, liens_str):
        if not liens_str:
            return [], 0

        liens = [l.strip() for l in liens_str.split(';') if l.strip()]
        liens_suspects = []
        score = 0

        for lien in liens:
            try:
                url = lien.replace('https://', '').replace('http://', '').split('/')[0]

                for domaine_suspect in DOMAINES_SUSPECTS:
                    if domaine_suspect in url:
                        liens_suspects.append(lien[:50])
                        score += 1
                        break
            except:
                pass

        return liens_suspects, score

    def count_links(self, liens_str):
        """Compte le nombre de liens (separes par ';')"""
        if not liens_str:
            return 0
        return len([l for l in liens_str.split(';') if l.strip()])

    def check_has_image(self, body):
        """Detecte la presence d'une balise <img> dans le corps de l'email"""
        if not body:
            return 0
        return 1 if re.search(r'<img\b', body, re.IGNORECASE) else 0

    def build_auth_combo(self, spf, dkim, dmarc):
        """Combine SPF/DKIM/DMARC en un seul indicateur lisible"""
        spf = spf or 'unknown'
        dkim = dkim or 'unknown'
        dmarc = dmarc or 'unknown'
        return f"spf={spf},dkim={dkim},dmarc={dmarc}"

    def extract_domain(self, expediteur):
        """Extrait le domaine de l'adresse email de l'expediteur"""
        if not expediteur:
            return ''
        match = re.search(r'@([\w.-]+)', expediteur)
        return match.group(1).lower() if match else ''

    def calculate_spam_score(self, email_data, analysis_results):
        score = 0

        if analysis_results['ip_blacklistee']:
            score += 30

        if not analysis_results['spf_valide']:
            score += 20

        if not analysis_results['dkim_valide']:
            score += 20

        if not analysis_results['dmarc_valide']:
            score += 15

        score += analysis_results['score_mots_suspects'] * 5

        score += analysis_results['score_liens_suspects'] * 10

        score = min(score, 100)

        return score

    def analyze_email(self, email_data):
        """Analyser un email complet"""
        results = {
            'ip_blacklistee': False,
            'raison_ip': 'OK',

            'spf_valide': False,
            'raison_spf': 'SPF absent',

            'dkim_valide': False,
            'raison_dkim': 'DKIM absent',

            'dmarc_valide': False,
            'raison_dmarc': 'DMARC absent',

            'mots_suspects': [],
            'score_mots_suspects': 0,

            'liens_suspects': [],
            'score_liens_suspects': 0,

            'link_count': 0,
            'has_image': 0,
            'text_length': 0,
            'auth_combo': '',

            'domain': '',
        }

        is_blacklisted, reason = self.check_ip_blacklisted(email_data.get('ip', ''))
        results['ip_blacklistee'] = is_blacklisted
        results['raison_ip'] = reason

        spf_valid, reason = self.check_spf_valid(email_data.get('spf', 'Unknown'))
        results['spf_valide'] = spf_valid
        results['raison_spf'] = reason

        dkim_valid, reason = self.check_dkim_valid(email_data.get('dkim', 'Unknown'))
        results['dkim_valide'] = dkim_valid
        results['raison_dkim'] = reason

        dmarc_valid, reason = self.check_dmarc_valid(email_data.get('dmarc', 'Unknown'))
        results['dmarc_valide'] = dmarc_valid
        results['raison_dmarc'] = reason

        mots, score = self.check_subject_spam_words(email_data.get('objet', ''))
        results['mots_suspects'] = ', '.join(mots) if mots else ''
        results['score_mots_suspects'] = score

        liens, score = self.check_links_suspicious(email_data.get('liens', ''))
        results['liens_suspects'] = ', '.join(liens) if liens else ''
        results['score_liens_suspects'] = score

        # Nouvelles colonnes structurees (Phase 4 du plan encadrante)
        results['link_count'] = self.count_links(email_data.get('liens', ''))
        results['has_image'] = self.check_has_image(email_data.get('body', ''))
        results['text_length'] = len(email_data.get('body', '') or '')
        results['auth_combo'] = self.build_auth_combo(
            email_data.get('spf', ''),
            email_data.get('dkim', ''),
            email_data.get('dmarc', '')
        )

        results['domain'] = self.extract_domain(email_data.get('expediteur', ''))

        results['score_spam'] = self.calculate_spam_score(email_data, results)

        if results['score_spam'] >= 70:
            results['classification'] = 'SPAM'
        elif results['score_spam'] >= 40:
            results['classification'] = 'SUSPECT'
        else:
            results['classification'] = 'LEGITIME'

        return results
