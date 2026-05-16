<h1 align="center">📦 Inventory Management System</h1>

<p align="center">
  <strong>A modern inventory management system built with MySQL and Python</strong>
</p>

<p align="center">
  <strong>Student:</strong> Vũ Đức Anh &nbsp;|&nbsp;
  <strong>Student ID:</strong> 11245840<br/>
  Final Project — Database Management Course · NEU College of Technology
</p>

<p align="center">
  <img src="docs/screenshots/gui_dashboard.png" width="900" alt="GUI Dashboard Preview"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-2563EB?style=flat-square"/>
  <img src="https://img.shields.io/badge/CLI-17%20Features-111827?style=flat-square"/>
</p>

---

## 📘 Project Overview

This project is a final assignment for the **Database Management** course. It implements a complete **Inventory Management System** using **MySQL** and **Python**, with both a **CLI application** and a **modern GUI built with CustomTkinter**.

The system supports:

- product management
- supplier management
- warehouse management
- inbound and outbound stock operations
- low-stock alerts
- delivery history and inventory history
- full inventory reporting
- stock turnover reporting with chart visualization

---

## ✨ Main Features

### Database Features
- Relational database design with **PK**, **FK**, and **constraints**
- **Indexes** for query performance
- **Views** for reporting and stock monitoring
- **Stored Procedures** for stock in / stock out operations
- **Functions** for stock lookup and turnover calculation
- **Triggers** for automatic inventory history updates
- **Security roles** and backup notes

### Application Features
- **CLI version** with 17 functional options
- **GUI version** with dashboard and multiple management screens
- Product, supplier, and warehouse CRUD operations
- Stock add / remove workflows
- Low-stock alerts
- Delivery history
- Inventory history
- Full inventory report
- Stock turnover chart

---

## 📸 Screenshots

<table>
  <tr>
    <td align="center">
      <img src="docs/screenshots/gui_dashboard.png" width="420" alt="Dashboard"/><br/>
      <em>Dashboard Overview</em>
    </td>
    <td align="center">
      <img src="docs/screenshots/gui_stock.png" width="420" alt="Stock by Warehouse"/><br/>
      <em>Stock by Warehouse</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/screenshots/gui_chart.png" width="420" alt="Turnover Report"/><br/>
      <em>Stock Turnover Report</em>
    </td>
    <td align="center">
      <img src="docs/screenshots/gui_login.png" width="420" alt="Login"/><br/>
      <em>Login Screen</em>
    </td>
  </tr>
</table>

---

## 💻 CLI Preview

<p align="center">
  <img src="docs/cli_preview.png" width="760" alt="CLI Preview"/>
</p>

---

## 🧱 Database Design

### ER Diagram
<p align="center">
  <img src="docs/ERDiagram of Inventory Management System.png" width="900" alt="ER Diagram"/>
</p>

### Relational Schema
<p align="center">
  <img src="docs/Relational Schema Diagram of the Inventory Management System.png" width="900" alt="Relational Schema"/>
</p>

### Main Tables
- `suppliers`
- `products`
- `warehouses`
- `warehouse_stock`
- `stock_entries`
- `inventory_history`

---

## 🛠️ Tech Stack

- **Database:** MySQL
- **Backend / Application Logic:** Python
- **GUI:** CustomTkinter
- **CLI:** Python terminal application
- **Visualization:** Matplotlib
- **Documentation:** Markdown / PDF report

---

## 🚀 How to Run

### 1) Clone or download the project
```bash
git clone https://github.com/tombeo0912/inventory-management-system.git
cd inventory_final_project
```

### 2) Create the database
You can run the full setup script:

```sql
SOURCE sql/01_full_project.sql;
```

Or run the scripts step by step:

```sql
SOURCE sql/01_create_database_and_tables.sql;
SOURCE sql/02_indexes.sql;
SOURCE sql/03_functions_triggers_procedures.sql;
SOURCE sql/04_views.sql;
SOURCE sql/05_sample_data.sql;
SOURCE sql/06_security_backup.sql;
SOURCE sql/07_demo_queries.sql;
```

### 3) Install Python dependencies
```bash
cd python_app
pip install -r requirements.txt
```

### 4) Configure environment variables
Create a `.env` file based on `.env.example` and set your MySQL connection information.

