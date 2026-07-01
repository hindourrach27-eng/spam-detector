# 🌐 Interface Web Flask — Système de Diagnostic Spam

## Architecture

La migration de scripts autonomes vers Flask réutilise le code existant :

```
spam-detector/
├── step1_connect.py          ← Script original (conservé)
├── step2_collect.py          ← Script original (conservé)
├── step3_analyse.py          ← Script original (conservé)
│
├── gmail_utils.py            ← 🆕 Réutilise step1 adapté pour Flask
├── gmail_service.py          ← 🆕 Réutilise step2 adapté pour Flask
├── database.py               ← 🆕 Gestion SQLite (users + emails)
├── app.py                    ← 🆕 Routes Flask principales
│
├── templates/
│   ├── base.html             ← 🆕 Template de base
│   ├── emails.html           ← 🆕 Sélection et collecte d'emails
│   └── collected.html        ← 🆕 Affichage des emails collectés
│
├── spam_detector.db          ← 🆕 Base SQLite (créée automatiquement)
├── requirements.txt          ← 🆕 Dépendances Python
└── README.md                 ← 📝 Ce fichier
```

---

## 🔑 Points clés d'architecture

### 1. **Gestion des tokens par utilisateur**

**Avant (scripts autonomes):**
```python
# step1_connect.py sauvegardait UN SEUL token.json
token.json  ← Fichier unique, UN utilisateur seulement
```

**Après (Flask) :**
```python
# Tokens EN SESSION Flask (par utilisateur)
session['user_credentials'] = {
    'token': '...',
    'refresh_token': '...',
    'token_uri': '...',
    # ...
}

# OU en base SQLite (pour persistance multi-navigateurs)
users.token = JSON.dumps(creds_dict)
```

**Avantage :** Plusieurs utilisateurs peuvent être connectés simultanément sans s'écraser les tokens.

### 2. **Credentials partagé (credentials.json)**

Tous les utilisateurs utilisent le **même credentials.json** :
- ✅ Un seul projet Google Cloud
- ✅ Une seule "identité" d'application
- ✅ Chaque utilisateur a son propre token OAuth2 (distinct)

```
credentials.json  ← Shared par tous les utilisateurs
├── user1@gmail.com → token1.json (EN SESSION)
├── user2@gmail.com → token2.json (EN SESSION)
└── user3@gmail.com → token3.json (EN SESSION)
```

### 3. **Base SQLite (au lieu de CSV)**

**Avant :**
```
dataset_emails.csv  ← Fichier CSV unique
dataset_analyse.csv ← Fichier CSV unique
```

**Après :**
```
spam_detector.db
├── Table: users
│   ├── id_user (PK)
│   ├── email (UNIQUE)
│   ├── token (JSON sérialisé)
│   └── date_created
│
└── Table: emails
    ├── id (PK)
    ├── id_user (FK → users)
    ├── msg_id (UNIQUE per user)
    ├── label (INBOX/SPAM)
    ├── expediteur, objet, ip, spf, dkim, liens
    └── date_collecte
```

**Avantage :** Chaque utilisateur a ses propres emails, pas de mélange.

---

## 🚀 Installation et lancement

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Vérifier que credentials.json existe

```bash
ls credentials.json
# Si absent : téléchargez-le depuis Google Cloud Console
```

### 3. Lancer l'app Flask

```bash
python app.py
```

L'app se lance sur **http://localhost:5000**

---

## 📋 Flux utilisateur

```
1. Utilisateur arrive sur http://localhost:5000
   ↓
2. Est redirigé vers /login
   ↓
3. Clique sur "Se connecter avec Gmail" (lien vers /login)
   ↓
4. Google OAuth2 affiche un écran de consentement
   ↓
5. Utilisateur accepte → Google redirige vers /auth/callback
   ↓
6. /auth/callback :
   - Récupère le code d'autorisation
   - L'échange contre un token
   - Crée l'utilisateur en BD (ou récupère s'il existe)
   - Sauvegarde le token en BD + session
   ↓
7. Utilisateur redirigé vers /emails
   ↓
8. /emails :
   - Affiche 20 emails de INBOX
   - Affiche 20 emails de SPAM
   - Cases à cocher devant chaque email
   ↓
9. Utilisateur sélectionne des emails + clique "Collecter"
   ↓
10. /collect (POST) :
    - Récupère les IDs sélectionnés
    - Extrait les données (expéditeur, objet, IP, SPF, DKIM, etc.)
    - Les insère en BD (INSERT OR IGNORE pour éviter doublons)
    ↓
11. Réponse JSON : "X email(s) collecté(s)"
    ↓
12. Utilisateur clique "Voir les emails collectés"
    ↓
13. /collected : affiche les emails de l'utilisateur en table
```

---

## 📂 Fichiers clés

### `gmail_utils.py` (Authentification OAuth2)

Réutilise et adapte le code de **step1_connect.py** :

```python
# ✅ Créer le flux OAuth2
auth_url, state, flow = get_authorization_url()

# ✅ Récupérer les credentials depuis le code d'auth
creds_dict = credentials_from_auth_code(auth_code)

# ✅ Sérialiser pour la session
creds_serialized = serialize_credentials(creds)

# ✅ Désérialiser pour utiliser
creds = deserialize_credentials(creds_serialized)

# ✅ Récupérer l'email de l'utilisateur
email = get_user_email(creds)
```

