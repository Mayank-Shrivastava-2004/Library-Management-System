import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LibraryPro"
}

def clean_reset_admin():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cur = cnx.cursor()
        
        email = "admin@library.com"
        password = "admin123"
        hashed_pw = generate_password_hash(password)
        unique_id = "ADMIN_SECURE_001"
        name = "System Administrator"
        role = "admin"
        
        # We'll use REPLACE INTO or check existince
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        ext = cur.fetchone()
        
        if ext:
            print(f"Updating existing admin: {email}")
            cur.execute(
                "UPDATE users SET name=%s, password=%s, unique_id=%s, role=%s WHERE email=%s",
                (name, hashed_pw, unique_id, role, email)
            )
        else:
            print(f"Creating new admin: {email}")
            cur.execute(
                "INSERT INTO users (name, email, password, unique_id, role) VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed_pw, unique_id, role)
            )
            
        cnx.commit()
        print("SUCCESS: Admin credentials have been reset.")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
        cur.close()
        cnx.close()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    clean_reset_admin()
