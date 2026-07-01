"""
app/home/routes.py — Routes de l'application (diagnostic spam)
"""

import threading
from flask import session, redirect, url_for, request, jsonify, render_template
from app.home import home_blueprint
from clean_text import build_model_input_from_form, analyze_with_ollama, detecter_texte_cache_html
from gmail_utils import (
    get_authorization_url, credentials_from_auth_code,
    deserialize_credentials, get_user_email, serialize_credentials,
    get_gmail_service
)
from gmail_service import fetch_gmail_labels, fetch_emails_list, collect_emails_from_gmail, extract_email_data
from database import (
    init_database, get_or_create_user, update_user_token,
    get_user_token, save_email, get_user_emails, count_user_emails,
    get_email_by_id, save_analyse , get_all_emails_ids,
    save_simulation, get_simulations, get_simulation_by_id,
    get_stats_heuristique, get_stats_simulations
)
from spam_analyzer import SpamAnalyzer


# Etat de la collecte en masse (partage entre les requetes)
collection_status = {
    "en_cours": False,
    "traites": 0,
    "total": 0,
    "termine": False,
    "erreur": None
}

# Etat de l'analyse heuristique en masse (partage entre les requetes)
heuristic_status = {
    "en_cours": False,
    "traites": 0,
    "total": 0,
    "termine": False,
    "erreur": None
}

@home_blueprint.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('home_blueprint.emails_page'))
    return redirect(url_for('home_blueprint.login_page'))

@home_blueprint.route('/login')
def login_page():
    try:
        auth_url, state, code_verifier = get_authorization_url()
        session['oauth_state'] = state
        session['code_verifier'] = code_verifier
        return redirect(auth_url)
    except FileNotFoundError as e:
        return f"❌ Erreur : {e}", 400
    except Exception as e:
        print(f"❌ Erreur login : {e}")
        return f"❌ Erreur lors de la connexion : {e}", 500

@home_blueprint.route('/auth/callback')
def auth_callback():
    try:
        code = request.args.get('code')

        if not code:
            return "❌ Code d'autorisation manquant", 400

        code_verifier = session.get('code_verifier')

        try:
            creds_dict = credentials_from_auth_code(code, code_verifier)
        except Exception as e:
            print(f"❌ Erreur échange code : {e}")
            return f"❌ Erreur lors de l'authentification Google : {e}", 500

        creds = deserialize_credentials(creds_dict)

        user_email = get_user_email(creds)
        if not user_email:
            return "❌ Impossible de récupérer l'adresse email", 500

        user_id = get_or_create_user(user_email)
        update_user_token(user_email, creds_dict)

        session['user_email'] = user_email
        session['user_id'] = user_id
        session['user_credentials'] = creds_dict

        print(f"✅ Utilisateur connecté : {user_email}")
        return redirect(url_for('home_blueprint.emails_page'))

    except Exception as e:
        print(f"❌ Erreur auth_callback : {e}")
        return f"❌ Erreur d'authentification : {e}", 500



@home_blueprint.route('/emails')
def emails_page():
    """Renders the page shell only — no email fetching here."""
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))
    return render_template(
        'emails.html',
        user_email=session['user_email']
    )


@home_blueprint.route('/emails/data')
def emails_data():
    """Returns emails_by_label + collected_msg_ids as JSON for the DataTable."""
    if 'user_email' not in session:
        return jsonify({"error": "unauthorized"}), 401

    try:
        creds_dict = session.get('user_credentials')
        creds = deserialize_credentials(creds_dict)
        if not creds:
            return jsonify({"error": "Credentials invalides"}), 500

        service = get_gmail_service(creds)
        if not service:
            return jsonify({"error": "Impossible de se connecter à Gmail"}), 500

        labels = fetch_gmail_labels(service)
        emails_to_display = {}

        if 'INBOX' in labels:
            inbox_msg_ids = fetch_emails_list(service, labels['INBOX'], max_results=20)
            inbox_emails = []
            for msg_id in inbox_msg_ids:
                email_data = extract_email_data(service, msg_id, 'INBOX')
                if email_data:
                    inbox_emails.append(email_data)
            emails_to_display['INBOX'] = inbox_emails

        if 'SPAM' in labels:
            spam_msg_ids = fetch_emails_list(service, labels['SPAM'], max_results=20)
            spam_emails = []
            for msg_id in spam_msg_ids:
                email_data = extract_email_data(service, msg_id, 'SPAM')
                if email_data:
                    spam_emails.append(email_data)
            emails_to_display['SPAM'] = spam_emails

        collected = get_user_emails(session['user_id'])
        collected_msg_ids = {email['msg_id'] for email in collected}

        # Flatten into a single list of rows for DataTables
        rows = []
        for label_name, email_list in emails_to_display.items():
            for email in email_list:
                rows.append({
                    "msg_id": email.get("msg_id"),
                    "label": label_name,
                    "expediteur": email.get("expediteur"),
                    "objet": email.get("objet"),
                    "is_collected": email.get("msg_id") in collected_msg_ids
                })

        return jsonify({
            "data": rows,
            "collected_count": len(collected),
            "total_available": len(rows)
        })

    except Exception as e:
        print(f"❌ Erreur emails_data : {e}")
        return jsonify({"error": str(e)}), 500



