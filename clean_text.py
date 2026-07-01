"""
clean_text.py — Nettoyage du texte des emails collectés
Script separe : lit la base, nettoie le body (HTML, encodage, troncature),
ecrit le resultat dans la colonne body_clean (le body brut original
n'est jamais modifie).
A executer manuellement : python clean_text.py
"""

import re
import json
import time
import unicodedata
from bs4 import BeautifulSoup
import ollama

from database import (
    get_emails_to_clean, save_body_clean, get_email_full_for_ai,
    get_emails_to_analyze_ia, get_emails_to_analyze_ia_test, save_analyse_ia
)

# Limite de troncature : ~32k tokens pour Qwen2.5.
# Approximation prudente : 1 token ~ 4 caracteres -> 32000 * 4 = 128000
# On reste plus prudent avec une limite plus basse pour laisser de la
# place a l'objet/headers qui seront assembles plus tard.
MAX_CARACTERES = 20000

# Seuil en-dessous duquel on considere le body_clean comme "trop pauvre"
# pour etre soumis a l'IA normalement (cause connue de blocages/timeouts)
SEUIL_BODY_VIDE = 20

# IDs des emails choisis comme exemples few-shot (diversite : legitime,
# spam par incoherence d'expediteur, spam par obfuscation, cas ambigu)
FEW_SHOT_IDS = {
    561: {
        'verdict': 'legitime',
        'raison': "Authentification SPF/DKIM/DMARC toutes valides, contenu coherent et substantiel, aucune incoherence d'expediteur."
    },
    1781: {
        'verdict': 'spam',
        'raison': "Incoherence flagrante entre le nom affiche ('NPR', une radio connue) et le domaine reel de l'expediteur (rapidactionbusiness.com), qui n'a aucun rapport. Absence de DMARC malgre SPF/DKIM valides."
    },
    5924: {
        'verdict': 'spam',
        'raison': "Objet contenant des caracteres speciaux meles aux lettres (obfuscation classique : 'Sp@am14728/&'), technique utilisee pour contourner les filtres anti-spam bases sur les mots-cles."
    },
    622: {
        'verdict': 'suspect',
        'raison': "SPF/DKIM/DMARC tous a 'Unknown' (authentification non confirmee, ni positive ni negative), bien que le contenu et l'expediteur semblent coherents. Necessite une prudence sans conclure au spam par defaut."
    },
}


def remove_html_noise(raw_text):
    """Retire les balises HTML (div, style, script, etc.) et garde le texte lisible"""
    if not raw_text:
        return ''

    try:
        soup = BeautifulSoup(raw_text, 'html.parser')

        for balise in soup(['script', 'style', 'head', 'meta', 'link']):
            balise.decompose()

        texte = soup.get_text(separator=' ')
        texte = re.sub(r'\s+', ' ', texte).strip()

        return texte
    except Exception as e:
        print(f"⚠️ Erreur remove_html_noise : {e}")
        return raw_text


def normalize_encoding(text):
    """Normalise l'encodage du texte (UTF-8, gere arabe/francais correctement)"""
    if not text:
        return ''

    try:
        texte_normalise = unicodedata.normalize('NFC', text)
        return texte_normalise
    except Exception as e:
        print(f"⚠️ Erreur normalize_encoding : {e}")
        return text


def truncate_text(text, max_length=MAX_CARACTERES):
    """Tronque le texte s'il depasse la limite, pour respecter le contexte de l'IA"""
    if not text:
        return ''

    if len(text) <= max_length:
        return text

    return text[:max_length] + ' [...TRONQUE...]'


def clean_body(raw_body):
    """Pipeline complet de nettoyage : HTML -> encodage -> troncature"""
    texte = remove_html_noise(raw_body)
    texte = normalize_encoding(texte)
    texte = truncate_text(texte)
    return texte


def build_model_input(email):
    """
    Assemble headers + From/Subject + body_clean en un seul bloc de texte,
    pret a etre envoye au modele IA (Ollama/Groq).
    """
    ip = email.get('ip') or 'inconnue'
    spf = email.get('spf') or 'Unknown'
    dkim = email.get('dkim') or 'Unknown'
    dmarc = email.get('dmarc') or 'Unknown'
    expediteur = email.get('expediteur') or 'inconnu'
    objet = email.get('objet') or '(sans objet)'
    body_clean = email.get('body_clean') or ''

    bloc = (
        f"IP: {ip}\n"
        f"SPF: {spf}\n"
        f"DKIM: {dkim}\n"
        f"DMARC: {dmarc}\n"
        f"From: {expediteur}\n"
        f"Subject: {objet}\n"
        f"\n"
        f"{body_clean}"
    )

    return bloc


