# Plan detallado de análisis y limpieza (Bronze → Silver)

## Objetivo
Transformar `solicitudes_ciudadanas.csv` y `oficinas.csv` desde Bronze a Silver con reglas de limpieza y validaciones, manteniendo trazabilidad y sin particionar fechas.

## Alcance
- Fuente: `data/bronze/solicitudes_ciudadanas.csv`, `data/bronze/oficinas.csv`.
- Salida Silver: `data/silver/solicitudes_ciudadanas.parquet` y `data/silver/oficinas.parquet`.
- Implementación: Python (pandas), script en `pipelines/silver/transform.py`.

## Exploración inicial
- Conteo de filas y columnas.
- % de nulos por columna.
- Duplicados por `request_id` y `office_id`.
- Valores únicos de columnas categóricas.
- Chequeo de coherencia entre fechas (`closed_at` vs `created_at`).

## Reglas de limpieza (con ejemplos)
### Solicitudes
1) **Normalizar columnas**: minúsculas y `snake_case`.
2) **`request_id`**:
   - Trim + validar no nulo.
   - Duplicados: conservar el registro con `created_at` más reciente.
   - Ejemplo: `REQ-1000` duplicado → se mantiene el más nuevo.
3) **Fechas**:
   - Validar orden con parsing temporal y guardar solo la fecha (`YYYY-MM-DD`) en la salida.
   - Si `closed_at < created_at`, entonces `closed_at = nulo` y `resolution_hours = NaN`.
   - Ejemplo: `created_at=2024-07-12T02:00:00` → `2024-07-12`.
4) **`status`**:
   - Normalizar a minúsculas.
   - Corregir typo: `cerrrado` → `cerrado`.
5) **Categóricos** (`priority`, `channel`, `request_type`, `category`, `subcategory`, `department`, `province`, `district`):
   - Trim, minúsculas, vacíos → nulo.
6) **Numéricos** (`resolution_hours`, `cost_soles`, `satisfaction_rating`):
   - Convertir a numérico con `errors="coerce"`.
   - `satisfaction_rating` válido solo en [1,5]; fuera de rango → nulo.
7) **Geográficos** (`latitude`, `longitude`):
   - Convertir a float.
   - Rango Perú aprox.: lat [-19.5, -0.5], lon [-82.5, -68.0]; fuera de rango → nulo.
   - Ejemplo: `longitude=""` → nulo.
8) **Contacto**:
   - `contact_email`: trim y validación básica (regex simple); inválido → nulo.
   - `contact_phone`: mantener solo dígitos; válido si tiene **9 dígitos**; si no, → nulo.
   - Ejemplo: `"+51 912-345-678"` → `912345678`; `"12345"` → nulo.
9) **Integridad referencial**:
   - `office_id` debe existir en `oficinas`.
   - Si no existe, setear `office_id` a nulo (o `OF-UNK` si se decide crear catálogo).

### Oficinas
1) **Normalizar columnas**.
2) **`office_id`**:
   - No nulo y único.
   - Duplicados: mantener el primero.
3) **`categoria_principal`**:
   - Minúsculas; mapear `desconocida` → `otra`.
4) **Contacto**:
   - `telefono_contacto`: remover símbolos y dejar solo dígitos (sin validar 9 dígitos).
   - `email_contacto`: trim y validación básica.

## Fechas (sin particionado)
- No se particiona por año/mes.
- Se guarda solo la fecha (`YYYY-MM-DD`) en las columnas de fecha.

## Validaciones de salida (Silver)
- Conteo pre/post y % de nulos.
- Duplicados eliminados por clave.
- Distribución de `status`, `priority`, `category`.
- Integridad `office_id` entre tablas.
- Verificación de formato de fecha (`YYYY-MM-DD`).

## Reporte de calidad de datos (al ejecutar el script)
- Generar un reporte automático por tabla con:
  - Número y porcentaje de nulos por columna.
  - Número de duplicados por clave (`request_id`, `office_id`).
  - Outliers numéricos (p. ej. `resolution_hours`, `cost_soles`) usando IQR.
  - Valores fuera de rango (p. ej. `satisfaction_rating` fuera de [1,5], lat/lon fuera de Perú).
  - Registros con fechas inconsistentes (`closed_at < created_at`).
- Guardar el reporte como `data/silver/quality_report.json` y/o `data/silver/quality_report.md`.

## Entregables
- `data/silver/solicitudes_ciudadanas.parquet`.
- `data/silver/oficinas.parquet`.
- Log/resumen de limpieza (conteos y reglas aplicadas).

## Próximos pasos
- Implementar y ejecutar `pipelines/silver/transform.py`.
- Agregar pruebas de calidad en `pipelines/validation/`.

## Pasos detallados para crear el script (accionables)
1) Crear carpeta `pipelines/silver/` si no existe.
2) Crear archivo `pipelines/silver/transform.py`.
3) Definir constantes de rutas (`data/bronze`, `data/silver`) y listas de valores nulos.
4) Implementar funciones utilitarias:
   - `normalize_columns(df)` para estandarizar nombres.
   - `clean_string_series(s)` para trim y nulos.
   - `digits_only(value)` y validadores básicos (email, teléfono).
5) Implementar `clean_oficinas(df)` con reglas del plan.
6) Implementar `clean_solicitudes(df, oficinas_ids)` con reglas del plan.
7) Agregar deduplicación de `request_id` (por fecha y completitud).
8) Implementar escritura a Silver:
   - Parquet único por tabla (sin particionado).
   - Convertir fechas a `YYYY-MM-DD`.
10) Implementar generación de reporte de calidad:
   - Nulos por columna.
   - Duplicados por clave.
   - Outliers numéricos (IQR).
   - Fuera de rango (rating, lat/lon).
   - Fechas inconsistentes.
   - Guardar en `data/silver/quality_report.json` y/o `.md`.
11) Ejecutar el script y verificar salidas en `data/silver/`.

## Estado de avance (al 2026-01-18)
- Script Silver creado en `pipelines/silver/transform.py`.
- Ejecución realizada y salida Silver generada en `data/silver/`.
- Reporte de calidad generado en `data/silver/quality_report.json` y `.md`.
