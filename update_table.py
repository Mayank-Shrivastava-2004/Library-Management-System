import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LibraryPro"
}

def update_table():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cur = cnx.cursor()

        # Check existing columns
        cur.execute("SHOW COLUMNS FROM users")
        columns = [row[0] for row in cur.fetchall()]

        updates_made = False

        if 'unique_id' not in columns:
            print("Adding 'unique_id' column...")
            cur.execute("ALTER TABLE users ADD COLUMN unique_id VARCHAR(50) UNIQUE")
            updates_made = True
            
        if 'mobile_number' not in columns:
            print("Adding 'mobile_number' column...")
            cur.execute("ALTER TABLE users ADD COLUMN mobile_number VARCHAR(15)")
            updates_made = True

        if 'role' not in columns:
            print("Adding 'role' column...")
            cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'student'")
            updates_made = True

        if updates_made:
            cnx.commit()
            print("Success! The 'users' table has been perfectly updated with the new columns.")
        else:
            print("No updates needed. The 'users' table already has all the required columns.")

        cur.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"Error updating table: {err}")

if __name__ == "__main__":
    print("Connecting to database...")
    update_table()
