import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

class InventoryWindow(tk.Toplevel):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.title("Inventory Management")
        self.geometry("800x500")
        self.build()
        self.refresh()

    def build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Label(top, text="Inventory", font=("Helvetica", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Add Item", command=self.add_item).pack(side="right")
        self.tree = ttk.Treeview(self, columns=("id","name","qty","unit","low"), show="headings")
        for c in ("id","name","qty","unit","low"):
            self.tree.heading(c, text=c.title())
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.edit_item)
        ttk.Button(self, text="Low Stock Alert", command=self.show_low).pack(pady=5)

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,quantity,unit,low_threshold FROM inventory")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)

    def add_item(self):
        name = simpledialog.askstring("Name","Item name")
        if not name: return
        qty = simpledialog.askfloat("Quantity","Initial quantity",initialvalue=0.0)
        unit = simpledialog.askstring("Unit","Unit (e.g. pcs, kg, L)")
        low = simpledialog.askfloat("Low threshold","Low stock threshold",initialvalue=0.0)
        cur = self.conn.cursor()
        cur.execute("INSERT INTO inventory (name,quantity,unit,low_threshold) VALUES (?,?,?,?)",(name, qty or 0.0, unit or '', low or 0.0))
        self.conn.commit()
        self.refresh()

    def edit_item(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        iid = vals[0]
        name = vals[1]
        qty = vals[2]
        new_qty = simpledialog.askfloat("Quantity", f"Set new quantity for {name}", initialvalue=qty)
        if new_qty is None: return
        cur = self.conn.cursor()
        cur.execute("UPDATE inventory SET quantity=? WHERE id=?",(new_qty,iid))
        self.conn.commit()
        self.refresh()

    def show_low(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name,quantity,low_threshold FROM inventory WHERE quantity<=low_threshold")
        rows = cur.fetchall()
        if not rows:
            messagebox.showinfo("Low stock","No low stock items")
            return
        msg = "\\n".join([f\"{r[0]}: {r[1]} <= {r[2]}\" for r in rows])
        messagebox.showwarning("Low stock", msg)
