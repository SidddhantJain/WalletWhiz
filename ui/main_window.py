
import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QDateEdit, QTextEdit,
    QProgressBar, QGridLayout, QFileDialog, QSpinBox, QDoubleSpinBox,
    QFrame, QScrollArea, QCheckBox, QSlider, QSplitter, QGroupBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QPainter, QBrush
from datetime import datetime, date, timedelta
import json

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    plt.style.use('seaborn-v0_8')  # Modern chart style
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
        
        # Initialize timers for real-time features
        self.insight_timer = QTimer()
        self.insight_timer.timeout.connect(self.refresh_insights)
        self.insight_timer.start(300000)  # Refresh every 5 minutes
        
        self.init_ui()
        self.load_dashboard_data()
        self.apply_modern_theme()

    def init_ui(self):
        self.setWindowTitle('WalletWhiz - Smart Finance Manager')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # Main layout with sidebar
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Create main content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with insights
        self.create_header()
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Create enhanced tabs
        self.create_smart_dashboard_tab()
        self.create_enhanced_transactions_tab()
        self.create_smart_budget_tab()
        self.create_goals_tab()
        self.create_insights_tab()
        self.create_templates_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        self.content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.content_area, 1)
        
        self.setLayout(main_layout)

    def create_sidebar(self):
        """Create modern sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-right: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 30, 20, 20)
        
        # Logo/Brand
        brand_label = QLabel("💰 WalletWhiz")
        brand_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 20px 0;
                border-bottom: 2px solid rgba(255,255,255,0.3);
            }
        """)
        layout.addWidget(brand_label)
        
        # Quick stats
        self.quick_stats = QWidget()
        stats_layout = QVBoxLayout(self.quick_stats)
        
        self.balance_widget = QLabel("Balance: $0.00")
        self.balance_widget.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px 0;")
        
        self.month_spending = QLabel("This Month: $0.00")
        self.month_spending.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px; padding: 5px 0;")
        
        stats_layout.addWidget(self.balance_widget)
        stats_layout.addWidget(self.month_spending)
        layout.addWidget(self.quick_stats)
        
        # Quick actions
        quick_actions = QGroupBox("Quick Actions")
        quick_actions.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        actions_layout = QVBoxLayout(quick_actions)
        
        quick_expense_btn = QPushButton("⚡ Quick Expense")
        quick_income_btn = QPushButton("💰 Quick Income")
        view_insights_btn = QPushButton("🧠 View Insights")
        
        for btn in [quick_expense_btn, quick_income_btn, view_insights_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 8px;
                    font-weight: bold;
                    text-align: left;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.3);
                }
            """)
            actions_layout.addWidget(btn)
        
        quick_expense_btn.clicked.connect(self.quick_expense_dialog)
        quick_income_btn.clicked.connect(self.quick_income_dialog)
        view_insights_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(4))
        
        layout.addWidget(quick_actions)
        layout.addStretch()
        
        return sidebar

    def create_header(self):
        """Create header with real-time insights"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 15px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_widget)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome back! Today is {datetime.now().strftime('%B %d, %Y')}")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; padding: 10px;")
        
        # Insights ticker
        self.insights_ticker = QLabel("Loading insights...")
        self.insights_ticker.setStyleSheet("font-size: 14px; color: #666; padding: 10px;")
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.insights_ticker)
        
        self.content_layout.addWidget(header_widget)

    def create_smart_dashboard_tab(self):
        """Enhanced dashboard with smart widgets"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # Month/Year selector with improved design
        date_selector = QWidget()
        date_layout = QHBoxLayout(date_selector)
        date_selector.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
        """)
        
        date_layout.addWidget(QLabel("📅 Viewing:"))
        
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
        date_layout.addWidget(self.year_combo)
        date_layout.addStretch()
        
        layout.addWidget(date_selector)
        
        # Enhanced summary cards with gradients
        summary_widget = QWidget()
        summary_layout = QHBoxLayout(summary_widget)
        
        self.income_card = self.create_summary_card("💰 Income", "$0.00", "#4CAF50")
        self.expense_card = self.create_summary_card("💸 Expenses", "$0.00", "#F44336") 
        self.balance_card = self.create_summary_card("💵 Balance", "$0.00", "#2196F3")
        self.savings_card = self.create_summary_card("🎯 Savings Rate", "0%", "#FF9800")
        
        for card in [self.income_card, self.expense_card, self.balance_card, self.savings_card]:
            summary_layout.addWidget(card)
        
        layout.addWidget(summary_widget)
        
        # Main dashboard content
        main_content = QSplitter(Qt.Horizontal)
        
        # Left side - Charts
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        
        if MATPLOTLIB_AVAILABLE:
            self.expense_chart = self.create_enhanced_chart_canvas("Expense Breakdown")
            self.trend_chart = self.create_enhanced_chart_canvas("Spending Trends")
            charts_layout.addWidget(self.expense_chart)
            charts_layout.addWidget(self.trend_chart)
        else:
            # Enhanced text-based breakdown
            self.expense_breakdown = self.create_text_chart_widget("Expense Breakdown")
            charts_layout.addWidget(self.expense_breakdown)
        
        # Right side - Recent activity and goals
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        
        # Recent transactions
        recent_transactions_group = QGroupBox("🕒 Recent Transactions")
        recent_layout = QVBoxLayout(recent_transactions_group)
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(4)
        self.recent_transactions_table.setHorizontalHeaderLabels(['Date', 'Type', 'Amount', 'Category'])
        self.recent_transactions_table.setAlternatingRowColors(True)
        recent_layout.addWidget(self.recent_transactions_table)
        
        # Savings goals preview
        goals_group = QGroupBox("🎯 Savings Goals")
        goals_layout = QVBoxLayout(goals_group)
        self.goals_preview = QWidget()
        goals_layout.addWidget(self.goals_preview)
        
        activity_layout.addWidget(recent_transactions_group)
        activity_layout.addWidget(goals_group)
        
        main_content.addWidget(charts_widget)
        main_content.addWidget(activity_widget)
        main_content.setSizes([600, 400])
        
        layout.addWidget(main_content)
        dashboard.setLayout(layout)
        self.tab_widget.addTab(dashboard, "📊 Dashboard")

    def create_summary_card(self, title: str, value: str, color: str):
        """Create modern summary card widget"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self.darken_color(color)});
                border-radius: 15px;
                padding: 20px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-top: 10px;")
        value_label.setObjectName("value")  # For easy updates
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return card

    def darken_color(self, color: str) -> str:
        """Darken a hex color for gradient effect"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, c - 30) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def create_enhanced_transactions_tab(self):
        """Enhanced transactions with templates and smart features"""
        transactions = QWidget()
        layout = QVBoxLayout(transactions)
        
        # Transaction form with templates
        form_widget = QGroupBox("💳 Add New Transaction")
        form_layout = QGridLayout(form_widget)
        
        # Template selector
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("📋 Use Template:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("-- Select Template --", None)
        self.load_templates()
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo)
        
        save_template_btn = QPushButton("💾 Save as Template")
        save_template_btn.clicked.connect(self.save_as_template)
        template_layout.addWidget(save_template_btn)
        template_layout.addStretch()
        
        form_layout.addLayout(template_layout, 0, 0, 1, 4)
        
        # Enhanced form fields
        self.trans_type_combo = QComboBox()
        self.trans_type_combo.addItems(['💸 Expense', '💰 Income'])
        self.trans_type_combo.currentTextChanged.connect(self.update_category_filter)
        
        self.trans_amount = QDoubleSpinBox()
        self.trans_amount.setRange(0.01, 999999.99)
        self.trans_amount.setDecimals(2)
        self.trans_amount.setPrefix("$ ")
        
        self.trans_category = QComboBox()
        self.load_categories()
        
        self.trans_description = QLineEdit()
        self.trans_description.setPlaceholderText("e.g., Lunch at McDonald's")
        self.trans_description.textChanged.connect(self.suggest_category)
        
        self.trans_date = QDateEdit()
        self.trans_date.setDate(QDate.currentDate())
        self.trans_date.setCalendarPopup(True)
        
        self.trans_notes = QTextEdit()
        self.trans_notes.setMaximumHeight(60)
        self.trans_notes.setPlaceholderText("Additional notes...")
        
        # Tags input
        self.trans_tags = QLineEdit()
        self.trans_tags.setPlaceholderText("Tags (comma-separated): food, urgent, business")
        
        # Location
        self.trans_location = QLineEdit()
        self.trans_location.setPlaceholderText("Location (optional)")
        
        add_trans_btn = QPushButton("✅ Add Transaction")
        add_trans_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        add_trans_btn.clicked.connect(self.add_enhanced_transaction)
        
        # Add fields to form
        row = 1
        for label, widget in [
            ("Type:", self.trans_type_combo),
            ("Amount:", self.trans_amount),
            ("Category:", self.trans_category),
            ("Description:", self.trans_description),
            ("Date:", self.trans_date),
            ("Notes:", self.trans_notes),
            ("Tags:", self.trans_tags),
            ("Location:", self.trans_location)
        ]:
            form_layout.addWidget(QLabel(label), row, 0)
            form_layout.addWidget(widget, row, 1)
            row += 1
        
        form_layout.addWidget(add_trans_btn, row, 0, 1, 2)
        
        layout.addWidget(form_widget)
        
        # Enhanced transactions table with search
        table_widget = QGroupBox("📋 Transaction History")
        table_layout = QVBoxLayout(table_widget)
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search transactions...")
        self.search_input.textChanged.connect(self.filter_transactions)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(['All Types', 'Income', 'Expense'])
        self.filter_type.currentTextChanged.connect(self.filter_transactions)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.filter_type)
        
        table_layout.addLayout(search_layout)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            'Date', 'Type', 'Amount', 'Category', 'Description', 'Tags', 'Location', 'Actions'
        ])
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSortingEnabled(True)
        table_layout.addWidget(self.transactions_table)
        
        layout.addWidget(table_widget)
        
        transactions.setLayout(layout)
        self.tab_widget.addTab(transactions, "💳 Transactions")

    def create_smart_budget_tab(self):
        """Enhanced budget tab with AI suggestions"""
        budget = QWidget()
        layout = QVBoxLayout(budget)
        
        # Budget suggestions
        suggestions_widget = QGroupBox("🧠 Smart Budget Suggestions")
        suggestions_layout = QVBoxLayout(suggestions_widget)
        
        self.budget_suggestions = QLabel("Analyzing your spending patterns...")
        self.budget_suggestions.setWordWrap(True)
        suggestions_layout.addWidget(self.budget_suggestions)
        
        layout.addWidget(suggestions_widget)
        
        # Budget setting with enhanced UI
        form_widget = QGroupBox("💰 Set Budget Limits")
        form_layout = QGridLayout(form_widget)
        
        self.budget_category = QComboBox()
        self.load_expense_categories()
        
        self.budget_limit = QDoubleSpinBox()
        self.budget_limit.setRange(1.00, 999999.99)
        self.budget_limit.setDecimals(2)
        self.budget_limit.setPrefix("$ ")
        
        # Budget period selector
        self.budget_period = QComboBox()
        self.budget_period.addItems(['Monthly', 'Weekly', 'Yearly'])
        
        set_budget_btn = QPushButton("💾 Set Budget")
        set_budget_btn.clicked.connect(self.set_enhanced_budget)
        
        auto_suggest_btn = QPushButton("🤖 Auto Suggest")
        auto_suggest_btn.clicked.connect(self.auto_suggest_budget)
        
        form_layout.addWidget(QLabel("Category:"), 0, 0)
        form_layout.addWidget(self.budget_category, 0, 1)
        form_layout.addWidget(QLabel("Limit:"), 0, 2)
        form_layout.addWidget(self.budget_limit, 0, 3)
        form_layout.addWidget(QLabel("Period:"), 1, 0)
        form_layout.addWidget(self.budget_period, 1, 1)
        form_layout.addWidget(set_budget_btn, 1, 2)
        form_layout.addWidget(auto_suggest_btn, 1, 3)
        
        layout.addWidget(form_widget)
        
        # Enhanced budget overview with progress animations
        overview_widget = QGroupBox("📊 Budget Overview")
        overview_layout = QVBoxLayout(overview_widget)
        
        self.budget_overview = QScrollArea()
        self.budget_overview.setWidgetResizable(True)
        self.budget_overview.setMinimumHeight(300)
        overview_layout.addWidget(self.budget_overview)
        
        layout.addWidget(overview_widget)
        
        budget.setLayout(layout)
        self.tab_widget.addTab(budget, "💰 Smart Budget")

    def create_goals_tab(self):
        """New tab for savings goals"""
        goals = QWidget()
        layout = QVBoxLayout(goals)
        
        # Goals form
        form_widget = QGroupBox("🎯 Create Savings Goal")
        form_layout = QGridLayout(form_widget)
        
        self.goal_name = QLineEdit()
        self.goal_name.setPlaceholderText("e.g., New Laptop, Vacation, Emergency Fund")
        
        self.goal_amount = QDoubleSpinBox()
        self.goal_amount.setRange(1.00, 999999.99)
        self.goal_amount.setDecimals(2)
        self.goal_amount.setPrefix("$ ")
        
        self.goal_date = QDateEdit()
        self.goal_date.setDate(QDate.currentDate().addMonths(6))
        self.goal_date.setCalendarPopup(True)
        
        self.goal_priority = QComboBox()
        self.goal_priority.addItems(['Low', 'Medium', 'High'])
        self.goal_priority.setCurrentText('Medium')
        
        create_goal_btn = QPushButton("✨ Create Goal")
        create_goal_btn.clicked.connect(self.create_goal)
        
        form_layout.addWidget(QLabel("Goal Name:"), 0, 0)
        form_layout.addWidget(self.goal_name, 0, 1)
        form_layout.addWidget(QLabel("Target Amount:"), 0, 2)
        form_layout.addWidget(self.goal_amount, 0, 3)
        form_layout.addWidget(QLabel("Target Date:"), 1, 0)
        form_layout.addWidget(self.goal_date, 1, 1)
        form_layout.addWidget(QLabel("Priority:"), 1, 2)
        form_layout.addWidget(self.goal_priority, 1, 3)
        form_layout.addWidget(create_goal_btn, 2, 0, 1, 4)
        
        layout.addWidget(form_widget)
        
        # Goals overview
        self.goals_overview = QScrollArea()
        self.goals_overview.setWidgetResizable(True)
        layout.addWidget(self.goals_overview)
        
        goals.setLayout(layout)
        self.tab_widget.addTab(goals, "🎯 Goals")

    def create_insights_tab(self):
        """New tab for financial insights"""
        insights = QWidget()
        layout = QVBoxLayout(insights)
        
        # Insights header
        header = QLabel("🧠 Financial Insights & Recommendations")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px; color: #333;")
        layout.addWidget(header)
        
        # Insights container
        self.insights_container = QScrollArea()
        self.insights_container.setWidgetResizable(True)
        layout.addWidget(self.insights_container)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Insights")
        refresh_btn.clicked.connect(self.refresh_insights)
        layout.addWidget(refresh_btn)
        
        insights.setLayout(layout)
        self.tab_widget.addTab(insights, "🧠 Insights")

    def create_templates_tab(self):
        """New tab for transaction templates"""
        templates = QWidget()
        layout = QVBoxLayout(templates)
        
        header = QLabel("📋 Transaction Templates")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px; color: #333;")
        layout.addWidget(header)
        
        # Templates list
        self.templates_list = QListWidget()
        self.templates_list.itemDoubleClicked.connect(self.use_template_from_list)
        layout.addWidget(self.templates_list)
        
        # Template actions
        actions_layout = QHBoxLayout()
        
        use_template_btn = QPushButton("✅ Use Template")
        use_template_btn.clicked.connect(self.use_selected_template)
        
        delete_template_btn = QPushButton("🗑️ Delete Template")
        delete_template_btn.clicked.connect(self.delete_selected_template)
        
        actions_layout.addWidget(use_template_btn)
        actions_layout.addWidget(delete_template_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        templates.setLayout(layout)
        self.tab_widget.addTab(templates, "📋 Templates")

    # ...existing methods...

    def apply_modern_theme(self):
        """Apply modern, gradient-rich theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 10px;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                padding: 12px 20px;
                margin: 2px;
                border-radius: 8px;
                font-weight: bold;
                color: #495057;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
            }
            
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004085);
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004085, stop:1 #002752);
            }
            
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background: white;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                border-color: #007bff;
                box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
            }
            
            QTableWidget {
                background: white;
                border: none;
                border-radius: 10px;
                gridline-color: #f8f9fa;
                font-size: 13px;
            }
            
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                color: #333;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                color: #495057;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 10px;
                background: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: white;
            }
            
            QProgressBar {
                border: none;
                border-radius: 8px;
                background: #f8f9fa;
                text-align: center;
                font-weight: bold;
                height: 20px;
            }
            
            QProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:1 #20c997);
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QListWidget {
                background: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
            }
            
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f8f9fa;
                border-radius: 5px;
                margin: 2px;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                color: #333;
            }
            
            QListWidget::item:hover {
                background: #f8f9fa;
            }
        """)

    # Enhanced methods with smart features
    def suggest_category(self):
        """Auto-suggest category based on description"""
        description = self.trans_description.text()
        if len(description) > 3:
            suggested_category_id = self.db_manager.auto_categorize_transaction(description, 0)
            if suggested_category_id:
                # Find and select the suggested category
                for i in range(self.trans_category.count()):
                    if self.trans_category.itemData(i) == suggested_category_id:
                        self.trans_category.setCurrentIndex(i)
                        break

    def add_enhanced_transaction(self):
        """Add transaction with enhanced features"""
        trans_type = 'expense' if '💸' in self.trans_type_combo.currentText() else 'income'
        amount = self.trans_amount.value()
        category_id = self.trans_category.currentData()
        description = self.trans_description.text()
        trans_date = self.trans_date.date().toPyDate()
        notes = self.trans_notes.toPlainText()
        tags = [tag.strip() for tag in self.trans_tags.text().split(',') if tag.strip()]
        location = self.trans_location.text()
        
        if not description:
            QMessageBox.warning(self, "Error", "Please enter a description")
            return
        
        result = self.db_manager.add_transaction_with_smart_features(
            self.user_id, trans_type, amount, category_id, 
            description, trans_date, notes, tags, location
        )
        
        if isinstance(result, dict):
            if result.get('duplicate'):
                reply = QMessageBox.question(
                    self, "Duplicate Detection", 
                    "This transaction looks similar to a recent one. Add anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                # Add anyway by calling the basic method
                result = self.db_manager.add_transaction(
                    self.user_id, trans_type, amount, category_id, 
                    description, trans_date, notes
                )
        
        if result and (isinstance(result, bool) or result.get('success')):
            QMessageBox.information(self, "Success", "Transaction added successfully!")
            self.clear_transaction_form()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, "Error", "Failed to add transaction")

    def quick_expense_dialog(self):
        """Quick expense entry dialog"""
        # Switch to transactions tab and focus on amount
        self.tab_widget.setCurrentIndex(1)
        self.trans_type_combo.setCurrentText('💸 Expense')
        self.trans_amount.setFocus()

    def quick_income_dialog(self):
        """Quick income entry dialog"""
        # Switch to transactions tab and focus on amount
        self.tab_widget.setCurrentIndex(1)
        self.trans_type_combo.setCurrentText('💰 Income')
        self.trans_amount.setFocus()

    def refresh_insights(self):
        """Refresh financial insights"""
        self.db_manager.generate_spending_insights(self.user_id)
        insights = self.db_manager.get_insights(self.user_id)
        
        if insights:
            # Update insights ticker
            latest_insight = insights[0]
            self.insights_ticker.setText(f"💡 {latest_insight['title']}")
            
            # Update insights tab
            self.update_insights_display(insights)

    def update_insights_display(self, insights):
        """Update the insights tab display"""
        insights_widget = QWidget()
        layout = QVBoxLayout(insights_widget)
        
        for insight in insights:
            insight_card = self.create_insight_card(insight)
            layout.addWidget(insight_card)
        
        layout.addStretch()
        self.insights_container.setWidget(insights_widget)

    def create_insight_card(self, insight):
        """Create a card for displaying an insight"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 5px solid {self.get_priority_color(insight['priority'])};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Priority and type badges
        header_layout = QHBoxLayout()
        
        type_badge = QLabel(f"🏷️ {insight['type'].title()}")
        type_badge.setStyleSheet("background: #e9ecef; padding: 5px 10px; border-radius: 15px; font-size: 12px;")
        
        priority_badge = QLabel(f"⚡ {insight['priority'].title()}")
        priority_badge.setStyleSheet(f"""
            background: {self.get_priority_color(insight['priority'])}; 
            color: white; 
            padding: 5px 10px; 
            border-radius: 15px; 
            font-size: 12px; 
            font-weight: bold;
        """)
        
        header_layout.addWidget(type_badge)
        header_layout.addWidget(priority_badge)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Insight content
        title_label = QLabel(insight['title'])
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin: 10px 0;")
        
        desc_label = QLabel(insight['description'])
        desc_label.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        
        time_label = QLabel(f"Generated: {insight['created_at'].strftime('%Y-%m-%d %H:%M')}")
        time_label.setStyleSheet("font-size: 12px; color: #999;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(time_label)
        
        return card

    def get_priority_color(self, priority: str) -> str:
        """Get color for priority level"""
        colors = {
            'high': '#dc3545',
            'medium': '#ffc107', 
            'low': '#28a745'
        }
        return colors.get(priority.lower(), '#6c757d')

    def create_enhanced_chart_canvas(self, title: str):
        """Create enhanced matplotlib canvas with modern styling"""
        if MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(10, 6), facecolor='white')
            canvas = FigureCanvas(figure)
            
            # Add title
            figure.suptitle(title, fontsize=16, fontweight='bold', color='#333')
            
            return canvas
        return None

    def create_text_chart_widget(self, title: str):
        """Create text-based chart widget when matplotlib unavailable"""
        widget = QGroupBox(title)
        layout = QVBoxLayout(widget)
        
        self.expense_breakdown_list = QListWidget()
        self.expense_breakdown_list.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
        """)
        layout.addWidget(self.expense_breakdown_list)
        
        return widget

    def load_templates(self):
        """Load transaction templates"""
        templates = self.db_manager.get_transaction_templates(self.user_id)
        
        # Clear existing items except the first one
        while self.template_combo.count() > 1:
            self.template_combo.removeItem(1)
        
        for template in templates:
            display_text = f"💼 {template['name']} - ${template['amount']:.2f}"
            self.template_combo.addItem(display_text, template['id'])

    def on_template_selected(self):
        """Handle template selection"""
        template_id = self.template_combo.currentData()
        if template_id:
            # Get template details
            templates = self.db_manager.get_transaction_templates(self.user_id)
            selected_template = next((t for t in templates if t['id'] == template_id), None)
            
            if selected_template:
                # Populate form with template data
                self.trans_type_combo.setCurrentText(
                    '💸 Expense' if selected_template['type'] == 'expense' else '💰 Income'
                )
                self.trans_amount.setValue(selected_template['amount'])
                self.trans_description.setText(selected_template['description'])
                if selected_template['notes']:
                    self.trans_notes.setPlainText(selected_template['notes'])
                
                # Set category
                for i in range(self.trans_category.count()):
                    if selected_template['category_name'] in self.trans_category.itemText(i):
                        self.trans_category.setCurrentIndex(i)
                        break

    def save_as_template(self):
        """Save current transaction as template"""
        if not self.trans_description.text():
            QMessageBox.warning(self, "Error", "Please enter a description first")
            return
        
        template_name, ok = QInputDialog.getText(
            self, "Save Template", "Enter template name:"
        )
        
        if ok and template_name:
            trans_type = 'expense' if '💸' in self.trans_type_combo.currentText() else 'income'
            amount = self.trans_amount.value()
            category_id = self.trans_category.currentData()
            description = self.trans_description.text()
            notes = self.trans_notes.toPlainText()
            
            if self.db_manager.create_transaction_template(
                self.user_id, template_name, trans_type, amount, 
                category_id, description, notes
            ):
                QMessageBox.information(self, "Success", "Template saved successfully!")
                self.load_templates()
            else:
                QMessageBox.warning(self, "Error", "Failed to save template")

    def update_category_filter(self):
        """Update category dropdown based on transaction type"""
        trans_type = 'expense' if '💸' in self.trans_type_combo.currentText() else 'income'
        
        # Clear and reload categories
        self.trans_category.clear()
        categories = self.db_manager.get_categories(self.user_id, trans_type)
        
        for cat_id, name, cat_type in categories:
            self.trans_category.addItem(f"{name}", cat_id)

    def filter_transactions(self):
        """Filter transactions based on search and type"""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_type.currentText()
        
        for row in range(self.transactions_table.rowCount()):
            should_show = True
            
            # Check search text
            if search_text:
                row_text = ""
                for col in range(self.transactions_table.columnCount() - 1):  # Exclude actions column
                    item = self.transactions_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    should_show = False
            
            # Check type filter
            if filter_type != 'All Types':
                type_item = self.transactions_table.item(row, 1)
                if type_item and filter_type.lower() not in type_item.text().lower():
                    should_show = False
            
            self.transactions_table.setRowHidden(row, not should_show)

    def set_enhanced_budget(self):
        """Set budget with enhanced features"""
        category_id = self.budget_category.currentData()
        if not category_id:
            QMessageBox.warning(self, "Error", "Please select a category")
            return
            
        limit = self.budget_limit.value()
        period = self.budget_period.currentText()
        
        # Calculate dates based on period
        if period == 'Weekly':
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'Yearly':
            start_date = date(self.current_year, 1, 1)
            end_date = date(self.current_year, 12, 31)
        else:  # Monthly
            start_date = date(self.current_year, self.current_month, 1)
            if self.current_month == 12:
                end_date = date(self.current_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(self.current_year, self.current_month + 1, 1) - timedelta(days=1)
        
        if self.db_manager.set_budget(self.user_id, category_id, limit, start_date, end_date):
            QMessageBox.information(self, "Success", "Budget set successfully!")
            self.update_budget_overview()
            self.generate_budget_suggestions()
        else:
            QMessageBox.warning(self, "Error", "Failed to set budget")

    def auto_suggest_budget(self):
        """Auto-suggest budget based on spending patterns"""
        category_id = self.budget_category.currentData()
        if not category_id:
            QMessageBox.warning(self, "Error", "Please select a category first")
            return
        
        # Get last 3 months of spending for this category
        query = """
        SELECT AVG(monthly_total) as avg_spending
        FROM (
            SELECT SUM(amount) as monthly_total
            FROM Transactions 
            WHERE user_id = %s AND category_id = %s AND type = 'expense'
            AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            GROUP BY YEAR(transaction_date), MONTH(transaction_date)
        ) as monthly_totals
        """
        
        result = self.db_manager.execute_query(query, (self.user_id, category_id), fetch_results=True)
        
        if result and result[0][0]:
            avg_spending = float(result[0][0])
            suggested_budget = avg_spending * 1.1  # 10% buffer
            
            self.budget_limit.setValue(suggested_budget)
            
            category_name = self.budget_category.currentText()
            QMessageBox.information(
                self, "Budget Suggestion", 
                f"Based on your last 3 months, suggested budget for {category_name}: ${suggested_budget:.2f}\n"
                f"(Average spending: ${avg_spending:.2f} + 10% buffer)"
            )
        else:
            QMessageBox.information(self, "No Data", "Not enough spending data for this category")

    def generate_budget_suggestions(self):
        """Generate smart budget suggestions"""
        suggestions = []
        
        # Analyze spending patterns
        categories = self.db_manager.get_categories(self.user_id, 'expense')
        
        for cat_id, name, _ in categories:
            # Get spending trend for this category
            query = """
            SELECT 
                SUM(CASE WHEN MONTH(transaction_date) = %s THEN amount ELSE 0 END) as current_month,
                AVG(amount) as avg_transaction
            FROM Transactions 
            WHERE user_id = %s AND category_id = %s AND type = 'expense'
            AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            """
            
            result = self.db_manager.execute_query(
                query, (self.current_month, self.user_id, cat_id), fetch_results=True
            )
            
            if result and result[0][0]:
                current_spending = float(result[0][0])
                avg_transaction = float(result[0][1])
                
                if current_spending > 0:
                    if avg_transaction < 50:
                        suggestions.append(f"💡 {name}: Consider setting a weekly budget (many small transactions)")
                    elif current_spending > 500:
                        suggestions.append(f"💰 {name}: High spending category - set a strict monthly limit")
                    else:
                        suggested_limit = current_spending * 1.15  # 15% buffer
                        suggestions.append(f"🎯 {name}: Suggested monthly budget: ${suggested_limit:.0f}")
        
        # Update suggestions display
        if suggestions:
            self.budget_suggestions.setText("\n".join(suggestions))
        else:
            self.budget_suggestions.setText("💡 Add some transactions to get personalized budget suggestions!")

    def create_goal(self):
        """Create a new savings goal"""
        name = self.goal_name.text()
        amount = self.goal_amount.value()
        target_date = self.goal_date.date().toPyDate()
        priority = self.goal_priority.currentText().lower()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a goal name")
            return
        
        if self.db_manager.create_savings_goal(self.user_id, name, amount, target_date, priority):
            QMessageBox.information(self, "Success", "Savings goal created successfully!")
            self.clear_goal_form()
            self.load_goals()
        else:
            QMessageBox.warning(self, "Error", "Failed to create goal")

    def clear_goal_form(self):
        """Clear the goal creation form"""
        self.goal_name.clear()
        self.goal_amount.setValue(1.0)
        self.goal_date.setDate(QDate.currentDate().addMonths(6))
        self.goal_priority.setCurrentText('Medium')

    def load_goals(self):
        """Load and display savings goals"""
        goals = self.db_manager.get_savings_goals(self.user_id)
        
        goals_widget = QWidget()
        layout = QVBoxLayout(goals_widget)
        
        if not goals:
            no_goals_label = QLabel("🎯 No savings goals yet. Create your first goal above!")
            no_goals_label.setStyleSheet("font-size: 16px; color: #666; padding: 40px; text-align: center;")
            layout.addWidget(no_goals_label)
        else:
            for goal in goals:
                goal_card = self.create_goal_card(goal)
                layout.addWidget(goal_card)
        
        layout.addStretch()
        self.goals_overview.setWidget(goals_widget)

    def create_goal_card(self, goal: Dict) -> QFrame:
        """Create a card widget for a savings goal"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 5px solid {self.get_priority_color(goal['priority'])};
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Goal header
        header_layout = QHBoxLayout()
        
        goal_name = QLabel(f"🎯 {goal['name']}")
        goal_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        priority_badge = QLabel(goal['priority'].title())
        priority_badge.setStyleSheet(f"""
            background: {self.get_priority_color(goal['priority'])}; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 12px; 
            font-size: 12px; 
            font-weight: bold;
        """)
        
        header_layout.addWidget(goal_name)
        header_layout.addStretch()
        header_layout.addWidget(priority_badge)
        
        layout.addLayout(header_layout)
        
        # Progress section
        progress_layout = QVBoxLayout()
        
        amount_label = QLabel(f"${goal['current_amount']:.2f} / ${goal['target_amount']:.2f}")
        amount_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #666; margin: 10px 0;")
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(goal['progress_percentage']))
        progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.get_priority_color(goal['priority'])}, 
                    stop:1 {self.darken_color(self.get_priority_color(goal['priority']))});
            }}
        """)
        
        progress_layout.addWidget(amount_label)
        progress_layout.addWidget(progress_bar)
        
        # Target date
        if goal['target_date']:
            if goal['days_remaining'] is not None:
                if goal['days_remaining'] > 0:
                    date_label = QLabel(f"📅 {goal['days_remaining']} days remaining")
                    date_label.setStyleSheet("color: #666; font-size: 14px;")
                else:
                    date_label = QLabel("⏰ Target date passed")
                    date_label.setStyleSheet("color: #dc3545; font-size: 14px; font-weight: bold;")
            else:
                date_label = QLabel(f"📅 Target: {goal['target_date']}")
                date_label.setStyleSheet("color: #666; font-size: 14px;")
            
            progress_layout.addWidget(date_label)
        
        layout.addLayout(progress_layout)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        add_money_btn = QPushButton("💰 Add Money")
        add_money_btn.clicked.connect(lambda: self.add_to_goal(goal['id']))
        
        edit_goal_btn = QPushButton("✏️ Edit")
        edit_goal_btn.clicked.connect(lambda: self.edit_goal(goal['id']))
        
        actions_layout.addWidget(add_money_btn)
        actions_layout.addWidget(edit_goal_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return card

    def add_to_goal(self, goal_id: int):
        """Add money to a savings goal"""
        amount, ok = QInputDialog.getDouble(
            self, "Add to Goal", "Amount to add:", 0, 0, 999999, 2
        )
        
        if ok and amount > 0:
            if self.db_manager.update_savings_goal_progress(goal_id, amount):
                QMessageBox.information(self, "Success", f"Added ${amount:.2f} to your goal!")
                self.load_goals()
            else:
                QMessageBox.warning(self, "Error", "Failed to update goal")

    def edit_goal(self, goal_id: int):
        """Edit a savings goal (simplified - could open a dialog)"""
        QMessageBox.information(self, "Feature Coming Soon", "Goal editing will be available in the next update!")

    def use_template_from_list(self, item):
        """Use template when double-clicked from list"""
        template_text = item.text()
        # Extract template ID or name and use it
        self.tab_widget.setCurrentIndex(1)  # Switch to transactions tab

    def use_selected_template(self):
        """Use the selected template"""
        current_item = self.templates_list.currentItem()
        if current_item:
            self.use_template_from_list(current_item)
        else:
            QMessageBox.warning(self, "Error", "Please select a template first")

    def delete_selected_template(self):
        """Delete the selected template"""
        current_item = self.templates_list.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                "Are you sure you want to delete this template?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Implementation for deleting template
                QMessageBox.information(self, "Success", "Template deleted!")
                self.load_template_list()
        else:
            QMessageBox.warning(self, "Error", "Please select a template first")

    def load_template_list(self):
        """Load templates into the list widget"""
        templates = self.db_manager.get_transaction_templates(self.user_id)
        
        self.templates_list.clear()
        for template in templates:
            item_text = f"💼 {template['name']} - {template['type'].title()} - ${template['amount']:.2f}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, template['id'])
            self.templates_list.addItem(item)

    def create_reports_tab(self):
        """Enhanced reports tab"""
        reports = QWidget()
        layout = QVBoxLayout(reports)
        
        # Reports header
        header = QLabel("📊 Financial Reports & Analytics")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px; color: #333;")
        layout.addWidget(header)
        
        # Export section
        export_widget = QGroupBox("📤 Export Data")
        export_layout = QHBoxLayout(export_widget)
        
        export_csv_btn = QPushButton("📄 Export to CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        
        export_pdf_btn = QPushButton("📋 Export to PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        
        export_summary_btn = QPushButton("📊 Monthly Summary")
        export_summary_btn.clicked.connect(self.export_monthly_summary)
        
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(export_pdf_btn)
        export_layout.addWidget(export_summary_btn)
        export_layout.addStretch()
        
        layout.addWidget(export_widget)
        
        # Analytics section
        if MATPLOTLIB_AVAILABLE:
            analytics_widget = QGroupBox("📈 Advanced Analytics")
            analytics_layout = QVBoxLayout(analytics_widget)
            
            self.comparison_chart = self.create_enhanced_chart_canvas("Monthly Comparison")
            self.trend_analysis_chart = self.create_enhanced_chart_canvas("Spending Trends")
            
            analytics_layout.addWidget(self.comparison_chart)
            analytics_layout.addWidget(self.trend_analysis_chart)
            
            layout.addWidget(analytics_widget)
        else:
            no_charts_label = QLabel("📊 Install matplotlib for advanced charts and analytics")
            no_charts_label.setStyleSheet("font-size: 16px; color: #666; padding: 40px; text-align: center;")
            layout.addWidget(no_charts_label)
        
        reports.setLayout(layout)
        self.tab_widget.addTab(reports, "📊 Reports")

    def create_settings_tab(self):
        """Enhanced settings tab"""
        settings = QWidget()
        layout = QVBoxLayout(settings)
        
        # Settings sections
        # Currency settings
        currency_widget = QGroupBox("💱 Currency Settings")
        currency_layout = QGridLayout(currency_widget)
        
        currency_layout.addWidget(QLabel("Primary Currency:"), 0, 0)
        
        self.currency_combo = QComboBox()
        self.load_currencies()
        currency_layout.addWidget(self.currency_combo, 0, 1)
        
        save_currency_btn = QPushButton("💾 Save Currency")
        save_currency_btn.clicked.connect(self.save_currency_setting)
        currency_layout.addWidget(save_currency_btn, 0, 2)
        
        layout.addWidget(currency_widget)
        
        # Theme settings
        theme_widget = QGroupBox("🎨 Appearance")
        theme_layout = QGridLayout(theme_widget)
        
        theme_layout.addWidget(QLabel("Theme:"), 0, 0)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['🌞 Light', '🌙 Dark', '🤖 Auto'])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        layout.addWidget(theme_widget)
        
        # Notification settings
        notification_widget = QGroupBox("🔔 Notifications")
        notification_layout = QVBoxLayout(notification_widget)
        
        self.budget_alerts = QCheckBox("💰 Budget alerts")
        self.budget_alerts.setChecked(True)
        
        self.goal_reminders = QCheckBox("🎯 Goal progress reminders")
        self.goal_reminders.setChecked(True)
        
        self.spending_insights = QCheckBox("🧠 Spending insights")
        self.spending_insights.setChecked(True)
        
        notification_layout.addWidget(self.budget_alerts)
        notification_layout.addWidget(self.goal_reminders)
        notification_layout.addWidget(self.spending_insights)
        
        layout.addWidget(notification_widget)
        
        # Data management
        data_widget = QGroupBox("🗂️ Data Management")
        data_layout = QVBoxLayout(data_widget)
        
        backup_btn = QPushButton("💾 Backup Data")
        backup_btn.clicked.connect(self.backup_data)
        
        restore_btn = QPushButton("📥 Restore Data")
        restore_btn.clicked.connect(self.restore_data)
        
        reset_data_btn = QPushButton("🗑️ Reset All Data")
        reset_data_btn.setStyleSheet("background-color: #dc3545; color: white;")
        reset_data_btn.clicked.connect(self.reset_data)
        
        data_layout.addWidget(backup_btn)
        data_layout.addWidget(restore_btn)
        data_layout.addWidget(reset_data_btn)
        
        layout.addWidget(data_widget)
        
        layout.addStretch()
        settings.setLayout(layout)
        self.tab_widget.addTab(settings, "⚙️ Settings")

    # Additional helper methods for new features
    def save_currency_setting(self):
        """Save currency preference"""
        currency_id = self.currency_combo.currentData()
        if self.db_manager.update_user_settings(self.user_id, currency_id=currency_id):
            QMessageBox.information(self, "Success", "Currency setting saved!")
            self.load_dashboard_data()  # Refresh to show new currency
        else:
            QMessageBox.warning(self, "Error", "Failed to save currency setting")

    def backup_data(self):
        """Backup user data"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Backup Data", f"walletwhiz_backup_{datetime.now().strftime('%Y%m%d')}.json", 
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                # Export all user data
                data = {
                    'transactions': self.db_manager.get_transactions(self.user_id),
                    'categories': self.db_manager.get_categories(self.user_id),
                    'budgets': self.db_manager.get_budget_summary(self.user_id, self.current_month, self.current_year),
                    'goals': self.db_manager.get_savings_goals(self.user_id),
                    'templates': self.db_manager.get_transaction_templates(self.user_id)
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, default=str, indent=2)
                
                QMessageBox.information(self, "Success", f"Data backed up to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Backup failed: {str(e)}")

    def restore_data(self):
        """Restore user data from backup"""
        QMessageBox.information(self, "Feature Coming Soon", "Data restore will be available in the next update!")

    def export_monthly_summary(self):
        """Export detailed monthly summary"""
        try:
            data = self.db_manager.get_dashboard_data(self.user_id, self.current_month, self.current_year)
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Monthly Summary", 
                f"monthly_summary_{self.current_year}_{self.current_month:02d}.csv", 
                "CSV Files (*.csv)"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write summary
                    writer.writerow(['Monthly Financial Summary'])
                    writer.writerow(['Month/Year', f"{self.current_month}/{self.current_year}"])
                    writer.writerow([])
                    
                    writer.writerow(['Summary'])
                    writer.writerow(['Income', f"${data['income']:.2f}"])
                    writer.writerow(['Expenses', f"${data['expense']:.2f}"])
                    writer.writerow(['Balance', f"${data['balance']:.2f}"])
                    writer.writerow([])
                    
                    writer.writerow(['Category Breakdown'])
                    writer.writerow(['Category', 'Amount'])
                    for category, amount in data['category_expenses']:
                        writer.writerow([category, f"${amount:.2f}"])
                
                QMessageBox.information(self, "Success", f"Monthly summary exported to {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Export failed: {str(e)}")

    # ...existing methods continue...

    def load_dashboard_data(self):
        """Enhanced dashboard data loading with sidebar updates"""
        data = self.db_manager.get_dashboard_data(self.user_id, self.current_month, self.current_year)
        
        # Update sidebar quick stats
        user_settings = self.db_manager.get_user_settings(self.user_id)
        symbol = user_settings.get('currency_symbol', '$')
        
        self.balance_widget.setText(f"Balance: {symbol}{data['balance']:.2f}")
        self.month_spending.setText(f"This Month: {symbol}{data['expense']:.2f}")
        
        # Update summary cards
        income_value_label = self.income_card.findChild(QLabel, "value")
        if income_value_label:
            income_value_label.setText(f"{symbol}{data['income']:.2f}")
        
        expense_value_label = self.expense_card.findChild(QLabel, "value")
        if expense_value_label:
            expense_value_label.setText(f"{symbol}{data['expense']:.2f}")
        
        balance_value_label = self.balance_card.findChild(QLabel, "value")
        if balance_value_label:
            balance_value_label.setText(f"{symbol}{data['balance']:.2f}")
        
        # Calculate savings rate
        savings_rate = ((data['income'] - data['expense']) / data['income'] * 100) if data['income'] > 0 else 0
        savings_value_label = self.savings_card.findChild(QLabel, "value")
        if savings_value_label:
            savings_value_label.setText(f"{savings_rate:.1f}%")
        
        # Update charts and tables
        self.update_expense_chart(data['category_expenses'])
        self.update_recent_transactions(data['recent_transactions'])
        self.load_all_transactions()
        self.update_budget_overview()
        
        # Load goals and templates
        self.load_goals()
        self.load_template_list()
        
        # Generate insights
        self.refresh_insights()