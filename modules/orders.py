import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3, datetime, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class OrdersWindow(tk.Toplevel):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.title("Orders - POS")
        self.geometry("1100x650")
        self.selected_table = None
        self.order_items = []  # list of dicts {menu_id,name,qty,price}
        self.build()

    def build(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Label(left, text="Tables", font=("Helvetica",12,"bold")).pack()
        self.table_frame = ttk.Frame(left)
        self.table_frame.pack(fill="y", pady=5)
        ttk.Button(left, text="Refresh Tables", command=self.load_tables).pack(pady=5)
        ttk.Button(left, text="New Table", command=self.create_table).pack(pady=5)
        self.load_tables()

        mid = ttk.Frame(self)
        mid.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ttk.Label(mid, text="Menu", font=("Helvetica",12,"bold")).pack(anchor="w")
        self.menu_tree = ttk.Treeview(mid, columns=("id","name","cat","price"), show="headings", height=15)
        for c in ("id","name","cat","price"):
            self.menu_tree.heading(c, text=c.title())
        self.menu_tree.pack(fill="both", expand=True)
        ttk.Button(mid, text="Add Selected to Order", command=self.add_selected).pack(pady=5)
        self.load_menu()

        right = ttk.Frame(self)
        right.pack(side="right", fill="y", padx=10, pady=10)
        ttk.Label(right, text="Order", font=("Helvetica",12,"bold")).pack()
        cols=("name","qty","price","total")
        self.order_tree = ttk.Treeview(right, columns=cols, show="headings", height=12)
        for c in cols:
            self.order_tree.heading(c, text=c.title())
        self.order_tree.pack()
        btns = ttk.Frame(right)
        btns.pack(pady=5)
        ttk.Button(btns, text="Remove Item", command=self.remove_item).pack(side="left",padx=5)
        ttk.Button(btns, text="Clear Order", command=self.clear_order).pack(side="left",padx=5)
        ttk.Button(btns, text="Save Order", command=self.save_order).pack(side="left",padx=5)
        ttk.Button(btns, text="Print Receipt (PDF)", command=self.print_receipt).pack(side="left",padx=5)
        # totals
        self.total_var = tk.StringVar(value="0.00")
        self.tax_var = tk.StringVar(value="0.00")
        self.service_var = tk.StringVar(value="0.00")
        self.discount_var = tk.StringVar(value="0.00")
        totals = ttk.Frame(right)
        totals.pack(pady=10)
        ttk.Label(totals, text="Subtotal:").grid(row=0,column=0,sticky="e")
        ttk.Label(totals, textvariable=self.total_var).grid(row=0,column=1,sticky="w")
        ttk.Label(totals, text="Tax:").grid(row=1,column=0,sticky="e")
        ttk.Label(totals, textvariable=self.tax_var).grid(row=1,column=1,sticky="w")
        ttk.Label(totals, text="Service:").grid(row=2,column=0,sticky="e")
        ttk.Label(totals, textvariable=self.service_var).grid(row=2,column=1,sticky="w")
        ttk.Label(totals, text="Discount:").grid(row=3,column=0,sticky="e")
        ttk.Label(totals, textvariable=self.discount_var).grid(row=3,column=1,sticky="w")

    def load_tables(self):
        for w in self.table_frame.winfo_children():
            w.destroy()
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,zone,status FROM tables")
        for row in cur.fetchall():
            b = ttk.Button(self.table_frame, text=f\"{row[1]} ({row[2]})\\n{row[3]}\", width=14)
            b.config(command=lambda rid=row[0],name=row[1]: self.select_table(rid,name))
            b.pack(padx=2,pady=2)

    def create_table(self):
        name = simpledialog.askstring("Table name","Enter table name (e.g. T5)")
        if not name: return
        cur = self.conn.cursor()
        cur.execute("INSERT INTO tables (name,zone,status) VALUES (?,?,?)",(name,"Dining","free"))
        self.conn.commit()
        self.load_tables()

    def select_table(self, table_id, name):
        self.selected_table = table_id
        messagebox.showinfo("Table Selected", f"Selected {name}")
        # load any unpaid order for table
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM orders WHERE table_id=? AND paid=0 ORDER BY id DESC LIMIT 1",(table_id,))
        row = cur.fetchone()
        self.order_items=[]
        if row:
            order_id=row[0]
            cur.execute("SELECT menu_item_id,name,qty,price FROM order_items WHERE order_id=?",(order_id,))
            for it in cur.fetchall():
                self.order_items.append({"menu_id":it[0],"name":it[1],"qty":it[2],"price":it[3]})
        self.refresh_order_view()

    def load_menu(self):
        for r in self.menu_tree.get_children():
            self.menu_tree.delete(r)
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,category,price FROM menu_items WHERE available=1")
        for row in cur.fetchall():
            self.menu_tree.insert("", "end", values=row)

    def add_selected(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a menu item")
            return
        vals = self.menu_tree.item(sel[0])["values"]
        menu_id, name, cat, price = vals
        # ask qty
        qty = simpledialog.askinteger("Qty","Enter quantity",initialvalue=1,minvalue=1)
        if not qty: return
        # add or update
        for it in self.order_items:
            if it['menu_id']==menu_id:
                it['qty'] += qty
                break
        else:
            self.order_items.append({"menu_id":menu_id,"name":name,"qty":qty,"price":price})
        self.refresh_order_view()

    def refresh_order_view(self):
        for r in self.order_tree.get_children():
            self.order_tree.delete(r)
        subtotal = 0
        for it in self.order_items:
            total = it['qty']*it['price']
            subtotal += total
            self.order_tree.insert("", "end", values=(it['name'], it['qty'], f\"{it['price']:.2f}\", f\"{total:.2f}\" ))
        # compute tax/service from settings
        cur = self.conn.cursor()
        cur.execute(\"SELECT value FROM settings WHERE key='tax_percent'\")
        tax_p = float(cur.fetchone()[0]) if cur.fetchone() is not None else None
        # note: above fetchone consumed row; safer to requery
        cur.execute(\"SELECT value FROM settings WHERE key='tax_percent'\")
        row = cur.fetchone()
        tax_p = float(row[0]) if row else 0.0
        cur.execute(\"SELECT value FROM settings WHERE key='service_percent'\")
        row = cur.fetchone()
        service_p = float(row[0]) if row else 0.0
        tax = subtotal * tax_p/100.0
        service = subtotal * service_p/100.0
        discount = 0.0
        self.total_var.set(f\"{subtotal:.2f}\")
        self.tax_var.set(f\"{tax:.2f}\")
        self.service_var.set(f\"{service:.2f}\")
        self.discount_var.set(f\"{discount:.2f}\")

    def remove_item(self):
        sel = self.order_tree.selection()
        if not sel: return
        vals = self.order_tree.item(sel[0])["values"]
        name = vals[0]
        for it in list(self.order_items):
            if it['name']==name:
                self.order_items.remove(it)
                break
        self.refresh_order_view()

    def clear_order(self):
        if messagebox.askyesno(\"Clear\",\"Clear current order?\"):
            self.order_items=[]
            self.refresh_order_view()

    def save_order(self):
        if not self.selected_table:
            messagebox.showwarning(\"Table\",\"Select a table first\")
            return
        if not self.order_items:
            messagebox.showwarning(\"Order\",\"Add items to order first\")
            return
        cur = self.conn.cursor()
        subtotal = sum(it['qty']*it['price'] for it in self.order_items)
        cur.execute(\"SELECT value FROM settings WHERE key='tax_percent'\")
        row = cur.fetchone(); tax_p = float(row[0]) if row else 0.0
        cur.execute(\"SELECT value FROM settings WHERE key='service_percent'\")
        row = cur.fetchone(); service_p = float(row[0]) if row else 0.0
        tax = subtotal*tax_p/100.0
        service = subtotal*service_p/100.0
        discount = 0.0
        now = datetime.datetime.now().isoformat()
        cur.execute(\"INSERT INTO orders (table_id,total,tax,service,discount,paid,created_at) VALUES (?,?,?,?,?,0,?)\",
                    (self.selected_table, subtotal+tax+service, tax, service, discount, now))
        order_id = cur.lastrowid
        for it in self.order_items:
            cur.execute(\"INSERT INTO order_items (order_id,menu_item_id,name,qty,price) VALUES (?,?,?,?,?)\",
                        (order_id, it['menu_id'], it['name'], it['qty'], it['price']))
            # basic inventory deduction: reduce inventory item with same name if exists
            cur.execute(\"SELECT id,quantity FROM inventory WHERE name=?\", (it['name'],))
            r = cur.fetchone()
            if r:
                cur.execute(\"UPDATE inventory SET quantity=? WHERE id=?\", (max(0, r[1]-it['qty']), r[0]))
        # mark table occupied
        cur.execute(\"UPDATE tables SET status='occupied' WHERE id=?\", (self.selected_table,))
        self.conn.commit()
        messagebox.showinfo(\"Saved\",\"Order saved successfully\")
        self.clear_order()
        self.load_tables()

    def print_receipt(self):
        if not self.order_items:
            messagebox.showwarning(\"Order\",\"Add items to order first\")
            return
        # create simple PDF receipt in exports folder
        exports = os.path.join(os.path.dirname(__file__),'..','exports')
        exports = os.path.abspath(exports)
        if not os.path.exists(exports): os.makedirs(exports)
        fname = os.path.join(exports, f\"receipt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf\")
        c = canvas.Canvas(fname, pagesize=A4)
        x = 50
        y = 800
        c.setFont('Helvetica-Bold', 14)
        c.drawString(x,y, 'Restaurant & Bar Receipt')
        y -= 30
        c.setFont('Helvetica',10)
        for it in self.order_items:
            line = f\"{it['qty']} x {it['name']} @ {it['price']:.2f} = {it['qty']*it['price']:.2f}\"
            c.drawString(x,y,line); y -= 15
        subtotal = sum(it['qty']*it['price'] for it in self.order_items)
        cur = self.conn.cursor()
        cur.execute(\"SELECT value FROM settings WHERE key='tax_percent'\")
        row = cur.fetchone(); tax_p = float(row[0]) if row else 0.0
        cur.execute(\"SELECT value FROM settings WHERE key='service_percent'\")
        row = cur.fetchone(); service_p = float(row[0]) if row else 0.0
        tax = subtotal*tax_p/100.0
        service = subtotal*service_p/100.0
        y -= 10
        c.drawString(x,y, f\"Subtotal: {subtotal:.2f}\"); y -= 15
        c.drawString(x,y, f\"Tax ({tax_p}%): {tax:.2f}\"); y -= 15
        c.drawString(x,y, f\"Service ({service_p}%): {service:.2f}\"); y -= 15
        c.drawString(x,y, f\"TOTAL: {subtotal+tax+service:.2f}\")
        c.showPage(); c.save()
        messagebox.showinfo(\"Receipt\", f\"Saved receipt to {fname}\")
