# example_fastapi/routers/__init__.py

# Isso permite que você faça a importação "from .routers import users_router" 
# ou "from .routers import items_router" diretamente se quiser.
# No entanto, a forma como fizemos no main.py, importando o módulo inteiro, é geralmente mais clara.

# Exemplo de como exportar a variável 'router' se você renomeá-la localmente
# from .root import router as root_router
# from .users import router as users_router
# from .items import router as items_router