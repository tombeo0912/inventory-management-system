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
