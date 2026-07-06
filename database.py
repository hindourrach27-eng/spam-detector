"""
database.py — Gestion de la base SQLite
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = 'spam_detector.db'

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            token TEXT,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER NOT NULL,
            msg_id TEXT NOT NULL,
            label TEXT,
            expediteur TEXT,
            objet TEXT,
            body TEXT,
            ip TEXT,
            spf TEXT,
            dkim TEXT,
            liens TEXT,
            date_collecte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_user) REFERENCES users(id_user),
            UNIQUE(id_user, msg_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER NOT NULL,
            domaine TEXT,
            nom_affiche TEXT,
            sujet TEXT,
            description_offre TEXT,
            spf_ok INTEGER,
            dkim_ok INTEGER,
            dmarc_ok INTEGER,
            verdict TEXT,
            score INTEGER,
            score_explication TEXT,
            label_phishing INTEGER,
            label_spoofing INTEGER,
            label_scam INTEGER,
            label_bulk INTEGER,
            harmful_elements TEXT,
            recommendation TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_user) REFERENCES users(id_user)
        )
    ''')

    # Ajouter colonne body si elle n'existe pas (pour BD existante)
    try:
        cursor.execute('ALTER TABLE emails ADD COLUMN body TEXT')
    except:
        pass

    # Colonnes pour l'analyse spam (ajoutees si elles n'existent pas)
    nouvelles_colonnes = [
        ('score_spam', 'INTEGER'),
        ('classification', 'TEXT'),
        ('ip_blacklistee', 'INTEGER'),
        ('raison_ip', 'TEXT'),
        ('spf_valide', 'INTEGER'),
        ('raison_spf', 'TEXT'),
        ('dkim_valide', 'INTEGER'),
        ('raison_dkim', 'TEXT'),
        ('dmarc_valide', 'INTEGER'),
        ('raison_dmarc', 'TEXT'),
        ('mots_suspects', 'TEXT'),
        ('liens_suspects', 'TEXT'),
        ('dmarc', 'TEXT'),
        ('link_count', 'INTEGER'),
        ('has_image', 'INTEGER'),
        ('text_length', 'INTEGER'),
        ('auth_combo', 'TEXT'),
        ('body_clean', 'TEXT'),
        ('verdict_ia', 'TEXT'),
        ('score_ia', 'INTEGER'),
        ('elements_ia', 'TEXT'),
        ('recommandation_ia', 'TEXT'),
        ('label_phishing', 'INTEGER'),
        ('label_spoofing', 'INTEGER'),
        ('label_scam', 'INTEGER'),
        ('label_bulk', 'INTEGER'),
        ('domain', 'TEXT'),
    ]
    for nom_colonne, type_colonne in nouvelles_colonnes:
        try:
            cursor.execute(f'ALTER TABLE emails ADD COLUMN {nom_colonne} {type_colonne}')
        except:
            pass

    conn.commit()
    conn.close()

def get_or_create_user(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id_user FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        cursor.execute('INSERT INTO users (email) VALUES (?)', (email,))
        user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_or_create_anonymous_user(anon_token):
    """Cree (ou recupere) un utilisateur 'anonyme' rattache a un token de
    session Flask, pour permettre l'usage du simulateur/historique sans
    connexion Google. Reutilise la table users existante avec un email
    synthetique unique (jamais un vrai email Google), pour ne pas avoir
    a modifier le schema ni les fonctions existantes (save_simulation,
    get_simulations, etc. qui prennent juste un id_user)."""
    email_synthetique = f"anon-{anon_token}@local.session"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id_user FROM users WHERE email = ?', (email_synthetique,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        cursor.execute('INSERT INTO users (email) VALUES (?)', (email_synthetique,))
        user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def update_user_token(email, token_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    token_json = json.dumps(token_dict)
    cursor.execute('UPDATE users SET token = ? WHERE email = ?', (token_json, email))
    conn.commit()
    conn.close()

def get_user_token(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT token FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None

def save_email(id_user, msg_id, email_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO emails 
            (id_user, msg_id, label, expediteur, objet, body, ip, spf, dkim, dmarc, liens)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_user,
            msg_id,
            email_data.get('label', ''),
            email_data.get('expediteur', ''),
            email_data.get('objet', ''),
            email_data.get('body', ''),
            email_data.get('ip', ''),
            email_data.get('spf', ''),
            email_data.get('dkim', ''),
            email_data.get('dmarc', ''),
            email_data.get('liens', '')

        ))
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Erreur save_email : {e}")
        success = False
    finally:
        conn.close()
    return success

def get_user_emails(id_user):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, msg_id, label, expediteur, objet, body, ip, spf, dkim, dmarc, liens, date_collecte
        FROM emails
        WHERE id_user = ?
        ORDER BY date_collecte DESC
    ''', (id_user,))
    rows = cursor.fetchall()
    conn.close()
    emails = []
    for row in rows:
        emails.append({
            'id': row[0],
            'msg_id': row[1],
            'label': row[2],
            'expediteur': row[3],
            'objet': row[4],
            'body': row[5],
            'ip': row[6],
            'spf': row[7],
            'dkim': row[8],
            'dmarc': row[9],
            'liens': row[10],
            'date_collecte': row[11]
        })
    return emails

def count_user_emails(id_user):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM emails WHERE id_user = ?', (id_user,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def delete_email(id_user, email_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM emails WHERE id = ? AND id_user = ?', (email_id, id_user))
    conn.commit()
    conn.close()

def reset_database():
    if Path(DB_PATH).exists():
        Path(DB_PATH).unlink()
    init_database()

def get_email_by_id(email_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, msg_id, label, expediteur, objet, body, ip, spf, dkim, dmarc, liens, date_collecte
        FROM emails
        WHERE id = ?
    ''', (email_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'msg_id': row[1],
            'label': row[2],
            'expediteur': row[3],
            'objet': row[4],
            'body': row[5],
            'ip': row[6],
            'spf': row[7],
            'dkim': row[8],
            'dmarc': row[9],
            'liens': row[10],
            'date_collecte': row[11]
        }
    return None

def save_analyse(email_id, resultats):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE emails SET
                score_spam = ?,
                classification = ?,
                ip_blacklistee = ?,
                raison_ip = ?,
                spf_valide = ?,
                raison_spf = ?,
                dkim_valide = ?,
                raison_dkim = ?,
                dmarc_valide = ?,
                raison_dmarc = ?,
                mots_suspects = ?,
                liens_suspects = ?,
                link_count = ?,
                has_image = ?,
                text_length = ?,
                auth_combo = ?,
                domain = ?
            WHERE id = ?
        ''', (
            resultats.get('score_spam'),
            resultats.get('classification'),
            int(resultats.get('ip_blacklistee', False)),
            resultats.get('raison_ip'),
            int(resultats.get('spf_valide', False)),
            resultats.get('raison_spf'),
            int(resultats.get('dkim_valide', False)),
            resultats.get('raison_dkim'),
            int(resultats.get('dmarc_valide', False)),
            resultats.get('raison_dmarc'),
            resultats.get('mots_suspects'),
            resultats.get('liens_suspects'),
            resultats.get('link_count'),
            resultats.get('has_image'),
            resultats.get('text_length'),
            resultats.get('auth_combo'),
            resultats.get('domain'),
            email_id
        ))
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Erreur save_analyse : {e}")
        success = False
    finally:
        conn.close()
    return success

def get_emails_to_clean():
    """Recupere tous les emails dont le body n'a pas encore ete nettoye"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, body
        FROM emails
        WHERE body_clean IS NULL
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'body': row[1]} for row in rows]


def save_body_clean(email_id, body_clean):
    """Sauvegarde le texte nettoye pour un email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE emails SET body_clean = ? WHERE id = ?
        ''', (body_clean, email_id))
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Erreur save_body_clean : {e}")
        success = False
    finally:
        conn.close()
    return success

def get_email_full_for_ai(email_id):
    """Recupere un email avec toutes les colonnes utiles pour l'assemblage IA"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ip, spf, dkim, dmarc, expediteur, objet, body_clean, label
        FROM emails
        WHERE id = ?
    ''', (email_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'ip': row[0],
            'spf': row[1],
            'dkim': row[2],
            'dmarc': row[3],
            'expediteur': row[4],
            'objet': row[5],
            'body_clean': row[6],
            'label': row[7]
        }
    return None


def get_emails_to_analyze_ia():
    """Recupere tous les emails dont l'analyse IA n'a pas encore ete faite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, ip, spf, dkim, dmarc, expediteur, objet, body_clean, label
        FROM emails
        WHERE verdict_ia IS NULL
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'ip': row[1],
            'spf': row[2],
            'dkim': row[3],
            'dmarc': row[4],
            'expediteur': row[5],
            'objet': row[6],
            'body_clean': row[7],
            'label': row[8]
        }
        for row in rows
    ]


def save_analyse_ia(email_id, resultat_ia):
    """Sauvegarde le resultat de l'analyse IA pour un email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        elements = resultat_ia.get('harmful_elements', [])
        elements_texte = ', '.join(elements) if elements else ''

        cursor.execute('''
            UPDATE emails SET
                verdict_ia = ?,
                score_ia = ?,
                elements_ia = ?,
                recommandation_ia = ?,
                label_phishing = ?,
                label_spoofing = ?,
                label_scam = ?,
                label_bulk = ?
            WHERE id = ?
        ''', (
            resultat_ia.get('verdict'),
            resultat_ia.get('score'),
            elements_texte,
            resultat_ia.get('recommendation'),
            int(resultat_ia.get('label_phishing', False)),
            int(resultat_ia.get('label_spoofing', False)),
            int(resultat_ia.get('label_scam', False)),
            int(resultat_ia.get('label_bulk', False)),
            email_id
        ))
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Erreur save_analyse_ia : {e}")
        success = False
    finally:
        conn.close()
    return success

def get_emails_to_analyze_ia_test(limite=5):
    """Version de test : recupere seulement quelques emails, pour chronometrer"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, ip, spf, dkim, dmarc, expediteur, objet, body_clean, label
        FROM emails
        WHERE verdict_ia IS NULL
        LIMIT ?
    ''', (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'ip': row[1],
            'spf': row[2],
            'dkim': row[3],
            'dmarc': row[4],
            'expediteur': row[5],
            'objet': row[6],
            'body_clean': row[7],
            'label': row[8]
        }
        for row in rows
    ]

