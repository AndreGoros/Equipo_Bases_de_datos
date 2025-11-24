CREATE DATABASE proyecto_taxis;

\c proyecto_taxis

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

\copy taxis_raw_text FROM 'C:/Users/LARIG/OneDrive/Desktop/ITAM/Semestre_3/Bases_de_Datos/Taxi_Trips_(2013-2023)_20251102.csv' WITH (FORMAT CSV, HEADER TRUE);
