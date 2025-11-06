import sqlite3, os
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )""")
    # menu items
    c.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        description TEXT,
        available INTEGER DEFAULT 1
    )""")
    # inventory
    c.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity REAL DEFAULT 0,
        unit TEXT,
        low_threshold REAL DEFAULT 0
    )""")
    # tables
    c.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        zone TEXT,
        status TEXT DEFAULT 'free'
    )""")
    # orders
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        total REAL,
        tax REAL,
        service REAL,
        discount REAL,
        paid INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    # order items
    c.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        menu_item_id INTEGER,
        name TEXT,
        qty INTEGER,
        price REAL
    )""")
    # settings
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    conn.commit()

    # default admin
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Admin"))
    # default sample tables
    c.execute("SELECT COUNT(*) FROM tables")
    if c.fetchone()[0] == 0:
        tables = [('T1','Dining','free'),('T2','Dining','free'),('B1','Bar','free'),('VIP1','VIP','free')]
        c.executemany("INSERT INTO tables (name, zone, status) VALUES (?,?,?)", tables)
    # default settings
    def set_if_missing(k,v):
        c.execute("INSERT OR IGNORE INTO settings (key,value) VALUES (?,?)",(k,v))
    set_if_missing('tax_percent','10')
    set_if_missing('service_percent','5')
    conn.commit()
    conn.close()

if __name__=='__main__':
    init_db()
    print("Initialized DB at", DB_PATH)
