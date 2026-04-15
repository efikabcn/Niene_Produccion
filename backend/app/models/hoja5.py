from sqlalchemy import (
    Column, Integer, String, DateTime, Date,
    Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Hoja5Esquema(Base):
    """
    Hoja 5 - Esquema de Montada.
    Esquema de les filades (colors i quantitats) de la montada.
    """
    __tablename__ = "hoja5_esquema"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to OF
    of_id = Column(Integer, ForeignKey("ordres_fabricacio.id"), nullable=False, unique=True)
    of = relationship("OrdreFabricacio", back_populates="hoja5")

    # General data
    data = Column(Date)

    # Observacions
    observacions = Column(Text)

    # Status
    estat = Column(String(20), default="borrador")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Child rows
    filades = relationship("Hoja5Filada", back_populates="hoja5", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hoja5 OF={self.of_id} estat={self.estat}>"


class Hoja5Filada(Base):
    """
    Rows in the FILADES table within Hoja 5.
    Each row represents a color/thread group in the schema.
    """
    __tablename__ = "hoja5_filada"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to Hoja5
    hoja5_id = Column(Integer, ForeignKey("hoja5_esquema.id"), nullable=False)
    hoja5 = relationship("Hoja5Esquema", back_populates="filades")

    # Filada data
    quantitat = Column(Integer)
    color = Column(String(50))
    notes = Column(String(200))
    total_acumulat = Column(Integer)

    # Order within the table
    ordre = Column(Integer, default=0)

    def __repr__(self):
        return f"<Filada {self.color} qty={self.quantitat}>"
