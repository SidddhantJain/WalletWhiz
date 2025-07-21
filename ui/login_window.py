#- filepath: d:\Siddhant\projects\WalletWhiz\WalletWhiz\ui\login_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from database.db_manager import DBManager

class LoginWindow(QWidget):
    login_successful = pyqtSignal(int)  # Emit user_id when login successful
    
    def __init__(self):
        super().__init__()
        self.db_manager = DBManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('WalletWhiz - Login')
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('WalletWhiz')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Tab widget for Login/Register
        self.tab_widget = QTabWidget()
        
        # Login tab
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        
        login_layout.addWidget(QLabel("Username:"))
        login_layout.addWidget(self.login_username)
        login_layout.addWidget(QLabel("Password:"))
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(login_btn)
        
        login_tab.setLayout(login_layout)
        self.tab_widget.addTab(login_tab, "Login")
        
        # Register tab
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Username")
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm Password")
        self.register_confirm.setEchoMode(QLineEdit.Password)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        
        register_layout.addWidget(QLabel("Username:"))
        register_layout.addWidget(self.register_username)
        register_layout.addWidget(QLabel("Password:"))
        register_layout.addWidget(self.register_password)
        register_layout.addWidget(QLabel("Confirm Password:"))
        register_layout.addWidget(self.register_confirm)
        register_layout.addWidget(register_btn)
        
        register_tab.setLayout(register_layout)
        self.tab_widget.addTab(register_tab, "Register")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget { background-color: #f8f9fa; }
            QLineEdit { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            QPushButton { 
                background-color: #007bff; color: white; 
                padding: 10px; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
    
    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        user_id = self.db_manager.authenticate_user(username, password)
        if user_id:
            self.login_successful.emit(user_id)
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            
    def handle_register(self):
        username = self.register_username.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if not username or not password or not confirm:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
            
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
            
        if self.db_manager.create_user(username, password):
            QMessageBox.information(self, "Success", "Account created successfully! Please login.")
            self.tab_widget.setCurrentIndex(0)  # Switch to login tab
        else:
            QMessageBox.warning(self, "Error", "Username already exists or database error")