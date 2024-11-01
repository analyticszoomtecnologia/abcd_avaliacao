import streamlit as st
from login import login_page
from func_data import func_data_page
from alter_nota import func_data_nota
from st_pages import hide_pages

# URL da aplicação externa onde o `abcd.py` está hospedado
link_abcd_base = "https://aplicacao.streamlit.app"  # Substitua pelo URL real

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
    pagina_selecionada = st.sidebar.selectbox(
        "Escolha a página",
        ["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"]
    )

    # Redireciona para o link externo da aplicação `abcd.py` se "Avaliação ABCD" for selecionada
    if pagina_selecionada == "Avaliação ABCD":
        # Usa o token JWT armazenado no session_state
        token = st.session_state["token"]
        # Constrói a URL com o token JWT como parâmetro
        link_abcd = f"{link_abcd_base}?token={token}"

        # Redirecionamento com link clicável
        st.write("Redirecionando para a página principal...")
        st.markdown(f"[Clique aqui se não for redirecionado automaticamente.]({link_abcd})", unsafe_allow_html=True)

    elif pagina_selecionada == "Funcionários Data":
        func_data_page()
    elif pagina_selecionada == "Lista de Avaliados":
        func_data_nota()
