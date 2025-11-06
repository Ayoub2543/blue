import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow(ttk.Frame):
    def __init__(self, parent, success_callback, conn):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.conn = conn
        self.success_callback = success_callback
        self.build()

    def build(self):
        frm = ttk.Frame(self)
        frm.place(relx=0.5, rely=0.45, anchor="center")
        ttk.Label(frm, text="Restaurant & Bar - Login", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frm, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username = ttk.Entry(frm)
        self.username.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(frm, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.password = ttk.Entry(frm, show="*")
        self.password.grid(row=2, column=1, padx=5, pady=5)
        btn = ttk.Button(frm, text="Login", command=self.try_login)
        btn.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Label(frm, text="(Default admin: admin / admin123)", foreground="gray").grid(row=4, column=0, columnspan=2)

    def try_login(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            messagebox.showwarning("Missing", "Enter username and password")
            return
        cur = self.conn.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (u, p))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Login Failed", "Incorrect credentials")
            return
        user = {"id": row[0], "username": row[1], "role": row[2]}
        self.success_callback(user)
