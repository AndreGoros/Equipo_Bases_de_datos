from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# --- Modelo para la tabla community_area ---
class CommunityArea(BaseModel):
    community_id: int
    community: Optional[str] = None

    class Config:
        orm_mode = True
        title = "CommunityArea"

# --- Modelo para la tabla pagos ---
class Pago(BaseModel):
    trip_id: str
    fare: Optional[float] = 0.0
    tips: Optional[float] = 0.0
    tolls: Optional[float] = 0.0
    extras: Optional[float] = 0.0
    trip_total: Optional[float] = 0.0

    class Config:
        orm_mode = True
        title = "Pago"

# --- Modelo para la tabla ciudad_viaje ---
class CiudadViaje(BaseModel):
    trip_id: str
    pickup_community_area: Optional[int] = None
    dropoff_community_area: Optional[int] = None

    class Config:
        orm_mode = True
        title = "CiudadViaje"

# --- Modelo para la tabla viajes ---
class Viaje(BaseModel):
    trip_id: str
    taxi_id: Optional[str] = None
    trip_start_timestamp: Optional[datetime] = None
    trip_end_timestamp: Optional[datetime] = None
    trip_miles: Optional[float] = None

    # Opcional: Si quisieras devolver el pago y la ciudad anidados dentro del viaje
    # tendrías que descomentar las siguientes líneas y asegurarte de que las relaciones
    # existan en tu archivo entities.py (SQLAlchemy):
    
    # pago_info: Optional[Pago] = None
    # ciudad_info: Optional[CiudadViaje] = None

    class Config:
        orm_mode = True
        title = "Viaje"