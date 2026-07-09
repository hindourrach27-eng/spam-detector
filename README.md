# Système de Diagnostic Spam — E Market Solutions

Application web de diagnostic anti-spam développée pour **E Market Solutions (EMS)**, permettant de collecter, analyser et tester des emails afin de détecter le spam, le phishing et les tentatives de fraude — via une analyse heuristique (SPF/DKIM/DMARC) et une analyse par intelligence artificielle locale.

## Fonctionnalités

- **Connexion Google (OAuth2)** : collecte et analyse des emails Gmail réels de l'utilisateur.
- **Analyse heuristique** : vérification technique (SPF, DKIM, DMARC, IP, mots suspects, liens).
- **Analyse par IA locale (Ollama)** : diagnostic avancé du contenu d'un email ou d'une offre commerciale simulée.
- **Simulateur d'offre** : teste une offre commerciale fictive avant envoi pour vérifier si elle serait perçue comme du spam, avec détection de texte caché dans le code HTML.
- **Double mode d'accès** :
  - *Connecté (Google)* : accès complet (Mes emails, Collecte, Analyse heuristique, Simulateur, Historique, Statistiques, Glossaire).
  - *Invité (sans connexion)* : accès limité (Simulateur, Historique, Statistiques, Glossaire), sans lier de compte Google.
- **Historique des simulations** avec export en rapport PDF.
- **Statistiques** comparant l'analyse heuristique et les résultats du simulateur IA.

## Stack technique

- **Backend** : Python 3.11+, Flask, Flask-Session
- **Base de données** : SQLite
- **Frontend** : AdminLTE + Bootstrap 4, Jinja2
- **Authentification** : Google OAuth2 (Gmail API, scope `gmail.readonly`)
- **IA** : [Ollama](https://ollama.com) (modèle `qwen2.5`, en local — aucune donnée envoyée à un service tiers)
- **Génération de rapports** : ReportLab (PDF)

## Prérequis

- Python 3.11 ou supérieur
- [Ollama](https://ollama.com/download) installé et lancé localement
- Un projet Google Cloud avec un identifiant OAuth 2.0 (type "Application Web") et l'API Gmail activée

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/hindourrach27-eng/spam-detector.git
cd spam-detector
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv .venv
```

Windows (PowerShell) :
```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux :
```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
python -m pip install beautifulsoup4 ollama reportlab
```

### 4. Configurer les identifiants Google OAuth2

1. Crée un projet sur [Google Cloud Console](https://console.cloud.google.com/).
2. Active l'**API Gmail**.
3. Crée un identifiant OAuth 2.0 de type **Application Web**.
4. Ajoute `http://localhost:5000/auth/callback` dans les **URI de redirection autorisés**.
5. Télécharge le fichier JSON des identifiants et place-le à la racine du projet sous le nom **`credentials.json`** (ce fichier est ignoré par Git — ne jamais le commiter).

### 5. Télécharger le modèle IA

```bash
ollama pull qwen2.5:3b
```

> Le modèle `qwen2.5:7b` offre une meilleure qualité d'analyse mais nécessite ~5-6 Go de RAM libre. Sur une machine avec moins de RAM, `qwen2.5:3b` (~2-3 Go) est recommandé — le nom du modèle utilisé se configure dans `clean_text.py`.

### 6. Lancer l'application

```bash
python run.py
```

Ouvre ensuite [http://localhost:5000](http://localhost:5000) dans ton navigateur.

## Structure du projet
spam-detector/
├── app/
│   ├── init.py
│   └── home/
│       ├── routes.py       # Routes Flask
│       └── access.py       # Gestion du double mode d'acces (Google / invite)
├── templates/              # Templates Jinja2 (AdminLTE)
├── static/                 # Assets (CSS, JS, images)
├── database.py             # Acces a la base SQLite
├── gmail_utils.py          # Authentification Google OAuth2
├── gmail_service.py        # Collecte des emails Gmail
├── spam_analyzer.py        # Analyse heuristique (SPF/DKIM/DMARC)
├── clean_text.py           # Nettoyage de texte + appel a l'IA (Ollama)
├── rapport_pdf.py          # Generation des rapports PDF
├── run.py                  # Point d'entree de l'application
└── requirements.txt

## Sécurité et confidentialité

- L'authentification passe exclusivement par le protocole officiel **OAuth2 de Google** : l'application ne stocke jamais de mot de passe.
- Le scope demandé (`gmail.readonly`) permet uniquement la **lecture** des emails : aucune suppression ni envoi n'est possible depuis l'application.
- L'analyse par intelligence artificielle s'exécute **entièrement en local** via Ollama : aucun email n'est transmis à un service tiers.

## À propos

**E Market Solutions (SARL)** — Fondée à Fès en juin 2015, spécialisée dans la publicité par e-mail et le marketing digital.

📍 Rue Abbas Mahmoud Akkad, Hay Qods, Ville Nouvelle, Bureau Amin, 2ème et 3ème étage — 30000 Fès
📞 05 35 93 19 69
✉️ emscontact1@gmail.com