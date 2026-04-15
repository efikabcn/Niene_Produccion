from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
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
