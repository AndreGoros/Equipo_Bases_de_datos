# Proyecto Final: Bases de Datos (COM-12101-2)

## Análisis del Comportamiento de Taxis en Chicago (2019-2022)

-----

## A) Introducción al Conjunto de Datos

Este repositorio utiliza un conjunto de datos público que contiene información detallada sobre 212 millones de viajes en taxi en la ciudad de Chicago. Cada registro incluye datos del trayecto, tiempos, ubicaciones aproximadas de origen y destino, costos y formas de pago. Este conjunto de datos fue recolectado por el gobierno de la ciudad de Chicago y publicado en su portal oficial de datos abiertos. El propósito de su recolección fue analizar tendencias de movilidad sin comprometer la privacidad de usuarios y conductores.

### Objetivo del Proyecto

El conjunto de datos original cubre el período de 2013 a 2023. Nuestro equipo lo utilizará con el objetivo de **analizar cómo cambió el comportamiento de los taxis antes, durante y después de la pandemia**.
Nos enfocaremos especialmente en los años 2019 a 2022, con el fin de identificar variaciones en la movilidad, precios y tendencias como pueden ser las propinas.

### Consideraciones Éticas

El análisis de este dataset debe hacerse con responsabilidad, teniendo presente que se trata de información sensible. Para ello, el proyecto se adhiere a los siguientes principios:

  * Respetar la privacidad de pasajeros y conductores.
  * Reconocer los sesgos inherentes en los datos.
  * Mantener transparencia metodológica en el análisis y en la comunicación de resultados.
  * Usar esta información únicamente con fines académicos y sociales, evitando aplicaciones que puedan resultar en discriminación o explotación comercial indebida.

### Atributos del Dataset

El conjunto de datos completo cuenta con 23 atributos:

  * **Identificadores y texto:** `trip_id`, `taxi_id`, `pickup_census_tract`, `dropoff_census_tract`
  * **Fechas y tiempos:** `trip_start_timestamp`, `trip_end_timestamp`
  * **Numéricos:** `trip_seconds`, `trip_miles`, `pickup_community_area`, `dropoff_community_area`, `fare`, `tips`, `tolls`, `extras`, `trip_total`, `pickup_centroid_latitude`, `pickup_centroid_longitude`, `dropoff_centroid_latitude`, `dropoff_centroid_longitude`
  * **Categóricos:** `payment_type`, `company`
  * **Geoespaciales:** `pickup_centroid_location`, `dropoff_centroid_location`

-----

## B) Carga Inicial 

Esta sección documenta el proceso de Ingesta, Transformación y Carga (ETL) para preparar los datos brutos para el análisis.

### 1\. Descarga y Filtrado Inicial

Primero, se descargó la base de datos como un archivo CSV desde el portal de datos de Chicago. Para optimizar el análisis, realizamos dos acciones en la descarga:

1.  **Selección de Columnas:** Nos quedamos solamente con las 12 columnas relevantes para nuestro objetivo: `trip_id`, `taxi_id`, `trip_start_timestamp`, `trip_end_timestamp`, `trip_miles`,  `pickup_community_area`, `dropoff_community_area`, `fare`, `tips`, `tolls`, `extras` y `trip_total`.
2.  **Filtrado de Fechas:** Aplicamos un filtro en el portal para descargar exclusivamente los registros del intervalo de años **2019 a 2022**.

### 2\. Estrategia de Carga (Staging)

Debido a que los datos brutos presentaban formatos inconsistentes (especialmente en fechas y valores monetarios), adoptamos un enfoque de "staging" (tabla de paso) para asegurar una carga limpia y sin errores.

**Paso 1: Creación de la Base de Datos**
Se utilizó `psql` (SQL Shell) para crear y conectarse a la base de datos del proyecto.

```sql
CREATE DATABASE proyecto_taxis;
\c proyecto_taxis
```

**Paso 2: Creación de la "Staging Table"**
Se creó una tabla `taxis_raw_text` donde todas las 12 columnas se definieron como tipo `TEXT`. Esto permite cargar cualquier dato en bruto, sin importar su formato.

```sql
CREATE TABLE taxis_raw_text (
    col1 TEXT,
    col2 TEXT,
    col3 TEXT,
    col4 TEXT,
    col5 TEXT,
    col6 TEXT,
    col7 TEXT,
    col8 TEXT,
    col9 TEXT,
    col10 TEXT,
    col11 TEXT,
    col12 TEXT
);
```

**Paso 3: Carga del CSV a la Staging Table**
Se usó el comando `\copy` para volcar el contenido del CSV en la tabla `taxis_raw_text`.

```sql
\copy taxis_raw_text FROM 'C:/Users/LARIG/OneDrive/Desktop/ITAM/Semestre_3/Bases_de_Datos/Taxi_Trips_(2013-2023)_20251102.csv' WITH (FORMAT CSV, HEADER TRUE);
```

**Paso 4: Creación de la Tabla Final y Limpieza (ETL)**
Finalmente, se creó la tabla de destino `taxis_raw` (con los tipos de datos correctos) y se utilizó un script `INSERT ... SELECT` para migrar los datos. Este script realizó toda la limpieza y transformación necesaria en un solo paso:

