"""
SAGE ERP Connector - Read Only

This service queries the SAGE MSSQL database to retrieve
production order data (OFs), articles, providers, etc.

Main table: dbo.OrdenesFabricacion
Key: CO_OrdenFabricacion (format: "NO/26.0610" or "XM/22.0008")
CodigoEmpresa: 1 = Olot (OLO), 20 = Xàtiva (XM)
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
import logging

from app.database import get_sage_engine
from app.config import settings

logger = logging.getLogger(__name__)

# ============================================
# SAGE Field -> App Field Mapping
# ============================================
# dbo.OrdenesFabricacion fields:
#
# CO_OrdenFabricacion    -> of_number (e.g. "NO/22.1257")
# CodigoArticulo         -> codi_article (e.g. "3146")
# DescripcionArticulo    -> nom_article (e.g. "LM LIGHT BRINZIO (180 cm) 180")
# CO_Ancho               -> ample (width, e.g. "180")
# CO_HilosTotales        -> fils_totals (total threads, e.g. 4560)
# UnidadesAFabricar      -> metres (meters to produce, e.g. 2240)
# CO_AnchoPlegador       -> ample_plegador_mm (beam width mm, e.g. 1941)
# CO_Fajas               -> num_faixes (number of bands, e.g. 16)
# CO_PlegadorTeler       -> teler_num (loom number, e.g. 7)
#
# Additional production params:
# CO_Pua                 -> pua (reed, e.g. 8.0)
# CO_AnchoPua            -> ample_pua (reed width, e.g. 190.0)
# CO_AnchoAcabado        -> ample_acabat (finished width, e.g. 180)
# CO_AnchoTejido         -> ample_teixit (woven width, e.g. 185.0)
# CO_Pasadas             -> passades (picks/passes, e.g. 16.0)
# CO_Ligamiento          -> lligament (weave pattern)
# CO_HilosPua            -> fils_pua (threads per reed dent, e.g. "3")
# CO_HilosFaja           -> fils_faixa (threads per band)
# CO_AnchoFaja           -> ample_faixa (band width)
# CO_Fajas2              -> num_faixes_2 (second band set)
# CO_HilosFaja2          -> fils_faixa_2
# CO_AnchoFaja2          -> ample_faixa_2
# CO_PresionUrdidor      -> pressio_ordidor (warper pressure)
# CO_VelocidadUrdidor    -> velocitat_ordidor (warper speed)
# CO_PresionPrensa       -> pressio_premsa (press pressure)
# CO_VelocidadPlegado    -> velocitat_plegat (folding speed)
# CO_VelocidadTelar      -> velocitat_teler (loom speed)
# CO_PresionPlegado      -> pressio_plegat (folding pressure)
# CO_DensAcaOrdidor      -> densitat_ordidor (warper density)
# CO_DobleAmple          -> doble_ample (double width)
# CO_UnidadesaUrdir      -> metres_urdir (meters to warp)
# CO_MetrosPiezaTelar    -> metres_peca_teler (meters per piece on loom)
# CO_Plegador            -> plegador (beam number)
# CO_Urdidor             -> ordidor (warper number)
# CO_6Pintes             -> sis_pintes (6-comb flag)
# CO_Rcpt_Codi           -> recepta_codi (recipe code)
# CO_Tipo                -> tipus (type)
# CO_Rollos              -> rollos (rolls)
# CO_LugarTejido         -> lloc_teixit (weaving location)
# CO_LugarUrdido         -> lloc_urdit (warping location)
#
# Status / dates:
# EstadoOF               -> estat_sage (0=planned, 1=launched, 2=closed)
# FechaCreacion          -> data_creacio
# FechaInicioPrevista    -> data_inici_prevista
# FechaFinalPrevista     -> data_final_prevista
# FechaInicioReal        -> data_inici_real
# FechaFinalReal         -> data_final_real
# CO_OperacionActual     -> operacio_actual
# CO_UnidadesUrdidas     -> metres_urdits
# CO_UnidadesTejidas     -> metres_teixits
# CO_UnidadesAcabadas    -> metres_acabats
#
# Observations:
# CO_ObservacionesFabricacion -> observacions_fabricacio
# CO_ObsAcabado              -> observacions_acabat
# CO_ObsTelares              -> observacions_telers
# CO_ObsUrdido               -> observacions_urdit
# CO_ObsOtros                -> observacions_altres
#
# Series: SerieFabricacion (NO=Olot, XM=Xàtiva, TT=test, NT=new)
# ============================================


# Base query selecting all relevant fields from OrdenesFabricacion
_OF_SELECT = """
    SELECT
        of_.CO_OrdenFabricacion     AS of_number,
        of_.CodigoArticulo          AS codi_article,
        of_.DescripcionArticulo     AS nom_article,
        of_.CO_Ancho                AS ample,
        of_.CO_HilosTotales         AS fils_totals,
        of_.UnidadesAFabricar       AS metres,
        of_.CO_AnchoPlegador        AS ample_plegador_mm,
        of_.CO_Fajas                AS num_faixes,
        of_.CO_PlegadorTeler        AS teler_num,
        of_.Formula                 AS formula,

        -- Production parameters
        of_.CO_Pua                  AS pua,
        of_.CO_AnchoPua             AS ample_pua,
        of_.CO_AnchoAcabado         AS ample_acabat,
        of_.CO_AnchoTejido          AS ample_teixit,
        of_.CO_Pasadas              AS passades,
        of_.CO_Ligamiento           AS lligament,
        of_.CO_HilosPua             AS fils_pua,
        of_.CO_HilosFaja            AS fils_faixa,
        of_.CO_AnchoFaja            AS ample_faixa,
        of_.CO_Fajas2               AS num_faixes_2,
        of_.CO_HilosFaja2           AS fils_faixa_2,
        of_.CO_AnchoFaja2           AS ample_faixa_2,
        of_.CO_PresionUrdidor       AS pressio_ordidor,
        of_.CO_VelocidadUrdidor     AS velocitat_ordidor,
        of_.CO_PresionPrensa        AS pressio_premsa,
        of_.CO_VelocidadPlegado     AS velocitat_plegat,
        of_.CO_VelocidadTelar       AS velocitat_teler,
        of_.CO_PresionPlegado       AS pressio_plegat,
        of_.CO_DensAcaOrdidor       AS densitat_ordidor,
        of_.CO_DobleAmple           AS doble_ample,
        of_.CO_UnidadesaUrdir       AS metres_urdir,
        of_.CO_MetrosPiezaTelar     AS metres_peca_teler,
        of_.CO_Plegador             AS plegador,
        of_.CO_Urdidor              AS ordidor,
        of_.CO_6Pintes              AS sis_pintes,
        of_.CO_Rcpt_Codi            AS recepta_codi,
        of_.CO_Tipo                 AS tipus,
        of_.CO_Rollos               AS rollos,
        of_.CO_LugarTejido          AS lloc_teixit,
        of_.CO_LugarUrdido          AS lloc_urdit,
        of_.CO_AnchoAcabadoTxt      AS ample_acabat_txt,
        of_.CO_CodigoImpresion      AS codi_impressio,
        of_.CO_Partida              AS partida,

        -- Status and dates
        of_.EstadoOF                AS estat_sage,
        of_.FechaCreacion           AS data_creacio,
        of_.FechaInicioPrevista     AS data_inici_prevista,
        of_.FechaFinalPrevista      AS data_final_prevista,
        of_.FechaInicioReal         AS data_inici_real,
        of_.FechaFinalReal          AS data_final_real,
        of_.CO_OperacionActual      AS operacio_actual,
        of_.CO_UnidadesUrdidas      AS metres_urdits,
        of_.CO_UnidadesTejidas      AS metres_teixits,
        of_.CO_UnidadesAcabadas     AS metres_acabats,
        of_.CO_UnidadesAFabricar    AS metres_a_fabricar,
        of_.UnidadesFabricadas      AS metres_fabricats,

        -- Observations
        of_.CO_ObservacionesFabricacion AS observacions_fabricacio,
        of_.CO_ObsAcabado           AS observacions_acabat,
        of_.CO_ObsTelares           AS observacions_telers,
        of_.CO_ObsUrdido            AS observacions_urdit,
        of_.CO_ObsOtros             AS observacions_altres,
        of_.Observaciones           AS observacions_generals,

        -- Reference
        of_.EjercicioFabricacion    AS exercici,
        of_.SerieFabricacion        AS serie,
        of_.NumeroFabricacion       AS numero,
        of_.Delegacion              AS delegacio,
        of_.SuPedido                AS su_pedido

    FROM dbo.OrdenesFabricacion of_
