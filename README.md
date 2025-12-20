# Dataset
El link del dataset es el siguiente: https://drive.google.com/drive/folders/13RcFQmO2OpXNiIG9cFyVOqxgDyd2m0c_?usp=drive_link

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

**Nota**: En el siguiente comando, es necesario cambiar <PATH_DEL_ARCHIVO> con la ruta exacta en la que se encuentra guardado el archivo CSV en el equipo.

```sql
\copy taxis_raw_text FROM 'C:/<PATH_DEL_ARCHIVO>/Taxi_Trips_(2013-2023)_20251102.csv' WITH (FORMAT CSV, HEADER TRUE);
```

**Paso 4: Creación de la Tabla Final y Limpieza (ETL)**
Finalmente, se creó la tabla de destino `taxis_raw` (con los tipos de datos correctos) y se utilizó un script `INSERT ... SELECT` para migrar los datos. Este script realizó toda la limpieza y transformación necesaria en un solo paso:


1.  **Fechas:** Se usó `SET datestyle TO 'MDY';` para que Postgres interpretara correctamente el formato `MM/DD/YYYY`.
2.  **Números:** Se usó `CAST(REGEXP_REPLACE(col, '[^0-9\.]', '', 'g') AS NUMERIC)` para eliminar caracteres no numéricos (como `$`, `,`, `<`) de las columnas de dinero.
3.  **Filtrado:** Se añadió un `WHERE` para re-confirmar el rango de años (2019-2022).

<!-- end list -->

```sql
SET datestyle TO 'MDY';

CREATE TABLE taxis_raw(
    trip_id TEXT,
    taxi_id TEXT,
    trip_start_timestamp TIMESTAMP,
    trip_end_timestamp TIMESTAMP,
    pickup_community_area INT,
    dropoff_community_area INT,
    fare NUMERIC,
    tips NUMERIC,
    tolls NUMERIC,
    extras NUMERIC,
    trip_total NUMERIC,
    trip_miles NUMERIC
);

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

### D) Normalización de los datos
Este data set tiene 12 columnas, de las cuales haremos 4 entidades.
##### Viajes:
```sql
CREATE TABLE viajes(
trip_id TEXT PRIMARY KEY,
taxi_id TEXT,
trip_start_timestamp TIMESTAMP,
trip_end_timestamp TIMESTAMP,
trip_miles NUMERIC
);

INSERT INTO viajes (trip_id, taxi_id, trip_start_timestamp, trip_end_timestamp, trip_miles) 
SELECT trip_id, taxi_id, trip_start_timestamp, trip_end_timestamp, trip_miles
FROM taxis_raw;
```

##### Pagos:
```sql
CREATE TABLE pagos (
trip_id TEXT PRIMARY KEY,
fare NUMERIC,
tips NUMERIC,
tolls NUMERIC,
extras NUMERIC,
trip_total NUMERIC
);

INSERT INTO pagos (trip_id, fare, tips, tolls, extras, trip_total)
SELECT trip_id, fare, tips, tolls, extras, trip_total
FROM taxis_raw;
```

##### community_areas:
```sql
CREATE TABLE community_area (
community_id INT PRIMARY KEY,
community VARCHAR(30)
);

