import tkinter as tk
from tkinter import ttk, messagebox
from engine import LibraryEngine

# Theme Colors
BG_COLOR = "#0f172a"
FG_COLOR = "#f8fafc"
ACCENT_COLOR = "#38bdf8"
CARD_BG = "#1e293b"


class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LibraryPro — Native Control Console")
        self.geometry("900x600")
        self.configure(bg=BG_COLOR)
        
        self.engine = LibraryEngine()
        # Admin ID defaults to 1 for logging purposes. In a real system, you'd pass the actual logged-in admin's ID.
        self.admin_id = 1 

        self._apply_styles()
        self._build_ui()
        self.refresh_all()

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # TNotebook
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD_BG, foreground=FG_COLOR, padding=[15, 5], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#000000")])

        # TFrame
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Main.TFrame", background=BG_COLOR)

        # TLabel
        style.configure("TLabel", background=CARD_BG, foreground=FG_COLOR, font=("Inter", 10))
        style.configure("Header.TLabel", background=BG_COLOR, foreground=ACCENT_COLOR, font=("Inter", 16, "bold"))

        # Treeview
        style.configure(
            "Treeview",
            background=BG_COLOR,
            fieldbackground=BG_COLOR,
            foreground=FG_COLOR,
            rowheight=30,
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#000")])
        style.configure("Treeview.Heading", background=CARD_BG, foreground=ACCENT_COLOR, font=("Inter", 10, "bold"))

        # TButton
        style.configure("TButton", font=("Inter", 10, "bold"), padding=6)

    def _build_ui(self):
        # Header
        header_frame = ttk.Frame(self, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=10, padx=20)
        ttk.Label(header_frame, text="System Administrative Console", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Force Sync Data", command=self.refresh_all).pack(side=tk.RIGHT)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Build individual tabs
        self.tab_users = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_inventory = ttk.Frame(self.notebook, style="Card.TFrame")

        self.notebook.add(self.tab_users, text="User Registry")
        self.notebook.add(self.tab_inventory, text="Inventory Control")

        self._build_user_tab()
        self._build_inventory_tab()

    # ─────────────────────────────────────────────────────────
    #   TAB 1: User Registry
    # ─────────────────────────────────────────────────────────
    def _build_user_tab(self):
        top_frame = ttk.Frame(self.tab_users, style="Card.TFrame")
        top_frame.pack(fill=tk.X, pady=10, padx=10)
        ttk.Label(top_frame, text="Registered Directory (Students & Teachers)").pack(side=tk.LEFT)

        columns = ("id", "name", "role", "email", "unique_id")
        self.user_tree = ttk.Treeview(self.tab_users, columns=columns, show="headings")
        
        self.user_tree.heading("id", text="Sys ID")
        self.user_tree.heading("name", text="Full Name")
        self.user_tree.heading("role", text="Security Role")
        self.user_tree.heading("email", text="Email Address")
        self.user_tree.heading("unique_id", text="Internal ID / Roll No")
        
        self.user_tree.column("id", width=60, anchor=tk.CENTER)
        self.user_tree.column("name", width=200)
        self.user_tree.column("role", width=120, anchor=tk.CENTER)
        self.user_tree.column("email", width=200)
        self.user_tree.column("unique_id", width=150, anchor=tk.CENTER)
        
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
            
        users = self.engine.get_all_users()
        for u in users:
            self.user_tree.insert("", tk.END, values=(
                u["id"], u["name"], u["role"].upper(), u["email"], u["roll_no"] or "N/A"
            ))

    # ─────────────────────────────────────────────────────────
    #   TAB 2: Inventory Control
    # ─────────────────────────────────────────────────────────
    def _build_inventory_tab(self):
        # Tools panel on the right, Treeview on the left
        right_panel = ttk.Frame(self.tab_inventory, style="Card.TFrame", width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Delete Selected Book").pack(pady=(0, 5))
        ttk.Button(right_panel, text="Remove from System", command=self.handle_delete_book).pack(fill=tk.X, pady=5)
        
        ttk.Label(right_panel, text="Add New Book").pack(pady=(30, 5))
        
        # Add book form
        self.entry_title = ttk.Entry(right_panel)
        self.entry_title.insert(0, "Title")
        self.entry_title.pack(fill=tk.X, pady=2)
        
        self.entry_author = ttk.Entry(right_panel)
        self.entry_author.insert(0, "Author")
        self.entry_author.pack(fill=tk.X, pady=2)
        
        self.entry_cat = ttk.Entry(right_panel)
        self.entry_cat.insert(0, "Category")
        self.entry_cat.pack(fill=tk.X, pady=2)
        
        self.entry_isbn = ttk.Entry(right_panel)
        self.entry_isbn.insert(0, "ISBN")
        self.entry_isbn.pack(fill=tk.X, pady=2)
        
        self.entry_qty = ttk.Entry(right_panel)
        self.entry_qty.insert(0, "1")
        self.entry_qty.pack(fill=tk.X, pady=2)

        ttk.Button(right_panel, text="Commit Inventory", command=self.handle_add_book).pack(fill=tk.X, pady=10)

        # Inventory Table
        columns = ("id", "title", "author", "category", "avail", "total")
        self.inv_tree = ttk.Treeview(self.tab_inventory, columns=columns, show="headings")
        
        self.inv_tree.heading("id", text="Book ID")
        self.inv_tree.heading("title", text="Title")
        self.inv_tree.heading("author", text="Author")
        self.inv_tree.heading("category", text="Genre")
        self.inv_tree.heading("avail", text="Available")
        self.inv_tree.heading("total", text="Total")
        
        self.inv_tree.column("id", width=60, anchor=tk.CENTER)
        self.inv_tree.column("title", width=200)
        self.inv_tree.column("author", width=150)
        self.inv_tree.column("category", width=100)
        self.inv_tree.column("avail", width=70, anchor=tk.CENTER)
        self.inv_tree.column("total", width=70, anchor=tk.CENTER)
        
        self.inv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _load_inventory(self):
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
            
        books = self.engine.get_all_books()
        for b in books:
            self.inv_tree.insert("", tk.END, values=(
                b["id"], b["title"], b["author"], b["category"], b["available_qty"], b["total_qty"]
            ))

    def handle_delete_book(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a book to delete.")
            return

        item = self.inv_tree.item(selected[0])
        book_id = item["values"][0]
        title = item["values"][1]

        if messagebox.askyesno("Confirm Deletion", f"Permanently wipe '{title}' from database?"):
            ok, msg = self.engine.delete_book(book_id, admin_id=self.admin_id)
            if ok:
                messagebox.showinfo("Success", msg)
                self._load_inventory()
            else:
                messagebox.showerror("Validation Blocked", msg)

    def handle_add_book(self):
        t = self.entry_title.get().strip()
        a = self.entry_author.get().strip()
        c = self.entry_cat.get().strip()
        i = self.entry_isbn.get().strip()
        q = self.entry_qty.get().strip()

        if not (t and a and c and i and q.isdigit()):
            messagebox.showerror("Error", "Please fill all fields. Qty must be a number.")
            return

        ok, msg = self.engine.add_book(t, a, c, i, int(q))
        if ok:
            messagebox.showinfo("Success", msg)
            self._load_inventory()
            # Reset entries
            self.entry_title.delete(0, tk.END)
            self.entry_author.delete(0, tk.END)
            self.entry_cat.delete(0, tk.END)
            self.entry_isbn.delete(0, tk.END)
            self.entry_qty.delete(0, tk.END)
            self.entry_qty.insert(0, "1")
        else:
            messagebox.showerror("Error", msg)

    # ─────────────────────────────────────────────────────────
    #   General Actions
    # ─────────────────────────────────────────────────────────
    def refresh_all(self):
        self._load_users()
        self._load_inventory()


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
