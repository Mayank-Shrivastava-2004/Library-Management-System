import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "librarypro",
}

try:
    cnx = mysql.connector.connect(**DB_CONFIG)
    cur = cnx.cursor()
    # Modify the role enum to include teacher
    cur.execute(
        "ALTER TABLE users "
        "MODIFY COLUMN role ENUM('admin', 'student', 'guest', 'teacher') NOT NULL DEFAULT 'student'"
    )
    cnx.commit()
    print("[OK] Schema updated: Added 'teacher' role successfully.")
    cur.close()
    cnx.close()
except Exception as e:
    print("[ERROR]", str(e))
