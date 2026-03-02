from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import anyio

from .settings import settings
from .schemas import ProductOut, ProductExtraIn, ProductExtraOut
from .db import (
    ensure_ext_schema,
    fetch_products_from_cache,
    health_check_deep,
    fetch_extras_for_products,
    get_product_extra,
    upsert_product_extra,
)

app = FastAPI(title="Catálogo Viña Aromo API", version="1.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # No fatal si EXT no está disponible
    await anyio.to_thread.run_sync(ensure_ext_schema)


@app.get("/health")
async def health(deep: bool = Query(False)):
    if not deep:
        return {"ok": True}

    status = await anyio.to_thread.run_sync(health_check_deep)
    return {"ok": True, "db": status}


@app.get("/products", response_model=list[ProductOut])
async def products(
    q: str | None = Query(None),
    include_inactive: bool = Query(False, description="Si true, incluye productos desactivados (EXT)."),
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    rows = await anyio.to_thread.run_sync(fetch_products_from_cache, limit, offset, q)

    cods = [int(r["cod_producto"]) for r in rows]
    extras = await anyio.to_thread.run_sync(fetch_extras_for_products, cods)

    out: list[ProductOut] = []
    for r in rows:
        cod = int(r["cod_producto"])
        ex = extras.get(cod, {})

        is_active = bool(ex.get("is_active", True))
        if (not include_inactive) and (not is_active):
            continue

        out.append(
            ProductOut(
                cod_producto=cod,
                desc_producto=r["desc_producto"],
                precio_neto=float(r["precio_neto"]),
                image_filename=ex.get("image_filename"),
                is_featured=bool(ex.get("is_featured", False)),
                is_active=is_active,
                sort_order=ex.get("sort_order"),
                notes=ex.get("notes"),
            )
        )

    return out


@app.get("/product-extra/{cod_producto}", response_model=ProductExtraOut)
async def product_extra(cod_producto: int):
    r = await anyio.to_thread.run_sync(get_product_extra, cod_producto)
    if r is None:
        raise HTTPException(status_code=404, detail="No existe extra o no hay conexión a EXT")

    return ProductExtraOut(
        cod_producto=int(r["cod_producto"]),
        image_filename=r["image_filename"],
        is_featured=bool(r["is_featured"]),
        is_active=bool(r.get("is_active", True)),
        sort_order=r["sort_order"],
        notes=r["notes"],
    )


@app.put("/product-extra/{cod_producto}", response_model=ProductExtraOut)
async def put_product_extra(cod_producto: int, body: ProductExtraIn):
    updated = await anyio.to_thread.run_sync(
        upsert_product_extra,
        cod_producto,
        body.model_dump(exclude_unset=True),
    )

    return ProductExtraOut(
        cod_producto=int(updated["cod_producto"]),
        image_filename=updated["image_filename"],
        is_featured=bool(updated["is_featured"]),
        is_active=bool(updated.get("is_active", True)),
        sort_order=updated["sort_order"],
        notes=updated["notes"],
    )
