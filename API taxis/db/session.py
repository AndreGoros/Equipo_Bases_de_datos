from fastapi import Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

# Asegúrate de que este archivo existe, o elimina la dependencia si no usas logger
from util.logger import LoggerSessionManager 

# --- CONFIGURACIÓN DE CONEXIÓN ---
# Ajusta usuario, contraseña y puerto según tu configuración local de PostgreSQL
# Formato: postgresql+psycopg2://usuario:password@host:puerto/nombre_base_datos
DATABASE_URL = "postgresql+psycopg2://postgres:tu_password@localhost:5432/proyecto_taxis"


class DBSessionManager:

    def __init__(
        self,
        logger_session_manager: LoggerSessionManager,
        db_url: str = DATABASE_URL,
        echo: bool = False,
    ):
        # future=True asegura compatibilidad con SQLAlchemy 2.0
        self.engine = create_engine(db_url, echo=echo, future=True)
        
        self.logger_session_manager = logger_session_manager
        self.logger = self.logger_session_manager.get_logger()
        
        self.SessionLocal = sessionmaker(
            bind=self.engine, 
            autoflush=False, 
            autocommit=False, 
            future=True
        )

    @contextmanager
    def get_managed_session(self):
        """
        Generador de contexto que maneja el ciclo de vida de la sesión:
        crear -> entregar -> commit (si todo bien) -> rollback (si error) -> cerrar.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error en la transacción de BD: {str(e)}")
            raise e
        finally:
            session.close()


class DBSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware que inyecta una sesión de base de datos en cada request.
    Permite usar: request.state.db_session en los endpoints.
    """
    def __init__(self, app, db_session_manager: DBSessionManager):
        super().__init__(app)
        self.db_session_manager = db_session_manager

    async def dispatch(self, request: Request, call_next):
        try:
            with self.db_session_manager.get_managed_session() as db_session:
                # Inyectamos la sesión en el estado del request
                request.state.db_session = db_session
                
                # Procesamos el request
                response: Response = await call_next(request)
                
                return response
        except Exception as e:
            # Si ocurre un error no manejado, aseguramos que el error suba
            # (El middleware de excepciones de FastAPI lo capturará)
            raise e