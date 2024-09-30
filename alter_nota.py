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

# Função para calcular o Quarter com base na data de resposta
def calcular_quarter(data):
    mes = data.month
    if mes <= 3:
        return "Q1"
    elif mes <= 6:
        return "Q2"
    elif mes <= 9:
        return "Q3"
    else:
        return "Q4"

# Função para listar avaliados e incluir a coluna de Quarter
def listar_avaliados(conn, quarter=None):
    query = """
    SELECT id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota, soma_final, 
           colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico, data_resposta
    FROM datalake.avaliacao_abcd.avaliacao_abcd
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)
    
    # Calculando o Quarter com base na data de resposta
    df['data_resposta'] = pd.to_datetime(df['data_resposta'])
    df['quarter'] = df['data_resposta'].apply(calcular_quarter)
    
    # Filtrando por Quarter se for especificado
    if quarter:
        df = df[df['quarter'] == quarter]
    
    cursor.close()
    return df

# Função que encapsula toda a lógica da página
def func_data_nota():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.error("Você precisa fazer login para acessar essa página.")
        return
    st.title("Avaliações")

    # Opções de CRUD
    opcao = st.selectbox("Escolha a operação", ["Listar", "Atualizar", "Deletar"])

    conn = conectar_banco()

    if conn:
        if opcao == "Listar":
            st.subheader("Lista de Avaliados")
            
            # Adicionando a seleção de Quarter
            quarter_selecionado = st.selectbox("Selecione o Quarter", ["Todos", "Q1", "Q2", "Q3", "Q4"])
            
            # Filtrando os avaliados pelo Quarter
            if quarter_selecionado == "Todos":
                df = listar_avaliados(conn)
            else:
                df = listar_avaliados(conn, quarter=quarter_selecionado)
            
            st.dataframe(df)

        elif opcao == "Atualizar":
            st.subheader("Atualizar Dados de Avaliado")

            nome_busca = st.text_input("Digite o nome para buscar")
            
            if nome_busca:
                df_busca = buscar_por_nome(conn, nome_busca)
                if df_busca.empty:
                    st.warning(f"Nenhum funcionário encontrado com o nome: {nome_busca}")
                else:
                    st.dataframe(df_busca)
                    funcionarios_opcoes = df_busca.apply(lambda row: f"ID {row['id_emp']}: {row['nome_colaborador']}", axis=1).tolist()
                    id_selecionado = st.selectbox("Selecione o Avaliado para Atualizar", options=df_busca['id_emp'], format_func=lambda x: f"ID {x}: {df_busca[df_busca['id_emp'] == x]['nome_colaborador'].values[0]}")
                    
                    # Exibir as colunas para atualização
                    nome_colaborador = st.text_input("Novo Nome do Colaborador", value=df_busca[df_busca['id_emp'] == id_selecionado]['nome_colaborador'].values[0])
                    nome_gestor = st.text_input("Novo Nome do Gestor", value=df_busca[df_busca['id_emp'] == id_selecionado]['nome_gestor'].values[0])
                    setor = st.text_input("Novo Setor", value=df_busca[df_busca['id_emp'] == id_selecionado]['setor'].values[0])
                    diretoria = st.text_input("Nova Diretoria", value=df_busca[df_busca['id_emp'] == id_selecionado]['diretoria'].values[0])
                    nota = st.text_input("Nova Nota", value=df_busca[df_busca['id_emp'] == id_selecionado]['nota'].values[0])
                    soma_final = st.text_input("Nova Soma Final", value=df_busca[df_busca['id_emp'] == id_selecionado]['soma_final'].values[0])
                    
                    # Adicionar as colunas novas
                    colaboracao = st.text_input("Colaboração", value=df_busca[df_busca['id_emp'] == id_selecionado]['colaboracao'].values[0])
                    inteligencia_emocional = st.text_input("Inteligência Emocional", value=df_busca[df_busca['id_emp'] == id_selecionado]['inteligencia_emocional'].values[0])
                    responsabilidade = st.text_input("Responsabilidade", value=df_busca[df_busca['id_emp'] == id_selecionado]['responsabilidade'].values[0])
                    iniciativa_proatividade = st.text_input("Iniciativa / Pró Atividade", value=df_busca[df_busca['id_emp'] == id_selecionado]['iniciativa_proatividade'].values[0])
                    flexibilidade = st.text_input("Flexibilidade", value=df_busca[df_busca['id_emp'] == id_selecionado]['flexibilidade'].values[0])
                    conhecimento_tecnico = st.text_input("Conhecimento Técnico", value=df_busca[df_busca['id_emp'] == id_selecionado]['conhecimento_tecnico'].values[0])

                    if st.button("Atualizar"):
                        atualizar_avaliado(conn, id_selecionado, nome_colaborador, nome_gestor, setor, diretoria, nota, soma_final, colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico)

        elif opcao == "Deletar":
            st.subheader("Deletar Nota Avaliada")

            nome_busca = st.text_input("Digite o nome para buscar")
            
            if nome_busca:
                df_busca = buscar_por_nome(conn, nome_busca)
                if df_busca.empty:
                    st.warning(f"Nenhum funcionário encontrado com o nome: {nome_busca}")
                else:
                    st.dataframe(df_busca)
                    id_selecionado = st.selectbox("Selecione o Avaliado para Deletar", options=df_busca['id_emp'], format_func=lambda x: f"ID {x}: {df_busca[df_busca['id_emp'] == x]['nome_colaborador'].values[0]}")
                    
                    if st.button("Deletar"):
                        deletar_avaliado(conn, id_selecionado)

        conn.close()

    else:
        st.error("Não foi possível conectar ao banco de dados.")

# Funções CRUD que serão usadas na página

def listar_avaliados(conn, quarter=None):
    query = """
    SELECT id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota, soma_final, 
           colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico, data_resposta
    FROM datalake.avaliacao_abcd.avaliacao_abcd
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)
    
    # Calculando o Quarter com base na data de resposta
    df['data_resposta'] = pd.to_datetime(df['data_resposta'])
    df['quarter'] = df['data_resposta'].apply(calcular_quarter)
    
    # Filtrando por Quarter se for especificado
    if quarter and quarter != "Todos":
        df = df[df['quarter'] == quarter]
    
    cursor.close()
    return df


