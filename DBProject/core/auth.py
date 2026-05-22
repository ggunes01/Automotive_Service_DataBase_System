from core.db import DBHelper
from utils.hashing import hash_password


def login_base(email, password):
    """Authenticate personnel by comparing the SHA-256 password hash."""
    db = DBHelper()
    conn = db.connect()
    cur = conn.cursor()

    try:
        hashed_input = hash_password(password)

        cur.execute("""
            SELECT PersonnelID, FirstName, LastName, PositionID, DepartmentID
            FROM Personnel
            WHERE Email = ? AND Password = ?
        """, (email, hashed_input))

        row = cur.fetchone()

        if row:
            return {
                "status": True,
                "PersonnelID": row[0],
                "FullName": f"{row[1]} {row[2]}",
                "PositionID": row[3],
                "DepartmentID": row[4],
            }

        return {"status": False, "message": "Invalid email or password"}

    except Exception as e:
        return {"status": False, "message": f"Login Error: {str(e)}"}

    finally:
        conn.close()


def car_repair_login(email, password):
    return login_base(email, password)


def damage_login(email, password):
    return login_base(email, password)
