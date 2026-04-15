#!/usr/bin/env python3
"""
Test local: servidor que sirve el frontend y hace proxy al API de SAGE.

Ejecutar desde la raiz del proyecto:
    cd ~/Desktop/Niene_Produccion
    python3 scripts/run_local_test.py

Abre http://localhost:3000 automaticamente.

Requisitos:
    pip3 install pymssql
"""

import http.server
import json
import os
import sys
import webbrowser
import threading
import time
import urllib.parse

# Add project paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env
SAGE_CONFIG = {}
env_file = os.path.join(ROOT_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                SAGE_CONFIG[key.strip()] = val.strip()


def get_sage_connection():
    """Create a pymssql connection to SAGE."""
    import pymssql
    server = SAGE_CONFIG.get("SAGE_DB_HOST", "")
    instance = SAGE_CONFIG.get("SAGE_DB_INSTANCE", "")
    if instance:
        server = server + "\\" + instance
    return pymssql.connect(
        server=server,
        database=SAGE_CONFIG.get("SAGE_DB_NAME", ""),
        user=SAGE_CONFIG.get("SAGE_DB_USER", ""),
        password=SAGE_CONFIG.get("SAGE_DB_PASSWORD", ""),
        login_timeout=10,
        as_dict=True,
    )


# ============================================
# SAGE API handlers
# ============================================

def handle_sage_status():
    """GET /api/sage/status"""
    try:
        conn = get_sage_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"connected": True, "message": "SAGE connectat"}
    except Exception as e:
        return {"connected": False, "message": "SAGE no disponible: " + str(e)}


def handle_sage_of(of_number):
    """GET /api/sage/of/{of_number}"""
    try:
        conn = get_sage_connection()
        cursor = conn.cursor()

        # Try exact match first
        cursor.execute("""
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
                of_.CO_VelocidadPlegado     AS velocitat_plegat,
                of_.CO_VelocidadTelar       AS velocitat_teler,
                of_.CO_PresionPlegado       AS pressio_plegat,
                of_.CO_DensAcaOrdidor       AS densitat_ordidor,
                of_.CO_DobleAmple           AS doble_ample,
                of_.CO_UnidadesaUrdir       AS metres_urdir,
                of_.CO_AnchoPlegador        AS ample_plegador,
                of_.CO_6Pintes              AS sis_pintes,
                of_.CO_Rcpt_Codi            AS recepta_codi,
                of_.CO_Tipo                 AS tipus,
                of_.CO_Partida              AS partida,
                of_.EstadoOF                AS estat_sage,
                of_.FechaCreacion           AS data_creacio,
                of_.CO_OperacionActual      AS operacio_actual,
                of_.CO_ObservacionesFabricacion AS observacions_fabricacio,
                of_.CO_ObsTelares           AS observacions_telers,
                of_.CO_ObsUrdido            AS observacions_urdit,
                of_.EjercicioFabricacion    AS exercici,
                of_.SerieFabricacion        AS serie,
                of_.NumeroFabricacion       AS numero,
                of_.Delegacion              AS delegacio
            FROM dbo.OrdenesFabricacion of_
            WHERE of_.CO_OrdenFabricacion = %s
        """, (of_number,))

        row = cursor.fetchone()

        # If not found, try LIKE search
        if not row:
            cursor.execute("""
                SELECT TOP 1
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
                    of_.CO_VelocidadPlegado     AS velocitat_plegat,
                    of_.CO_VelocidadTelar       AS velocitat_teler,
                    of_.CO_PresionPlegado       AS pressio_plegat,
                    of_.CO_DensAcaOrdidor       AS densitat_ordidor,
                    of_.CO_DobleAmple           AS doble_ample,
                    of_.CO_UnidadesaUrdir       AS metres_urdir,
                    of_.CO_AnchoPlegador        AS ample_plegador,
                    of_.CO_6Pintes              AS sis_pintes,
                    of_.CO_Rcpt_Codi            AS recepta_codi,
                    of_.CO_Tipo                 AS tipus,
                    of_.CO_Partida              AS partida,
                    of_.EstadoOF                AS estat_sage,
                    of_.FechaCreacion           AS data_creacio,
                    of_.CO_OperacionActual      AS operacio_actual,
                    of_.CO_ObservacionesFabricacion AS observacions_fabricacio,
                    of_.CO_ObsTelares           AS observacions_telers,
                    of_.CO_ObsUrdido            AS observacions_urdit,
                    of_.EjercicioFabricacion    AS exercici,
                    of_.SerieFabricacion        AS serie,
                    of_.NumeroFabricacion       AS numero,
                    of_.Delegacion              AS delegacio
                FROM dbo.OrdenesFabricacion of_
                WHERE of_.CO_OrdenFabricacion LIKE %s
                ORDER BY of_.FechaCreacion DESC
            """, ("%" + of_number + "%",))
            row = cursor.fetchone()

        conn.close()

        if row:
            # Clean up the data
            result = {}
            for key, val in row.items():
                if val is not None:
                    if isinstance(val, str):
                        result[key] = val.strip()
                    elif hasattr(val, 'is_zero') and val.is_zero():
                        result[key] = 0
                    else:
                        # Convert Decimal to float for JSON
                        try:
                            result[key] = float(val) if '.' in str(val) else val
                        except (ValueError, TypeError):
                            result[key] = val
                else:
                    result[key] = val
            return result
        else:
            return None

    except Exception as e:
        print("SAGE error: " + str(e))
        return None