1.  **Fechas:** Se usó `SET datestyle TO 'MDY';` para que Postgres interpretara correctamente el formato `MM/DD/YYYY`.
2.  **Números:** Se usó `CAST(REGEXP_REPLACE(col, '[^0-9\.]', '', 'g') AS NUMERIC)` para eliminar caracteres no numéricos (como `$`, `,`, `<`) de las columnas de dinero.
3.  **Filtrado:** Se añadió un `WHERE` para re-confirmar el rango de años (2019-2022).

<!-- end list -->

```sql
SET datestyle TO 'MDY';

INSERT INTO taxis_raw (
    trip_id,
    taxi_id,
    trip_start_timestamp,
    trip_end_timestamp,
    pickup_community_area,
    dropoff_community_area,
    fare,
    tips,
    tolls,
    extras,
    trip_total,
    trip_miles
)
SELECT
    col1,
    col2,
    CAST(col3 AS TIMESTAMP),
    CAST(col4 AS TIMESTAMP),
    CAST(NULLIF(col5, '') AS INT),
    CAST(NULLIF(col6, '') AS INT),
    CAST(REGEXP_REPLACE(col7, '[^0-9\.]', '', 'g') AS NUMERIC),
    CAST(REGEXP_REPLACE(col8, '[^0-9\.]', '', 'g') AS NUMERIC),
    CAST(REGEXP_REPLACE(col9, '[^0-9\.]', '', 'g') AS NUMERIC),
    CAST(REGEXP_REPLACE(col10, '[^0-9\.]', '', 'g') AS NUMERIC),
    CAST(REGEXP_REPLACE(col11, '[^0-9\.]', '', 'g') AS NUMERIC),
    CAST(REGEXP_REPLACE(col12, '[^0-9\.]', '', 'g') AS NUMERIC)
FROM
    taxis_raw_text
WHERE
    EXTRACT(YEAR FROM CAST(col3 AS TIMESTAMP)) BETWEEN 2019 AND 2022;
```
¡Absolutamente\! Has hecho un excelente trabajo de perfilado y limpieza de datos.

Aquí tienes esa información formateada como una sección profesional para tu archivo `README.md`.

-----

## C) Limpieza de Datos

Después de la fase de carga (Sección B), la tabla `taxis_raw` contenía **30,694,643** registros. Sin embargo, estos datos, aunque limpios en formato, requerían una limpieza lógica para asegurar la integridad del análisis.

Se ejecutaron varias consultas de perfilado para identificar y tratar datos anómalos, irrelevantes o erróneos.

### Resumen de la Limpieza Lógica

  * **Viajes con Tiempos Inválidos:** Se identificaron **9,812,064** registros donde la fecha/hora de fin (`trip_end_timestamp`) era anterior o igual a la de inicio. Estos datos son ilógicos y se eliminaron.
  * **Viajes sin Geografía:** Se encontraron **3,764,970** viajes donde `pickup_community_area` o `dropoff_community_area` eran nulos. Dado que el análisis geográfico es clave para el proyecto, estos registros fueron eliminados.
  * **Viajes No Representativos:** Se detectaron **4,409,849** viajes que registraron 0 millas (`trip_miles`) pero un costo (`trip_total`) mayor a cero. Se determinó que estos registros probablemente representan tarifas de cancelación o errores de datos y fueron excluidos del análisis.
  * **Viajes con Pagos Nulos:** Se encontraron **2,721** viajes donde `fare` o `trip_total` eran nulos. Al ser campos cruciales para el análisis, estos registros fueron eliminados.
  * **Normalización de Nulos (Propinas y Peajes):** A diferencia de la tarifa, se asumió que un valor `NULL` en `tips` (propinas) y `tolls` (peajes) representaba un valor de **cero**. Por lo tanto, se ejecutó un `UPDATE` para asignarles el valor `0` en lugar de eliminarlos.

Tras aplicar estas reglas de limpieza, el conjunto de datos en la tabla `taxis_raw` se redujo a **16,325,806** registros, listos para la fase de normalización.

### Script de Limpieza Ejecutado

```sql
-- 1. Normalizar nulos en propinas y peajes
UPDATE taxis_raw
SET tips = 0
WHERE tips IS NULL;

UPDATE taxis_raw
SET tolls = 0
WHERE tolls IS NULL;

-- 2. Eliminar viajes con tiempos inválidos
DELETE FROM taxis_raw
WHERE trip_end_timestamp <= trip_start_timestamp;

-- 3. Eliminar viajes sin geografía 
DELETE FROM taxis_raw
WHERE pickup_community_area IS NULL OR dropoff_community_area IS NULL;

-- 4. Eliminar viajes de 0 millas con costo 
DELETE FROM taxis_raw
WHERE trip_miles <= 0 AND trip_total > 0;

-- 5. Eliminar viajes sin tarifa o total
DELETE FROM taxis_raw
WHERE fare IS NULL OR trip_total IS NULL;

-- 6. Verificación final de conteo
SELECT COUNT(*) FROM taxis_raw;
-- Resultado: 16,325,806
```


Al terminar este script, la tabla `taxis_raw` quedó poblada con los datos listos para la siguiente fase de normalización.

