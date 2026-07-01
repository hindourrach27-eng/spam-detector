"""
Étape 1 : Connexion Gmail API
Script pour se connecter à Gmail via OAuth2 et afficher l'adresse email
"""

import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.gapic_v1 import client_info as grpc_client_info
from googleapiclient.discovery import build

# Si vous modifiez ces scopes, supprimez le fichier token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """
    Authentifier l'utilisateur avec Gmail API via OAuth2
    Retourne le service Gmail
    """
    creds = None
    
    # token.json stocke les credentials de l'utilisateur
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    
    # Si pas de credentials valides, lance le flux OAuth2
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarde les credentials pour les prochaines fois
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_user_profile(service):
    """
    Récupérer les informations du profil utilisateur Gmail
    """
    try:
        profile = service.users().getProfile(userId='me').execute()
        return profile.get('emailAddress')
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du profil : {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Connexion à Gmail API - Étape 1")
    print("=" * 60)
    
    # Vérifier que credentials.json existe
    if not os.path.exists('credentials.json'):
        print("❌ ERREUR : credentials.json n'a pas été trouvé dans le dossier courant")
        print("📝 Vous devez :")
        print("   1. Créer un projet sur https://console.cloud.google.com")
        print("   2. Activer l'API Gmail")
        print("   3. Créer des identifiants OAuth 2.0 (Application de bureau)")
        print("   4. Télécharger le fichier JSON et le renommer en 'credentials.json'")
        print("   5. Placer credentials.json dans ce dossier")
        exit(1)
    
    try:
        # Authentifier
        print("\n⏳ Authentification en cours...")
        service = authenticate_gmail()
        print("✅ Authentification réussie !")
        
        # Récupérer l'email
        print("\n⏳ Récupération du profil utilisateur...")
        email = get_user_profile(service)
        
        if email:
            print(f"\n✅ SUCCÈS ! Connecté à : {email}")
            print("\n📧 Vous êtes maintenant connecté à Gmail API")
            print("💾 Un fichier 'token.json' a été créé pour les connexions futures")
            print("\n" + "=" * 60)
            print("✨ Étape 1 terminée - Prêt pour l'Étape 2 !")
            print("=" * 60)
        else:
            print("❌ Impossible de récupérer l'adresse email")
            exit(1)
            
    except FileNotFoundError:
        print("❌ ERREUR : credentials.json introuvable")
        exit(1)
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        exit(1)
