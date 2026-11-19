DELIMITER $$
CREATE PROCEDURE farmer_cultivations(IN p_farmer_id INT)
READS SQL DATA
BEGIN
 SELECT c.cultivation_code, f.name AS farm,
        i.common_name AS crop, v.name AS variety, c.season, c.sowing_date, c.status
 FROM Cultivation_Record c JOIN Farm f ON f.id = c.farm_id
 LEFT JOIN Seed_Variety v ON v.id = c.seed_variety_id
 JOIN Indigenous_Crop i ON i.id = COALESCE(c.crop_id, v.crop_id)
 WHERE f.farmer_id = p_farmer_id ORDER BY c.sowing_date DESC, c.id DESC;
END$$

CREATE PROCEDURE seasonal_harvest(IN p_year INT, IN p_season VARCHAR(16))
READS SQL DATA
BEGIN
 SELECT * FROM Seasonal_Harvest_Report
 WHERE (p_year IS NULL OR p_year = harvest_year)
   AND (p_season IS NULL OR p_season = season)
 ORDER BY harvest_year DESC, season, yield_unit;
END$$

CREATE PROCEDURE adjust_seed_stock(IN p_batch_id INT, IN p_delta DECIMAL(12,3))
MODIFIES SQL DATA
BEGIN
 IF p_delta IS NULL OR p_delta = 0 THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Enter a nonzero stock adjustment';
 END IF;
 UPDATE Seed_Storage SET current_quantity = current_quantity + p_delta
 WHERE id = p_batch_id AND current_quantity + p_delta >= 0;
 IF ROW_COUNT() = 0 THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Batch missing or insufficient seed stock';
 END IF;
END$$
DELIMITER ;
