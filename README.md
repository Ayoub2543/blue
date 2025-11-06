Restaurant & Bar Management - Desktop (Enhanced)
===============================================

This is an enhanced Python Tkinter desktop application for managing a restaurant/bar.
Added features in this version:
- Full POS with table management and receipts (PDF)
- Order items saved to the database
- Inventory management with low-stock alerts and manual adjustment
- Sales reports (daily) and export to CSV
- Settings table and example tax/service config
- More polished UI layout (still Tkinter/ttk based)

How to run
----------
1. Install Python 3.8+.
2. (Optional) Create a virtualenv and activate it.
3. Install required Python packages:
   pip install -r requirements.txt
4. Initialize the database (first run):
   python db_init.py
5. Run the app:
   python main.py

Default credentials
-------------------
Username: admin
Password: admin123

What's next
----------
You can ask me to:
- Add authentication hashing (bcrypt)
- Add recipes to auto-deduct exact ingredients per menu item
- Add payroll, reservations reminders, SMS/email integration
- Create Windows installer (exe) or change to PyQt for richer UI
