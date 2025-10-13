from pydantic import BaseModel, EmailStr

# --- Esquemas de Usuário ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        # Permite mapeamento do ORM (SQLAlchemy) para o Pydantic
        orm_mode = True 

# --- Esquemas de Item ---

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True