"""
update_user_schema.py
---------------------
Migrates the existing 'users' table to include a 'role' column, 
and seeds a default admin account.

Usage:
    python update_user_schema.py
"""

import sys
import hashlib
import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "librarypro",
}

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def main():
    print("--------------------------------------------------")
    print(" [*] Upgrading Database Schema (Adding Roles)")
    print("--------------------------------------------------")

    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
    except mysql.connector.Error as err:
        print("[!] Connection error:", err)
        sys.exit(1)

    # 1. Add the 'role' column to the 'users' table
    try:
        cursor.execute(
            "ALTER TABLE users "
            "ADD COLUMN role ENUM('admin', 'student', 'guest') NOT NULL DEFAULT 'student'"
        )
        print("[OK] Added 'role' column to users table.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_FIELDNAME:
            print("[>>] 'role' column already exists in 'users'. Skipping ALTER.")
        else:
            print("[!] Could not alter table:", err)

    # Note: 'email' is already UNIQUE from our initial setup.
    
    # 2. Seed a default 'admin' account
    admin_email = "admin@library.com"
    admin_pwd_plain = "admin123"
    admin_pwd_hashed = sha256(admin_pwd_plain)

    cursor.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
    if cursor.fetchone():
        print(f"[>>] Admin account '{admin_email}' already exists. Skipping seed.")
    else:
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            ("System Admin", admin_email, admin_pwd_hashed, "admin")
        )
        cnx.commit()
        print("[OK] Default admin account created.")
        print()
        print("    Email    :", admin_email)
        print("    Password :", admin_pwd_plain)
        print("    Role     : admin")

    cursor.close()
    cnx.close()
    print("--------------------------------------------------")
    print(" [OK] Database migration complete!\n")

if __name__ == "__main__":
    main()
