# Trabajo Final - Gestion y Gobierno de Datos (UPC)

Autor: Sofia German Riofrio
GitHub: https://github.com/SofiaGR20

Este repositorio corresponde al trabajo final del curso de Gestion y Gobierno de Datos de la UPC. El objetivo es realizar un proceso de limpieza de datos y atravesar todas las etapas del esquema Medallion (Bronze -> Silver -> Gold) utilizando datos reales del repositorio.

## Alcance del trabajo

Se trabajara con los siguientes archivos ubicados en la capa Bronze:

- `C:\Users\Sofia\Desktop\evaluacion_final\data\bronze\oficinas.csv`
- `C:\Users\Sofia\Desktop\evaluacion_final\data\bronze\solicitudes_ciudadanas.csv`

## Estructura del repositorio (esperada)

- `data\`
  - `bronze\`
    - `oficinas.csv`
    - `solicitudes_ciudadanas.csv`
    Archivos de entrada originales (sin transformaciones).
  - `silver\`
    Salidas limpias y estandarizadas (sin duplicados, con tipos consistentes).
  - `gold\`
    Salidas curadas y listas para analisis o consumo.
- `pipeline\`
  Carpeta del pipeline (a crear). Contendra scripts/notebooks, configuracion y orquestacion.
- `docs\`
  Documentacion tecnica (a crear): diccionarios de datos, reglas, decisiones y pruebas.
- `README.md`
  Descripcion del trabajo, pasos generales y criterios de calidad.

## Flujo de trabajo detallado

### 1) Bronze (ingesta y validacion)

- Verificar columnas y tipos esperados en ambos CSV.
- Revisar valores nulos, duplicados y formatos inconsistentes.
- Mantener los archivos en su forma original como fuente de verdad.
- Registrar metadatos basicos (fecha de ingesta, fuente, responsable).

### 2) Silver (limpieza y estandarizacion)

Aplicar transformaciones como:

- Normalizacion de nombres de columnas.
- Limpieza de espacios, caracteres extra, y formatos de texto.
- Conversion de tipos (fechas, numericos, codigos).
- Tratamiento de nulos y duplicados con reglas definidas.
- Validaciones basicas de rango y valores permitidos.

Resultado esperado: datos confiables, coherentes y preparados para analisis.

### 3) Gold (curado y enriquecido)

Aplicar reglas de negocio y consolidaciones:

- Unificacion de claves entre tablas si corresponde.
- Agregaciones o resumenes para indicadores.
- Dataset final listo para reportes o visualizacion.
- Versionado logico de salidas (por fecha o periodo).

## Como ejecutar (guia general)

1. Ubicar los archivos fuente en `data\bronze\`.
2. Ejecutar el proceso de limpieza para generar `data\silver\`.
3. Ejecutar el proceso de curado para generar `data\gold\`.
4. Validar resultados (conteos, consistencia, reglas de negocio).
5. Documentar cambios y supuestos en este README.

### Placeholder de ejecucion

Pendiente de definir cuando el pipeline este implementado. Ejemplo esperado:

```sh
# Ejemplo (a definir)
# python pipeline/run.py --date YYYY-MM-DD --stage all
```

## Pipeline (planificado)

Se creara un pipeline reproducible para ejecutar el flujo Medallion de extremo a extremo.
La idea es separar ingesta, limpieza, validaciones y curado en etapas claras, con logs
y control de versiones de salidas por fecha de ejecucion.

Componentes previstos:

- Ingesta: lectura de archivos Bronze, registro de metadatos y versionado.
- Transformacion Silver: limpieza, estandarizacion y reglas de calidad.
- Transformacion Gold: reglas de negocio, agregaciones e indicadores.
- Validaciones: conteos, nulos, duplicados y consistencia entre capas.
- Orquestacion: ejecucion por etapas, con salidas en carpetas fechadas.

Estructura sugerida del pipeline (a crear):

- `pipeline\ingest\`
- `pipeline\silver\`
- `pipeline\gold\`
- `pipeline\validation\`
- `pipeline\config\`

## Objetivo final

Entregar un flujo completo de tratamiento de datos siguiendo el esquema Medallion, demostrando buenas practicas de gestion y gobierno de datos.

## Criterios de calidad (propuestos)

- Trazabilidad: cada capa conserva el origen y transformaciones aplicadas.
- Consistencia: tipos y formatos uniformes en las columnas clave.
- Completitud: tratamiento explicito de valores nulos y faltantes.
- Integridad: reglas de duplicados y claves coherentes.
- Reproducibilidad: pasos claros para reejecutar el flujo.

## Entregables

- Dataset en capa Silver con datos limpios.
- Dataset en capa Gold con datos curados y listos para analisis.
- Documentacion del proceso (este README).

## Supuestos y decisiones

- Los archivos en Bronze se consideran la fuente original y no se modifican.
- Las reglas de limpieza se documentan y se aplican de forma consistente.
- Las salidas en Silver y Gold conservan trazabilidad a los datos de origen.

## Validaciones minimas

- Conteo de registros antes y despues de cada etapa.
- Porcentaje de valores nulos en campos clave.
- Duplicados detectados y criterio de resolucion.
- Reglas de negocio criticas verificadas.

## Convenciones recomendadas

- Nombres de columnas en minusculas y con guion bajo.
- Fechas en formato ISO `YYYY-MM-DD`.
- Codigos sin espacios y con longitud uniforme.
- Separador decimal y de miles consistente.

## Cambios en el tiempo

Registrar aqui las modificaciones relevantes al proceso:

- Fecha:
  - Cambio:
  - Motivo:

## Diccionario de datos (plantilla)

Completar esta tabla para cada dataset final (Silver y Gold).

| Campo | Descripcion | Tipo | Origen | Reglas/Transformaciones |
|------|-------------|------|--------|-------------------------|
|      |             |      |        |                         |