# @home_blueprint.route('/emails')
# def emails_page():
#     if 'user_email' not in session:
#         return redirect(url_for('home_blueprint.login_page'))
#
#     try:
#         creds_dict = session.get('user_credentials')
#         creds = deserialize_credentials(creds_dict)
#
#         if not creds:
#             return "❌ Credentials invalides", 500
#
#         service = get_gmail_service(creds)
#         if not service:
#             return "❌ Impossible de se connecter à Gmail", 500
#
#         labels = fetch_gmail_labels(service)
#         emails_to_display = {}
#
#         if 'INBOX' in labels:
#             inbox_msg_ids = fetch_emails_list(service, labels['INBOX'], max_results=20)
#             inbox_emails = []
#             for msg_id in inbox_msg_ids:
#                 email_data = extract_email_data(service, msg_id, 'INBOX')
#                 if email_data:
#                     inbox_emails.append(email_data)
#             emails_to_display['INBOX'] = inbox_emails
#
#         if 'SPAM' in labels:
#             spam_msg_ids = fetch_emails_list(service, labels['SPAM'], max_results=20)
#             spam_emails = []
#             for msg_id in spam_msg_ids:
#                 email_data = extract_email_data(service, msg_id, 'SPAM')
#                 if email_data:
#                     spam_emails.append(email_data)
#             emails_to_display['SPAM'] = spam_emails
#
#         collected = get_user_emails(session['user_id'])
#         collected_msg_ids = {email['msg_id'] for email in collected}
#         print("emails_to_display ",emails_to_display)
#         return render_template(
#             'emails.html',
#             user_email=session['user_email'],
#             # emails_by_label=emails_to_display,
#             collected_count=len(collected),
#             total_available=sum(len(v) for v in emails_to_display.values()),
#             collected_msg_ids=collected_msg_ids
#         )
#
#     except Exception as e:
#         print(f"❌ Erreur emails_page : {e}")
#         return f"❌ Erreur : {e}", 500

@home_blueprint.route('/collect', methods=['POST'])
def collect_emails():
    if 'user_email' not in session:
        return jsonify({'error': 'Non authentifié'}), 401

    try:
        data = request.get_json()
        message_ids = data.get('message_ids', [])

        if not message_ids:
            return jsonify({'error': 'Aucun email sélectionné'}), 400

        creds_dict = session.get('user_credentials')
        creds = deserialize_credentials(creds_dict)

        if not creds:
            return jsonify({'error': 'Credentials invalides'}), 500

        service = get_gmail_service(creds)
        all_emails = []

        for msg_id in message_ids:
            msg = service.users().messages().get(
                userId='me', id=msg_id, format='minimal'
            ).execute()
            label_ids = msg.get('labelIds', [])
            label_name = 'SPAM' if 'SPAM' in label_ids else 'INBOX'
            all_emails.append({'msg_id': msg_id, 'label': label_name})

        emails_data = []
        for email_info in all_emails:
            email_data = extract_email_data(service, email_info['msg_id'], email_info['label'])
            if email_data:
                emails_data.append(email_data)

        collected_count = 0
        for email_data in emails_data:
            if save_email(session['user_id'], email_data['msg_id'], email_data):
                collected_count += 1

        return jsonify({
            'success': True,
            'collected': collected_count,
            'message': f"{collected_count} email(s) collecté(s)"
        }), 200

    except Exception as e:
        print(f"❌ Erreur collect_emails : {e}")
        return jsonify({'error': str(e)}), 500


