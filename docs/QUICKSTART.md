# 🚀 Guide de démarrage — Interface Web Flask

## ✅ Prérequis

- ✅ Python 3.11+ installé
- ✅ `credentials.json` dans le dossier (depuis Google Cloud Console)
- ✅ Virtual environment créé (`.venv`)

---

## 📦 Installation rapide

### 1. Installer les dépendances Flask

```bash
# Activer l'environnement virtuel
cd "c:\Users\pc\Desktop\projet stage\spam-detector"
& ".\.venv\Scripts\Activate.ps1"

# Installer les packages
pip install -r requirements.txt
```

### 2. Initialiser la base de données

```bash
python -c "from database import init_database; init_database(); print('✅ BD initialisée')"
```

---

## 🎬 Lancer l'application

### Démarrer Flask en développement

```bash
python app.py
```

Vous devriez voir :
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://localhost:5000
```

### Accéder à l'interface

Ouvrez votre navigateur et allez sur : **http://localhost:5000**

---

## 🔐 Flux de test

### 1. Cliquez sur "Se connecter avec Gmail"

- Vous êtes redirigé vers Google
- Google vous demande de vous identifier (hindourrach27@gmail.com)
- Acceptez l'accès aux emails

### 2. Sélectionnez vos emails

- Vous voyez la liste des 20 emails INBOX + 20 SPAM
- Cochez ceux que vous voulez collecter
- Cliquez "Collecter"

### 3. Vérifiez la collecte

- Allez sur "Voir les emails collectés"
- Vous voyez votre table SQLite avec toutes les données

---

## 🗂️ Structure des fichiers créés

```
spam-detector/
├── gmail_utils.py               # OAuth2 réutilisé de step1
├── gmail_service.py             # Collecte réutilisée de step2
├── database.py                  # Gestion SQLite
├── app.py                       # Routes Flask
├── requirements.txt             # Dépendances
├── spam_detector.db             # Base SQLite (créée auto)
│
├── templates/
│   ├── base.html               # Template de base
│   ├── emails.html             # Page de sélection
│   └── collected.html          # Page de résultats
│
└── FLASK_ARCHITECTURE.md       # Documentation complète
```

---

## 🧪 Tests rapides

### Vérifier que tout est OK

```bash
# Test 1: Authentification
python -c "from gmail_utils import get_authorization_url; print('✅ OAuth2 OK')"

# Test 2: BD SQLite
python -c "from database import init_database, get_or_create_user; init_database(); user = get_or_create_user('test@gmail.com'); print(f'✅ BD OK (user_id={user})')"

# Test 3: Gmail Service
python -c "from gmail_service import fetch_gmail_labels; print('✅ Gmail Service OK')"
```

---

## ❌ Dépannage

### "credentials.json introuvable"

```bash
# Solution: Téléchargez-le depuis Google Cloud Console
# https://console.cloud.google.com/apis/credentials
# 1. Sélectionnez votre projet
# 2. Créez des identifiants OAuth 2.0 (Application de bureau)
# 3. Téléchargez le JSON
# 4. Renommez-le en "credentials.json"
```

### "Port 5000 déjà utilisé"

```bash
# Solution: Changez le port dans app.py (dernière ligne)
# Remplacez:
app.run(debug=True, host='localhost', port=5000)
# Par:
app.run(debug=True, host='localhost', port=5001)
```

### "ImportError: No module named 'flask'"

```bash
# Solution: Réinstallez les dépendances
pip install -r requirements.txt --force-reinstall
```

### "Aucun email ne s'affiche"

```bash
# Vérifiez que le token est valide
# Allez sur http://localhost:5000/logout
# Puis http://localhost:5000/login
# Réauthentifiez-vous
```

---

## 📊 Prochaines étapes

### Intégrer l'analyse spam (step3_analyse.py)

Route `/analyze` pour analyser les emails collectés :

```python
@app.route('/analyze/<int:email_id>')
def analyze_email(email_id):
    # Charger l'email de la BD
    # Lancer l'analyseur spam
    # Afficher les résultats
    pass
```

### Afficher le diagnostic dans l'interface

Ajouter une colonne "Score de spam" dans la table `collected.html`.

### Export et rapports

Routes pour exporter en CSV/JSON avec filtres (INBOX vs SPAM).

---

## 🎯 Résumé commandes

```bash
# Activer l'environnement
& ".\.venv\Scripts\Activate.ps1"

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
python app.py

# Tester (optionnel)
python -c "from database import init_database; init_database(); print('✅')"

# Arrêter l'app (dans le terminal Flask)
Ctrl+C
```

---

**Bon test ! 🚀 Si vous avez des questions, j'suis là pour aider.**
