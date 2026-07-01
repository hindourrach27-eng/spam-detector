"""
rapport_pdf.py — Generation du rapport PDF pedagogique de diagnostic spam.
Utilise reportlab (Python pur, sans dependance systeme).
Le PDF est genere a la demande, envoye au navigateur, puis supprime du serveur.
"""

import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Chemin vers le logo EMS
LOGO_PATH = os.path.join('static', 'assets', 'images', 'icon', 'logo2.png')

# Couleurs du theme
COULEUR_TITRE = colors.HexColor('#26c6da')
COULEUR_SPAM = colors.HexColor('#f44336')
COULEUR_LEGITIME = colors.HexColor('#26c6da')
COULEUR_WARNING = colors.HexColor('#fb9678')
COULEUR_GRIS = colors.HexColor('#757575')
COULEUR_FOND_SECTION = colors.HexColor('#f5f5f5')

# Definitions pedagogiques des labels (reprises du glossaire)
DEFINITIONS_LABELS = {
    'phishing': {
        'titre': 'Phishing detecte',
        'definition': (
            "Le phishing est une tentative de voler des informations sensibles "
            "(mots de passe, numeros de carte bancaire) en se faisant passer pour "
            "une entite de confiance. Un email de phishing contient souvent un lien "
            "vers un faux site qui imite un site officiel (banque, service en ligne...). "
            "Consequence : vos destinataires pourraient croire que votre email est une "
            "tentative d'arnaque, ce qui nuit gravement a votre reputation."
        ),
        'conseil': (
            "Evitez les formulations alarmistes ('votre compte sera bloque'), "
            "les liens raccourcis, et les demandes d'informations personnelles. "
            "Incluez des informations de contact verifiables."
        )
    },
    'spoofing': {
        'titre': 'Spoofing detecte',
        'definition': (
            "Le spoofing est une usurpation d'identite : le nom affiche dans l'email "
            "ne correspond pas au domaine reel de l'expediteur. Par exemple, afficher "
            "'PayPal' comme nom d'expediteur alors que l'email vient de 'promo-deals.biz'. "
            "Les filtres anti-spam modernes detectent cette incoherence automatiquement."
        ),
        'conseil': (
            "Assurez-vous que le nom affiche (From) correspond exactement a votre "
            "domaine d'envoi. Configurez SPF, DKIM et DMARC pour authentifier "
            "votre identite aupres des services de messagerie."
        )
    },
    'scam': {
        'titre': 'Scam detecte',
        'definition': (
            "Un scam est une arnaque financiere directe : promesse de gain d'argent facile, "
            "heritage inattendu, investissement miracle, gain de loterie... "
            "Le but est de pousser la victime a envoyer de l'argent ou des "
            "informations bancaires. Ce type de contenu est immediatement flagge "
            "par tous les filtres anti-spam."
        ),
        'conseil': (
            "Evitez toute promesse de gain financier garanti, tout langage "
            "qui suggere une opportunite 'exclusive' ou 'limitee dans le temps'. "
            "Privilegiez un contenu factuel, verifable et personnalise."
        )
    },
    'bulk': {
        'titre': 'Envoi en masse (Bulk) detecte',
        'definition': (
            "Le label 'Bulk' indique que l'email ressemble a un envoi en masse "
            "non personnalise : newsletter generique, offre promotionnelle standardisee "
            "envoyee a des milliers de destinataires sans adaptation individuelle. "
            "Ce n'est pas forcement malveillant, mais ce type d'email est souvent "
            "classe automatiquement dans le dossier 'Promotions' ou 'Spam'."
        ),
        'conseil': (
            "Personnalisez vos emails (nom du destinataire, historique d'achat...), "
            "segmentez votre audience, reduisez la frequence d'envoi, "
            "et ajoutez un lien de desabonnement clair."
        )
    }
}


# Explications du score
def get_explication_score(score):
    if score is None:
        return "Score non disponible."
    if score >= 70:
        return (
            f"Un score de {score}/100 indique un risque ELEVE. "
            "Cet email a de fortes chances d'etre bloque ou classe en spam "
            "par les filtres de messagerie modernes. Des corrections importantes "
            "sont necessaires avant tout envoi."
        )
    elif score >= 40:
        return (
            f"Un score de {score}/100 indique un risque MODERE. "
            "Cet email pourrait etre classe en spam par certains filtres. "
            "Des ameliorations sont recommandees pour maximiser la delivrabilite."
        )
    else:
        return (
            f"Un score de {score}/100 indique un risque FAIBLE. "
            "Cet email a de bonnes chances d'arriver en boite de reception. "
            "Verifiez quand meme les recommandations ci-dessous."
        )


