from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class FiladaBase(BaseModel):
    quantitat: Optional[int] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    total_acumulat: Optional[int] = None
    ordre: int = 0


class FiladaCreate(FiladaBase):
    pass


class FiladaResponse(FiladaBase):
    id: int

    class Config:
        from_attributes = True


class Hoja5Base(BaseModel):
    data: Optional[date] = None
    observacions: Optional[str] = None
    estat: str = "borrador"


class Hoja5Create(Hoja5Base):
    of_number: str
    filades: List[FiladaCreate] = []


class Hoja5Update(Hoja5Base):
    filades: List[FiladaCreate] = []


class Hoja5Response(Hoja5Base):
    id: int
    of_id: int
    of_number: str = ""
    nom_article: str = ""
    filades: List[FiladaResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Hoja5Summary(BaseModel):
    id: int
    of_number: str
    nom_article: str
    data: Optional[date] = None
    estat: str
    total_filades: int = 0

    class Config:
        from_attributes = True
