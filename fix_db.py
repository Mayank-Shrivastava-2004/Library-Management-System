"""
fix_db.py
---------
Quick-fix script for "Error 1049: Unknown database librarypro".

Connects to MySQL, creates the database + tables if they don't exist,
then inserts sample books and test users so you can log in immediately.

Usage:
    python fix_db.py
"""

import sys
from werkzeug.security import generate_password_hash
import mysql.connector
from mysql.connector import errorcode

# -------------------------------------------------------
#  CONFIGURATION  -- update only if your MySQL differs
# -------------------------------------------------------
HOST     = "localhost"
USER     = "root"
PASSWORD = ""           # leave blank if no root password
DB_NAME  = "librarypro" # lowercase -- matches what MySQL stores it as


def sha256(text):
    return generate_password_hash(text)


def sep(title=""):
    """Print a plain-ASCII section divider."""
    width = 52
    if title:
        pad = "-" * ((width - len(title) - 2) // 2)
        print("\n" + pad + " " + title + " " + pad)
    else:
        print("-" * width)


def ok(msg):   print("  [OK] " + msg)
def skip(msg): print("  [--] " + msg)
def err(msg):  print("  [!!] " + msg)


# -------------------------------------------------------
#  STEP 1 -- Connect to MySQL (no database selected yet)
# -------------------------------------------------------
sep("Step 1: Connect to MySQL")
try:
    cnx = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
    )
    ok("Connected to MySQL at " + HOST)
except mysql.connector.Error as e:
    if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        err("Access denied. Check USER / PASSWORD in this script.")
    else:
        err("Connection failed: " + str(e))
    sys.exit(1)

cursor = cnx.cursor()

# -------------------------------------------------------
#  STEP 2 -- Create database if it does not exist
# -------------------------------------------------------
sep("Step 2: Database")
cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
if cursor.fetchone():
    skip("Database '" + DB_NAME + "' already exists -- skipping CREATE.")
else:
    cursor.execute(
        "CREATE DATABASE `" + DB_NAME + "` "
        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    ok("Database '" + DB_NAME + "' created.")

cursor.execute("USE `" + DB_NAME + "`")

# -------------------------------------------------------
#  STEP 3 -- Create tables (IF NOT EXISTS)
# -------------------------------------------------------
sep("Step 3: Tables")

TABLES = {

    "books": (
        "CREATE TABLE IF NOT EXISTS `books` ("
        "  `id`            INT          NOT NULL AUTO_INCREMENT,"
        "  `title`         VARCHAR(255) NOT NULL,"
        "  `author`        VARCHAR(255) NOT NULL,"
        "  `category`      VARCHAR(100) NOT NULL DEFAULT 'General',"
        "  `isbn`          VARCHAR(20)           DEFAULT NULL,"
        "  `total_qty`     INT          NOT NULL DEFAULT 1,"
        "  `available_qty` INT          NOT NULL DEFAULT 1,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    ),

    "users": (
        "CREATE TABLE IF NOT EXISTS `users` ("
        "  `id`       INT          NOT NULL AUTO_INCREMENT,"
        "  `name`     VARCHAR(150) NOT NULL,"
        "  `email`    VARCHAR(150) NOT NULL UNIQUE,"
        "  `password` VARCHAR(255) NOT NULL,"
        "  `roll_no`  VARCHAR(50)           DEFAULT NULL,"
        "  `role`     ENUM('admin', 'student', 'guest') NOT NULL DEFAULT 'student',"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    ),

    "transactions": (
        "CREATE TABLE IF NOT EXISTS `transactions` ("
        "  `id`          INT          NOT NULL AUTO_INCREMENT,"
        "  `user_id`     INT          NOT NULL,"
        "  `book_id`     INT          NOT NULL,"
        "  `issue_date`  DATE         NOT NULL,"
        "  `due_date`    DATE                  DEFAULT NULL,"
        "  `status`      ENUM('issued','returned','overdue')"
        "                NOT NULL DEFAULT 'issued',"
        "  `fine_amount` DECIMAL(8,2) NOT NULL DEFAULT 0.00,"
        "  PRIMARY KEY (`id`),"
        "  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)  ON DELETE CASCADE,"
        "  FOREIGN KEY (`book_id`) REFERENCES `books`(`id`)  ON DELETE CASCADE"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    ),

    "activity_logs": (
        "CREATE TABLE IF NOT EXISTS `activity_logs` ("
        "  `id`        INT          NOT NULL AUTO_INCREMENT,"
        "  `user_id`   INT                   DEFAULT NULL,"
        "  `action`    VARCHAR(500) NOT NULL,"
        "  `timestamp` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY (`id`),"
        "  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    ),
}

for name, ddl in TABLES.items():
    cursor.execute(ddl)
    ok("Table '" + name + "' -- ready.")

cnx.commit()

# -------------------------------------------------------
#  STEP 4 -- Sample books
# -------------------------------------------------------
sep("Step 4: Sample Books")
cursor.execute("SELECT COUNT(*) FROM books")
book_count = cursor.fetchone()[0]

SAMPLE_BOOKS = [
    ("Clean Code",               "Robert C. Martin",  "Tech",    "978-0132350884", 5, 5),
    ("1984",                     "George Orwell",      "Fiction", "978-0451524935", 4, 4),
    ("Sapiens",                  "Yuval Noah Harari",  "History", "978-0062316110", 3, 3),
    ("The Pragmatic Programmer", "Andrew Hunt",        "Tech",    "978-0135957059", 3, 3),
    ("To Kill a Mockingbird",    "Harper Lee",         "Fiction", "978-0061935466", 2, 2),
]

if book_count == 0:
    cursor.executemany(
        "INSERT INTO books "
        "(title, author, category, isbn, total_qty, available_qty) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        SAMPLE_BOOKS,
    )
    cnx.commit()
    ok("Inserted " + str(len(SAMPLE_BOOKS)) + " sample books.")
else:
    skip("Books table already has " + str(book_count) + " rows -- skipping.")

# -------------------------------------------------------
#  STEP 5 -- Sample users
# -------------------------------------------------------
sep("Step 5: Sample Users")
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

DEMO_USERS = [
    ("Alice Johnson", "alice@library.com", "alice123", "STU001"),
    ("Bob Smith",     "bob@library.com",   "bob123",   "STU002"),
]

if user_count == 0:
    rows = [(n, e, sha256(p), r) for n, e, p, r in DEMO_USERS]
    cursor.executemany(
        "INSERT INTO users (name, email, password, roll_no) "
        "VALUES (%s, %s, %s, %s)",
        rows,
    )
    cnx.commit()
    ok("Inserted " + str(len(DEMO_USERS)) + " demo user(s).")
else:
    skip("Users table already has " + str(user_count) + " rows -- skipping.")

# -------------------------------------------------------
#  Done
# -------------------------------------------------------
cursor.close()
cnx.close()

sep()
print("\n  fix_db.py finished successfully!")
print()
print("  +------------------------------------------+")
print("  |  Log in to the Student Portal with:       |")
print("  +------------------------------------------+")
for name, email, pwd, roll in DEMO_USERS:
    print("  |  Name    : " + name)
    print("  |  Email   : " + email)
    print("  |  Password: " + pwd)
    print("  |  Roll No : " + roll)
    print("  +------------------------------------------+")
print()
print("  Next steps:")
print("    python setup_database.py   (if you want the full seed data)")
print("    python main.py             [1] Web Portal  [2] Admin App")
print()