INSERT INTO community_area (community_id, community) VALUES
(1, 'Rogers Park'),
(2, 'West Ridge'),
(3, 'Uptown'),
(4, 'Lincoln Square'),
(5, 'North Center'),
(6, 'Lake View'),
(7, 'Lincoln Park'),
(8, 'Near North Side'),
(9, 'Edison Park'),
(10, 'Norwood Park'),
(11, 'Jefferson Park'),
(12, 'Forest Glen'),
(13, 'North Park'),
(14, 'Albany Park'),
(15, 'Portage Park'),
(16, 'Irving Park'),
(17, 'Dunning'),
(18, 'Montclare'),
(19, 'Belmont Cragin'),
(20, 'Hermosa'),
(21, 'Avondale'),
(22, 'Logan Square'),
(23, 'Humboldt Park'),
(24, 'West Town'),
(25, 'Austin'),
(26, 'West Garfield Park'),
(27, 'East Garfield Park'),
(28, 'Near West Side'),
(29, 'North Lawndale'),
(30, 'South Lawndale'),
(31, 'Lower West Side'),
(32, 'Loop'),
(33, 'Near South Side'),
(34, 'Armour Square'),
(35, 'Douglas'),
(36, 'Oakland'),
(37, 'Fuller Park'),
(38, 'Grand Boulevard'),
(39, 'Kenwood'),
(40, 'Washington Park'),
(41, 'Hyde Park'),
(42, 'Woodlawn'),
(43, 'South Shore'),
(44, 'Chatham'),
(45, 'Avalon Park'),
(46, 'South Chicago'),
(47, 'Burnside'),
(48, 'Calumet Heights'),
(49, 'Roseland'),
(50, 'Pullman'),
(51, 'South Deering'),
(52, 'East Side'),
(53, 'West Pullman'),
(54, 'Riverdale'),
(55, 'Hegewisch'),
(56, 'Garfield Ridge'),
(57, 'Archer Heights'),
(58, 'Brighton Park'),
(59, 'Mckinley Park'),
(60, 'Bridgeport'),
(61, 'New City'),
(62, 'West Elsdon'),
(63, 'Gage Park'),
(64, 'Clearing'),
(65, 'West Lawn'),
(66, 'Chicago Lawn'),
(67, 'West Englewood'),
(68, 'Englewood'),
(69, 'Greater Grand Crossing'),
(70, 'Ashburn'),
(71, 'Auburn Gresham'),
(72, 'Beverly'),
(73, 'Washington Heights'),
(74, 'Mount Greenwood'),
(75, 'Morgan Park'),
(76, 'Ohare'),
(77, 'Edgewater');
```

##### ciudad_viaje:
```sql
CREATE TABLE ciudad_viaje (
trip_id TEXT PRIMARY KEY,
pickup_community_area INT,
dropoff_community_area INT
);

INSERT INTO ciudad_viaje
SELECT trip_id, pickup_community_area, dropoff_community_area
FROM taxis_raw;
``` 

### E) Análisis de datos a través de consultas SQL y creación de atributos analíticos
##### Análisis inicial
tarifas: dolares, distancia: millas

Para empezar a explorar los datos ya limpios y listos para trabajarse, optamos por medir en promedios trimestrales de los años 2019-2022. Consultamos la cantidad de viajes y la cantidad de taxis. Luego, las medidas por taxi, ya que estas ilustran cambios de manera más directa en los ingresos, porque no deflactamos los precios ante la inflación. Finalmente, los promedios de distancia y tarifa por distancia. Tomamos en cuenta solamente el precio de las tarifas (sin extras o peajes).

##### Valores exploratorios iniciales
```sql
SELECT EXTRACT(YEAR FROM trip_start_timestamp) AS año,
       EXTRACT(QUARTER FROM trip_start_timestamp) AS trimestre,
       COUNT(DISTINCT viajes.trip_id) AS cantidad_viajes,
       COUNT (DISTINCT viajes.taxi_id) AS cantidad_taxis,
       COUNT(DISTINCT viajes.trip_id) / COUNT(DISTINCT viajes.taxi_id) AS viajes_por_taxi,
       SUM(pagos.fare) / COUNT(DISTINCT viajes.taxi_id) AS ingreso_por_taxi,
       AVG(viajes.trip_miles) AS promedio_distancia_millas,
       SUM(pagos.fare) / NULLIF(SUM(viajes.trip_miles), 0) AS promedio_tarifa_por_milla
FROM viajes
JOIN pagos
	ON viajes.trip_id = pagos.trip_id
GROUP BY EXTRACT(YEAR FROM trip_start_timestamp),
         EXTRACT(QUARTER FROM trip_start_timestamp)
