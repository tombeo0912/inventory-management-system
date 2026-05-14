-- INDEXES
-- -------------------------
CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_warehouses_name ON warehouses(warehouse_name);
CREATE INDEX idx_stock_entries_wh_date ON stock_entries(warehouse_id, entry_date);
CREATE INDEX idx_stock_entries_product_date ON stock_entries(product_id, entry_date);
CREATE INDEX idx_inventory_history_product_wh_date ON inventory_history(product_id, warehouse_id, transaction_date);
CREATE INDEX idx_inventory_history_type_date ON inventory_history(transaction_type, transaction_date);
CREATE INDEX idx_warehouse_stock_qty ON warehouse_stock(quantity_on_hand);
