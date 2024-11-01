import streamlit as st
import pandas as pd
from databricks import sql
from dotenv import load_dotenv
import os

load_dotenv()
DB_SERVER_HOSTNAME = os.getenv("DB_SERVER_HOSTNAME")
DB_HTTP_PATH = os.getenv("DB_HTTP_PATH")
DB_ACCESS_TOKEN = os.getenv("DB_ACCESS_TOKEN")


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

def buscar_funcionarios_subordinados():
    id_gestor = st.session_state.get('id_emp', None)

    if id_gestor:
        connection = conectar_banco()
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT Nome
            FROM datalake.silver_pny.func_zoom
            WHERE id = {id_gestor}
        """)
        resultado = cursor.fetchone()

        if resultado:
            nome_gestor = resultado['Nome']

            cursor.execute(f"""
                SELECT id, Nome
                FROM datalake.silver_pny.func_zoom
                WHERE Gestor_Direto = '{nome_gestor}' OR Diretor_Gestor = '{nome_gestor}'
            """)
            funcionarios = cursor.fetchall()

            cursor.close()
            connection.close()

            return {row['id']: row['Nome'] for row in funcionarios}

    return {}

def listar_avaliados_subordinados(conn, quarter=None):
    subordinados = buscar_funcionarios_subordinados()

    if not subordinados:
        st.write("Nenhum subordinado encontrado.")
        return pd.DataFrame() 

    ids_subordinados = tuple(subordinados.keys())

    query = f"""
        SELECT id_emp, nome_colaborador, nome_gestor, setor, diretoria, nota as nota_final, 
            colaboracao, inteligencia_emocional, responsabilidade, iniciativa_proatividade, flexibilidade, conhecimento_tecnico, data_resposta, data_resposta_quarter
        FROM datalake.avaliacao_abcd.avaliacao_abcd
        WHERE id_emp IN {ids_subordinados}
        """

    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)

    df['data_resposta_quarter'] = pd.to_datetime(df['data_resposta_quarter'])
    df['quarter'] = df['data_resposta_quarter'].apply(calcular_quarter)

    if quarter and quarter != "Todos":
        df = df[df['quarter'] == quarter]

    cursor.close()
    return df

def func_data_nota():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.error("Você precisa fazer login para acessar essa página.")
        return
    st.title("Avaliações")

    opcao = st.selectbox("Escolha a operação", ["Listar", "Deletar"])

    conn = conectar_banco()

    if conn:
        if opcao == "Listar":
            st.subheader("Lista de Avaliados")

            quarter_selecionado = st.selectbox("Selecione o Quarter", ["Todos", "Q1", "Q2", "Q3", "Q4"])

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
    
    st.markdown(
        """
        <br><hr>
        <div style='text-align: center;'>
            Desenvolvido por 
            <a href='https://www.linkedin.com/in/gabriel-cordeiro-033641144/' target='_blank' style='text-decoration: none; color: #0A66C2;'>
                Gabriel Cordeiro
                <img src='https://upload.wikimedia.org/wikipedia/commons/f/f8/LinkedIn_icon_circle.svg' alt='LinkedIn' width='20' style='vertical-align: middle; margin-right: 5px;' />
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


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