def get_few_shot_examples():
    """
    Recupere les emails choisis comme exemples few-shot et construit
    le bloc de texte a inserer dans le prompt, avant le nouvel email
    a analyser.
    """
    blocs = []
    for email_id, info in FEW_SHOT_IDS.items():
        email = get_email_full_for_ai(email_id)
        if not email:
            continue

        model_input = build_model_input(email)
        bloc = (
            f"--- Exemple ---\n"
            f"{model_input}\n\n"
            f"Diagnostic attendu : verdict=\"{info['verdict']}\"\n"
            f"Raison : {info['raison']}\n"
        )
        blocs.append(bloc)

    return "\n".join(blocs)


def build_ai_prompt(model_input, label_gmail=None):
    """
    Construit le prompt complet envoye a l'IA, incluant des exemples
    few-shot, les instructions, et le bloc de texte de l'email a analyser.

    label_gmail (optionnel) : 'INBOX' ou 'SPAM'. Donne a l'IA le contexte
    du dossier Gmail d'origine, sans dicter sa conclusion.
    """
    contexte_label = ""
    if label_gmail == 'SPAM':
        contexte_label = (
            "\nNote de contexte : Gmail a classe cet email dans son dossier SPAM. "
            "Gmail ne classe jamais un email en spam sans raison technique ou "
            "comportementale (reputation du domaine, plaintes, contenu suspect, "
            "incoherences d'authentification, etc.), meme si le corps du texte "
            "visible semble court, vide ou peu suspect en apparence. "
            "Examine attentivement les headers (incoherence entre le nom affiche "
            "et le domaine reel de l'expediteur, absence de DMARC malgre SPF/DKIM "
            "valides, etc.) avant de conclure que l'email est legitime. Si tu ne "
            "trouves vraiment aucun signal suspect malgre cet examen attentif, tu "
            "peux tout de meme conclure 'legitime' — l'objectif est la rigueur, "
            "pas de confirmer automatiquement le classement de Gmail.\n"
        )

    exemples = get_few_shot_examples()

    prompt = f"""Tu es un expert en cybersecurite et en detection de spam/phishing.
Voici quelques exemples d'emails deja diagnostiques, pour t'aider a comprendre le pattern attendu :

{exemples}

Analyse maintenant le NOUVEL email ci-dessous (headers d'authentification + expediteur + objet + corps) et donne ton diagnostic, en suivant le meme type de raisonnement que dans les exemples.
{contexte_label}
Reponds UNIQUEMENT avec un objet JSON valide, sans aucun texte avant ou apres, au format exact suivant :
{{
  "verdict": "spam" ou "legitime",
  "score": un nombre entier de 0 a 100 (0 = totalement legitime, 100 = spam evident),
  "score_explication": une phrase courte en francais expliquant precisement pourquoi ce score a ete attribue (quels facteurs ont le plus pese : authentification, contenu, incoherence expediteur, etc.),
  "label_phishing": true ou false (l'email tente-t-il de voler des identifiants ou informations sensibles, ex: fausse page de connexion, demande de mot de passe ?),
  "label_spoofing": true ou false (UNIQUEMENT si le nom affiche dans le champ From -avant le symbole @ ou entre guillemets- correspond a une marque/organisation connue qui NE CORRESPOND PAS au domaine reel apres le @, comme dans l'exemple id=1781 ou "NPR" est affiche mais le domaine est rapidactionbusiness.com. Si le nom affiche et le domaine sont coherents entre eux -meme si le contenu de l'email est promotionnel, urgent ou commercial-, label_spoofing DOIT etre false. Un ton vendeur, pressant ou alarmiste n'est PAS du spoofing en soi -c'est au mieux du bulk ou du scam-, sauf si combine a une incoherence reelle et verifiable entre le nom affiche et le domaine.),
  "label_scam": true ou false (l'email propose-t-il une arnaque financiere, ex: gain d'argent, heritage, investissement douteux ?),
  "label_bulk": true ou false (l'email ressemble-t-il a un envoi de masse non personnalise, ex: newsletter publicitaire generique sans lien avec un compte ou une action specifique du destinataire ?),
  "harmful_elements": une liste de chaines de texte courtes decrivant les elements suspects trouves (vide si aucun),
  "recommendation": une phrase en francais expliquant comment ameliorer cet email pour eviter qu'il soit classe comme spam (vide si l'email est legitime)
}}

Un email peut avoir plusieurs de ces labels a true en meme temps, ou aucun si l'email est legitime.

Nouvel email a analyser :
---
{model_input}
---

Reponds uniquement avec le JSON, rien d'autre."""
    return prompt


