from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SharedFinanceTab(QWidget):
    def __init__(self, lending_controller):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Shared Finances / Lend & Borrow"))
        # Add UI elements for lending_controller here
        self.setLayout(layout)