Example:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=inventory_management
MYSQL_PORT=3306
```

### 5) Run the application

#### Run CLI version
```bash
python main.py
```

#### Run GUI version
```bash
python GUI.py
```

---

## 🔐 Demo Accounts

Default demo accounts used in the application:

- **Admin**
  - Username: `admin`
  - Password: `admin123`

- **Inventory Manager**
  - Username: `manager`
  - Password: `manager123`

> These credentials are intended for demonstration/testing purposes only.

---

## 📂 Project Structure

```text
inventory_final_project/
│
├── assets/
│   └── original_assignment.pdf          ← Original assignment file
│
├── docs/
│   ├── screenshots/
│   │   ├── gui_chart.png                ← GUI turnover report screenshot
│   │   ├── gui_dashboard.png            ← GUI dashboard screenshot
│   │   ├── gui_login.png                ← GUI login screenshot
│   │   └── gui_stock.png                ← GUI stock/warehouse screenshot
│   │
│   ├── cli_preview.png                  ← CLI application screenshot
│   ├── ERDiagram of Inventory Management System.png
│   │                                     ← ER diagram image
│   ├── inventory_erd.mmd                ← ERD source (Mermaid)
│   ├── Relational Schema Diagram of the Inventory Management System.png
│   │                                     ← Relational schema diagram
│   └── relational_schema.md             ← Relational schema documentation
│
├── python_app/
│   ├── __pycache__/                     ← Python cache files
│   ├── .env.example                     ← Environment variable template
│   ├── db.py                            ← MySQL connection helper
│   ├── GUI.py                           ← GUI application (CustomTkinter)
│   ├── main.py                          ← CLI application
│   ├── requirements.txt                 ← Python dependencies
│   └── services.py                      ← Business logic / DB queries
│
├── sql/
│   ├── 01_create_database_and_tables.sql
│   │                                     ← Create database and tables
│   ├── 01_full_project.sql              ← Run this file to set up the full project
│   ├── 02_indexes.sql                   ← Index definitions
│   ├── 03_functions_triggers_procedures.sql
│   │                                     ← Stored procedures, functions, triggers
│   ├── 04_views.sql                     ← SQL views
│   ├── 05_sample_data.sql               ← Sample data insertion
│   ├── 06_security_backup.sql           ← Security roles and backup notes
│   └── 07_demo_queries.sql              ← Demo/test queries
│
├── submission/
│   └── final_submission_report_....pdf  ← Final report PDF
│
└── README.md                            ← Project overview and usage guide
```

---

## 📋 Implemented Functionalities

### CLI / GUI Functional Modules
1. List products  
2. Add product  
3. Update product price  
4. List suppliers  
5. Add supplier  
6. List warehouses  
7. Add warehouse  
8. Add stock (inbound)  
9. Remove stock (outbound)  
10. View stock by warehouse  
11. Low-stock alerts  
12. Supplier delivery history  
13. Inventory history  
14. Check current stock  
15. Stock turnover report  
16. Full inventory report  
17. Turnover chart visualization  

---

## 🧪 Validation and Business Rules

The system validates business rules at both application and database levels:

- invalid supplier ID is rejected by foreign key constraints
- unit price must be greater than 0
- reorder level must be 0 or greater
- warehouse capacity must be greater than 0
- phone number length is validated
- outbound stock cannot exceed available quantity
- low-stock alert is triggered when current stock is less than or equal to reorder level

---

## 📎 Included Deliverables

This repository contains the core project deliverables:

- MySQL scripts
- Python source code
- ER diagram
- relational schema documentation
- CLI and GUI screenshots
- final report PDF
- original assignment PDF

---

## 🎥 Demo

- **GitHub Repository:** `https://github.com/tombeo0912/inventory-management-system.git`
- **YouTube Demo:** `https://youtu.be/6MoBctTNVW4`

---

## 📌 Notes

- The GUI version is intended as the main presentation interface.
- The CLI version is preserved as a functional alternative and for feature completeness.
- The database includes sample data for demonstration and reporting.
- Some screenshots and deliverables are stored in the `docs/` and `submission/` folders.

---

## 👨‍🎓 Author

| | |
|---|---|
| **Họ tên** | Vũ Đức Anh |
| **Student ID** | 11245840 |
| **Class** | DSEB66B |
| **University** | National Economics University |
---

## 📚 References

- MySQL Documentation  
- Python Documentation  
- CustomTkinter Documentation  
- Matplotlib Documentation  
- Course materials and project assignment provided by NEU College of Technology