def _run_collect_all(creds_dict, user_id):
    """
    Fonction executee EN ARRIERE-PLAN (dans un thread separe).
    Met a jour collection_status au fur et a mesure.
    """
    global collection_status
    try:
        creds = deserialize_credentials(creds_dict)
        service = get_gmail_service(creds)
        if not service:
            collection_status["erreur"] = "Impossible de se connecter à Gmail"
            collection_status["en_cours"] = False
            collection_status["termine"] = True
            return

        labels = fetch_gmail_labels(service)
        all_msg_infos = []

        if 'INBOX' in labels:
            inbox_ids = fetch_emails_list(service, labels['INBOX'], max_results=500)
            for msg_id in inbox_ids:
                all_msg_infos.append({'msg_id': msg_id, 'label': 'INBOX'})

        if 'SPAM' in labels:
            spam_ids = fetch_emails_list(service, labels['SPAM'], max_results=500)
            for msg_id in spam_ids:
                all_msg_infos.append({'msg_id': msg_id, 'label': 'SPAM'})

        total_found = len(all_msg_infos)
        collection_status["total"] = total_found

        for idx, info in enumerate(all_msg_infos, 1):
            email_data = extract_email_data(service, info['msg_id'], info['label'])
            if email_data:
                save_email(user_id, email_data['msg_id'], email_data)

            collection_status["traites"] = idx

            if idx % 50 == 0:
                print(f"   ... {idx}/{total_found} traités")

        print(f"✅ Collecte terminee : {total_found} emails traites")

    except Exception as e:
        print(f"❌ Erreur _run_collect_all : {e}")
        collection_status["erreur"] = str(e)
    finally:
        collection_status["en_cours"] = False
        collection_status["termine"] = True


@home_blueprint.route('/collect-all', methods=['POST'])
def collect_all_emails():
    """
    Lance la collecte en masse (INBOX + SPAM, jusqu'a 500 chacun)
    dans un thread separe, et repond immediatement.
    """
    global collection_status

    if 'user_email' not in session:
        return jsonify({'error': 'Non authentifié'}), 401

    if collection_status["en_cours"]:
        return jsonify({'error': 'Une collecte est déjà en cours'}), 409

    creds_dict = session.get('user_credentials')
    if not creds_dict:
        return jsonify({'error': 'Credentials invalides'}), 500

    # Reinitialiser l'etat
    collection_status = {
        "en_cours": True,
        "traites": 0,
        "total": 0,
        "termine": False,
        "erreur": None
    }

    user_id = session['user_id']

    thread = threading.Thread(target=_run_collect_all, args=(creds_dict, user_id))
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Collecte démarrée en arrière-plan'
    }), 202


@home_blueprint.route('/collect-all/status')
def collect_all_status():
    """Renvoie l'etat actuel de la collecte en masse."""
    if 'user_email' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    return jsonify(collection_status)

def _run_heuristic_all():
    """
    Fonction executee EN ARRIERE-PLAN (dans un thread separe).
    Applique l'heuristique SpamAnalyzer sur TOUS les emails de la base
    (tous comptes confondus), met a jour heuristic_status au fur et a mesure.
    """
    global heuristic_status
    try:
        analyzer = SpamAnalyzer()
        all_ids = get_all_emails_ids()
        total = len(all_ids)
        heuristic_status["total"] = total

        for idx, email_id in enumerate(all_ids, 1):
            email = get_email_by_id(email_id)
            if email:
                resultats = analyzer.analyze_email(email)
                save_analyse(email_id, resultats)

            heuristic_status["traites"] = idx

            if idx % 200 == 0:
                print(f"   ... {idx}/{total} traites (heuristique)")

        print(f"✅ Analyse heuristique terminee : {total} emails traites")

    except Exception as e:
        print(f"❌ Erreur _run_heuristic_all : {e}")
        heuristic_status["erreur"] = str(e)
    finally:
        heuristic_status["en_cours"] = False
        heuristic_status["termine"] = True


@home_blueprint.route('/analyze-all-heuristic', methods=['POST'])
def analyze_all_heuristic():
    """Lance l'analyse heuristique en masse sur TOUS les emails, dans un thread."""
    global heuristic_status

    if 'user_email' not in session:
        return jsonify({'error': 'Non authentifié'}), 401

    if heuristic_status["en_cours"]:
        return jsonify({'error': 'Une analyse est déjà en cours'}), 409

    heuristic_status = {
        "en_cours": True,
        "traites": 0,
        "total": 0,
        "termine": False,
        "erreur": None
    }

    thread = threading.Thread(target=_run_heuristic_all)
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Analyse heuristique démarrée en arrière-plan'
    }), 202


