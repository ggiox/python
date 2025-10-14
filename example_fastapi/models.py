# example_fastapi/models.py

# Importações de bibliotecas externas
from typing import List
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
# Importa a Base declarativa que foi definida em database.py
from .database import Base 

# --- Modelo User ---
class User(Base):
    __tablename__ = "users"
    
    # Colunas com tipagem Python e mapped_column para metadados
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    # Senhas e estado
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relacionamento: User.items é uma lista de objetos Item
    items: Mapped[List["Item"]] = relationship(back_populates="owner")


# --- Modelo Item ---
class Item(Base):
    __tablename__ = "items"

    # Colunas simples
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String, index=True, nullable=True) # Uso do tipo "str | None"

    # Chave Estrangeira: mapped_column(ForeignKey)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id")) 

    # Relacionamento: Item.owner é um único objeto User
    owner: Mapped["User"] = relationship(back_populates="items")