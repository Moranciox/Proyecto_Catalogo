# Backend (VS Code) – FastAPI + PostgreSQL (INTEGRA + EXT)

## Endpoints
- `GET /health` (rápido)
- `GET /health?deep=true` (prueba conexión a INTEGRA y EXT)
- `GET /products?q=<texto opcional>&featured_only=<true|false>&include_inactive=<true|false>&min_price=<n>`
- `GET /product-extra/<cod_producto>`
- `PUT /product-extra/<cod_producto>` (upsert)

## Tabla en BD externa (EXT)
Se crea automáticamente si existe la conexión. También puedes ejecutar:
- `scripts/01_ext_schema.sql`

## Semilla (opcional)
Para crear una fila en `catalog.product_extra` por cada producto activo:
```powershell
python scripts/seed_product_extra.py
```

## Cache de catálogo (recomendado)
Para acelerar búsqueda y filtrar productos "reales", se construye un cache en EXT:
```powershell
python scripts/build_catalog_cache.py
```

Reglas clave:
- Descarta nombres vacíos
- Descarta precios muy bajos (configurable con `CATALOG_MIN_PRICE`)
- Incluye alcohólicos por `graduaje > 0`
- Incluye excepciones no alcohólicas por `NON_ALCOHOL_SUBFAMILIAS` (ej: energéticas)

