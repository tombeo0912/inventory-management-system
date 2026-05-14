from __future__ import annotations

from typing import Any, Iterable

from db import get_cursor


def fetch_all(query: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    with get_cursor(dictionary=True) as (_, cursor):
        cursor.execute(query, params or ())
        return list(cursor.fetchall())


def fetch_one(query: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
    with get_cursor(dictionary=True) as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchone()


def execute(query: str, params: Iterable[Any] | None = None) -> None:
    with get_cursor(dictionary=False) as (_, cursor):
        cursor.execute(query, params or ())


def callproc(name: str, args: list[Any]) -> None:
    with get_cursor(dictionary=False) as (_, cursor):
        cursor.callproc(name, args)


def callproc_fetch(name: str, args: list[Any] | None = None) -> list[dict[str, Any]]:
    """Call a stored procedure that returns a result set."""
    with get_cursor(dictionary=True) as (_, cursor):
        cursor.callproc(name, args or [])
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        return results


# =========================
# PRODUCT MANAGEMENT
# =========================
def list_products() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            p.product_id,
            p.product_name,
            p.unit_price,
            p.reorder_level,
            p.unit,
            s.supplier_name,
            p.is_active
        FROM products p
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        ORDER BY p.product_id
        """
    )


def add_product(
    product_name: str,
    description: str,
    unit_price: float,
    supplier_id: int,
    reorder_level: int,
    unit: str,
) -> None:
    execute(
        """
        INSERT INTO products
            (product_name, description, unit_price, supplier_id, reorder_level, unit)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (product_name, description, unit_price, supplier_id, reorder_level, unit),
    )


def update_product_price(product_id: int, new_price: float) -> None:
    execute(
        "UPDATE products SET unit_price = %s WHERE product_id = %s",
        (new_price, product_id),
    )


# =========================
# SUPPLIER MANAGEMENT
# =========================
def list_suppliers() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT supplier_id, supplier_name, phone_number, email, contact_person, status
        FROM suppliers
        ORDER BY supplier_id
        """
    )


def add_supplier(
    supplier_name: str,
    address: str,
    phone_number: str,
    email: str,
    contact_person: str,
) -> None:
    execute(
        """
        INSERT INTO suppliers
            (supplier_name, address, phone_number, email, contact_person)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (supplier_name, address, phone_number, email, contact_person),
    )


# =========================
# WAREHOUSE MANAGEMENT
# =========================
def list_warehouses() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT warehouse_id, warehouse_name, address, capacity, manager_name, phone_number
        FROM warehouses
        ORDER BY warehouse_id
        """
    )


def add_warehouse(
    warehouse_name: str,
    address: str,
    capacity: int,
    manager_name: str,
    phone_number: str,
) -> None:
    execute(
        """
        INSERT INTO warehouses
            (warehouse_name, address, capacity, manager_name, phone_number)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (warehouse_name, address, capacity, manager_name, phone_number),
    )


# =========================
# STOCK OPERATIONS
# =========================
def add_stock(
    product_id: int,
    warehouse_id: int,
    supplier_id: int,
    quantity: int,
    unit_cost: float,
    notes: str,
) -> None:
    callproc(
        "sp_add_stock",
        [product_id, warehouse_id, supplier_id, quantity, unit_cost, notes],
    )


def remove_stock(
    product_id: int,
    warehouse_id: int,
    quantity: int,
    notes: str,
) -> None:
    callproc(
        "sp_remove_stock",
        [product_id, warehouse_id, quantity, notes],
    )


def restock_product(
    product_id: int,
    warehouse_id: int,
    quantity: int,
    unit_cost: float,
) -> None:
    callproc(
        "sp_restock_product",
        [product_id, warehouse_id, quantity, unit_cost],
    )


# =========================
# REPORTS
# =========================
def get_stock_by_warehouse() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT warehouse_name, product_name, supplier_name, quantity_on_hand,
               reorder_level, unit, alert_status
        FROM vw_stock_by_warehouse
        ORDER BY warehouse_name, product_name
        """
    )


def get_low_stock_alerts() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT warehouse_name, product_name, supplier_name,
               quantity_on_hand, reorder_level, unit, alert_status
        FROM vw_low_stock_products
        ORDER BY quantity_on_hand ASC, warehouse_name, product_name
        """
    )


def get_supplier_delivery_history() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT supplier_name, product_name, total_deliveries,
               total_quantity_delivered, avg_unit_cost, last_delivery_date
        FROM vw_supplier_delivery_history
        ORDER BY total_quantity_delivered DESC, supplier_name, product_name
        """
    )


def get_inventory_history(limit: int = 50) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            ih.history_id,
            p.product_name,
            w.warehouse_name,
            ih.quantity,
            ih.transaction_type,
            ih.transaction_date,
            ih.notes
        FROM inventory_history ih
        JOIN products p ON ih.product_id = p.product_id
        JOIN warehouses w ON ih.warehouse_id = w.warehouse_id
        ORDER BY ih.transaction_date DESC, ih.history_id DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_current_stock(product_id: int, warehouse_id: int) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT
            p.product_name,
            w.warehouse_name,
            fn_current_stock(%s, %s) AS current_stock
        FROM products p
        CROSS JOIN warehouses w
        WHERE p.product_id = %s AND w.warehouse_id = %s
        """,
        (product_id, warehouse_id, product_id, warehouse_id),
    )


def get_stock_turnover() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            p.product_id,
            p.product_name,
            fn_stock_turnover(p.product_id) AS stock_turnover_rate
        FROM products p
        ORDER BY stock_turnover_rate DESC, p.product_name
        """
    )


def generate_full_inventory_report() -> list[dict[str, Any]]:
    """Call sp_generate_inventory_report() — full inventory with stock status."""
    return callproc_fetch("sp_generate_inventory_report")