def generer_rapport_pdf(simulation_data):
    """
    Genere un rapport PDF pedagogique a partir des donnees d'une simulation.

    Args:
        simulation_data (dict) : donnees de la simulation (domaine, score, verdict,
                                  labels, elements, recommendation, etc.)

    Returns:
        str : chemin vers le fichier PDF temporaire genere
    """
    # Creation d'un fichier temporaire
    tmp = tempfile.NamedTemporaryFile(
        suffix='.pdf', delete=False, prefix='rapport_diagnostic_'
    )
    chemin_pdf = tmp.name
    tmp.close()

    # Configuration du document
    doc = SimpleDocTemplate(
        chemin_pdf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    # Styles
    styles = getSampleStyleSheet()

    style_titre_principal = ParagraphStyle(
        'TitrePrincipal',
        parent=styles['Title'],
        fontSize=18,
        textColor=COULEUR_TITRE,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    style_sous_titre = ParagraphStyle(
        'SousTitre',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COULEUR_GRIS,
        spaceAfter=4
    )
    style_section = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=COULEUR_TITRE,
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4
    )
    style_label_titre = ParagraphStyle(
        'LabelTitre',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=COULEUR_SPAM,
        spaceBefore=10,
        spaceAfter=4
    )
    style_corps = ParagraphStyle(
        'Corps',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    style_conseil = ParagraphStyle(
        'Conseil',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#555555'),
        leftIndent=12,
        spaceAfter=6
    )
    style_centre = ParagraphStyle(
        'Centre',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER
    )
    style_pied = ParagraphStyle(
        'Pied',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COULEUR_GRIS,
        alignment=TA_CENTER
    )

    # Construction du contenu
    contenu = []

    # ===== EN-TETE =====
    en_tete_data = []

    # Logo (si disponible)
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=4 * cm, height=2 * cm)
        logo.hAlign = 'LEFT'
        en_tete_data.append([logo, ''])

    en_tete_table = Table(
        [[
            Image(LOGO_PATH, width=4 * cm, height=2 * cm) if os.path.exists(LOGO_PATH) else Paragraph('EMS',
                                                                                                      style_titre_principal),
            Paragraph('Rapport de diagnostic spam', style_titre_principal)
        ]],
        colWidths=[5 * cm, 12 * cm]
    )
    en_tete_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    contenu.append(en_tete_table)
    contenu.append(Spacer(1, 0.3 * cm))

    # Date de generation
    date_str = datetime.now().strftime('%d/%m/%Y a %H:%M')
    contenu.append(Paragraph(f"Genere le {date_str}", style_sous_titre))
    contenu.append(HRFlowable(width="100%", thickness=1, color=COULEUR_TITRE, spaceAfter=8))

    # ===== SECTION 1 : OFFRE TESTEE =====
    contenu.append(Paragraph("1. Offre testee", style_section))

    domaine = simulation_data.get('domaine', '-')
    nom_affiche = simulation_data.get('nom_affiche') or '-'
    sujet = simulation_data.get('sujet') or '-'
    description = simulation_data.get('description_offre') or '-'
    spf = 'Configure' if simulation_data.get('spf_ok') else 'Non configure'
    dkim = 'Configure' if simulation_data.get('dkim_ok') else 'Non configure'
    dmarc = 'Configure' if simulation_data.get('dmarc_ok') else 'Non configure'

    offre_data = [
        ['Domaine d\'expedition', domaine],
        ['Nom affiche (From)', nom_affiche],
        ['Sujet de l\'email', sujet],
        ['SPF', spf],
        ['DKIM', dkim],
        ['DMARC', dmarc],
    ]

    offre_table = Table(offre_data, colWidths=[5 * cm, 12 * cm])
    offre_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COULEUR_FOND_SECTION),
        ('TEXTCOLOR', (0, 0), (0, -1), COULEUR_GRIS),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    contenu.append(offre_table)

    # Description (en dessous du tableau pour qu'elle ne soit pas ecrasee)
    contenu.append(Spacer(1, 0.3 * cm))
    contenu.append(Paragraph(f"<b>Contenu de l'offre :</b> {description}", style_corps))

    # ===== SECTION 2 : RESULTATS =====
    contenu.append(Paragraph("2. Resultats du diagnostic", style_section))

    score = simulation_data.get('score')
    verdict = simulation_data.get('verdict', 'inconnu')
    score_explication = simulation_data.get('score_explication') or ''

    # Score et verdict cote a cote
    couleur_verdict = COULEUR_SPAM if verdict == 'spam' else COULEUR_LEGITIME
    verdict_texte = 'SPAM' if verdict == 'spam' else 'LEGITIME'

    resultats_data = [
        [
            Paragraph(f"<b>Score de spam</b>", style_centre),
            Paragraph(f"<b>Verdict</b>", style_centre),
        ],
        [
            Paragraph(
                f"<font size='14' color='{'#f44336' if (score or 0) >= 70 else ('#fb9678' if (score or 0) >= 40 else '#26c6da')}'><b>{score}/100</b></font>",
                style_centre),
            Paragraph(
                f"<font size='12' color='{'#f44336' if verdict == 'spam' else '#26c6da'}'><b>{verdict_texte}</b></font>",
                style_centre),
        ]
    ]

    resultats_table = Table(resultats_data, colWidths=[8.5 * cm, 8.5 * cm])
    resultats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_FOND_SECTION),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    contenu.append(resultats_table)
    contenu.append(Spacer(1, 0.3 * cm))

    # Explication du score
    contenu.append(Paragraph(get_explication_score(score), style_corps))
    if score_explication:
        contenu.append(Paragraph(f"<i>Detail : {score_explication}</i>", style_conseil))

    # ===== SECTION 3 : LABELS ET EXPLICATIONS PEDAGOGIQUES =====
    labels_detectes = []
    if simulation_data.get('label_phishing'):
        labels_detectes.append('phishing')
    if simulation_data.get('label_spoofing'):
        labels_detectes.append('spoofing')
    if simulation_data.get('label_scam'):
        labels_detectes.append('scam')
    if simulation_data.get('label_bulk'):
        labels_detectes.append('bulk')

    if labels_detectes:
        contenu.append(Paragraph("3. Explication des problemes detectes", style_section))
        contenu.append(Paragraph(
            "Les labels suivants ont ete detectes par l'analyse IA. "
            "Voici ce qu'ils signifient et comment y remedier :",
            style_corps
        ))

        for label in labels_detectes:
            if label in DEFINITIONS_LABELS:
                info = DEFINITIONS_LABELS[label]
                contenu.append(Paragraph(info['titre'], style_label_titre))
                contenu.append(Paragraph(info['definition'], style_corps))
                contenu.append(Paragraph(f"<b>Conseil :</b> {info['conseil']}", style_conseil))
    else:
        contenu.append(Paragraph("3. Labels detectes", style_section))
        contenu.append(Paragraph(
            "Aucun label suspect n'a ete detecte par l'analyse IA pour cette offre.",
            style_corps
        ))

    # ===== SECTION 4 : ELEMENTS SUSPECTS =====
    contenu.append(Paragraph("4. Elements suspects identifies", style_section))

    elements_texte = simulation_data.get('harmful_elements') or ''
    elements = [e.strip() for e in elements_texte.split(',') if e.strip()] if elements_texte else []

    if elements:
        for element in elements:
            contenu.append(Paragraph(f"• {element}", style_conseil))
    else:
        contenu.append(Paragraph("Aucun element suspect identifie.", style_corps))

    # ===== SECTION 5 : RECOMMANDATION =====
    contenu.append(Paragraph("5. Recommandation", style_section))

    recommendation = simulation_data.get('recommendation') or 'Aucune recommandation particuliere.'
    contenu.append(Paragraph(recommendation, style_corps))

    # ===== PIED DE PAGE =====
    contenu.append(Spacer(1, 1 * cm))
    contenu.append(HRFlowable(width="100%", thickness=0.5, color=COULEUR_GRIS))
    contenu.append(Spacer(1, 0.2 * cm))
    contenu.append(Paragraph(
        "Rapport genere automatiquement par le Systeme de Diagnostic Spam — E Market Solutions",
        style_pied
    ))
    contenu.append(Paragraph(
        "Ce rapport est fourni a titre indicatif. Les resultats sont bases sur une analyse IA "
        "et peuvent varier. Consultez un expert en delivrabilite pour un audit complet.",
        style_pied
    ))

    # Generation du PDF
    doc.build(contenu)

    return chemin_pdf