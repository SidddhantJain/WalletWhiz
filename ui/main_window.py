#-- filepath: d:\Siddhant\projects\WalletWhiz\WalletWhiz\ui\main_window.py
import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QDateEdit, QTextEdit,
    QProgressBar, QGridLayout, QFileDialog, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime, date

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. Charts will be disabled.")

from database.db_manager import DBManager

class WalletWhizMainWindow(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db_manager = DBManager()
        self.db_manager.current_user_id = user_id
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        self.setWindowTitle('WalletWhiz - Personal Finance Manager')
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header = QLabel('WalletWhiz Dashboard')
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont('Arial', 24, QFont.Bold))
        main_layout.addWidget(header)

        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_transactions_tab()
        self.create_budget_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
        
        # Apply styling
        self.apply_theme('light')

    def create_dashboard_tab(self):
        dashboard = QWidget()
        layout = QVBoxLayout()
        
        # Month/Year selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Month:"))
        
        self.month_combo = QComboBox()
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.currentIndexChanged.connect(self.on_date_changed)
        
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        self.year_combo.addItems([str(year) for year in range(current_year - 5, current_year + 2)])
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.on_date_changed)
        
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(QLabel("Year:"))
        date_layout.addWidget(self.year_combo)
        date_layout.addStretch()
        
        layout.addLayout(date_layout)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        self.income_label = QLabel("Income: $0.00")
        self.expense_label = QLabel("Expenses: $0.00")
        self.balance_label = QLabel("Balance: $0.00")
        
        for label in [self.income_label, self.expense_label, self.balance_label]:
            label.setStyleSheet("padding: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; font-weight: bold;")
            summary_layout.addWidget(label)
        
        layout.addLayout(summary_layout)
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Expense pie chart (only if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            self.expense_chart = self.create_chart_canvas()
            charts_layout.addWidget(self.expense_chart)
        else:
            # Create a simple text widget showing expense breakdown
            self.expense_breakdown = QWidget()
            breakdown_layout = QVBoxLayout()
            breakdown_layout.addWidget(QLabel("Expense Breakdown"))
            self.expense_breakdown_list = QListWidget()
            breakdown_layout.addWidget(self.expense_breakdown_list)
            self.expense_breakdown.setLayout(breakdown_layout)
            charts_layout.addWidget(self.expense_breakdown)
        
        # Recent transactions
        transactions_widget = QWidget()
        transactions_layout = QVBoxLayout()
        transactions_layout.addWidget(QLabel("Recent Transactions"))
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(4)
        self.recent_transactions_table.setHorizontalHeaderLabels(['Date', 'Type', 'Amount', 'Category'])
        transactions_layout.addWidget(self.recent_transactions_table)
        
        transactions_widget.setLayout(transactions_layout)
        charts_layout.addWidget(transactions_widget)
        
        layout.addLayout(charts_layout)
        dashboard.setLayout(layout)
        self.tab_widget.addTab(dashboard, "Dashboard")

    def create_transactions_tab(self):
        transactions = QWidget()
        layout = QVBoxLayout()
        
        # Add transaction form
        form_layout = QGridLayout()
        
        self.trans_type_combo = QComboBox()
        self.trans_type_combo.addItems(['expense', 'income'])
        
        self.trans_amount = QDoubleSpinBox()
        self.trans_amount.setRange(0.01, 999999.99)
        self.trans_amount.setDecimals(2)
        
        self.trans_category = QComboBox()
        self.load_categories()
        
        self.trans_description = QLineEdit()
        self.trans_date = QDateEdit()
        self.trans_date.setDate(QDate.currentDate())
        self.trans_notes = QTextEdit()
        self.trans_notes.setMaximumHeight(60)
        
        add_trans_btn = QPushButton("Add Transaction")
        add_trans_btn.clicked.connect(self.add_transaction)
        
        form_layout.addWidget(QLabel("Type:"), 0, 0)
        form_layout.addWidget(self.trans_type_combo, 0, 1)
        form_layout.addWidget(QLabel("Amount:"), 0, 2)
        form_layout.addWidget(self.trans_amount, 0, 3)
        form_layout.addWidget(QLabel("Category:"), 1, 0)
        form_layout.addWidget(self.trans_category, 1, 1)
        form_layout.addWidget(QLabel("Description:"), 1, 2)
        form_layout.addWidget(self.trans_description, 1, 3)
        form_layout.addWidget(QLabel("Date:"), 2, 0)
        form_layout.addWidget(self.trans_date, 2, 1)
        form_layout.addWidget(QLabel("Notes:"), 2, 2)
        form_layout.addWidget(self.trans_notes, 2, 3)
        form_layout.addWidget(add_trans_btn, 3, 0, 1, 4)
        
        layout.addLayout(form_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(['Date', 'Type', 'Amount', 'Category', 'Description', 'Notes'])
        layout.addWidget(self.transactions_table)
        
        transactions.setLayout(layout)
        self.tab_widget.addTab(transactions, "Transactions")

    def create_budget_tab(self):
        budget = QWidget()
        layout = QVBoxLayout()
        
        # Budget setting form
        form_layout = QGridLayout()
        
        self.budget_category = QComboBox()
        self.load_expense_categories()
        
        self.budget_limit = QDoubleSpinBox()
        self.budget_limit.setRange(1.00, 999999.99)
        self.budget_limit.setDecimals(2)
        
        set_budget_btn = QPushButton("Set Budget")
        set_budget_btn.clicked.connect(self.set_budget)
        
        form_layout.addWidget(QLabel("Category:"), 0, 0)
        form_layout.addWidget(self.budget_category, 0, 1)
        form_layout.addWidget(QLabel("Monthly Limit:"), 0, 2)
        form_layout.addWidget(self.budget_limit, 0, 3)
        form_layout.addWidget(set_budget_btn, 0, 4)
        
        layout.addLayout(form_layout)
        
        # Budget overview
        self.budget_overview = QWidget()
        layout.addWidget(self.budget_overview)
        
        budget.setLayout(layout)
        self.tab_widget.addTab(budget, "Budget")

    def create_reports_tab(self):
        reports = QWidget()
        layout = QVBoxLayout()
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        
        export_pdf_btn = QPushButton("Export to PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(export_pdf_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
        
        # Monthly comparison chart (only if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            self.comparison_chart = self.create_chart_canvas()
            layout.addWidget(self.comparison_chart)
        else:
            layout.addWidget(QLabel("Charts require matplotlib installation"))
        
        reports.setLayout(layout)
        self.tab_widget.addTab(reports, "Reports")

    def create_settings_tab(self):
        settings = QWidget()
        layout = QVBoxLayout()
        
        # Currency settings
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("Currency:"))
        
        self.currency_combo = QComboBox()
        self.load_currencies()
        
        currency_layout.addWidget(self.currency_combo)
        currency_layout.addStretch()
        
        layout.addLayout(currency_layout)
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['light', 'dark'])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        # Data management
        data_layout = QVBoxLayout()
        
        reset_data_btn = QPushButton("Reset All Data")
        reset_data_btn.setStyleSheet("background-color: #dc3545; color: white;")
        reset_data_btn.clicked.connect(self.reset_data)
        
        data_layout.addWidget(reset_data_btn)
        layout.addLayout(data_layout)
        
        layout.addStretch()
        settings.setLayout(layout)
        self.tab_widget.addTab(settings, "Settings")

    def create_chart_canvas(self):
        """Create a matplotlib canvas for charts"""
        if MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(8, 6))
            canvas = FigureCanvas(figure)
            return canvas
        return None

    def load_categories(self):
        """Load all categories for transaction form"""
        categories = self.db_manager.get_categories(self.user_id)
        self.trans_category.clear()
        for cat_id, name, cat_type in categories:
            self.trans_category.addItem(f"{name} ({cat_type})", cat_id)

    def load_expense_categories(self):
        """Load expense categories for budget form"""
        categories = self.db_manager.get_categories(self.user_id, 'expense')
        self.budget_category.clear()
        for cat_id, name, cat_type in categories:
            self.budget_category.addItem(name, cat_id)

    def load_currencies(self):
        """Load currencies for settings"""
        currencies = self.db_manager.execute_query("SELECT id, name, code FROM Currencies", fetch_results=True)
        self.currency_combo.clear()
        for curr_id, name, code in currencies or []:
            self.currency_combo.addItem(f"{name} ({code})", curr_id)

    def on_date_changed(self):
        """Handle month/year change"""
        self.current_month = self.month_combo.currentIndex() + 1
        self.current_year = int(self.year_combo.currentText())
        self.load_dashboard_data()

    def load_dashboard_data(self):
        """Load and display dashboard data"""
        data = self.db_manager.get_dashboard_data(self.user_id, self.current_month, self.current_year)
        
        # Update summary labels
        user_settings = self.db_manager.get_user_settings(self.user_id)
        symbol = user_settings.get('currency_symbol', '$')
        
        self.income_label.setText(f"Income: {symbol}{data['income']:.2f}")
        self.expense_label.setText(f"Expenses: {symbol}{data['expense']:.2f}")
        self.balance_label.setText(f"Balance: {symbol}{data['balance']:.2f}")
        
        # Update expense pie chart
        self.update_expense_chart(data['category_expenses'])
        
        # Update recent transactions
        self.update_recent_transactions(data['recent_transactions'])
        
        # Load all transactions for transactions tab
        self.load_all_transactions()
        
        # Update budget overview
        self.update_budget_overview()

    def update_expense_chart(self, category_expenses):
        """Update expense pie chart"""
        if not category_expenses:
            return
            
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'expense_chart'):
            figure = self.expense_chart.figure
            figure.clear()
            
            ax = figure.add_subplot(111)
            
            categories = [cat[0] for cat in category_expenses[:6]]  # Top 6 categories
            amounts = [cat[1] for cat in category_expenses[:6]]
            
            if amounts:
                ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.set_title('Expense Breakdown')
            
            self.expense_chart.draw()
        else:
            # Update text-based breakdown
            if hasattr(self, 'expense_breakdown_list'):
                self.expense_breakdown_list.clear()
                for cat, amount in category_expenses[:6]:
                    self.expense_breakdown_list.addItem(f"{cat}: ${amount:.2f}")

    def update_recent_transactions(self, transactions):
        """Update recent transactions table"""
        self.recent_transactions_table.setRowCount(len(transactions))
        
        for i, trans in enumerate(transactions):
            self.recent_transactions_table.setItem(i, 0, QTableWidgetItem(str(trans[5])))  # date
            self.recent_transactions_table.setItem(i, 1, QTableWidgetItem(trans[1].title()))  # type
            self.recent_transactions_table.setItem(i, 2, QTableWidgetItem(f"${trans[2]:.2f}"))  # amount
            self.recent_transactions_table.setItem(i, 3, QTableWidgetItem(trans[3]))  # category

    def load_all_transactions(self):
        """Load all transactions for current month"""
        transactions = self.db_manager.get_transactions(self.user_id, self.current_month, self.current_year)
        
        self.transactions_table.setRowCount(len(transactions))
        
        for i, trans in enumerate(transactions):
            self.transactions_table.setItem(i, 0, QTableWidgetItem(str(trans[5])))  # date
            self.transactions_table.setItem(i, 1, QTableWidgetItem(trans[1].title()))  # type
            self.transactions_table.setItem(i, 2, QTableWidgetItem(f"${trans[2]:.2f}"))  # amount
            self.transactions_table.setItem(i, 3, QTableWidgetItem(trans[3]))  # category
            self.transactions_table.setItem(i, 4, QTableWidgetItem(trans[4] or ''))  # description
            self.transactions_table.setItem(i, 5, QTableWidgetItem(trans[6] or ''))  # notes

    def add_transaction(self):
        """Add a new transaction"""
        trans_type = self.trans_type_combo.currentText()
        amount = self.trans_amount.value()
        category_id = self.trans_category.currentData()
        description = self.trans_description.text()
        trans_date = self.trans_date.date().toPyDate()
        notes = self.trans_notes.toPlainText()
        
        if self.db_manager.add_transaction(self.user_id, trans_type, amount, category_id, 
                                         description, trans_date, notes):
            QMessageBox.information(self, "Success", "Transaction added successfully!")
            self.clear_transaction_form()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, "Error", "Failed to add transaction")

    def clear_transaction_form(self):
        """Clear transaction form"""
        self.trans_amount.setValue(0.01)
        self.trans_description.clear()
        self.trans_notes.clear()
        self.trans_date.setDate(QDate.currentDate())

    def set_budget(self):
        """Set budget for selected category"""
        category_id = self.budget_category.currentData()
        limit = self.budget_limit.value()
        
        start_date = date(self.current_year, self.current_month, 1)
        if self.current_month == 12:
            end_date = date(self.current_year + 1, 1, 1)
        else:
            end_date = date(self.current_year, self.current_month + 1, 1)
        
        if self.db_manager.set_budget(self.user_id, category_id, limit, start_date, end_date):
            QMessageBox.information(self, "Success", "Budget set successfully!")
            self.update_budget_overview()
        else:
            QMessageBox.warning(self, "Error", "Failed to set budget")

    def update_budget_overview(self):
        """Update budget overview with progress bars"""
        budgets = self.db_manager.get_budget_summary(self.user_id, self.current_month, self.current_year)
        
        # Clear existing budget overview
        for i in reversed(range(self.budget_overview.layout().count() if self.budget_overview.layout() else 0)):
            self.budget_overview.layout().itemAt(i).widget().setParent(None)
        
        if not budgets:
            layout = QVBoxLayout()
            layout.addWidget(QLabel("No budgets set for this month"))
            self.budget_overview.setLayout(layout)
            return
        
        layout = QVBoxLayout()
        
        for budget in budgets:
            budget_widget = QWidget()
            budget_layout = QVBoxLayout()
            
            # Category name and amounts
            header = QLabel(f"{budget['category']}: ${budget['spent']:.2f} / ${budget['limit']:.2f}")
            header.setFont(QFont('Arial', 12, QFont.Bold))
            
            # Progress bar
            progress = QProgressBar()
            progress.setMaximum(100)
            progress.setValue(min(int(budget['percentage']), 100))
            
            # Color coding
            if budget['percentage'] > 100:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #dc3545; }")
            elif budget['percentage'] > 80:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #ffc107; }")
            else:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #28a745; }")
            
            budget_layout.addWidget(header)
            budget_layout.addWidget(progress)
            budget_widget.setLayout(budget_layout)
            layout.addWidget(budget_widget)
        
        self.budget_overview.setLayout(layout)

    def export_csv(self):
        """Export transactions to CSV"""
        transactions = self.db_manager.get_transactions(self.user_id)
        
        if not transactions:
            QMessageBox.information(self, "Info", "No transactions to export")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Export CSV", "transactions.csv", "CSV Files (*.csv)")
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(['ID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'Notes', 'Attachment'])
                    
                    # Write data
                    for transaction in transactions:
                        writer.writerow(transaction)
                    
                QMessageBox.information(self, "Success", f"Transactions exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export CSV: {str(e)}")

    def export_pdf(self):
        """Export basic transaction report to PDF"""
        # This is a simplified PDF export - you can enhance it with ReportLab
        QMessageBox.information(self, "Info", "PDF export feature coming soon!")

    def change_theme(self, theme):
        """Change application theme"""
        self.db_manager.update_user_settings(self.user_id, theme=theme)
        self.apply_theme(theme)

    def apply_theme(self, theme):
        """Apply theme styling"""
        if theme == 'dark':
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QTabWidget::pane { border: 1px solid #555; }
                QTabBar::tab { background-color: #404040; padding: 8px; margin: 2px; }
                QTabBar::tab:selected { background-color: #0078d4; }
                QPushButton { background-color: #0078d4; color: white; padding: 8px; border: none; border-radius: 4px; }
                QPushButton:hover { background-color: #106ebe; }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background-color: #404040; border: 1px solid #555; padding: 5px; }
                QTableWidget { background-color: #404040; alternate-background-color: #4a4a4a; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background-color: #ffffff; color: #000000; }
                QPushButton { background-color: #007bff; color: white; padding: 8px; border: none; border-radius: 4px; }
                QPushButton:hover { background-color: #0056b3; }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { border: 1px solid #ddd; padding: 5px; }
            """)

    def reset_data(self):
        """Reset all user data with confirmation"""
        reply = QMessageBox.question(self, "Confirm Reset", 
                                   "Are you sure you want to delete ALL your data? This cannot be undone!",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Delete user's transactions, budgets, and categories
            queries = [
                "DELETE FROM Transactions WHERE user_id = %s",
                "DELETE FROM Budgets WHERE user_id = %s", 
                "DELETE FROM Categories WHERE user_id = %s"
            ]
            
            for query in queries:
                self.db_manager.execute_query(query, (self.user_id,))
            
            # Recreate default categories
            self.db_manager._create_default_categories(self.user_id)
            
            QMessageBox.information(self, "Success", "All data has been reset!")
            self.load_dashboard_data()
            self.load_categories()
            self.load_expense_categories()

    def closeEvent(self, event):
        """Handle window close event"""
        self.db_manager.disconnect()
        event.accept()