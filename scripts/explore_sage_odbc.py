#!/usr/bin/env python3
"""
Alternativa usando pyodbc (ODBC Driver 18) para explorar SAGE.
Usar si pymssql no conecta con la instancia nombrada.

  pip install pyodbc
  python3 explore_sage_odbc.py
"""

import sys
import os

try:
    import pyodbc
except ImportError:
    print("Instalando pyodbc...")
    os.system(f"{sys.executable} -m pip install pyodbc")
    import pyodbc

from datetime import datetime

SAGE_CONFIG = {
    "server": "192.168.230.181\\CONTROL_SM",
    "database": "SAULEDA_SM",
    "user": "sage_interfaz",
    "password": "InterfazSage#2025!",
    "driver": "ODBC Driver 18 for SQL Server",
}

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_schema_report.txt")


def write_and_print(f, text=""):
    print(text)
    f.write(text + "\n")


def explore():
    conn_str = (
        f"DRIVER={{{SAGE_CONFIG['driver']}}};"
        f"SERVER={SAGE_CONFIG['server']};"
        f"DATABASE={SAGE_CONFIG['database']};"
        f"UID={SAGE_CONFIG['user']};"
        f"PWD={SAGE_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )

    try:
        print(f"Conectando con ODBC Driver 18...")
        print(f"Server: {SAGE_CONFIG['server']}")
        print(f"Database: {SAGE_CONFIG['database']}")
        conn = pyodbc.connect(conn_str, timeout=15)
        cursor = conn.cursor()
        print("Conexion OK!\n")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nVerifica que tienes ODBC Driver 18 instalado:")
        print("  - Windows: suele venir con SQL Server tools")
        print("  - Mac: brew install msodbcsql18")
        print("  - Linux: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_and_print(f, "=" * 80)
        write_and_print(f, f"SAGE DATABASE SCHEMA REPORT - {SAGE_CONFIG['database']}")
        write_and_print(f, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        write_and_print(f, f"Driver: {SAGE_CONFIG['driver']}")
        write_and_print(f, "=" * 80)

        # 1. ALL TABLES
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
        for row in tables:
            write_and_print(f, f"  {row.TABLE_SCHEMA}.{row.TABLE_NAME}")

        # 2. OF-RELATED TABLES
        write_and_print(f, "\n\n>>> 2. TABLES LIKELY RELATED TO OF")
        write_and_print(f, "-" * 60)

        of_keywords = [
            "fabric", "ordre", "order", "produc", "of_", "articl", "article",
            "teixit", "teixid", "telar", "teler", "urdid", "ordit", "muntad",
            "plegad", "color", "fil", "fils", "lote", "lot_", "materia",
            "stock", "magat", "almac", "proveedor", "proveid", "operari",
            "maquina", "pua", "faixa", "program", "planif", "cabec", "linea"
        ]

        for row in tables:
            table_lower = row.TABLE_NAME.lower()
            matched = [kw for kw in of_keywords if kw in table_lower]
            if matched:
                write_and_print(f, f"\n  [{', '.join(matched)}] {row.TABLE_SCHEMA}.{row.TABLE_NAME}")

                # Show columns
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                """, row.TABLE_SCHEMA, row.TABLE_NAME)
                cols = cursor.fetchall()
                for col in cols:
                    size = f"({col.CHARACTER_MAXIMUM_LENGTH})" if col.CHARACTER_MAXIMUM_LENGTH else ""
                    null_str = "NULL" if col.IS_NULLABLE == "YES" else "NOT NULL"
                    write_and_print(f, f"    {col.COLUMN_NAME:<40} {col.DATA_TYPE}{size:<15} {null_str}")

                # Sample data
                try:
                    col_names = [c.COLUMN_NAME for c in cols]
                    cursor.execute(f"SELECT TOP 3 * FROM [{row.TABLE_SCHEMA}].[{row.TABLE_NAME}]")
                    samples = cursor.fetchall()
                    if samples:
                        write_and_print(f, f"\n    Sample data ({len(samples)} rows):")
                        for i, sample in enumerate(samples):
                            write_and_print(f, f"    Row {i+1}:")
                            for j, val in enumerate(sample):
                                if j < len(col_names):
                                    val_str = str(val)[:100] if val is not None else "NULL"
                                    write_and_print(f, f"      {col_names[j]}: {val_str}")
                except Exception as e:
                    write_and_print(f, f"    (Sample data error: {e})")

        # 3. COLUMNS WITH OF KEYWORDS
        write_and_print(f, "\n\n>>> 3. COLUMNS MATCHING OF KEYWORDS")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """)
        all_cols = cursor.fetchall()

        col_keywords = ["of_", "ordre", "fabric", "articl", "ample", "fils",
                        "metres", "teler", "plegad", "faixa", "color", "ordit",
                        "urdid", "muntad", "lote", "proveid", "proveedor"]

        for kw in col_keywords:
            matches = [c for c in all_cols if kw in c.COLUMN_NAME.lower()]
            if matches:
                write_and_print(f, f"\n  Keyword '{kw}' in columns:")
                for c in matches:
                    write_and_print(f, f"    {c.TABLE_SCHEMA}.{c.TABLE_NAME}.{c.COLUMN_NAME} [{c.DATA_TYPE}]")

        # 4. VIEWS
        write_and_print(f, "\n\n>>> 4. DATABASE VIEWS")
        write_and_print(f, "-" * 60)

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.VIEWS
            ORDER BY TABLE_NAME
        """)
        views = cursor.fetchall()
        write_and_print(f, f"Total views: {len(views)}\n")
        for v in views:
            write_and_print(f, f"  {v.TABLE_SCHEMA}.{v.TABLE_NAME}")

        # 5. SUMMARY
        write_and_print(f, "\n\n>>> SUMMARY")
        write_and_print(f, "=" * 80)
        write_and_print(f, f"Total tables: {len(tables)}")
        write_and_print(f, f"Total views: {len(views)}")
        write_and_print(f, f"Report saved to: {OUTPUT_FILE}")

    conn.close()
    print(f"\nDone! Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    explore()
