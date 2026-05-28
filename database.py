import sqlite3
from config import DATABASE_PATH

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Enforces foreign key constraints.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    # Enable Foreign Key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    # Return row factory to allow column access by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the SQLite tables required for the CRM.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. USERS Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE NOT NULL,
        mr_name TEXT NOT NULL,
        employee_code TEXT NOT NULL,
        hq TEXT NOT NULL,
        division TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 2. DOCTORS Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        speciality TEXT NOT NULL,
        hospital TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
    );
    """)

    # 3. POB_ENTRIES Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pob_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        doctor_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity TEXT NOT NULL,
        order_value REAL NOT NULL,
        entry_date TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );
    """)

    # 4. VISITS Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        doctor_id INTEGER NOT NULL,
        visit_date TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
        UNIQUE(user_id, doctor_id, visit_date)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print(f"Initializing database at: {DATABASE_PATH}")
    init_db()
    print("Database initialized successfully.")