### `gmail_service.py` (Collecte)

Réutilise et adapte le code de **step2_collect.py** :

```python
# ✅ Récupérer les labels (INBOX, SPAM)
labels = fetch_gmail_labels(service)

# ✅ Récupérer la liste des IDs de messages
msg_ids = fetch_emails_list(service, label_id, max_results=20)

# ✅ Extraire les données d'un email
email_data = extract_email_data(service, msg_id, label_name)
# Retourne: {msg_id, label, expediteur, objet, ip, spf, dkim, liens}

# ✅ Collecter plusieurs emails
all_emails = collect_emails_from_gmail(creds, message_ids, label_name)
```

### `database.py` (SQLite)

Gère la persistance :

```python
# ✅ Initialiser la BD
init_database()

# ✅ Créer ou récupérer un utilisateur
user_id = get_or_create_user(email)

# ✅ Sauvegarder le token d'un utilisateur
update_user_token(email, creds_dict)

# ✅ Sauvegarder un email collecté
save_email(user_id, msg_id, email_data)
# ← Utilise INSERT OR IGNORE (évite doublons)

# ✅ Récupérer les emails d'un utilisateur
emails = get_user_emails(user_id)
```

### `app.py` (Routes Flask)

Routes principales :

```python
@app.route('/login')                 # Début du flux OAuth
@app.route('/auth/callback')         # Callback Google
@app.route('/emails')                # Affichage des emails
@app.route('/collect', methods=['POST'])  # Collecte (AJAX)
@app.route('/collected')             # Affichage des collectés
@app.route('/logout')                # Déconnexion
```

---

## 🔄 Évolution vers plusieurs utilisateurs

L'architecture est **déjà prête** pour supporter plusieurs utilisateurs test :

### Ajouter un nouvel utilisateur (hindourrach28@gmail.com, par exemple)

1. Aucune modification de code nécessaire ! ✅
2. Le nouvel utilisateur arrive sur http://localhost:5000/login
3. Google OAuth lui demande de se connecter avec SON compte
4. Son token est sauvegardé dans SA session + la BD
5. Il voit SES propres emails
6. ZERO collision avec hindourrach27@gmail.com

### Basculer vers une vraie boîte entreprise

1. Votre encadrant fournit `credentials.json` pour le projet Google Cloud de l'entreprise
2. Remplacez simplement le fichier `credentials.json` local
3. ✅ Tous les utilisateurs continuent de fonctionner
4. Les tokens et emails restent en BD

---

## 🔐 Sécurité

**Points à améliorer en production :**

```python
# ⚠️ À CHANGER dans app.py:

# 1. Secret key aléatoire (pas "dev-secret-key")
app.config['SECRET_KEY'] = os.urandom(24)

# 2. HTTPS obligatoire (pas juste adhoc)
app.run(ssl_context=('cert.pem', 'key.pem'))

# 3. CORS si frontend séparé
from flask_cors import CORS
CORS(app, origins=['https://yourdomain.com'])

# 4. Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: session.get('user_id'))

# 5. Token refresh automatique
if creds.expired:
    refresh_credentials(creds)
```

---

## 📝 Notes pour vous

### Tokens en session vs BD

**Option 1 : Session Flask (actuel)**
- ✅ Simple
- ✅ Pas de persistance disque des secrets
- ❌ Token perdu si l'utilisateur ferme le navigateur

**Option 2 : BD SQLite**
- ✅ Token persiste entre sessions
- ✅ Support multi-onglets
- ❌ Secrets en disque (chiffrer en prod!)

Pour supporter les deux :
```python
# Dans /auth/callback:
session['user_credentials'] = creds_dict  # Session
update_user_token(user_email, creds_dict) # BD
```

### Prochaines étapes

1. ✅ **Étape 4** (prévue) : Intégrer l'analyse spam (step3_analyse.py)
   - Ajouter une route `/analyze` pour analyser les emails collectés
   - Ajouter les colonnes à la table `emails` : score_spam, classification, etc.

2. ✅ **Étape 5** : Afficher le diagnostic dans l'interface
   - Page `/emails/{id}/details` avec les résultats

3. ✅ **Étape 6** : Export et rapports
   - CSV/JSON export avec filters
   - Dashboard avec graphiques

---

## 🎯 Résumé des fichiers nouveaux

| Fichier | Rôle | Réutilise |
|---------|------|-----------|
| `gmail_utils.py` | OAuth2 + sérialisation | step1_connect.py |
| `gmail_service.py` | Extraction d'emails | step2_collect.py |
| `database.py` | Persistance SQLite | — (nouveau) |
| `app.py` | Routes Flask | — (nouveau) |
| `templates/base.html` | Mise en page | — (nouveau) |
| `templates/emails.html` | Sélection d'emails | — (nouveau) |
| `templates/collected.html` | Affichage collectés | — (nouveau) |
| `requirements.txt` | Dépendances | — (nouveau) |

---

**Prêt à tester ? Lancez `python app.py` !** 🚀