ORDER BY año, trimestre;
```
|  Año | Trimestre | Cantidad de viajes | Cantidad de taxis | Viajes por taxi | Ingreso por taxi | Promedio distancia (millas) | Tarifa promedio por milla |
| ---: | --------: | -----------------: | ----------------: | --------------: | ---------------: | --------------------------: | ------------------------: |
| 2019 |         1 |          2,045,079 |             4,397 |             465 |         8,088.89 |                        5.03 |                      3.46 |
| 2019 |         2 |          2,273,850 |             4,485 |             506 |         9,441.35 |                        5.49 |                      3.39 |
| 2019 |         3 |          2,110,588 |             4,199 |             502 |         9,143.51 |                        5.31 |                      3.43 |
| 2019 |         4 |          2,051,084 |             4,204 |             487 |         8,909.40 |                        5.21 |                      3.51 |
| 2020 |         1 |          1,358,823 |             3,890 |             349 |         6,367.18 |                        4.99 |                      3.65 |
| 2020 |         2 |            121,236 |               815 |             148 |         2,894.60 |                        5.64 |                      3.45 |
| 2020 |         3 |            229,101 |               866 |             264 |         5,202.19 |                        5.66 |                      3.47 |
| 2020 |         4 |            257,889 |               875 |             294 |         6,187.95 |                        6.16 |                      3.41 |
| 2021 |         1 |            288,240 |               868 |             332 |         7,364.21 |                        6.73 |                      3.29 |
| 2021 |         2 |            466,600 |             1,187 |             393 |         9,259.14 |                        7.21 |                      3.27 |
| 2021 |         3 |            665,840 |             1,815 |             366 |         9,096.48 |                        7.57 |                      3.28 |
| 2021 |         4 |            766,440 |             2,051 |             373 |         8,798.81 |                        7.18 |                      3.28 |
| 2022 |         1 |            660,584 |             1,987 |             332 |         7,632.59 |                        7.06 |                      3.25 |
| 2022 |         2 |          1,012,136 |             2,354 |             429 |        10,664.11 |                        7.71 |                      3.22 |
| 2022 |         3 |          1,030,809 |             2,527 |             407 |         9,794.80 |                        7.58 |                      3.17 |
| 2022 |         4 |            987,507 |             2,599 |             379 |         9,165.71 |                        7.69 |                      3.14 |

La cantidad de taxis y de viajes, después de la caida, no lograron recuperarse totalamente. Se quedaron al rededor de la mitad de sus valores antes de la pandemia. Los ingresos y viajes por taxi, en cambio, aparte de estar altamente correlacionados, si lograron recuperarse a sus valores prepandemia, en algunos casos excediendolos. 
El promedio de distancia en millas incrementó constantemente a través de los años, lo que demuestra un aumento de viajes más largos en taxi. Esto puede ser derivado de que la cuarentena que nos otorgó una noción de "solo tomar riesgos (como un taxi) si es necesario, como un viaje más largo. Si no, evitarlo". 
La tarifa promedio por milla es la más impresionante de todas, ya que observamos un decrecimiento constante en la cantidad de dinero que se paga por milla en taxi desde la pandemia. Esto puede estar relacionado a la sustitución del taxi por otros medios de transporte, como compañías privadas de mobilidad (Uber, Lyft), entonces se deben de bajar los precios para ajustar el decrecimiento de la demanda por taxis convencionales.


##### Análisis completo de las propinas
Escogimos hacer un análisis completo de las propinas porque creemos que es una buena medida para medir el impacto de la pandemia tanto en la economía local como en la solidaridad de la población con los conductores de taxi.

##### Medidas imporantes por año
```sql
SELECT EXTRACT(YEAR FROM trip_start_timestamp) AS año, SUM(tips) as total_propinas, AVG(tips) as promedio_propinas, MAX(tips) as maximo, MIN(tips) as minimo
FROM pagos
JOIN viajes
	ON viajes.trip_id = pagos.trip_id
GROUP BY EXTRACT(YEAR FROM trip_start_timestamp);
```
Resultado:
| Año  | Total de propinas | Promedio de propinas | Propina máxima | Propina mínima |
|------|-------------------|----------------------|----------------|----------------|
| 2019 | 19,580,923.31     | 2.31                 | 407.68         | 0.00           |
| 2020 | 3,516,491.31      | 1.79                 | 200.00         | 0.00           |
| 2021 | 4,683,228.12      | 2.14                 | 350.00         | 0.00           |
| 2022 | 10,670,438.57     | 2.89                 | 210.00         | 0.00           |

Como se puede observar, el total y el promedio de propinas cayó durante la pandemia. Sin embargo, es impresionante que a pesar de que en 2022 el total de propinas fue más bajo que en 2019, el promedio de propinas aumentó considerablemente.


##### Propina como porcentaje del total del viaje por periodo
```sql
SELECT 
    CASE 
        WHEN viajes.trip_start_timestamp < '2020-03-01' THEN 'Pre-Pandemia'
        WHEN viajes.trip_start_timestamp BETWEEN '2020-03-01' AND '2021-12-31' THEN 'Pandemia'
        ELSE 'Post-Pandemia'
    END AS periodo,
    AVG((pagos.tips/NULLIF(pagos.trip_total, 0)) * 100) AS Porcentaje_propina_promedio
