import streamlit as st
import google.generativeai as genai
import base64
import re
from io import BytesIO
from PIL import Image
from xhtml2pdf import pisa  # Remplacement robuste pour éviter l'erreur de DLL de WeasyPrint

# ----------------------------------------------------
# 1. DESIGN ULTRA-SAAS PREMIUM (GLASSMORPHISM & ANIMATIONS)
# ----------------------------------------------------
st.set_page_config(page_title="Career Suite AI Ultra", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=300;400;500;600;700;800&display=swap');
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); filter: blur(10px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

    .stApp {
        background: radial-gradient(circle at top left, #064e3b 0%, #0f172a 50%, #020617 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc !important;
    }

    .element-container, .form-card, .hero-container, .stTabs {
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] label {
        color: #34d399 !important;
        font-weight: 600;
    }

    /* Style des Onglets / Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #94a3b8;
        padding: 0 24px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(5, 150, 105, 0.2);
    }

    .hero-container {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(25px);
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 30px;
    }
    .hero-text h1 {
        font-weight: 800;
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #38bdf8 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .form-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
    }
    .form-card h3 {
        color: #38bdf8 !important;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 20px;
    }

    input, textarea, div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #059669 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 16px;
        font-size: 1.1rem;
        font-weight: 700;
        border-radius: 16px;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(37, 99, 235, 0.4);
    }

    .preview-box {
        background: #ffffff;
        border-radius: 24px;
        padding: 10px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.4);
        border: 2px solid rgba(52, 211, 153, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. LEXIQUE MULTILINGUE
# ----------------------------------------------------
LANGUAGES = {
    "FR": {
        "title": "Career Suite AI Pro",
        "subtitle": "Conception automatisée de documents de candidature via l'IA",
        "tab_form": "📋 Formulaire", "tab_cv": "✨ Aperçu CV", "tab_lm": "✉️ Aperçu Lettre",
        "sidebar_design": "Design & Référence Visuelle",
        "personal_info": "👤 1. Informations Personnelles & Contact",
        "experience": "🛠️ 2. Parcours & Expertises",
        "raw_data": "Vos informations brutes (l'IA s'occupe de la rédaction professionnelle)",
        "job_desc": "🎯 Offre d'emploi ciblée (Optionnel - pour optimisation ATS)",
        "generate_btn": "Générer mon Dossier Professionnel",
        "loading": "Analyse du profil et rédaction des documents...",
        "success": "🔥 Documents générés avec succès au format PDF !",
        "download_cv": "📥 Télécharger le CV (PDF)",
        "download_lm": "📥 Télécharger la Lettre (PDF)"
    },
    "EN": {
        "title": "Career Suite AI Pro",
        "subtitle": "Automated generation of elite professional materials via AI",
        "tab_form": "📋 Form", "tab_cv": "✨ CV Preview", "tab_lm": "✉️ Letter Preview",
        "sidebar_design": "Design & Layout Theme",
        "personal_info": "👤 1. Personal Information & Contact",
        "experience": "🛠️ 2. Career History & Skills",
        "raw_data": "Your raw career data (AI handles copywriting and formatting)",
        "job_desc": "🎯 Target Job Description (Optional - for ATS optimization)",
        "generate_btn": "Generate Professional Suite",
        "loading": "Processing profile and aligning with benchmarks...",
        "success": "🔥 Documents successfully generated as PDF!",
        "download_cv": "📥 Download CV (PDF)",
        "download_lm": "📥 Download Letter (PDF)"
    }
}

# ----------------------------------------------------
# 3. PANNEAU LATÉRAL (CONTRÔLES PRINCIPAUX)
# ----------------------------------------------------
st.sidebar.markdown("<h2 style='margin-top:0;'>👑 Studio Premium</h2>", unsafe_allow_html=True)
lang = st.sidebar.selectbox("🌐 Language", ["FR", "EN"])
t = LANGUAGES[lang]

st.sidebar.markdown("---")
template = st.sidebar.selectbox(t['sidebar_design'], [
    "Classic Slate Executive (Barre latérale sombre)", 
    "Harvard Corporate Pro (Bandeau Anthracite)", 
    "Modern Executive Pro (Bleu Roi Éclatant)", 
    "Tech Minimal Pro (Émeraude Épuré)"
])

custom_color = st.sidebar.color_picker("🎨 Couleur personnalisée des bannières/titres", "#2c3e50")

uploaded_photo = st.sidebar.file_uploader("📸 Photo d'identité (Optionnelle)", type=["jpg", "png", "jpeg"])
photo_b64 = ""
if uploaded_photo:
    image = Image.open(uploaded_photo)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    photo_b64 = base64.b64encode(buffered.getvalue()).decode()

# Rendu de la photo pour compatibilité PDF (pisa gère mieux les balises img simples)
if not photo_b64:
    photo_tag = '<div style="background-color: #334155; color: #94a3b8; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; text-align: center; margin: 0 auto; font-size: 30px;">👤</div>'
else:
    photo_tag = f'<img src="data:image/png;base64,{photo_b64}" style="width: 110px; height: 110px; border-radius: 50%;">'

# ----------------------------------------------------
# 4. NETTOYAGE DU CODE SOURCE HTML DE GEMINI
# ----------------------------------------------------
def clean_html_content(raw_text):
    """Nettoie de manière robuste toutes les balises Markdown parasites émises par l'IA."""
    if not raw_text:
        return ""
    cleaned = re.sub(r'```html\s*', '', raw_text)
    cleaned = re.sub(r'```\s*', '', cleaned)
    return cleaned.strip()

def get_canva_theme_font(template_name):
    if "Harvard" in template_name:
        return "Georgia, serif"
    return "Helvetica, Arial, sans-serif"

# ----------------------------------------------------
# 5. SYSTÈME D'ONGLETS & INTERFACE PRINCIPALE
# ----------------------------------------------------
st.markdown(f"""
    <div class="hero-container">
        <div class="hero-text">
            <h1>{t['title']}</h1>
            <p style="color: #94a3b8; margin: 5px 0 0 0;">{t['subtitle']}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

tab_form, tab_cv, tab_lm = st.tabs([t["tab_form"], t["tab_cv"], t["tab_lm"]])

with tab_form:
    st.markdown(f'<div class="form-card"><h3>{t["personal_info"]}</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nom & Prénom", value="Jean Dupont")
        email = st.text_input("Adresse Email", value="jean.dupont@email.com")
    with col2:
        phone = st.text_input("Mobile", value="+33 7 00 00 00 00")
        job_title = st.text_input("Titre du Poste Visé", value="Stage Technicien")
    st.markdown('</div>', unsafe_allow_html=True)

    col_pane1, col_pane2 = st.columns(2)
    with col_pane1:
        st.markdown(f'<div class="form-card"><h3>{t["experience"]}</h3>', unsafe_allow_html=True)
        user_profile = st.text_area(t['raw_data'], height=180, placeholder="Vos compétences, formations et tâches...")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_pane2:
        st.markdown(f'<div class="form-card"><h3>{t["job_desc"]}</h3>', unsafe_allow_html=True)
        job_ad = st.text_area("Descriptif du poste", height=180, placeholder="Copiez l'annonce ici pour insérer les mots-clés ATS...")
        st.markdown('</div>', unsafe_allow_html=True)

    generate_clicked = st.button(t['generate_btn'], use_container_width=True)

# ----------------------------------------------------
# 6. LOGIQUE D'APPEL ET DE COMPILATION PDF (STRUCTURE COMPATIBLE PISA)
# ----------------------------------------------------
if generate_clicked:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("🔑 Erreur : La clé API 'GEMINI_API_KEY' n'est pas configurée dans vos secrets Streamlit.")
    elif not name or not user_profile:
        st.warning("Veuillez renseigner votre nom et votre parcours.")
    else:
        with st.spinner(t['loading']):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt_cv = f"Génère uniquement les blocs de contenu sémantiques HTML (uniquement des div, h3, ul, li, p) pour un CV. Langue : {lang}. Poste ciblé : {job_title}. Candidat : {name}. Profil : {user_profile}. Annonce ciblée : {job_ad}. Optimise pour les filtres ATS. Ne mets aucun bloc de code markdown, uniquement le code brut."
                prompt_lm = f"Rédige une lettre de motivation professionnelle en langue {lang} pour le poste de {job_title}. Candidat : {name}. Profil : {user_profile}. Annonce : {job_ad}. Renvoie uniquement le corps du texte découpé en paragraphes HTML (<p>)."

                cv_raw = model.generate_content(prompt_cv).text
                lm_raw = model.generate_content(prompt_lm).text
                
                cv_content = clean_html_content(cv_raw)
                lm_content = clean_html_content(lm_raw)
                
                font_family = get_canva_theme_font(template)
                
                # RESTRUCTURATION COMPATIBLE PDF (Tableau HTML pour éviter l'incompatibilité flexbox)
                full_cv_html = f"""
                <html>
                <head>
                <style>
                    @page {{ size: A4; margin: 0cm; }}
                    body {{ font-family: {font_family}; background-color: #ffffff; color: #1e293b; margin: 0; padding: 0; }}
                    .cv-table {{ width: 100%; border-collapse: collapse; min-height: 29.7cm; }}
                    .canva-sidebar {{ width: 35%; background-color: {custom_color}; color: #ffffff; padding: 30px 15px; text-align: center; vertical-align: top; }}
                    .canva-main {{ width: 65%; padding: 40px 30px; background-color: #ffffff; vertical-align: top; }}
                    .canva-sidebar h2 {{ color: #ffffff; font-size: 20px; margin-bottom: 5px; font-weight: 800; text-transform: uppercase; margin-top: 15px; }}
                    .canva-sidebar p {{ color: #e2e8f0; font-size: 12px; margin: 6px 0; text-align: left; }}
                    h3, p, li {{ font-family: {font_family}; }}
                    ul {{ padding-left: 20px; }}
                    li, p {{ font-size: 12px; line-height: 1.5; }}
                </style>
                </head>
                <body>
                    <table class="cv-table">
                        <tr>
                            <td class="canva-sidebar">
                                <div>{photo_tag}</div>
                                <h2>{name}</h2>
                                <p style="font-weight: 600; text-align: center; color: #34d399;">{job_title}</p>
                                <div style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px;">
                                    <p><b>📧 Email:</b><br>{email}</p>
                                    <p><b>📞 Téléphone:</b><br>{phone}</p>
                                </div>
                            </td>
                            <td class="canva-main">
                                {cv_content}
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
                
                # Structure HTML Finale pour la Lettre
                full_lm_html = f"""
                <html>
                <head>
                <style>
                    @page {{ size: A4; margin: 0cm; }}
                    body {{ font-family: {font_family}; background-color: #ffffff; color: #334155; margin: 0; padding: 0; }}
                    .letter-banner {{ background-color: {custom_color}; color: #ffffff; padding: 40px; }}
                    .letter-banner h1 {{ margin: 0; font-size: 24px; font-weight: 800; color: #ffffff; }}
                    .letter-banner p {{ color: #e2e8f0; font-size: 13px; margin: 5px 0 0 0; }}
                    .letter-body {{ padding: 45px; text-align: justify; font-size: 13px; line-height: 1.6; }}
                </style>
                </head>
                <body>
                    <div class="letter-banner">
                        <h1>{name}</h1>
                        <p>{job_title} &nbsp;|&nbsp; {email} &nbsp;|&nbsp; {phone}</p>
                    </div>
                    <div class="letter-body">
                        <p style="text-align: right;">Fait le 25 Mai 2026</p>
                        <p><b>Objet :</b> Candidature stratégique pour le poste de <u>{job_title}</u></p>
                        <br>
                        {lm_content}
                        <br>
                        <p>Cordialement,<br><b>{name}</b></p>
                    </div>
                </body>
                </html>
                """
                
                # Compilation sécurisée sans dépendance système externe (pisa)
                pdf_cv_io = BytesIO()
                pisa.CreatePDF(full_cv_html, dest=pdf_cv_io)
                st.session_state['pdf_cv_bytes'] = pdf_cv_io.getvalue()
                st.session_state['full_cv_html'] = full_cv_html
                
                pdf_lm_io = BytesIO()
                pisa.CreatePDF(full_lm_html, dest=pdf_lm_io)
                st.session_state['pdf_lm_bytes'] = pdf_lm_io.getvalue()
                st.session_state['full_lm_html'] = full_lm_html
                
                st.success(t['success'])
                
            except Exception as model_error:
                st.error(f"Erreur d'exécution de l'application : {model_error}")

# ----------------------------------------------------
# 7. LOGIQUE DE RENDU DANS LES ONGLETS (PERSISTENCE)
# ----------------------------------------------------
if 'pdf_cv_bytes' in st.session_state:
    with tab_cv:
        st.markdown(f"### {t['tab_cv']}")
        st.download_button(t['download_cv'], data=st.session_state['pdf_cv_bytes'], file_name="CV_Professionnel.pdf", mime="application/pdf", use_container_width=True)
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.components.v1.html(st.session_state['full_cv_html'], height=850, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_lm:
        st.markdown(f"### {t['tab_lm']}")
        st.download_button(t['download_lm'], data=st.session_state['pdf_lm_bytes'], file_name="Lettre_Motivation.pdf", mime="application/pdf", use_container_width=True)
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.components.v1.html(st.session_state['full_lm_html'], height=850, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)