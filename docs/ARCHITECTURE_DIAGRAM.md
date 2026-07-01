# 🏗️ Diagramme d'architecture Flask

## Vue globale du système

```
┌─────────────────────────────────────────────────────────────────┐
│                         Navigateur Web                          │
│                    http://localhost:5000                        │
└────────────────────────┬──────────────────────────────────────┘
                         │
                    HTTP(S) Requests
                         │
         ┌───────────────┴──────────────────┐
         │                                  │
    ┌────▼─────┐                    ┌──────▼──────┐
    │  route   │                    │  templates  │
    │  /login  │◄────────────────►  │ base.html   │
    │  /emails │                    │ emails.html │
    │/collected│                    │collected.html
    └────┬─────┘                    └─────────────┘
         │
    app.py (Flask)
         │
    ┌────┴──────────────────────┐
    │                           │
    │   session['user_']        │
    │   session['credentials']  │ 📦 En mémoire navigateur
    │                           │
    └────┬──────────────────────┘
         │
    ┌────▼────────────────────────────────┐
    │         Gmail Utils & Service       │
    │                                     │
    │  gmail_utils.py:                    │ 🔌 Réutilise step1
    │  ├─ get_authorization_url()        │
    │  ├─ credentials_from_auth_code()   │
    │  └─ deserialize_credentials()      │
    │                                     │
    │  gmail_service.py:                 │ 🔌 Réutilise step2
    │  ├─ fetch_gmail_labels()           │
    │  ├─ fetch_emails_list()            │
    │  └─ extract_email_data()           │
    │                                     │
    └────┬──────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Google Gmail API                │
    │                                   │
    │  GET /users/me/labels/            │
    │  GET /users/me/messages/          │
    │  GET /users/me/messages/{id}/     │
    │                                   │
    └───────────────────────────────────┘
         │
    ┌────▼────────────────────┐
    │   database.py           │ 💾 Persistance
    │                         │
    │  users:                 │
    │  ├─ id_user (PK)        │
    │  ├─ email               │
    │  ├─ token (JSON)        │
    │  └─ date_created        │
    │                         │
    │  emails:                │
    │  ├─ id (PK)             │
    │  ├─ id_user (FK)        │
    │  ├─ msg_id              │
    │  ├─ label               │
    │  ├─ expediteur          │
    │  ├─ objet               │
    │  ├─ ip, spf, dkim, etc  │
    │  └─ date_collecte       │
    │                         │
    └────┬────────────────────┘
         │
    ┌────▼────────────────────┐
    │   spam_detector.db      │
    │   (SQLite)              │
    └─────────────────────────┘
```

---

## Flux détaillé : authentification

```
Utilisateur                    App Flask                    Google OAuth
     │                             │                              │
     ├──── Visite localhost:5000 ──►│                              │
     │                             │                              │
     │                             ├─── Génère auth URL ─────────►│
     │                             │    (credentials.json)         │
     │                             │                              │
     │◄────── Redirige vers Google ┤                              │
     │        (auth URL)           │                              │
     │                             │                              │
     ├─── Accepte la permission ──────────────────────────────────►│
     │                             │                              │
     │                             │◄─ Google envoie code ────────┤
     │                             │    /auth/callback?code=...   │
     │                             │                              │
     │                             ├─ Échange code → token       │
     │                             │  (credentials_from_auth_code)│
     │                             │                              │
     │                             ├─ Crée user en BD            │
     │                             │  (get_or_create_user)        │
     │                             │                              │
     │                             ├─ Sauvegarde token en BD     │
     │                             │  (update_user_token)         │
     │                             │                              │
     │                             ├─ Sauvegarde en session      │
     │                             │  (session['user_credentials'])
     │                             │                              │
     │◄────── Redirige vers /emails ──────────────────────────────┤
     │
     ├─ Affiche INBOX + SPAM (avec checkboxes)
```

---

## Flux détaillé : collecte d'emails