def analyze_with_ollama(model_input, label_gmail=None):
    """
    Envoie le bloc de texte a Ollama (Qwen2.5) et parse la reponse JSON.
    Abandonne automatiquement apres 600s si Ollama ne repond pas,
    pour ne jamais bloquer tout le traitement sur un seul email.
    keep_alive='30m' : garde le modele charge en RAM 30 minutes apres
    cet appel, pour eviter de devoir le recharger (5.1 GB, ~400-600s)
    si on relance le script peu de temps apres pour le lot suivant.

    Retourne un tuple (resultat, type_erreur) :
    - (dict, None) si succes
    - (None, 'timeout') si Ollama n'a pas repondu dans les 600s
    - (None, 'json_invalide') si la reponse n'etait pas un JSON valide
    - (None, 'erreur_autre') pour tout autre probleme (connexion, etc.)
    """


    prompt = build_ai_prompt(model_input, label_gmail=label_gmail)

    try:
        client = ollama.Client(timeout=900)
        response = client.chat(
            model='qwen2.5:7b',
            messages=[{'role': 'user', 'content': prompt}],
            format='json',
            keep_alive='30m',
            #options={'num_ctx': 4096}
        )
        contenu = response['message']['content']
        resultat = json.loads(contenu)
        return resultat, None
    except json.JSONDecodeError as e:
        print(f"⚠️ Reponse IA non-JSON : {e}")
        return None, 'json_invalide'
    except Exception as e:
        message = str(e).lower()
        if 'timed out' in message or 'timeout' in message:
            print(f"⏱️ Timeout appel Ollama : {e}")
            return None, 'timeout'
        print(f"❌ Erreur appel Ollama : {e}")
        return None, 'erreur_autre'


def build_fallback_result(email):
    """
    Construit un resultat par defaut SANS appeler l'IA, pour les emails
    dont le body_clean est vide ou trop court (cause connue de
    blocages/timeouts). Se base uniquement sur les headers et le label
    Gmail, de facon prudente.
    """
    label_gmail = email.get('label')
    spf = email.get('spf')
    dkim = email.get('dkim')
    dmarc = email.get('dmarc')

    auth_ok = (spf == 'pass' and dkim == 'pass')

    if label_gmail == 'SPAM':
        # Gmail a deja detecte un signal fort ; sans texte a analyser,
        # on fait confiance prudemment au label Gmail
        verdict = 'spam'
        score = 60
        elements = ["Corps de l'email vide ou illisible (template tronque a la collecte)",
                    "Classe par Gmail dans le dossier spam"]
        reco = "Verifier manuellement cet email : le contenu n'a pas pu etre analyse automatiquement."
    else:
        verdict = 'legitime'
        score = 20
        elements = []
        reco = ''

    return {
        'verdict': verdict,
        'score': score,
        'label_phishing': False,
        'label_spoofing': not auth_ok,
        'label_scam': False,
        'label_bulk': False,
        'harmful_elements': elements,
        'recommendation': reco
    }


def analyze_email_with_fallback(email):
    """
    Point d'entree unique pour analyser un email avec l'IA :
    - si body_clean est vide/trop court -> resultat par defaut (rapide,
      pas d'appel IA, evite les blocages/timeouts observes)
    - sinon -> appel normal a Ollama

    Retourne un tuple (resultat, source) :
    - source = 'fallback' si body_clean vide/court (pas d'appel IA)
    - source = 'ollama' si reponse reelle de l'IA
    - source = 'timeout' / 'json_invalide' / 'erreur_autre' si echec IA
    """
    body_clean = email.get('body_clean') or ''

    if len(body_clean.strip()) < SEUIL_BODY_VIDE:
        print(f"   ⚠️ id={email.get('id')} : body_clean vide/court ({len(body_clean.strip())} car.) -> fallback sans IA")
        return build_fallback_result(email), 'fallback'

    model_input = build_model_input(email)
    resultat, type_erreur = analyze_with_ollama(model_input, label_gmail=email.get('label'))

    if resultat is not None:
        return resultat, 'ollama'
    return None, type_erreur


