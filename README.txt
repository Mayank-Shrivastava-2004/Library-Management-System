======================================================
LIBRARYPRO - MULTI-LAYER LIBRARY MANAGEMENT SYSTEM
======================================================

PROJECT DESCRIPTION:
--------------------
LibraryPro is a Multi-Layer Library Management System designed to simplify book inventory tracking and intelligently recommend reading material to students. It comprises a centralized MySQL database that serves two separate platforms simultaneously:
1. A Tkinter Desktop Application used by Admins/Librarians to manage book inventory, monitor student transactions, and calculate fine penalties.
2. A Flask Web Dashboard for Students to browse books, issue resources, and view their personalized "Heuristic Recommendations".

ABSTRACT:
---------
The digitalization of library resources has made inventory management highly complex. This project proposes a Multi-Layer Library Management System designed to simplify library operations while actively engaging students through a dual-interface architecture. 

The system features a robust Tkinter-based Desktop Application serving as an administrative console for librarians to manage book inventory, monitor real-time transactions, and process fining mechanisms. Concurrently, a Flask-powered web platform allows students to browse catalogs, view their digital profiles, and process book issuances. 

A standout feature of this system is the implementation of a computationally lightweight, non-ML Heuristic Recommendation Engine. By leveraging relational database metrics, the system intelligently recommends new reading material based on an individual student’s past category preferences and system-wide trending data. Built on Python and MySQL, the architecture demonstrates an effective integration of backend logic, GUI, and database administration tailored for academic institutions.

SOFTWARE REQUIREMENTS:
----------------------
1. Operating System : Windows 10 or Windows 11
2. Database Server : MySQL (Available inherently or via XAMPP)
3. Programming Language : Python 3.8+
4. Web Framework : Flask & Werkzeug
5. Database Connector: mysql-connector-python
6. Frontend Tech : HTML5, CSS3, Bootstrap 5
7. Desktop UI Tech : Tkinter (Standard Python Library)

DATA FLOW EXPLANATION:
----------------------
When a student interacts with the system, the Data Flow is seamlessly integrated. For instance, if a student wants to issue a book via the Web UI:
1. The student clicks "Issue" on the Flask Web Dashboard (`app.py`).
2. Flask sends the user_id and book_id to the Central Logic Engine (`engine.py`).
3. The Engine checks the database to verify `available_qty > 0`. If true, it inserts a new row into the `transactions` table in MySQL and decrements the book's quantity.
4. Instantaneously, if the Librarian is reviewing the Tkinter `admin_panel.py`, they click "Refresh" on the Transactions tab.
5. The Admin App fetches the exact same MySQL database, retrieving the new transaction data. The student's name, the book, and the "Due Date" appear on the librarian's screen without any syncing issues since MySQL acts as the central source of truth.

INSTALLATION & RUN GUIDE:
-------------------------

STEP 1: DATABASE SETUP
- Ensure MySQL is running on your machine (via XAMPP or standalone).
- Open `setup_database.py` or `fix_db.py` in a text editor.
- Make sure HOST="localhost" and USER="root". If you set a password for MySQL, add it to the PASSWORD="" variable.
- Open your terminal/command prompt and run:
  > python fix_db.py
  (This script creates the database "librarypro", all 4 tables, constraints, and demo data).

STEP 2: INSTALL PYTHON DEPENDENCIES
- In the terminal, run the following to install all necessary Python packages:
  > pip install flask mysql-connector-python Werkzeug

STEP 3: RUN THE APPLICATION
- Launch the main menu hub by running:
  > python main.py

Option 1: Student Web App
- Type "1" and press Enter.
- Open your browser and go to: http://127.0.0.1:5000
- Log in using demo credentials: alice@library.com (Password: alice123)

Option 2: Admin Desktop App
- Type "2" and press Enter.
- The Tkinter window will pop up showing Books, Transactions, and Fine collections.

To stop either application, close their window or press Ctrl+C in the terminal.
