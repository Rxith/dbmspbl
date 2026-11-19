CREATE VIEW Farmer_Cultivation_Summary AS
SELECT f.id AS farmer_id, f.registration_code,
       COUNT(DISTINCT a.id) AS farms, COUNT(c.id) AS cultivations,
       SUM(CASE WHEN c.status = 'active' THEN 1 ELSE 0 END) AS active_cultivations
FROM Farmer f LEFT JOIN Farm a ON a.farmer_id = f.id
LEFT JOIN Cultivation_Record c ON c.farm_id = a.id
GROUP BY f.id, f.registration_code;

CREATE VIEW Indigenous_Seed_Availability AS
SELECT c.id AS crop_id, c.common_name, v.id AS variety_id, v.name AS variety_name,
       s.quantity_unit, COUNT(s.id) AS available_batches,
       COALESCE(SUM(s.current_quantity), 0) AS available_quantity
FROM Seed_Variety v JOIN Indigenous_Crop c ON c.id = v.crop_id
LEFT JOIN Seed_Storage s ON s.seed_variety_id = v.id AND s.status = 'available'
 AND (s.expected_expiry_on IS NULL OR s.expected_expiry_on >= CURRENT_DATE)
GROUP BY c.id, c.common_name, v.id, v.name, s.quantity_unit;

CREATE VIEW Seasonal_Harvest_Report AS
SELECT YEAR(h.harvested_on) AS harvest_year, c.season, h.yield_unit,
       COUNT(*) AS harvests, SUM(h.gross_yield) AS gross_yield,
       SUM(h.net_yield) AS net_yield, SUM(h.gross_yield - h.net_yield) AS losses
FROM Harvest_Record h JOIN Cultivation_Record c ON c.id = h.cultivation_id
GROUP BY YEAR(h.harvested_on), c.season, h.yield_unit;
