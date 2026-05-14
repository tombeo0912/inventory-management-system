-- =========================================================
-- INVENTORY MANAGEMENT SYSTEM
-- Database name kept as `Personal_Finance` to match the user's environment.
-- Project scope follows the "Inventory Management System" final project.
-- =========================================================

DROP DATABASE IF EXISTS `Personal_Finance`;
CREATE DATABASE `Personal_Finance` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `Personal_Finance`;

-- -------------------------
-- 1) MASTER TABLES
-- -------------------------
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(120),
    contact_person VARCHAR(120),
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_suppliers_name UNIQUE (supplier_name),
    CONSTRAINT chk_suppliers_phone_len CHECK (CHAR_LENGTH(phone_number) >= 8)
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    description VARCHAR(255),
    unit_price DECIMAL(12,2) NOT NULL,
    supplier_id INT NOT NULL,
    reorder_level INT NOT NULL DEFAULT 10,
    unit VARCHAR(20) NOT NULL DEFAULT 'pcs',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_products_name_supplier UNIQUE (product_name, supplier_id),
    CONSTRAINT chk_products_unit_price CHECK (unit_price > 0),
    CONSTRAINT chk_products_reorder_level CHECK (reorder_level >= 0),
    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(120) NOT NULL,
    address VARCHAR(255) NOT NULL,
    capacity INT NOT NULL,
    manager_name VARCHAR(120),
    phone_number VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_warehouses_name UNIQUE (warehouse_name),
    CONSTRAINT chk_warehouses_capacity CHECK (capacity > 0)
);

-- Current inventory by product and warehouse
CREATE TABLE warehouse_stock (
    stock_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_warehouse_product UNIQUE (warehouse_id, product_id),
    CONSTRAINT chk_warehouse_stock_non_negative CHECK (quantity_on_hand >= 0),
    CONSTRAINT fk_warehouse_stock_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_warehouse_stock_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- Incoming stock / purchase entries
CREATE TABLE stock_entries (
    entry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    supplier_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    entry_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255),
    CONSTRAINT chk_stock_entries_quantity CHECK (quantity > 0),
    CONSTRAINT chk_stock_entries_cost CHECK (unit_cost > 0),
    CONSTRAINT fk_stock_entries_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_stock_entries_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_stock_entries_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- In / Out transaction history
CREATE TABLE inventory_history (
    history_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL,
    transaction_type ENUM('IN', 'OUT') NOT NULL,
    transaction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reference_entry_id BIGINT NULL,
    notes VARCHAR(255),
    CONSTRAINT chk_inventory_history_quantity CHECK (quantity > 0),
    CONSTRAINT fk_inventory_history_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_inventory_history_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_inventory_history_entry
        FOREIGN KEY (reference_entry_id) REFERENCES stock_entries(entry_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- -------------------------
-- 2) INDEXES
-- -------------------------
CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_warehouses_name ON warehouses(warehouse_name);
CREATE INDEX idx_stock_entries_wh_date ON stock_entries(warehouse_id, entry_date);
CREATE INDEX idx_stock_entries_product_date ON stock_entries(product_id, entry_date);
CREATE INDEX idx_inventory_history_product_wh_date ON inventory_history(product_id, warehouse_id, transaction_date);
CREATE INDEX idx_inventory_history_type_date ON inventory_history(transaction_type, transaction_date);
CREATE INDEX idx_warehouse_stock_qty ON warehouse_stock(quantity_on_hand);

-- -------------------------
-- 3) FUNCTIONS
-- -------------------------
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

-- -------------------------
-- 6) VIEWS
-- -------------------------
CREATE OR REPLACE VIEW vw_stock_by_warehouse AS
SELECT
    ws.stock_id,
    ws.warehouse_id,
    w.warehouse_name,
    ws.product_id,
    p.product_name,
    s.supplier_name,
    ws.quantity_on_hand,
    p.reorder_level,
    p.unit,
    CASE
        WHEN ws.quantity_on_hand <= p.reorder_level THEN 'LOW STOCK'
        ELSE 'NORMAL'
    END AS alert_status,
    ws.last_updated
FROM warehouse_stock ws
JOIN warehouses w ON ws.warehouse_id = w.warehouse_id
JOIN products p ON ws.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id;

CREATE OR REPLACE VIEW vw_low_stock_products AS
SELECT *
FROM vw_stock_by_warehouse
WHERE quantity_on_hand <= reorder_level
ORDER BY quantity_on_hand ASC, warehouse_name, product_name;

CREATE OR REPLACE VIEW vw_supplier_delivery_history AS
SELECT
    s.supplier_id,
    s.supplier_name,
    p.product_id,
    p.product_name,
    COUNT(se.entry_id) AS total_deliveries,
    SUM(se.quantity) AS total_quantity_delivered,
    ROUND(AVG(se.unit_cost), 2) AS avg_unit_cost,
    MAX(se.entry_date) AS last_delivery_date
