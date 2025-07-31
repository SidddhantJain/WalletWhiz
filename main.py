#-- filepath: d:\Siddhant\projects\WalletWhiz\WalletWhiz\main.py
# main.py

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox

def print_module_paths():
    print("sys.path:")
    for p in sys.path:
        print("  ", p)
    print("Current working directory:", os.getcwd())
    print("Expected UI paths:")
    print("  ", os.path.abspath(os.path.join(os.getcwd(), "ui", "login_window.py")))
    print("  ", os.path.abspath(os.path.join(os.getcwd(), "ui", "main_window.py")))

def global_exception_hook(exctype, value, tb):
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print("Uncaught exception:", error_msg)
    QMessageBox.critical(None, "Uncaught Exception", error_msg)
    sys.exit(1)

class WalletWhizApp:
    def __init__(self):
        print_module_paths()
        self.app = QApplication(sys.argv)  # <-- Ensure QApplication is created first
        sys.excepthook = global_exception_hook
        try:
            from ui.login_window import LoginWindow
            from ui.main_window import WalletWhizMainWindow
            print("UI modules imported successfully.")
        except Exception as e:
            print("Error importing UI modules:", e)
            print(traceback.format_exc())
            QMessageBox.critical(None, "Import Error", f"Failed to import UI modules:\n{e}\n\n{traceback.format_exc()}")
            sys.exit(1)
        self.LoginWindow = LoginWindow
        self.WalletWhizMainWindow = WalletWhizMainWindow

        self.login_window = None
        self.main_window = None

    def show_login(self):
        try:
            print("Showing login window...")
            self.login_window = self.LoginWindow()
            self.login_window.login_successful.connect(self.on_login_success)
            self.login_window.show()
            print("Login window shown.")
        except Exception as e:
            print("Error in show_login:", e)
            print(traceback.format_exc())
            QMessageBox.critical(None, "Startup Error", f"Failed to start WalletWhiz:\n{e}\n\n{traceback.format_exc()}")
            sys.exit(1)

    def on_login_success(self, user_id):
        try:
            print(f"Login successful for user_id: {user_id}")
            if self.login_window:
                self.login_window.close()
            self.main_window = self.WalletWhizMainWindow(user_id)
            self.main_window.logout_requested.connect(self.show_login)  # Add logout handler
            self.main_window.show()
            print("Main window shown.")
        except Exception as e:
            print("Error in on_login_success:", e)
            print(traceback.format_exc())
            QMessageBox.critical(None, "Application Error", f"Failed to load main application:\n{e}\n\n{traceback.format_exc()}")
            self.show_login()

    def run(self):
        try:
            self.show_login()
            print("Starting event loop...")
            result = self.app.exec_()
            print("Event loop finished.")
            return result
        except Exception as e:
            print("Error in run:", e)
            print(traceback.format_exc())
            QMessageBox.critical(None, "Fatal Error", f"Application crashed:\n{e}\n\n{traceback.format_exc()}")
            return 1

if __name__ == '__main__':
    print("Starting WalletWhizApp...")
    try:
        sys.exit(WalletWhizApp().run())
    except Exception as e:
        print("Fatal error at startup:", e)
        import traceback
        print(traceback.format_exc())
        QMessageBox.critical(None, "Startup Error", f"Fatal error:\n{e}\n\n{traceback.format_exc()}")
        sys.exit(1)