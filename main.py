#-- filepath: d:\Siddhant\projects\WalletWhiz\WalletWhiz\main.py
# main.py

import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import WalletWhizMainWindow

class WalletWhizApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.main_window = None
        
    def show_login(self):
        """Show login window"""
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
        
    def on_login_success(self, user_id):
        """Handle successful login"""
        self.main_window = WalletWhizMainWindow(user_id)
        self.main_window.show()
        
    def run(self):
        """Run the application"""
        self.show_login()
        return self.app.exec_()

if __name__ == '__main__':
    app = WalletWhizApp()
    sys.exit(app.run())