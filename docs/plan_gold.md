# Plan detallado para Gold (dashboard de desempeño)

## Objetivo
Construir un dataset Gold único (un solo Parquet) optimizado para dashboards de desempeño de reclamos/solicitudes por categorías, canales, ubicación y tiempos.

## Entradas
- `data/silver/solicitudes_ciudadanas.parquet`
- `data/silver/oficinas.parquet`

## Salida Gold
- `data/gold/dashboard_reclamos.parquet` (archivo único, sin particionado)

## Diseño del dataset Gold
Dataset **denormalizado** para análisis rápido en BI:
- Unir solicitudes con oficinas por `office_id`.
- Conservar campos clave y derivar métricas de desempeño.
- Agregar columnas de calendario para filtros (año, mes, semana) sin cambiar las fechas base.

### Campos base sugeridos
- Identificadores: `request_id`, `citizen_id`, `office_id`.
- Dimensiones: `request_type`, `category`, `subcategory`, `channel`, `status`, `priority`.
- Ubicación: `department`, `province`, `district`.
- Tiempo: `created_at`, `closed_at` (date `YYYY-MM-DD`), `year`, `month`, `week`.
- Métricas: `resolution_hours`, `cost_soles`, `satisfaction_rating`.
- Oficina: `office_name`, `categoria_principal`.

## Transformaciones Gold (pasos)
1) **Lectura Silver**
   - Cargar `solicitudes_ciudadanas.parquet` y `oficinas.parquet`.

2) **Join y normalización**
   - Left join por `office_id`.
   - Verificar integridad: `office_id` sin match → `office_name` nulo.

3) **Dimensiones y calendarios**
   - Crear `year`, `month`, `week` a partir de `created_at` (solo fecha).
   - Mantener `created_at`/`closed_at` sin hora.

4) **Métricas de desempeño**
   - `is_closed`: 1 si `status == 'cerrado'`, 0 caso contrario.
   - `resolution_days`: `resolution_hours / 24` (redondeado a 2 decimales).
   - `sla_breach`: 1 si `resolution_hours` > umbral (definir, p.ej. 72h), 0 si no.

5) **Limpieza final (Gold debe ser lo más limpio posible)**
   - Eliminar columnas no útiles para dashboard (contacto, lat/lon si no se usan).
   - Asegurar tipos consistentes y nulos controlados.
   - Filtrar registros sin `request_id`.

6) **Validaciones Gold**
   - Conteo de filas pre/post.
   - Distribuciones por `status`, `category`, `channel`.
   - Métricas de completitud en dimensiones clave.

7) **Escritura Gold**
   - Guardar en `data/gold/dashboard_reclamos.parquet`.

## Reglas claras (ejemplos de inconsistencias y cómo se tratan)
- `status` fuera de catálogo → mantener como `otros`.
- `resolution_hours` negativo → nulo.
- `created_at` nulo → `year=0`, `month=0`, `week=0` (o eliminar si se decide).

## Entregables
- `data/gold/dashboard_reclamos.parquet`
- Log/resumen de métricas (conteos, % nulos por dimensión clave).

## Próximo paso
- Implementar `pipelines/gold/transform.py` y ejecutar.