FROM pagos
JOIN viajes ON viajes.trip_id = pagos.trip_id
GROUP BY periodo
ORDER BY periodo;
```
Resultado:
| Periodo        | Porcentaje promedio de propina |
|----------------|--------------------------------|
| Pre-Pandemia   | 9.39 %                         |
| Pandemia       | 6.36 %                         |
| Post-Pandemia  | 9.19 %                         |

Como se puede observar, también el procentaje promedio de propina cayó durante la pandemia pero volvió a alzarse después de esta. A diferencia de la consulta anterior, el porcentaje no logró estar por arriba del año previo a la pandemia.


##### Porcentaje de viajes con propina por periodo
```sql
SELECT
    CASE 
        WHEN viajes.trip_start_timestamp < '2020-03-01' THEN 'Pre-Pandemia'
        WHEN viajes.trip_start_timestamp BETWEEN '2020-03-01' AND '2021-12-31' THEN 'Pandemia'
        ELSE 'Post-Pandemia'
    END AS periodo,
    COUNT(*) FILTER (WHERE pagos.tips > 0)::float / COUNT(*) * 100 AS porcentaje_con_propina
FROM pagos
JOIN viajes ON viajes.trip_id = pagos.trip_id
GROUP BY periodo
ORDER BY periodo;
```
Resultados:
| Periodo        | Porcentaje de viajes con propina |
|----------------|----------------------------------|
| Pre-Pandemia   | 51.62 %                          |
| Pandemia       | 35.22 %                          |
| Post-Pandemia  | 51.47 %                          |

De manera muy similar, podemos observar que la mayoría de personas dejaban propina antes de pandemia, tendencia que se dió a la baja durante la crisis y que volvió a la normalidad después de esta.


##### Promedio de propina por milla en distintos periodos
```sql
SELECT
    CASE 
        WHEN viajes.trip_start_timestamp < '2020-03-01' 
            THEN 'Pre-Pandemia'
        WHEN viajes.trip_start_timestamp BETWEEN '2020-03-01' AND '2021-12-31' 
            THEN 'Pandemia'
        ELSE 'Post-Pandemia'
    END AS periodo,
    AVG(pagos.tips / NULLIF(viajes.trip_miles, 0)) AS propina_por_milla
FROM pagos
JOIN viajes ON viajes.trip_id = pagos.trip_id
GROUP BY periodo
ORDER BY periodo;
```
Resultados:
| Periodo        | Propina promedio por milla |
|----------------|----------------------------|
| Pre-Pandemia   | 1.13                       |
| Pandemia       | 0.75                       |
| Post-Pandemia  | 0.91                       |

Sorprendentemente, al repetir el análisis de propina promedio pero ahora por milla, podemos descubrir que el valor más alto lo tiene el año antes de la pandemia. A diferencia de los casos anteriores, esta variable no se logró recuperar totalmente un año después del evento.


##### Correlación entre millas y propinas en distintos periodos
```sql
SELECT
    CASE 
        WHEN viajes.trip_start_timestamp < '2020-03-01' THEN 'Pre-Pandemia'
        WHEN viajes.trip_start_timestamp BETWEEN '2020-03-01' AND '2021-12-31' THEN 'Pandemia'
        ELSE 'Post-Pandemia'
    END AS periodo,
    CORR(viajes.trip_miles, pagos.tips) AS correlacion_millas_propina