"""


def _row_to_dict(row) -> Dict:
    """Convert a SQLAlchemy row to a clean dictionary."""
    d = dict(row._mapping)
    # Clean up None-like values
    for key, val in d.items():
        if val is not None:
            # Convert Decimal zero-ish values
            if hasattr(val, 'is_zero') and val.is_zero():
                d[key] = 0
            # Strip whitespace from strings
            elif isinstance(val, str):
                d[key] = val.strip()
    return d


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
        except Exception as e:
            logger.warning(f"SAGE connection check failed: {e}")
            return False

    @staticmethod
    def get_of(of_number: str) -> Optional[Dict]:
        """
        Retrieve OF data from SAGE by CO_OrdenFabricacion.

        The of_number can be:
        - Full format: "NO/22.1257"
        - Short format: "22.1257" (will search with LIKE)
        """
        engine = get_sage_engine()
        if engine is None:
            return None

        try:
            with engine.connect() as conn:
                # Try exact match first
                query = text(_OF_SELECT + """
                    WHERE of_.CO_OrdenFabricacion = :of_num
                """)
                result = conn.execute(query, {"of_num": of_number})
                row = result.fetchone()

                # If not found, try LIKE search (user may omit prefix)
                if row is None:
                    query = text(_OF_SELECT + """
                        WHERE of_.CO_OrdenFabricacion LIKE :of_pattern
                        ORDER BY of_.FechaCreacion DESC
                    """)
                    result = conn.execute(query, {"of_pattern": f"%{of_number}%"})
                    row = result.fetchone()

                if row:
                    return _row_to_dict(row)

        except Exception as e:
            logger.error(f"Error querying SAGE OF {of_number}: {e}")

        return None

    @staticmethod
    def search_ofs(
        search: str = "",
        limit: int = 50,
        estado: Optional[int] = None,
        ejercicio: Optional[int] = None,
        serie: Optional[str] = None,
    ) -> List[Dict]:
        """
        Search OFs in SAGE.

        Filters:
        - search: free text search on OF number, article code, or description
        - estado: 0=planned, 1=launched, 2=closed
        - ejercicio: year (e.g. 2026)
        - serie: series code (e.g. "NO", "XM")
        """
        engine = get_sage_engine()
        if engine is None:
            return []

        try:
            conditions = ["of_.CodigoEmpresa > 0"]  # Exclude dummy row 0
            params = {"limit": limit}

            if search:
                conditions.append("""(
                    of_.CO_OrdenFabricacion LIKE :search
                    OR of_.CodigoArticulo LIKE :search
                    OR of_.DescripcionArticulo LIKE :search
                )""")
                params["search"] = f"%{search}%"

            if estado is not None:
                conditions.append("of_.EstadoOF = :estado")
                params["estado"] = estado

            if ejercicio is not None:
                conditions.append("of_.EjercicioFabricacion = :ejercicio")
                params["ejercicio"] = ejercicio

            if serie is not None:
                conditions.append("of_.SerieFabricacion = :serie")
                params["serie"] = serie

            where = " AND ".join(conditions)
            query_str = _OF_SELECT + f"""
                WHERE {where}
                ORDER BY of_.FechaCreacion DESC
                OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY
            """

            with engine.connect() as conn:
                result = conn.execute(text(query_str), params)
                return [_row_to_dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error searching SAGE OFs: {e}")

        return []

    @staticmethod
    def get_of_components(of_number: str) -> List[Dict]:
        """
        Get the material components (threads/yarns) for an OF
        from the Estructura_Fabricacion table.
        """
        engine = get_sage_engine()
        if engine is None:
            return []

        try:
            # First get the OF's EjercicioTrabajo and NumeroTrabajo
            with engine.connect() as conn:
                # Get OF identifier
                of_query = text("""
                    SELECT EjercicioFabricacion, NumeroFabricacion, SerieFabricacion
                    FROM dbo.OrdenesFabricacion
                    WHERE CO_OrdenFabricacion = :of_num
                """)
                of_row = conn.execute(of_query, {"of_num": of_number}).fetchone()
                if not of_row:
                    return []

                # Get components from Estructura_Fabricacion
                comp_query = text("""
                    SELECT
                        ef.CodigoArticulo       AS codi_article,
                        a.DescripcionArticulo   AS nom_article,
                        ef.Colores_             AS color_code,
                        ef.CodigoColor_         AS color,
                        ef.UnidadesAFabricar2   AS unitats,
                        ef.UnidadesBrutas2      AS unitats_brutes,
                        ef.Orden                AS ordre
                    FROM dbo.Estructura_Fabricacion ef
                    LEFT JOIN dbo.Articulos a
                        ON a.CodigoEmpresa = ef.CodigoEmpresa
                        AND a.CodigoArticulo = ef.CodigoArticulo
                    WHERE ef.CodigoEmpresa > 0
                        AND ef.EjercicioTrabajo = :ejercicio
                        AND ef.NumeroTrabajo = :numero
                    ORDER BY ef.Orden
                """)
                result = conn.execute(comp_query, {
                    "ejercicio": of_row[0],
                    "numero": of_row[1],
                })
                return [_row_to_dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting OF components: {e}")

        return []

    @staticmethod
    def get_article(codi_article: str) -> Optional[Dict]:
        """Get article details from the Articulos table."""
        engine = get_sage_engine()
        if engine is None:
            return None

        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT
                        a.CodigoArticulo        AS codi_article,
                        a.DescripcionArticulo   AS nom_article,
                        a.PesoNetoUnitario_     AS pes_net
                    FROM dbo.Articulos a
                    WHERE a.CodigoArticulo = :codi
                        AND a.CodigoEmpresa > 0
                """)
                result = conn.execute(query, {"codi": codi_article})
                row = result.fetchone()
                if row:
                    return _row_to_dict(row)
        except Exception as e:
            logger.error(f"Error getting article {codi_article}: {e}")

        return None

    @staticmethod
    def get_providers() -> List[Dict]:
        """Get list of thread/yarn providers from SAGE."""
        engine = get_sage_engine()
        if engine is None:
            return []

        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT DISTINCT
                        p.CodigoProveedor       AS codi_proveidor,
                        p.RazonSocial           AS nom_proveidor
                    FROM dbo.Proveedores p
                    WHERE p.CodigoEmpresa > 0
                        AND p.RazonSocial IS NOT NULL
                        AND p.RazonSocial != ''
                    ORDER BY p.RazonSocial
                """)
                result = conn.execute(query)
                return [_row_to_dict(row) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting providers: {e}")

        return []

    @staticmethod
    def get_recipe(recepta_codi: str) -> Optional[Dict]:
        """Get recipe details from CO_Receptes_Articles."""
        engine = get_sage_engine()
        if engine is None:
            return None

        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT
                        r.CO_Rcpt_Codi          AS recepta_codi,
                        r.CodigoArticulo        AS codi_article,
                        r.Formula               AS formula,
                        r.Unidades              AS unitats
                    FROM dbo.CO_Receptes_Articles r
                    WHERE r.CO_Rcpt_Codi = :codi
                        AND r.CodigoEmpresa > 0
                    ORDER BY r.CodigoArticulo
                """)
                result = conn.execute(query, {"codi": recepta_codi})
                rows = result.fetchall()
                if rows:
                    return {
                        "recepta_codi": recepta_codi,
                        "articles": [_row_to_dict(row) for row in rows]
                    }
        except Exception as e:
            logger.error(f"Error getting recipe {recepta_codi}: {e}")

        return None


sage_service = SageService()
