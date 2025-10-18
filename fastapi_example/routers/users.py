# example_fastapi/routers/users.py

# Importações de bibliotecas externas
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
# Importações de módulos locais
from .. import models, schemas, crud, auth
from ..database import get_db

# Definição das dependências (Repetição necessária para evitar importação circular)
DBDependency = Annotated[Session, Depends(get_db)]
CurrentUserDependency = Annotated[models.User, Depends(auth.get_current_user)]

# 1. Cria o APIRouter
router = APIRouter(prefix="/users", tags=["Users & Auth"])

# Rota de Autenticação (Login)
@router.post("/token")
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

# Rota de Criação de Usuário (Registro Público)
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: DBDependency):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# Rota Protegida para obter o usuário logado
@router.get("/me/", response_model=schemas.User)
def read_users_me(current_user: CurrentUserDependency):
    return current_user

# Rota para listar todos os usuários (Protegida)
@router.get("/", response_model=list[schemas.User])
def read_users(
    db: DBDependency,
    current_user: CurrentUserDependency, # Requer que o usuário esteja logado
    skip: int = 0, 
    limit: int = 100
):
    """
    Lista todos os usuários cadastrados. Acesso restrito a usuários autenticados.
    """
    # Você não precisa de uma função CRUD nova, pois o SQLAlchemy já faz essa lógica
    # diretamente, ou você pode definir uma função no crud.py se preferir.
    
    # Se você tivesse um campo 'is_admin' no modelo User,
    # poderia adicionar uma verificação aqui:
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Acesso negado")
        
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Rota de Alteração (UPDATE/PATCH) de Usuário
@router.patch("/{user_id}", response_model=schemas.User)
def update_user_record(
    user_id: int, 
    user_update: schemas.UserUpdate, 
    db: DBDependency,
    current_user: CurrentUserDependency # Rota Protegida
):
    # Verificação de Autorização: Apenas o próprio usuário pode alterar seu registro
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Não autorizado a modificar este registro."
        )

    updated_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado."
        )
    
    return updated_user