import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "librarypro",
}

print("--------------------------------------------------")
print(" [*] Applying Database Schema Update V2")
print("--------------------------------------------------")

try:
    cnx = mysql.connector.connect(**DB_CONFIG)
    cur = cnx.cursor()

    # 1. Rename 'roll_no' to 'unique_id'
    try:
        cur.execute("ALTER TABLE users CHANGE COLUMN roll_no unique_id VARCHAR(50)")
        print("[OK] Renamed 'roll_no' to 'unique_id'.")
    except mysql.connector.Error as err:
        if err.errno == 1054:  # Unknown column (already changed)
            print("[>>] 'roll_no' already renamed to 'unique_id'.")
        else:
            print("[!] Could not rename:", err)

    # 2. Ensure unique_id is UNIQUE
    try:
        cur.execute("ALTER TABLE users ADD UNIQUE(unique_id)")
        print("[OK] Enforced UNIQUE constraint on 'unique_id'.")
    except mysql.connector.Error as err:
        if err.errno == 1061: # Duplicate key name
            print("[>>] UNIQUE constraint on 'unique_id' already exists.")
        else:
            pass # might have been unique already as roll_no

    # 3. Add 'mobile_number'
    try:
        cur.execute("ALTER TABLE users ADD COLUMN mobile_number VARCHAR(15) DEFAULT NULL")
        print("[OK] Added 'mobile_number' column.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_FIELDNAME:
            print("[>>] 'mobile_number' column already exists.")
        else:
            print("[!] Could not add mobile_number:", err)

    # 4. Enforce STRICT role Enum check (Student/Teacher/Admin)
    try:
        cur.execute(
            "ALTER TABLE users "
            "MODIFY COLUMN role ENUM('admin', 'student', 'teacher') NOT NULL DEFAULT 'student'"
        )
        print("[OK] Locked User Roles to ('admin', 'student', 'teacher').")
    except Exception as e:
        print("[!] Role constraint error:", e)

    cnx.commit()
    cur.close()
    cnx.close()
    print("--------------------------------------------------")
    print(" [OK] Schema V2 Migration Complete!")

except Exception as err:
    print("[ERROR] Database connection failed:", err)
