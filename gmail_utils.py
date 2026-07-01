import os
import secrets
import hashlib
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
REDIRECT_URI = 'http://localhost:5000/auth/callback'

def get_gmail_service(creds):
    if not creds:
        return None
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Erreur service Gmail : {e}")
        return None

def refresh_credentials(creds):
    if not creds:
        return None
    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"❌ Erreur rafraîchissement : {e}")
        return None

def get_authorization_url():
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Générer code_verifier
    code_verifier = secrets.token_urlsafe(96)

    # Générer code_challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()

    auth_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        code_challenge=code_challenge,
        code_challenge_method='S256'
    )

    return auth_url, state, code_verifier

def credentials_from_auth_code(code, code_verifier):
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(
        code=code,
        code_verifier=code_verifier
    )
    creds = flow.credentials
    return serialize_credentials(creds)

def get_user_email(creds):
    try:
        service = get_gmail_service(creds)
        if not service:
            return None
        profile = service.users().getProfile(userId='me').execute()
        return profile.get('emailAddress')
    except Exception as e:
        print(f"❌ Erreur profil : {e}")
        return None

def serialize_credentials(creds):
    try:
        return {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes) if creds.scopes else [],
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }
    except Exception as e:
        print(f"❌ Erreur sérialisation : {e}")
        return None

def deserialize_credentials(creds_dict):
    from datetime import datetime
    try:
        if not creds_dict:
            return None
        expiry = None
        if creds_dict.get('expiry'):
            expiry = datetime.fromisoformat(creds_dict['expiry'])
        creds = Credentials(
            token=creds_dict.get('token'),
            refresh_token=creds_dict.get('refresh_token'),
            token_uri=creds_dict.get('token_uri'),
            client_id=creds_dict.get('client_id'),
            client_secret=creds_dict.get('client_secret'),
            scopes=creds_dict.get('scopes'),
        )
        creds.expiry = expiry
        return creds
    except Exception as e:
        print(f"❌ Erreur désérialisation : {e}")
        return None