```
┌─────────────────────────────────────────────────────────────┐
│ Route /emails - Affichage                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Récupère credentials de session['user_credentials']    │
│  2. Construit service Gmail avec deserialize_credentials() │
│  3. Appelle fetch_gmail_labels() → {'INBOX': '1', ...}    │
│  4. Appelle fetch_emails_list(labels['INBOX'], 20)        │
│     → ['msg_id_1', 'msg_id_2', ...]                       │
│  5. Affiche la template avec checkboxes                    │
│  6. Récupère emails déjà collectés depuis BD               │
│     → Marque les emails comme "déjà collectés"            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         │
                    Utilisateur sélectionne
                         │
┌─────────────────────────────────────────────────────────────┐
│ POST /collect - Collecte (AJAX)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Reçoit JSON: {"message_ids": ['msg_id_1', 'msg_id_2']} │
│  2. Récupère credentials de session                        │
│  3. Pour chaque message_id:                                │
│     a. Appelle extract_email_data()                        │
│        → {msg_id, label, expediteur, objet, ip, spf, dkim}│
│     b. Appelle save_email()                                │
│        → INSERT OR IGNORE (évite doublons)                │
│  4. Retourne JSON: {"success": true, "collected": 5}       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Flux détaillé : affichage des collectés

```
┌──────────────────────────────────────────────────┐
│ Route /collected - Affichage                     │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Récupère session['user_id']                 │
│  2. Appelle get_user_emails(user_id)            │
│  3. Récupère tous les emails de cet utilisateur │
│     (WHERE id_user = session['user_id'])        │
│  4. Affiche tableau avec :                      │
│     - label (INBOX vs SPAM)                     │
│     - expediteur, objet, ip, spf, dkim         │
│     - date_collecte                             │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Réutilisation du code existant

### step1_connect.py → gmail_utils.py

```python
AVANT (step1_connect.py):
├─ authenticate_gmail()        → Lit token.json, lance OAuth si nécessaire
├─ get_user_profile(service)   → Récupère l'email

APRÈS (gmail_utils.py):
├─ get_authorization_url()             → Génère l'URL OAuth
├─ credentials_from_auth_code(code)    → Récupère le token
├─ serialize_credentials(creds)        → Pour la session
├─ deserialize_credentials(dict)       → Depuis la session
├─ get_user_email(creds)               → Récupère l'email
└─ get_gmail_service(creds)            → Construit le service

✅ Logique identique, mais adaptée pour Flask (session au lieu de fichier)
```

### step2_collect.py → gmail_service.py

```python
AVANT (step2_collect.py):
├─ load_credentials()                  → Charge token.json
├─ get_header_value(headers, field)    → Extrait un header
├─ extract_ip_from_received()          → Parse l'IP
├─ extract_spf_from_header()           → Parse SPF
├─ extract_dkim_from_header()          → Parse DKIM
├─ extract_links_from_body()           → Extrait les URLs
├─ collect_emails_from_label()         → Collecte depuis Gmail
└─ save_to_csv()                       → Sauvegarde en CSV

APRÈS (gmail_service.py):
├─ fetch_gmail_labels()                → Récupère les labels
├─ fetch_emails_list()                 → Récupère les IDs
├─ extract_email_data()                → Extrait les données d'un email
├─ collect_emails_from_gmail()         → Collecte plusieurs emails
└─ (Fonctions helpers: get_header_value, extract_ip, extract_spf, extract_dkim, extract_links)

✅ Code identique, appelé par app.py au lieu du script principal
```

---

## Comment les modules parlent entre eux

```
app.py (main)
├─ Importe gmail_utils
│  └─ Appelle: get_authorization_url(), credentials_from_auth_code(),
│              deserialize_credentials(), get_user_email()
│
├─ Importe gmail_service
│  └─ Appelle: fetch_gmail_labels(), fetch_emails_list(),
│              extract_email_data(), collect_emails_from_gmail()
│
└─ Importe database
   └─ Appelle: init_database(), get_or_create_user(),
               update_user_token(), save_email(), get_user_emails()
```

---

## Intégration step3_analyse.py

Prochaine étape : ajouter une route `/analyze` qui :

```
app.py
├─ Importe step3_analyse ou crée un module analysis.py
│  (réutilise SpamAnalyzer)
│
├─ Nouvelle route: @app.route('/analyze/<int:email_id>')
│  └─ Récupère email de la BD
│     Analyse avec SpamAnalyzer
│     Sauvegarde résultats en colonne "analysis"
│     Affiche le diagnostic
│
└─ Modifie template collected.html
   └─ Ajoute colonne: Score spam, Classification, Raison
```

---

## Points de sécurité à vérifier

```
✅ Authentification
   - OAuth2 Google (sécurisé par Google)
   - Token stocké en session (pas en fichier)
   - CSRF token implicite (Flask-Session)

⚠️  À améliorer en production
   - HTTPS obligatoire (adhoc SSL OK pour dev)
   - SECRET_KEY aléatoire (pas hard-coded)
   - Rate limiting sur /collect
   - Chiffrer les tokens en BD (si persistance)
   - Valider l'email_id avant accès (belongsToUser check)
```

---

**Architecture solide et extensible ! 🚀**
