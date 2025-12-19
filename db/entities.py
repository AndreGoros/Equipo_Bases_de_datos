from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column

Base = declarative_base()

# ==========================================
# 1. TABLA CATÁLOGO: COMMUNITY AREA
# ==========================================
class CommunityArea(Base):
    __tablename__ = "community_area"

    community_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    community: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)


# ==========================================
# 2. TABLA PRINCIPAL: VIAJES
# ==========================================
class Viaje(Base):
    __tablename__ = "viajes"

    trip_id: Mapped[str] = mapped_column(Text, primary_key=True)
    taxi_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    trip_start_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    trip_end_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    trip_miles: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # uselist=False indica que es una relación 1 a 1
    pago: Mapped["Pago"] = relationship(
        "Pago", back_populates="viaje", uselist=False, cascade="all, delete-orphan"
    )
    
    ciudad_info: Mapped["CiudadViaje"] = relationship(
        "CiudadViaje", back_populates="viaje", uselist=False, cascade="all, delete-orphan"
    )


# ==========================================
# 3. TABLA: PAGOS (Relación 1 a 1 con Viajes)
# ==========================================
class Pago(Base):
    __tablename__ = "pagos"

    trip_id: Mapped[str] = mapped_column(
        ForeignKey("viajes.trip_id", ondelete="CASCADE"), 
        primary_key=True
    )
    
    fare: Mapped[float] = mapped_column(Numeric, nullable=True)
    tips: Mapped[float] = mapped_column(Numeric, nullable=True)
    tolls: Mapped[float] = mapped_column(Numeric, nullable=True)
    extras: Mapped[float] = mapped_column(Numeric, nullable=True)
    trip_total: Mapped[float] = mapped_column(Numeric, nullable=True)

    # Relación inversa
    viaje: Mapped["Viaje"] = relationship("Viaje", back_populates="pago")


# ==========================================
# 4. TABLA: CIUDAD_VIAJE (Relación 1 a 1 con Viajes)
# ==========================================
class CiudadViaje(Base):
    __tablename__ = "ciudad_viaje"


    trip_id: Mapped[str] = mapped_column(
        ForeignKey("viajes.trip_id", ondelete="CASCADE"), 
        primary_key=True
    )

    pickup_community_area: Mapped[Optional[int]] = mapped_column(
        ForeignKey("community_area.community_id"), nullable=True
    )
    dropoff_community_area: Mapped[Optional[int]] = mapped_column(
        ForeignKey("community_area.community_id"), nullable=True
    )

    # Relación inversa hacia Viaje
    viaje: Mapped["Viaje"] = relationship("Viaje", back_populates="ciudad_info")

    # Relaciones opcionales hacia los objetos de CommunityArea
    pickup_area_obj: Mapped["CommunityArea"] = relationship(
        "CommunityArea", foreign_keys=[pickup_community_area]
    )
    dropoff_area_obj: Mapped["CommunityArea"] = relationship(
        "CommunityArea", foreign_keys=[dropoff_community_area]
    )