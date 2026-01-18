# Catálogo de KPIs - Servicio al Usuario

Este catálogo sigue buenas prácticas DAMABOK para definición de métricas: nombre, fórmula, utilidad, owner, frecuencia y fuente.

| KPI | Fórmula | Utilidad | Owner | Frecuencia | Fuente |
|---|---|---|---|---|---|
| Total de solicitudes | `total_requests` | Medir demanda y carga operativa. | Jefe de Operaciones de Atención | Mensual / Lifetime | `data/gold/dashboard_reclamos.parquet` |
| Solicitudes abiertas | `open_requests` | Monitorear backlog y presión operativa. | Coordinador de Mesa de Ayuda | Mensual / Lifetime | Gold |
| Tasa de cierre | `closed_requests / total_requests` | Medir efectividad de cierre. | Supervisor de Atención | Mensual / Lifetime | Gold |
| Incumplimiento de SLA | `sla_breach_count / total_requests` | Control de tiempos y cumplimiento. | Responsable de Calidad | Mensual / Lifetime | Gold |
| Tiempo medio de resolución | `avg_resolution_hours` | Eficiencia en la atención. | Jefe de Operaciones | Mensual / Lifetime | Gold |
| Mediana de resolución | `median_resolution_hours` | Tiempo típico sin sesgo de outliers. | Responsable de Mejora Continua | Mensual / Lifetime | Gold |
| P90 resolución | `p90_resolution_hours` | Identificar casos extremos. | Responsable de Mejora Continua | Mensual / Lifetime | Gold |
| Satisfacción promedio | `avg_satisfaction` | Calidad percibida por el ciudadano. | Responsable de Experiencia del Usuario | Mensual / Lifetime | Gold |
| Alta satisfacción | `high_satisfaction_count / total_requests` | % de atenciones con score alto. | Responsable de Experiencia del Usuario | Mensual / Lifetime | Gold |
| Tasa alta prioridad | `high_priority_count / total_requests` | Carga de casos críticos. | Supervisor de Atención | Mensual / Lifetime | Gold |
| Costo total | `total_cost_soles` | Impacto económico por categoría/mes. | Responsable Administrativo | Mensual / Lifetime | Gold |
| Costo promedio | `avg_cost_soles` | Comparar eficiencia de atención. | Responsable Administrativo | Mensual / Lifetime | Gold |
| Backlog rate | `open_requests / total_requests` | Presión operativa relativa. | Coordinador de Mesa de Ayuda | Mensual / Lifetime | Gold |
| Casos cerrados por alto impacto | `closed_requests * high_priority_rate` | Enfoque en casos críticos cerrados. | Supervisor de Atención | Mensual / Lifetime | Derivado Gold |
| Tasa de satisfacción alta por cerrados | `high_satisfaction_count / closed_requests` | Calidad percibida en casos cerrados. | Responsable de Experiencia del Usuario | Mensual / Lifetime | Derivado Gold |
| Costo por solicitud | `total_cost_soles / total_requests` | Eficiencia de gasto por caso. | Responsable Administrativo | Mensual / Lifetime | Derivado Gold |
| Costo por caso cerrado | `total_cost_soles / closed_requests` | Coste real de atención completada. | Responsable Administrativo | Mensual / Lifetime | Derivado Gold |
| Tiempo medio en días | `avg_resolution_hours / 24` | Lectura ejecutiva en días. | Jefe de Operaciones | Mensual / Lifetime | Derivado Gold |
