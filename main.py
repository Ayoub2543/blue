import tkinter as tk
from tkinter import ttk
import os, sqlite3
from modules.login import LoginWindow
from modules.dashboard import DashboardWindow

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def ensure_db():
    if not os.path.exists(DB_PATH):
        import db_init
        db_init.init_db()

class App:
    def __init__(self, root):
        self.root = root
        root.title("Restaurant & Bar Management - Enhanced")
        root.geometry("1100x700")
        style = ttk.Style(root)
        try:
            style.theme_use('clam')
        except:
            pass
        self.conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.user = None
        self.show_login()

    def show_login(self):
        for w in self.root.winfo_children(): w.destroy()
        LoginWindow(self.root, self.on_login_success, self.conn)

    def on_login_success(self, user):
        self.user = user
        for w in self.root.winfo_children(): w.destroy()
        DashboardWindow(self.root, self.conn, user)

if __name__=='__main__':
    ensure_db()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
