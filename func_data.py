import streamlit as st
import pandas as pd
from databricks import sql
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()
DB_SERVER_HOSTNAME = os.getenv("DB_SERVER_HOSTNAME")
DB_HTTP_PATH = os.getenv("DB_HTTP_PATH")
DB_ACCESS_TOKEN = os.getenv("DB_ACCESS_TOKEN")

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        conn = sql.connect(
            server_hostname=DB_SERVER_HOSTNAME,
            http_path=DB_HTTP_PATH,
            access_token=DB_ACCESS_TOKEN
        )
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função que encapsula toda a lógica da página
def func_data_page():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.error("Você precisa fazer login para acessar essa página.")
        return
    st.title("Gerenciamento de Colaboradores")

    # Opções de CRUD
    opcao = st.selectbox("Escolha a operação", ["Adicionar", "Listar", "Atualizar", "Deletar"])

    conn = conectar_banco()

    if conn:
        if opcao == "Adicionar":
            st.subheader("Adicionar Novo Funcionário")
            nome = st.text_input("Nome")
            setor = st.text_input("Setor")
            gestor_direto = st.text_input("Gestor Direto")
            diretor_gestor = st.text_input("Diretor Gestor")
            diretoria = st.text_input("Diretoria")
            
            if st.button("Adicionar"):
                adicionar_pessoa(conn, nome, setor, gestor_direto, diretor_gestor, diretoria)

        elif opcao == "Listar":
            st.subheader("Lista de Funcionários")
            df = listar_pessoas(conn)
            st.dataframe(df)

        elif opcao == "Atualizar":
            st.subheader("Atualizar Dados de Funcionário")

            nome_busca = st.text_input("Digite o nome para buscar")
            
            if nome_busca:
                df_busca = buscar_por_nome(conn, nome_busca)
                if df_busca.empty:
                    st.warning(f"Nenhum funcionário encontrado com o nome: {nome_busca}")
                else:
                    st.dataframe(df_busca)
                    funcionarios_opcoes = df_busca.apply(lambda row: f"ID {row['id']}: {row['Nome']}", axis=1).tolist()
                    id_selecionado = st.selectbox("Selecione o Funcionário para Atualizar", options=df_busca['id'], format_func=lambda x: f"ID {x}: {df_busca[df_busca['id'] == x]['Nome'].values[0]}")
                    
                    nome = st.text_input("Novo Nome", value=df_busca[df_busca['id'] == id_selecionado]['Nome'].values[0])
                    setor = st.text_input("Novo Setor", value=df_busca[df_busca['id'] == id_selecionado]['Setor'].values[0])
                    gestor_direto = st.text_input("Novo Gestor Direto", value=df_busca[df_busca['id'] == id_selecionado]['Gestor_Direto'].values[0])
                    diretor_gestor = st.text_input("Novo Diretor Gestor", value=df_busca[df_busca['id'] == id_selecionado]['Diretor_Gestor'].values[0])
                    diretoria = st.text_input("Nova Diretoria", value=df_busca[df_busca['id'] == id_selecionado]['Diretoria'].values[0])

                    if st.button("Atualizar"):
                        atualizar_pessoa(conn, id_selecionado, nome, setor, gestor_direto, diretor_gestor, diretoria)

        elif opcao == "Deletar":
            st.subheader("Deletar Funcionário")

            nome_busca = st.text_input("Digite o nome para buscar")
            
            if nome_busca:
                df_busca = buscar_por_nome(conn, nome_busca)
                if df_busca.empty:
                    st.warning(f"Nenhum funcionário encontrado com o nome: {nome_busca}")
                else:
                    st.dataframe(df_busca)
                    funcionarios_opcoes = df_busca.apply(lambda row: f"ID {row['id']}: {row['Nome']}", axis=1).tolist()
                    id_selecionado = st.selectbox("Selecione o Funcionário para Deletar", options=df_busca['id'], format_func=lambda x: f"ID {x}: {df_busca[df_busca['id'] == x]['Nome'].values[0]}")
                    
                    if st.button("Deletar"):
                        deletar_pessoa(conn, id_selecionado)

        conn.close()

    else:
        st.error("Não foi possível conectar ao banco de dados.")

# Funções CRUD que serão usadas na página
def adicionar_pessoa(conn, nome, setor, gestor_direto, diretor_gestor, diretoria):
    query = f"""
    INSERT INTO datalake.silver_pny.func_zoom (Nome, Setor, Gestor_Direto, Diretor_Gestor, Diretoria)
    VALUES ('{nome}', '{setor}', '{gestor_direto}', '{diretor_gestor}', '{diretoria}');
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        st.success(f"Funcionário {nome} adicionado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao adicionar funcionário: {e}")

def listar_pessoas(conn):
    query = "SELECT * FROM datalake.silver_pny.func_zoom"
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)
    cursor.close()
    return df

def buscar_por_nome(conn, nome):
    query = f"""
    SELECT id, Nome, Setor, Gestor_Direto, Diretor_Gestor, Diretoria 
    FROM datalake.silver_pny.func_zoom 
    WHERE LOWER(Nome) LIKE LOWER('%{nome}%')
    """
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)
    cursor.close()
    return df

def atualizar_pessoa(conn, id, nome, setor, gestor_direto, diretor_gestor, diretoria):
    query = f"""
    UPDATE datalake.silver_pny.func_zoom 
    SET Nome = '{nome}', Setor = '{setor}', Gestor_Direto = '{gestor_direto}', Diretor_Gestor = '{diretor_gestor}', Diretoria = '{diretoria}'
    WHERE id = {id};
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        st.success(f"Funcionário {nome} atualizado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao atualizar funcionário: {e}")

def deletar_pessoa(conn, id):
    query = f"DELETE FROM datalake.silver_pny.func_zoom WHERE id = {id};"
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        st.success(f"Funcionário com ID {id} deletado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao deletar funcionário: {e}")
