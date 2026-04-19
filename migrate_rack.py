import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LibraryPro"
}

def migrate():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cur = cnx.cursor()
        
        # Check if column exists
        cur.execute("SHOW COLUMNS FROM books LIKE 'rack_no'")
        if cur.fetchone():
            print("[→] 'rack_no' column already exists in 'books' table.")
        else:
            print("[+] Adding 'rack_no' column to 'books' table...")
            cur.execute("ALTER TABLE books ADD COLUMN rack_no VARCHAR(50) DEFAULT 'Unassigned'")
            cnx.commit()
            print("[✓] Migration successful.")
            
        cur.close()
        cnx.close()
    except Exception as e:
        print(f"[✗] Migration failed: {e}")

if __name__ == "__main__":
    migrate()
