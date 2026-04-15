from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.of import OrdreFabricacio
from app.models.hoja4 import Hoja4Plegador
from app.schemas.hoja4 import (
    Hoja4Create, Hoja4Update, Hoja4Response, Hoja4Summary
)

router = APIRouter(prefix="/api/hoja4", tags=["Hoja 4 - Col·locació Plegador"])


@router.get("/", response_model=List[Hoja4Summary])
def list_hoja4(
    search: Optional[str] = None,
    estat: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all Hoja 4 records."""
    query = db.query(Hoja4Plegador).join(OrdreFabricacio)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (OrdreFabricacio.of_number.ilike(pattern)) |
            (OrdreFabricacio.nom_article.ilike(pattern))
        )
    if estat:
        query = query.filter(Hoja4Plegador.estat == estat)

    records = query.order_by(Hoja4Plegador.updated_at.desc()).all()

    summaries = []
    for rec in records:
        summaries.append(Hoja4Summary(
            id=rec.id,
            of_number=rec.of.of_number,
            nom_article=rec.of.nom_article or "",
            data=rec.data,
            estat=rec.estat,
            num_teler=rec.num_teler,
        ))

    return summaries


@router.get("/{hoja4_id}", response_model=Hoja4Response)
def get_hoja4(hoja4_id: int, db: Session = Depends(get_db)):
    """Get a single Hoja 4 record."""
    rec = db.query(Hoja4Plegador).filter(Hoja4Plegador.id == hoja4_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Hoja 4 no trobada")

    response = Hoja4Response.model_validate(rec)
    response.of_number = rec.of.of_number
    response.nom_article = rec.of.nom_article or ""
    return response


@router.post("/", response_model=Hoja4Response)
def create_hoja4(data: Hoja4Create, db: Session = Depends(get_db)):
    """Create a new Hoja 4 record."""
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == data.of_number
    ).first()

    if not of:
        of = OrdreFabricacio(of_number=data.of_number)
        db.add(of)
        db.flush()

    existing = db.query(Hoja4Plegador).filter(
        Hoja4Plegador.of_id == of.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"La OF {data.of_number} ja te una Hoja 4"
        )

    hoja4_data = data.model_dump(exclude={"of_number"})
    hoja4 = Hoja4Plegador(of_id=of.id, **hoja4_data)
    db.add(hoja4)
    db.commit()
    db.refresh(hoja4)

    response = Hoja4Response.model_validate(hoja4)
    response.of_number = of.of_number
    response.nom_article = of.nom_article or ""
    return response


@router.put("/{hoja4_id}", response_model=Hoja4Response)
def update_hoja4(hoja4_id: int, data: Hoja4Update, db: Session = Depends(get_db)):
    """Update an existing Hoja 4 record."""
    hoja4 = db.query(Hoja4Plegador).filter(Hoja4Plegador.id == hoja4_id).first()
    if not hoja4:
        raise HTTPException(status_code=404, detail="Hoja 4 no trobada")

    update_data = data.model_dump()
    for key, value in update_data.items():
        setattr(hoja4, key, value)

    db.commit()
    db.refresh(hoja4)

    response = Hoja4Response.model_validate(hoja4)
    response.of_number = hoja4.of.of_number
    response.nom_article = hoja4.of.nom_article or ""
    return response


@router.delete("/{hoja4_id}")
def delete_hoja4(hoja4_id: int, db: Session = Depends(get_db)):
    """Delete a Hoja 4 record."""
    hoja4 = db.query(Hoja4Plegador).filter(Hoja4Plegador.id == hoja4_id).first()
    if not hoja4:
        raise HTTPException(status_code=404, detail="Hoja 4 no trobada")

    db.delete(hoja4)
    db.commit()
    return {"message": "Hoja 4 eliminada correctament"}
