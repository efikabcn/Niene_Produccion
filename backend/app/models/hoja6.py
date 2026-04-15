from sqlalchemy import (
    Column, Integer, String, DateTime, Date,
    Numeric, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Hoja6Programacio(Base):
    """
    Hoja 6 - Programacio Passat de Pua.
    Programacio de les faixes i passat de pua.
    """
    __tablename__ = "hoja6_programacio"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to OF
    of_id = Column(Integer, ForeignKey("ordres_fabricacio.id"), nullable=False, unique=True)
    of = relationship("OrdreFabricacio", back_populates="hoja6")

    # General data
    data = Column(Date)
    nom_article = Column(String(150))
    total_fils = Column(Integer)

    # Config passat pua
    passat_pua_faixes = Column(Integer)
    pua_pallcm = Column(String(20))
    passat_fils_pall = Column(String(20))

    # Calculated fields (stored for reference)
    total_fils_calculat = Column(Integer)
    total_ample_mm = Column(Numeric(10, 2))
    ample_valones_cm = Column(Numeric(10, 2))
    eixamplament_mm = Column(Numeric(10, 2))

    # Observacions
    observacions = Column(Text)

    # Status
    estat = Column(String(20), default="borrador")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Child rows
    faixes = relationship("Hoja6Faixa", back_populates="hoja6", cascade="all, delete-orphan")
    programacio = relationship("Hoja6ProgramacioRow", back_populates="hoja6", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hoja6 OF={self.of_id} fils={self.total_fils}>"


class Hoja6Faixa(Base):
    """
    Rows in the FAIXES table within Hoja 6.
    """
    __tablename__ = "hoja6_faixa"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to Hoja6
    hoja6_id = Column(Integer, ForeignKey("hoja6_programacio.id"), nullable=False)
    hoja6 = relationship("Hoja6Programacio", back_populates="faixes")

    # Faixa data
    tipus = Column(String(50))       # FAIXA, VORA, etc.
    fils = Column(Integer)
    pallets = Column(Integer)
    fan = Column(Numeric(8, 2))
    mm = Column(Numeric(8, 2))
    s_ha_de_passar = Column(String(10))  # SI/NO

    # Order
    ordre = Column(Integer, default=0)

    def __repr__(self):
        return f"<Faixa {self.tipus} fils={self.fils}>"


class Hoja6ProgramacioRow(Base):
    """
    Rows in the PROGRAMACIO table within Hoja 6.
    """
    __tablename__ = "hoja6_programacio_row"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to Hoja6
    hoja6_id = Column(Integer, ForeignKey("hoja6_programacio.id"), nullable=False)
    hoja6 = relationship("Hoja6Programacio", back_populates="programacio")

    # Programacio data
    tipus_faixa = Column(String(50))
    fils = Column(Integer)
    ample_mm = Column(Numeric(8, 2))
    observacio = Column(String(200))

    # Order
    ordre = Column(Integer, default=0)

    def __repr__(self):
        return f"<ProgRow {self.tipus_faixa} fils={self.fils}>"
