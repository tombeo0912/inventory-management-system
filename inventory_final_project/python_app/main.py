from __future__ import annotations

import getpass
import os
from datetime import datetime
from typing import Iterable

import mysql.connector

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = BLUE = ""
    class Back:
        RED = GREEN = YELLOW = CYAN = ""
    class Style:
        BRIGHT = RESET_ALL = DIM = ""

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

import services


# ─────────────────────────────────────────────
#  ROLE / AUTH CONFIG
# ─────────────────────────────────────────────
USERS = {
    "admin":   {"password": "admin123",   "role": "ADMIN"},
    "manager": {"password": "manager123", "role": "MANAGER"},
}

# Options that MANAGER role is allowed to use.
# ADMIN has access to everything.
MANAGER_ALLOWED = {"1", "4", "6", "8", "10", "11", "12", "13", "14", "15", "16", "17", "0"}


# ─────────────────────────────────────────────
#  COLOR HELPERS
# ─────────────────────────────────────────────
def c_success(text: str) -> str:
    return f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def c_error(text: str) -> str:
    return f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def c_warn(text: str) -> str:
    return f"{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def c_header(text: str) -> str:
    return f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def c_title(text: str) -> str:
    return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def c_dim(text: str) -> str:
    return f"{Style.DIM}{text}{Style.RESET_ALL}"


# ─────────────────────────────────────────────
#  LOGIN SCREEN
# ─────────────────────────────────────────────
def login() -> dict | None:
    border = "=" * 60
    print(c_title(f"\n{border}"))
    print(c_title("       🔐  INVENTORY SYSTEM — LOGIN  🔐"))
    print(c_title(border))
    print(f"  {Fore.CYAN}1.{Style.RESET_ALL} Admin             {c_dim('(username: admin)')}")
    print(f"  {Fore.CYAN}2.{Style.RESET_ALL} Inventory Manager {c_dim('(username: manager)')}")
    print(c_title(border))

    role_choice = input(f"\n{Fore.MAGENTA}{Style.BRIGHT}  Select role (1/2): {Style.RESET_ALL}").strip()

    if role_choice == "1":
        username = "admin"
    elif role_choice == "2":
        username = "manager"
    else:
        print(c_error("\n  ✘  Invalid role.\n"))
        return None


    password = input(f"{Fore.CYAN}  Password: {Style.RESET_ALL}")

    user = USERS.get(username)
    if not user or user["password"] != password:
        print(c_error("\n  ✘  Wrong username or password.\n"))
        return None

    print(c_success(f"\n  ✔  Welcome, {username.upper()}! Role: {user['role']}\n"))
    return {"username": username, "role": user["role"]}


def is_allowed(role: str, choice: str) -> bool:
    if role == "ADMIN":
        return True
    return choice in MANAGER_ALLOWED


# ─────────────────────────────────────────────
#  TABLE PRINTER WITH COLORS
# ─────────────────────────────────────────────
def print_rows(rows: list[dict]) -> None:
    if not rows:
        print(c_warn("\n  (No data found.)\n"))
        return

    headers = list(rows[0].keys())
    widths = {
        header: max(len(str(header)), *(len(str(row.get(header, ""))) for row in rows))
        for header in headers
    }

    line = "+-" + "-+-".join("-" * widths[h] for h in headers) + "-+"

    print(c_header(line))
    print(c_header("| ") + c_header(" | ".join(str(h).ljust(widths[h]) for h in headers)) + c_header(" |"))
    print(c_header(line))

    for row in rows:
        alert = str(row.get("alert_status", ""))
        stock_status = str(row.get("stock_status", ""))
        transaction = str(row.get("transaction_type", ""))

        if alert == "LOW STOCK" or stock_status == "LOW STOCK":
            row_color = Fore.RED + Style.BRIGHT
        elif alert == "NORMAL" or stock_status == "OK":
            row_color = Fore.GREEN
        elif transaction == "IN":
            row_color = Fore.GREEN
        elif transaction == "OUT":
            row_color = Fore.YELLOW
        else:
            row_color = Fore.WHITE

        cells = " | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)
        print(f"{row_color}| {cells} |{Style.RESET_ALL}")

    print(c_header(line))
    print()


# ─────────────────────────────────────────────
#  INPUT HELPERS
# ─────────────────────────────────────────────
def prompt_int(message: str) -> int:
    while True:
        try:
            return int(input(f"{Fore.CYAN}{message}{Style.RESET_ALL}").strip())
        except ValueError:
            print(c_error("  Please enter a valid integer."))


