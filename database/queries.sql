-- Run after installation and seeding.
SELECT f.registration_code, a.name FROM Farmer f INNER JOIN Farm a ON a.farmer_id = f.id;
SELECT c.common_name, v.name FROM Indigenous_Crop c LEFT JOIN Seed_Variety v ON v.crop_id = c.id;
SELECT a.name, f.registration_code FROM Farm a RIGHT JOIN Farmer f ON f.id = a.farmer_id;
SELECT a.name, i.common_name, h.net_yield, h.yield_unit
FROM Harvest_Record h JOIN Cultivation_Record c ON c.id = h.cultivation_id
JOIN Farm a ON a.id = c.farm_id LEFT JOIN Seed_Variety v ON v.id = c.seed_variety_id
JOIN Indigenous_Crop i ON i.id = COALESCE(c.crop_id, v.crop_id);
SELECT yield_unit, COUNT(*) AS samples, SUM(net_yield) AS total,
       AVG(net_yield) AS mean, MIN(net_yield) AS minimum, MAX(net_yield) AS maximum
FROM Harvest_Record GROUP BY yield_unit HAVING COUNT(*) >= 2;
SELECT id, name FROM Farm WHERE farmer_id IN
 (SELECT farmer_id FROM Farmer_Cultivation_Summary WHERE active_cultivations > 0);
SELECT c.common_name FROM Indigenous_Crop c WHERE EXISTS
 (SELECT 1 FROM Seed_Variety v WHERE v.crop_id = c.id);
SELECT f.registration_code FROM Farmer f WHERE NOT EXISTS
 (SELECT 1 FROM Farm a WHERE a.farmer_id = f.id);
EXPLAIN SELECT * FROM Farm WHERE state_name = 'Karnataka' AND district = 'Mandya';
EXPLAIN SELECT * FROM Cultivation_Record WHERE sowing_date >= '2025-07-01';
EXPLAIN SELECT * FROM Farmer WHERE registration_code = 'DEMO-F001';
EXPLAIN SELECT * FROM Indigenous_Crop WHERE common_name = 'Finger millet';
EXPLAIN SELECT * FROM Seed_Storage WHERE seed_variety_id = 1;

-- CREATE is demonstrated by schema.sql. This example leaves no demo records behind.
START TRANSACTION;
INSERT INTO Farmer (registration_code,given_name,registered_on,synthetic)
 VALUES ('SQL-DEMO','Demo',CURRENT_DATE,TRUE);
SELECT id, registration_code FROM Farmer WHERE registration_code = 'SQL-DEMO';
UPDATE Farmer SET specialization = 'Demonstration' WHERE registration_code = 'SQL-DEMO';
DELETE FROM Farmer WHERE registration_code = 'SQL-DEMO';
ROLLBACK;
