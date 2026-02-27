import psycopg
from psycopg.rows import dict_row
from typing import Any, Optional
from .settings import settings

def _connect_integra():
    return psycopg.connect(
        host=settings.INTEGRA_PG_HOST,
        port=settings.INTEGRA_PG_PORT,
        dbname=settings.INTEGRA_PG_NAME,
        user=settings.INTEGRA_PG_USER,
        password=settings.INTEGRA_PG_PASSWORD,
        row_factory=dict_row,
        connect_timeout=5,
    )

def _connect_ext():
    return psycopg.connect(
        host=settings.EXT_PG_HOST,
        port=settings.EXT_PG_PORT,
        dbname=settings.EXT_PG_NAME,
        user=settings.EXT_PG_USER,
        password=settings.EXT_PG_PASSWORD,
        row_factory=dict_row,
        connect_timeout=5,
    )

def health_check_deep() -> dict:
    out = {"integra": False, "ext": False}
    try:
        with _connect_integra() as c:
            with c.cursor() as cur:
                cur.execute("select 1;")
                cur.fetchone()
        out["integra"] = True
    except Exception:
        out["integra"] = False

    try:
        with _connect_ext() as c:
            with c.cursor() as cur:
                cur.execute("select 1;")
                cur.fetchone()
        out["ext"] = True
    except Exception:
        out["ext"] = False

    return out

def ensure_ext_schema() -> None:
    # No levantes excepción fatal; si EXT no está disponible, el backend igual parte.
    sql = """
    CREATE SCHEMA IF NOT EXISTS catalog;

    CREATE TABLE IF NOT EXISTS catalog.product_extra (
      cod_producto      integer PRIMARY KEY,
      image_filename    text,
      is_featured       boolean NOT NULL DEFAULT false,
      sort_order        integer,
      notes             text,
      updated_at        timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_product_extra_featured
      ON catalog.product_extra (is_featured);

    CREATE INDEX IF NOT EXISTS idx_product_extra_sort
      ON catalog.product_extra (sort_order);
    """
    try:
        with _connect_ext() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
    except Exception:
        # EXT no disponible; se manejará por endpoint
        return

def fetch_products_from_integra(lp: int, q: Optional[str] = None):
    where_extra = ""
    params: dict[str, Any] = {"lp": lp}
    if q and q.strip():
        where_extra = " AND p.desc_producto ILIKE %(q)s "
        params["q"] = f"%{q.strip()}%"

    sql = f"""
    SELECT
        p.cod_producto,
        p.desc_producto,
        d.p_base AS precio_neto
        FROM comun.producto p
        JOIN LATERAL (
        SELECT d.p_base
        FROM ventas.detalle_lp_vendedor d
        WHERE d.cod_producto = p.cod_producto
            AND d.cod_lp_vendedor = %(lp)s
            AND d.p_base > 0
        ORDER BY d.inserttime DESC NULLS LAST,
                d.cod_detalle_lp_vendedor DESC
        LIMIT 1
        ) d ON true
        WHERE p.activo = true
    {where_extra}
    ORDER BY p.desc_producto;
    """

    with _connect_integra() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def fetch_extras_for_products(cods: list[int]) -> dict[int, dict]:
    if not cods:
        return {}
    try:
        with _connect_ext() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT cod_producto, image_filename, is_featured, sort_order, notes
                    FROM catalog.product_extra
                    WHERE cod_producto = ANY(%(cods)s);
                    """,
                    {"cods": cods},
                )
                rows = cur.fetchall()
        extras = {}
        for r in rows:
            extras[int(r["cod_producto"])] = {
                "image_filename": r["image_filename"],
                "is_featured": bool(r["is_featured"]),
                "sort_order": r["sort_order"],
                "notes": r["notes"],
            }
        return extras
    except Exception:
        return {}

def get_product_extra(cod_producto: int):
    try:
        with _connect_ext() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT cod_producto, image_filename, is_featured, sort_order, notes
                    FROM catalog.product_extra
                    WHERE cod_producto = %(cod)s;
                    """,
                    {"cod": cod_producto},
                )
                return cur.fetchone()
    except Exception:
        return None

def upsert_product_extra(cod_producto: int, data: dict):
    ensure_ext_schema()
    sql = """
    INSERT INTO catalog.product_extra (cod_producto, image_filename, is_featured, sort_order, notes, updated_at)
    VALUES (%(cod)s, %(image_filename)s, COALESCE(%(is_featured)s, false), %(sort_order)s, %(notes)s, now())
    ON CONFLICT (cod_producto) DO UPDATE SET
      image_filename = COALESCE(EXCLUDED.image_filename, catalog.product_extra.image_filename),
      is_featured = COALESCE(EXCLUDED.is_featured, catalog.product_extra.is_featured),
      sort_order = COALESCE(EXCLUDED.sort_order, catalog.product_extra.sort_order),
      notes = COALESCE(EXCLUDED.notes, catalog.product_extra.notes),
      updated_at = now()
    RETURNING cod_producto, image_filename, is_featured, sort_order, notes;
    """
    params = {
        "cod": cod_producto,
        "image_filename": data.get("image_filename"),
        "is_featured": data.get("is_featured"),
        "sort_order": data.get("sort_order"),
        "notes": data.get("notes"),
    }
    with _connect_ext() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

def fetch_products_from_cache(limit: int = 200, offset: int = 0, q: str | None = None):
    where = ""
    params = {"limit": limit, "offset": offset}
    if q and q.strip():
        where = "WHERE desc_producto ILIKE %(q)s"
        params["q"] = f"%{q.strip()}%"

    sql = f"""
    SELECT cod_producto, desc_producto, precio_neto, lp_usada
    FROM catalog.product_catalog_cache
    {where}
    ORDER BY desc_producto
    LIMIT %(limit)s OFFSET %(offset)s;
    """

    with _connect_ext() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()