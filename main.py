from fastapi import FastAPI
from db.entities import Base
from db.session import DBSessionManager, DBSessionMiddleware
from api.routers import PagosRouter, ViajesRouter, CommunityRouter
from util.logger import LoggerSessionManager

# 1. Inicialización de Gestores (Logger y DB)
logger_session_manager = LoggerSessionManager()

# Se pasa el logger al manager de la DB
db_session_manager = DBSessionManager(logger_session_manager)

# 2. Creación de tablas (si no existen)
# Nota: Como te conectas a una BD existente, esto no borrará datos, 
# solo crearía tablas que falten según tus entidades.
Base.metadata.create_all(bind=db_session_manager.engine)

# 3. Inicialización de Routers (Inyección de dependencias)
viajes_router = ViajesRouter(db_session_manager, logger_session_manager)
pagos_router = PagosRouter(db_session_manager, logger_session_manager)
community_router = CommunityRouter(db_session_manager, logger_session_manager)

# 4. Configuración de la App
app = FastAPI(title="API Taxis Chicago (FastAPI + SQLAlchemy)")

# Registrar rutas
app.include_router(viajes_router.router)
app.include_router(pagos_router.router)
app.include_router(community_router.router)

# 5. Registrar Middleware (Crucial para request.state.db_session)
app.add_middleware(DBSessionMiddleware, db_session_manager=db_session_manager)