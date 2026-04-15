"""
PDF download endpoints for all hojas.
Each endpoint streams the generated PDF as a downloadable file.
"""
import io
import zipfile
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.of import OrdreFabricacio
from app.models.hoja2 import Hoja2Preparacio
from app.models.hoja3 import Hoja3Revisio
from app.models.hoja4 import Hoja4Plegador
from app.models.hoja5 import Hoja5Esquema
from app.models.hoja6 import Hoja6Programacio
from app.services.pdf_generator import (
    generate_hoja2_pdf, generate_hoja3_pdf, generate_hoja4_pdf,
    generate_hoja5_pdf, generate_hoja6_pdf,
)

router = APIRouter(prefix="/api/pdf", tags=["PDF Generation"])

# Map hoja number to (model, generator, document name)
HOJA_MAP = {
    2: (Hoja2Preparacio, generate_hoja2_pdf, "Preparacio_i_Muntatge"),
    3: (Hoja3Revisio, generate_hoja3_pdf, "Revisio_Ordida"),
    4: (Hoja4Plegador, generate_hoja4_pdf, "Collocacio_Plegador"),
    5: (Hoja5Esquema, generate_hoja5_pdf, "Esquema_Montada"),
    6: (Hoja6Programacio, generate_hoja6_pdf, "Programacio_Pua"),
}


def _safe_filename(of_number):
    """Sanitise OF number for use in filenames."""
    return re.sub(r'[^\w\-.]', '_', of_number)


def _pdf_response(pdf_bytes, filename):
    """Return a StreamingResponse for a PDF file."""
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ----- Individual hoja endpoints -----

@router.get("/hoja2/{hoja_id}")
def download_hoja2_pdf(hoja_id: int, db: Session = Depends(get_db)):
    """Download PDF for Hoja 2."""
    hoja = db.query(Hoja2Preparacio).filter(Hoja2Preparacio.id == hoja_id).first()
    if not hoja:
        raise HTTPException(status_code=404, detail="Hoja 2 no trobada")
    pdf = generate_hoja2_pdf(hoja, hoja.of)
    fn = _safe_filename(hoja.of.of_number) + "_Preparacio_i_Muntatge.pdf"
    return _pdf_response(pdf, fn)


@router.get("/hoja3/{hoja_id}")
def download_hoja3_pdf(hoja_id: int, db: Session = Depends(get_db)):
    """Download PDF for Hoja 3."""
    hoja = db.query(Hoja3Revisio).filter(Hoja3Revisio.id == hoja_id).first()
    if not hoja:
        raise HTTPException(status_code=404, detail="Hoja 3 no trobada")
    pdf = generate_hoja3_pdf(hoja, hoja.of)
    fn = _safe_filename(hoja.of.of_number) + "_Revisio_Ordida.pdf"
    return _pdf_response(pdf, fn)


@router.get("/hoja4/{hoja_id}")
def download_hoja4_pdf(hoja_id: int, db: Session = Depends(get_db)):
    """Download PDF for Hoja 4."""
    hoja = db.query(Hoja4Plegador).filter(Hoja4Plegador.id == hoja_id).first()
    if not hoja:
        raise HTTPException(status_code=404, detail="Hoja 4 no trobada")
    pdf = generate_hoja4_pdf(hoja, hoja.of)
    fn = _safe_filename(hoja.of.of_number) + "_Collocacio_Plegador.pdf"
    return _pdf_response(pdf, fn)


@router.get("/hoja5/{hoja_id}")
def download_hoja5_pdf(hoja_id: int, db: Session = Depends(get_db)):
    """Download PDF for Hoja 5."""
    hoja = db.query(Hoja5Esquema).filter(Hoja5Esquema.id == hoja_id).first()
    if not hoja:
        raise HTTPException(status_code=404, detail="Hoja 5 no trobada")
    pdf = generate_hoja5_pdf(hoja, hoja.of)
    fn = _safe_filename(hoja.of.of_number) + "_Esquema_Montada.pdf"
    return _pdf_response(pdf, fn)


@router.get("/hoja6/{hoja_id}")
def download_hoja6_pdf(hoja_id: int, db: Session = Depends(get_db)):
    """Download PDF for Hoja 6."""
    hoja = db.query(Hoja6Programacio).filter(Hoja6Programacio.id == hoja_id).first()
    if not hoja:
        raise HTTPException(status_code=404, detail="Hoja 6 no trobada")
    pdf = generate_hoja6_pdf(hoja, hoja.of)
    fn = _safe_filename(hoja.of.of_number) + "_Programacio_Pua.pdf"
    return _pdf_response(pdf, fn)


# ----- Download all PDFs for an OF as ZIP -----

@router.get("/of/{of_number:path}")
def download_all_pdfs(of_number: str, db: Session = Depends(get_db)):
    """Download a ZIP with all existing PDFs for a given OF number."""
    of = db.query(OrdreFabricacio).filter(
        OrdreFabricacio.of_number == of_number
    ).first()

    if not of:
        raise HTTPException(status_code=404, detail="OF no trobada")

    safe_of = _safe_filename(of_number)

    # Collect PDFs
    pdfs = []

    h2 = db.query(Hoja2Preparacio).filter(Hoja2Preparacio.of_id == of.id).first()
    if h2:
        pdfs.append((safe_of + "_Preparacio_i_Muntatge.pdf", generate_hoja2_pdf(h2, of)))

    h3 = db.query(Hoja3Revisio).filter(Hoja3Revisio.of_id == of.id).first()
    if h3:
        pdfs.append((safe_of + "_Revisio_Ordida.pdf", generate_hoja3_pdf(h3, of)))

    h4 = db.query(Hoja4Plegador).filter(Hoja4Plegador.of_id == of.id).first()
    if h4:
        pdfs.append((safe_of + "_Collocacio_Plegador.pdf", generate_hoja4_pdf(h4, of)))

    h5 = db.query(Hoja5Esquema).filter(Hoja5Esquema.of_id == of.id).first()
    if h5:
        pdfs.append((safe_of + "_Esquema_Montada.pdf", generate_hoja5_pdf(h5, of)))

    h6 = db.query(Hoja6Programacio).filter(Hoja6Programacio.of_id == of.id).first()
    if h6:
        pdfs.append((safe_of + "_Programacio_Pua.pdf", generate_hoja6_pdf(h6, of)))

    if not pdfs:
        raise HTTPException(status_code=404, detail="No hi ha documents per aquesta OF")

    # Build ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, pdf_bytes in pdfs:
            zf.writestr(filename, pdf_bytes)

    zip_buffer.seek(0)
    zip_filename = safe_of + "_Documents.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
    )
