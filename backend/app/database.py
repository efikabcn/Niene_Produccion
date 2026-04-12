from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# ============================================
# PostgreSQL - Our database (read/write)
# ============================================
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# SAGE MSSQL - Read only connection
# ============================================
_sage_engine = None


def get_sage_engine():
    """Lazy initialization of SAGE connection."""
    global _sage_engine
    if _sage_engine is None and settings.sage_configured:
        sage_url = (
            f"mssql+pymssql://{settings.sage_db_user}:{settings.sage_db_password}"
            f"@{settings.sage_db_host}:{settings.sage_db_port}/{settings.sage_db_name}"
        )
        _sage_engine = create_engine(sage_url, pool_pre_ping=True)
    return _sage_engine


def get_sage_db():
    """Dependency: get a SAGE read-only session."""
    sage_engine = get_sage_engine()
    if sage_engine is None:
        yield None
        return
    SageSession = sessionmaker(bind=sage_engine)
    db = SageSession()
    try:
        yield db
    finally:
        db.close()
