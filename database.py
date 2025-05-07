import sqlite3
from datetime import datetime, timedelta
import hashlib

# Connect to the SQLite database
def get_db_connection():
    """Creates a connection to the database file 'drug_inventory.db'."""
    conn = sqlite3.connect('drug_inventory.db')
    conn.row_factory = sqlite3.Row  # Lets us access columns by name (e.g., drug['name'])
    return conn

# Set up the database tables
def init_db():
    """Creates all necessary tables if they don’t already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drugs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Drugs (
            drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            expiry_date DATE NOT NULL,
            manufacturer TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            storage_conditions TEXT
        )
    ''')

    # Suppliers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_info TEXT,
            address TEXT
        )
    ''')

    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date DATE NOT NULL,
            supplier_id INTEGER,
            status TEXT NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
        )
    ''')

    # Order_Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Order_Items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            drug_id INTEGER,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id),
            FOREIGN KEY (drug_id) REFERENCES Drugs(drug_id)
        )
    ''')

    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# User Management Functions
def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Adds a new user with a hashed password to the Users table."""
    password_hash = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Users (username, password_hash)
            VALUES (?, ?)
        ''', (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Username already exists
    conn.close()
    return True

def verify_user(username, password):
    """Verifies if the username and password match a record in the Users table."""
    password_hash = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE username = ? AND password_hash = ?', (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Drug Management Functions
def add_drug(name, batch_number, expiry_date, manufacturer, quantity, storage_conditions):
    """Adds a new drug to the Drugs table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Drugs (name, batch_number, expiry_date, manufacturer, quantity, storage_conditions)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, batch_number, expiry_date, manufacturer, quantity, storage_conditions))
    conn.commit()
    conn.close()

def get_all_drugs():
    """Returns all drugs from the Drugs table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Drugs')
    drugs = cursor.fetchall()
    conn.close()
    return drugs

def update_drug(drug_id, name, batch_number, expiry_date, manufacturer, quantity, storage_conditions):
    """Updates an existing drug’s details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Drugs
        SET name = ?, batch_number = ?, expiry_date = ?, manufacturer = ?, quantity = ?, storage_conditions = ?
        WHERE drug_id = ?
    ''', (name, batch_number, expiry_date, manufacturer, quantity, storage_conditions, drug_id))
    conn.commit()
    conn.close()

def delete_drug(drug_id):
    """Deletes a drug from the Drugs table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Drugs WHERE drug_id = ?', (drug_id,))
    conn.commit()
    conn.close()

def search_drugs(search_term):
    """Returns drugs where the name contains the search term."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Drugs WHERE LOWER(name) LIKE LOWER(?)', (f'%{search_term}%',))
    drugs = cursor.fetchall()
    conn.close()
    return drugs

# Supplier Management Functions
def add_supplier(name, contact_info, address):
    """Adds a new supplier to the Suppliers table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Suppliers (name, contact_info, address)
        VALUES (?, ?, ?)
    ''', (name, contact_info, address))
    conn.commit()
    conn.close()

def get_all_suppliers():
    """Returns all suppliers from the Suppliers table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Suppliers')
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers

def update_supplier(supplier_id, name, contact_info, address):
    """Updates an existing supplier’s details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Suppliers
        SET name = ?, contact_info = ?, address = ?
        WHERE supplier_id = ?
    ''', (name, contact_info, address, supplier_id))
    conn.commit()
    conn.close()

def delete_supplier(supplier_id):
    """Deletes a supplier from the Suppliers table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Suppliers WHERE supplier_id = ?', (supplier_id,))
    conn.commit()
    conn.close()

def search_suppliers(search_term):
    """Returns suppliers where the name contains the search term."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Suppliers WHERE LOWER(name) LIKE LOWER(?)', (f'%{search_term}%',))
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers

# Order Management Functions
def add_order(supplier_id, status, items):
    """Adds a new order and its items to the Orders and Order_Items tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    order_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO Orders (order_date, supplier_id, status)
        VALUES (?, ?, ?)
    ''', (order_date, supplier_id, status))
    order_id = cursor.lastrowid

    for item in items:
        cursor.execute('''
            INSERT INTO Order_Items (order_id, drug_id, quantity)
            VALUES (?, ?, ?)
        ''', (order_id, item['drug_id'], item['quantity']))
    conn.commit()
    conn.close()

def get_all_orders():
    """Returns all orders with supplier names."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.order_id, o.order_date, s.name as supplier_name, o.status
        FROM Orders o
        JOIN Suppliers s ON o.supplier_id = s.supplier_id
    ''')
    orders = cursor.fetchall()
    conn.close()
    return orders

def search_orders(search_term):
    """Returns orders where the order ID or supplier name contains the search term."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.order_id, o.order_date, s.name as supplier_name, o.status
        FROM Orders o
        JOIN Suppliers s ON o.supplier_id = s.supplier_id
        WHERE LOWER(CAST(o.order_id AS TEXT)) LIKE LOWER(?) OR LOWER(s.name) LIKE LOWER(?)
    ''', (f'%{search_term}%', f'%{search_term}%'))
    orders = cursor.fetchall()
    conn.close()
    return orders

# Inventory Tracking
def update_inventory(drug_id, quantity_change):
    """Updates a drug’s quantity (positive to add, negative to subtract)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Drugs
        SET quantity = quantity + ?
        WHERE drug_id = ?
    ''', (quantity_change, drug_id))
    conn.commit()
    conn.close()

# Reporting Functions
def get_low_stock_drugs(threshold=10):
    """Returns drugs with quantity below the threshold (default 10)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Drugs WHERE quantity < ?', (threshold,))
    drugs = cursor.fetchall()
    conn.close()
    return drugs

def get_expiring_soon_drugs(days=30):
    """Returns drugs expiring within the next 30 days."""
    conn = get_db_connection()
    cursor = conn.cursor()
    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    cursor.execute('SELECT * FROM Drugs WHERE expiry_date < ?', (expiry_date,))
    drugs = cursor.fetchall()
    conn.close()
    return drugs

# Initialize the database
init_db()
