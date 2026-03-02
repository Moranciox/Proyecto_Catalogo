# Pack: Paginación + Búsqueda global (server-side) + Inactivos (opcional)

Este pack NO puede sobrescribir tu repo automáticamente porque aquí no tengo acceso al árbol completo de archivos.
Pero está preparado para que lo pegues en tu proyecto con cambios mínimos.

## Objetivo
- Quitar el límite fijo (200) y poder **ver todos** los productos usando **paginación** (infinite scroll).
- Que el buscador **busque en toda la base** (no solo en lo ya cargado).
- (Opcional) incluir `include_inactive` para ver productos desactivados.

## Backend (FastAPI + psycopg)
Archivos:
- `backend/app/products_paged.py`  -> router con GET /products paginado + búsqueda `q`

### Cómo integrarlo (rápido)
1) Copia `backend/app/products_paged.py` dentro de tu backend, en una ruta similar.
2) En tu `main.py` (o donde creas FastAPI), agrega:

```python
from backend.app.products_paged import router as products_router
app.include_router(products_router)
```

(si tu estructura es `app/` en vez de `backend/app/`, ajusta el import)

### Parámetros del endpoint
GET /products
- `page` (default 1)
- `page_size` (default 50, max 200)
- `q` (opcional) -> busca por nombre o código exacto
- `include_inactive` (default false)

Respuesta:
{
  "items": [...],
  "page": 1,
  "page_size": 50,
  "total": 1234
}

### Nota sobre `lp`
Como me dijiste que `lp=7` era solo un ejemplo:
- El endpoint acepta `lp` opcionalmente, pero **si no viene**, usa `DEFAULT_LP` del .env (si existe) o 7.
- Si en tu BD realmente NO necesitas LP, puedes eliminar ese filtro en SQL.

## Android (Compose)
Incluye ejemplos listos para copiar (con package placeholder):
- `android/README_ANDROID/` trae código de ejemplo para:
  - DTO de página
  - Repository
  - ViewModel con debounce y paginación manual
  - Pantalla Compose con infinite scroll (LazyVerticalGrid)

### Integración
- Copia los archivos Kotlin a tu `android/app/src/main/java/<tu/package>/...`
- Reemplaza `YOUR_PACKAGE` por tu package real.
- Asegúrate de que tu API base siga apuntando a `http://10.0.2.2:8080`

## Si quieres que te lo deje 100% "descargar y reemplazar"
Sube aquí un ZIP de tu repo (o al menos las carpetas `android/` y `backend/`) y te lo devuelvo con:
- rutas exactas
- imports correctos
- compilando sin tocar nada
