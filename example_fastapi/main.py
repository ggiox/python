# Importações de bibliotecas externas
from fastapi import FastAPI
from . import models, crud
from .database import engine, get_db
# Importe todos os routers
from .routers import users, items, root # <- Adicione 'root'

# ----------------------------------------------------
# Inicialização (Sem Alteração)
# ----------------------------------------------------

# Cria todas as tabelas no DB
models.Base.metadata.create_all(bind=engine)

# Cria o usuário admin se ele não existir
try:
    db = next(get_db())
    crud.create_initial_superuser(db=db)
finally:
    if 'db' in locals() and db:
        db.close()


# ----------------------------------------------------
# Aplicação FastAPI
# ----------------------------------------------------

app = FastAPI()

# 2. Incluir os routers na aplicação principal
# É boa prática incluir a rota raiz primeiro (sem prefixo)
app.include_router(root.router) # Inclui a rota raiz
app.include_router(users.router)
app.include_router(items.router)