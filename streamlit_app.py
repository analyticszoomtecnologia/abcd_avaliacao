import streamlit as st
from login import login_page
from abcd import abcd_page
from func_data import func_data_page
from alter_nota import func_data_nota

from st_pages import hide_pages

# Verifica se o usuário está logado
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Se o usuário não estiver logado, mostra a página de login
if not st.session_state['logged_in']:
    hide_pages(["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"])  # Oculta as páginas
    login_page()
else:
    hide_pages([])  # Mostra todas as páginas

    # Seletor de páginas na barra lateral
    st.sidebar.title("Navegação")
    
    # Verifica se o usuário logado é 'grasiele.gof'
    if st.session_state.get('username') == 'grasiele.gof':
        # Usuário 'grasiele.gof' pode ver todas as páginas
        pagina_selecionada = st.sidebar.selectbox(
            "Escolha a página",
            ["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"]
        )
    else:
        # Outros usuários não podem ver a página "Funcionários Data"
        pagina_selecionada = st.sidebar.selectbox(
            "Escolha a página",
            ["Avaliação ABCD", "Lista de Avaliados"]
        )

    # Navega para a página selecionada
    if pagina_selecionada == "Avaliação ABCD":
        abcd_page()
    elif pagina_selecionada == "Funcionários Data":
        if st.session_state.get('username') == 'grasiele.gof':  # Verificação extra por segurança
            func_data_page()
    elif pagina_selecionada == "Lista de Avaliados":
        func_data_nota()
