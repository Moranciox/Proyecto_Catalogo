import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Regex de apoyo (por si graduaje viene malo en algunos registros)
INCLUDE_REGEX = r"(VINO|ESPUMANTE|CHAMP|CAVA|PISCO|LICOR|RON|WHISK|WHISKY|VODKA|GIN|TEQUILA|CERVEZA|VERMOUTH|APERITIV|SIDRA|SANGRIA)"
EXCLUDE_REGEX = r"(AGUA|JUGO|GASEOSA|SNACK|GALLET|CONFITE|AZUCAR|HARINA|ARROZ|FIDEO|ACEITE|LECHE|YOGUR|PAN|MERMEL|QUESO)"

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

MIN_PRICE = float(os.environ.get("CATALOG_MIN_PRICE", "500"))

def parse_int_list(val: str, default: list[int]) -> list[int]:
    try:
        out: list[int] = []
        for x in (val or "").split(","):
            x = x.strip()
            if not x:
                continue
            out.append(int(x))
        return out if out else default
    except Exception:
        return default

NON_ALC_SUBS = parse_int_list(os.environ.get("NON_ALCOHOL_SUBFAMILIAS", "481"), [481])


def _safe_any_list(vals: list[int]) -> list[int]:
    """Postgres ANY() con lista vacía siempre da FALSE; usamos [-1] como guardia."""
    return vals if vals else [-1]


def _fetch_catalog_sets(conn: psycopg.Connection) -> tuple[list[int], list[int]]:
    """Deriva sub-familias y tipos "de catálogo" para tolerar graduajes malos.

    Regla: tomamos todos los cod_sub_familia / cod_tipo_producto que aparezcan en productos
    que cumplan alguna señal fuerte de "bebida" (graduaje>0, regex de inclusión,
    o excepciones no alcohólicas).
    """

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT p.cod_sub_familia
            FROM comun.producto p
            WHERE p.activo = true
              AND p.cod_sub_familia IS NOT NULL
              AND (
                    COALESCE(p.graduaje, 0) > 0
                    OR p.desc_producto ~* %(include_regex)s
                    OR p.cod_sub_familia = ANY(%(non_alc_subs)s)
                    OR p.desc_producto ~* 'ENERGET'
                  );
            """,
            {"include_regex": INCLUDE_REGEX, "non_alc_subs": _safe_any_list(NON_ALC_SUBS)},
        )
        subs = [int(r["cod_sub_familia"]) for r in cur.fetchall() if r["cod_sub_familia"] is not None]

        cur.execute(
            """
            SELECT DISTINCT p.cod_tipo_producto
            FROM comun.producto p
            WHERE p.activo = true
              AND p.cod_tipo_producto IS NOT NULL
              AND (
                    COALESCE(p.graduaje, 0) > 0
                    OR p.desc_producto ~* %(include_regex)s
                    OR p.cod_sub_familia = ANY(%(non_alc_subs)s)
                    OR p.desc_producto ~* 'ENERGET'
                  );
            """,
            {"include_regex": INCLUDE_REGEX, "non_alc_subs": _safe_any_list(NON_ALC_SUBS)},
        )
        tipos = [int(r["cod_tipo_producto"]) for r in cur.fetchall() if r["cod_tipo_producto"] is not None]

    return subs, tipos

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
    AND d.p_base >= %(min_price)s
  ORDER BY
    d.inserttime DESC NULLS LAST,
    d.cod_detalle_lp_vendedor DESC
  LIMIT 1
) x ON true
WHERE p.activo = true
AND p.desc_producto IS NOT NULL
AND btrim(p.desc_producto) <> ''
AND char_length(btrim(p.desc_producto)) >= 3

-- Regla de catálogo:
-- 1) alcohólicos reales por graduaje
-- 2) excepciones no alcohólicas por sub-familia (ej energéticas)
-- 3) respaldo por regex (si graduaje está malo)
AND (
    COALESCE(p.graduaje, 0) > 0
    OR p.cod_sub_familia = ANY(%(non_alc_subs)s)
    OR p.cod_sub_familia = ANY(%(cat_subs)s)
    OR p.cod_tipo_producto = ANY(%(cat_tipos)s)
    OR p.desc_producto ~* %(include_regex)s
)

-- Excluir cosas que no son del catálogo, pero sin matar las excepciones (energéticas, etc.)
AND (
    NOT (p.desc_producto ~* %(exclude_regex)s)
    OR p.cod_sub_familia = ANY(%(non_alc_subs)s)
    OR p.desc_producto ~* 'ENERGET'
)
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
        cat_subs, cat_tipos = _fetch_catalog_sets(inte)

        # Debug útil: cuántas LP existen realmente (ya NO filtramos por un set fijo)
        with inte.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(DISTINCT cod_lp_vendedor) AS n
                FROM ventas.detalle_lp_vendedor
                WHERE p_base >= %(min_price)s;
                """,
                {"min_price": MIN_PRICE},
            )
            n_lps = int(cur.fetchone()["n"])

        with inte.cursor() as cur:
            cur.execute(
                SQL,
                {
                    "include_regex": INCLUDE_REGEX,
                    "exclude_regex": EXCLUDE_REGEX,
                    "min_price": MIN_PRICE,
                    "non_alc_subs": _safe_any_list(NON_ALC_SUBS),
                    "cat_subs": _safe_any_list(cat_subs),
                    "cat_tipos": _safe_any_list(cat_tipos),
                },
            )
            rows = cur.fetchall()

    print(f"LP detectadas (>= min_price): {n_lps}")
    print(f"Filas desde INTEGRA: {len(rows)}")

    with psycopg.connect(**EXT, row_factory=dict_row) as ext:
        with ext.cursor() as cur:
            for r in rows:
                cur.execute(UPSERT, r)
        ext.commit()

    print("OK: cache actualizado.")

if __name__ == "__main__":
    main()