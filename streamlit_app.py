import streamlit as st
from login import login_page
from func_data import func_data_page
from alter_nota import func_data_nota
import jwt
import datetime
from st_pages import hide_pages

# Chave secreta para gerar o token JWT (use a mesma chave na aplicação externa)
secret_key = "data"  # Defina uma chave segura compartilhada

# Verifica se o usuário está logado
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Gera um token JWT com o ID do usuário logado
def gerar_token(user_id):
    token = jwt.encode(
        {
            "user_id": st.session_state["id_emp"],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)  # Token expira em 15 minutos
        },
        secret_key,
        algorithm="HS256"
    )
    return token

# URL da aplicação externa onde o `abcd.py` está hospedado
link_abcd_base = "https://aplicacao.streamlit.app/"  # Substitua pelo URL real

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
        # Gera o token com o ID do usuário logado
        token = gerar_token(st.session_state['id_emp'])
        # Constrói a URL com o token JWT como parâmetro
        link_abcd = f"{link_abcd_base}?token={token}"

        # Redirecionamento com link clicável
        # Redirecionamento manual
        st.write("Redirecionando para a página principal...")
        st.markdown(f"[Clique aqui se não for redirecionado automaticamente.]({link_abcd})", unsafe_allow_html=True)


    elif pagina_selecionada == "Funcionários Data":
        func_data_page()
    elif pagina_selecionada == "Lista de Avaliados":
        func_data_nota()