@home_blueprint.route('/analyze-all-heuristic/status')
def analyze_all_heuristic_status():
    """Renvoie l'etat actuel de l'analyse heuristique en masse."""
    if 'user_email' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    return jsonify(heuristic_status)





@home_blueprint.route('/collected')
def collected_page():
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))
    return render_template(
        'collected.html',
        user_email=session['user_email']
    )

@home_blueprint.route('/collected/data')
def collected_data():
    if 'user_email' not in session:
        return jsonify({"error": "unauthorized"}), 401

    try:
        user_id = session['user_id']
        emails = get_user_emails(user_id)

        rows = []
        for email in emails:
            rows.append({
                "id": email.get("id"),
                "label": email.get("label"),
                "expediteur": email.get("expediteur"),
                "objet": email.get("objet"),
                "spf": email.get("spf"),
                "dkim": email.get("dkim"),
                "ip": email.get("ip"),
                "date_collecte": email.get("date_collecte")
            })

        total = len(emails)
        inbox_count = sum(1 for e in emails if e.get('label') == 'INBOX')
        spam_count = sum(1 for e in emails if e.get('label') == 'SPAM')
        spf_valid_count = sum(1 for e in emails if e.get('spf') == 'pass')

        return jsonify({
            "data": rows,
            "total": total,
            "inbox_count": inbox_count,
            "spam_count": spam_count,
            "spf_valid_count": spf_valid_count
        })

    except Exception as e:
        print(f"❌ Erreur collected_data : {e}")
        return jsonify({"error": str(e)}), 500

@home_blueprint.route('/analyse/<int:email_id>')
def analyse_email(email_id):
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))

    try:
        email = get_email_by_id(email_id)

        if not email:
            return "Email introuvable", 404

        analyzer = SpamAnalyzer()
        resultats = analyzer.analyze_email(email)

        save_analyse(email_id, resultats)

        return render_template(
            'analyse.html',
            user_email=session['user_email'],
            email=email,
            resultats=resultats
        )

    except Exception as e:
        print(f"❌ Erreur analyse_email : {e}")
        return f"❌ Erreur : {e}", 500

@home_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_blueprint.login_page'))

@home_blueprint.route('/api/user')
def api_user():
    if 'user_email' not in session:
        return jsonify({'logged_in': False})
    return jsonify({
        'logged_in': True,
        'email': session['user_email'],
        'collected_count': count_user_emails(session['user_id'])
    })

@home_blueprint.route('/simulateur')
def simulateur_page():
    """Affiche le formulaire du simulateur d'offre (analyse IA en direct,
    sans passer par un email deja collecte en base)."""
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))
    return render_template(
        'simulateur.html',
        user_email=session['user_email']
    )