def get_emails_for_ia_sample(n_inbox=145, n_spam=55):
    """
    Selectionne un echantillon representatif pour l'analyse IA,
    en respectant le ratio reel INBOX/SPAM de la base, et en
    excluant les emails deja analyses par l'IA (verdict_ia IS NULL).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, ip, spf, dkim, dmarc, expediteur, objet, body_clean, label
        FROM emails
        WHERE verdict_ia IS NULL AND label = 'INBOX'
        ORDER BY RANDOM()
        LIMIT ?
    ''', (n_inbox,))
    inbox_rows = cursor.fetchall()

    cursor.execute('''
        SELECT id, ip, spf, dkim, dmarc, expediteur, objet, body_clean, label
        FROM emails
        WHERE verdict_ia IS NULL AND label = 'SPAM'
        ORDER BY RANDOM()
        LIMIT ?
    ''', (n_spam,))
    spam_rows = cursor.fetchall()

    conn.close()

    tous = inbox_rows + spam_rows
    return [
        {
            'id': row[0], 'ip': row[1], 'spf': row[2], 'dkim': row[3],
            'dmarc': row[4], 'expediteur': row[5], 'objet': row[6],
            'body_clean': row[7], 'label': row[8]
        }
        for row in tous
    ]

def get_all_emails_ids():
    """Recupere les id de TOUS les emails (tous comptes confondus)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM emails')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def save_simulation(id_user, donnees_formulaire, resultat_ia):
    """Sauvegarde une simulation d'offre (formulaire + resultat IA) en base,
    pour alimenter l'historique consultable plus tard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        elements = resultat_ia.get('harmful_elements', [])
        elements_texte = ', '.join(elements) if elements else ''

        cursor.execute('''
            INSERT INTO simulations
            (id_user, domaine, nom_affiche, sujet, description_offre,
             spf_ok, dkim_ok, dmarc_ok, verdict, score, score_explication,
             label_phishing, label_spoofing, label_scam, label_bulk,
             harmful_elements, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_user,
            donnees_formulaire.get('domaine'),
            donnees_formulaire.get('nom_affiche'),
            donnees_formulaire.get('sujet'),
            donnees_formulaire.get('description_offre'),
            int(donnees_formulaire.get('spf_ok', False)),
            int(donnees_formulaire.get('dkim_ok', False)),
            int(donnees_formulaire.get('dmarc_ok', False)),
            resultat_ia.get('verdict'),
            resultat_ia.get('score'),
            resultat_ia.get('score_explication'),
            int(resultat_ia.get('label_phishing', False)),
            int(resultat_ia.get('label_spoofing', False)),
            int(resultat_ia.get('label_scam', False)),
            int(resultat_ia.get('label_bulk', False)),
            elements_texte,
            resultat_ia.get('recommendation')
        ))
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Erreur save_simulation : {e}")
        success = False
    finally:
        conn.close()
    return success


def get_simulations(id_user):
    """Recupere l'historique des simulations pour un utilisateur, les plus
    recentes en premier."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, domaine, nom_affiche, sujet, verdict, score,
               label_phishing, label_spoofing, label_scam, label_bulk,
               date_creation
        FROM simulations
        WHERE id_user = ?
        ORDER BY date_creation DESC
    ''', (id_user,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0], 'domaine': row[1], 'nom_affiche': row[2],
            'sujet': row[3], 'verdict': row[4], 'score': row[5],
            'label_phishing': row[6], 'label_spoofing': row[7],
            'label_scam': row[8], 'label_bulk': row[9],
            'date_creation': row[10]
        }
        for row in rows
    ]

def get_simulation_by_id(simulation_id, id_user):
    """Recupere le detail complet d'une simulation precise, en verifiant
    qu'elle appartient bien a l'utilisateur connecte."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, domaine, nom_affiche, sujet, description_offre,
               spf_ok, dkim_ok, dmarc_ok, verdict, score, score_explication,
               label_phishing, label_spoofing, label_scam, label_bulk,
               harmful_elements, recommendation, date_creation
        FROM simulations
        WHERE id = ? AND id_user = ?
    ''', (simulation_id, id_user))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0], 'domaine': row[1], 'nom_affiche': row[2],
            'sujet': row[3], 'description_offre': row[4],
            'spf_ok': row[5], 'dkim_ok': row[6], 'dmarc_ok': row[7],
            'verdict': row[8], 'score': row[9], 'score_explication': row[10],
            'label_phishing': row[11], 'label_spoofing': row[12],
            'label_scam': row[13], 'label_bulk': row[14],
            'harmful_elements': row[15], 'recommendation': row[16],
            'date_creation': row[17]
        }
    return None

