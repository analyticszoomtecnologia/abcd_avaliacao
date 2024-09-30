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

# Função para buscar os subordinados do gestor ou diretor logado
def buscar_funcionarios_subordinados():
    id_gestor = st.session_state.get('id_emp', None)

    if id_gestor:
        connection = conectar_banco()
        cursor = connection.cursor()

        # Busca o nome do gestor com base no id_emp logado
        cursor.execute(f"""
            SELECT Nome
            FROM datalake.silver_pny.func_zoom
            WHERE id = {id_gestor}
        """)
        resultado = cursor.fetchone()

        if resultado:
            nome_gestor = resultado['Nome']

            # Busca os funcionários subordinados diretos
            cursor.execute(f"""
                SELECT id, Nome
                FROM datalake.silver_pny.func_zoom
                WHERE Gestor_Direto = '{nome_gestor}' OR Diretor_Gestor = '{nome_gestor}'
            """)
            funcionarios = cursor.fetchall()

            cursor.close()
            connection.close()

            # Retorna os funcionários como um dicionário
            return {row['id']: row['Nome'] for row in funcionarios}

    return {}

# Função para listar subordinados avaliados
def listar_avaliados_subordinados(conn, quarter=None):
    # Verifica se o gestor logado tem subordinados
    subordinados = buscar_funcionarios_subordinados()

    if not subordinados:
        st.write("Nenhum subordinado encontrado.")
        return pd.DataFrame()  # Retorna um DataFrame vazio

    # Gerar uma lista de IDs dos subordinados
    ids_subordinados = tuple(subordinados.keys())

    query = f"""
    SELECT id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota as nota_final, 
           colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico, data_resposta
    FROM datalake.avaliacao_abcd.avaliacao_abcd
    WHERE id_emp IN {ids_subordinados}
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

# Função que encapsula toda a lógica da página
def func_data_nota():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.error("Você precisa fazer login para acessar essa página.")
        return
    st.title("Avaliações")

    # Opções de CRUD
    opcao = st.selectbox("Escolha a operação", ["Listar", "Deletar"])

    conn = conectar_banco()

    if conn:
        if opcao == "Listar":
            st.subheader("Lista de Avaliados")

            # Adicionando a seleção de Quarter
            quarter_selecionado = st.selectbox("Selecione o Quarter", ["Todos", "Q1", "Q2", "Q3", "Q4"])

            # Filtrando os avaliados pelo Quarter
            if quarter_selecionado == "Todos":
                df = listar_avaliados_subordinados(conn)
            else:
                df = listar_avaliados_subordinados(conn, quarter=quarter_selecionado)

            if not df.empty:
                st.dataframe(df)
            else:
                st.write("Nenhuma avaliação encontrada para o Quarter selecionado.")

        elif opcao == "Deletar":
            st.subheader("Deletar Nota Avaliada")

            subordinados = buscar_funcionarios_subordinados()

            if not subordinados:
                st.warning("Nenhum subordinado encontrado.")
                return

            nome_busca = st.text_input("Digite o nome para buscar")

            if nome_busca:
                df_busca = buscar_por_nome(conn, nome_busca, subordinados)

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

def buscar_por_nome(conn, nome, subordinados):
    ids_subordinados = tuple(subordinados.keys())
    query = f"""
    SELECT id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota, soma_final, 
           colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico
    FROM datalake.avaliacao_abcd.avaliacao_abcd 
    WHERE LOWER(nome_colaborador) LIKE LOWER('%{nome}%') AND id_emp IN {ids_subordinados}
    """
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)
    cursor.close()
    return df

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
