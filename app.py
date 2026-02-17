import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# 1. Configurações Iniciais e Estilo CSS
st.set_page_config(page_title="NPS - Escrita Contabilidade", page_icon="📊")

custom_css = """
<style>
    /* Fundo do App */
    .stApp { background-color: #F4F6F8; }
    
    /* Cabeçalho */
    .header-container {
        background-color: #0E3A5D;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .header-title { color: #FFFFFF; font-weight: bold; margin-bottom: 0; }
    .header-subtitle { color: #B79A5B; font-size: 1.1rem; }
    
    /* Botão */
    div.stButton > button {
        background-color: #1F5E8C !important;
        color: white !important;
        border: 2px solid #B79A5B !important;
        width: 100%;
    }
    
    /* Input de Notas */
    .stSlider label { color: #0E3A5D; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. Conexão com Google Planilhas
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(credentials)

def save_to_sheets(score, comment):
    try:
        client = get_gsheet_client()
        sheet_id = st.secrets["SHEET_ID"]
        sh = client.open_by_key(sheet_id)
        
        # Tenta selecionar a aba, se não existir, cria
        try:
            worksheet = sh.worksheet("respostas")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title="respostas", rows="100", cols="20")
            worksheet.append_row(["timestamp", "nps_score", "nps_comment", "source", "app_version"])
        
        data = [
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            score,
            comment[:500], # Limite de caracteres
            "streamlit_app",
            "v1"
        ]
        worksheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# 3. Interface Visual
with st.container():
    # Cabeçalho
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    try:
        st.image("Logo Escrita.png", width=180)
    except:
        st.warning("Logo não encontrado em assets/logo.png")
    st.markdown('<h1 class="header-title">Pesquisa de Satisfação</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Leva menos de 30 segundos</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Formulário
    with st.form("nps_form", clear_on_submit=True):
        st.markdown("### De 0 a 10, o quanto você recomendaria a Escrita Contabilidade para um amigo ou colega?")
        score = st.select_slider("Arraste para escolher sua nota:", options=list(range(11)), value=10)
        
        comment = st.text_area("Se quiser, conte rapidamente o motivo da sua nota (opcional):", 
                              placeholder="Sua opinião é muito importante para nós...",
                              max_chars=500)
        
        submit = st.form_submit_button("Enviar Resposta")
        
        if submit:
            with st.spinner("Enviando..."):
                sucesso = save_to_sheets(score, comment)
                if sucesso:
                    st.balloons()
                    st.success("Obrigado! Sua resposta foi registrada com sucesso.")
