from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class FaixaBase(BaseModel):
    tipus: Optional[str] = None
    fils: Optional[int] = None
    pallets: Optional[int] = None
    fan: Optional[Decimal] = None
    mm: Optional[Decimal] = None
    s_ha_de_passar: Optional[str] = None
    ordre: int = 0


class FaixaCreate(FaixaBase):
    pass


class FaixaResponse(FaixaBase):
    id: int

    class Config:
        from_attributes = True


class ProgramacioRowBase(BaseModel):
    tipus_faixa: Optional[str] = None
    fils: Optional[int] = None
    ample_mm: Optional[Decimal] = None
    observacio: Optional[str] = None
    ordre: int = 0


class ProgramacioRowCreate(ProgramacioRowBase):
    pass


class ProgramacioRowResponse(ProgramacioRowBase):
    id: int

    class Config:
        from_attributes = True


class Hoja6Base(BaseModel):
    data: Optional[date] = None
    nom_article: Optional[str] = None
    total_fils: Optional[int] = None
    passat_pua_faixes: Optional[int] = None
    pua_pallcm: Optional[str] = None
    passat_fils_pall: Optional[str] = None
    total_fils_calculat: Optional[int] = None
    total_ample_mm: Optional[Decimal] = None
    ample_valones_cm: Optional[Decimal] = None
    eixamplament_mm: Optional[Decimal] = None
    observacions: Optional[str] = None
    estat: str = "borrador"


class Hoja6Create(Hoja6Base):
    of_number: str
    faixes: List[FaixaCreate] = []
    programacio: List[ProgramacioRowCreate] = []


class Hoja6Update(Hoja6Base):
    faixes: List[FaixaCreate] = []
    programacio: List[ProgramacioRowCreate] = []


class Hoja6Response(Hoja6Base):
    id: int
    of_id: int
    of_number: str = ""
    nom_article_of: str = ""
    faixes: List[FaixaResponse] = []
    programacio: List[ProgramacioRowResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Hoja6Summary(BaseModel):
    id: int
    of_number: str
    nom_article: str
    data: Optional[date] = None
    estat: str
    total_fils: Optional[int] = None
    total_faixes: int = 0

    class Config:
        from_attributes = True
