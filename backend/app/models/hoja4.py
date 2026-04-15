from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time,
    Numeric, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Hoja4Plegador(Base):
    """
    Hoja 4 - Col-locacio Plegador.
    Registre de la instal-lacio del plegador al teler.
    """
    __tablename__ = "hoja4_plegador"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to OF
    of_id = Column(Integer, ForeignKey("ordres_fabricacio.id"), nullable=False, unique=True)
    of = relationship("OrdreFabricacio", back_populates="hoja4")

    # General data
    data = Column(Date)
    hora = Column(Time)

    # Plegador info
    num_teler = Column(Integer)
    num_ferro_plegador = Column(String(50))
    color_plegador = Column(String(50))

    # Verificacions
    verificar_colors = Column(Boolean)
    manquen_cargols = Column(Boolean, default=False)
    cargols_reposats = Column(Boolean, default=False)
    visualitzacio_optim = Column(Boolean, default=False)

    # Valones
    posicio_valones = Column(String(20))  # centrada, descentrada
    mida_valones_baix = Column(Numeric(8, 2))
    mida_valones_dalt = Column(Numeric(8, 2))

    # Confirmacions
    confirmat_mgtz = Column(Boolean, default=False)
    confirmat_ordidor = Column(Boolean, default=False)
    signatura_responsable = Column(String(100))
    signatura_ordidor = Column(String(100))

    # Observacions
    observacions = Column(Text)

    # Status
    estat = Column(String(20), default="borrador")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Hoja4 OF={self.of_id} teler={self.num_teler}>"
