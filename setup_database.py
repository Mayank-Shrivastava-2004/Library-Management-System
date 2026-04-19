"""
setup_database.py
-----------------
Creates the 'LibraryPro' MySQL database, defines all tables, and seeds
initial data (15 books + 2 test users).

Usage:
    python setup_database.py
"""

from werkzeug.security import generate_password_hash
import mysql.connector
from mysql.connector import errorcode

# ─────────────────────────────────────────────
#  DATABASE CONFIGURATION
#  Update HOST / USER / PASSWORD to match your
#  local MySQL installation.
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",   # ← change if your MySQL root has a password
}

DB_NAME = "LibraryPro"

# ─────────────────────────────────────────────
#  TABLE DEFINITIONS
# ─────────────────────────────────────────────
TABLES = {}

TABLES["books"] = (
    "CREATE TABLE IF NOT EXISTS `books` ("
    "  `id`            INT          NOT NULL AUTO_INCREMENT,"
    "  `title`         VARCHAR(255) NOT NULL,"
    "  `author`        VARCHAR(255) NOT NULL,"
    "  `category`      VARCHAR(100) NOT NULL,"
    "  `isbn`          VARCHAR(20)  NOT NULL UNIQUE,"
    "  `total_qty`     INT          NOT NULL DEFAULT 1,"
    "  `available_qty` INT          NOT NULL DEFAULT 1,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

TABLES["users"] = (
    "CREATE TABLE IF NOT EXISTS `users` ("
    "  `id`            INT          NOT NULL AUTO_INCREMENT,"
    "  `name`          VARCHAR(150) NOT NULL,"
    "  `email`         VARCHAR(150) NOT NULL UNIQUE,"
    "  `mobile_number` VARCHAR(15)           DEFAULT NULL,"
    "  `unique_id`     VARCHAR(50)  NOT NULL UNIQUE,"
    "  `password`      VARCHAR(255) NOT NULL,"
    "  `role`          ENUM('admin', 'student', 'teacher', 'guest') NOT NULL DEFAULT 'student',"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

TABLES["transactions"] = (
    "CREATE TABLE IF NOT EXISTS `transactions` ("
    "  `id`           INT         NOT NULL AUTO_INCREMENT,"
    "  `user_id`      INT         NOT NULL,"
    "  `book_id`      INT         NOT NULL,"
    "  `issue_date`   DATE        NOT NULL,"
    "  `due_date`     DATE        NOT NULL,"
    "  `status`       ENUM('issued','returned','overdue') NOT NULL DEFAULT 'issued',"
    "  `fine_amount`  DECIMAL(8,2) NOT NULL DEFAULT 0.00,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,"
    "  FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB"
)

TABLES["activity_logs"] = (
    "CREATE TABLE IF NOT EXISTS `activity_logs` ("
    "  `id`        INT          NOT NULL AUTO_INCREMENT,"
    "  `user_id`   INT,"
    "  `action`    VARCHAR(500) NOT NULL,"
    "  `timestamp` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL"
    ") ENGINE=InnoDB"
)

# ─────────────────────────────────────────────
#  SEED DATA
# ─────────────────────────────────────────────
SEED_BOOKS = [
    # Tech
    ("Clean Code", "Robert C. Martin", "Tech", "978-0132350884", 5, 5),
    ("The Pragmatic Programmer", "Andrew Hunt", "Tech", "978-0135957059", 3, 3),
    ("Introduction to Algorithms", "Cormen et al.", "Tech", "978-0262033848", 4, 4),
    ("Python Crash Course", "Eric Matthes", "Tech", "978-1593279288", 6, 6),
    ("Design Patterns", "Gang of Four", "Tech", "978-0201633610", 3, 3),

    # Fiction
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", "978-0061935466", 4, 4),
    ("1984", "George Orwell", "Fiction", "978-0451524935", 5, 5),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "978-0743273565", 3, 3),
    ("Brave New World", "Aldous Huxley", "Fiction", "978-0060850524", 4, 4),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "978-0316769174", 2, 2),

    # History
    ("Sapiens", "Yuval Noah Harari", "History", "978-0062316110", 5, 5),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", "978-0393317558", 3, 3),
    ("The Silk Roads", "Peter Frankopan", "History", "978-1408839997", 2, 2),
    ("A Short History of Nearly Everything", "Bill Bryson", "History", "978-0767908184", 4, 4),
    ("The Rise and Fall of the Third Reich", "William L. Shirer", "History", "978-0671728687", 2, 2),
]

SEED_USERS = [
    # (name, email, unique_id, plaintext_password)
    ("Alice Johnson", "alice@library.com", "STU001", "alice123"),
    ("Bob Smith",     "bob@library.com",   "STU002", "bob123"),
]


def _hash_password(plain: str) -> str:
    """Werkzeug hash."""
    return generate_password_hash(plain)


def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4")
        print(f"[✓] Database '{DB_NAME}' ready.")
    except mysql.connector.Error as err:
        print(f"[✗] Failed to create database: {err}")
        raise


def create_tables(cursor):
    for name, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
            print(f"[✓] Table '{name}' ready.")
        except mysql.connector.Error as err:
            print(f"[✗] Failed to create table '{name}': {err}")
            raise


def seed_books(cursor, cnx):
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"[→] Books table already has {count} rows – skipping seed.")
        return
    insert_sql = (
        "INSERT INTO books (title, author, category, isbn, total_qty, available_qty) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    cursor.executemany(insert_sql, SEED_BOOKS)
    cnx.commit()
    print(f"[✓] Seeded {len(SEED_BOOKS)} books.")


def seed_users(cursor, cnx):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"[→] Users table already has {count} rows – skipping seed.")
        return
    insert_sql = (
        "INSERT INTO users (name, email, unique_id, password) "
        "VALUES (%s, %s, %s, %s)"
    )
    rows = [(n, e, r, _hash_password(p)) for n, e, r, p in SEED_USERS]
    cursor.executemany(insert_sql, rows)
    cnx.commit()
    print(f"[✓] Seeded {len(SEED_USERS)} test users.")
    print()
    print("  Test credentials:")
    for n, e, r, p in SEED_USERS:
        print(f"    Email: {e}  |  Password: {p}  |  Unique ID: {r}")


def main():
    print("=" * 52)
    print("   LibraryPro — Database Initialisation Script")
    print("=" * 52)

    # Step 1: connect without specifying a database
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("[✗] Access denied. Check your MySQL username/password in DB_CONFIG.")
        else:
            print(f"[✗] Connection error: {err}")
        return

    cursor = cnx.cursor()

    # Step 2: create the database
    create_database(cursor)
    cursor.execute(f"USE `{DB_NAME}`")

    # Step 3: create tables
    create_tables(cursor)

    # Step 4: seed data
    seed_books(cursor, cnx)
    seed_users(cursor, cnx)

    cursor.close()
    cnx.close()
    print()
    print("[✓] Setup complete!  Run 'python main.py' to launch the system.")


if __name__ == "__main__":
    main()
