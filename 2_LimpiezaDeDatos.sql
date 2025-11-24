SET datestyle TO 'MDY';
DROP TABLE taxis_raw;
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