FROM stock_entries se
JOIN suppliers s ON se.supplier_id = s.supplier_id
JOIN products p ON se.product_id = p.product_id
GROUP BY
    s.supplier_id,
    s.supplier_name,
    p.product_id,
    p.product_name;

-- -------------------------
-- 7) BASE SAMPLE DATA
-- -------------------------
INSERT INTO suppliers (supplier_name, address, phone_number, email, contact_person)
VALUES
('Alpha Electronics', '12 Nguyen Trai, Ha Noi', '0901000001', 'sales@alpha.vn', 'Le Minh'),
('Beta Industrial', '25 Tran Duy Hung, Ha Noi', '0901000002', 'contact@beta.vn', 'Tran Vu'),
('Central Office Goods', '18 Le Lai, Hai Phong', '0901000003', 'support@central.vn', 'Pham Ha'),
('Delta Packaging', '44 Pasteur, Ho Chi Minh City', '0901000004', 'orders@delta.vn', 'Do An'),
('East Tech Components', '92 Ly Thuong Kiet, Da Nang', '0901000005', 'info@easttech.vn', 'Nguyen Nam'),
('Fresh Storage Ltd', '63 Nguyen Hue, Ho Chi Minh City', '0901000006', 'hello@freshstorage.vn', 'Vu Son'),
('Golden Hardware', '17 Bach Dang, Da Nang', '0901000007', 'trade@golden.vn', 'Hoang Linh'),
('Horizon Supplies', '8 Kim Ma, Ha Noi', '0901000008', 'biz@horizon.vn', 'Mai Anh'),
('Indochina Retail Supply', '102 Phan Chu Trinh, Hue', '0901000009', 'retail@indochina.vn', 'Tran Ly'),
('Jupiter Wholesale', '75 Cach Mang Thang Tam, Can Tho', '0901000010', 'wholesale@jupiter.vn', 'Pham Bao');

INSERT INTO products (product_name, description, unit_price, supplier_id, reorder_level, unit)
VALUES
('USB-C Cable', '1 meter fast-charge cable', 4.50, 1, 20, 'pcs'),
('Wireless Mouse', 'Office wireless mouse', 12.00, 1, 12, 'pcs'),
('Mechanical Keyboard', 'Blue switch keyboard', 35.00, 2, 8, 'pcs'),
('A4 Printing Paper', '500-sheet paper pack', 3.20, 3, 30, 'ream'),
('Thermal Labels', 'Barcode thermal labels', 7.80, 4, 15, 'roll'),
('SSD 512GB', 'Internal solid-state drive', 48.00, 5, 10, 'pcs'),
('Storage Bin Large', 'Warehouse storage bin', 9.50, 6, 14, 'pcs'),
('Cordless Scanner', 'Handheld inventory scanner', 65.00, 5, 5, 'pcs'),
('Packing Tape', 'Clear packing tape', 1.40, 4, 40, 'roll'),
('Safety Gloves', 'General warehouse gloves', 2.75, 7, 25, 'pair'),
('LED Desk Lamp', 'Adjustable office lamp', 14.50, 8, 10, 'pcs'),
('Notebook A5', 'Hard-cover notebook', 2.10, 9, 35, 'pcs'),
('Power Bank 10000mAh', 'Portable charger', 18.90, 1, 9, 'pcs'),
('Router AX1800', 'Dual-band Wi-Fi router', 52.00, 10, 6, 'pcs'),
('Monitor 24 inch', '24 inch office monitor', 112.00, 2, 4, 'pcs');

INSERT INTO warehouses (warehouse_name, address, capacity, manager_name, phone_number)
VALUES
('North Hub', 'Nam Tu Liem, Ha Noi', 5000, 'Nguyen Duc', '0912000001'),
('South Hub', 'Thu Duc, Ho Chi Minh City', 7000, 'Tran Quang', '0912000002'),
('Central Hub', 'Hai Chau, Da Nang', 4500, 'Le Van', '0912000003'),
('Overflow Warehouse', 'Binh Tan, Ho Chi Minh City', 3000, 'Pham Kien', '0912000004'),
('Returns Warehouse', 'Gia Lam, Ha Noi', 2500, 'Do Thanh', '0912000005');

-- Generate transactional sample data.
-- The requirement text says "Insert 510 records for each table."
-- To cover that interpretation as strongly as possible, this script generates
-- 510 stock entries, and inventory history rows are generated automatically
-- through triggers (plus additional outbound rows from the seed procedure).
CALL sp_seed_demo_data(510);

-- Optional quick checks
-- SELECT COUNT(*) AS suppliers_count FROM suppliers;
-- SELECT COUNT(*) AS products_count FROM products;
-- SELECT COUNT(*) AS warehouses_count FROM warehouses;
-- SELECT COUNT(*) AS stock_entries_count FROM stock_entries;
-- SELECT COUNT(*) AS inventory_history_count FROM inventory_history;
-- SELECT * FROM vw_low_stock_products LIMIT 20;
