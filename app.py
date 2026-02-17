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
        padding: 0.8rem !important;
        font-weight: bold !important;
        border: 2px solid #B79A5B !important;
        width: 100%;
    }
    
    /* Estilização dos campos de texto e seleção */
    .stTextInput label, .stSelectbox label { color: #0E3A5D; font-weight: bold; }
    
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

def save_to_sheets(nome, setor, score, comment):
    try:
        client = get_gsheet_client()
        sheet_id = st.secrets["SHEET_ID"]
        sh = client.open_by_key(sheet_id)
        
        # Seleciona a aba que você acabou de renomear manualmente
        worksheet = sh.worksheet("respostas")
        
        # Prepara a linha com os dados na ordem exata das colunas da planilha
        data = [
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"), # timestamp
            nome,                                         # cliente
            setor,                                        # setor
            score,                                        # nps_score
            comment[:500],                                # nps_comment
            "streamlit_app",                              # source
            "v1"                                          # app_version
        ]
        
        # Adiciona a linha no final da planilha
        worksheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return False
        
# 3. Interface Visual
with st.container():
    # Cabeçalho
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    try:
        # Mantendo sua alteração manual do nome do arquivo
        st.image("Logo Escrita.png", width=220)
    except:
        st.warning("Arquivo 'Logo Escrita.png' não encontrado na raiz do projeto.")
        
    st.markdown('<h1 class="header-title">Pesquisa de Satisfação</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Sua opinião ajuda a Escrita Contabilidade a crescer</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Formulário
    with st.form("nps_form", clear_on_submit=True):
        st.markdown("### Identificação")
        col1, col2 = st.columns(2)
        with col1:
            nome_cliente = st.text_input("Seu nome ou empresa:", placeholder="Ex: João Silva / Empresa ABC")
        with col2:
            setor_atendimento = st.selectbox(
                "Qual setor te atendeu?", 
                ["Contábil", "Fiscal", "RH / Pessoal", "Legal / Societário", "Diretoria", "Outros"]
            )

        st.divider()
        
        st.markdown("### De 0 a 10, o quanto você recomendaria a Escrita Contabilidade para um amigo ou colega?")
        score = st.select_slider("Arraste para escolher sua nota:", options=list(range(11)), value=10)
        
        comment = st.text_area("Conte-nos o motivo da sua nota (opcional):", 
                              placeholder="Fale sobre sua experiência...",
                              max_chars=500)
        
        st.write("---")
        submit = st.form_submit_button("Enviar Resposta")
        
        if submit:
            if not nome_cliente:
                st.error("Por favor, preencha o campo de identificação (Nome ou Empresa).")
            else:
                with st.spinner("Registrando sua resposta..."):
                    sucesso = save_to_sheets(nome_cliente, setor_atendimento, score, comment)
                    if sucesso:
                        st.balloons()
                        st.success(f"Obrigado, {nome_cliente}! Sua resposta foi registrada com sucesso.")