def get_stats_heuristique():
    """
    Calcule les statistiques de l'analyse heuristique sur tout le dataset
    collecte, en comparant le vrai label Gmail (INBOX/SPAM) a la
    classification heuristique (SPAM/SUSPECT/LEGITIME), pour mettre en
    evidence la qualite reelle (ou les limites) de l'heuristique.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Repartition globale des classifications (tous emails confondus, analyses uniquement)
    cursor.execute('''
        SELECT classification, COUNT(*)
        FROM emails
        WHERE classification IS NOT NULL
        GROUP BY classification
    ''')
    repartition_classification = dict(cursor.fetchall())

    # Score moyen
    cursor.execute('''
        SELECT AVG(score_spam)
        FROM emails
        WHERE score_spam IS NOT NULL
    ''')
    score_moyen = cursor.fetchone()[0]

    # Croisement : vrai label Gmail x classification heuristique
    cursor.execute('''
        SELECT label, classification, COUNT(*)
        FROM emails
        WHERE label IS NOT NULL AND classification IS NOT NULL
        GROUP BY label, classification
    ''')
    croisement_rows = cursor.fetchall()

    conn.close()

    # Organisation du croisement en structure exploitable par le template
    croisement = {'INBOX': {}, 'SPAM': {}}
    for label, classification, count in croisement_rows:
        if label in croisement:
            croisement[label][classification] = count

    # Calcul du taux de detection correcte pour les vrais SPAM
    total_vrai_spam = sum(croisement.get('SPAM', {}).values())
    spam_correctement_detecte = croisement.get('SPAM', {}).get('SPAM', 0)
    taux_detection_spam = (
        round(spam_correctement_detecte / total_vrai_spam * 100, 1)
        if total_vrai_spam > 0 else 0
    )

    # Calcul du taux de bonne classification pour les vrais INBOX (legitime)
    total_vrai_inbox = sum(croisement.get('INBOX', {}).values())
    inbox_correctement_detecte = croisement.get('INBOX', {}).get('LEGITIME', 0)
    taux_detection_inbox = (
        round(inbox_correctement_detecte / total_vrai_inbox * 100, 1)
        if total_vrai_inbox > 0 else 0
    )

    return {
        'repartition_classification': repartition_classification,
        'score_moyen': round(score_moyen, 1) if score_moyen is not None else None,
        'total_analyse': sum(repartition_classification.values()),
        'croisement': croisement,
        'total_vrai_spam': total_vrai_spam,
        'total_vrai_inbox': total_vrai_inbox,
        'taux_detection_spam': taux_detection_spam,
        'taux_detection_inbox': taux_detection_inbox,
    }


def get_stats_simulations(id_user):
    """
    Calcule les statistiques sur les tests effectues via le simulateur
    par un utilisateur donne : repartition SPAM/LEGITIME, score moyen,
    et frequence d'apparition de chaque label (Phishing/Spoofing/Scam/Bulk).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Repartition verdict (spam/legitime)
    cursor.execute('''
        SELECT verdict, COUNT(*)
        FROM simulations
        WHERE id_user = ? AND verdict IS NOT NULL
        GROUP BY verdict
    ''', (id_user,))
    repartition_verdict = dict(cursor.fetchall())

    # Score moyen
    cursor.execute('''
        SELECT AVG(score)
        FROM simulations
        WHERE id_user = ? AND score IS NOT NULL
    ''', (id_user,))
    score_moyen = cursor.fetchone()[0]

    # Nombre total de simulations
    cursor.execute('''
        SELECT COUNT(*) FROM simulations WHERE id_user = ?
    ''', (id_user,))
    total = cursor.fetchone()[0]

    # Frequence de chaque label
    cursor.execute('''
        SELECT
            SUM(label_phishing) as phishing,
            SUM(label_spoofing) as spoofing,
            SUM(label_scam) as scam,
            SUM(label_bulk) as bulk
        FROM simulations
        WHERE id_user = ?
    ''', (id_user,))
    row = cursor.fetchone()

    conn.close()

    repartition_labels = {
        'Phishing': row[0] or 0,
        'Spoofing': row[1] or 0,
        'Scam': row[2] or 0,
        'Bulk': row[3] or 0,
    }

    return {
        'repartition_verdict': repartition_verdict,
        'score_moyen': round(score_moyen, 1) if score_moyen is not None else None,
        'total': total,
        'repartition_labels': repartition_labels,
    }


def vider_simulations(id_user):
    """Supprime toutes les simulations d'un utilisateur."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM simulations WHERE id_user = ?', (id_user,))
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Erreur vider_simulations : {e}")
        success = False
    finally:
        conn.close()
    return success