FROM pagos
JOIN viajes ON viajes.trip_id = pagos.trip_id
GROUP BY periodo;
```
Resultados:
| Periodo        | Correlación millas–propina |
|----------------|----------------------------|
| Pre-Pandemia   | 0.53                       |
| Pandemia       | 0.26                       |
| Post-Pandemia  | 0.46                       |

La correlación entre las millas recorridas y la propina sigue una tendencia similar al promedio entre estas mismas variables.


##### Cambio entre promedio de propinas por comunidad antes y después de pandemia
```sql
WITH propinas_periodo AS (
    SELECT
        community_area.community AS comunidad,
        CASE 
            WHEN viajes.trip_start_timestamp < '2020-03-01' THEN 'Pre'
            WHEN viajes.trip_start_timestamp BETWEEN '2020-03-01' AND '2021-12-31' THEN 'Pandemia'
            ELSE 'Post'
        END AS periodo,
        AVG(pagos.tips) AS propina_promedio
    FROM pagos
    JOIN viajes
        ON viajes.trip_id = pagos.trip_id
    JOIN ciudad_viaje
        ON ciudad_viaje.trip_id = viajes.trip_id
    JOIN community_area
        ON community_area.community_id = ciudad_viaje.dropoff_community_area
    GROUP BY community_area.community, periodo
),
pivot AS (
    SELECT
        comunidad,
        MAX(CASE WHEN periodo = 'Pre' THEN propina_promedio END) AS propina_pre,
        MAX(CASE WHEN periodo = 'Pandemia' THEN propina_promedio END) AS propina_pandemia,
        MAX(CASE WHEN periodo = 'Post' THEN propina_promedio END) AS propina_post,
        (MAX(CASE WHEN periodo = 'Post' THEN propina_promedio END) - MAX(CASE WHEN periodo = 'Pre' THEN propina_promedio END)) AS cambio_pre_post
    FROM propinas_periodo
    GROUP BY comunidad
),
top_10 AS (
    SELECT *
    FROM pivot
    ORDER BY cambio_pre_post DESC
    LIMIT 10
),
bottom_10 AS (
    SELECT *
    FROM pivot
    ORDER BY cambio_pre_post ASC
    LIMIT 10
)
SELECT *
FROM top_10
UNION ALL
SELECT *
FROM bottom_10
ORDER BY cambio_pre_post DESC;
```
Resultados:
| Comunidad        | Pre  | Pandemia | Post | Cambio Pre–Post |
|------------------|------|----------|------|-----------------|
| Loop             | 2.07 | 2.32     | 3.34 | 1.27 |
| Near North Side  | 2.07 | 2.34     | 3.07 | 1.00 |
| Hermosa          | 0.89 | 0.83     | 1.84 | 0.95 |
| West Town        | 2.31 | 2.50     | 3.19 | 0.89 |
| North Center     | 3.26 | 2.88     | 4.02 | 0.75 |
| Lincoln Park     | 2.32 | 2.42     | 3.04 | 0.72 |
| Logan Square     | 2.69 | 2.45     | 3.41 | 0.72 |
| Near South Side  | 2.23 | 1.85     | 2.82 | 0.59 |
| Bridgeport       | 1.72 | 1.22     | 2.29 | 0.56 |
| Lake View        | 2.60 | 2.35     | 3.12 | 0.52 |
| Oakland          | 0.99 | 0.20     | 0.42 | -0.57 |
| Hegewisch        | 1.01 | 0.45     | 0.37 | -0.63 |
| Norwood Park     | 2.18 | 1.04     | 1.53 | -0.65 |
| Archer Heights   | 1.98 | 1.12     | 1.32 | -0.66 |
| Morgan Park      | 1.09 | 0.25     | 0.42 | -0.67 |
| Beverly          | 3.62 | 1.49     | 2.82 | -0.80 |
| Kenwood          | 2.13 | 0.72     | 1.33 | -0.80 |
| East Side        | 1.27 | 0.30     | 0.45 | -0.82 |
| Jefferson Park   | 3.22 | 1.72     | 1.77 | -1.45 |
| Clearing         | 3.81 | 1.33     | 2.02 | -1.79 |

Finalmente, hicimos un listado de las 10 comunidades más resilientes contra las 10 menos resilientes. Asombrosamente, podemos observar que hubo gran discrepancia entre la reacción de las comunidades de Chicago frente al mismo fenómeno. Por un lado, hubo comunidades que aumentaron aproximandamente 60% su promedio de propinas antes y después de la pandemia, mientras que hubo otras que lo disminuyeron casi en un 50%. Estos resultados muestran que no todas las comunidades se recuperaron a la misma velocidad de este fenómeno sanitario.