def run_cleaning():
    """Lance le nettoyage sur tous les emails dont body_clean est encore vide"""
    print("=" * 70)
    print("🧹 Nettoyage du texte des emails — body -> body_clean")
    print("=" * 70)

    emails = get_emails_to_clean()
    total = len(emails)

    if total == 0:
        print("✅ Aucun email a nettoyer (tout est deja fait, ou base vide)")
        return

    print(f"\n📋 {total} email(s) a nettoyer...")

    nb_succes = 0
    nb_echecs = 0

    for idx, email in enumerate(emails, 1):
        try:
            body_clean = clean_body(email['body'])
            if save_body_clean(email['id'], body_clean):
                nb_succes += 1
            else:
                nb_echecs += 1
        except Exception as e:
            print(f"❌ Erreur sur l'email id={email['id']} : {e}")
            nb_echecs += 1

        if idx % 100 == 0:
            print(f"   ... {idx}/{total} traites")

    print("\n" + "=" * 70)
    print(f"✨ Nettoyage termine")
    print(f"   ✅ Succes : {nb_succes}")
    print(f"   ❌ Echecs : {nb_echecs}")
    print("=" * 70)


def run_ia_analysis():
    """Lance l'analyse IA sur TOUS les emails dont verdict_ia est encore vide.
    A utiliser plus tard, une fois le timing valide via run_ia_analysis_test()."""
    print("=" * 70)
    print("🤖 Analyse IA des emails — verdict_ia, score_ia, etc.")
    print("=" * 70)

    emails = get_emails_to_analyze_ia()
    total = len(emails)

    if total == 0:
        print("✅ Aucun email a analyser (tout est deja fait, ou base vide)")
        return

    print(f"\n📋 {total} email(s) a analyser avec l'IA...")

    nb_succes = 0
    nb_echecs = 0

    for idx, email in enumerate(emails, 1):
        try:
            resultat_ia, source = analyze_email_with_fallback(email)

            if resultat_ia and save_analyse_ia(email['id'], resultat_ia):
                nb_succes += 1
            else:
                nb_echecs += 1
        except Exception as e:
            print(f"❌ Erreur sur l'email id={email['id']} : {e}")
            nb_echecs += 1

        if idx % 10 == 0:
            print(f"   ... {idx}/{total} traites")

    print("\n" + "=" * 70)
    print(f"✨ Analyse IA terminee")
    print(f"   ✅ Succes : {nb_succes}")
    print(f"   ❌ Echecs : {nb_echecs}")
    print("=" * 70)


def run_ia_analysis_test():
    """Version de test : analyse seulement 5 emails, pour chronometrer"""
    print("=" * 70)
    print("🤖 TEST — Analyse IA sur un petit echantillon")
    print("=" * 70)

    emails = get_emails_to_analyze_ia_test(limite=5)
    total = len(emails)

    if total == 0:
        print("✅ Aucun email a analyser")
        return

    print(f"\n📋 {total} email(s) a analyser...")

    debut = time.time()

    for idx, email in enumerate(emails, 1):
        t0 = time.time()
        resultat_ia, source = analyze_email_with_fallback(email)
        duree = time.time() - t0

        if resultat_ia:
            save_analyse_ia(email['id'], resultat_ia)
            print(f"   [{idx}/{total}] id={email['id']} -> {resultat_ia.get('verdict')} [source={source}] ({duree:.1f}s)")
        else:
            print(f"   [{idx}/{total}] id={email['id']} -> ECHEC [raison={source}] ({duree:.1f}s)")

    duree_totale = time.time() - debut
    print(f"\n✅ Termine en {duree_totale:.1f}s ({duree_totale/total:.1f}s par email en moyenne)")


