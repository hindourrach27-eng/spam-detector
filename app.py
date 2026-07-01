"""
app.py — Application Flask pour le système de diagnostic spam
Routes : /login, /auth/callback, /emails, /collect
"""

from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from flask_session import Session
import os
from datetime import timedelta

from gmail_utils import (
    get_authorization_url, credentials_from_auth_code,
    deserialize_credentials, get_user_email, serialize_credentials,
    get_gmail_service
)
from gmail_service import fetch_gmail_labels, fetch_emails_list, collect_emails_from_gmail, extract_email_data
from database import (
    init_database, get_or_create_user, update_user_token,
    get_user_token, save_email, get_user_emails, count_user_emails
)

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
Session(app)

init_database()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('emails_page'))
    return redirect(url_for('login_page'))

@app.route('/login')
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

@app.route('/auth/callback')
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
        return redirect(url_for('emails_page'))

    except Exception as e:
        print(f"❌ Erreur auth_callback : {e}")
        return f"❌ Erreur d'authentification : {e}", 500

@app.route('/emails')
def emails_page():
    if 'user_email' not in session:
        return redirect(url_for('login_page'))

    try:
        creds_dict = session.get('user_credentials')
        creds = deserialize_credentials(creds_dict)

        if not creds:
            return "❌ Credentials invalides", 500

        service = get_gmail_service(creds)
        if not service:
            return "❌ Impossible de se connecter à Gmail", 500

        labels = fetch_gmail_labels(service)
        emails_to_display = {}

        if 'INBOX' in labels:
            inbox_msg_ids = fetch_emails_list(service, labels['INBOX'], max_results=20)
            emails_to_display['INBOX'] = [
                {'msg_id': msg_id, 'label': 'INBOX'} for msg_id in inbox_msg_ids
            ]

        if 'SPAM' in labels:
            spam_msg_ids = fetch_emails_list(service, labels['SPAM'], max_results=20)
            emails_to_display['SPAM'] = [
                {'msg_id': msg_id, 'label': 'SPAM'} for msg_id in spam_msg_ids
            ]

        collected = get_user_emails(session['user_id'])
        collected_msg_ids = {email['msg_id'] for email in collected}

        return render_template(
            'emails.html',
            user_email=session['user_email'],
            emails_by_label=emails_to_display,
            collected_count=len(collected),
            total_available=sum(len(v) for v in emails_to_display.values()),
            collected_msg_ids=collected_msg_ids
        )

    except Exception as e:
        print(f"❌ Erreur emails_page : {e}")
        return f"❌ Erreur : {e}", 500

@app.route('/collect', methods=['POST'])
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

@app.route('/collected')
def collected_page():
    if 'user_email' not in session:
        return redirect(url_for('login_page'))

    try:
        user_id = session['user_id']
        emails = get_user_emails(user_id)
        return render_template(
            'collected.html',
            user_email=session['user_email'],
            emails=emails,
            count=len(emails)
        )
    except Exception as e:
        return f"❌ Erreur : {e}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/api/user')
def api_user():
    if 'user_email' not in session:
        return jsonify({'logged_in': False})
    return jsonify({
        'logged_in': True,
        'email': session['user_email'],
        'collected_count': count_user_emails(session['user_id'])
    })

@app.errorhandler(404)
def not_found(e):
    return "❌ Page non trouvée", 404

@app.errorhandler(500)
def server_error(e):
    return f"❌ Erreur serveur : {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)