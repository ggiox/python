import streamlit as st
import pandas as pd
from typing import Optional

# =========================================================================
# CLASSE: PostgresConnector
# Responsável por toda a lógica de acesso e consulta ao PostgreSQL.
# =========================================================================

class PostgresConnector:
    """
    Encapsula a conexão e os métodos de consulta para o banco de dados PostgreSQL
    usando o st.connection do Streamlit.
    """
    
    def __init__(self, connection_name: str = "postgresql"):
        """
        Inicializa o conector, tentando estabelecer a conexão com o banco de dados.
        """
        self.connection_name = connection_name
        self.conn = None
        
        try:
            # st.connection armazena a conexão em cache de forma segura
            self.conn = st.connection(self.connection_name, type="sql")
        except Exception as e:
            st.error(f"Erro ao conectar ao banco de dados '{self.connection_name}'. "
                     f"Verifique suas credenciais em .streamlit/secrets.toml. Detalhes: {e}")
            st.stop() # Para o app se a conexão falhar
            
    def get_tables(self) -> Optional[pd.DataFrame]:
        """
        Método que lista todas as tabelas no esquema 'public'.
        Retorna um DataFrame do Pandas ou None em caso de erro.
        """
        st.subheader("Tabelas Encontradas")
        
        # Query SQL para listar tabelas
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        
        # Usamos st.cache_data para cachear o resultado das tabelas,
        # pois elas raramente mudam, economizando tempo.
        @st.cache_data(ttl=600)
        def fetch_table_names():
            try:
                if self.conn is None:
                    st.error("Conexão com o banco de dados não está estabelecida.")
                    return None
                df = self.conn.query(query, ttl=600)
                return df
            except Exception as e:
                st.error(f"Erro ao listar tabelas: {e}")
                return None

        df_tabelas = fetch_table_names()

        if df_tabelas is not None and not df_tabelas.empty:
            st.dataframe(df_tabelas, use_container_width=True)
        else:
            st.warning("Nenhuma tabela encontrada ou erro na consulta de metadados.")
            
        return df_tabelas
            
    def execute_query(self, query: str):
        """
        Método para executar qualquer query SQL fornecida pelo usuário.
        """
        st.subheader("Resultado da Query Personalizada")
        
        # Limpa o cache para garantir que SELECTs recentes sejam atualizados
        st.cache_data.clear()
        
        try:
            # conn.query() executa e tenta retornar um DataFrame. 
            # Funciona para SELECT, INSERT, UPDATE, etc.
            if self.conn is None:
                st.error("Conexão com o banco de dados não está estabelecida.")
                return
            df_resultado = self.conn.query(query, ttl=0) # ttl=0 executa sempre
            
            if not df_resultado.empty:
                # Query de seleção (SELECT)
                st.success("Query SELECT executada com sucesso!")
                st.dataframe(df_resultado, use_container_width=True)
            else:
                # Query de modificação (INSERT, UPDATE, DELETE)
                if query.strip().upper().startswith("SELECT"):
                    st.info("Query SELECT executada, mas retornou um resultado vazio (0 linhas).")
                else:
                    st.success("Comando SQL (INSERT, UPDATE, DELETE, CREATE, etc.) executado com sucesso!")
                    
        except Exception as e:
            # Captura e exibe erros de SQL
            st.error(f"Erro ao executar a Query:\n\n{e}")

# =========================================================================
# APLICAÇÃO STREAMLIT PRINCIPAL
# =========================================================================

def main():
    st.title("Interface para PostgreSQL com Streamlit")
    
    # 1. Criação do OBJETO (instância da classe)
    # Passamos o nome da conexão do secrets.toml (padrão é "postgresql")
    db_connector = PostgresConnector(connection_name="postgresql")
    
    # --- 2. Listar Tabelas (Usando o primeiro método do objeto) ---
    st.markdown("---")
    list_tables = db_connector.get_tables()
    
    # --- 3. Execução de Query Personalizada (Usando o segundo método) ---
    st.markdown("---")
    st.header("Executar Query SQL Personalizada")
    
    # Define uma tabela padrão se nenhuma tabela for encontrada
    table_name = "table_name"
    if list_tables is not None and not list_tables.empty:
        table_name = list_tables.iloc[0, 0]  # Pega o nome da primeira tabela

    # Campo de entrada de texto
    query_input = st.text_area(
        "Digite sua Query SQL:",        
        # A f-String do Python 3.6, permite o uso de variáveis dentro do texto através de chaves {}
        value=f"SELECT * FROM {table_name} LIMIT 10;", 
        height=150,
        key="sql_query_input"
    )

    # Botão de execução
    with st.form("query_form"):
        submitted = st.form_submit_button("Executar Query")

    if submitted and query_input:
        # Chama o método do objeto para executar a query
        db_connector.execute_query(query_input)

if __name__ == "__main__":
    main()