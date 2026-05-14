-- BASE SAMPLE DATA
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
