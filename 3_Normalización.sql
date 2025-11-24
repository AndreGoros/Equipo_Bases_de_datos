-- Normalización:
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

CREATE TABLE ciudad_viaje (
trip_id TEXT PRIMARY KEY,
pickup_community_area INT,
dropoff_community_area INT
);

INSERT INTO ciudad_viaje
SELECT trip_id, pickup_community_area, dropoff_community_area
FROM taxis_raw;