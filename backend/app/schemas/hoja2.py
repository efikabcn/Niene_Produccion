from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal


# ============================================
# Muntada
# ============================================
class MuntadaBase(BaseModel):
    color: Optional[str] = None
    partida: Optional[str] = None
    proveidor: Optional[str] = None
    n_bulto: Optional[str] = None
    conos: Optional[int] = None
    pes: Optional[Decimal] = None
    ordre: int = 0


class MuntadaCreate(MuntadaBase):
    pass


class MuntadaResponse(MuntadaBase):
    id: int

    class Config:
        from_attributes = True


# ============================================
# Hoja2
# ============================================
class Hoja2Base(BaseModel):
    data: Optional[date] = None
    hora_inici_prep: Optional[time] = None
    hora_final_prep: Optional[time] = None
    fil_traspassat_sllp: Optional[bool] = None
    nom_resp_preparacio: Optional[str] = None
    vores: Optional[bool] = None
    telomares_panama: bool = False
    penelope: bool = False
    fitxa_antiga: bool = False
    guia_montatge: bool = False
    repas_conjunt: bool = False
    cons_bones_condicions: Optional[bool] = None
    responsables_muntar: Optional[str] = None
    responsables_desmuntar: Optional[str] = None
    ordidor_revisio: Optional[str] = None
    observacions: Optional[str] = None
    estat: str = "borrador"


class Hoja2Create(Hoja2Base):
    of_number: str
    muntada: List[MuntadaCreate] = []


class Hoja2Update(Hoja2Base):
    muntada: List[MuntadaCreate] = []


class Hoja2Response(Hoja2Base):
    id: int
    of_id: int
    of_number: str = ""
    nom_article: str = ""
    codi_article: str = ""
    muntada: List[MuntadaResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# List/summary view
# ============================================
class Hoja2Summary(BaseModel):
    id: int
    of_number: str
    nom_article: str
    data: Optional[date] = None
    estat: str
    total_conos: int = 0
    colors_usats: List[str] = []
    responsables_muntar: Optional[str] = None

    class Config:
        from_attributes = True
