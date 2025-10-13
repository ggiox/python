from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, crud, auth
from .database import engine, get_db

# ----------------------------------------------------
# Inicialização do Banco de Dados e Criação do Superusuário
# ----------------------------------------------------

# 1. Cria todas as tabelas no DB (se não existirem)
models.Base.metadata.create_all(bind=engine)

# 2. Cria o usuário admin se ele não existir
try:
    db = next(get_db())
    crud.create_initial_superuser(db=db)
finally:
    if 'db' in locals() and db:
        db.close()


# ----------------------------------------------------
# Configuração do FastAPI e suas Rotas
# ----------------------------------------------------

app = FastAPI()

# Dependência do DB
DBDependency = Annotated[Session, Depends(get_db)]
# Dependência de Usuário Autenticado
CurrentUserDependency = Annotated[models.User, Depends(auth.get_current_user)]


# --- Rota de Autenticação (Login) ---
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: DBDependency
) -> dict:
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Rota Protegida de Teste ---
@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: CurrentUserDependency):
    return current_user


# --- Rotas CRUD de Usuário (Criação e Leitura) ---
# A criação de usuário é pública para permitir o registro
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
# Caso queira restrigir a criação de usuários, adicione a dependência de autenticação:
# def create_user(user: schemas.UserCreate, db: DBDependency, current_user: CurrentUserDependency):
def create_user(user: schemas.UserCreate, db: DBDependency):    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# A listagem de usuários pode ser protegida (opcionalmente)
@app.get("/users/", response_model=list[schemas.User])
def read_users(db: DBDependency, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


# --- Rotas CRUD de Item (PROTEGIDAS) ---

# CREATE
@app.post("/users/me/items/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item_for_current_user(
    item: schemas.ItemCreate, 
    db: DBDependency, 
    current_user: CurrentUserDependency # Requer autenticação
):
    return crud.create_user_item(db=db, item=item, user_id=current_user.id)

# READ ALL
@app.get("/items/", response_model=list[schemas.Item])
def read_items(db: DBDependency, skip: int = 0, limit: int = 100):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

# READ ONE
@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: DBDependency):
    item = crud.get_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# DELETE
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int, 
    db: DBDependency, 
    current_user: CurrentUserDependency # Requer autenticação
):
    item = crud.get_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Validação de propriedade: só pode deletar seu próprio item
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")

    crud.delete_item(db, item)
    return 

# *Observação: Rotas PUT/PATCH para atualização seguiriam a mesma lógica de DELETE e CREATE.