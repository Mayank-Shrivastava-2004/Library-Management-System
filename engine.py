"""
engine.py
---------
Core logic engine for LibraryPro.

All database interactions live here.  Flask app.py and Tkinter
admin_panel.py import LibraryEngine and call its methods.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
import mysql.connector
from mysql.connector import errorcode

# ─────────────────────────────────────────────
#  Shared DB config  (keep in sync with setup_database.py)
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",          # ← update if needed
    "database": "LibraryPro",
}

ISSUE_DAYS   = 14      # default loan period in days
FINE_PER_DAY = 5.00    # fine in ₹ per overdue day


class LibraryEngine:
    """Encapsulates all database operations for LibraryPro."""

    # ──────────────────────────────────────────
    #  Connection helpers
    # ──────────────────────────────────────────

    def _get_connection(self):
        """Return a fresh MySQL connection."""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as err:
            raise ConnectionError(f"DB connection failed: {err}") from err

    # ──────────────────────────────────────────
    #  Authentication & Registration
    # ──────────────────────────────────────────

    def register_user(self, name, email, password, mobile, role='student', unique_id=None):
        """
        Hashes password via Werkzeug and saves the user to DB.
        Returns (True, "Registered") or (False, "Error message").
        """
        cnx = self._get_connection()
        cur = cnx.cursor()
        hashed_pw = generate_password_hash(password)
        try:
            cur.execute(
                "INSERT INTO users (name, email, password, mobile_number, unique_id, role) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, hashed_pw, mobile, unique_id, role)
            )
            user_id = cur.lastrowid
            cnx.commit()
            self._log(cur, cnx, user_id, f"User '{name}' registered as {role}.")
            return True, "Registration successful."
        except mysql.connector.IntegrityError:
            return False, "User with this email or Unique ID already exists."
        finally:
            cur.close(); cnx.close()

    def authenticate_user(self, email: str, password: str):
        """
        Verifies Werkzeug password hash.
        Returns user dict (id, name, role, email, unique_id, mobile_number) if matches, else None.
        """
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id, name, email, unique_id, mobile_number, role, password FROM users "
            "WHERE email = %s",
            (email.strip(),),
        )
        user = cur.fetchone()
        
        # Check if user exists and password is correct using Werkzeug
        if user and check_password_hash(user["password"], password):
            del user["password"] # Never return the hash
            self._log(cur, cnx, user["id"], f"User '{user['name']}' logged in.")
            cur.close(); cnx.close()
            return user
            
        cur.close(); cnx.close()
        return None

    # ──────────────────────────────────────────
    #  Book queries
    # ──────────────────────────────────────────

    def get_all_books(self):
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM books ORDER BY category, title")
        books = cur.fetchall()
        cur.close(); cnx.close()
        return books

    def search_books(self, query: str):
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        like = f"%{query}%"
        cur.execute(
            "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR category LIKE %s",
            (like, like, like),
        )
        books = cur.fetchall()
        cur.close(); cnx.close()
        return books

    def get_book_by_id(self, book_id: int):
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
        cur.close(); cnx.close()
        return book

    # ──────────────────────────────────────────
    #  Issue & Return
    # ──────────────────────────────────────────

    def issue_book(self, user_id: int, book_id: int):
        """
        Issue a book to a user.  Returns (True, message) or (False, error).
        """
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)

        # Check availability
        cur.execute("SELECT title, available_qty FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
        if not book:
            cur.close(); cnx.close()
            return False, "Book not found."
        if book["available_qty"] < 1:
            cur.close(); cnx.close()
            return False, f"'{book['title']}' is currently unavailable."

        # Check if user already has this book
        cur.execute(
            "SELECT id FROM transactions WHERE user_id=%s AND book_id=%s AND status='issued'",
            (user_id, book_id),
        )
        if cur.fetchone():
            cur.close(); cnx.close()
            return False, "You have already issued this book."

        today    = date.today()
        due_date = today + timedelta(days=ISSUE_DAYS)

        cur.execute(
            "INSERT INTO transactions (user_id, book_id, issue_date, due_date, status) "
            "VALUES (%s, %s, %s, %s, 'issued')",
            (user_id, book_id, today, due_date),
        )
        cur.execute(
            "UPDATE books SET available_qty = available_qty - 1 WHERE id = %s", (book_id,)
        )
        self._log(cur, cnx, user_id, f"Issued book id={book_id} '{book['title']}'.")
        cnx.commit()
        cur.close(); cnx.close()
        return True, f"Book '{book['title']}' issued successfully! Due by {due_date}."

    def return_book(self, transaction_id: int, user_id: int):
        """
        Return a book.  Calculates fine if overdue.
        Returns (True, message) or (False, error).
        """
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)

        cur.execute(
            "SELECT t.*, b.title FROM transactions t "
            "JOIN books b ON t.book_id = b.id "
            "WHERE t.id = %s AND t.user_id = %s AND t.status = 'issued'",
            (transaction_id, user_id),
        )
        txn = cur.fetchone()
        if not txn:
            cur.close(); cnx.close()
            return False, "Transaction not found or book already returned."

        today    = date.today()
        due_date = txn["due_date"]
        fine     = 0.0
        if today > due_date:
            overdue_days = (today - due_date).days
            fine = round(overdue_days * FINE_PER_DAY, 2)

        cur.execute(
            "UPDATE transactions SET status='returned', fine_amount=%s WHERE id=%s",
            (fine, transaction_id),
        )
        cur.execute(
            "UPDATE books SET available_qty = available_qty + 1 WHERE id = %s",
            (txn["book_id"],),
        )
        self._log(cur, cnx, user_id,
                  f"Returned book id={txn['book_id']} '{txn['title']}'. Fine=₹{fine}.")
        cnx.commit()
        cur.close(); cnx.close()

        if fine > 0:
            return True, f"Book returned. Fine charged: ₹{fine:.2f}"
        return True, "Book returned successfully. No fine."

    # ──────────────────────────────────────────
    #  User Profile
    # ──────────────────────────────────────────

    def get_user_profile(self, user_id: int):
        """Returns user info + currently issued books."""
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)

        cur.execute("SELECT id, name, email, mobile_number, unique_id FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        cur.execute(
            "SELECT t.id AS txn_id, b.title, b.author, b.category, "
            "       t.issue_date, t.due_date, t.status, t.fine_amount "
            "FROM transactions t JOIN books b ON t.book_id = b.id "
            "WHERE t.user_id = %s AND t.status = 'issued' "
            "ORDER BY t.due_date",
            (user_id,),
        )
        issued = cur.fetchall()

        # Mark overdue
        today = date.today()
        for row in issued:
            row["overdue"] = row["due_date"] < today

        cur.close(); cnx.close()
        return user, issued

    # ──────────────────────────────────────────
    #  Heuristic Recommendation Engine
    # ──────────────────────────────────────────

    def get_recommendations(self, user_id: int):
        """
        Returns a dict:
          'category_picks'  — books in user's top borrowed category
          'trending'        — top 5 most issued books system-wide
          'author_picks'    — books by user's top borrowed author
          'top_category'    — name of the inferred category
        """
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)

        # 1. User's most-borrowed category
        cur.execute(
            "SELECT b.category, COUNT(*) AS cnt "
            "FROM transactions t JOIN books b ON t.book_id = b.id "
            "WHERE t.user_id = %s "
            "GROUP BY b.category ORDER BY cnt DESC LIMIT 1",
            (user_id,),
        )
        fav_row = cur.fetchone()
        top_category = fav_row["category"] if fav_row else None

        category_picks = []
        if top_category:
            # Already-issued book ids for this user
            cur.execute(
                "SELECT book_id FROM transactions WHERE user_id=%s", (user_id,)
            )
            issued_ids = {r["book_id"] for r in cur.fetchall()}

            cur.execute(
                "SELECT * FROM books WHERE category=%s AND available_qty > 0 ORDER BY title",
                (top_category,),
            )
            category_picks = [b for b in cur.fetchall() if b["id"] not in issued_ids]

        # 2. Trending books (most issued system-wide, available)
        cur.execute(
            "SELECT b.*, COUNT(t.id) AS issue_count "
            "FROM books b LEFT JOIN transactions t ON b.id = t.book_id "
            "WHERE b.available_qty > 0 "
            "GROUP BY b.id ORDER BY issue_count DESC LIMIT 5",
        )
        trending = cur.fetchall()

        # 3. Top author from user history
        cur.execute(
            "SELECT b.author, COUNT(*) AS cnt "
            "FROM transactions t JOIN books b ON t.book_id = b.id "
            "WHERE t.user_id = %s "
            "GROUP BY b.author ORDER BY cnt DESC LIMIT 1",
            (user_id,),
        )
        fav_author_row = cur.fetchone()
        author_picks = []
        if fav_author_row:
            fav_author = fav_author_row["author"]
            cur.execute(
                "SELECT * FROM books WHERE author = %s AND available_qty > 0",
                (fav_author,),
            )
            author_picks = cur.fetchall()

        # Fallback: if no history, recommend top-5 available books
        if not category_picks and not trending:
            cur.execute("SELECT * FROM books WHERE available_qty > 0 LIMIT 5")
            category_picks = cur.fetchall()

        cur.close(); cnx.close()
        return {
            "category_picks": category_picks[:5],
            "trending":        trending,
            "author_picks":    author_picks[:5],
            "top_category":    top_category or "General",
        }


    # ──────────────────────────────────────────
    #  Admin — Book Management
    # ──────────────────────────────────────────

    def add_new_book(self, title, author, category, qty, isbn=None, rack_no="Unassigned"):
        """
        Executes an INSERT query into the 'books' table.
        Syncs with the new Admin submission route.
        """
        return self.add_book(title, author, category, isbn, qty, rack_no)

    def add_book(self, title, author, category, isbn, total_qty, rack_no="Unassigned"):
        cnx = self._get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(
                "INSERT INTO books (title, author, category, isbn, total_qty, available_qty, rack_no) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (title, author, category, isbn, int(total_qty), int(total_qty), rack_no),
            )
            cnx.commit()
            return True, f"'{title}' has been committed to global inventory."
        except mysql.connector.IntegrityError:
            return False, "Process failed: ISBN conflict or duplicate entry."
        finally:
            cur.close(); cnx.close()

    def update_book(self, book_id, title, author, category, isbn, total_qty):
        cnx = self._get_connection()
        cur = cnx.cursor()
        cur.execute(
            "UPDATE books SET title=%s, author=%s, category=%s, isbn=%s, total_qty=%s "
            "WHERE id=%s",
            (title, author, category, isbn, int(total_qty), book_id),
        )
        cnx.commit()
        cur.close(); cnx.close()
        return True, "Book updated."

    def delete_book(self, book_id, admin_id=None):
        """
        Deletes a book, BUT first validates if the book is currently out on loan.
        """
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        
        # 1. Validation check
        cur.execute("SELECT COUNT(*) as active FROM transactions WHERE book_id=%s AND status='issued'", (book_id,))
        count_row = cur.fetchone()
        if count_row and count_row['active'] > 0:
            cur.close(); cnx.close()
            return False, "Cannot delete book. Copies are currently checked out by users!"
            
        # 2. Deletion
        try:
            cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
            cnx.commit()
            if admin_id:
                self._log(cur, cnx, admin_id, f"Deleted book (ID {book_id})")
            cur.close(); cnx.close()
            return True, "Book successfully deleted."
        except Exception as e:
            cur.close(); cnx.close()
            return False, f"Deletion failed: {e}"

    # ──────────────────────────────────────────
    #  Admin — Transactions & Fines
    # ──────────────────────────────────────────

    def get_all_transactions(self):
        """Native JOIN query merging transactions, users, and books for Live Tracking."""
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        query = '''
            SELECT t.id, t.issue_date, t.due_date, t.status, t.fine_amount,
                   u.name as user_name, u.unique_id as roll_no,
                   b.title as book_title, b.author
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN books b ON t.book_id = b.id
            ORDER BY t.issue_date DESC LIMIT 50
        '''
        cur.execute(query)
        txs = cur.fetchall()
        cur.close(); cnx.close()
        return txs

    def collect_fine(self, transaction_id: int):
        """
        Mark fine as collected (fine_amount → 0, status stays 'returned').
        """
        cnx = self._get_connection()
        cur = cnx.cursor()
        cur.execute(
            "UPDATE transactions SET fine_amount = 0 WHERE id = %s AND status = 'returned'",
            (transaction_id,),
        )
        cnx.commit()
        affected = cur.rowcount
        cur.close(); cnx.close()
        if affected:
            return True, "Fine collected and cleared."
        return False, "No returned transaction found with that ID."

    def get_all_users(self):
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT id, name, email, mobile_number, unique_id as roll_no, role FROM users WHERE role != 'admin' ORDER BY name")
        users = cur.fetchall()
        cur.close(); cnx.close()
        return users

    def delete_user(self, target_user_id, admin_id=None):
        """
        Deletes a user. Blocks deletion if the user is currently holding any 'issued' books,
        otherwise ON DELETE CASCADE in MySQL would erase the ledger without restoring inventory.
        """
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        
        # Validation: Are they holding a book?
        cur.execute("SELECT COUNT(*) as active FROM transactions WHERE user_id=%s AND status='issued'", (target_user_id,))
        res = cur.fetchone()
        if res and res['active'] > 0:
            cur.close(); cnx.close()
            return False, "Cannot drop user. They must return all issued books first!"
            
        try:
            cur.execute("DELETE FROM users WHERE id = %s", (target_user_id,))
            cnx.commit()
            if admin_id:
                self._log(cur, cnx, admin_id, f"Deleted user account ID {target_user_id}.")
            cur.close(); cnx.close()
            return True, "User account successfully removed."
        except Exception as e:
            cur.close(); cnx.close()
            return False, f"Deletion failed: {e}"

    # ──────────────────────────────────────────
    #  Advanced Admin Analytics
    # ──────────────────────────────────────────

    def get_admin_stats(self):
        """Returns complex counts for the Admin Web Dashboard statistics cards."""
        cnx = self._get_connection()
        cur = cnx.cursor(dictionary=True)
        stats = {
            "total_students": 0,
            "total_teachers": 0,
            "total_books": 0,
            "active_issues": 0,
            "fines_collected": 0.00
        }
        
        cur.execute("SELECT role, COUNT(*) as c FROM users GROUP BY role")
        for row in cur.fetchall():
            if row['role'] == 'student': stats['total_students'] = row['c']
            if row['role'] == 'teacher': stats['total_teachers'] = row['c']
            
        cur.execute("SELECT SUM(total_qty) as t FROM books")
        res = cur.fetchone()
        stats['total_books'] = res['t'] if res['t'] else 0
        
        cur.execute("SELECT COUNT(*) as c FROM transactions WHERE status='issued'")
        stats['active_issues'] = cur.fetchone()['c']
        
        cur.execute("SELECT SUM(fine_amount) as f FROM transactions WHERE status='returned'")
        res = cur.fetchone()
        stats['fines_collected'] = float(res['f']) if res['f'] else 0.00
        
        cur.close(); cnx.close()
        return stats

    def get_inventory_report(self):
        return self.get_all_books()

    # ──────────────────────────────────────────
    #  Utility
    # ──────────────────────────────────────────

    def _log(self, cursor, cnx, user_id, action: str):
        """Insert an activity log row (best-effort)."""
        try:
            cursor.execute(
                "INSERT INTO activity_logs (user_id, action) VALUES (%s, %s)",
                (user_id, action),
            )
        except Exception:
            pass  # logging should never break the main flow
