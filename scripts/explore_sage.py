#!/usr/bin/env python3
"""
Script para explorar el esquema de la BBDD SAGE y localizar
tablas/campos relacionados con Ordres de Fabricacio (OF).

Ejecutar desde un equipo con acceso a la red del servidor SAGE:
  pip install pymssql
  python3 explore_sage.py

Los resultados se guardan en: sage_schema_report.txt
"""

import pymssql
import sys
import os
from datetime import datetime

# ============================================
# CONFIGURACION - Modificar si es necesario
# ============================================
SAGE_CONFIG = {
    "server": "192.168.230.181\\CONTROL_SM",
    "database": "SAULEDA_SM",
    "user": "sage_interfaz",
    "password": "InterfazSage#2025!",
}

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_schema_report.txt")


def write_and_print(f, text=""):
    """Write to file and print to console."""
    print(text)
    f.write(text + "\n")


def explore_sage():
    report_lines = []

    try:
        print("Conectando a SAGE MSSQL...")
        conn = pymssql.connect(
            server=SAGE_CONFIG["server"],
            database=SAGE_CONFIG["database"],
            user=SAGE_CONFIG["user"],
            password=SAGE_CONFIG["password"],
            login_timeout=15,
        )
        cursor = conn.cursor()
        print("Conexion OK!\n")
    except Exception as e:
        print(f"ERROR de conexion: {e}")
        print("\nSi usas ODBC en vez de pymssql, prueba con el script explore_sage_odbc.py")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_and_print(f, "=" * 80)
        write_and_print(f, f"SAGE DATABASE SCHEMA REPORT - {SAGE_CONFIG['database']}")
        write_and_print(f, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        write_and_print(f, "=" * 80)

        # ============================================
        # 1. LIST ALL TABLES (user tables only)
        # ============================================
        write_and_print(f, "\n\n>>> 1. ALL USER TABLES")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        tables = cursor.fetchall()
        write_and_print(f, f"Total tables: {len(tables)}\n")

        for schema, table in tables:
            write_and_print(f, f"  {schema}.{table}")

        # ============================================
        # 2. SEARCH FOR OF-RELATED TABLES
        # ============================================
        write_and_print(f, "\n\n>>> 2. TABLES LIKELY RELATED TO OF (Ordres de Fabricacio)")
        write_and_print(f, "-" * 60)

        of_keywords = [
            "fabric", "ordre", "order", "produc", "of_", "articl", "article",
            "teixit", "teixid", "telar", "teler", "urdid", "ordit", "muntad",
            "plegad", "color", "fil", "fils", "lote", "lot_", "materia",
            "stock", "magat", "almac", "proveedor", "proveid", "operari",
            "maquina", "pua", "faixa", "program", "planif"
        ]

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        all_tables = cursor.fetchall()

        found_tables = []
        for schema, table in all_tables:
            table_lower = table.lower()
            for kw in of_keywords:
                if kw in table_lower:
                    found_tables.append((schema, table, kw))
                    break

        if found_tables:
            for schema, table, matched_kw in found_tables:
                write_and_print(f, f"\n  [{matched_kw}] {schema}.{table}")
        else:
            write_and_print(f, "  No tables found matching OF keywords.")
            write_and_print(f, "  (SAGE may use different naming conventions)")

        # ============================================
        # 3. SEARCH ALL COLUMN NAMES FOR OF-RELATED FIELDS
        # ============================================
        write_and_print(f, "\n\n>>> 3. COLUMNS MATCHING OF-RELATED KEYWORDS")
        write_and_print(f, "-" * 60)

        col_keywords = [
            "of_", "ordre", "fabric", "articl", "ample", "fils",
            "metres", "teler", "plegad", "faixa", "color", "ordit",
            "urdid", "muntad", "lote", "lot_", "proveid", "proveedor"
        ]

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE,
                   CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """)
        all_columns = cursor.fetchall()

        for kw in col_keywords:
            matches = [c for c in all_columns if kw in c[2].lower()]
            if matches:
                write_and_print(f, f"\n  Keyword '{kw}' found in columns:")
                for schema, table, col, dtype, maxlen, nullable in matches:
                    size = f"({maxlen})" if maxlen else ""
                    write_and_print(f, f"    {schema}.{table}.{col} [{dtype}{size}]")

        # ============================================
        # 4. DETAILED SCHEMA OF CANDIDATE TABLES
        # ============================================
        write_and_print(f, "\n\n>>> 4. DETAILED SCHEMA OF CANDIDATE TABLES")
        write_and_print(f, "-" * 60)

        # Find tables that might contain OF data - broader search
        candidate_keywords = ["fabric", "ordre", "order", "produc", "of_",
                              "articl", "article", "cabec", "linea", "linee"]

        candidate_tables = set()
        for schema, table in all_tables:
            table_lower = table.lower()
            for kw in candidate_keywords:
                if kw in table_lower:
                    candidate_tables.add((schema, table))
                    break

        # Also add tables that have columns with 'of' or 'ordre' in their name
        for schema, table, col, dtype, maxlen, nullable in all_columns:
            col_lower = col.lower()
            if any(k in col_lower for k in ["num_of", "ordre_fab", "of_number", "n_of", "nof"]):
                candidate_tables.add((schema, table))

        if not candidate_tables:
            write_and_print(f, "  No strong candidates found. Showing first 20 tables with full schema:")
            candidate_tables = set(list(all_tables)[:20])

        for schema, table in sorted(candidate_tables):
            write_and_print(f, f"\n  TABLE: {schema}.{table}")
            write_and_print(f, "  " + "~" * 50)

            cols_for_table = [c for c in all_columns if c[0] == schema and c[1] == table]
            for _, _, col, dtype, maxlen, nullable in cols_for_table:
                size = f"({maxlen})" if maxlen else ""
                null_str = "NULL" if nullable == "YES" else "NOT NULL"
                write_and_print(f, f"    {col:<40} {dtype}{size:<15} {null_str}")

            # Show sample data (first 3 rows)
            try:
                cursor.execute(f"SELECT TOP 3 * FROM [{schema}].[{table}]")
                rows = cursor.fetchall()
                if rows:
                    col_names = [c[2] for c in cols_for_table]
                    write_and_print(f, f"\n    Sample data ({len(rows)} rows):")
                    for i, row in enumerate(rows):
                        write_and_print(f, f"    Row {i+1}:")
                        for j, val in enumerate(row):
                            if j < len(col_names):
                                val_str = str(val)[:80] if val is not None else "NULL"
                                write_and_print(f, f"      {col_names[j]}: {val_str}")
            except Exception as e:
                write_and_print(f, f"    (Could not read sample data: {e})")

        # ============================================
        # 5. LOOK FOR VIEWS (SAGE often uses views)
        # ============================================
        write_and_print(f, "\n\n>>> 5. DATABASE VIEWS")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.VIEWS
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        views = cursor.fetchall()
        write_and_print(f, f"Total views: {len(views)}\n")

        for schema, view in views:
            write_and_print(f, f"  {schema}.{view}")

        # Also detail views matching OF keywords
        of_views = [(s, v) for s, v in views
                    if any(kw in v.lower() for kw in candidate_keywords)]
        if of_views:
            write_and_print(f, "\n  OF-related views with columns:")
            for schema, view in of_views:
                write_and_print(f, f"\n  VIEW: {schema}.{view}")
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{view}'
                    ORDER BY ORDINAL_POSITION
                """)
                for col, dtype, maxlen in cursor.fetchall():
                    size = f"({maxlen})" if maxlen else ""
                    write_and_print(f, f"    {col:<40} {dtype}{size}")

        # ============================================
        # 6. STORED PROCEDURES (may reveal OF logic)
        # ============================================
        write_and_print(f, "\n\n>>> 6. STORED PROCEDURES (OF-related)")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE'
            ORDER BY ROUTINE_NAME
        """)
        procs = cursor.fetchall()
        of_procs = [(s, n, t) for s, n, t in procs
                    if any(kw in n.lower() for kw in ["fabric", "ordre", "of_", "produc", "articl"])]

        if of_procs:
            for schema, name, rtype in of_procs:
                write_and_print(f, f"  {schema}.{name}")
        else:
            write_and_print(f, f"  Total procedures: {len(procs)}")
            write_and_print(f, "  No OF-specific procedures found. All procedures:")
            for schema, name, rtype in procs[:30]:
                write_and_print(f, f"    {schema}.{name}")
            if len(procs) > 30:
                write_and_print(f, f"    ... and {len(procs) - 30} more")

        # ============================================
        # 7. SUMMARY
        # ============================================
        write_and_print(f, "\n\n>>> 7. SUMMARY")
        write_and_print(f, "=" * 80)
        write_and_print(f, f"Total user tables: {len(tables)}")
        write_and_print(f, f"Total views: {len(views)}")
        write_and_print(f, f"Total procedures: {len(procs)}")
        write_and_print(f, f"OF-candidate tables: {len(candidate_tables)}")
        write_and_print(f, f"\nReport saved to: {OUTPUT_FILE}")

        conn.close()
        print(f"\nDone! Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    explore_sage()
