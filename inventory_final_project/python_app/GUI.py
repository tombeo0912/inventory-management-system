"""
Inventory Management System — GUI Application (v2 Premium)
Dark modern theme · Role-based access · 17 features
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import sys
import mysql.connector

try:
    import customtkinter as ctk
except ImportError:
    print("ERROR: customtkinter not installed. Run: pip install customtkinter")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

import services

# ─────────────────────────────────────────────
#  THEME — Dark Modern Premium
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

C = {
    # Backgrounds
    "bg":           "#0B1020",
    "sidebar":      "#111C3A",
    "card":         "#151F42",
    "card_hover":   "#1A2550",
    "border":       "#243056",
    "input_bg":     "#111C3A",

    # Text
    "text":         "#F5F7FB",
    "text_sec":     "#9AA4C7",
    "text_dim":     "#6B7499",

    # Accent
    "accent":       "#5B8CFF",
    "accent_hover": "#4A7AEE",
    "accent_soft":  "#1A2B5F",

    # Status
    "success":      "#22C55E",
    "success_soft": "rgba(34,197,94,0.12)",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "danger_soft":  "#2A1520",

    # Table
    "tbl_header":   "#1D2A52",
    "tbl_row1":     "#101936",
    "tbl_row2":     "#0F1730",
    "tbl_low":      "#1F1318",
    "tbl_out_bg":   "#1C1520",
}

USERS = {
    "admin":   {"password": "admin123",   "role": "ADMIN"},
    "manager": {"password": "manager123", "role": "MANAGER"},
}

MANAGER_ALLOWED = {"1", "4", "6", "8", "10", "11", "12", "13", "14", "15", "16", "17", "0"}


def friendly_db_error(exc: Exception) -> tuple[str, str]:
    msg = str(exc)
    low = msg.lower()

    # Foreign key / invalid ID
    if "fk_products_supplier" in low or ("foreign key" in low and "supplier" in low):
        return ("Invalid Supplier ID", "Supplier ID does not exist. Please enter a valid Supplier ID.")

    if "fk_stock_entries_product" in low or ("foreign key" in low and "product" in low):
        return ("Invalid Product ID", "Product ID does not exist. Please enter a valid Product ID.")

    if "fk_stock_entries_warehouse" in low or ("foreign key" in low and "warehouse" in low):
        return ("Invalid Warehouse ID", "Warehouse ID does not exist. Please enter a valid Warehouse ID.")

    if "fk_stock_entries_supplier" in low:
        return ("Invalid Supplier ID", "Supplier ID does not exist. Please enter a valid Supplier ID.")

    # Check constraints
    if "chk_products_unit_price" in low:
        return ("Invalid Unit Price", "Unit price must be greater than 0.")

    if "chk_products_reorder_level" in low:
        return ("Invalid Reorder Level", "Reorder level must be 0 or greater.")

    if "chk_suppliers_phone_len" in low:
        return ("Invalid Phone Number", "Phone number must contain at least 8 digits.")

    if "chk_warehouses_capacity" in low:
        return ("Invalid Capacity", "Warehouse capacity must be greater than 0.")

    if "chk_stock_entries_quantity" in low or "quantity must be greater than 0" in low:
        return ("Invalid Quantity", "Quantity must be greater than 0.")

    if "chk_stock_entries_cost" in low:
        return ("Invalid Unit Cost", "Unit cost must be greater than 0.")

    # Business rule from stored procedure
    if "not enough stock in warehouse" in low:
        return ("Insufficient Stock", "Not enough stock in this warehouse to complete the outbound transaction.")

    # Duplicate values
    if "uq_products_name_supplier" in low or "duplicate entry" in low:
        return ("Duplicate Product", "This product already exists for the selected supplier.")

    if "uq_suppliers_name" in low:
        return ("Duplicate Supplier", "A supplier with this name already exists.")

    if "uq_warehouses_name" in low:
        return ("Duplicate Warehouse", "A warehouse with this name already exists.")

    # Numeric parsing / empty input
    if isinstance(exc, ValueError):
        return ("Invalid Input", "Please enter valid numeric values in all required numeric fields.")

    # Fallback
    return ("Database Error", msg)
# Font shortcuts
F_H1      = ("Segoe UI", 28, "bold")
F_H2      = ("Segoe UI", 20, "bold")
F_KPI_NUM = ("Segoe UI", 36, "bold")
F_KPI_LBL = ("Segoe UI", 13)
F_KPI_SUB = ("Segoe UI", 11)
F_MENU    = ("Segoe UI", 13)
F_MENU_SM = ("Segoe UI", 10, "bold")
F_BODY    = ("Segoe UI", 13)
F_TBL     = ("Segoe UI", 12)
F_TBL_H   = ("Segoe UI", 12, "bold")
F_BTN     = ("Segoe UI", 14, "bold")
F_INPUT   = ("Segoe UI", 13)
F_LABEL   = ("Segoe UI", 12)


# ═══════════════════════════════════════════════
#  LOGIN WINDOW
# ═══════════════════════════════════════════════
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory System — Login")
        self.geometry("460x560")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.user = None

        # Logo
        ctk.CTkLabel(self, text="📦", font=("Segoe UI Emoji", 48)).pack(pady=(45, 8))
        ctk.CTkLabel(self, text="Inventory Management",
                     font=("Segoe UI", 22, "bold"), text_color=C["text"]).pack()
        ctk.CTkLabel(self, text="Sign in to your account",
                     font=F_KPI_LBL, text_color=C["text_sec"]).pack(pady=(2, 28))

        # Card
        card = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=20,
                            border_width=1, border_color=C["border"])
        card.pack(padx=50, fill="x")

        # Role
        ctk.CTkLabel(card, text="ROLE", font=F_MENU_SM,
                     text_color=C["text_dim"]).pack(anchor="w", padx=28, pady=(24, 6))
        self.role_var = ctk.StringVar(value="admin")
        rf = ctk.CTkFrame(card, fg_color="transparent")
        rf.pack(fill="x", padx=28)
        for val, label in [("admin", "Admin"), ("manager", "Manager")]:
            ctk.CTkRadioButton(
                rf, text=label, variable=self.role_var, value=val,
                font=F_BODY, fg_color=C["accent"], hover_color=C["accent_hover"],
                text_color=C["text"]
            ).pack(side="left", padx=(0, 24))

        # Password
        ctk.CTkLabel(card, text="PASSWORD", font=F_MENU_SM,
                     text_color=C["text_dim"]).pack(anchor="w", padx=28, pady=(18, 6))
        self.pw = ctk.CTkEntry(
            card, show="●", font=F_INPUT, height=42,
            placeholder_text="Enter password...",
            fg_color=C["input_bg"], border_color=C["border"], corner_radius=10
        )
        self.pw.pack(fill="x", padx=28)
        self.pw.bind("<Return>", lambda e: self._login())

        # Button
        ctk.CTkButton(
            card, text="Sign In", font=F_BTN,
            fg_color=C["accent"], hover_color=C["accent_hover"],
            height=44, corner_radius=12, command=self._login
        ).pack(fill="x", padx=28, pady=(22, 24))

        # Error
        self.err = ctk.CTkLabel(self, text="", font=F_LABEL, text_color=C["danger"])
        self.err.pack(pady=(12, 0))

        # Hint
        ctk.CTkLabel(self, text="admin / admin123  ·  manager / manager123",
                     font=F_KPI_SUB, text_color=C["text_dim"]).pack(side="bottom", pady=18)

    def _login(self):
        u = USERS.get(self.role_var.get())
        if u and u["password"] == self.pw.get():
            self.user = {"username": self.role_var.get(), "role": u["role"]}
            self.destroy()
        else:
            self.err.configure(text="Incorrect password. Try again.")
            self.pw.delete(0, "end")


# ═══════════════════════════════════════════════
#  DATA TABLE
# ═══════════════════════════════════════════════
class DataTable(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)

    def display(self, rows: list[dict], highlight_col: str | None = None,
                highlight_val: str = "LOW STOCK"):
        for w in self.winfo_children():
            w.destroy()

        if not rows:
            ctk.CTkLabel(self, text="No data found.", font=F_BODY,
                         text_color=C["text_dim"]).pack(pady=40)
            return

        headers = list(rows[0].keys())

        s = ttk.Style()
        s.theme_use("clam")
        s.configure("T.Treeview",
                     background=C["tbl_row1"], foreground=C["text"],
                     fieldbackground=C["tbl_row1"], rowheight=34,
                     font=F_TBL, borderwidth=0)
        s.configure("T.Treeview.Heading",
                     background=C["tbl_header"], foreground=C["text"],
                     font=F_TBL_H, relief="flat", borderwidth=0)
        s.map("T.Treeview",
              background=[("selected", C["accent_soft"])],
              foreground=[("selected", C["text"])])
        s.map("T.Treeview.Heading",
              background=[("active", C["card"])])

        wrap = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        wrap.pack(fill="both", expand=True)

        sy = ttk.Scrollbar(wrap, orient="vertical")
        sx = ttk.Scrollbar(wrap, orient="horizontal")
        tree = ttk.Treeview(wrap, columns=headers, show="headings",
                            style="T.Treeview",
                            yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.config(command=tree.yview)
        sx.config(command=tree.xview)
        sy.pack(side="right", fill="y", padx=(0, 2), pady=2)
        sx.pack(side="bottom", fill="x", padx=2, pady=(0, 2))
        tree.pack(fill="both", expand=True, padx=2, pady=2)

        for h in headers:
            tree.heading(h, text=h.replace("_", " ").title(), anchor="w")
            maxw = max(len(str(h)), *(len(str(r.get(h, ""))) for r in rows))
            tree.column(h, width=min(maxw * 10 + 20, 260), anchor="w")

        tree.tag_configure("low",    background=C["tbl_low"],  foreground="#F87171")
        tree.tag_configure("ok",     foreground=C["success"])
        tree.tag_configure("out",    background=C["tbl_out_bg"], foreground="#FB923C")
        tree.tag_configure("in_tx",  foreground="#4ADE80")
        tree.tag_configure("even",   background=C["tbl_row1"])
        tree.tag_configure("odd",    background=C["tbl_row2"])

        for i, row in enumerate(rows):
            vals = [str(row.get(h, "")) for h in headers]
            alert = str(row.get("alert_status", "") or row.get("stock_status", ""))
            tx = str(row.get("transaction_type", ""))

            if alert in ("LOW STOCK",):
                tag = "low"
            elif alert in ("NORMAL", "OK"):
                tag = "ok"
            elif tx == "OUT":
                tag = "out"
            elif tx == "IN":
                tag = "in_tx"
            else:
                tag = "even" if i % 2 == 0 else "odd"

            tree.insert("", "end", values=vals, tags=(tag,))


# ═══════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════
class MainApp(ctk.CTk):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.title(f"Inventory Management System — [{user['role']}]")
        self.geometry("1320x800")
        self.minsize(1040, 620)
        self.configure(fg_color=C["bg"])
        self.active_page = None

        self._build_sidebar()
        self._build_content()
        self._navigate("Dashboard", self._page_dashboard)

    # ─────────────────────────────────────
    #  SIDEBAR
    # ─────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=C["sidebar"], width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo (fixed top)
        top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        top.pack(fill="x", pady=(18, 6))
        ctk.CTkLabel(top, text="📦", font=("Segoe UI Emoji", 26)).pack()
        ctk.CTkLabel(top, text="Inventory System", font=("Segoe UI", 14, "bold"),
                     text_color=C["text"]).pack(pady=(2, 0))
        rc = C["success"] if self.user["role"] == "ADMIN" else C["warning"]
        ctk.CTkLabel(top, text=self.user["role"], font=F_MENU_SM, text_color=rc).pack(pady=(1, 0))

        # Logout (fixed bottom)
        bot = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bot.pack(side="bottom", fill="x", padx=14, pady=(6, 14))
        ctk.CTkButton(bot, text="Logout", font=("Segoe UI", 13),
                      fg_color="#2A1520", hover_color="#3A1F2A",
                      text_color=C["danger"], height=38, corner_radius=10,
                      command=self._logout).pack(fill="x")

        # Scrollable menu
        menu = ctk.CTkScrollableFrame(self.sidebar, fg_color=C["sidebar"],
                                       scrollbar_button_color=C["border"],
                                       scrollbar_button_hover_color=C["accent"])
        menu.pack(fill="both", expand=True, padx=0, pady=0)

        # VIEWS section
        self._section_label(menu, "VIEWS")
        self.nav_btns = {}
        views = [
            ("Dashboard",        "📊", self._page_dashboard),
            ("Products",         "📋", self._page_products),
            ("Suppliers",        "🏭", self._page_suppliers),
            ("Warehouses",       "🏢", self._page_warehouses),
            ("Stock / Warehouse","📦", self._page_stock),
            ("Low-Stock Alerts", "⚠️",  self._page_low_stock),
            ("Turnover Report",  "📈", self._page_turnover),
            ("Inventory History","📜", self._page_history),
            ("Full Report",      "📄", self._page_full_report),
            ("Delivery History", "🔀", self._page_delivery),
            ("Check Stock",      "🔍", self._page_check_stock),
        ]
        for label, icon, cmd in views:
            self._nav_btn(menu, f"{icon}  {label}", label, cmd)

        # ACTIONS section
        self._section_label(menu, "ACTIONS")
        actions = [
            ("Add Stock",     "➕", self._form_add_stock,     True),
            ("Remove Stock",  "➖", self._form_remove_stock,  False),
            ("Add Product",   "📝", self._form_add_product,   False),
            ("Update Price",  "✏️",  self._form_update_price,  False),
            ("Add Supplier",  "🏭", self._form_add_supplier,  False),
            ("Add Warehouse", "🏢", self._form_add_warehouse, False),
        ]
        for label, icon, cmd, mgr_ok in actions:
            blocked = self.user["role"] == "MANAGER" and not mgr_ok
            self._nav_btn(menu, f"{icon}  {label}", label, cmd,
                          blocked=blocked)

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=f"  {text}", font=F_MENU_SM,
                     text_color=C["text_dim"]).pack(anchor="w", padx=10, pady=(14, 4))

    def _nav_btn(self, parent, text, key, cmd, blocked=False):
        if blocked:
            btn = ctk.CTkButton(
                parent, text=f"🔒  {text.split('  ',1)[1]}", font=F_MENU,
                fg_color="transparent", text_color=C["text_dim"],
                hover_color=C["sidebar"], anchor="w", height=36,
                corner_radius=10, command=lambda: None)
        else:
            btn = ctk.CTkButton(
                parent, text=text, font=F_MENU,
                fg_color="transparent", hover_color=C["accent_soft"],
                text_color=C["text_sec"], anchor="w", height=36,
                corner_radius=10,
                command=lambda k=key, c=cmd: self._navigate(k, c))
        btn.pack(fill="x", padx=8, pady=1)
        self.nav_btns[key] = btn

    def _navigate(self, key, page_fn):
        # Reset all nav buttons
        for k, btn in self.nav_btns.items():
            if btn.cget("text_color") != C["text_dim"]:  # skip blocked
                btn.configure(fg_color="transparent", text_color=C["text_sec"])
        # Highlight active
        if key in self.nav_btns and self.nav_btns[key].cget("text_color") != C["text_dim"]:
            self.nav_btns[key].configure(fg_color=C["accent_soft"], text_color=C["text"])
        self.active_page = key
        page_fn()

    # ─────────────────────────────────────
    #  CONTENT AREA
    # ─────────────────────────────────────
    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _title(self, text, sub=""):
        ctk.CTkLabel(self.content, text=text, font=F_H1,
                     text_color=C["text"]).pack(anchor="w", padx=36, pady=(28, 2))
        if sub:
            ctk.CTkLabel(self.content, text=sub, font=F_LABEL,
                         text_color=C["text_sec"]).pack(anchor="w", padx=36, pady=(0, 16))

    # ─────────────────────────────────────
    #  DASHBOARD
    # ─────────────────────────────────────
    def _page_dashboard(self):
        self._clear()
        self._title("Dashboard", f"Welcome back, {self.user['username'].capitalize()}")

        # KPI cards
        kpi_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=36, pady=(0, 12))

        kpis = [
            ("Products",   len(services.list_products()),        C["accent"],  "📋"),
            ("Suppliers",  len(services.list_suppliers()),       "#06B6D4",    "🏭"),
            ("Warehouses", len(services.list_warehouses()),      C["warning"], "🏢"),
            ("Low Stock",  len(services.get_low_stock_alerts()), C["danger"],  "⚠️"),
        ]
        for i, (label, count, color, icon) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=C["card"], corner_radius=16,
                                border_width=1, border_color=C["border"])
            card.pack(side="left", fill="both", expand=True,
                      padx=(0 if i == 0 else 6, 6 if i < 3 else 0))
            card.pack_propagate(False)
            card.configure(height=140)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(expand=True)
            ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 24)).pack(pady=(0, 4))
            ctk.CTkLabel(inner, text=str(count), font=F_KPI_NUM,
                         text_color=color).pack()
            ctk.CTkLabel(inner, text=label, font=F_KPI_LBL,
                         text_color=C["text_sec"]).pack(pady=(0, 2))
            ctk.CTkLabel(inner, text="Updated just now", font=F_KPI_SUB,
                         text_color=C["text_dim"]).pack()

        # Recent transactions
        hdr = ctk.CTkFrame(self.content, fg_color="transparent")
        hdr.pack(fill="x", padx=36, pady=(14, 6))
        ctk.CTkLabel(hdr, text="Recent Transactions", font=F_H2,
                     text_color=C["text"]).pack(side="left")
        ctk.CTkLabel(hdr, text="Last 20 entries", font=F_KPI_SUB,
                     text_color=C["text_dim"]).pack(side="right")

        tbl = DataTable(self.content)
        tbl.pack(fill="both", expand=True, padx=36, pady=(0, 24))
        tbl.display(services.get_inventory_history(20),
                    highlight_col="transaction_type", highlight_val="OUT")

    # ─────────────────────────────────────
    #  DATA PAGES
    # ─────────────────────────────────────
    def _simple_page(self, title, sub, rows, hl_col=None, hl_val="LOW STOCK"):
        self._clear()
        self._title(title, sub)
        tbl = DataTable(self.content)
        tbl.pack(fill="both", expand=True, padx=36, pady=(0, 24))
        tbl.display(rows, hl_col, hl_val)

    def _page_products(self):
        self._simple_page("Products", "All products in the system",
                          services.list_products())

    def _page_suppliers(self):
        self._simple_page("Suppliers", "Supplier contacts and status",
                          services.list_suppliers())

    def _page_warehouses(self):
        self._simple_page("Warehouses", "Locations and capacity",
                          services.list_warehouses())

    def _page_stock(self):
        self._simple_page("Stock by Warehouse", "Current inventory levels",
                          services.get_stock_by_warehouse(),
                          "alert_status", "LOW STOCK")

    def _page_low_stock(self):
        alerts = services.get_low_stock_alerts()
        n = len(alerts)
        self._simple_page(
            f"Low-Stock Alerts ({n})",
            "Products at or below reorder level" if n else "All stock levels are healthy ✓",
            alerts, "alert_status", "LOW STOCK")

    def _page_history(self):
        self._simple_page("Inventory History", "All IN/OUT transactions",
                          services.get_inventory_history(100),
                          "transaction_type", "OUT")

    def _page_full_report(self):
        self._clear()
        self._title("Full Inventory Report", "Generated by sp_generate_inventory_report()")
        tbl = DataTable(self.content)
        tbl.pack(fill="both", expand=True, padx=36, pady=(0, 24))
        try:
            tbl.display(services.generate_full_inventory_report(),
                        "stock_status", "LOW STOCK")
        except Exception as e:
            ctk.CTkLabel(self.content, text=f"Error: {e}",
                         text_color=C["danger"], font=F_BODY).pack(padx=36)

    def _page_delivery(self):
        self._simple_page("Supplier Delivery History", "Aggregated statistics",
                          services.get_supplier_delivery_history())

    # ─────────────────────────────────────
    #  TURNOVER + CHART
    # ─────────────────────────────────────
    def _page_turnover(self):
        self._clear()
        self._title("Stock Turnover Report", "Turnover rate per product")
        rows = services.get_stock_turnover()

        if HAS_MATPLOTLIB and rows:
            chart_card = ctk.CTkFrame(self.content, fg_color=C["card"],
                                      corner_radius=16, border_width=1,
                                      border_color=C["border"], height=300)
            chart_card.pack(fill="x", padx=36, pady=(0, 12))
            chart_card.pack_propagate(False)

            top = sorted(rows, key=lambda r: float(r.get("stock_turnover_rate", 0) or 0),
                         reverse=True)[:7]
            names = [str(r["product_name"]) for r in top]
            rates = [float(r.get("stock_turnover_rate", 0) or 0) for r in top]

            fig, ax = plt.subplots(figsize=(9, 2.8))
            fig.patch.set_facecolor(C["card"])
            ax.set_facecolor(C["card"])

            colors = ["#5B8CFF", "#06B6D4", "#22C55E", "#F59E0B",
                      "#EF4444", "#A855F7", "#EC4899"][:len(names)]
            bars = ax.barh(names[::-1], rates[::-1], color=colors[::-1],
                           height=0.55, edgecolor="none")

            ax.set_xlabel("Turnover Rate", color=C["text_sec"], fontsize=10)
            ax.set_title("Top Products by Stock Turnover",
                         color=C["text"], fontsize=14, fontweight="bold", pad=10)
            ax.tick_params(colors=C["text_sec"], labelsize=9)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.grid(axis="x", linestyle="--", alpha=0.15, color=C["text_dim"])

            for bar, rate in zip(bars, rates[::-1]):
                ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
                        f"{rate:.2f}", va="center", ha="left",
                        color=C["text"], fontsize=9, fontweight="bold")

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=chart_card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            plt.close(fig)

        tbl = DataTable(self.content)
        tbl.pack(fill="both", expand=True, padx=36, pady=(0, 24))
        tbl.display(rows)

    # ─────────────────────────────────────
    #  CHECK STOCK
    # ─────────────────────────────────────
    def _page_check_stock(self):
        self._clear()
        self._title("Check Stock", "Lookup current stock for a specific product and warehouse")

        card = ctk.CTkFrame(self.content, fg_color=C["card"], corner_radius=16,
                            border_width=1, border_color=C["border"])
        card.pack(fill="x", padx=36, pady=(0, 16))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=24)

        ctk.CTkLabel(row, text="Product ID", font=F_LABEL,
                     text_color=C["text_sec"]).grid(row=0, column=0, padx=(0, 8), sticky="w")
        pid = ctk.CTkEntry(row, placeholder_text="e.g. 1", width=110, height=40,
                           font=F_INPUT, fg_color=C["input_bg"],
                           border_color=C["border"], corner_radius=10)
        pid.grid(row=0, column=1, padx=(0, 24))

        ctk.CTkLabel(row, text="Warehouse ID", font=F_LABEL,
                     text_color=C["text_sec"]).grid(row=0, column=2, padx=(0, 8), sticky="w")
        wid = ctk.CTkEntry(row, placeholder_text="e.g. 1", width=110, height=40,
                           font=F_INPUT, fg_color=C["input_bg"],
                           border_color=C["border"], corner_radius=10)
        wid.grid(row=0, column=3, padx=(0, 24))

        result_area = ctk.CTkFrame(self.content, fg_color="transparent")
        result_area.pack(fill="both", expand=True, padx=36, pady=(0, 24))

        def do_check():
            for w in result_area.winfo_children():
                w.destroy()
            try:
                r = services.get_current_stock(int(pid.get()), int(wid.get()))
                t = DataTable(result_area)
                t.pack(fill="both", expand=True)
                t.display([r] if r else [])
            except ValueError:
                messagebox.showerror("Error", "Enter valid integer IDs.")

        ctk.CTkButton(row, text="Check", font=F_BTN,
                      fg_color=C["accent"], hover_color=C["accent_hover"],
                      width=110, height=40, corner_radius=10,
                      command=do_check).grid(row=0, column=4)

    # ─────────────────────────────────────
    #  FORM DIALOG
    # ─────────────────────────────────────
    def _form_dialog(self, title, fields, on_submit):
        d = ctk.CTkToplevel(self)
        d.title(title)
        d.geometry("460x" + str(min(180 + len(fields) * 78, 660)))
        d.resizable(False, True)
        d.configure(fg_color=C["bg"])
        d.transient(self)
        d.grab_set()

        ctk.CTkLabel(d, text=title, font=F_H2, text_color=C["accent"]).pack(pady=(20, 6))

        form = ctk.CTkScrollableFrame(d, fg_color=C["bg"])
        form.pack(fill="both", expand=True, padx=8, pady=(0, 0))

        entries = {}
        for label, ph in fields:
            ctk.CTkLabel(form, text=label.upper(), font=F_MENU_SM,
                         text_color=C["text_dim"]).pack(anchor="w", padx=24, pady=(12, 3))
            e = ctk.CTkEntry(form, placeholder_text=ph, height=40, font=F_INPUT,
                             fg_color=C["input_bg"], border_color=C["border"],
                             corner_radius=10)
            e.pack(fill="x", padx=24)
            entries[label] = e

        bf = ctk.CTkFrame(d, fg_color="transparent")
        bf.pack(fill="x", padx=28, pady=(12, 18))

        
        def submit():
            try:
                values = {label: entry.get().strip() for label, entry in entries.items()}
                on_submit(values)
                d.destroy()
                messagebox.showinfo("Success", f"{title} completed successfully!")

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter valid numeric values in all required numeric fields."
                )

            except mysql.connector.Error as e:
                err_title, err_msg = friendly_db_error(e)
                messagebox.showerror(err_title, err_msg)
            except Exception as e:
                err_title, err_msg = friendly_db_error(e)
                messagebox.showerror(err_title, err_msg)

        ctk.CTkButton(bf, text="✓  Confirm", font=F_BTN,
                      fg_color=C["success"], hover_color="#1BA34E",
                      height=44, corner_radius=12, command=submit
                      ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(bf, text="✕  Cancel", font=F_BTN,
                      fg_color="#2A1520", hover_color="#3A1F2A",
                      text_color=C["danger"],
                      height=44, corner_radius=12, command=d.destroy
                      ).pack(side="right", expand=True, fill="x", padx=(6, 0))

    # ─────────────────────────────────────
    #  ACTION FORMS
    # ─────────────────────────────────────
    def _form_add_stock(self):
        self._form_dialog("Add Stock", [
            ("Product ID", "e.g. 1"), ("Warehouse ID", "e.g. 1"),
            ("Supplier ID", "e.g. 1"), ("Quantity", "e.g. 50"),
            ("Unit Cost", "e.g. 25.99"), ("Notes", "e.g. Monthly restock"),
        ], lambda v: [services.add_stock(
            int(v["Product ID"]), int(v["Warehouse ID"]),
            int(v["Supplier ID"]), int(v["Quantity"]),
            float(v["Unit Cost"]), v["Notes"]), self._page_stock()])

    def _form_remove_stock(self):
        if self.user["role"] == "MANAGER":
            return messagebox.showwarning("Denied", "Manager cannot remove stock.")
        self._form_dialog("Remove Stock", [
            ("Product ID", "e.g. 1"), ("Warehouse ID", "e.g. 1"),
            ("Quantity", "e.g. 10"), ("Notes", "e.g. Customer order"),
        ], lambda v: [services.remove_stock(
            int(v["Product ID"]), int(v["Warehouse ID"]),
            int(v["Quantity"]), v["Notes"]), self._page_stock()])

    def _form_add_product(self):
        if self.user["role"] == "MANAGER":
            return messagebox.showwarning("Denied", "Manager cannot add products.")
        self._form_dialog("Add Product", [
            ("Product Name", "e.g. USB-C Hub"), ("Description", "e.g. 4-port hub"),
            ("Unit Price", "e.g. 19.99"), ("Supplier ID", "e.g. 1"),
            ("Reorder Level", "e.g. 10"), ("Unit", "pcs / roll / ream"),
        ], lambda v: [services.add_product(
            v["Product Name"], v["Description"], float(v["Unit Price"]),
            int(v["Supplier ID"]), int(v["Reorder Level"]),
            v["Unit"] or "pcs"), self._page_products()])

    def _form_update_price(self):
        if self.user["role"] == "MANAGER":
            return messagebox.showwarning("Denied", "Manager cannot update prices.")
        self._form_dialog("Update Price", [
            ("Product ID", "e.g. 1"), ("New Unit Price", "e.g. 29.99"),
        ], lambda v: [services.update_product_price(
            int(v["Product ID"]), float(v["New Unit Price"])),
            self._page_products()])

    def _form_add_supplier(self):
        if self.user["role"] == "MANAGER":
            return messagebox.showwarning("Denied", "Manager cannot add suppliers.")
        self._form_dialog("Add Supplier", [
            ("Supplier Name", "e.g. TechParts Co."), ("Address", "e.g. 123 Main St"),
            ("Phone Number", "e.g. 0901234567"), ("Email", "e.g. info@tech.vn"),
            ("Contact Person", "e.g. John Doe"),
        ], lambda v: [services.add_supplier(
            v["Supplier Name"], v["Address"], v["Phone Number"],
            v["Email"], v["Contact Person"]), self._page_suppliers()])

    def _form_add_warehouse(self):
        if self.user["role"] == "MANAGER":
            return messagebox.showwarning("Denied", "Manager cannot add warehouses.")
        self._form_dialog("Add Warehouse", [
            ("Warehouse Name", "e.g. East Hub"), ("Address", "e.g. Hai Phong"),
            ("Capacity", "e.g. 5000"), ("Manager Name", "e.g. Nguyen Van A"),
            ("Phone Number", "e.g. 0912345678"),
        ], lambda v: [services.add_warehouse(
            v["Warehouse Name"], v["Address"], int(v["Capacity"]),
            v["Manager Name"], v["Phone Number"]), self._page_warehouses()])

    def _logout(self):
        self.destroy()
        run_app()


# ═══════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════
def run_app():
    login = LoginWindow()
    login.mainloop()
    if login.user is None:
        return
    MainApp(login.user).mainloop()

if __name__ == "__main__":
    run_app()
