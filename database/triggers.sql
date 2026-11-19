DELIMITER $$
CREATE TRIGGER audit_seed_quantity BEFORE UPDATE ON Seed_Storage
FOR EACH ROW
BEGIN
 SET NEW.quantity_history = OLD.quantity_history;
 IF (OLD.quantity_unit <> NEW.quantity_unit OR OLD.seed_variety_id <> NEW.seed_variety_id)
    AND (OLD.current_quantity > 0 OR JSON_LENGTH(OLD.quantity_history) > 0) THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Use a new batch to change the variety or unit of tracked stock';
 END IF;
 IF OLD.current_quantity <> NEW.current_quantity THEN
   SET NEW.quantity_history = JSON_ARRAY_APPEND(
     OLD.quantity_history, '$',
     JSON_OBJECT('at_utc', UTC_TIMESTAMP(6), 'account', USER(),
                 'before', OLD.current_quantity, 'after', NEW.current_quantity,
                 'unit', NEW.quantity_unit)
   );
 END IF;
END$$
DELIMITER ;
