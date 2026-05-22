import os

import pyodbc


class DBHelper:
    def __init__(self):
        driver = os.getenv("DB_DRIVER", "SQL Server")
        server = os.getenv("DB_SERVER", "DESKTOP-6ALKE60")
        database = os.getenv("DB_NAME", "DBProject")
        trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes")

        conn_parts = [
            f"Driver={{{driver}}}",
            f"Server={server}",
            f"Database={database}",
        ]

        if trusted_connection.lower() in ("yes", "true", "1"):
            conn_parts.append("Trusted_Connection=yes")
        else:
            conn_parts.extend([
                f"UID={os.getenv('DB_USER', '')}",
                f"PWD={os.getenv('DB_PASSWORD', '')}",
            ])

        self.conn_str = ";".join(conn_parts) + ";"

    def connect(self):
        return pyodbc.connect(self.conn_str)

    def get_personnel_by_email(self, email):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT PersonnelID, FirstName, LastName, Email, Password, PositionID
            FROM Personnel
            WHERE Email = ?
        """, (email,))

        row = cursor.fetchone()
        conn.close()
        return row
