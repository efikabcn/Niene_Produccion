from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.of import OrdreFabricacio
from app.models.hoja2 import Hoja2Preparacio, Hoja2Muntada
from app.schemas.hoja2 import (
    Hoja2Create, Hoja2Update, Hoja2Response, Hoja2Summary,
    MuntadaCreate
)

router = APIRouter(prefix="/api/hoja2", tags=["Hoja 2 - Preparació"])


@router.get("/", response_model=List[Hoja2Summary])
def list_hoja2(
    search: Optional[str] = None,
    estat: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all Hoja 2 records with optional filtering."""
    query = db.query(Hoja2Preparacio).join(OrdreFabricacio)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (OrdreFabricacio.of_number.ilike(pattern)) |
            (OrdreFabricacio.nom_article.ilike(pattern)) |
            (Hoja2Preparacio.responsables_muntar.ilike(pattern))
        )
    if estat:
        query = query.filter(Hoja2Preparacio.estat == estat)

    records = query.order_by(Hoja2Preparacio.updated_at.desc()).all()

    summaries = []
    for rec in records:
        total_conos = sum(m.conos or 0 for m in rec.muntada)
        colors_usats = list(set(m.color for m in rec.muntada if m.color))
        summaries.append(Hoja2Summary(
            id=rec.id,
            of_number=rec.of.of_number,
            nom_article=rec.of.nom_article or "",
            data=rec.data,
            estat=rec.estat,
            total_conos=total_conos,
            colors_usats=colors_usats,
            responsables_muntar=rec.responsables_muntar,
        ))

    return summaries


@router.get("/{hoja2_id}", response_model=Hoja2Response)
def get_hoja2(hoja2_id: int, db: Session = Depends(get_db)):
    """Get a single Hoja 2 record with all details."""
    rec = db.query(Hoja2Preparacio).filter(Hoja2Preparacio.id == hoja2_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Hoja 2 no trobada")

    response = Hoja2Response.model_validate(rec)
    response.of_number = rec.of.of_number
    response.nom_article = rec.of.nom_article or ""
    response.codi_article = rec.of.codi_article or ""
    return response


@router.post("/", response_model=Hoja2Response)
def create_hoja2(data: Hoja2Create, db: Session = Depends(get_db)):
    """Create a new Hoja 2 record. Creates the OF if it doesn't exist."""
    # Find or create OF
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == data.of_number
    ).first()

    if not of:
        of = OrdreFabricacio(of_number=data.of_number)
        db.add(of)
        db.flush()

    # Check if Hoja 2 already exists for this OF
    existing = db.query(Hoja2Preparacio).filter(
        Hoja2Preparacio.of_id == of.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"La OF {data.of_number} ja te una Hoja 2"
        )

    # Create Hoja 2
    hoja2_data = data.model_dump(exclude={"of_number", "muntada"})
    hoja2 = Hoja2Preparacio(of_id=of.id, **hoja2_data)
    db.add(hoja2)
    db.flush()

    # Create muntada rows
    for i, m in enumerate(data.muntada):
        muntada = Hoja2Muntada(hoja2_id=hoja2.id, ordre=i, **m.model_dump())
        db.add(muntada)

    db.commit()
    db.refresh(hoja2)

    response = Hoja2Response.model_validate(hoja2)
    response.of_number = of.of_number
    response.nom_article = of.nom_article or ""
    response.codi_article = of.codi_article or ""
    return response


@router.put("/{hoja2_id}", response_model=Hoja2Response)
def update_hoja2(hoja2_id: int, data: Hoja2Update, db: Session = Depends(get_db)):
    """Update an existing Hoja 2 record."""
    hoja2 = db.query(Hoja2Preparacio).filter(Hoja2Preparacio.id == hoja2_id).first()
    if not hoja2:
        raise HTTPException(status_code=404, detail="Hoja 2 no trobada")

    # Update fields
    update_data = data.model_dump(exclude={"muntada"})
    for key, value in update_data.items():
        setattr(hoja2, key, value)

    # Replace muntada rows
    db.query(Hoja2Muntada).filter(Hoja2Muntada.hoja2_id == hoja2_id).delete()
    for i, m in enumerate(data.muntada):
        muntada = Hoja2Muntada(hoja2_id=hoja2_id, ordre=i, **m.model_dump())
        db.add(muntada)

    db.commit()
    db.refresh(hoja2)

    response = Hoja2Response.model_validate(hoja2)
    response.of_number = hoja2.of.of_number
    response.nom_article = hoja2.of.nom_article or ""
    response.codi_article = hoja2.of.codi_article or ""
    return response


@router.delete("/{hoja2_id}")
def delete_hoja2(hoja2_id: int, db: Session = Depends(get_db)):
    """Delete a Hoja 2 record."""
    hoja2 = db.query(Hoja2Preparacio).filter(Hoja2Preparacio.id == hoja2_id).first()
    if not hoja2:
        raise HTTPException(status_code=404, detail="Hoja 2 no trobada")

    db.delete(hoja2)
    db.commit()
    return {"message": "Hoja 2 eliminada correctament"}
