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


@router.get("/of/{of_number:path}")
def get_sage_of(of_number: str):
    """
    Get OF data from SAGE.

    of_number can be full (NO/22.1257) or short (22.1257).
    """
    if not sage_service.is_available():
        raise HTTPException(status_code=503, detail="SAGE no disponible")

    data = sage_service.get_of(of_number)
    if not data:
        raise HTTPException(status_code=404, detail=f"OF {of_number} no trobada a SAGE")
    return data


@router.get("/ofs")
def search_sage_ofs(
    search: Optional[str] = "",
    limit: int = 50,
    estado: Optional[int] = None,
    ejercicio: Optional[int] = None,
    serie: Optional[str] = None,
):
    """
    Search OFs in SAGE.

    Params:
    - search: text to search in OF number, article code, or description
    - estado: filter by status (0=planned, 1=launched, 2=closed)
    - ejercicio: filter by year
    - serie: filter by series (NO, XM, TT...)
    - limit: max results (default 50)
    """
    if not sage_service.is_available():
        return {"ofs": [], "sage_available": False}

    ofs = sage_service.search_ofs(
        search=search,
        limit=limit,
        estado=estado,
        ejercicio=ejercicio,
        serie=serie,
    )
    return {"ofs": ofs, "sage_available": True, "total": len(ofs)}


@router.get("/of/{of_number:path}/components")
def get_of_components(of_number: str):
    """Get material components (threads/yarns) for an OF."""
    if not sage_service.is_available():
        raise HTTPException(status_code=503, detail="SAGE no disponible")

    components = sage_service.get_of_components(of_number)
    return {"components": components, "total": len(components)}


@router.get("/article/{codi_article}")
def get_article(codi_article: str):
    """Get article details from SAGE."""
    if not sage_service.is_available():
        raise HTTPException(status_code=503, detail="SAGE no disponible")

    data = sage_service.get_article(codi_article)
    if not data:
        raise HTTPException(status_code=404, detail=f"Article {codi_article} no trobat")
    return data


@router.get("/providers")
def get_providers():
    """Get list of thread/yarn providers."""
    if not sage_service.is_available():
        return {"providers": [], "sage_available": False}

    providers = sage_service.get_providers()
    return {"providers": providers, "sage_available": True, "total": len(providers)}


@router.get("/recipe/{recepta_codi}")
def get_recipe(recepta_codi: str):
    """Get recipe details."""
    if not sage_service.is_available():
        raise HTTPException(status_code=503, detail="SAGE no disponible")

    data = sage_service.get_recipe(recepta_codi)
    if not data:
        raise HTTPException(status_code=404, detail=f"Recepta {recepta_codi} no trobada")
    return data
