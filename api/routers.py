from typing import List
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm.session import Session

# Importamos Schemas (Pydantic)
from api.models import (
    Viaje as ViajeSchema, 
    Pago as PagoSchema, 
    CommunityArea as CommunitySchema,
    CiudadViaje as CiudadSchema
)
# Importamos Entidades (SQLAlchemy)
from db.entities import Viaje, Pago, CommunityArea, CiudadViaje

# Importamos utilidades
from db.session import DBSessionManager
from util.logger import LoggerSessionManager


# ==========================================
# 1. ROUTER DE VIAJES (Tabla Principal)
# ==========================================
class ViajesRouter:
    router = APIRouter(prefix="/viajes", tags=["Viajes"])

    def __init__(self, db_session_manager: DBSessionManager, logger_session_manager: LoggerSessionManager):
        self.db_session_manager = db_session_manager
        self.logger_session = logger_session_manager
        self.logger = logger_session_manager.get_logger(__name__)

        self.router = APIRouter(prefix="/viajes", tags=["Viajes"])

        # GET /viajes/ (Listado con paginación)
        self.router.add_api_route(
            "/", self.list, methods=["GET"], response_model=List[ViajeSchema]
        )
        # GET /viajes/{trip_id} (Detalle de un viaje)
        self.router.add_api_route(
            "/{trip_id}", self.get, methods=["GET"], response_model=ViajeSchema
        )
        # DELETE /viajes/{trip_id}
        self.router.add_api_route("/{trip_id}", self.delete, methods=["DELETE"])

    def list(self, request: Request, skip: int = 0, limit: int = 100):
        """
        Lista viajes. 
        Nota: 'skip' y 'limit' son query params (ej: /viajes?skip=0&limit=50)
        """
        db_session: Session = request.state.db_session
        self.logger.info(f"Listando viajes: skip={skip}, limit={limit}")
        
        # Consulta básica. Si definiste relaciones en entities.py, 
        # SQLAlchemy las cargará lazy o eager según configures.
        viajes = db_session.query(Viaje).offset(skip).limit(limit).all()
        return viajes

    def get(self, trip_id: str, request: Request):
        db_session: Session = request.state.db_session
        self.logger.info(f"Buscando viaje ID: {trip_id}")
        
        viaje = db_session.query(Viaje).get(trip_id)
        
        if not viaje:
            return JSONResponse(
                status_code=404, content={"error_description": "Viaje no encontrado"}
            )
        return viaje

    def delete(self, trip_id: str, request: Request):
        db_session: Session = request.state.db_session
        viaje = db_session.query(Viaje).get(trip_id)
        
        if not viaje:
            raise HTTPException(status_code=404, detail="Viaje no encontrado")
        
        db_session.delete(viaje)
        # El middleware o context manager se encarga del commit
        return {"message": f"Viaje {trip_id} eliminado correctamente"}


# ==========================================
# 2. ROUTER DE PAGOS
# ==========================================
class PagosRouter:
    router = APIRouter(prefix="/pagos", tags=["Pagos"])

    def __init__(self, db_session_manager: DBSessionManager, logger_session_manager: LoggerSessionManager):
        self.db_session_manager = db_session_manager
        self.logger_session = logger_session_manager
        self.logger = logger_session_manager.get_logger(__name__)

        self.router = APIRouter(prefix="/pagos", tags=["Pagos"])

        # GET /pagos/{trip_id}
        self.router.add_api_route(
            "/{trip_id}", self.get_by_trip_id, methods=["GET"], response_model=PagoSchema
        )

    def get_by_trip_id(self, trip_id: str, request: Request):
        db_session: Session = request.state.db_session
        
        # Buscamos en la tabla Pagos usando trip_id
        pago = db_session.query(Pago).filter(Pago.trip_id == trip_id).first()
        
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado para este viaje")
        
        return pago


# ==========================================
# 3. ROUTER DE COMMUNITY AREAS (Catálogo)
# ==========================================
class CommunityRouter:
    router = APIRouter(prefix="/communities", tags=["Community Areas"])

    def __init__(self, db_session_manager: DBSessionManager, logger_session_manager: LoggerSessionManager):
        self.db_session_manager = db_session_manager
        self.logger_session = logger_session_manager
        self.logger = logger_session_manager.get_logger(__name__)

        self.router = APIRouter(prefix="/communities", tags=["Community Areas"])

        # GET /communities/
        self.router.add_api_route(
            "/", self.list, methods=["GET"], response_model=List[CommunitySchema]
        )
        # GET /communities/{community_id}
        self.router.add_api_route(
            "/{community_id}", self.get, methods=["GET"], response_model=CommunitySchema
        )

    def list(self, request: Request):
        db_session: Session = request.state.db_session
        # Tabla pequeña (catálogo), safe to fetch all
        return db_session.query(CommunityArea).all()

    def get(self, community_id: int, request: Request):
        db_session: Session = request.state.db_session
        area = db_session.query(CommunityArea).get(community_id)
        
        if not area:
            raise HTTPException(status_code=404, detail="Area no encontrada")
        return area