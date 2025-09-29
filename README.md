# Dataset de Viajes en Taxi en Chicago (2013–2023)



Este repositorio utiliza un conjunto de datos público que contiene información detallada sobre 212 millones de viajes en taxi en la ciudad de Chicago. Cada registro incluye datos del trayecto, tiempos, ubicaciones aproximadas de origen y destino, costos y formas de pago. Este conjunto de datos fue recolectado por el gobierno de la ciudad de Chicago y publicado en su portal oficial de datos abiertos. El propósito de su recolección fue analizar tendencias de movilidad sin comprometer la privacidad de usuarios y conductores. Para ello, el identificador del taxi es consistente pero anonimizado y no muestra el número de medallón real, algunos tramos censales fueron suprimidos para evitar identificación de usuarios y las marcas de tiempo se redondearon al cuarto de hora más cercano. El dataset cubre el período comprendido entre los años 2013 y 2023. Actualmente ya no se actualiza, y la última actualización se realizó a inicios de 2024. El conjunto de datos cuenta con 212,000,000 registros y 23 atributos. Nuestro equipo lo utilizará con el objetivo de analizar cómo cambió el comportamiento de los taxis antes, durante y después de la pandemia, tomando en cuenta especialmente los años 2018 a 2023, con el fin de identificar variaciones en la movilidad, las distancias recorridas, la duración de los viajes y los métodos de pago. El análisis de este dataset debe hacerse con responsabilidad, teniendo presente que se trata de información sensible. Es necesario respetar la privacidad de pasajeros y conductores, reconocer los sesgos inherentes en los datos, mantener transparencia metodológica en el análisis y en la comunicación de resultados, y usar esta información únicamente con fines académicos y sociales, evitando aplicaciones que puedan resultar en discriminación o explotación comercial indebida.



---



A continuación se listan los atributos disponibles en el dataset:

* Identificadores y texto: trip\_id, taxi\_id, pickup\_census\_tract, dropoff\_census\_tract
* Fechas y tiempos: trip\_start\_timestamp, trip\_end\_timestamp
* Numéricos: trip\_seconds, trip\_miles, pickup\_community\_area, dropoff\_community\_area, fare, tips, tolls, extras, trip\_total, pickup\_centroid\_latitude, pickup\_centroid\_longitude, dropoff\_centroid\_latitude, dropoff\_centroid\_longitude
* Categóricos: payment\_type, company
* Geoespaciales: pickup\_centroid\_location, dropoff\_centroid\_location