def handle_sage_ofs(search="", limit=20):
    """GET /api/sage/ofs"""
    try:
        conn = get_sage_connection()
        cursor = conn.cursor()

        if search:
            cursor.execute("""
                SELECT TOP """ + str(int(limit)) + """
                    of_.CO_OrdenFabricacion     AS of_number,
                    of_.CodigoArticulo          AS codi_article,
                    of_.DescripcionArticulo     AS nom_article,
                    of_.CO_Ancho                AS ample,
                    of_.CO_HilosTotales         AS fils_totals,
                    of_.UnidadesAFabricar       AS metres,
                    of_.EstadoOF                AS estat_sage,
                    of_.SerieFabricacion        AS serie,
                    of_.Delegacion              AS delegacio
                FROM dbo.OrdenesFabricacion of_
                WHERE of_.CodigoEmpresa > 0
                    AND (of_.CO_OrdenFabricacion LIKE %s
                         OR of_.CodigoArticulo LIKE %s
                         OR of_.DescripcionArticulo LIKE %s)
                ORDER BY of_.FechaCreacion DESC
            """, ("%" + search + "%", "%" + search + "%", "%" + search + "%"))
        else:
            cursor.execute("""
                SELECT TOP """ + str(int(limit)) + """
                    of_.CO_OrdenFabricacion     AS of_number,
                    of_.CodigoArticulo          AS codi_article,
                    of_.DescripcionArticulo     AS nom_article,
                    of_.CO_Ancho                AS ample,
                    of_.CO_HilosTotales         AS fils_totals,
                    of_.UnidadesAFabricar       AS metres,
                    of_.EstadoOF                AS estat_sage,
                    of_.SerieFabricacion        AS serie,
                    of_.Delegacion              AS delegacio
                FROM dbo.OrdenesFabricacion of_
                WHERE of_.CodigoEmpresa > 0
                    AND of_.CO_OrdenFabricacion IS NOT NULL
                    AND of_.CO_OrdenFabricacion != ''
                ORDER BY of_.FechaCreacion DESC
            """)

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            clean = {}
            for key, val in row.items():
                if val is not None:
                    if isinstance(val, str):
                        clean[key] = val.strip()
                    else:
                        try:
                            clean[key] = float(val) if '.' in str(val) else val
                        except (ValueError, TypeError):
                            clean[key] = val
                else:
                    clean[key] = val
            results.append(clean)

        return {"ofs": results, "sage_available": True, "total": len(results)}

    except Exception as e:
        print("SAGE search error: " + str(e))
        return {"ofs": [], "sage_available": False}


# ============================================
# HTTP Server with API routing
# ============================================

class TestHandler(http.server.SimpleHTTPRequestHandler):
    """Serves frontend files and handles /api/ requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0]
        query_string = self.path.split("?")[1] if "?" in self.path else ""
        params = urllib.parse.parse_qs(query_string)

        # API routes
        if path == "/api/sage/status":
            self.send_json(handle_sage_status())
            return

        if path.startswith("/api/sage/of/"):
            of_number = urllib.parse.unquote(path[len("/api/sage/of/"):].rstrip("/"))
            result = handle_sage_of(of_number)
            if result:
                self.send_json(result)
            else:
                self.send_json({"detail": "OF no trobada a SAGE"}, status=404)
            return

        if path == "/api/sage/ofs" or path == "/api/sage/ofs/":
            search = params.get("search", [""])[0]
            limit = int(params.get("limit", ["20"])[0])
            self.send_json(handle_sage_ofs(search, limit))
            return

        if path == "/api/health":
            self.send_json({"status": "ok", "app": "Niene Produccion (test local)", "sage_configured": True})
            return

        # For /api/hoja* routes, return empty lists (no PostgreSQL in local test)
        if path.startswith("/api/hoja"):
            if path.rstrip("/").count("/") == 2:
                # List endpoint
                self.send_json([])
            else:
                self.send_json({"detail": "Not found in local test mode"}, status=404)
            return

        # Serve static files
        super().do_GET()

    def send_json(self, data, status=200):
        """Send JSON response."""
        import datetime

        def json_serial(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            if hasattr(obj, '__float__'):
                return float(obj)
            raise TypeError("Type not serializable: " + str(type(obj)))

        body = json.dumps(data, default=json_serial, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Custom log format."""
        if "/api/" in str(args[0]):
            print("  API: " + str(args[0]))
        # Suppress static file logs


def main():
    port = 3000

    print("=" * 60)
    print("  NIENE PRODUCCION - Test Local")
    print("=" * 60)
    print("")

    # Test SAGE connection first
    print("Testejant connexio SAGE...")
    status = handle_sage_status()
    if status["connected"]:
        print("  SAGE: CONNECTAT OK!")
    else:
        print("  SAGE: " + status["message"])
        print("  (El frontend funcionara en mode localStorage)")

    print("")
    print("  Frontend + API:  http://localhost:" + str(port))
    print("  SAGE Status:     http://localhost:" + str(port) + "/api/sage/status")
    print("  Buscar OF:       http://localhost:" + str(port) + "/api/sage/of/NO/26.0503")
    print("")
    print("  Pulsa Ctrl+C per parar")
    print("=" * 60)
    print("")

    # Open browser
    def open_browser():
        time.sleep(1)
        webbrowser.open("http://localhost:" + str(port))

    threading.Thread(target=open_browser, daemon=True).start()

    # Start server
    server = http.server.HTTPServer(("0.0.0.0", port), TestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nParant servidor...")
        server.shutdown()
        print("Fet!")


if __name__ == "__main__":
    main()
