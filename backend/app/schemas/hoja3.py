from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


class Hoja3Base(BaseModel):
    data: Optional[date] = None
    hora_inici_ordir: Optional[time] = None
    hora_final_ordir: Optional[time] = None
    hora_inici_plegar: Optional[time] = None
    hora_final_plegar: Optional[time] = None
    tensio_ordit: Optional[Decimal] = None
    tensio_plegat: Optional[Decimal] = None
    producte_no_conforme: Optional[bool] = None
    quadra_amb_fulla: Optional[bool] = None
    responsable_1_nom: Optional[str] = None
    responsable_1_faixes: Optional[int] = None
    responsable_2_nom: Optional[str] = None
    responsable_2_faixes: Optional[int] = None
    fileta_neta: bool = False
    avanc_automatic: bool = False
    avanc_valor: Optional[str] = None
    fils_creuats: bool = False
    revisat_passat_pua: bool = False
    coincidir_mostra: bool = False
    mida_pua_igual: bool = False
    encarament_pua: bool = False
    primer_fil_faixa: bool = False
    observacions: Optional[str] = None
    estat: str = "borrador"


class Hoja3Create(Hoja3Base):
    of_number: str


class Hoja3Update(Hoja3Base):
    pass


class Hoja3Response(Hoja3Base):
    id: int
    of_id: int
    of_number: str = ""
    nom_article: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Hoja3Summary(BaseModel):
    id: int
    of_number: str
    nom_article: str
    data: Optional[date] = None
    estat: str
    responsable_1_nom: Optional[str] = None

    class Config:
        from_attributes = True
