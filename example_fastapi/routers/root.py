# routers/root.py

from fastapi import APIRouter

# 1. Cria o APIRouter
router = APIRouter(tags=["General"])

@router.get("/")
async def root_info():
    """
    Retorna a apresentação básica do projeto de estudo da API.
    """
    return {
        "project": "FastAPI CRUD & Auth Study API",
        "version": "1.0.0",
        "status": "online",
        "description": "API de estudo construída com FastAPI, SQLAlchemy (PostgreSQL) e JWT para demonstrar operações CRUD em usuários e itens, com autenticação completa.",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "auth": "/users/token",
            "users": "/users/",
            "items": "/items/"
        }
    }