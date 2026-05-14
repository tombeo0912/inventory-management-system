-- VIEWS
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
