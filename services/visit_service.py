import datetime
from database import get_db_connection

def create_visit_entry(user_id, doctor_id, visit_date=None):
    """
    Logs a new doctor visit (call) in the database.
    Bypasses insertion if a visit for this doctor on the same date already exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False
    
    now = datetime.datetime.now()
    if not visit_date:
        visit_date = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # INSERT OR IGNORE will skip if UNIQUE constraint (user_id, doctor_id, visit_date) is triggered
        cursor.execute(
            """
            INSERT OR IGNORE INTO visits (user_id, doctor_id, visit_date, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (str(user_id), doctor_id, visit_date, timestamp)
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error creating visit entry: {e}")
    finally:
        conn.close()
    return success

def get_today_visits(user_id):
    """
    Retrieves all doctor visits logged by the MR today.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute(
        """
        SELECT v.*, d.doctor_name, d.speciality, d.hospital 
        FROM visits v
        JOIN doctors d ON v.doctor_id = d.id
        WHERE v.user_id = ? AND v.visit_date = ?
        ORDER BY v.timestamp ASC
        """,
        (str(user_id), today_str)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_monthly_visits(user_id):
    """
    Retrieves all doctor visits logged by the MR in the current month.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    current_month_prefix = datetime.datetime.now().strftime("%Y-%m")
    
    cursor.execute(
        """
        SELECT v.*, d.doctor_name, d.speciality, d.hospital 
        FROM visits v
        JOIN doctors d ON v.doctor_id = d.id
        WHERE v.user_id = ? AND v.visit_date LIKE ?
        ORDER BY v.visit_date ASC
        """,
        (str(user_id), f"{current_month_prefix}%")
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
