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

    def __init__(
        self,
        db_session_manager: DBSessionManager, 
        logger_session_manager: LoggerSessionManager
    ):
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

        # INSERT /viajes/ 
        self.router.add_api_route(
            "/", self.create, methods=["POST"], response_model=ViajeSchema)

        # UPDATE /viajes/{trip_id} se manejan en otro router o endpoint separado
        self.router.add_api_route(
            "/{trip_id}", self.update, methods=["PUT"], response_model=ViajeSchema)

    def list(self, request: Request, skip: int = 0, limit: int = 100, community_id: int = Query(default=None,ge=1, description="ID de Community Area de salida")):
        """
        Lista viajes. 
        Nota: 'skip' y 'limit' son query params para paginación.
        """
        db_session: Session = request.state.db_session
        self.logger.info(f"Listando viajes: skip={skip}, limit={limit}")

        if community_id is not None:
            # Filtrar por ciudad_id si se proporciona
            viajes = (
                db_session.query(Viaje)
                .join(CiudadViaje, Viaje.trip_id == CiudadViaje.trip_id)
                .join(CommunityArea, CiudadViaje.pickup_community_area == CommunityArea.community_id)
                .filter(CommunityArea.community_id == community_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
            return viajes
        
        # Consulta básica. Si definiste relaciones en entities.py, 
        # SQLAlchemy las cargará lazy o eager según configures.
        viajes = db_session.query(Viaje).offset(skip).limit(limit).all()
        return viajes

    def list(self, request: Request, skip: int = 0, limit: int = 100, community_id: int = Query(default=None,ge=1, description="ID de Community Area de arrivo")):
        """
        Lista viajes. 
        Nota: 'skip' y 'limit' son query params para paginación.
        """
        db_session: Session = request.state.db_session
        self.logger.info(f"Listando viajes: skip={skip}, limit={limit}")

        if community_id is not None:
            # Filtrar por ciudad_id si se proporciona
            viajes = (
                db_session.query(Viaje)
                .join(CiudadViaje, Viaje.trip_id == CiudadViaje.trip_id)
                .join(CommunityArea, CiudadViaje.dropoff_community_area == CommunityArea.community_id)
                .filter(CommunityArea.community_id == community_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
            return viajes
        
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
    
    def create(self, request: Request, data: ViajeSchema):
        """Crea un nuevo viaje en la BD."""
        db_session: Session = request.state.db_session
        self.logger.info(f"Creando nuevo viaje: {data.trip_id}")
        
        # Convertimos el Schema Pydantic a la Entidad SQLAlchemy
        # model_dump() se usa en Pydantic v2
        new_viaje = Viaje(**data.model_dump())
        
        try:
            db_session.add(new_viaje)
            db_session.flush() # Hacemos flush para detectar errores (ej. ID duplicado)
            return new_viaje
        except Exception as e:
            self.logger.error(f"Error al crear viaje: {e}")
            raise HTTPException(status_code=400, detail="Error al crear el viaje. Verifique que el ID no exista.")

    def update(self, trip_id: str, request: Request, data: ViajeSchema):
        """Actualiza un viaje existente."""
        db_session: Session = request.state.db_session
        self.logger.info(f"Actualizando viaje ID: {trip_id}")
        
        viaje = db_session.query(Viaje).get(trip_id)
        if not viaje:
            raise HTTPException(status_code=404, detail="Viaje no encontrado")

        # Actualizamos los campos
        # exclude_unset=True evita actualizar campos que no enviaste en el JSON
        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(viaje, key):
                setattr(viaje, key, value)
        
        db_session.flush()
        return viaje


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
        
        # POST /pagos/ (Crear Pago)
        self.router.add_api_route(
            "/", self.create, methods=["POST"], response_model=PagoSchema
        )

        # PUT /pagos/{trip_id} (Actualizar Pago)
        self.router.add_api_route(
            "/{trip_id}", self.update, methods=["PUT"], response_model=PagoSchema
        )

        # DELETE /pagos/{trip_id} (Eliminar Pago)
        self.router.add_api_route(
            "/{trip_id}", self.delete, methods=["DELETE"]
        )

    def get_by_trip_id(self, trip_id: str, request: Request):
        db_session: Session = request.state.db_session
        pago = db_session.query(Pago).filter(Pago.trip_id == trip_id).first()
        
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado para este viaje")
        
        return pago

    def create(self, request: Request, data: PagoSchema):
        """
        Registra el pago de un viaje existente.
        El trip_id dentro de 'data' debe existir previamente en la tabla 'viajes'.
        """
        db_session: Session = request.state.db_session
        self.logger.info(f"Registrando pago para viaje ID: {data.trip_id}")

        new_pago = Pago(**data.model_dump())

        try:
            db_session.add(new_pago)
            db_session.flush()
            return new_pago
        except IntegrityError as e:
            # Esto pasa si el trip_id no existe en la tabla viajes
            db_session.rollback()
            self.logger.error(f"Error de integridad al crear pago: {e}")
            raise HTTPException(
                status_code=400, 
                detail="Error: Verifique que el trip_id exista en la tabla Viajes y que no tenga ya un pago registrado."
            )
        except Exception as e:
            db_session.rollback()
            self.logger.error(f"Error al crear pago: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def update(self, trip_id: str, request: Request, data: PagoSchema):
        """Actualiza la información de un pago existente."""
        db_session: Session = request.state.db_session
        self.logger.info(f"Actualizando pago del viaje ID: {trip_id}")
        
        # Buscamos el pago
        pago = db_session.query(Pago).filter(Pago.trip_id == trip_id).first()
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        # Actualizamos solo los campos enviados
        for key, value in data.model_dump(exclude_unset=True).items():
            # Evitamos modificar el trip_id ya que es la PK y FK
            if key == "trip_id":
                continue
            if hasattr(pago, key):
                setattr(pago, key, value)
        
        db_session.flush()
        return pago

    def delete(self, trip_id: str, request: Request):
        """Elimina el registro de pago asociado a un viaje."""
        db_session: Session = request.state.db_session
        self.logger.info(f"Eliminando pago del viaje ID: {trip_id}")
        
        pago = db_session.query(Pago).filter(Pago.trip_id == trip_id).first()
        
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        db_session.delete(pago)
        return {"message": f"Pago del viaje {trip_id} eliminado correctamente"}


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