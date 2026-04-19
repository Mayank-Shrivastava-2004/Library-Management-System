import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "librarypro",
}

print("Healing old passwords to Werkzeug security format...")
cnx = mysql.connector.connect(**DB_CONFIG)
cur = cnx.cursor()

# Reseed Alice
alice_hash = generate_password_hash("alice123")
cur.execute("UPDATE users SET password=%s WHERE email='alice@library.com'", (alice_hash,))

# Reseed Bob
bob_hash = generate_password_hash("bob123")
cur.execute("UPDATE users SET password=%s WHERE email='bob@library.com'", (bob_hash,))

cnx.commit()
cur.close()
cnx.close()
print("Passwords healed successfully!")