@home_blueprint.route('/simulateur/analyser', methods=['POST'])
def simulateur_analyser():
    """
    Recoit les donnees du formulaire (domaine, offre, cases SPF/DKIM/DMARC),
    construit un bloc de texte simule et appelle l'IA (Ollama) en direct.
    Ne touche a aucune donnee existante en base (pas de email_id, pas de
    sauvegarde dans la table emails) -- c'est une simulation isolee.
    """
    if 'user_email' not in session:
        return jsonify({'error': 'Non authentifié'}), 401

    try:
        data = request.get_json()

        domaine = (data.get('domaine') or '').strip()
        nom_affiche = (data.get('nom_affiche') or '').strip()
        sujet = (data.get('sujet') or '').strip()
        description_offre = (data.get('description_offre') or '').strip()
        code_html = (data.get('code_html') or '').strip()
        spf_ok = bool(data.get('spf_ok'))
        dkim_ok = bool(data.get('dkim_ok'))
        dmarc_ok = bool(data.get('dmarc_ok'))

        if not domaine or not description_offre or not code_html:
            return jsonify({'error': "Domaine, description de l'offre et code HTML sont obligatoires"}), 400

        # Verification deterministe (Python, pas IA) du texte cache dans le HTML
        problemes_html = detecter_texte_cache_html(code_html)

        model_input = build_model_input_from_form(
            domaine, nom_affiche, sujet, description_offre, spf_ok, dkim_ok, dmarc_ok
        )
        # Pas de label_gmail ici : ce n'est pas un email Gmail reel, juste une simulation
        resultat_ia, type_erreur = analyze_with_ollama(model_input, label_gmail=None)

        if resultat_ia is None:
            messages_erreur = {
                'timeout': "L'IA n'a pas repondu a temps (timeout). Le modele est peut-etre en train de se recharger en memoire, reessayez dans une minute.",
                'json_invalide': "L'IA a repondu dans un format inattendu. Reessayez.",
                'erreur_autre': "Une erreur technique est survenue lors de l'appel a l'IA. Reessayez."
            }
            return jsonify({
                'error': messages_erreur.get(type_erreur, "Erreur inconnue lors de l'analyse.")
            }), 500

        # Override deterministe : si du texte cache reel est detecte dans le HTML,
        # le verdict global doit refleter ce risque, independamment de l'avis de l'IA
        # sur le texte visible seul.
        if problemes_html:
            resultat_ia['verdict'] = 'spam'
            resultat_ia['score'] = max(resultat_ia.get('score', 0), 85)
            resultat_ia['score_explication'] = (
                    "Score force a la hausse : du texte cache a ete detecte dans le code HTML "
                    "(verification technique deterministe), ce qui constitue un signal fort de "
                    "tentative de contournement des filtres anti-spam, independamment du contenu visible. "
                    + (resultat_ia.get('score_explication') or '')
            )
            elements_existants = resultat_ia.get('harmful_elements', [])
            resultat_ia['harmful_elements'] = elements_existants + [
                f"Texte cache detecte dans le HTML ({len(problemes_html)} probleme(s))"
            ]
            resultat_ia['recommendation'] = (
                "Retirez immediatement le texte cache du code HTML (proprietes CSS comme "
                "opacity:0, font-size:0, display:none ou max-height:0 appliquees a du contenu "
                "textuel). Cette technique est detectee et penalisee par la plupart des filtres "
                "anti-spam modernes, et peut nuire durablement a la reputation du domaine d'envoi."
            )

        # Sauvegarde automatique de la simulation pour l'historique
        donnees_formulaire = {
            'domaine': domaine,
            'nom_affiche': nom_affiche,
            'sujet': sujet,
            'description_offre': description_offre,
            'spf_ok': spf_ok,
            'dkim_ok': dkim_ok,
            'dmarc_ok': dmarc_ok
        }
        save_simulation(session['user_id'], donnees_formulaire, resultat_ia)

        return jsonify({
            'success': True,
            'resultat': resultat_ia,
            'problemes_html': problemes_html
        }), 200


    except Exception as e:
        print(f"❌ Erreur simulateur_analyser : {e}")
        return jsonify({'error': str(e)}), 500


@home_blueprint.route('/glossaire')
def glossaire_page():
    """Page statique expliquant les termes techniques du diagnostic spam
    en langage accessible (SPF, DKIM, DMARC, Spoofing, Phishing, etc.)."""
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))
    return render_template(
        'glossaire.html',
        user_email=session['user_email']
    )

@home_blueprint.route('/simulateur/historique')
def simulateur_historique():
    """Affiche l'historique des simulations passees de l'utilisateur,
    sous forme de tableau simple."""
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))

    simulations = get_simulations(session['user_id'])

    return render_template(
        'simulateur_historique.html',
        user_email=session['user_email'],
        simulations=simulations
    )

@home_blueprint.route('/simulateur/historique/<int:simulation_id>')
def simulateur_historique_detail(simulation_id):
    """Affiche le detail complet d'une simulation passee."""
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))

    simulation = get_simulation_by_id(simulation_id, session['user_id'])

    if not simulation:
        return "Simulation introuvable", 404

    return render_template(
        'simulateur_historique_detail.html',
        user_email=session['user_email'],
        simulation=simulation
    )


@home_blueprint.route('/statistiques')
def statistiques_page():
    """
    Affiche deux sections de statistiques distinctes :
    1. Sur le dataset reel collecte (analyse heuristique vs vrai label Gmail)
    2. Sur les tests effectues via le simulateur (IA)
    Ces deux sources ne sont JAMAIS combinees en une seule statistique,
    car elles representent des choses fondamentalement differentes
    (vrais emails avec verite terrain vs cas fictifs testes par l'utilisateur).
    """
    if 'user_email' not in session:
        return redirect(url_for('home_blueprint.login_page'))

    stats_heuristique = get_stats_heuristique()
    stats_simulations = get_stats_simulations(session['user_id'])

    return render_template(
        'statistiques.html',
        user_email=session['user_email'],
        stats_heuristique=stats_heuristique,
        stats_simulations=stats_simulations
    )