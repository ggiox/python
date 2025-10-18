from sqlalchemy import create_engine, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError

# --- 1. Configuração do Banco de Dados ---
# Formato da URL: 'dialeto+driver://usuario:senha@host:porta/nome_do_banco'
DB_URL = "postgresql+psycopg://postgres:postgres@py-postgres:5432/postgres"

# Crie o Engine, o ponto de entrada para o banco de dados
try:
    engine = create_engine(DB_URL, echo=False) # 'echo=True' mostra o SQL gerado
except Exception as e:
    print(f"Erro ao criar o Engine. Verifique o DB_URL: {e}")
    exit()

# Crie a Base para a definição das classes (modelos)
Base = declarative_base()

# --- 2. Definição da Classe (Modelo ORM) ---
class Cliente(Base):
    """
    Mapeia para a tabela 'cliente' no banco de dados.
    """
    __tablename__ = 'cliente' # Nome da tabela no PostgreSQL

    # Definição das colunas com tipagem para SQLAlchemy 2.x
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Método para uma representação amigável do objeto
    def __repr__(self):
        return f"Cliente(id={self.id}, nome='{self.nome}', email='{self.email}')"

# --- 3. Criação da Tabela ---
# Cria a tabela no banco de dados, se ela não existir
Base.metadata.create_all(engine)
print("Tabela 'cliente' verificada/criada.")

# --- 4. Configuração da Sessão ---
# A Sessão é a área de staging para todas as operações de banco de dados
Session = sessionmaker(bind=engine)

# --- 5. Função de Demonstração (Utilizando a Classe Cliente) ---
def executar_operacoes_cliente():
    """
    Demonstra as operações CRUD (Create, Read, Update, Delete) usando o ORM.
    """
    # Gerenciador de contexto para a sessão, garante que ela será fechada
    try:
        with Session.begin() as session:
            print("\n--- INSERINDO NOVOS CLIENTES ---")
            
            # A. Create (Inserir dados)
            cliente1 = Cliente(nome="Maria Silva", email="maria.silva@exemplo.com")
            cliente2 = Cliente(nome="João Souza", email="joao.souza@exemplo.com")
            
            session.add_all([cliente1, cliente2])
            
            # O commit é feito automaticamente ao sair do bloco 'with Session.begin() as session:'
            print("Clientes inseridos na sessão.")

            print("\n--- CONSULTANDO CLIENTES (READ) ---")
            
            # B. Read (Consultar todos)
            clientes = session.query(Cliente).all()
            print("Todos os clientes no BD:")
            for cliente in clientes:
                print(f"  ID: {cliente.id}, Nome: {cliente.nome}, Email: {cliente.email}")
            
            # C. Read (Consultar com filtro)
            # Consulta por nome
            cliente_joao = session.query(Cliente).filter(Cliente.nome == "João Souza").first()
            if cliente_joao:
                print(f"\nCliente 'João Souza' encontrado (ID: {cliente_joao.id}).")
                
                # D. Update (Atualizar dados)
                cliente_joao.email = "joao.s.novo@exemplo.com"
                print(f"Email do ID {cliente_joao.id} atualizado para: {cliente_joao.email}")
                
            # E. Delete (Excluir dados)
            # Remove o cliente1 (Maria Silva) da sessão
            session.delete(cliente1) 
            print(f"\nCliente com ID {cliente1.id} (Maria Silva) marcado para exclusão.")
            
        # O commit final é executado aqui.

        # --- Reconsultando para verificar as alterações ---
        with Session.begin() as session_check:
            print("\n--- VERIFICANDO ALTERAÇÕES FINAIS ---")
            clientes_finais = session_check.query(Cliente).all()
            print("Clientes restantes no BD:")
            for cliente in clientes_finais:
                print(f"  ID: {cliente.id}, Nome: {cliente.nome}, Email: {cliente.email}")

    except SQLAlchemyError as e:
        print(f"\nOcorreu um erro na transação (SQLAlchemyError): {e}")
        # O rollback é feito automaticamente pelo bloco 'with Session.begin()' em caso de erro.
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

# Executa a demonstração
executar_operacoes_cliente()
print("\nOperações do ORM concluídas.")