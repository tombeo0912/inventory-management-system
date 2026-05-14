-- FUNCTIONS, TRIGGERS, PROCEDURES
DELIMITER $$
CREATE FUNCTION fn_current_stock(p_product_id INT, p_warehouse_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_qty INT DEFAULT 0;

    SELECT COALESCE(quantity_on_hand, 0)
      INTO v_qty
      FROM warehouse_stock
     WHERE product_id = p_product_id
       AND warehouse_id = p_warehouse_id
     LIMIT 1;

    RETURN COALESCE(v_qty, 0);
END$$

CREATE FUNCTION fn_stock_turnover(p_product_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total_out INT DEFAULT 0;
    DECLARE v_avg_stock DECIMAL(12,2) DEFAULT 0;

    SELECT COALESCE(SUM(quantity), 0)
      INTO v_total_out
      FROM inventory_history
     WHERE product_id = p_product_id
       AND transaction_type = 'OUT';

    SELECT COALESCE(AVG(quantity_on_hand), 0)
      INTO v_avg_stock
      FROM warehouse_stock
     WHERE product_id = p_product_id;

    IF v_avg_stock = 0 THEN
        RETURN 0;
    END IF;

    RETURN ROUND(v_total_out / v_avg_stock, 2);
END$$

-- -------------------------
-- 4) TRIGGERS
-- -------------------------

CREATE TRIGGER trg_inventory_history_before_insert
BEFORE INSERT ON inventory_history
FOR EACH ROW
BEGIN
    IF NEW.transaction_type = 'OUT'
       AND fn_current_stock(NEW.product_id, NEW.warehouse_id) < NEW.quantity THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient stock for outgoing transaction';
    END IF;
END$$

CREATE TRIGGER trg_stock_entries_after_insert
AFTER INSERT ON stock_entries
FOR EACH ROW
BEGIN
    INSERT INTO warehouse_stock (warehouse_id, product_id, quantity_on_hand)
    VALUES (NEW.warehouse_id, NEW.product_id, NEW.quantity)
    ON DUPLICATE KEY UPDATE
        quantity_on_hand = quantity_on_hand + VALUES(quantity_on_hand),
        last_updated = CURRENT_TIMESTAMP;

    INSERT INTO inventory_history (
        product_id,
        warehouse_id,
        quantity,
        transaction_type,
        transaction_date,
        reference_entry_id,
        notes
    )
    VALUES (
        NEW.product_id,
        NEW.warehouse_id,
        NEW.quantity,
        'IN',
        NEW.entry_date,
        NEW.entry_id,
        CONCAT('Inbound stock. ', COALESCE(NEW.notes, ''))
    );
END$$

CREATE TRIGGER trg_inventory_history_after_insert
AFTER INSERT ON inventory_history
FOR EACH ROW
BEGIN
    IF NEW.transaction_type = 'OUT' THEN
        INSERT INTO warehouse_stock (warehouse_id, product_id, quantity_on_hand)
        VALUES (NEW.warehouse_id, NEW.product_id, 0)
        ON DUPLICATE KEY UPDATE last_updated = CURRENT_TIMESTAMP;

        UPDATE warehouse_stock
           SET quantity_on_hand = quantity_on_hand - NEW.quantity,
               last_updated = CURRENT_TIMESTAMP
         WHERE warehouse_id = NEW.warehouse_id
           AND product_id = NEW.product_id;
    END IF;
END$$

-- -------------------------
-- 5) STORED PROCEDURES
-- -------------------------

CREATE PROCEDURE sp_add_stock(
    IN p_product_id INT,
    IN p_warehouse_id INT,
    IN p_supplier_id INT,
    IN p_quantity INT,
    IN p_unit_cost DECIMAL(12,2),
    IN p_notes VARCHAR(255)
)
BEGIN
    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Quantity must be greater than 0';
    END IF;

    IF p_unit_cost <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unit cost must be greater than 0';
    END IF;

    INSERT INTO stock_entries (
        product_id,
        warehouse_id,
        supplier_id,
        quantity,
        unit_cost,
        entry_date,
        notes
    )
    VALUES (
        p_product_id,
        p_warehouse_id,
        p_supplier_id,
        p_quantity,
        p_unit_cost,
        NOW(),
        p_notes
    );
END$$

CREATE PROCEDURE sp_remove_stock(
    IN p_product_id INT,
    IN p_warehouse_id INT,
    IN p_quantity INT,
    IN p_notes VARCHAR(255)
)
BEGIN
    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Quantity must be greater than 0';
    END IF;

    IF fn_current_stock(p_product_id, p_warehouse_id) < p_quantity THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Not enough stock in warehouse';
    END IF;

    INSERT INTO inventory_history (
        product_id,
        warehouse_id,
        quantity,
        transaction_type,
        transaction_date,
        notes
    )
    VALUES (
        p_product_id,
        p_warehouse_id,
        p_quantity,
        'OUT',
        NOW(),
        p_notes
    );
END$$

CREATE PROCEDURE sp_restock_product(
    IN p_product_id INT,
    IN p_warehouse_id INT,
    IN p_quantity INT,
    IN p_unit_cost DECIMAL(12,2)
)
BEGIN
    DECLARE v_supplier_id INT;

    SELECT supplier_id
      INTO v_supplier_id
      FROM products
     WHERE product_id = p_product_id;

    CALL sp_add_stock(
        p_product_id,
        p_warehouse_id,
        v_supplier_id,
        p_quantity,
        p_unit_cost,
        'Automatic restock procedure'
    );
END$$

CREATE PROCEDURE sp_generate_inventory_report()
BEGIN
    SELECT
        w.warehouse_name,
        p.product_name,
        s.supplier_name,
        ws.quantity_on_hand,
        p.reorder_level,
        CASE
            WHEN ws.quantity_on_hand <= p.reorder_level THEN 'LOW STOCK'
            ELSE 'OK'
        END AS stock_status
    FROM warehouse_stock ws
    JOIN warehouses w ON ws.warehouse_id = w.warehouse_id
    JOIN products p ON ws.product_id = p.product_id
    JOIN suppliers s ON p.supplier_id = s.supplier_id
    ORDER BY w.warehouse_name, p.product_name;
END$$

CREATE PROCEDURE sp_seed_demo_data(IN p_target_entries INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE v_product_id INT;
    DECLARE v_warehouse_id INT;
    DECLARE v_supplier_id INT;
    DECLARE v_qty_in INT;
    DECLARE v_qty_out INT;
    DECLARE v_cost DECIMAL(12,2);

    WHILE i <= p_target_entries DO
        SET v_product_id = 1 + MOD(i - 1, 15);
        SET v_warehouse_id = 1 + MOD(i - 1, 5);

        SELECT supplier_id INTO v_supplier_id
          FROM products
         WHERE product_id = v_product_id;

        SET v_qty_in = 15 + MOD(i, 35);
        SET v_cost = 10 + MOD(i, 40);

        CALL sp_add_stock(
            v_product_id,
            v_warehouse_id,
            v_supplier_id,
            v_qty_in,
            v_cost,
            CONCAT('Seed inbound transaction #', i)
        );

        IF MOD(i, 3) = 0 THEN
            SET v_qty_out = 1 + MOD(i, 8);
            CALL sp_remove_stock(
                v_product_id,
                v_warehouse_id,
                v_qty_out,
                CONCAT('Seed outbound transaction #', i)
            );
        END IF;

        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;
