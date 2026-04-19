"""
app.py
------
Flask web application — Student-facing portal for LibraryPro.
"""

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash,
)
from engine import LibraryEngine
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)          # rotate every restart (fine for dev)

engine = LibraryEngine()

# ─────────────────────────────────────────────
#  Helper – login guard
# ─────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@app.route("/", methods=["GET"])
@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user_id" in session:
        role = session.get("role", "student")
        if role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif role == "guest":
            return redirect(url_for("guest_dashboard"))
        elif role == "teacher":
            return redirect(url_for("teacher_dashboard"))
        else:
            return redirect(url_for("student_dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        unique_id = request.form.get("unique_id", "").strip()
        mobile = request.form.get("mobile", "").strip()
        role = request.form.get("role", "student").strip()
        password = request.form.get("password", "")
        
        ok, msg = engine.register_user(name, email, password, mobile, role, unique_id)
        if ok:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        flash(msg, "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user     = engine.authenticate_user(email, password)
        if user:
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            session["role"]      = user.get("role", "student")
            
            flash(f"Welcome back, {user['name']}! 👋", "success")
            # Redirect logic based on role
            if session["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif session["role"] == "guest":
                return redirect(url_for("guest_dashboard"))
            elif session["role"] == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
                
        flash("Invalid email or password. Please try again.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/admin_dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Access Denied: Admins only.", "danger")
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        # Legacy support (keeping for robustness)
        return redirect(url_for("add_book_route"), code=307)
        
    stats = engine.get_admin_stats()
    users = engine.get_all_users()
    books = engine.get_inventory_report()
    txs = engine.get_all_transactions()
        
    return render_template(
        "admin_dashboard.html",
        stats=stats,
        users=users,
        books=books,
        transactions=txs
    )

# ─────────────────────────────────────────────
#  Admin — Book Management
# ─────────────────────────────────────────────

@app.route('/admin/add_book', methods=['POST'])
@login_required
def add_book_route():
    """
    Handles the submission of the 'Provision New Book' form from the Admin Dashboard.
    Ensures that only users with the 'admin' role can execute this operation.
    """
    if session.get("role") != "admin":
        flash("Unauthorized access attempt detected.", "danger")
        return redirect(url_for("dashboard"))
    
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()
    qty = request.form.get("qty", "0")
    isbn = request.form.get("isbn", "").strip()
    rack_no = request.form.get("rack_no", "").strip() or "Unassigned"
    
    # Backend synchronization with LibraryEngine
    ok, msg = engine.add_new_book(title, author, category, int(qty), isbn, rack_no)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/delete_book/<int:book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    if session.get("role") != "admin":
        flash("Access Denied: Admins only.", "danger")
        return redirect(url_for("dashboard"))
        
    ok, msg = engine.delete_book(book_id, admin_id=session["user_id"])
    flash(msg, "success" if ok else "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if session.get("role") != "admin":
        flash("Access Denied.", "danger")
        return redirect(url_for("dashboard"))
        
    ok, msg = engine.delete_user(user_id, admin_id=session["user_id"])
    flash(msg, "success" if ok else "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/student_dashboard")
@login_required
def student_dashboard():
    # Only block guests or admins if you wish to enforce strict routing
    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
        
    query = request.args.get("q", "").strip()
    if query:
        books = engine.search_books(query)
    else:
        books = engine.get_all_books()

    recs = engine.get_recommendations(session["user_id"])
    return render_template(
        "dashboard.html",
        books=books,
        recs=recs,
        query=query,
        user_name=session["user_name"],
        role=session.get("role", "student")
    )


@app.route("/teacher_dashboard")
@login_required
def teacher_dashboard():
    query = request.args.get("q", "").strip()
    if query:
        books = engine.search_books(query)
    else:
        books = engine.get_all_books()

    recs = engine.get_recommendations(session["user_id"])
    return render_template(
        "dashboard.html",
        books=books,
        recs=recs,
        query=query,
        user_name=session["user_name"],
        role="teacher"
    )


@app.route("/guest_dashboard")
@login_required
def guest_dashboard():
    query = request.args.get("q", "").strip()
    if query:
        books = engine.search_books(query)
    else:
        books = engine.get_all_books()

    # Guests don't get personalised recs, but we can send generic ones
    recs = engine.get_recommendations(session["user_id"])
    return render_template(
        "dashboard.html",
        books=books,
        recs=recs,
        query=query,
        user_name=session["user_name"],
        role="guest"
    )


@app.route("/recommendations")
@login_required
def recommendations():
    recs = engine.get_recommendations(session["user_id"])
    return render_template(
        "recommendations.html",
        recs=recs,
        user_name=session["user_name"],
    )


@app.route("/profile")
@login_required
def profile():
    user, issued = engine.get_user_profile(session["user_id"])
    return render_template(
        "profile.html",
        user=user,
        issued=issued,
        user_name=session["user_name"],
    )


@app.route("/issue/<int:book_id>", methods=["POST"])
@login_required
def issue_book(book_id):
    ok, msg = engine.issue_book(session["user_id"], book_id)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("dashboard"))


@app.route("/return/<int:txn_id>", methods=["POST"])
@login_required
def return_book(txn_id):
    ok, msg = engine.return_book(txn_id, session["user_id"])
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("profile"))


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting LibraryPro Student Portal on http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
