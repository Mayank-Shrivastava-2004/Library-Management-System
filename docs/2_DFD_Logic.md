# 2. Data Flow Diagram (DFD) & Logic Flow

## Level 0 DFD (Context Diagram)

The Level 0 DFD shows the entire system as a single central process interacting with external entities.

```text
[ External Entities ]                     [ System ]                      [ Data Store ]
                                           
+------------------+                   +---------------+
|     Student      | ===(Requests)===> |               |
|  (Web Browser)   | <===(Views)====== |               |
+------------------+                   |  LibraryPro   |                   +--------------+
                                       |  Management   | === (Queries) ==> |    MySQL     |
+------------------+                   |    System     | <== (Results) === |   Database   |
|     Admin        | ===(Updates)====> |               |                   +--------------+
| (Tkinter Desktop)| <===(Reports)==== |               |
+------------------+                   +---------------+
```

## Level 1 DFD (Process Level)

The Level 1 DFD breaks down the main system into specific functional sub-processes.

```text
+----------+      1. Auth Request     +--------------------+
| Student  | -----------------------> | 1.0 Authentication | ------ (Query: User Details) ----+
| / Admin  | <----------------------- |      Process       |                                  |
+----------+       Access Granted     +--------------------+                                  |
     |                                                                                        V
     |            Search Query        +--------------------+                           +---------------+
     +------------------------------> | 2.0 Web Backend    | --- (Query: Search) ----> |      D1       |
     |                                |   (Flask App)      | <--- (Book Data) -------- |  MySQL Database|
     | <----------------------------- |                    |                           +---------------+
     |            Search Results      +--------------------+                                  ^
     |                                          | (Recommendation Engine Process)             |
     |                                          V                                             |
     |                                +--------------------+                                  |
     |            Add/Edit Book       | 3.0 Desktop Admin  | --- (INSERT/UPDATE) ---------+   |
     +------------------------------> |    (Tkinter)       |                              |   |
                                      +--------------------+                              |   |
                                                                                          V   V
```

---

## Logic Flows

### 1. Data Flow: Student searching for a book via the Flask Web App
1. **User Action:** The student types a book name into the search bar on `dashboard.html` and clicks Search.
2. **Web Server:** The browser sends an HTTP GET request with the query parameter `?q=search term` to the Flask `app.py` server.
3. **App Engine:** Flask routes the request to the central `engine.py`.
4. **Database Query:** The engine constructs an SQL query using `LIKE` operator to find corresponding titles/authors and executes it securely using `mysql-connector-python`.
5. **Database Response:** MySQL returns the matching records to Python.
6. **Web View Generation:** Flask injects the data into the HTML via Jinja2 templates.
7. **User View:** The filtered list of books appears in the student's browser.

### 2. Data Flow: Admin adding a new book via Tkinter Desktop App
1. **User Action:** The librarian fills out the text fields in the Tkinter UI (`admin_panel.py`) and clicks "Add Book".
2. **Input Fetch:** Tkinter extracts strings from the input widgets (`get()`).
3. **Logic Engine Pass:** The strings are passed to the `add_book()` method in `engine.py`.
4. **Database Insertion:** The engine formulates an `INSERT INTO books...` SQL query.
5. **Database Execution:** `mysql-connector` executes the transaction and issues a `commit()`.
6. **UI Refresh:** If the insert is successful, the app queries the database again to fetch the updated book list and refreshes the Tkinter TreeView to show the newly added book immediately.

### Centralized Architecture
The **Database as the Central Nervous System:** Notice that both `app.py` (Flask) and `admin_panel.py` (Tkinter) never talk to each other directly. They both connect to `engine.py`, which routes traffic directly into the **MySQL Database**. This ensures that if an Admin adds a book on the desktop, a student will instantly see it available on the web portal without any sync delays.
