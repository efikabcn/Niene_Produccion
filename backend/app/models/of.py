from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class OrdreFabricacio(Base):
    """
    Ordre de Fabricacio (OF) - The master document that links everything.
    Core data comes from SAGE; we store a local copy plus our own fields.
    """
    __tablename__ = "ordres_fabricacio"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiers (from SAGE)
    of_number = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "26.0610"
    codi_article = Column(String(20))                                         # e.g., "2805"
    nom_article = Column(String(100))                                         # e.g., "WASHINGTON"
    ample = Column(Numeric(6, 1))                                             # e.g., 243.0

    # Urdido params (from SAGE or manual)
    fils_totals = Column(Integer)         # e.g., 7344
    metres = Column(Integer)             # e.g., 2000
    ample_plegador_mm = Column(Integer)  # e.g., 2500
    num_faixes = Column(Integer)         # e.g., 16
    teler_num = Column(Integer)          # e.g., 96

    # Status
    estat = Column(String(20), default="pendent")  # pendent, en_curs, completada, tancada

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    hoja2 = relationship("Hoja2Preparacio", back_populates="of", uselist=False)

    def __repr__(self):
        return f"<OF {self.of_number} - {self.nom_article}>"
