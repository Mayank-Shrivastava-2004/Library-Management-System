"""
main.py
-------
Entry point for LibraryPro.

Presents a menu to the user:
  1. Launch Student Web Portal  (Flask)
  2. Launch Librarian Admin App (Tkinter)
"""

import subprocess
import sys
import os
import time

BANNER = r"""
╔══════════════════════════════════════════════════╗
║           📚  L i b r a r y P r o               ║
║     Multi-Layer Library Management System        ║
╚══════════════════════════════════════════════════╝
"""

MENU = """
  Select interface to launch:

    [1]  🌐  Student Web Portal     (Flask @ http://127.0.0.1:5000)
    [2]  🖥   Librarian Admin Panel  (Tkinter Desktop App)
    [0]  ❌  Exit

"""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    clear()
    print(BANNER)


def launch_web():
    print("\n  [→] Starting Student Web Portal …")
    print("      Open http://127.0.0.1:5000 in your browser.")
    print("      Press Ctrl+C here to stop the server.\n")
    try:
        proc = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\n  [✓] Web Portal stopped.")


def launch_admin():
    print("\n  [→] Opening Librarian Admin Panel …\n")
    proc = subprocess.Popen(
        [sys.executable, "admin_panel.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    proc.wait()
    print("\n  [✓] Admin Panel closed.")


def check_setup():
    """Remind user to run setup_database.py if this is the first run."""
    marker = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".db_initialized")
    if not os.path.exists(marker):
        print("  ⚠  First time setup detected!")
        print("  Run: python setup_database.py")
        print("  Then restart main.py.\n")
        ans = input("  Run setup now? [y/N]: ").strip().lower()
        if ans == "y":
            subprocess.run([sys.executable, "setup_database.py"],
                           cwd=os.path.dirname(os.path.abspath(__file__)))
            open(marker, "w").close()
        print()


def main():
    print_banner()
    check_setup()

    while True:
        print(MENU)
        choice = input("  Enter choice [0/1/2]: ").strip()

        if choice == "1":
            launch_web()
            print_banner()
        elif choice == "2":
            launch_admin()
            print_banner()
        elif choice == "0":
            print("\n  Goodbye! 📚\n")
            break
        else:
            print("\n  Invalid choice. Please enter 0, 1, or 2.")
            time.sleep(1)
            print_banner()


if __name__ == "__main__":
    main()
