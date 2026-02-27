import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

INTEGRA = dict(
    host=os.environ["INTEGRA_PG_HOST"],
    port=int(os.environ.get("INTEGRA_PG_PORT", "5432")),
    dbname=os.environ["INTEGRA_PG_NAME"],
    user=os.environ["INTEGRA_PG_USER"],
    password=os.environ["INTEGRA_PG_PASSWORD"],
)

EXT = dict(
    host=os.environ["EXT_PG_HOST"],
    port=int(os.environ.get("EXT_PG_PORT", "5432")),
    dbname=os.environ["EXT_PG_NAME"],
    user=os.environ["EXT_PG_USER"],
    password=os.environ["EXT_PG_PASSWORD"],
)

FALLBACK_LPS = (2, 4, 7, 8)

SQL = f"""
SELECT
  p.cod_producto,
  p.desc_producto,
  x.p_base AS precio_neto,
  x.cod_lp_vendedor AS lp_usada
FROM comun.producto p
JOIN LATERAL (
  SELECT d.cod_lp_vendedor, d.p_base
  FROM ventas.detalle_lp_vendedor d
  WHERE d.cod_producto = p.cod_producto
    AND d.p_base > 0
    AND d.cod_lp_vendedor = ANY(%(lps)s)
  ORDER BY
    CASE d.cod_lp_vendedor
      WHEN 2 THEN 1 WHEN 4 THEN 2 WHEN 7 THEN 3 WHEN 8 THEN 4 ELSE 99 END,
    d.inserttime DESC NULLS LAST,
    d.cod_detalle_lp_vendedor DESC
  LIMIT 1
) x ON true
WHERE p.activo = true
ORDER BY p.desc_producto;
"""

DDL = """
CREATE SCHEMA IF NOT EXISTS catalog;

CREATE TABLE IF NOT EXISTS catalog.product_catalog_cache (
  cod_producto   integer PRIMARY KEY,
  desc_producto  varchar(200) NOT NULL,
  precio_neto    numeric(12,2) NOT NULL,
  lp_usada       integer NOT NULL,
  updated_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_catalog_cache_desc
  ON catalog.product_catalog_cache (desc_producto);

CREATE INDEX IF NOT EXISTS idx_catalog_cache_lp
  ON catalog.product_catalog_cache (lp_usada);

CREATE INDEX IF NOT EXISTS idx_catalog_cache_precio
  ON catalog.product_catalog_cache (precio_neto);
"""

UPSERT = """
INSERT INTO catalog.product_catalog_cache (cod_producto, desc_producto, precio_neto, lp_usada, updated_at)
VALUES (%(cod_producto)s, %(desc_producto)s, %(precio_neto)s, %(lp_usada)s, now())
ON CONFLICT (cod_producto) DO UPDATE SET
  desc_producto = EXCLUDED.desc_producto,
  precio_neto = EXCLUDED.precio_neto,
  lp_usada = EXCLUDED.lp_usada,
  updated_at = now();
"""

def main():
    with psycopg.connect(**EXT, row_factory=dict_row) as ext:
        with ext.cursor() as cur:
            cur.execute(DDL)
        ext.commit()

    with psycopg.connect(**INTEGRA, row_factory=dict_row) as inte:
        with inte.cursor() as cur:
            cur.execute(SQL, {"lps": list(FALLBACK_LPS)})
            rows = cur.fetchall()

    print(f"Filas desde INTEGRA: {len(rows)}")

    with psycopg.connect(**EXT, row_factory=dict_row) as ext:
        with ext.cursor() as cur:
            for r in rows:
                cur.execute(UPSERT, r)
        ext.commit()

    print("OK: cache actualizado.")

if __name__ == "__main__":
    main()