def run_ia_analysis_sample():
    """Lance l'analyse IA sur l'echantillon representatif (par petits lots)"""
    from database import get_emails_for_ia_sample

    print("=" * 70)
    print("🤖 Analyse IA sur un lot de l'echantillon representatif")
    print("=" * 70)

    emails = get_emails_for_ia_sample(n_inbox=4, n_spam=1)
    total = len(emails)

    if total == 0:
        print("✅ Aucun email a analyser")
        return

    print(f"\n📋 {total} email(s) a analyser...")

    debut = time.time()
    nb_succes = 0
    nb_echecs = 0
    # Compteurs detailles pour le bilan final
    compteur_sources = {'fallback': 0, 'ollama': 0, 'timeout': 0, 'json_invalide': 0, 'erreur_autre': 0}

    for idx, email in enumerate(emails, 1):
        t0 = time.time()
        try:
            resultat_ia, source = analyze_email_with_fallback(email)
            duree = time.time() - t0
            compteur_sources[source] = compteur_sources.get(source, 0) + 1

            if resultat_ia and save_analyse_ia(email['id'], resultat_ia):
                nb_succes += 1
                print(f"   [{idx}/{total}] id={email['id']} -> {resultat_ia.get('verdict')} [source={source}] ({duree:.1f}s)")
            else:
                nb_echecs += 1
                print(f"   [{idx}/{total}] id={email['id']} -> ECHEC [raison={source}] ({duree:.1f}s)")
        except Exception as e:
            print(f"❌ Erreur sur l'email id={email['id']} : {e}")
            nb_echecs += 1

    duree_totale = time.time() - debut
    print("\n" + "=" * 70)
    print(f"✨ Lot termine en {duree_totale/60:.1f} minutes")
    print(f"   ✅ Succes : {nb_succes}")
    print(f"   ❌ Echecs : {nb_echecs}")
    print(f"   Detail : ollama={compteur_sources['ollama']}, fallback={compteur_sources['fallback']}, "
          f"timeout={compteur_sources['timeout']}, json_invalide={compteur_sources['json_invalide']}, "
          f"erreur_autre={compteur_sources['erreur_autre']}")
    print("=" * 70)


def build_model_input_from_form(domaine, nom_affiche, sujet, description_offre, spf_ok, dkim_ok, dmarc_ok):
    """
    Construit le meme format de bloc de texte que build_model_input(),
    mais a partir des donnees saisies dans le formulaire du simulateur
    (offre pas encore envoyee, donc pas de vraies donnees techniques
    SPF/DKIM/DMARC -- l'utilisateur simule via des cases a cocher).

    nom_affiche : le nom qui apparaitra dans le champ "From" du client
    email (ex: "PayPal", "Mon Entreprise"), distinct du domaine reel.
    Permet de verifier la coherence nom affiche / domaine (signal de
    spoofing si incoherents).
    """
    spf = 'pass' if spf_ok else 'Unknown'
    dkim = 'pass' if dkim_ok else 'Unknown'
    dmarc = 'pass' if dmarc_ok else 'Unknown'

    domaine = domaine or 'inconnu'
    nom = nom_affiche or domaine
    objet = sujet or '(sans objet)'

    bloc = (
        f"IP: inconnue (simulation, email pas encore envoye)\n"
        f"SPF: {spf}\n"
        f"DKIM: {dkim}\n"
        f"DMARC: {dmarc}\n"
        f"From: \"{nom}\" <contact@{domaine}>\n"
        f"Subject: {objet}\n"
        f"\n"
        f"{description_offre}"
    )

    return bloc


