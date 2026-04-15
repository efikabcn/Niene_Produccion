from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.of import OrdreFabricacio
from app.models.hoja5 import Hoja5Esquema, Hoja5Filada
from app.schemas.hoja5 import (
    Hoja5Create, Hoja5Update, Hoja5Response, Hoja5Summary
)

router = APIRouter(prefix="/api/hoja5", tags=["Hoja 5 - Esquema Montada"])


@router.get("/", response_model=List[Hoja5Summary])
def list_hoja5(
    search: Optional[str] = None,
    estat: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all Hoja 5 records."""
    query = db.query(Hoja5Esquema).join(OrdreFabricacio)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (OrdreFabricacio.of_number.ilike(pattern)) |
            (OrdreFabricacio.nom_article.ilike(pattern))
        )
    if estat:
        query = query.filter(Hoja5Esquema.estat == estat)

    records = query.order_by(Hoja5Esquema.updated_at.desc()).all()

    summaries = []
    for rec in records:
        summaries.append(Hoja5Summary(
            id=rec.id,
            of_number=rec.of.of_number,
            nom_article=rec.of.nom_article or "",
            data=rec.data,
            estat=rec.estat,
            total_filades=len(rec.filades),
        ))

    return summaries


@router.get("/{hoja5_id}", response_model=Hoja5Response)
def get_hoja5(hoja5_id: int, db: Session = Depends(get_db)):
    """Get a single Hoja 5 record with filades."""
    rec = db.query(Hoja5Esquema).filter(Hoja5Esquema.id == hoja5_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Hoja 5 no trobada")

    response = Hoja5Response.model_validate(rec)
    response.of_number = rec.of.of_number
    response.nom_article = rec.of.nom_article or ""
    return response


@router.post("/", response_model=Hoja5Response)
def create_hoja5(data: Hoja5Create, db: Session = Depends(get_db)):
    """Create a new Hoja 5 record."""
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == data.of_number
    ).first()

    if not of:
        of = OrdreFabricacio(of_number=data.of_number)
        db.add(of)
        db.flush()

    existing = db.query(Hoja5Esquema).filter(
        Hoja5Esquema.of_id == of.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"La OF {data.of_number} ja te una Hoja 5"
        )

    hoja5_data = data.model_dump(exclude={"of_number", "filades"})
    hoja5 = Hoja5Esquema(of_id=of.id, **hoja5_data)
    db.add(hoja5)
    db.flush()

    for i, f in enumerate(data.filades):
        filada = Hoja5Filada(hoja5_id=hoja5.id, ordre=i, **f.model_dump())
        db.add(filada)

    db.commit()
    db.refresh(hoja5)

    response = Hoja5Response.model_validate(hoja5)
    response.of_number = of.of_number
    response.nom_article = of.nom_article or ""
    return response


@router.put("/{hoja5_id}", response_model=Hoja5Response)
def update_hoja5(hoja5_id: int, data: Hoja5Update, db: Session = Depends(get_db)):
    """Update an existing Hoja 5 record."""
    hoja5 = db.query(Hoja5Esquema).filter(Hoja5Esquema.id == hoja5_id).first()
    if not hoja5:
        raise HTTPException(status_code=404, detail="Hoja 5 no trobada")

    update_data = data.model_dump(exclude={"filades"})
    for key, value in update_data.items():
        setattr(hoja5, key, value)

    # Replace filades
    db.query(Hoja5Filada).filter(Hoja5Filada.hoja5_id == hoja5_id).delete()
    for i, f in enumerate(data.filades):
        filada = Hoja5Filada(hoja5_id=hoja5_id, ordre=i, **f.model_dump())
        db.add(filada)

    db.commit()
    db.refresh(hoja5)

    response = Hoja5Response.model_validate(hoja5)
    response.of_number = hoja5.of.of_number
    response.nom_article = hoja5.of.nom_article or ""
    return response


@router.delete("/{hoja5_id}")
def delete_hoja5(hoja5_id: int, db: Session = Depends(get_db)):
    """Delete a Hoja 5 record."""
    hoja5 = db.query(Hoja5Esquema).filter(Hoja5Esquema.id == hoja5_id).first()
    if not hoja5:
        raise HTTPException(status_code=404, detail="Hoja 5 no trobada")

    db.delete(hoja5)
    db.commit()
    return {"message": "Hoja 5 eliminada correctament"}
