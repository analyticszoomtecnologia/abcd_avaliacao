import streamlit as st
import jwt
import datetime
from databricks import sql
from dotenv import load_dotenv
import os
from time import sleep
from st_pages import hide_pages

load_dotenv()
DB_SERVER_HOSTNAME = os.getenv("DB_SERVER_HOSTNAME")
DB_HTTP_PATH = os.getenv("DB_HTTP_PATH")
DB_ACCESS_TOKEN = os.getenv("DB_ACCESS_TOKEN")

# Chave secreta para gerar o token JWT
secret_key = "data"

def conectar_banco():
    return sql.connect(
        server_hostname=DB_SERVER_HOSTNAME,
        http_path=DB_HTTP_PATH,
        access_token=DB_ACCESS_TOKEN
    )

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
    return resultado['id_emp'] if resultado else None

def gerar_token(user_id):
    token = jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        },
        secret_key,
        algorithm="HS256"
    )
    return token

def salvar_token_no_banco(user_id, token):
    connection = conectar_banco()
    cursor = connection.cursor()
    cursor.execute(f"""
        INSERT INTO datalake.avaliacao_abcd.tokens (user_id, token, created_at)
        VALUES ('{user_id}', '{token}', '{datetime.datetime.now()}')
    """)
    connection.commit()
    cursor.close()
    connection.close()

def login_page():
    if not st.session_state.get("logged_in", False):
        hide_pages(["Avaliação ABCD", "Funcionários Data", "Lista de Avaliados"])
        
        st.title("Login")
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", key="password", type="password")
        
        login_button = st.button("Login")

        if login_button:
            id_emp = verificar_login(username, password)
            if id_emp:
                token = gerar_token(id_emp)
                salvar_token_no_banco(id_emp, token)  # Salva o token no banco de dados
                st.session_state["logged_in"] = True
                st.session_state["id_emp"] = id_emp
                st.session_state["token"] = token  # Armazena o token no session state para uso interno
                hide_pages([])
                st.success("Login bem-sucedido! Você será redirecionado.")
                sleep(0.5)
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        st.success("Você já está logado!")
