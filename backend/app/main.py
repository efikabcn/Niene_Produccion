from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.models.of import OrdreFabricacio
from app.models.hoja2 import Hoja2Preparacio
from app.models.hoja3 import Hoja3Revisio
from app.models.hoja4 import Hoja4Plegador
from app.models.hoja5 import Hoja5Esquema
from app.models.hoja6 import Hoja6Programacio
from app.routers import hoja2, hoja3, hoja4, hoja5, hoja6, sage

# Create tables
Base.metadata.create_all(bind=engine)

# App
app = FastAPI(
    title="Niene Producció",
    description="Sistema de gestió de producció - Sauleda / Niene",
    version="2.0.0",
)

# CORS - allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(hoja2.router)
app.include_router(hoja3.router)
app.include_router(hoja4.router)
app.include_router(hoja5.router)
app.include_router(hoja6.router)
app.include_router(sage.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": "Niene Producció",
        "version": "2.0.0",
        "sage_configured": settings.sage_configured,
    }


@app.get("/api/of-status/{of_number:path}")
def get_of_status(of_number: str, db: Session = Depends(get_db)):
    """
    Get the status of all hojas for a given OF number.
    Returns which documents exist and their current state.
    """
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == of_number
    ).first()

    if not of:
        return {
            "of_number": of_number,
            "found": False,
            "hojas": {
                "hoja2": {"exists": False, "estat": None, "id": None},
                "hoja3": {"exists": False, "estat": None, "id": None},
                "hoja4": {"exists": False, "estat": None, "id": None},
                "hoja5": {"exists": False, "estat": None, "id": None},
                "hoja6": {"exists": False, "estat": None, "id": None},
            },
        }

    # Query each hoja
    h2 = db.query(Hoja2Preparacio).filter(Hoja2Preparacio.of_id == of.id).first()
    h3 = db.query(Hoja3Revisio).filter(Hoja3Revisio.of_id == of.id).first()
    h4 = db.query(Hoja4Plegador).filter(Hoja4Plegador.of_id == of.id).first()
    h5 = db.query(Hoja5Esquema).filter(Hoja5Esquema.of_id == of.id).first()
    h6 = db.query(Hoja6Programacio).filter(Hoja6Programacio.of_id == of.id).first()

    def hoja_status(h):
        if not h:
            return {"exists": False, "estat": None, "id": None}
        return {"exists": True, "estat": h.estat, "id": h.id}

    return {
        "of_number": of_number,
        "found": True,
        "nom_article": of.nom_article or "",
        "codi_article": of.codi_article or "",
        "hojas": {
            "hoja2": hoja_status(h2),
            "hoja3": hoja_status(h3),
            "hoja4": hoja_status(h4),
            "hoja5": hoja_status(h5),
            "hoja6": hoja_status(h6),
        },
    }
