from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time,
    Numeric, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Hoja2Preparacio(Base):
    """
    Hoja 2 - Preparacio i Muntatge del Fil.
    Full de revisio de proces.
    """
    __tablename__ = "hoja2_preparacio"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to OF
    of_id = Column(Integer, ForeignKey("ordres_fabricacio.id"), nullable=False, unique=True)
    of = relationship("OrdreFabricacio", back_populates="hoja2")

    # General data
    data = Column(Date)
    hora_inici_prep = Column(Time)
    hora_final_prep = Column(Time)

    # Preparacio i Muntatge del Fil
    fil_traspassat_sllp = Column(Boolean)
    nom_resp_preparacio = Column(String(100))
    vores = Column(Boolean)
    telomares_panama = Column(Boolean, default=False)
    penelope = Column(Boolean, default=False)
    fitxa_antiga = Column(Boolean, default=False)
    guia_montatge = Column(Boolean, default=False)
    repas_conjunt = Column(Boolean, default=False)

    # Condicions
    cons_bones_condicions = Column(Boolean)

    # Responsables
    responsables_muntar = Column(String(200))
    responsables_desmuntar = Column(String(200))
    ordidor_revisio = Column(String(100))

    # Observacions
    observacions = Column(Text)

    # Status
    estat = Column(String(20), default="borrador")  # borrador, completat, revisat

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    muntada = relationship("Hoja2Muntada", back_populates="hoja2", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hoja2 OF={self.of_id} estat={self.estat}>"


class Hoja2Muntada(Base):
    """
    Rows in the MUNTADA table within Hoja 2.
    Each row represents a bulto of thread mounted on the creel.
    """
    __tablename__ = "hoja2_muntada"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to Hoja2
    hoja2_id = Column(Integer, ForeignKey("hoja2_preparacio.id"), nullable=False)
    hoja2 = relationship("Hoja2Preparacio", back_populates="muntada")

    # Muntada data
    color = Column(String(50))        # Champagne, Azafran, Toffe, Cru
    partida = Column(String(20))      # e.g., "04932"
    proveidor = Column(String(20))    # e.g., "06"
    n_bulto = Column(String(30))      # e.g., "48871"
    conos = Column(Integer)           # e.g., 36
    pes = Column(Numeric(8, 2))       # e.g., 66.20 kg

    # Order within the table
    ordre = Column(Integer, default=0)

    def __repr__(self):
        return f"<Muntada {self.color} conos={self.conos} pes={self.pes}>"