def detecter_texte_cache_html(code_html):
    """
    Analyse un code HTML pour detecter des techniques courantes de
    dissimulation de texte (souvent utilisees pour tromper les filtres
    anti-spam, parfois presentes par accident dans un template mal
    configure). Detection DETERMINISTE en Python (pas d'IA), pour
    garantir un resultat fiable et reproductible.

    Retourne une liste de chaines de texte decrivant les problemes
    trouves (liste vide si rien de suspect detecte).
    """
    if not code_html or not code_html.strip():
        return []

    problemes = []

    try:
        soup = BeautifulSoup(code_html, 'html.parser')

        # Cherche tous les elements ayant un attribut style
        elements_avec_style = soup.find_all(style=True)

        for element in elements_avec_style:
            style = element.get('style', '').lower().replace(' ', '')

            # 1. Texte avec taille de police nulle ou quasi-nulle
            if 'font-size:0' in style or 'font-size:0px' in style or 'font-size:0.1px' in style:
                texte = element.get_text(strip=True)
                if texte:
                    problemes.append(
                        f"Texte a taille de police nulle detecte (font-size:0) : \"{texte[:60]}...\""
                        if len(texte) > 60 else
                        f"Texte a taille de police nulle detecte (font-size:0) : \"{texte}\""
                    )

            # 2. Opacite nulle (texte invisible)
            if 'opacity:0' in style and 'opacity:0.' not in style:
                texte = element.get_text(strip=True)
                if texte:
                    problemes.append(
                        f"Element avec opacite nulle (invisible) contenant du texte : \"{texte[:60]}...\""
                        if len(texte) > 60 else
                        f"Element avec opacite nulle (invisible) contenant du texte : \"{texte}\""
                    )

            # 3. Affichage masque (display:none) contenant du texte
            if 'display:none' in style:
                texte = element.get_text(strip=True)
                if texte:
                    problemes.append(
                        f"Element cache (display:none) contenant du texte : \"{texte[:60]}...\""
                        if len(texte) > 60 else
                        f"Element cache (display:none) contenant du texte : \"{texte}\""
                    )

            # 4. Visibilite masquee
            if 'visibility:hidden' in style:
                texte = element.get_text(strip=True)
                if texte:
                    problemes.append(
                        f"Element avec visibilite cachee contenant du texte : \"{texte[:60]}...\""
                        if len(texte) > 60 else
                        f"Element avec visibilite cachee contenant du texte : \"{texte}\""
                    )

            # 5. Hauteur maximale nulle (texte ecrase visuellement)
            if 'max-height:0' in style:
                texte = element.get_text(strip=True)
                if texte:
                    problemes.append(
                        f"Element avec hauteur maximale nulle (texte ecrase) : \"{texte[:60]}...\""
                        if len(texte) > 60 else
                        f"Element avec hauteur maximale nulle (texte ecrase) : \"{texte}\""
                    )

        # 6. Texte blanc SANS fond colore explicite (suspect car invisible sur fond blanc par defaut)
        a_fond_colore = lambda s: 'background' in s and 'background:none' not in s and 'background:transparent' not in s

        for element in elements_avec_style:
            style = element.get('style', '').lower().replace(' ', '')
            est_blanc = ('color:#fff' in style or 'color:#ffffff' in style or 'color:white' in style)

            if est_blanc and not a_fond_colore(style):
                texte = element.get_text(strip=True)
                if texte:
                    problemes.append(
                        f"Texte blanc sans fond colore associe (potentiellement invisible) : \"{texte[:60]}...\""
                        if len(texte) > 60 else
                        f"Texte blanc sans fond colore associe (potentiellement invisible) : \"{texte}\""
                    )

        # 7. Attribut mso-hide (technique specifique a Outlook)
        if 'mso-hide' in code_html.lower():
            problemes.append(
                "Attribut 'mso-hide' detecte : technique de dissimulation specifique a Outlook."
            )

    except Exception as e:
        print(f"⚠️ Erreur detecter_texte_cache_html : {e}")
        problemes.append("Erreur lors de l'analyse du code HTML : le code n'a pas pu etre verifie correctement.")

    return problemes

"""
keep_ollama_alive.py — Envoie un appel leger a Ollama toutes les 25 minutes
pour eviter que le modele ne se decharge de la RAM (keep_alive de 30 min).
A lancer une fois, dans un terminal separe, laisse ouvert en arriere-plan.
"""

import time
import ollama

INTERVALLE_SECONDES = 25 * 60  # 25 minutes (marge avant les 30 min de keep_alive)

def ping_ollama():
    try:
        client = ollama.Client(timeout=900)
        client.chat(
            model='qwen2.5:7b',
            messages=[{'role': 'user', 'content': 'ping'}],
            keep_alive='30m',
        )
        print(f"✅ Ollama garde actif ({time.strftime('%H:%M:%S')})")
    except Exception as e:
        print(f"⚠️ Erreur ping Ollama : {e}")

if __name__ == '__main__':
    print("🔄 Maintien d'Ollama actif - Ctrl+C pour arreter")
    while True:
        ping_ollama()
        time.sleep(INTERVALLE_SECONDES)



if __name__ == '__main__':
    run_ia_analysis_sample()