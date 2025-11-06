import tkinter as tk
from tkinter import ttk, messagebox

class MenuManager(tk.Toplevel):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.title("Menu Management")
        self.geometry("800x500")
        self.build()

    def build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Label(top, text="Menu Items", font=("Helvetica", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Add Item", command=self.add_item).pack(side="right")
        cols = ("id","name","category","price","available")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_double)
        self.refresh()

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, category, price, available FROM menu_items")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)

    def add_item(self):
        ItemEditor(self, self.conn, on_save=self.refresh)

    def on_double(self, evt):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])["values"]
        ItemEditor(self, self.conn, item_id=vals[0], on_save=self.refresh)

class ItemEditor(tk.Toplevel):
    def __init__(self, parent, conn, item_id=None, on_save=None):
        super().__init__(parent)
        self.conn = conn
        self.item_id = item_id
        self.on_save = on_save
        self.title("Item Editor")
        self.geometry("400x350")
        self.build()
        if item_id:
            self.load_item()

    def build(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10, fill="both", expand=True)
        ttk.Label(frm, text="Name:").grid(row=0, column=0, sticky="e")
        self.name = ttk.Entry(frm); self.name.grid(row=0, column=1, pady=5)
        ttk.Label(frm, text="Category:").grid(row=1, column=0, sticky="e")
        self.category = ttk.Entry(frm); self.category.grid(row=1, column=1, pady=5)
        ttk.Label(frm, text="Price:").grid(row=2, column=0, sticky="e")
        self.price = ttk.Entry(frm); self.price.grid(row=2, column=1, pady=5)
        ttk.Label(frm, text="Available (1/0):").grid(row=3, column=0, sticky="e")
        self.available = ttk.Entry(frm); self.available.grid(row=3, column=1, pady=5)
        ttk.Label(frm, text="Description:").grid(row=4, column=0, sticky="ne")
        self.desc = tk.Text(frm, height=5, width=30); self.desc.grid(row=4, column=1, pady=5)
        btn_frame = ttk.Frame(frm); btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side="left", padx=5)
        if self.item_id:
            ttk.Button(btn_frame, text="Delete", command=self.delete).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="left")

    def load_item(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name, category, price, available, description FROM menu_items WHERE id=?", (self.item_id,))
        row = cur.fetchone()
        if not row:
            return
        self.name.insert(0, row[0])
        self.category.insert(0, row[1] or "")
        self.price.insert(0, str(row[2]))
        self.available.insert(0, str(row[3]))
        if row[4]:
            self.desc.insert("1.0", row[4])

    def save(self):
        n = self.name.get().strip()
        c = self.category.get().strip()
        try:
            p = float(self.price.get().strip())
        except:
            messagebox.showerror("Invalid", "Price must be a number")
            return
        a = 1
        try:
            a = int(self.available.get().strip())
        except:
            a = 1
        d = self.desc.get("1.0", "end").strip()
        cur = self.conn.cursor()
        if self.item_id:
            cur.execute("UPDATE menu_items SET name=?, category=?, price=?, available=?, description=? WHERE id=?",
                        (n,c,p,a,d,self.item_id))
        else:
            cur.execute("INSERT INTO menu_items (name, category, price, available, description) VALUES (?,?,?,?,?)",
                        (n,c,p,a,d))
        self.conn.commit()
        if self.on_save: self.on_save()
        self.destroy()

    def delete(self):
        if messagebox.askyesno("Delete", "Delete this item?"):
            cur = self.conn.cursor()
            cur.execute("DELETE FROM menu_items WHERE id=?", (self.item_id,))
            self.conn.commit()
            if self.on_save: self.on_save()
            self.destroy()
