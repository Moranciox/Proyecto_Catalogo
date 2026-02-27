# Proyecto Catálogo – Viña Aromo (desde 0)

Este zip trae una base **lista para copiar/pegar** con:
- `backend/` (VS Code): FastAPI + PostgreSQL (2 BDs)
  - **INTEGRA** (interna): lee `comun.producto` + `ventas.detalle_lp_vendedor` (precio = `p_base`)
  - **EXT** (local/external): guarda “extras” (imagen, destacados, orden, notas, etc.)
- `android/` (Android Studio): app Compose que consume `/products`

> Nota: el backend está hecho con `psycopg[binary]` para que funcione bien en Windows (sin compilar C como `asyncpg`).

## Quick start (Windows PowerShell)
1) Backend
```powershell
cd backend
./run_dev.ps1
```
2) Probar
- http://localhost:8080/health?deep=true
- http://localhost:8080/products?lp=7

3) Android
- Abrir carpeta `android/` en Android Studio
- (Emulador) la app apunta por defecto a `http://10.0.2.2:8080`

## Configuración
- `backend/.env` tiene:
  - INTEGRA_* (BD interna)
  - EXT_* (tu BD local/external)
  - CORS_ORIGINS

Si tu BD externa no está en localhost, cambia `EXT_PG_HOST`.

