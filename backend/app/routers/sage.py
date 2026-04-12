from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict

from app.services.sage import sage_service

router = APIRouter(prefix="/api/sage", tags=["SAGE ERP"])


@router.get("/status")
def sage_status():
    """Check if SAGE connection is available."""
    available = sage_service.is_available()
    return {
        "connected": available,
        "message": "SAGE connectat" if available else "SAGE no configurat o no accessible"
    }


@router.get("/of/{of_number}")
def get_sage_of(of_number: str):
    """Get OF data from SAGE."""
    if not sage_service.is_available():
        raise HTTPException(status_code=503, detail="SAGE no disponible")

    data = sage_service.get_of(of_number)
    if not data:
        raise HTTPException(status_code=404, detail=f"OF {of_number} no trobada a SAGE")
    return data


@router.get("/ofs")
def search_sage_ofs(search: Optional[str] = "", limit: int = 50):
    """Search OFs in SAGE."""
    if not sage_service.is_available():
        return {"ofs": [], "sage_available": False}

    return {"ofs": sage_service.search_ofs(search, limit), "sage_available": True}
