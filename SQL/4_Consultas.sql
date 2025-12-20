/* 
------OBJETIVO: 

Analizar si hubo algún cambio de horario en el uso de los taxis. Se hizo más frecuente (proporcionalmente) usarlos temprano, a medio día, tarde? Se mantuvo igual? */


--- CONSULTA 1: 
--- Dividir en intervalos de tiempo los viajes para analizar cada "sección" del día

WITH viajes_por_horarios AS (

SELECT 
	
	-- extraer el año para comparar cómo ha evolucionado (2020, 2021, 2022...
	EXTRACT (YEAR FROM trip_start_timestamp) AS anio, 
	
	--- hacer los intervalos en los que dividiremos el día
	CASE 
		WHEN EXTRACT (HOUR FROM trip_start_timestamp) >= 0 AND EXTRACT (HOUR FROM trip_start_timestamp) < 6 THEN 'Madugrada (00:00 - 05:59)'
		WHEN EXTRACT (HOUR FROM trip_start_timestamp) >= 6 AND EXTRACT (HOUR FROM trip_start_timestamp) < 12 THEN 'Mañana (06:00 - 11:59)'
		WHEN EXTRACT (HOUR FROM trip_start_timestamp) >= 12 AND EXTRACT (HOUR FROM trip_start_timestamp) < 18 THEN 'Tarde (12:00 - 17:59)'
		ELSE 'Noche (18:00 - 23:59)'
		END AS intervalos_horarios
		
		
	FROM viajes
)

SELECT 
    anio,
    intervalos_horarios,
    COUNT(*) AS total_viajes,
    ROUND(
        (COUNT(*) * 100.0) / 
        SUM(COUNT(*)) OVER (PARTITION BY anio),2) 
        AS porcentaje_por_anio

FROM viajes_por_horarios

GROUP BY 
    anio, intervalos_horarios 

ORDER BY 
    anio ASC, intervalos_horarios ASC;

-- Consultas adicionales para profundizar 

-- Análisis hora por hora

-- Este análisis permite ver si hubo horas pico, para reducir los intervalos grandes que se tenían de 6 horas

SELECT 
    EXTRACT(YEAR FROM trip_start_timestamp) AS anio,
    EXTRACT(HOUR FROM trip_start_timestamp) AS hora_exacta, 
    COUNT(*) AS total_viajes,

    ROUND(
        (COUNT(*) * 100.0) / 
        SUM(COUNT(*)) OVER (PARTITION BY EXTRACT(YEAR FROM trip_start_timestamp)), 2
    ) AS porcentaje_por_anio
FROM viajes
GROUP BY 1, 2
ORDER BY 1, 2;


-- Análisis de días (entre semana vs. fin de semana)
WITH categorias_dias AS (
    SELECT 
        EXTRACT(YEAR FROM trip_start_timestamp) AS anio,

        CASE 
            WHEN EXTRACT(ISODOW FROM trip_start_timestamp) IN (6, 7) THEN 'Fin de Semana'
            ELSE 'Entre Semana (Lunes-Viernes)'
        END AS tipo_dia,

        CASE 
            WHEN EXTRACT (HOUR FROM trip_start_timestamp) BETWEEN 0 AND 5 THEN 'Madrugada'
            WHEN EXTRACT (HOUR FROM trip_start_timestamp) BETWEEN 6 AND 11 THEN 'Mañana'
            WHEN EXTRACT (HOUR FROM trip_start_timestamp) BETWEEN 12 AND 17 THEN 'Tarde'
            ELSE 'Noche'
        END AS momento_dia
    FROM viajes
)

SELECT 
    anio,
    tipo_dia,
    momento_dia,
    COUNT(*) AS total_viajes,
    ROUND(
        (COUNT(*) * 100.0) / 
        SUM(COUNT(*)) OVER (PARTITION BY anio, tipo_dia), 2
    ) AS porcentaje_relativo
FROM categorias_dias
GROUP BY 1, 2, 3
ORDER BY anio, tipo_dia DESC, momento_dia;
	

-- CONSULTA 2: 
-- Para el análisis, tomaremos en cuenta solamente el precio de las tarifas (sin extras o peajes), el de las propinas y la duración de los viajes. El análisis será a traves de promedios mensuales.

SELECT EXTRACT(YEAR FROM trip_start_timestamp) AS trip_year,
       EXTRACT(MONTH FROM trip_start_timestamp) AS trip_month,
       AVG(pagos.fare) AS tarifa,
       AVG(pagos.tips) AS propinas,
       AVG(viajes.trip_miles) AS distancia_millas
FROM viajes
JOIN pagos
	ON viajes.trip_id = pagos.trip_id
GROUP BY EXTRACT(YEAR FROM trip_start_timestamp),
         EXTRACT(MONTH FROM trip_start_timestamp)
ORDER BY trip_year, trip_month;


--CONSULTA 3:
-- Promedios mensuales POR ZONA DE ORIGEN (pickup)
SELECT
    cv.pickup_community_area AS zona_origen,
    ca.community              AS nombre_zona_origen,
    
    EXTRACT(YEAR FROM v.trip_start_timestamp)  AS year,
    EXTRACT(MONTH FROM v.trip_start_timestamp) AS month,

    AVG(p.fare)         AS avg_fare,
    AVG(p.tips)         AS avg_tips,
    AVG(v.trip_miles)   AS avg_distance_miles,
    AVG( (v.trip_end_timestamp - v.trip_start_timestamp) ) AS avg_duration_interval,
    COUNT(*) AS total_viajes

FROM viajes v
JOIN pagos p
    ON v.trip_id = p.trip_id
JOIN ciudad_viaje cv
    ON v.trip_id = cv.trip_id
JOIN community_area ca
    ON cv.pickup_community_area = ca.community_id

WHERE cv.pickup_community_area IS NOT NULL

GROUP BY 
    cv.pickup_community_area,
    ca.community,
    EXTRACT(YEAR FROM v.trip_start_timestamp),
    EXTRACT(MONTH FROM v.trip_start_timestamp)

ORDER BY 
    zona_origen,
    year,
    month;

-- Consulta 4:
-- Promedios mensuales POR ZONA DE DESTINO (dropoff)

SELECT
    cv.dropoff_community_area AS zona_destino,
    ca.community              AS nombre_zona_destino,
    
    EXTRACT(YEAR FROM v.trip_start_timestamp)  AS year,
    EXTRACT(MONTH FROM v.trip_start_timestamp) AS month,

    AVG(p.fare)         AS avg_fare,
    AVG(p.tips)         AS avg_tips,
    AVG(v.trip_miles)   AS avg_distance_miles,
    AVG( (v.trip_end_timestamp - v.trip_start_timestamp) ) AS avg_duration_interval,
    COUNT(*) AS total_viajes

FROM viajes v
JOIN pagos p
    ON v.trip_id = p.trip_id
JOIN ciudad_viaje cv
    ON v.trip_id = cv.trip_id
JOIN community_area ca
    ON cv.dropoff_community_area = ca.community_id

WHERE cv.dropoff_community_area IS NOT NULL

GROUP BY 
    cv.dropoff_community_area,
    ca.community,
    EXTRACT(YEAR FROM v.trip_start_timestamp),
    EXTRACT(MONTH FROM v.trip_start_timestamp)

ORDER BY 
    zona_destino,
    year,
    month;

-- CONSULTA 5:
-- Compensación por la falta de de demanda (pickup)
SELECT
    cv.pickup_community_area AS zona_id,
    ca.community              AS nombre_zona,
    EXTRACT(YEAR FROM v.trip_start_timestamp)  AS year,
    EXTRACT(MONTH FROM v.trip_start_timestamp) AS month,

    COUNT(*)                      AS viajes,
    AVG(p.trip_total)             AS avg_trip_total,
    SUM(p.trip_total)             AS ingresos_totales,
    SUM(v.trip_miles)             AS millas_totales,
    CASE
        WHEN SUM(v.trip_miles) > 0
            THEN SUM(p.trip_total) / SUM(v.trip_miles)
        ELSE NULL
    END AS precio_promedio_por_milla

FROM viajes v
JOIN pagos p
    ON v.trip_id = p.trip_id
JOIN ciudad_viaje cv
    ON v.trip_id = cv.trip_id
JOIN community_area ca
    ON cv.pickup_community_area = ca.community_id

WHERE cv.pickup_community_area IS NOT NULL

GROUP BY
    cv.pickup_community_area,
    ca.community,
    year,
    month

ORDER BY
    zona_id,
    year,
    month;


-- CONSULTA 6: 
-- Compensación por la falta de de demanda (drop off)
SELECT
    cv.dropoff_community_area AS zona_id,
    ca.community               AS nombre_zona,
    EXTRACT(YEAR FROM v.trip_start_timestamp)  AS year,
    EXTRACT(MONTH FROM v.trip_start_timestamp) AS month,

    COUNT(*)                      AS viajes,
    AVG(p.trip_total)             AS avg_trip_total,
    SUM(p.trip_total)             AS ingresos_totales,
    SUM(v.trip_miles)             AS millas_totales,
    CASE
        WHEN SUM(v.trip_miles) > 0
            THEN SUM(p.trip_total) / SUM(v.trip_miles)
        ELSE NULL
    END AS precio_promedio_por_milla

FROM viajes v
JOIN pagos p
    ON v.trip_id = p.trip_id
JOIN ciudad_viaje cv
    ON v.trip_id = cv.trip_id
JOIN community_area ca
    ON cv.dropoff_community_area = ca.community_id

WHERE cv.dropoff_community_area IS NOT NULL

GROUP BY
    cv.dropoff_community_area,
    ca.community,
    year,
    month

ORDER BY
    zona_id,
    year,
    month;
	
	
-- CONSULTA 7:
-- Análisis propinas

-- Medidas importantes: (suma total, promedio, propina máxima y propina mínima)

-- Medidas importantes totales
SELECT SUM(tips) as total_propinas, AVG(tips) as promedio_propinas, MAX(tips) as maximo, MIN(tips) as minimo
FROM pagos;

-- Medidas imporantes por año
SELECT EXTRACT(YEAR FROM trip_start_timestamp) AS año, SUM(tips) as total_propinas, AVG(tips) as promedio_propinas, MAX(tips) as maximo, MIN(tips) as minimo
FROM pagos
JOIN viajes
	ON viajes.trip_id = pagos.trip_id
GROUP BY EXTRACT(YEAR FROM trip_start_timestamp);

-- Medidas importantes por zona
SELECT community_area.community AS comunidad, SUM(tips) as total_propinas, AVG(tips) as promedio_propinas
FROM pagos
JOIN viajes
	ON viajes.trip_id = pagos.trip_id
JOIN ciudad_viaje
	ON viajes.trip_id = ciudad_viaje.trip_id
JOIN community_area
	ON ciudad_viaje.dropoff_community_area = community_area.community_id
GROUP BY community_area.community;

-- En qué comunidad se dejan más y menos propinas
WITH total_propinas_comunidad AS (
	SELECT community_area.community AS comunidad, SUM(tips) as total_propinas
	FROM pagos
	JOIN viajes
		ON viajes.trip_id = pagos.trip_id
	JOIN ciudad_viaje
		ON viajes.trip_id = ciudad_viaje.trip_id
	JOIN community_area
		ON ciudad_viaje.dropoff_community_area = community_area.community_id
	GROUP BY community_area.community
)

SELECT comunidad, total_propinas
FROM total_propinas_comunidad
WHERE total_propinas = (SELECT MAX(total_propinas) from total_propinas_comunidad)

UNION

SELECT comunidad, total_propinas
FROM total_propinas_comunidad
WHERE total_propinas = (SELECT MIN(total_propinas) from total_propinas_comunidad);
	
	
	
	
	
	
	

	
