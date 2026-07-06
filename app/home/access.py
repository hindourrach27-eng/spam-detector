"""
app/home/access.py — Resolution centralisee du mode d'acces (Google vs anonyme)

Ce module NE TOUCHE PAS a session['user_email'] / session['user_id'] /
session['user_credentials'], qui restent geres par l'encadrante (OAuth2).
Il ajoute juste session['anon_token'] pour le mode "acces libre".
"""

import uuid
from database import get_or_create_anonymous_user


def get_current_user(session):
    """
    Retourne un dict {id_user, email, mode} quelle que soit la maniere
    dont l'utilisateur est arrive sur la page :

    - mode 'google'  : utilisateur connecte via OAuth2 (session['user_email'] existe)
    - mode 'anonyme' : pas de connexion Google, un id_user "anonyme" est
                        cree/recupere a partir d'un token stocke en session
    """
    if 'user_email' in session:
        return {
            'id_user': session['user_id'],
            'email': session['user_email'],
            'mode': 'google'
        }

    if 'anon_token' not in session:
        session['anon_token'] = uuid.uuid4().hex

    anon_user_id = get_or_create_anonymous_user(session['anon_token'])

    return {
        'id_user': anon_user_id,
        'email': None,
        'mode': 'anonyme'
    }


def is_google_mode(session):
    """Pratique pour les templates/routes qui doivent juste savoir si
    l'utilisateur est connecte via Google (accès complet)."""
    return 'user_email' in session