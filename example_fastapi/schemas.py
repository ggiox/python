from pydantic import BaseModel, ConfigDict, EmailStr

# --- Esquemas de Usuário ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    # Todos os campos são opcionais, exceto se você definir um Pydantic Field com '...'
    # O email pode ser opcional.
    email: str | None = None 
    
    # A senha deve ser opcional. Se for fornecida, será hasheada na lógica CRUD.
    password: str | None = None
    
    # Exemplo: Se você tiver um campo 'is_active' ou 'is_admin'
    is_active: bool | None = None 
    
    model_config = ConfigDict(from_attributes=True)

# --- Esquemas de Item ---

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)