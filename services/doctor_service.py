from database import get_db_connection

def create_doctor(user_id, doctor_name, speciality, hospital):
    """
    Adds a new doctor linked to a specific MR (user_id).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False
    try:
        cursor.execute(
            """
            INSERT INTO doctors (user_id, doctor_name, speciality, hospital)
            VALUES (?, ?, ?, ?)
            """,
            (str(user_id), doctor_name, speciality, hospital)
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error creating doctor: {e}")
    finally:
        conn.close()
    return success

def get_doctors_by_user_id(user_id):
    """
    Retrieves all doctors registered by a specific MR.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM doctors WHERE user_id = ? ORDER BY doctor_name ASC",
        (str(user_id),)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_doctor_by_id(doctor_id):
    """
    Retrieves a single doctor's details by their ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
