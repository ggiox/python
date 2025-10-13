from sqlalchemy.orm import Session
from . import models, schemas, auth

# --- Funções de Usuário ---

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Função para criar um usuário admin inicial ---

def create_initial_superuser(db: Session) -> models.User:
    # 1. Tenta buscar o usuário 'admin@admin.com'
    admin_email = "admin@admin.com"
    db_user = get_user_by_email(db, email=admin_email)

    if db_user:
        # Usuário já existe, retorna o existente
        print(f"Usuário admin '{admin_email}' já existe.")
        return db_user
    
    # 2. Se não existir, cria um novo usuário admin
    
    # Definimos os dados do admin (use uma senha forte na produção!)
    admin_data = schemas.UserCreate(
        email=admin_email,
        password="Admin@01" # Senha a ser hasheada
    )
    
    # Cria o usuário usando a lógica existente de criação e hashing
    db_user = create_user(db=db, user=admin_data)
    
    print(f"Usuário admin '{admin_email}' criado com sucesso.")
    return db_user

# --- Funções de Item ---

def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int) -> models.Item:
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Funções de CRUD para Item (Leitura, Atualização, Exclusão)
def get_item(db: Session, item_id: int) -> models.Item | None:
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def delete_item(db: Session, item: models.Item):
    db.delete(item)
    db.commit()