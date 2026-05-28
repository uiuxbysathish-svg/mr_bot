import datetime
from database import get_db_connection

def create_pob_entry(user_id, doctor_id, product_name, quantity, order_value):
    """
    Logs a new POB entry in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False
    
    # We log entry_date in YYYY-MM-DD format for query performance
    now = datetime.datetime.now()
    entry_date = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute(
            """
            INSERT INTO pob_entries (user_id, doctor_id, product_name, quantity, order_value, entry_date, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (str(user_id), doctor_id, product_name, quantity, float(order_value), entry_date, timestamp)
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error creating POB entry: {e}")
    finally:
        conn.close()
        
    if success:
        # Automatically record a doctor call/visit when POB is booked
        from services.visit_service import create_visit_entry
        create_visit_entry(user_id, doctor_id, entry_date)
        
    return success

def get_today_pob_entries(user_id):
    """
    Retrieves all POB entries logged by the MR today.
    Includes the doctor name by joining with the doctors table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute(
        """
        SELECT p.*, d.doctor_name 
        FROM pob_entries p
        JOIN doctors d ON p.doctor_id = d.id
        WHERE p.user_id = ? AND p.entry_date = ?
        ORDER BY p.timestamp ASC
        """,
        (str(user_id), today_str)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_monthly_pob_entries(user_id):
    """
    Retrieves all POB entries logged by the MR in the current calendar month.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    current_month_prefix = datetime.datetime.now().strftime("%Y-%m")  # YYYY-MM
    
    cursor.execute(
        """
        SELECT p.*, d.doctor_name 
        FROM pob_entries p
        JOIN doctors d ON p.doctor_id = d.id
        WHERE p.user_id = ? AND p.entry_date LIKE ?
        ORDER BY p.entry_date ASC
        """,
        (str(user_id), f"{current_month_prefix}%")
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_top_doctors_report(user_id, limit=5):
    """
    Retrieves doctors ranked by cumulative POB order value.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT d.doctor_name, d.speciality, d.hospital, SUM(p.order_value) as total_value, COUNT(p.id) as total_orders
        FROM pob_entries p
        JOIN doctors d ON p.doctor_id = d.id
        WHERE p.user_id = ?
        GROUP BY p.doctor_id
        ORDER BY total_value DESC
        LIMIT ?
        """,
        (str(user_id), limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
