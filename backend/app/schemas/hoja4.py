from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


class Hoja4Base(BaseModel):
    data: Optional[date] = None
    hora: Optional[time] = None
    num_teler: Optional[int] = None
    num_ferro_plegador: Optional[str] = None
    color_plegador: Optional[str] = None
    verificar_colors: Optional[bool] = None
    manquen_cargols: bool = False
    cargols_reposats: bool = False
    visualitzacio_optim: bool = False
    posicio_valones: Optional[str] = None
    mida_valones_baix: Optional[Decimal] = None
    mida_valones_dalt: Optional[Decimal] = None
    confirmat_mgtz: bool = False
    confirmat_ordidor: bool = False
    signatura_responsable: Optional[str] = None
    signatura_ordidor: Optional[str] = None
    observacions: Optional[str] = None
    estat: str = "borrador"


class Hoja4Create(Hoja4Base):
    of_number: str


class Hoja4Update(Hoja4Base):
    pass


class Hoja4Response(Hoja4Base):
    id: int
    of_id: int
    of_number: str = ""
    nom_article: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Hoja4Summary(BaseModel):
    id: int
    of_number: str
    nom_article: str
    data: Optional[date] = None
    estat: str
    num_teler: Optional[int] = None

    class Config:
        from_attributes = True
