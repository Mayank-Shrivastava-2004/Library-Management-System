import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LibraryPro"
}

def check_admin():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cur = cnx.cursor(dictionary=True)
        
        cur.execute("SELECT * FROM users WHERE email='admin@library.com'")
        admin = cur.fetchone()
        
        if admin:
            print("Admin found:")
            for k, v in admin.items():
                if k == 'password':
                    print(f"  {k}: [HASHED]")
                else:
                    print(f"  {k}: {v}")
                    
            # Update password to 'admin123' just in case
            new_hash = generate_password_hash("admin123")
            cur.execute("UPDATE users SET password = %s WHERE email = 'admin@library.com'", (new_hash,))
            cnx.commit()
            print("\n[✓] Admin password has been hard-reset to: admin123")
            
        else:
            print("Admin NOT found. Creating admin user...")
            new_hash = generate_password_hash("admin123")
            cur.execute(
                "INSERT INTO users (name, email, password, unique_id, role) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("Administrator", "admin@library.com", new_hash, "ADMIN_001", "admin")
            )
            cnx.commit()
            print("[✓] Admin user successfully created!")
            
        cur.close()
        cnx.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_admin()
