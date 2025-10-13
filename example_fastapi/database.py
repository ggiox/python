# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Importações para o modelo 2.0
from sqlalchemy.orm import DeclarativeBase 
from typing import Generator

# SUBSTITUA PELA SUA URL DE CONEXÃO DO POSTGRESQL
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:postgres@py-postgres:5432/postgres" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Dependência para obter a sessão do DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()