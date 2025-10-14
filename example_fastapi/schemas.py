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

class UserUpdate(BaseModel):
    # Todos os campos são opcionais, exceto se você definir um Pydantic Field com '...'
    # O email pode ser opcional.
    email: str | None = None 
    
    # A senha deve ser opcional. Se for fornecida, será hasheada na lógica CRUD.
    password: str | None = None
    
    # Exemplo: Se você tiver um campo 'is_active' ou 'is_admin'
    is_active: bool | None = None 
    
    class Config:
        # Permite que o Pydantic funcione com atributos de objeto (dot notation)
        from_attributes = True 

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