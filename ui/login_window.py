#- filepath: d:\Siddhant\projects\WalletWhiz\WalletWhiz\ui\login_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class LoginWindow(QWidget):
    login_successful = pyqtSignal(int)  # Signal to indicate login success

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WalletWhiz Login")
        self.setFixedSize(1350, 720)
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Login Tab
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        login_layout.addWidget(QLabel("Username:"))
        self.login_username = QLineEdit()
        login_layout.addWidget(self.login_username)
        login_layout.addWidget(QLabel("Password:"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.login_password)
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(login_btn)
        self.tabs.addTab(login_tab, "Login")

        # Register Tab
        register_tab = QWidget()
        register_layout = QVBoxLayout(register_tab)
        register_layout.addWidget(QLabel("Username:"))
        self.register_username = QLineEdit()
        register_layout.addWidget(self.register_username)
        register_layout.addWidget(QLabel("Password:"))
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        register_layout.addWidget(self.register_password)
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        register_layout.addWidget(register_btn)
        self.tabs.addTab(register_tab, "Register")

        self.setLayout(layout)

    def handle_login(self):
        # Dummy login: accept any non-empty username/password
        if self.login_username.text() and self.login_password.text():
            self.login_successful.emit(1)  # Emit dummy user_id
            self.close()

    def handle_register(self):
        # Dummy register: accept any non-empty username/password
        if self.register_username.text() and self.register_password.text():
            self.tabs.setCurrentIndex(0)