# Relational Schema

**Database name:** `Personal_Finance`  
**Academic scope:** Inventory Management System

## 1) Core entities

### Suppliers
`Suppliers(`  
`SupplierID PK, SupplierName UNIQUE, Address, PhoneNumber, Email, ContactPerson, Status, CreatedAt`  
`)`

### Products
`Products(`  
`ProductID PK, ProductName, Description, UnitPrice, SupplierID FK -> Suppliers.SupplierID, ReorderLevel, Unit, IsActive, CreatedAt, UNIQUE(ProductName, SupplierID)`  
`)`

### Warehouses
`Warehouses(`  
`WarehouseID PK, WarehouseName UNIQUE, Address, Capacity, ManagerName, PhoneNumber, CreatedAt`  
`)`

### WarehouseStock
`WarehouseStock(`  
`StockID PK, WarehouseID FK -> Warehouses.WarehouseID, ProductID FK -> Products.ProductID, QuantityOnHand, LastUpdated, UNIQUE(WarehouseID, ProductID)`  
`)`

### StockEntries
`StockEntries(`  
`EntryID PK, ProductID FK -> Products.ProductID, WarehouseID FK -> Warehouses.WarehouseID, SupplierID FK -> Suppliers.SupplierID, Quantity, UnitCost, EntryDate, Notes`  
`)`

### InventoryHistory
`InventoryHistory(`  
`HistoryID PK, ProductID FK -> Products.ProductID, WarehouseID FK -> Warehouses.WarehouseID, Quantity, TransactionType, TransactionDate, ReferenceEntryID FK -> StockEntries.EntryID, Notes`  
`)`

## 2) Cardinality summary

- One supplier supplies many products.
- One supplier can appear in many stock entries.
- One warehouse receives many stock entries.
- One product can have many stock entries and many history transactions.
- One product in one warehouse has one current-stock row in `WarehouseStock`.
- One stock entry can generate one inbound record in `InventoryHistory`.

## 3) Design rationale

The assignment requires the following minimum tables: **Products, Suppliers, Warehouses, StockEntries, InventoryHistory**.  
To make the solution stronger and more realistic, one helper table was added:

- `WarehouseStock`: stores the current balance of each product in each warehouse.
  This avoids recalculating stock totals from history every time and makes
  alerts, views, procedures, and Python reporting much faster.

## 4) Normalization notes

- The schema is in at least **3NF** for the project scope.
- Supplier information is stored once in `Suppliers`.
- Product-to-supplier ownership is maintained with a foreign key.
- Transaction facts are separated into inbound entries (`StockEntries`) and
  in/out movement logs (`InventoryHistory`).
