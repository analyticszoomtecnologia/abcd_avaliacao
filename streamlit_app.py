import streamlit as st
from login import login_page
from func_data import func_data_page
from alter_nota import func_data_nota
from st_pages import hide_pages
import urllib.parse

# URL da aplicação externa onde o abcd.py está hospedado
link_abcd_base = "https://aplicacao.streamlit.app"  # Substitua pelo URL real

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    hide_pages(["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"])
    login_page()
else:
    hide_pages([])

    st.sidebar.title("Navegação")
    pagina_selecionada = st.sidebar.selectbox(
        "Escolha a página",
        ["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"]
    )

    if pagina_selecionada == "Avaliação ABCD":
        user_id = st.session_state["id_emp"]
        link_abcd = f"{link_abcd_base}?user_id={urllib.parse.quote(str(user_id))}"  # Passa apenas o user_id

        #st.write("Redirecionando para a página principal...")
        st.markdown(f"[Clique aqui para Realizar Avaliação.]({link_abcd})", unsafe_allow_html=True)

    elif pagina_selecionada == "Funcionários Data":
        func_data_page()
    elif pagina_selecionada == "Lista de Avaliados":
        func_data_nota()

st.markdown(
        """
        <br><hr>
        <div style='text-align: center;'>
            Desenvolvido por 
            <a href='https://www.linkedin.com/in/gabriel-cordeiro-033641144/' target='_blank' style='text-decoration: none; color: #0A66C2;'>
                <img src='https://upload.wikimedia.org/wikipedia/commons/f/f8/LinkedIn_icon_circle.svg' alt='LinkedIn' width='20' style='vertical-align: middle; margin-right: 5px;' />
                Gabriel Cordeiro
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )