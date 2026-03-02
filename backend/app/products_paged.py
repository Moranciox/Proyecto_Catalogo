"""
Router FastAPI: /products paginado + búsqueda global (server-side)

Requisitos:
- fastapi
- psycopg[binary]

Asume 2 conexiones (INTEGRA y EXT) como describe tu README:
- INTEGRA: comun.producto + ventas.detalle_lp_vendedor (precio = p_base)
- EXT: extras (imagen, destacado, activo, notas, etc.)

⚠️ Ajusta nombres de schemas/tablas si difieren en tu BD real.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import psycopg
from fastapi import APIRouter, Query
from psycopg.rows import dict_row


router = APIRouter()


# -----------------------
# DB helpers
# -----------------------
@dataclass(frozen=True)
class PgCfg:
    host: str
    port: int
    db: str
    user: str
    password: str


def _env_cfg(prefix: str) -> PgCfg:
    return PgCfg(
        host=os.getenv(f"{prefix}_PG_HOST", "localhost"),
        port=int(os.getenv(f"{prefix}_PG_PORT", "5432")),
        db=os.getenv(f"{prefix}_PG_DB", ""),
        user=os.getenv(f"{prefix}_PG_USER", "postgres"),
        password=os.getenv(f"{prefix}_PG_PASSWORD", "postgres"),
    )


def _conn(cfg: PgCfg) -> psycopg.Connection:
    # autocommit porque solo leemos (y simplifica)
    return psycopg.connect(
        host=cfg.host,
        port=cfg.port,
        dbname=cfg.db,
        user=cfg.user,
        password=cfg.password,
        autocommit=True,
        row_factory=dict_row,
    )


INTEGRA = _env_cfg("INTEGRA")
EXT = _env_cfg("EXT")


def _default_lp() -> int:
    # Si no quieres usar LP, puedes ignorar esto y sacar el filtro lp.
    return int(os.getenv("DEFAULT_LP", "7"))


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


# -----------------------
# Endpoint
# -----------------------
@router.get("/products")
def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    lp: Optional[int] = Query(None, description="Opcional. Si no viene, se usa DEFAULT_LP o 7."),
) -> dict[str, Any]:
    """
    Devuelve productos en páginas y permite búsqueda server-side.
    - q: busca por nombre (ILIKE) o código exacto.
    - include_inactive: si false, filtra activo=true (en EXT).
    """
    lp_val = lp if lp is not None else _default_lp()

    # normalizamos q
    qn = (q or "").strip()
    q_param = qn if qn else None

    offset = (page - 1) * page_size

    # Nota: se lee desde INTEGRA y se LEFT JOIN a EXT por extras.
    # Ajusta nombres de tabla y columnas a tu realidad.
    count_sql = """
        SELECT COUNT(*) AS total
        FROM comun.producto p
        JOIN ventas.detalle_lp_vendedor pr
          ON pr.cod_producto = p.cod_producto
         AND pr.lp = %(lp)s
        LEFT JOIN producto_extra e
          ON e.cod_producto = p.cod_producto
        WHERE (%(include_inactive)s = TRUE OR COALESCE(e.activo, TRUE) = TRUE)
          AND (
              %(q)s IS NULL
              OR p.nombre ILIKE '%%' || %(q)s || '%%'
              OR CAST(p.cod_producto AS TEXT) = %(q)s
          )
    """

    data_sql = """
        SELECT
          p.cod_producto AS codigo,
          p.nombre AS nombre,
          pr.p_base AS precio_neto,
          e.image_url AS image_url,
          COALESCE(e.destacado, FALSE) AS destacado,
          COALESCE(e.activo, TRUE) AS activo,
          e.notas AS notas
        FROM comun.producto p
        JOIN ventas.detalle_lp_vendedor pr
          ON pr.cod_producto = p.cod_producto
         AND pr.lp = %(lp)s
        LEFT JOIN producto_extra e
          ON e.cod_producto = p.cod_producto
        WHERE (%(include_inactive)s = TRUE OR COALESCE(e.activo, TRUE) = TRUE)
          AND (
              %(q)s IS NULL
              OR p.nombre ILIKE '%%' || %(q)s || '%%'
              OR CAST(p.cod_producto AS TEXT) = %(q)s
          )
        ORDER BY p.nombre ASC, p.cod_producto ASC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    params = {
        "lp": lp_val,
        "include_inactive": include_inactive,
        "q": q_param,
        "limit": page_size,
        "offset": offset,
    }

    # 1) Total
    with _conn(INTEGRA) as c:
        with c.cursor() as cur:
            cur.execute(count_sql, params)
            total = int(cur.fetchone()["total"])

    # 2) Items
    with _conn(INTEGRA) as c:
        with c.cursor() as cur:
            cur.execute(data_sql, params)
            items = cur.fetchall()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
