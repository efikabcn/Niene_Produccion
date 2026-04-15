from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.of import OrdreFabricacio
from app.models.hoja3 import Hoja3Revisio
from app.schemas.hoja3 import (
    Hoja3Create, Hoja3Update, Hoja3Response, Hoja3Summary
)

router = APIRouter(prefix="/api/hoja3", tags=["Hoja 3 - Revisió Ordida"])


@router.get("/", response_model=List[Hoja3Summary])
def list_hoja3(
    search: Optional[str] = None,
    estat: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all Hoja 3 records."""
    query = db.query(Hoja3Revisio).join(OrdreFabricacio)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (OrdreFabricacio.of_number.ilike(pattern)) |
            (OrdreFabricacio.nom_article.ilike(pattern)) |
            (Hoja3Revisio.responsable_1_nom.ilike(pattern))
        )
    if estat:
        query = query.filter(Hoja3Revisio.estat == estat)

    records = query.order_by(Hoja3Revisio.updated_at.desc()).all()

    summaries = []
    for rec in records:
        summaries.append(Hoja3Summary(
            id=rec.id,
            of_number=rec.of.of_number,
            nom_article=rec.of.nom_article or "",
            data=rec.data,
            estat=rec.estat,
            responsable_1_nom=rec.responsable_1_nom,
        ))

    return summaries


@router.get("/{hoja3_id}", response_model=Hoja3Response)
def get_hoja3(hoja3_id: int, db: Session = Depends(get_db)):
    """Get a single Hoja 3 record."""
    rec = db.query(Hoja3Revisio).filter(Hoja3Revisio.id == hoja3_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Hoja 3 no trobada")

    response = Hoja3Response.model_validate(rec)
    response.of_number = rec.of.of_number
    response.nom_article = rec.of.nom_article or ""
    return response


@router.post("/", response_model=Hoja3Response)
def create_hoja3(data: Hoja3Create, db: Session = Depends(get_db)):
    """Create a new Hoja 3 record."""
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == data.of_number
    ).first()

    if not of:
        of = OrdreFabricacio(of_number=data.of_number)
        db.add(of)
        db.flush()

    existing = db.query(Hoja3Revisio).filter(
        Hoja3Revisio.of_id == of.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"La OF {data.of_number} ja te una Hoja 3"
        )

    hoja3_data = data.model_dump(exclude={"of_number"})
    hoja3 = Hoja3Revisio(of_id=of.id, **hoja3_data)
    db.add(hoja3)
    db.commit()
    db.refresh(hoja3)

    response = Hoja3Response.model_validate(hoja3)
    response.of_number = of.of_number
    response.nom_article = of.nom_article or ""
    return response


@router.put("/{hoja3_id}", response_model=Hoja3Response)
def update_hoja3(hoja3_id: int, data: Hoja3Update, db: Session = Depends(get_db)):
    """Update an existing Hoja 3 record."""
    hoja3 = db.query(Hoja3Revisio).filter(Hoja3Revisio.id == hoja3_id).first()
    if not hoja3:
        raise HTTPException(status_code=404, detail="Hoja 3 no trobada")

    update_data = data.model_dump()
    for key, value in update_data.items():
        setattr(hoja3, key, value)

    db.commit()
    db.refresh(hoja3)

    response = Hoja3Response.model_validate(hoja3)
    response.of_number = hoja3.of.of_number
    response.nom_article = hoja3.of.nom_article or ""
    return response


@router.delete("/{hoja3_id}")
def delete_hoja3(hoja3_id: int, db: Session = Depends(get_db)):
    """Delete a Hoja 3 record."""
    hoja3 = db.query(Hoja3Revisio).filter(Hoja3Revisio.id == hoja3_id).first()
    if not hoja3:
        raise HTTPException(status_code=404, detail="Hoja 3 no trobada")

    db.delete(hoja3)
    db.commit()
    return {"message": "Hoja 3 eliminada correctament"}
