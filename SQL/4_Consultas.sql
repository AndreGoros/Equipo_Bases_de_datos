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
	
	
	
	
	
	
	
	
	
	
	