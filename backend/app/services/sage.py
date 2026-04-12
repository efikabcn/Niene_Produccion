"""
SAGE ERP Connector - Read Only

This service queries the SAGE MSSQL database to retrieve
production order data (OFs), articles, providers, etc.

The actual SQL queries will be adapted once we have access
to the SAGE database schema.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Dict, List

from app.database import get_sage_engine
from app.config import settings


class SageService:
    """Read-only interface to SAGE ERP database."""

    @staticmethod
    def is_available() -> bool:
        """Check if SAGE connection is configured and reachable."""
        if not settings.sage_configured:
            return False
        try:
            engine = get_sage_engine()
            if engine is None:
                return False
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    @staticmethod
    def get_of(of_number: str) -> Optional[Dict]:
        """
        Retrieve OF data from SAGE.

        TODO: Adapt SQL query to actual SAGE schema.
        Expected to return:
        {
            "of_number": "26.0610",
            "codi_article": "2805",
            "nom_article": "WASHINGTON",
            "ample": 243.0,
            "fils_totals": 7344,
            "metres": 2000,
            ...
        }
        """
        engine = get_sage_engine()
        if engine is None:
            return None

        # PLACEHOLDER - Replace with actual SAGE query
        # query = text("""
        #     SELECT
        #         of_number, article_code, article_name,
        #         width, total_threads, meters
        #     FROM sage_of_table
        #     WHERE of_number = :of_num
        # """)
        # with engine.connect() as conn:
        #     result = conn.execute(query, {"of_num": of_number})
        #     row = result.fetchone()
        #     if row:
        #         return dict(row._mapping)

        return None

    @staticmethod
    def search_ofs(search: str = "", limit: int = 50) -> List[Dict]:
        """
        Search OFs in SAGE.

        TODO: Adapt SQL query to actual SAGE schema.
        """
        engine = get_sage_engine()
        if engine is None:
            return []

        # PLACEHOLDER - Replace with actual SAGE query
        return []

    @staticmethod
    def get_article_colors(codi_article: str) -> List[str]:
        """
        Get available colors for an article from SAGE.

        TODO: Adapt to actual SAGE schema.
        """
        engine = get_sage_engine()
        if engine is None:
            return []

        # PLACEHOLDER
        return []

    @staticmethod
    def get_providers() -> List[Dict]:
        """
        Get list of thread providers from SAGE.

        TODO: Adapt to actual SAGE schema.
        """
        engine = get_sage_engine()
        if engine is None:
            return []

        # PLACEHOLDER
        return []


sage_service = SageService()
