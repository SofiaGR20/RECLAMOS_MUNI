# Plan detallado para Dashboard (Streamlit) - Atención al Cliente

## Objetivo
Construir un dashboard en Streamlit para el área de Servicio al Cliente que permita monitorear desempeño, calidad de atención y cumplimiento de SLA usando `data/gold/dashboard_reclamos.parquet`.

## Fuente de datos
- Gold: `data/gold/dashboard_reclamos.parquet`
- Grano: mensual + lifetime (`is_lifetime = 1`)

## Estructura de datos (Gold)
Columnas clave disponibles:
- Dimensiones: `year`, `month`, `month_start`, `category`, `request_type`, `channel`, `status`, `priority`, `department`, `province`, `district`, `office_id`, `office_name`, `categoria_principal`, `is_lifetime`
- Métricas: `total_requests`, `closed_requests`, `open_requests`, `sla_breach_count`, `avg_resolution_hours`, `median_resolution_hours`, `p90_resolution_hours`, `avg_satisfaction`, `high_satisfaction_count`, `total_cost_soles`, `avg_cost_soles`, `high_priority_count`, `closure_rate`, `sla_breach_rate`, `high_satisfaction_rate`, `high_priority_rate`

## KPIs más relevantes (Servicio al Cliente)
Documentar cada KPI con fórmula, utilidad y owner.

### KPIs de volumen y carga
1) **Total de solicitudes**
   - Fórmula: `total_requests`
   - Utilidad: mide demanda y carga operativa.
   - Owner: Jefe de Operaciones de Atención.

2) **Solicitudes abiertas**
   - Fórmula: `open_requests`
   - Utilidad: backlog actual y presión operativa.
   - Owner: Coordinador de Mesa de Ayuda.

### KPIs de desempeño y SLA
3) **Tasa de cierre**
   - Fórmula: `closure_rate = closed_requests / total_requests`
   - Utilidad: efectividad de cierre.
   - Owner: Supervisor de Atención.

4) **Incumplimiento de SLA**
   - Fórmula: `sla_breach_rate = sla_breach_count / total_requests`
   - Utilidad: control de tiempos y cumplimiento.
   - Owner: Responsable de Calidad.

5) **Tiempo medio de resolución**
   - Fórmula: `avg_resolution_hours`
   - Utilidad: eficiencia en la atención.
   - Owner: Jefe de Operaciones.

6) **Percentil 90 de resolución**
   - Fórmula: `p90_resolution_hours`
   - Utilidad: detectar casos extremos.
   - Owner: Responsable de Mejora Continua.

### KPIs de satisfacción
7) **Satisfacción promedio**
   - Fórmula: `avg_satisfaction`
   - Utilidad: calidad percibida por el ciudadano.
   - Owner: Responsable de Experiencia del Cliente.

8) **Tasa de alta satisfacción**
   - Fórmula: `high_satisfaction_rate = high_satisfaction_count / total_requests`
   - Utilidad: porcentaje de atenciones con score alto.
   - Owner: Responsable de Experiencia del Cliente.

### KPIs de prioridad y criticidad
9) **Tasa de alta prioridad**
   - Fórmula: `high_priority_rate = high_priority_count / total_requests`
   - Utilidad: carga de casos críticos.
   - Owner: Supervisor de Atención.

### KPIs de costos
10) **Costo total**
   - Fórmula: `total_cost_soles`
   - Utilidad: impacto económico por categoría/mes.
   - Owner: Responsable Administrativo.

11) **Costo promedio**
   - Fórmula: `avg_cost_soles`
   - Utilidad: comparar eficiencia de atención.
   - Owner: Responsable Administrativo.

## Dashboard (diseño y secciones)
### 1) Encabezado de estado
- KPIs principales: Total solicitudes, Tasa de cierre, Incumplimiento SLA, Tiempo medio, Satisfacción promedio.

### 2) Tendencias mensuales
- Serie temporal de `total_requests`, `closure_rate`, `sla_breach_rate`.

### 3) Análisis por categoría y canal
- Barras por `category` y `channel` con volumen y SLA.

### 4) Análisis geográfico
- Ranking por `department`, `province`, `district`.

### 5) Prioridades y backlog
- Distribución por `priority` y `status`.

### 6) Lifetime (histórico completo)
- Tabla resumen con `is_lifetime = 1`.

## Pipeline paso a paso (Streamlit)
1) Cargar `dashboard_reclamos.parquet`.
2) Separar datos mensuales (`is_lifetime=0`) y lifetime (`is_lifetime=1`).
3) Crear filtros globales (año, mes, categoría, canal, oficina, ubicación).
4) Calcular KPIs para el rango filtrado.
5) Renderizar visualizaciones (líneas, barras, tablas, tarjetas KPI).
6) Exportar tablas filtradas (CSV).

## Documentación de KPIs (DAMABOK)
- Mantener catálogo de KPIs en `docs/kpi_catalog.md` con:
  - Nombre, fórmula, definición, utilidad, owner, frecuencia de actualización, fuente de datos.

## Entregables
- App Streamlit: `pipelines/dashboard/app.py`
- Documentación KPI: `docs/kpi_catalog.md`
- Guía de uso: `docs/dashboard_guide.md`

## Preguntas abiertas
- ¿SLA oficial sigue siendo 72h?
- ¿Qué filtros deben ser obligatorios?
- ¿Quién valida la definición de "caso cerrado"?
