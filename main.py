# WalletWhiz/main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from database.db_manager import DBManager

class WalletWhizMain(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WalletWhiz 💸")
        self.setGeometry(300, 150, 800, 600)

        # Connect to database
        self.db = DBManager()

        # UI setup
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        welcome_label = QLabel("Welcome to WalletWhiz!")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(welcome_label)

        # Example: Show total transactions count
        transactions = self.db.get_transactions()
        count_label = QLabel(f"Total Transactions Found: {len(transactions)}")
        count_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(count_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        # Ensure DB connection is closed
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WalletWhizMain()
    window.show()
    sys.exit(app.exec_())
