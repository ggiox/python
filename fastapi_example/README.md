
# Exemplo de FastAPI com PostgreSql

Estrutura do Projeto:
.
├── main.py        # Aplicação FastAPI, rotas de autenticação e inclusão de routers
├── database.py    # Configuração do banco de dados (Engine, Session, Base)
├── models.py      # Modelos de dados do SQLAlchemy (User, Item)
├── schemas.py     # Esquemas Pydantic (validação de dados)
├── auth.py        # Funções de segurança (Hashing, JWT, Dependência de Usuário)
├── crud.py        # Funções de CRUD (interação com o banco de dados)
└── routers/
    ├── __init__.py
    ├── users.py   # Contém rotas de Autenticação e Usuário (token, create_user, update_user)
    └── items.py   # Contém rotas CRUD de Item

# FastAPI e Uvicorn
pip install "fastapi[standard]"

# SQLAlchemy (e o driver do PostgreSQL)
pip install sqlalchemy psycopg2-binary

# Hashing de senha e JWT (para autenticação)
pip install PyJWT
pip install passlib[bcrypt]