def prompt_float(message: str) -> float:
    while True:
        try:
            return float(input(f"{Fore.CYAN}{message}{Style.RESET_ALL}").strip())
        except ValueError:
            print(c_error("  Please enter a valid number."))


def prompt_str(message: str) -> str:
    return input(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


# ─────────────────────────────────────────────
#  CHART HELPER (matplotlib)
# ─────────────────────────────────────────────
def draw_turnover_chart(rows: list[dict], top_n: int = 5) -> str | None:
    """Draw bar chart of top-N products by stock turnover. Returns saved path."""
    if not HAS_MATPLOTLIB:
        print(c_error("  ✘  matplotlib is not installed. Run: pip install matplotlib"))
        return None

    if not rows:
        print(c_warn("  No data to plot."))
        return None

    sorted_rows = sorted(
        rows,
        key=lambda r: float(r.get("stock_turnover_rate", 0) or 0),
        reverse=True,
    )[:top_n]

    names = [str(r["product_name"]) for r in sorted_rows]
    rates = [float(r.get("stock_turnover_rate", 0) or 0) for r in sorted_rows]

    if all(rate == 0 for rate in rates):
        print(c_warn("  All turnover rates are 0. Chart will be empty."))

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#e74c3c", "#f39c12", "#f1c40f", "#2ecc71", "#3498db"][:top_n]
    bars = ax.bar(names, rates, color=colors)

    ax.set_title(f"Top {top_n} Products by Stock Turnover Rate",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Product", fontsize=11)
    ax.set_ylabel("Turnover Rate", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, rate in zip(bars, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{rate:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    filename = f"chart_turnover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.abspath(filename)
    plt.savefig(filepath, dpi=120)
    plt.close()
    return filepath


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────
def menu(user: dict) -> None:
    border = "=" * 60

    role_badge = (
        f"{Fore.GREEN}{Style.BRIGHT}[ADMIN]{Style.RESET_ALL}"
        if user["role"] == "ADMIN"
        else f"{Fore.YELLOW}{Style.BRIGHT}[MANAGER]{Style.RESET_ALL}"
    )

    print(f"\n{c_title(border)}")
    print(c_title("       📦  INVENTORY MANAGEMENT SYSTEM  📦  ") + role_badge)
    print(c_title(border))

    options = [
        ("1",  "List products",                                           True),
        ("2",  "Add product",                                              False),
        ("3",  "Update product price",                                     False),
        ("4",  "List suppliers",                                           True),
        ("5",  "Add supplier",                                             False),
        ("6",  "List warehouses",                                          True),
        ("7",  "Add warehouse",                                            False),
        ("8",  "Add stock (inbound)",                                      True),
        ("9",  "Remove stock (outbound)",                                  False),
        ("10", "View stock by warehouse",                                  True),
        ("11", "Low-stock alerts",                                         True),
        ("12", "Supplier delivery history",                                True),
        ("13", "Inventory history",                                        True),
        ("14", "Check current stock for one product in one warehouse",     True),
        ("15", "Stock turnover report",                                    True),
        ("16", "Full inventory report (sp_generate_inventory_report)",     True),
        ("17", "Turnover chart (matplotlib, top 5)",                       True),
        ("0",  "Logout / Exit",                                            True),
    ]

    for num, label, manager_ok in options:
        if user["role"] == "MANAGER" and not manager_ok:
            tag = f"{Fore.RED}🔒{Style.RESET_ALL} "
            num_color = Fore.RED + Style.DIM
            label_color = Style.DIM
        else:
            tag = "   "
            if num == "0":
                num_color = Fore.RED + Style.BRIGHT
                label_color = Fore.WHITE
            elif num in ("8", "9"):
                num_color = Fore.GREEN + Style.BRIGHT
                label_color = Fore.WHITE
            elif num in ("11", "17"):
                num_color = Fore.YELLOW + Style.BRIGHT
                label_color = Fore.WHITE
            else:
                num_color = Fore.CYAN + Style.BRIGHT
                label_color = Fore.WHITE

        print(f"  {tag}{num_color}{num:>2}.{Style.RESET_ALL} {label_color}{label}{Style.RESET_ALL}")

    print(c_title(border))


# ─────────────────────────────────────────────
#  HANDLE CHOICE
# ─────────────────────────────────────────────
def handle_choice(choice: str, user: dict) -> bool:
    if not is_allowed(user["role"], choice):
        print(c_error(f"\n  🔒  Access denied. Role '{user['role']}' cannot use option {choice}.\n"))
        return True

    if choice == "1":
        print_rows(services.list_products())

    elif choice == "2":
        services.add_product(
            product_name=prompt_str("Product name: "),
            description=prompt_str("Description: "),
            unit_price=prompt_float("Unit price: "),
            supplier_id=prompt_int("Supplier ID: "),
            reorder_level=prompt_int("Reorder level: "),
            unit=prompt_str("Unit (pcs/roll/ream/...): ") or "pcs",
        )
        print(c_success("\n  ✔  Product added successfully.\n"))

    elif choice == "3":
        services.update_product_price(
            product_id=prompt_int("Product ID: "),
            new_price=prompt_float("New unit price: "),
        )
        print(c_success("\n  ✔  Product price updated successfully.\n"))

    elif choice == "4":
        print_rows(services.list_suppliers())

    elif choice == "5":
        services.add_supplier(
            supplier_name=prompt_str("Supplier name: "),
            address=prompt_str("Address: "),
            phone_number=prompt_str("Phone number: "),
            email=prompt_str("Email: "),
            contact_person=prompt_str("Contact person: "),
        )
        print(c_success("\n  ✔  Supplier added successfully.\n"))

    elif choice == "6":
        print_rows(services.list_warehouses())

    elif choice == "7":
        services.add_warehouse(
            warehouse_name=prompt_str("Warehouse name: "),
            address=prompt_str("Address: "),
            capacity=prompt_int("Capacity: "),
            manager_name=prompt_str("Manager name: "),
            phone_number=prompt_str("Phone number: "),
        )
        print(c_success("\n  ✔  Warehouse added successfully.\n"))

    elif choice == "8":
        services.add_stock(
            product_id=prompt_int("Product ID: "),
            warehouse_id=prompt_int("Warehouse ID: "),
            supplier_id=prompt_int("Supplier ID: "),
            quantity=prompt_int("Quantity: "),
            unit_cost=prompt_float("Unit cost: "),
            notes=prompt_str("Notes: "),
        )
        print(c_success("\n  ✔  Stock added successfully.\n"))

    elif choice == "9":
        services.remove_stock(
            product_id=prompt_int("Product ID: "),
            warehouse_id=prompt_int("Warehouse ID: "),
            quantity=prompt_int("Quantity: "),
            notes=prompt_str("Notes: "),
        )
        print(c_success("\n  ✔  Stock removed successfully.\n"))

    elif choice == "10":
        print_rows(services.get_stock_by_warehouse())

    elif choice == "11":
        rows = services.get_low_stock_alerts()
        if rows:
            print(c_warn(f"\n  ⚠  {len(rows)} low-stock alert(s) found!\n"))
        print_rows(rows)

    elif choice == "12":
        print_rows(services.get_supplier_delivery_history())

    elif choice == "13":
        limit = prompt_int("How many recent rows? ")
        print_rows(services.get_inventory_history(limit))

    elif choice == "14":
        result = services.get_current_stock(
            product_id=prompt_int("Product ID: "),
            warehouse_id=prompt_int("Warehouse ID: "),
        )
        if result:
            print_rows([result])
        else:
            print(c_warn("\n  No matching product or warehouse found.\n"))

    elif choice == "15":
        print_rows(services.get_stock_turnover())

    elif choice == "16":
        print(c_title("\n  Generating full inventory report...\n"))
        rows = services.generate_full_inventory_report()
        print_rows(rows)

    elif choice == "17":
        print(c_title("\n  Drawing turnover chart...\n"))
        rows = services.get_stock_turnover()
        path = draw_turnover_chart(rows, top_n=5)
        if path:
            print(c_success(f"  ✔  Chart saved to: {path}\n"))

    elif choice == "0":
        return False

    else:
        print(c_error("\n  Invalid option. Please choose again.\n"))

    return True


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main() -> None:
    print(c_title("\n  Connecting to MySQL Inventory Management System...\n"))

    user = None
    for attempt in range(3):
        user = login()
        if user:
            break
        print(c_warn(f"  Attempts left: {2 - attempt}\n"))
    else:
        print(c_error("\n  Too many failed attempts. Exiting.\n"))
        return

    while True:
        try:
            menu(user)
            choice = input(f"\n{Fore.MAGENTA}{Style.BRIGHT}  Choose an option: {Style.RESET_ALL}").strip()
            if not handle_choice(choice, user):
                print(c_title("\n  Goodbye! 👋\n"))
                break
        except mysql.connector.Error as exc:
            print(c_error(f"\n  MySQL error: {exc}\n"))
        except KeyboardInterrupt:
            print(c_title("\n\n  Interrupted. Goodbye! 👋\n"))
            break
        except Exception as exc:
            print(c_error(f"\n  Unexpected error: {exc}\n"))


if __name__ == "__main__":
    main()