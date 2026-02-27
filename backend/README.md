# Backend (VS Code) – FastAPI + PostgreSQL (INTEGRA + EXT)

## Endpoints
- `GET /health` (rápido)
- `GET /health?deep=true` (prueba conexión a INTEGRA y EXT)
- `GET /products?lp=<cod_lp_vendedor>&q=<texto opcional>&featured_only=<true|false>`
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

