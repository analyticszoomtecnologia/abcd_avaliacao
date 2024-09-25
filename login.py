import streamlit as st
from databricks import sql
from dotenv import load_dotenv
import os
from time import sleep
from st_pages import hide_pages

load_dotenv()
DB_SERVER_HOSTNAME = os.getenv("DB_SERVER_HOSTNAME")
DB_HTTP_PATH = os.getenv("DB_HTTP_PATH")
DB_ACCESS_TOKEN = os.getenv("DB_ACCESS_TOKEN")

# Função para conectar ao banco de dados
def conectar_banco():
    return sql.connect(
        server_hostname=DB_SERVER_HOSTNAME,
        http_path=DB_HTTP_PATH,
        access_token=DB_ACCESS_TOKEN
    )

# Função para verificar o login
def verificar_login(username, password):
    connection = conectar_banco()
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT id_emp
        FROM datalake.avaliacao_abcd.login
        WHERE username = '{username}' AND password = '{password}'
    """)
    resultado = cursor.fetchone()
    cursor.close()
    connection.close()
    return resultado is not None

# Função para a página de login
def login_page():
    if not st.session_state.get("logged_in", False):
        hide_pages(["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"])  # Oculta as páginas enquanto não logado
        
        st.title("Login")
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", key="password", type="password")
        
        login_button = st.button("Login")

        if login_button:
            if verificar_login(username, password):
                st.session_state["logged_in"] = True  # Marca como logado
                hide_pages([])  # Mostra todas as páginas após login
                st.success("Login bem-sucedido! Você será redirecionado.")
                sleep(0.5)
                st.experimental_rerun()  # Redireciona para a página principal
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        st.success("Você já está logado!")
