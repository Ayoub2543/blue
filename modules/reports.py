import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, csv, datetime, os

class ReportsWindow(tk.Toplevel):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.title("Reports")
        self.geometry("700x500")
        self.build()

    def build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Label(top, text="Reports", font=("Helvetica",14,"bold")).pack(side="left")
        ttk.Button(top, text="Daily Sales (Today)", command=self.daily_sales).pack(side="right")
        self.txt = tk.Text(self, height=25)
        self.txt.pack(fill="both", expand=True, padx=10, pady=10)

    def daily_sales(self):
        today = datetime.date.today().isoformat()
        cur = self.conn.cursor()
        cur.execute("SELECT id,table_id,total,created_at FROM orders WHERE date(created_at)=?", (today,))
        rows = cur.fetchall()
        total_sum = sum(r[2] for r in rows)
        self.txt.delete("1.0","end")
        self.txt.insert("1.0", f\"Daily sales for {today}\\n\\n\")
        for r in rows:
            self.txt.insert("end", f\"Order {r[0]} - Table {r[1]} - {r[2]} - {r[3]}\\n\")
        self.txt.insert("end", f\"\\nTOTAL: {total_sum}\\n\")
        # allow export
        if messagebox.askyesno(\"Export\",\"Export this report to CSV?\"):
            path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
            if not path: return
            with open(path,'w',newline='') as f:
                w = csv.writer(f)
                w.writerow(['order_id','table_id','total','created_at'])
                w.writerows(rows)
            messagebox.showinfo(\"Exported\", f\"Saved to {path}\")
