from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time,
    Numeric, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Hoja3Revisio(Base):
    """
    Hoja 3 - Fulla de Revisio: Ordida.
    Controls de qualitat del proces d'ordir i plegar.
    """
    __tablename__ = "hoja3_revisio"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to OF
    of_id = Column(Integer, ForeignKey("ordres_fabricacio.id"), nullable=False, unique=True)
    of = relationship("OrdreFabricacio", back_populates="hoja3")

    # General data
    data = Column(Date)
    hora_inici_ordir = Column(Time)
    hora_final_ordir = Column(Time)
    hora_inici_plegar = Column(Time)
    hora_final_plegar = Column(Time)

    # Tensions
    tensio_ordit = Column(Numeric(6, 1))
    tensio_plegat = Column(Numeric(6, 1))

    # Quality checks
    producte_no_conforme = Column(Boolean)
    quadra_amb_fulla = Column(Boolean)

    # Responsables
    responsable_1_nom = Column(String(100))
    responsable_1_faixes = Column(Integer)
    responsable_2_nom = Column(String(100))
    responsable_2_faixes = Column(Integer)

    # Checkboxes - Verificacions
    fileta_neta = Column(Boolean, default=False)
    avanc_automatic = Column(Boolean, default=False)
    avanc_valor = Column(String(50))
    fils_creuats = Column(Boolean, default=False)
    revisat_passat_pua = Column(Boolean, default=False)
    coincidir_mostra = Column(Boolean, default=False)
    mida_pua_igual = Column(Boolean, default=False)
    encarament_pua = Column(Boolean, default=False)
    primer_fil_faixa = Column(Boolean, default=False)

    # Observacions
    observacions = Column(Text)

    # Status
    estat = Column(String(20), default="borrador")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Hoja3 OF={self.of_id} estat={self.estat}>"
