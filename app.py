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
        width: 100%;
    }
    
    /* Estilização dos campos */
    .stTextInput label, .stSelectbox label, .stSlider label { 
        color: #0E3A5D; 
        font-weight: bold; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. Conexão com Google Planilhas
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(credentials)

def save_to_sheets(nome, setor, notas, comment):
    try:
        client = get_gsheet_client()
        sheet_id = st.secrets["SHEET_ID"]
        sh = client.open_by_key(sheet_id)
        worksheet = sh.worksheet("respostas")
        
        # Prepara a linha com as 12 colunas conforme a nova estrutura
        data = [
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"), # timestamp
            nome,                                         # cliente
            setor,                                        # setor
            notas['clareza'],                             # clareza
            notas['prazos'],                              # prazos
            notas['comunicacao'],                         # comunicacao
            notas['atendimento'],                         # atendimento
            notas['custo'],                               # custo
            notas['nps'],                                 # nps_score
            comment[:500],                                # nps_comment
            "streamlit_app",                              # source
            "v2"                                          # app_version
        ]
        
        worksheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Erro técnico ao salvar na planilha: {e}")
        return False

# 3. Interface Visual
with st.container():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    try:
        st.image("Logo Escrita.png", width=220)
    except:
        st.warning("Arquivo 'Logo Escrita.png' não encontrado.")
        
    st.markdown('<h1 class="header-title">Pesquisa de Satisfação</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Sua opinião ajuda a Escrita Contabilidade a crescer</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("nps_form", clear_on_submit=True):
        st.markdown("### 1. Identificação")
        col1, col2 = st.columns(2)
        with col1:
            nome_cliente = st.text_input("Seu nome ou empresa:", placeholder="Ex: João Silva")
        with col2:
            setor_atendimento = st.selectbox(
                "Qual setor te atendeu?", 
                ["Contábil", "Fiscal", "RH / Pessoal", "Legal / Societário", "Diretoria", "Outros"]
            )

        st.divider()
        st.markdown("### 2. Avaliação de Indicadores")
        st.caption("Dê uma nota de 0 a 10 para cada critério:")
        
        n_clareza = st.select_slider("Clareza nas informações e orientações:", options=list(range(11)), value=10)
        n_prazos = st.select_slider("Cumprimento de prazos acordados:", options=list(range(11)), value=10)
        n_comunicacao = st.select_slider("Qualidade e agilidade na comunicação:", options=list(range(11)), value=10)
        n_atendimento = st.select_slider("Cordialidade e presteza no atendimento:", options=list(range(11)), value=10)
        n_custo = st.select_slider("Relação custo-benefício dos serviços:", options=list(range(11)), value=10)

        st.divider()
        st.markdown("### 3. Recomendação Geral")
        st.markdown("De 0 a 10, o quanto você recomendaria a Escrita Contabilidade para um amigo ou colega?")
        score_nps = st.select_slider("Sua nota geral:", options=list(range(11)), value=10, key="nps_geral")
        
        comment = st.text_area("Conte-nos o motivo das suas notas (opcional):", 
                              placeholder="Fale sobre sua experiência...",
                              max_chars=500)
        
        st.write("---")
        submit = st.form_submit_button("Enviar Avaliação Completa")
        
        if submit:
            if not nome_cliente:
                st.error("Por favor, preencha o campo de identificação (Nome ou Empresa).")
            else:
                with st.spinner("Registrando sua resposta..."):
                    # Organiza as notas em um dicionário para enviar à função
                    dict_notas = {
                        'clareza': n_clareza,
                        'prazos': n_prazos,
                        'comunicacao': n_comunicacao,
                        'atendimento': n_atendimento,
                        'custo': n_custo,
                        'nps': score_nps
                    }
                    sucesso = save_to_sheets(nome_cliente, setor_atendimento, dict_notas, comment)
                    if sucesso:
                        st.balloons()
                        st.success(f"Obrigado, {nome_cliente}! Sua avaliação detalhada foi registrada.")
