from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCalendarWidget, QTabWidget, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QTextEdit,
    QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox, QProgressBar, QFileDialog
)
from PyQt5.QtCore import pyqtSignal, QDate
import csv
from utils.tags import extract_tags, suggest_tags, filter_transactions_by_tag
from utils.heatmap import get_daily_spending, get_heat_color
from utils.bank_import import import_bank_csv
from utils.backup import backup_to_local, restore_from_local
from utils.ai_analysis import analyze_expenses, get_payment_method_stats
from utils.recurring_detector import detect_recurring
from utils.achievements import check_achievements

class WalletWhizMainWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("WalletWhiz Main")
        self.setFixedSize(900, 700)
        self.transactions = []
        self.budgets = {}
        self.lendings = []
        self.currency = "₹"
        self.theme = "Light"
        main_layout = QVBoxLayout(self)

        # Top bar with logout
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel(f"User ID: {user_id}"))
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        top_bar.addStretch()
        top_bar.addWidget(logout_btn)
        main_layout.addLayout(top_bar)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Dashboard Tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        self.dashboard_summary = QLabel("Total Income: 0 | Expenses: 0 | Balance: 0")
        dashboard_layout.addWidget(self.dashboard_summary)
        dashboard_layout.addWidget(QLabel("Pie/Bar Chart (Demo)"))
        dashboard_layout.addWidget(QCalendarWidget())
        self.tabs.addTab(dashboard_tab, "Dashboard")

        # Transactions Tab
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)
        form_layout = QHBoxLayout()
        self.trans_type = QComboBox()
        self.trans_type.addItems(["Income", "Expense"])
        form_layout.addWidget(self.trans_type)
        self.trans_amount = QDoubleSpinBox()
        self.trans_amount.setMaximum(1000000)
        form_layout.addWidget(self.trans_amount)
        self.trans_category = QComboBox()
        self.trans_category.addItems(["Food", "Rent", "Transport", "Other"])
        form_layout.addWidget(self.trans_category)
        self.trans_notes = QLineEdit()
        self.trans_notes.setPlaceholderText("Notes")
        form_layout.addWidget(self.trans_notes)
        self.trans_date = QDate.currentDate()
        self.trans_date_widget = QCalendarWidget()
        self.trans_date_widget.setMaximumHeight(150)
        form_layout.addWidget(self.trans_date_widget)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_transaction)
        form_layout.addWidget(add_btn)
        transactions_layout.addLayout(form_layout)

        self.transactions_table = QTableWidget(0, 6)
        self.transactions_table.setHorizontalHeaderLabels(
            ["Date", "Type", "Amount", "Category", "Notes", "Actions"]
        )
        transactions_layout.addWidget(self.transactions_table)
        self.tabs.addTab(transactions_tab, "Transactions")

        # Budget Tab
        budget_tab = QWidget()
        budget_layout = QVBoxLayout(budget_tab)
        budget_form = QHBoxLayout()
        self.budget_category = QComboBox()
        self.budget_category.addItems(["Food", "Rent", "Transport", "Other"])
        budget_form.addWidget(self.budget_category)
        self.budget_limit = QDoubleSpinBox()
        self.budget_limit.setMaximum(1000000)
        budget_form.addWidget(self.budget_limit)
        set_budget_btn = QPushButton("Set Budget")
        set_budget_btn.clicked.connect(self.set_budget)
        budget_form.addWidget(set_budget_btn)
        budget_layout.addLayout(budget_form)
        self.budget_bar = QProgressBar()
        budget_layout.addWidget(self.budget_bar)
        self.budget_alert = QLabel("")
        budget_layout.addWidget(self.budget_alert)
        self.tabs.addTab(budget_tab, "Budget")

        # Reports Tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        reports_layout.addWidget(export_btn)
        self.tabs.addTab(reports_tab, "Reports")

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        currency_label = QLabel("Currency:")
        settings_layout.addWidget(currency_label)
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["₹", "$", "€"])
        self.currency_combo.setCurrentText(self.currency)
        self.currency_combo.currentTextChanged.connect(self.change_currency)
        settings_layout.addWidget(self.currency_combo)
        theme_label = QLabel("Theme:")
        settings_layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        settings_layout.addWidget(self.theme_combo)
        reset_btn = QPushButton("Reset Data")
        reset_btn.clicked.connect(self.reset_data)
        settings_layout.addWidget(reset_btn)
        self.tabs.addTab(settings_tab, "Settings")

        # Shared Finances Tab
        shared_tab = QWidget()
        shared_layout = QVBoxLayout(shared_tab)
        lend_form = QHBoxLayout()
        self.lend_amount = QDoubleSpinBox()
        self.lend_amount.setMaximum(1000000)
        lend_form.addWidget(self.lend_amount)
        self.lend_person = QLineEdit()
        self.lend_person.setPlaceholderText("Person")
        lend_form.addWidget(self.lend_person)
        self.lend_reason = QLineEdit()
        self.lend_reason.setPlaceholderText("Reason")
        lend_form.addWidget(self.lend_reason)
        self.lend_due = QLineEdit()
        self.lend_due.setPlaceholderText("Due Date")
        lend_form.addWidget(self.lend_due)
        add_lend_btn = QPushButton("Add")
        add_lend_btn.clicked.connect(self.add_lending)
        lend_form.addWidget(add_lend_btn)
        shared_layout.addLayout(lend_form)
        self.lending_table = QTableWidget(0, 5)
        self.lending_table.setHorizontalHeaderLabels(
            ["Amount", "Person", "Reason", "Due Date", "Status"]
        )
        shared_layout.addWidget(self.lending_table)
        self.tabs.addTab(shared_tab, "Shared Finances")

        # Insights Tab
        insights_tab = QWidget()
        insights_layout = QVBoxLayout(insights_tab)
        self.insights_label = QLabel("Insights will appear here.")
        insights_layout.addWidget(self.insights_label)
        show_insights_btn = QPushButton("Show Insights")
        show_insights_btn.clicked.connect(self.show_insights)
        insights_layout.addWidget(show_insights_btn)
        self.tabs.addTab(insights_tab, "Insights")

        self.setLayout(main_layout)
        self.refresh_dashboard()
        self.refresh_transactions()
        self.refresh_budget()
        self.refresh_lending()

    # Transactions
    def add_transaction(self):
        t = {
            "date": self.trans_date_widget.selectedDate().toString("yyyy-MM-dd"),
            "type": self.trans_type.currentText(),
            "amount": self.trans_amount.value(),
            "category": self.trans_category.currentText(),
            "notes": self.trans_notes.text()
        }
        tags = extract_tags(self.trans_notes.text())
        t["tags"] = tags
        self.transactions.append(t)
        self.refresh_transactions()
        self.refresh_dashboard()
        self.refresh_budget()
        self.refresh_heatmap()
        self.refresh_achievements()

    def refresh_transactions(self):
        self.transactions_table.setRowCount(len(self.transactions))
        for i, t in enumerate(self.transactions):
            self.transactions_table.setItem(i, 0, QTableWidgetItem(t["date"]))
            self.transactions_table.setItem(i, 1, QTableWidgetItem(t["type"]))
            self.transactions_table.setItem(i, 2, QTableWidgetItem(str(t["amount"])))
            self.transactions_table.setItem(i, 3, QTableWidgetItem(t["category"]))
            self.transactions_table.setItem(i, 4, QTableWidgetItem(t["notes"]))
            # Actions
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, row=i: self.delete_transaction(row))
            self.transactions_table.setCellWidget(i, 5, delete_btn)

    def delete_transaction(self, row):
        del self.transactions[row]
        self.refresh_transactions()
        self.refresh_dashboard()
        self.refresh_budget()

    # Budget
    def set_budget(self):
        cat = self.budget_category.currentText()
        limit = self.budget_limit.value()
        self.budgets[cat] = limit
        self.refresh_budget()

    def refresh_budget(self):
        cat = self.budget_category.currentText()
        limit = self.budgets.get(cat, 0)
        spent = sum(t["amount"] for t in self.transactions if t["category"] == cat and t["type"] == "Expense")
        self.budget_bar.setMaximum(int(limit) if limit else 1)
        self.budget_bar.setValue(int(spent))
        if limit and spent > limit:
            self.budget_alert.setText(f"Alert: Over budget for {cat}!")
        else:
            self.budget_alert.setText(f"Spent {spent}/{limit} on {cat}")

    # Dashboard
    def refresh_dashboard(self):
        income = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
        expense = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
        balance = income - expense
        self.dashboard_summary.setText(
            f"Total Income: {self.currency}{income} | Expenses: {self.currency}{expense} | Balance: {self.currency}{balance}"
        )

    # Reports
    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export CSV", "transactions.csv", "CSV Files (*.csv)")
        if filename:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Type", "Amount", "Category", "Notes"])
                for t in self.transactions:
                    writer.writerow([t["date"], t["type"], t["amount"], t["category"], t["notes"]])
            QMessageBox.information(self, "Export", "CSV exported!")

    # Settings
    def change_currency(self, text):
        self.currency = text
        self.refresh_dashboard()

    def change_theme(self, text):
        self.theme = text
        # Demo: just show a message
        QMessageBox.information(self, "Theme", f"Theme changed to {text}")

    def reset_data(self):
        self.transactions.clear()
        self.budgets.clear()
        self.lendings.clear()
        self.refresh_transactions()
        self.refresh_dashboard()
        self.refresh_budget()
        self.refresh_lending()
        QMessageBox.information(self, "Reset", "All data reset!")

    # Shared Finances
    def add_lending(self):
        l = {
            "amount": self.lend_amount.value(),
            "person": self.lend_person.text(),
            "reason": self.lend_reason.text(),
            "due": self.lend_due.text(),
            "status": "Unpaid"
        }
        self.lendings.append(l)
        self.refresh_lending()

    def refresh_lending(self):
        self.lending_table.setRowCount(len(self.lendings))
        for i, l in enumerate(self.lendings):
            self.lending_table.setItem(i, 0, QTableWidgetItem(str(l["amount"])))
            self.lending_table.setItem(i, 1, QTableWidgetItem(l["person"]))
            self.lending_table.setItem(i, 2, QTableWidgetItem(l["reason"]))
            self.lending_table.setItem(i, 3, QTableWidgetItem(l["due"]))
            self.lending_table.setItem(i, 4, QTableWidgetItem(l["status"]))

    # Insights
    def show_insights(self):
        if not self.transactions:
            self.insights_label.setText("No transactions yet.")
            return
        food_expense = sum(t["amount"] for t in self.transactions if t["category"] == "Food" and t["type"] == "Expense")
        rent_expense = sum(t["amount"] for t in self.transactions if t["category"] == "Rent" and t["type"] == "Expense")
        msg = f"You spent {self.currency}{food_expense} on Food, {self.currency}{rent_expense} on Rent."
        self.insights_label.setText(msg)

    def handle_logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            self.logout_requested.emit()