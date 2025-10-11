import psycopg2
from psycopg2 import Error

class PostgresDB:
    """
    Uma classe para gerenciar a conexão e a execução de consultas 
    com um banco de dados PostgreSQL usando psycopg2.
    """

    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        """
        Inicializa a classe com os parâmetros de conexão.
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None # Objeto de conexão
        self.cursor = None # Objeto cursor

    def __enter__(self):
        """
        Método chamado ao entrar no bloco 'with'. 
        Tenta estabelecer a conexão.
        """
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            return self

        except Error as e:
            # Em caso de falha na conexão, lança a exceção para ser tratada
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Método chamado ao sair do bloco 'with'.
        Trata transações (commit/rollback) e fecha o cursor e a conexão.
        """
        if self.conn:
            if exc_type is None:
                # Se não houve exceção, faz o commit (salva as alterações)
                self.conn.commit()
            else:
                # Se houve exceção, faz o rollback (desfaz as alterações)
                self.conn.rollback()
                print(f"Transação desfeita devido ao erro: {exc_val}")
                
            self.cursor.close()
            self.conn.close()
            # print("Conexão e cursor fechados.") # Opcional: para feedback

    def execute_query(self, query, params=None, fetch_results=False):
        """
        Executa uma consulta SQL.
        - query: A string SQL com placeholders (%s).
        - params: Tupla ou lista de valores para os placeholders.
        - fetch_results: Se True, retorna os resultados de uma consulta SELECT.
        """
        if not self.cursor:
            raise ConnectionError("A conexão não foi estabelecida ou foi fechada.")

        try:
            self.cursor.execute(query, params)
            
            if fetch_results:
                # Se for um SELECT, retorna os resultados
                return self.cursor.fetchall()
            
            # Retorna o número de linhas afetadas para INSERT/UPDATE/DELETE
            return self.cursor.rowcount 

        except Error as e:
            # Não faz o rollback aqui, o __exit__ faz. Apenas relança o erro.
            raise e

# --- Exemplo de Uso ---

# 1. Defina seus detalhes de conexão
DB_PARAMS = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'py-postgre',  # Use 'localhost' se estiver rodando localmente
}

# Consulta para criar uma tabela (se não existir)
SQL_CREATE = """
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco NUMERIC(10, 2)
);
"""

# Consulta para inserir dados
SQL_INSERT = "INSERT INTO produtos (nome, preco) VALUES (%s, %s);"

# Consulta para selecionar dados
SQL_SELECT = "SELECT nome, preco FROM produtos WHERE preco > %s;"

print("--- Iniciando Operações com o Banco de Dados ---")

try:
    # Cria uma instância da classe e entra no bloco 'with'
    with PostgresDB(**DB_PARAMS) as db:
        print("Conexão bem-sucedida.")
        
        # 1. Cria a tabela (se já existir, não fará nada)
        db.execute_query(SQL_CREATE)
        print("Tabela 'produtos' verificada/criada.")
        
        # 2. Insere um novo produto
        novos_produtos = [
            ("Laranja", 12.50),
            ("Maçã", 8.99),
            ("Banana", 4.00)
        ]
        
        for nome, preco in novos_produtos:
            db.execute_query(SQL_INSERT, (nome, preco))
        print(f"Inseridos {len(novos_produtos)} produtos.")

        # 3. Consulta os produtos mais caros
        preco_minimo = 5.00
        resultados = db.execute_query(SQL_SELECT, (preco_minimo,), fetch_results=True)
        
        print(f"\nProdutos com preço superior a R${preco_minimo:.2f}:")
        for nome, preco in resultados:
            print(f"- {nome}: R${preco}")
            
    # Ao sair do bloco 'with', o commit é executado e a conexão é fechada

except ConnectionError as e:
    print(f"Não foi possível continuar as operações: {e}")
except Error as e:
    print(f"Ocorreu um erro SQL durante a execução: {e}")

print("--- Fim das Operações ---")