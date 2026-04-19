# 📚 LibraryPro - Multi-Layer Library System

LibraryPro is a full-stack, dual-interface library management and heuristic recommendation system designed for modern academic institutions. It features an integrated centralized MySQL database connecting a Flask web portal (for students) and a Tkinter desktop application (for librarians).

## 🚀 Features
- **Dual Platforms:** Web dashboard for student access; native desktop software for admin oversight.
- **Heuristic Recommendation Engine:** Rule-based (non-ML) smart suggestions leveraging user borrowing history.
- **Automated Fines:** Real-time late fee calculation based purely on date mathematics.
- **Glassmorphism UI:** Modern, responsive frontend design layered over Bootstrap 5.
- **Centralized Synchronisation:** Changes natively sync across both ecosystems via MySQL.

---

## 🛠 Required Technologies
- **Python** (3.8 or newer)
- **MySQL Server** (Standalone or via XAMPP/WAMP)
- **Flask** & **Werkzeug**
- **Tkinter**
- **HTML/CSS + Bootstrap 5**

---

## ⚙️ Installation & Setup Guide

### Step 1: Install MySQL
You need a running MySQL database. If you don't have it, install [XAMPP](https://www.apachefriends.org/index.html) and start the **MySQL** module from the control panel.

### Step 2: Clone & Install Python Requirements
Open a terminal in the project directory and install the necessary specific packages:
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, manually run: `pip install flask mysql-connector-python Werkzeug`)*

### Step 3: Configure Database
If your MySQL root user has a password, open `setup_database.py` and `engine.py` and update the `PASSWORD` field in the `DB_CONFIG` dictionary. (If using default XAMPP, leave it blank `""`).

Run the initialization script. **This creates the database, schema, and inserts test data automatically:**
```bash
python setup_database.py
```
*(Note: If you run into unknown database errors, utilise the `python fix_db.py` script included in the repo.)*

---

## 🎮 How to Run the Application

The system includes a single launcher for simplicity.
```bash
python main.py
```
A CLI menu will appear asking what you wish to launch:
1. **Press `1`** to launch the **Student Web Portal** (Flask). It will run at `http://127.0.0.1:5000`.
2. **Press `2`** to launch the **Admin Desktop Panel** (Tkinter application).

### 🔑 Demo Credentials (Web App)
If you ran the setup scripts, use these credentials to immediately test the web portal functionality:
- **Email:** `alice@library.com` | **Password:** `alice123`
- **Email:** `bob@library.com`   | **Password:** `bob123`

---

## 👨‍💻 Project Structure
- `main.py` - Unified runner software
- `app.py` - Flask web-controller
- `engine.py` - Database API layer / Main class algorithms
- `admin_panel.py` - UI layout for Desktop admin software
- `templates/` & `static/` - HTML files and CSS aesthetic documents
- `docs/` - Academic paperwork, DB designs, and flow architectures
