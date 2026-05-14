USE `Personal_Finance`;

-- 1) Current stock report
CALL sp_generate_inventory_report();

-- 2) Low-stock alert list
SELECT * FROM vw_low_stock_products;

-- 3) Supplier delivery summary
SELECT * FROM vw_supplier_delivery_history ORDER BY total_quantity_delivered DESC;

-- 4) Example business queries
SELECT warehouse_name, COUNT(*) AS total_products
FROM vw_stock_by_warehouse
GROUP BY warehouse_name
ORDER BY total_products DESC;

SELECT
    p.product_name,
    fn_stock_turnover(p.product_id) AS stock_turnover_rate
FROM products p
ORDER BY stock_turnover_rate DESC, p.product_name;

-- 5) Test stored procedures
-- CALL sp_add_stock(1, 1, 1, 25, 4.25, 'Manual test inbound');
-- CALL sp_remove_stock(1, 1, 5, 'Manual test outbound');
