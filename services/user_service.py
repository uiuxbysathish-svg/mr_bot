import datetime
from database import get_db_connection

def get_user_by_telegram_id(telegram_id):
    """
    Retrieves a user by their Telegram ID.
    Returns a dictionary representing the user, or None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (str(telegram_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user(telegram_id, mr_name, employee_code, hq, division):
    """
    Registers a new Medical Representative in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            """
            INSERT INTO users (telegram_id, mr_name, employee_code, hq, division, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(telegram_id), mr_name, employee_code, hq, division, created_at)
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error creating user: {e}")
        success = False
    finally:
        conn.close()
    return success