def buscar_por_nome(conn, nome):
    query = f"""
    SELECT id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota, soma_final, 
           colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico
    FROM datalake.avaliacao_abcd.avaliacao_abcd 
    WHERE LOWER(nome_colaborador) LIKE LOWER('%{nome}%')
    """
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)
    cursor.close()
    return df

def atualizar_avaliado(conn, id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota, soma_final, colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico):
    query = f"""
    UPDATE datalake.avaliacao_abcd.avaliacao_abcd 
    SET nome_colaborador = '{nome_colaborador}', nome_gestor = '{nome_gestor}', setor = '{setor}', diretoria = '{diretoria}', 
        nota = '{nota}', soma_final = '{soma_final}', colaboracao = '{colaboracao}', inteligencia_emocional = '{inteligencia_emocional}', 
        responsabilidade = '{responsabilidade}', iniciativa_proatividade = '{iniciativa_proatividade}', flexibilidade = '{flexibilidade}', 
        conhecimento_tecnico = '{conhecimento_tecnico}'
    WHERE id_emp = {id_emp};
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        st.success(f"Avaliador {nome_colaborador} atualizado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao atualizar: {e}")

def deletar_avaliado(conn, id_emp):
    query = f"DELETE FROM datalake.avaliacao_abcd.avaliacao_abcd WHERE id_emp = {id_emp};"
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        st.success(f"Avaliador com ID {id_emp} deletado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao deletar: {e}")