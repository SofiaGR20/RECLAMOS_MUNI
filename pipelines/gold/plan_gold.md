# Plan detallado para Gold (dashboard de desempeño)

## Objetivo
Construir un dataset Gold único (un solo Parquet) optimizado para dashboards de desempeño de reclamos/solicitudes por categorías, canales, ubicación y tiempo, con métricas mensuales y métricas lifetime.

## Entradas
- `data/silver/solicitudes_ciudadanas.parquet`
- `data/silver/oficinas.parquet`

## Salida Gold
- `data/gold/dashboard_reclamos.parquet` (archivo único, sin particionado)

## Diseño del dataset Gold
Dataset **denormalizado** para BI con **grano mensual** y métricas agregadas por dimensiones clave.

**Grano**:
- `year` + `month` + (`category`, `request_type`, `channel`, `status`, `priority`, `department`, `province`, `district`, `office_id`, `categoria_principal`)

Además, filas **lifetime** (todo el histórico) con las mismas dimensiones y `is_lifetime = 1`.

### Dimensiones (columnas)
- Tiempo: `year`, `month`, `month_start`, `is_lifetime`.
- Categorías: `category`, `subcategory`, `request_type`.
- Canal/estado: `channel`, `status`, `priority`.
- Ubicación: `department`, `province`, `district`.
- Oficina: `office_id`, `office_name`, `categoria_principal`.

### Métricas para dashboard (accionables)
- Volumen: `total_requests`.
- Cierre: `closed_requests`, `open_requests`, `closure_rate`.
- SLA: `sla_breach_count`, `sla_breach_rate` (umbral 72h).
- Tiempo: `avg_resolution_hours`, `median_resolution_hours`, `p90_resolution_hours`.
- Satisfacción: `avg_satisfaction`, `high_satisfaction_rate` (>=4).
- Costos: `total_cost_soles`, `avg_cost_soles`.
- Prioridad: `high_priority_rate` (`priority` in {alta, critica}).

### Métricas lifetime
Las mismas métricas anteriores pero con `is_lifetime = 1`, `year = 0`, `month = 0`, `month_start = null`.

## Reglas de limpieza específicas para Gold
- `status` fuera de catálogo → `otros`.
- `category`, `channel`, `priority`, `request_type`, `department`, `province`, `district` nulos → `desconocido`.
- `resolution_hours` negativo → nulo.
- `cost_soles` negativo → se convierte a valor absoluto.
- `created_at` nulo → excluir del agregado mensual (solo lifetime si aplica).
- `satisfaction_rating` fuera de rango → nulo (se revalida).

## Pipeline paso a paso
1) **Lectura Silver**: cargar solicitudes y oficinas.
2) **Join**: left join por `office_id`.
3) **Normalización Gold**:
   - Mapear categorías y estados desconocidos.
   - Tipos consistentes (numéricos y categóricos).
4) **Calendario**:
   - Derivar `year`, `month` y `month_start` desde `created_at`.
5) **Agregación mensual**:
   - Agrupar por grano definido y calcular métricas.
6) **Agregación lifetime**:
   - Agrupar por mismas dimensiones sin tiempo.
   - Agregar `is_lifetime = 1`, `year=0`, `month=0`.
7) **Unión final**:
   - Concatenar mensual + lifetime.
8) **Validaciones Gold**:
   - Conteos de filas.
   - Revisión de métricas clave y nulos.
9) **Escritura Gold**:
   - Guardar en `data/gold/dashboard_reclamos.parquet`.

## Ejemplos de inconsistencias y tratamiento
- `status = 'cerrrado'` → `cerrado`.
- `status = ''` → `otros`.
- `priority = ''` → `desconocido`.
- `resolution_hours < 0` → nulo, no cuenta en promedios.
- `created_at = null` → no entra en mensual; sí en lifetime si tiene dimensiones válidas.

## Entregables
- `data/gold/dashboard_reclamos.parquet`
- Resumen de métricas (conteo, % nulos por dimensiones clave)

## Preguntas abiertas
- ¿Umbral SLA definitivo: 72h o distinto?
- ¿Filtrar `status='anulado'` del dashboard o incluirlo con su categoría?
- ¿Incluir `subcategory` en el grano o solo en filtros?
