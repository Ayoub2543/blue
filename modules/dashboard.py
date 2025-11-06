import tkinter as tk
from tkinter import ttk
from modules.menu import MenuManager
from modules.orders import OrdersWindow
from modules.inventory import InventoryWindow
from modules.reports import ReportsWindow

class DashboardWindow(ttk.Frame):
    def __init__(self, parent, conn, user):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.conn = conn
        self.user = user
        self.build()

    def build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)
        ttk.Label(header, text=f"Welcome, {self.user['username']} ({self.user['role']})", font=("Helvetica", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Logout", command=self.logout).pack(side="right")
        # Tiles
        tiles = ttk.Frame(self)
        tiles.pack(fill="both", expand=True, padx=20, pady=20)
        btn_menu = ttk.Button(tiles, text="Menu Management", command=self.open_menu, width=30)
        btn_orders = ttk.Button(tiles, text="Orders (POS)", command=self.open_orders, width=30)
        btn_inventory = ttk.Button(tiles, text="Inventory", command=self.open_inventory, width=30)
        btn_reports = ttk.Button(tiles, text="Reports", command=self.open_reports, width=30)
        btn_menu.grid(row=0, column=0, padx=10, pady=10)
        btn_orders.grid(row=0, column=1, padx=10, pady=10)
        btn_inventory.grid(row=0, column=2, padx=10, pady=10)
        btn_reports.grid(row=0, column=3, padx=10, pady=10)

    def logout(self):
        for w in self.winfo_toplevel().winfo_children():
            w.destroy()
        from main import App
        App(self.winfo_toplevel())

    def open_menu(self):
        MenuManager(self.winfo_toplevel(), self.conn)

    def open_orders(self):
        OrdersWindow(self.winfo_toplevel(), self.conn)

    def open_inventory(self):
        InventoryWindow(self.winfo_toplevel(), self.conn)

    def open_reports(self):
        ReportsWindow(self.winfo_toplevel(), self.conn)
