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
    """Crea/actualiza la tabla de extras en EXT.

    Nota: No levanta excepción fatal; si EXT no está disponible, el backend igual parte.
    """

    sql = """
    CREATE SCHEMA IF NOT EXISTS catalog;

    CREATE TABLE IF NOT EXISTS catalog.product_extra (
        cod_producto integer PRIMARY KEY,
        image_filename text,
        is_featured boolean NOT NULL DEFAULT false,
        is_active boolean NOT NULL DEFAULT true,
        sort_order integer,
        notes text,
        updated_at timestamptz NOT NULL DEFAULT now()
    );

    -- Si la tabla existía antes, agrega la columna si falta.
    ALTER TABLE catalog.product_extra
        ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;

    CREATE INDEX IF NOT EXISTS idx_product_extra_featured
        ON catalog.product_extra (is_featured);

    CREATE INDEX IF NOT EXISTS idx_product_extra_active
        ON catalog.product_extra (is_active);

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
        ORDER BY d.inserttime DESC NULLS LAST, d.cod_detalle_lp_vendedor DESC
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
                    SELECT
                        cod_producto,
                        image_filename,
                        is_featured,
                        is_active,
                        sort_order,
                        notes
                    FROM catalog.product_extra
                    WHERE cod_producto = ANY(%(cods)s);
                    """,
                    {"cods": cods},
                )
                rows = cur.fetchall()

        extras: dict[int, dict] = {}
        for r in rows:
            extras[int(r["cod_producto"])] = {
                "image_filename": r["image_filename"],
                "is_featured": bool(r["is_featured"]),
                "is_active": bool(r["is_active"]) if r["is_active"] is not None else True,
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
                    SELECT
                        cod_producto,
                        image_filename,
                        is_featured,
                        is_active,
                        sort_order,
                        notes
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
    INSERT INTO catalog.product_extra (
        cod_producto,
        image_filename,
        is_featured,
        is_active,
        sort_order,
        notes,
        updated_at
    )
    VALUES (
        %(cod)s,
        %(image_filename)s,
        COALESCE(%(is_featured)s, false),
        COALESCE(%(is_active)s, true),
        %(sort_order)s,
        %(notes)s,
        now()
    )
    ON CONFLICT (cod_producto)
    DO UPDATE SET
        image_filename = COALESCE(EXCLUDED.image_filename, catalog.product_extra.image_filename),
        is_featured = COALESCE(EXCLUDED.is_featured, catalog.product_extra.is_featured),
        is_active = COALESCE(EXCLUDED.is_active, catalog.product_extra.is_active),
        sort_order = COALESCE(EXCLUDED.sort_order, catalog.product_extra.sort_order),
        notes = COALESCE(EXCLUDED.notes, catalog.product_extra.notes),
        updated_at = now()
    RETURNING
        cod_producto,
        image_filename,
        is_featured,
        is_active,
        sort_order,
        notes;
    """

    params = {
        "cod": cod_producto,
        "image_filename": data.get("image_filename"),
        "is_featured": data.get("is_featured"),
        "is_active": data.get("is_active"),
        "sort_order": data.get("sort_order"),
        "notes": data.get("notes"),
    }

    with _connect_ext() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def fetch_products_from_cache(
    limit: int | None = None,
    offset: int = 0,
    q: str | None = None,
    min_price: float | None = None,
):
    # Salvavidas: aunque el cache ya viene filtrado por script,
    # aplicamos reglas mínimas acá para evitar que se cuele basura.
    where_parts = [
        "desc_producto IS NOT NULL",
        "btrim(desc_producto) <> ''",
        "char_length(btrim(desc_producto)) >= 3",
        "precio_neto IS NOT NULL",
        "precio_neto >= %(min_price)s",
    ]
    eff_min_price = float(settings.CATALOG_MIN_PRICE) if min_price is None else float(min_price)
    params = {"offset": offset, "min_price": eff_min_price}

    if q and q.strip():
        where_parts.append("desc_producto ILIKE %(q)s")
        params["q"] = f"%{q.strip()}%"

    where = "WHERE " + " AND ".join(where_parts)

    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT %(limit)s"
        params["limit"] = limit

    sql = f"""
    SELECT cod_producto, desc_producto, precio_neto, lp_usada
    FROM catalog.product_catalog_cache
    {where}
    ORDER BY desc_producto
    {limit_clause}
    OFFSET %(offset)s;
    """

    with _connect_ext() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()