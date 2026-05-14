# Demo Walkthrough

## SQL Demo
```sql
USE Personal_Finance;

SELECT COUNT(*) FROM suppliers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM warehouses;
SELECT COUNT(*) FROM stock_entries;
SELECT COUNT(*) FROM inventory_history;

CALL sp_generate_inventory_report();
SELECT * FROM vw_low_stock_products LIMIT 20;

CALL sp_add_stock(1, 1, 1, 20, 4.25, 'Demo inbound');
CALL sp_remove_stock(1, 1, 5, 'Demo outbound');

SELECT fn_current_stock(1, 1) AS current_stock;
SELECT fn_stock_turnover(1) AS stock_turnover;
```

## Python Demo
1. Run `python main.py`
2. Show "List products"
3. Show "List warehouses"
4. Use "Add stock"
5. Use "Remove stock"
6. Show "Low-stock alerts"
7. Show "Inventory history"

## Video Tips
- Keep the video between 5 and 10 minutes.
- Start from the assignment title and objective.
- End with conclusion + future improvements:
  - barcode scanning
  - ERP integration
  - demand forecasting
  - dashboard/web UI
