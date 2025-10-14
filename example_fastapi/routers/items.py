# example_fastapi/routers/items.py

# Importações de bibliotecas externas
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Importações de módulos locais
from .. import models, schemas, crud, auth
from ..database import get_db

# Definição das dependências
DBDependency = Annotated[Session, Depends(get_db)]
CurrentUserDependency = Annotated[models.User, Depends(auth.get_current_user)]

# 1. Cria o APIRouter
router = APIRouter(prefix="/items", tags=["Items"])


# CREATE Item (Protegido)
@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item_for_current_user(
    item: schemas.ItemCreate, 
    db: DBDependency, 
    current_user: CurrentUserDependency # Requer autenticação
):
    return crud.create_user_item(db=db, item=item, user_id=current_user.id)

# READ ALL Items
@router.get("/", response_model=list[schemas.Item])
def read_items(db: DBDependency, skip: int = 0, limit: int = 100):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

# READ ONE Item
@router.get("/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: DBDependency):
    item = crud.get_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# DELETE Item (Protegido)
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item")

    crud.delete_item(db, item)