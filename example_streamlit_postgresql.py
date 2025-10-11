import streamlit as st
import pandas as pd

st.title("Lista de Tabelas do PostgreSQL e Execução de Queries")

# --- 1. CONFIGURAÇÃO DA CONEXÃO (Bloco de código do exemplo anterior) ---
try:
    # O nome 'postgresql' corresponde à chave definida em secrets.toml
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados. Verifique suas credenciais em .streamlit/secrets.toml. Detalhes do erro: {e}")
    st.stop()

# Query para listar tabelas
QUERY_LISTA_TABELAS = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
"""

@st.cache_data(ttl=600)
def get_table_names():
    try:
        df = conn.query(QUERY_LISTA_TABELAS, ttl=600)
        return df
    except Exception as e:
        st.error(f"Erro ao executar a consulta: {e}")
        return pd.DataFrame()

# --- Exibição da lista de tabelas ---
st.header("Tabelas Encontradas")
df_tabelas = get_table_names()
st.dataframe(df_tabelas, use_container_width=True)

# ------------------------------------------------------------------------
# --- NOVO MÉTODO: Execução de Query Arbitrária ---
# ------------------------------------------------------------------------

st.markdown("---")
st.header("Executar Query SQL Personalizada")

# 2. Campo de entrada de texto (TextArea) para a Query
query_input = st.text_area(
    "Digite sua Query SQL (SELECT, INSERT, UPDATE, DELETE...)",
    value="SELECT * FROM table_name LIMIT 10;", # Query de exemplo
    height=150,
    key="sql_query_input"
)

# 3. Botão para acionar a execução
# Usamos um 'form' para ter controle sobre quando o script deve ser re-executado.
with st.form("query_form"):
    submitted = st.form_submit_button("Executar Query")

if submitted and query_input:
    # Remove o cache de todas as queries para garantir que a nova execução seja feita
    st.cache_data.clear()
    
    # 4. Executa a Query e exibe o resultado
    try:
        # Tenta executar a query
        # O método conn.query() é ideal para SELECTs, pois retorna um DataFrame.
        # Ele funcionará para INSERT/UPDATE/DELETE, mas a saída será vazia.
        df_resultado = conn.query(query_input, ttl=0) # ttl=0 garante que a query é executada sempre
        
        # Verifica se o resultado é um DataFrame (indicando um SELECT)
        if not df_resultado.empty:
            st.success("Query SELECT executada com sucesso!")
            st.subheader("Resultado")
            st.dataframe(df_resultado, use_container_width=True)
        else:
            # Caso não haja DataFrame, a query pode ter sido um INSERT, UPDATE, DELETE, etc.
            
            # Para queries INSERT, UPDATE, DELETE, o st.connection() do Streamlit
            # normalmente executa e faz o commit automaticamente em modo autocommit.
            # No entanto, a forma mais robusta de lidar com estas é usando conn.session.
            
            # Tenta um tratamento específico se não for SELECT:
            if query_input.strip().upper().startswith("SELECT"):
                 st.info("Query SELECT executada, mas retornou um resultado vazio (0 linhas).")
            else:
                 # Assumimos que foi uma operação que alterou dados (DML)
                 st.success("Comando SQL (INSERT, UPDATE, DELETE, CREATE, etc.) executado com sucesso!")


    except Exception as e:
        # Exibe qualquer erro de execução de SQL
        st.error(f"Erro ao executar a Query:\n\n{e}")

# ------------------------------------------------------------------------