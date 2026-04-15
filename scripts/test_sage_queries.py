#!/usr/bin/env python3
"""
Test de las queries SAGE para verificar que los datos se obtienen correctamente.

Ejecutar: python3 test_sage_queries.py

Guarda resultados en: sage_query_results.txt
"""
import pymssql
import sys
import os
from datetime import datetime

SAGE_CONFIG = {
    "server": "192.168.230.181\\CONTROL_SM",
    "database": "SAULEDA_SM",
    "user": "sage_interfaz",
    "password": "InterfazSage#2025!",
}

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_query_results.txt")


def write_and_print(f, text=""):
    print(text)
    f.write(text + "\n")


def test_queries():
    try:
        print("Conectando a SAGE...")
        conn = pymssql.connect(
            server=SAGE_CONFIG["server"],
            database=SAGE_CONFIG["database"],
            user=SAGE_CONFIG["user"],
            password=SAGE_CONFIG["password"],
            login_timeout=15,
            as_dict=True,
        )
        cursor = conn.cursor()
        print("OK!\n")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_and_print(f, "=" * 80)
        write_and_print(f, f"SAGE QUERY TEST RESULTS")
        write_and_print(f, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        write_and_print(f, "=" * 80)

        # ============================================
        # TEST 1: Get recent OFs (last 20)
        # ============================================
        write_and_print(f, "\n\n>>> TEST 1: Last 20 OFs")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT TOP 20
                of_.CO_OrdenFabricacion     AS of_number,
                of_.CodigoArticulo          AS codi_article,
                of_.DescripcionArticulo     AS nom_article,
                of_.CO_Ancho                AS ample,
                of_.CO_HilosTotales         AS fils_totals,
                of_.UnidadesAFabricar       AS metres,
                of_.CO_AnchoPlegador        AS ample_plegador_mm,
                of_.CO_Fajas                AS num_faixes,
                of_.CO_PlegadorTeler        AS teler_num,
                of_.EstadoOF                AS estat,
                of_.FechaCreacion           AS data_creacio,
                of_.SerieFabricacion        AS serie,
                of_.CO_OperacionActual      AS operacio,
                of_.Delegacion              AS delegacio
            FROM dbo.OrdenesFabricacion of_
            WHERE of_.CodigoEmpresa > 0
                AND of_.CO_OrdenFabricacion IS NOT NULL
                AND of_.CO_OrdenFabricacion != ''
            ORDER BY of_.FechaCreacion DESC
        """)
        rows = cursor.fetchall()
        write_and_print(f, f"Found: {len(rows)} OFs\n")

        for i, row in enumerate(rows):
            write_and_print(f, f"  OF #{i+1}: {row['of_number']}")
            write_and_print(f, f"    Article: {row['codi_article']} - {row['nom_article']}")
            write_and_print(f, f"    Ample: {row['ample']}  Fils: {row['fils_totals']}  Metres: {row['metres']}")
            write_and_print(f, f"    Plegador: {row['ample_plegador_mm']}mm  Faixes: {row['num_faixes']}  Teler: {row['teler_num']}")
            write_and_print(f, f"    Estat: {row['estat']}  Serie: {row['serie']}  Operacio: {row['operacio']}")
            write_and_print(f, f"    Data: {row['data_creacio']}  Delegacio: {row['delegacio']}")
            write_and_print(f, "")

        # ============================================
        # TEST 2: Get one specific OF with ALL fields
        # ============================================
        if rows:
            test_of = rows[0]['of_number']
            write_and_print(f, f"\n\n>>> TEST 2: Full details of OF '{test_of}'")
            write_and_print(f, "-" * 60)

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
                    of_.CO_Partida              AS partida,
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
                    of_.CO_ObservacionesFabricacion AS observacions_fabricacio,
                    of_.CO_ObsAcabado           AS observacions_acabat,
                    of_.CO_ObsTelares           AS observacions_telers,
                    of_.CO_ObsUrdido            AS observacions_urdit,
                    of_.CO_ObsOtros             AS observacions_altres,
                    of_.EjercicioFabricacion    AS exercici,
                    of_.SerieFabricacion        AS serie,
                    of_.NumeroFabricacion       AS numero,
                    of_.Delegacion              AS delegacio
                FROM dbo.OrdenesFabricacion of_
                WHERE of_.CO_OrdenFabricacion = %s
            """, (test_of,))

            detail = cursor.fetchone()
            if detail:
                for key, val in detail.items():
                    val_str = str(val).strip() if val is not None else "NULL"
                    if val_str and val_str != "0" and val_str != "0E-10" and val_str != "NULL":
                        write_and_print(f, f"  {key:<35} = {val_str}")

        # ============================================
        # TEST 3: Count OFs by status
        # ============================================
        write_and_print(f, "\n\n>>> TEST 3: OF counts by status")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT
                EstadoOF,
                COUNT(*) as total
            FROM dbo.OrdenesFabricacion
            WHERE CodigoEmpresa > 0
            GROUP BY EstadoOF
            ORDER BY EstadoOF
        """)
        for row in cursor.fetchall():
            estado_name = {0: "Planificada", 1: "Lanzada", 2: "Cerrada"}.get(
                row['EstadoOF'], f"Desconocido({row['EstadoOF']})")
            write_and_print(f, f"  {estado_name}: {row['total']}")

        # ============================================
        # TEST 4: Count OFs by year
        # ============================================
        write_and_print(f, "\n\n>>> TEST 4: OF counts by year (last 5)")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT TOP 5
                EjercicioFabricacion as anyo,
                COUNT(*) as total
            FROM dbo.OrdenesFabricacion
            WHERE CodigoEmpresa > 0
                AND EjercicioFabricacion > 0
            GROUP BY EjercicioFabricacion
            ORDER BY EjercicioFabricacion DESC
        """)
        for row in cursor.fetchall():
            write_and_print(f, f"  {row['anyo']}: {row['total']} OFs")

        # ============================================
        # TEST 5: Series available
        # ============================================
        write_and_print(f, "\n\n>>> TEST 5: Series in use")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT
                SerieFabricacion as serie,
                Delegacion as delegacio,
                COUNT(*) as total
            FROM dbo.OrdenesFabricacion
            WHERE CodigoEmpresa > 0
                AND SerieFabricacion != ''
            GROUP BY SerieFabricacion, Delegacion
            ORDER BY total DESC
        """)
        for row in cursor.fetchall():
            write_and_print(f, f"  Serie '{row['serie']}' (Delegacio: {row['delegacio']}): {row['total']} OFs")

        # ============================================
        # TEST 6: Check if Articulos table has useful data
        # ============================================
        write_and_print(f, "\n\n>>> TEST 6: Sample articles")
        write_and_print(f, "-" * 60)

        try:
            cursor.execute("""
                SELECT TOP 5
                    CodigoArticulo,
                    DescripcionArticulo,
                    CodigoFamilia_,
                    CodigoSubfamilia_,
                    PesoNetoUnitario_
                FROM dbo.Articulos
                WHERE CodigoEmpresa > 0
                    AND DescripcionArticulo IS NOT NULL
                    AND DescripcionArticulo != ''
                ORDER BY CodigoArticulo
            """)
            for row in cursor.fetchall():
                write_and_print(f, f"  {row['CodigoArticulo']}: {row['DescripcionArticulo']}")
                write_and_print(f, f"    Familia: {row['CodigoFamilia_']}  Subfam: {row['CodigoSubfamilia_']}  Peso: {row['PesoNetoUnitario_']}")
        except Exception as e:
            write_and_print(f, f"  Error: {e}")

        # ============================================
        # TEST 7: Check Proveedores
        # ============================================
        write_and_print(f, "\n\n>>> TEST 7: Sample providers")
        write_and_print(f, "-" * 60)

        try:
            cursor.execute("""
                SELECT TOP 10
                    CodigoProveedor,
                    RazonSocial
                FROM dbo.Proveedores
                WHERE CodigoEmpresa > 0
                    AND RazonSocial IS NOT NULL
                    AND RazonSocial != ''
                ORDER BY RazonSocial
            """)
            for row in cursor.fetchall():
                write_and_print(f, f"  {row['CodigoProveedor']}: {row['RazonSocial']}")
        except Exception as e:
            write_and_print(f, f"  Error: {e}")

        # ============================================
        # DONE
        # ============================================
        write_and_print(f, f"\n\nReport saved to: {OUTPUT_FILE}")

    conn.close()
    print(f"\nDone! Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    test_queries()
