from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.of import OrdreFabricacio
from app.models.hoja6 import Hoja6Programacio, Hoja6Faixa, Hoja6ProgramacioRow
from app.schemas.hoja6 import (
    Hoja6Create, Hoja6Update, Hoja6Response, Hoja6Summary
)

router = APIRouter(prefix="/api/hoja6", tags=["Hoja 6 - Programació Púa"])


@router.get("/", response_model=List[Hoja6Summary])
def list_hoja6(
    search: Optional[str] = None,
    estat: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all Hoja 6 records."""
    query = db.query(Hoja6Programacio).join(OrdreFabricacio)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (OrdreFabricacio.of_number.ilike(pattern)) |
            (OrdreFabricacio.nom_article.ilike(pattern))
        )
    if estat:
        query = query.filter(Hoja6Programacio.estat == estat)

    records = query.order_by(Hoja6Programacio.updated_at.desc()).all()

    summaries = []
    for rec in records:
        summaries.append(Hoja6Summary(
            id=rec.id,
            of_number=rec.of.of_number,
            nom_article=rec.of.nom_article or "",
            data=rec.data,
            estat=rec.estat,
            total_fils=rec.total_fils,
            total_faixes=len(rec.faixes),
        ))

    return summaries


@router.get("/{hoja6_id}", response_model=Hoja6Response)
def get_hoja6(hoja6_id: int, db: Session = Depends(get_db)):
    """Get a single Hoja 6 record with faixes and programacio rows."""
    rec = db.query(Hoja6Programacio).filter(Hoja6Programacio.id == hoja6_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Hoja 6 no trobada")

    response = Hoja6Response.model_validate(rec)
    response.of_number = rec.of.of_number
    response.nom_article_of = rec.of.nom_article or ""
    return response


@router.post("/", response_model=Hoja6Response)
def create_hoja6(data: Hoja6Create, db: Session = Depends(get_db)):
    """Create a new Hoja 6 record."""
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == data.of_number
    ).first()

    if not of:
        of = OrdreFabricacio(of_number=data.of_number)
        db.add(of)
        db.flush()

    existing = db.query(Hoja6Programacio).filter(
        Hoja6Programacio.of_id == of.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"La OF {data.of_number} ja te una Hoja 6"
        )

    hoja6_data = data.model_dump(exclude={"of_number", "faixes", "programacio"})
    hoja6 = Hoja6Programacio(of_id=of.id, **hoja6_data)
    db.add(hoja6)
    db.flush()

    # Create faixes rows
    for i, f in enumerate(data.faixes):
        faixa = Hoja6Faixa(hoja6_id=hoja6.id, ordre=i, **f.model_dump())
        db.add(faixa)

    # Create programacio rows
    for i, p in enumerate(data.programacio):
        prog = Hoja6ProgramacioRow(hoja6_id=hoja6.id, ordre=i, **p.model_dump())
        db.add(prog)

    db.commit()
    db.refresh(hoja6)

    response = Hoja6Response.model_validate(hoja6)
    response.of_number = of.of_number
    response.nom_article_of = of.nom_article or ""
    return response


@router.put("/{hoja6_id}", response_model=Hoja6Response)
def update_hoja6(hoja6_id: int, data: Hoja6Update, db: Session = Depends(get_db)):
    """Update an existing Hoja 6 record."""
    hoja6 = db.query(Hoja6Programacio).filter(Hoja6Programacio.id == hoja6_id).first()
    if not hoja6:
        raise HTTPException(status_code=404, detail="Hoja 6 no trobada")

    update_data = data.model_dump(exclude={"faixes", "programacio"})
    for key, value in update_data.items():
        setattr(hoja6, key, value)

    # Replace faixes
    db.query(Hoja6Faixa).filter(Hoja6Faixa.hoja6_id == hoja6_id).delete()
    for i, f in enumerate(data.faixes):
        faixa = Hoja6Faixa(hoja6_id=hoja6_id, ordre=i, **f.model_dump())
        db.add(faixa)

    # Replace programacio rows
    db.query(Hoja6ProgramacioRow).filter(Hoja6ProgramacioRow.hoja6_id == hoja6_id).delete()
    for i, p in enumerate(data.programacio):
        prog = Hoja6ProgramacioRow(hoja6_id=hoja6_id, ordre=i, **p.model_dump())
        db.add(prog)

    db.commit()
    db.refresh(hoja6)

    response = Hoja6Response.model_validate(hoja6)
    response.of_number = hoja6.of.of_number
    response.nom_article_of = hoja6.of.nom_article or ""
    return response


@router.delete("/{hoja6_id}")
def delete_hoja6(hoja6_id: int, db: Session = Depends(get_db)):
    """Delete a Hoja 6 record."""
    hoja6 = db.query(Hoja6Programacio).filter(Hoja6Programacio.id == hoja6_id).first()
    if not hoja6:
        raise HTTPException(status_code=404, detail="Hoja 6 no trobada")

    db.delete(hoja6)
    db.commit()
    return {"message": "Hoja 6 eliminada correctament"}
