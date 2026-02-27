"""Crea filas base en EXT para todos los productos activos de INTEGRA.

Uso (PowerShell):
  cd backend
  .\.venv\Scripts\Activate.ps1
  python scripts/seed_product_extra.py
"""
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def conn_integra():
    return psycopg.connect(
        host=os.environ["INTEGRA_PG_HOST"],
        port=int(os.environ.get("INTEGRA_PG_PORT", "5432")),
        dbname=os.environ["INTEGRA_PG_NAME"],
        user=os.environ["INTEGRA_PG_USER"],
        password=os.environ["INTEGRA_PG_PASSWORD"],
        row_factory=dict_row,
    )

def conn_ext():
    return psycopg.connect(
        host=os.environ["EXT_PG_HOST"],
        port=int(os.environ.get("EXT_PG_PORT", "5432")),
        dbname=os.environ["EXT_PG_NAME"],
        user=os.environ["EXT_PG_USER"],
        password=os.environ["EXT_PG_PASSWORD"],
        row_factory=dict_row,
    )

def main():
    with conn_ext() as ext:
        with ext.cursor() as cur:
            cur.execute(open("scripts/01_ext_schema.sql", "r", encoding="utf-8").read())

    with conn_integra() as inte:
        with inte.cursor() as cur:
            cur.execute("SELECT DISTINCT p.cod_producto FROM comun.producto p JOIN ventas.detalle_lp_vendedor d ON d.cod_producto = p.cod_producto WHERE p.activo = true AND d.p_base > 0;")
            cods = [int(r["cod_producto"]) for r in cur.fetchall()]

    inserted = 0
    with conn_ext() as ext:
        with ext.cursor() as cur:
            for cod in cods:
                cur.execute(
                    "INSERT INTO catalog.product_extra(cod_producto) VALUES(%s) ON CONFLICT DO NOTHING;",
                    (cod,),
                )
                inserted += 1
        ext.commit()

    print(f"OK: {inserted} filas aseguradas en catalog.product_extra")

if __name__ == "__main__":
    main()
