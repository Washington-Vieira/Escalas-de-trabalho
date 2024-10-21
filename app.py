import streamlit as st
from pages import cadastro_empresa, cadastro_funcionario, cadastro_folguista, gerar_escala, gerar_escala_folguista
from data_manager import carregar_empresas

# Função para remover o menu
def remove_menu():
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        div[data-testid="stDecoration"] {visibility: hidden;}
        div[data-testid="stStatusWidget"] {visibility: hidden;}
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

# Configuração da página e remoção do menu
st.set_page_config(page_title="Gerador de Escala", layout="wide")
remove_menu()

# Carregar o CSS externo
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles/main.css')

# Inicializar st.session_state.empresas
if 'empresas' not in st.session_state:
    st.session_state.empresas = carregar_empresas()

# Definir ícones para cada página
PAGES = {
    "🏢 Cadastro de Empresa": cadastro_empresa,
    "👤 Cadastro de Funcionário": cadastro_funcionario,
    "🔄 Cadastro de Folguista": cadastro_folguista,
    "📅 Gerar Escala": gerar_escala,
    "📊 Gerar Escala Folguista": gerar_escala_folguista
}

st.sidebar.title('🧭 Navegação')
st.sidebar.markdown('---')

# Criar botões de navegação
for name, page_func in PAGES.items():
    if st.sidebar.button(name):
        st.session_state.page = name

# Exibir a página selecionada
if 'page' not in st.session_state:
    st.session_state.page = "🏢 Cadastro de Empresa"

# Chamar a função app() da página selecionada
PAGES[st.session_state.page]()

# Adicionar informações no rodapé
st.sidebar.markdown('---')
st.sidebar.text('Versão 1.0')
