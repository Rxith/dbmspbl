DELIMITER $$
CREATE PROCEDURE allocate_seed(
 IN p_batch_id INT, IN p_quantity DECIMAL(12,3), IN p_farm_id INT,
 IN p_code VARCHAR(40), IN p_sowing_date DATE, IN p_season VARCHAR(16),
 IN p_area_ha DECIMAL(10,2)
)
MODIFIES SQL DATA
BEGIN
 DECLARE EXIT HANDLER FOR SQLEXCEPTION
 BEGIN
   ROLLBACK;
   RESIGNAL;
 END;
 START TRANSACTION;
 IF p_quantity IS NULL OR p_quantity <= 0 THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Allocation quantity must be positive';
 END IF;
 UPDATE Seed_Storage SET current_quantity = current_quantity - p_quantity
 WHERE id = p_batch_id AND status = 'available' AND current_quantity >= p_quantity
   AND stored_on <= p_sowing_date
   AND (expected_expiry_on IS NULL OR expected_expiry_on >= GREATEST(CURRENT_DATE, p_sowing_date));
 IF ROW_COUNT() <> 1 THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Batch is unavailable, expired, or has insufficient seed';
 END IF;
 INSERT INTO Cultivation_Record
   (farm_id, seed_variety_id, cultivation_code, sowing_date, season, seed_quantity, seed_unit, area_ha)
 SELECT p_farm_id, seed_variety_id, p_code, p_sowing_date, p_season, p_quantity, quantity_unit, p_area_ha
 FROM Seed_Storage WHERE id = p_batch_id;
 COMMIT;
END$$
DELIMITER ;
