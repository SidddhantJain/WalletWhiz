
import mysql.connector
from mysql.connector import Error
import hashlib
import bcrypt
import json
import re
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional, Dict, Any
from collections import defaultdict

class DBManager:
    def __init__(self):
        self.connection = None
        self.current_user_id = None
        # ML-like patterns for auto-categorization
        self.category_patterns = {
            'Food & Dining': ['swiggy', 'zomato', 'mcdonalds', 'kfc', 'dominos', 'pizza', 'restaurant', 'cafe', 'food', 'lunch', 'dinner'],
            'Transportation': ['uber', 'ola', 'metro', 'bus', 'taxi', 'fuel', 'petrol', 'diesel', 'parking'],
            'Shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'mall', 'store', 'shopping'],
            'Entertainment': ['netflix', 'spotify', 'prime', 'movie', 'cinema', 'game'],
            'Bills & Utilities': ['electricity', 'water', 'gas', 'internet', 'mobile', 'phone', 'broadband'],
            'Healthcare': ['hospital', 'doctor', 'pharmacy', 'medicine', 'clinic']
        }

    # ...existing methods...

    def auto_categorize_transaction(self, description: str, amount: float) -> Optional[int]:
        """Use ML-like pattern matching to suggest category"""
        description_lower = description.lower()
        
        for category_name, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in description_lower:
                    # Get category ID
                    category_result = self.execute_query(
                        "SELECT id FROM Categories WHERE user_id = %s AND name = %s",
                        (self.current_user_id, category_name),
                        fetch_results=True
                    )
                    if category_result:
                        return category_result[0][0]
        return None

    def add_transaction_with_smart_features(self, user_id: int, transaction_type: str, amount: float,
                                          category_id: int, description: str, transaction_date: date,
                                          notes: str = None, tags: List[str] = None, location: str = None) -> bool:
        """Enhanced transaction adding with smart features"""
        
        # Check for potential duplicates
        duplicate_check = self.check_duplicate_transaction(user_id, amount, description, transaction_date)
        if duplicate_check:
            return {'success': False, 'duplicate': True, 'message': 'Potential duplicate detected'}
        
        # Auto-suggest category if not provided
        if not category_id:
            suggested_category = self.auto_categorize_transaction(description, amount)
            if suggested_category:
                category_id = suggested_category
        
        # Convert tags to JSON
        tags_json = json.dumps(tags) if tags else None
        
        query = """
        INSERT INTO Transactions (user_id, type, amount, category_id, description, 
                                transaction_date, notes, tags, location) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (user_id, transaction_type, amount, category_id, description, 
                 transaction_date, notes, tags_json, location)
        
        result = self.execute_query(query, params, fetch_id=True)
        
        if result:
            # Generate insights after adding transaction
            self.generate_spending_insights(user_id)
            return {'success': True, 'transaction_id': result}
        
        return {'success': False, 'message': 'Failed to add transaction'}

    def check_duplicate_transaction(self, user_id: int, amount: float, description: str, 
                                  transaction_date: date, threshold_hours: int = 2) -> bool:
        """Check for potential duplicate transactions"""
        start_time = transaction_date - timedelta(hours=threshold_hours)
        end_time = transaction_date + timedelta(hours=threshold_hours)
        
        query = """
        SELECT COUNT(*) FROM Transactions 
        WHERE user_id = %s AND ABS(amount - %s) < 0.01 
        AND transaction_date BETWEEN %s AND %s
        AND LOWER(description) LIKE %s
        """
        
        description_pattern = f"%{description.lower()[:20]}%"
        result = self.execute_query(query, (user_id, amount, start_time, end_time, description_pattern), fetch_results=True)
        
        return result and result[0][0] > 0

    def generate_spending_insights(self, user_id: int):
        """Generate AI-like spending insights"""
        insights = []
        
        # Anomaly detection
        anomalies = self.detect_spending_anomalies(user_id)
        insights.extend(anomalies)
        
        # Budget warnings
        budget_warnings = self.check_budget_warnings(user_id)
        insights.extend(budget_warnings)
        
        # Seasonal trends
        trends = self.analyze_seasonal_trends(user_id)
        insights.extend(trends)
        
        # Save insights to database
        for insight in insights:
            self.save_insight(user_id, insight)

    def detect_spending_anomalies(self, user_id: int) -> List[Dict]:
        """Detect unusual spending patterns"""
        insights = []
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get category-wise spending for current and previous month
        query = """
        SELECT c.name, 
               SUM(CASE WHEN MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s 
                   THEN t.amount ELSE 0 END) as current_month,
               SUM(CASE WHEN MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s 
                   THEN t.amount ELSE 0 END) as previous_month
        FROM Categories c
        LEFT JOIN Transactions t ON c.id = t.category_id AND t.user_id = %s AND t.type = 'expense'
        WHERE c.user_id = %s AND c.type = 'expense'
        GROUP BY c.id, c.name
        HAVING current_month > 0 OR previous_month > 0
        """
        
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        
        results = self.execute_query(query, (current_month, current_year, prev_month, prev_year, user_id, user_id), fetch_results=True)
        
        for result in results or []:
            category, current, previous = result
            if previous > 0 and current > previous * 1.5:  # 50% increase
                percentage = ((current - previous) / previous) * 100
                insights.append({
                    'type': 'anomaly',
                    'title': f'High {category} Spending',
                    'description': f'Your {category} spending is {percentage:.0f}% higher than last month (₹{current:.0f} vs ₹{previous:.0f})',
                    'priority': 'high' if percentage > 100 else 'medium'
                })
        
        return insights

    def check_budget_warnings(self, user_id: int) -> List[Dict]:
        """Check for budget threshold warnings"""
        insights = []
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        budgets = self.get_budget_summary(user_id, current_month, current_year)
        
        for budget in budgets:
            if budget['percentage'] > 80:
                if budget['percentage'] > 100:
                    insights.append({
                        'type': 'anomaly',
                        'title': f'Budget Exceeded: {budget["category"]}',
                        'description': f'You\'ve exceeded your {budget["category"]} budget by ₹{budget["spent"] - budget["limit"]:.0f}',
                        'priority': 'high'
                    })
                else:
                    insights.append({
                        'type': 'suggestion',
                        'title': f'Budget Warning: {budget["category"]}',
                        'description': f'You\'ve used {budget["percentage"]:.0f}% of your {budget["category"]} budget',
                        'priority': 'medium'
                    })
        
        return insights

    def analyze_seasonal_trends(self, user_id: int) -> List[Dict]:
        """Analyze seasonal spending patterns"""
        insights = []
        current_month = datetime.now().month
        
        # Seasonal spending patterns (simplified)
        seasonal_categories = {
            12: ['Shopping', 'Entertainment'],  # December - holiday spending
            1: ['Healthcare', 'Fitness'],       # January - health resolutions
            4: ['Shopping', 'Travel'],          # April - spring shopping
            10: ['Shopping', 'Entertainment']   # October - festival season
        }
        
        if current_month in seasonal_categories:
            for category in seasonal_categories[current_month]:
                insights.append({
                    'type': 'trend',
                    'title': f'Seasonal Trend: {category}',
                    'description': f'{category} spending typically increases this month. Consider budgeting extra.',
                    'priority': 'low'
                })
        
        return insights

    def save_insight(self, user_id: int, insight: Dict):
        """Save insight to database"""
        query = """
        INSERT INTO FinancialInsights (user_id, insight_type, title, description, priority, data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data_json = json.dumps(insight.get('data', {}))
        self.execute_query(query, (user_id, insight['type'], insight['title'], 
                                 insight['description'], insight['priority'], data_json))

    def get_insights(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent insights for user"""
        query = """
        SELECT insight_type, title, description, priority, created_at, is_read
        FROM FinancialInsights 
        WHERE user_id = %s AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY priority DESC, created_at DESC 
        LIMIT %s
        """
        results = self.execute_query(query, (user_id, limit), fetch_results=True)
        
        insights = []
        for result in results or []:
            insights.append({
                'type': result[0],
                'title': result[1],
                'description': result[2],
                'priority': result[3],
                'created_at': result[4],
                'is_read': result[5]
            })
        
        return insights

    def create_transaction_template(self, user_id: int, name: str, transaction_type: str,
                                  amount: float, category_id: int, description: str, notes: str = None) -> bool:
        """Create a reusable transaction template"""
        query = """
        INSERT INTO TransactionTemplates (user_id, name, type, amount, category_id, description, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, name, transaction_type, amount, 
                                        category_id, description, notes)) is not None

    def get_transaction_templates(self, user_id: int) -> List[Dict]:
        """Get user's transaction templates"""
        query = """
        SELECT t.id, t.name, t.type, t.amount, c.name as category_name, 
               t.description, t.notes, t.usage_count
        FROM TransactionTemplates t
        JOIN Categories c ON t.category_id = c.id
        WHERE t.user_id = %s
        ORDER BY t.usage_count DESC, t.name
        """
        results = self.execute_query(query, (user_id,), fetch_results=True)
        
        templates = []
        for result in results or []:
            templates.append({
                'id': result[0],
                'name': result[1],
                'type': result[2],
                'amount': float(result[3]),
                'category_name': result[4],
                'description': result[5],
                'notes': result[6],
                'usage_count': result[7]
            })
        
        return templates

    def use_template(self, template_id: int, user_id: int, transaction_date: date = None) -> bool:
        """Create transaction from template"""
        if not transaction_date:
            transaction_date = date.today()
        
        # Get template details
        query = """
        SELECT type, amount, category_id, description, notes
        FROM TransactionTemplates 
        WHERE id = %s AND user_id = %s
        """
        result = self.execute_query(query, (template_id, user_id), fetch_results=True)
        
        if not result:
            return False
        
        template_data = result[0]
        
        # Create transaction
        success = self.add_transaction(user_id, template_data[0], template_data[1], 
                                     template_data[2], template_data[3], 
                                     transaction_date, template_data[4])
        
        if success:
            # Update usage count
            self.execute_query("UPDATE TransactionTemplates SET usage_count = usage_count + 1 WHERE id = %s", 
                             (template_id,))
        
        return success

    def create_savings_goal(self, user_id: int, name: str, target_amount: float, 
                          target_date: date = None, priority: str = 'medium') -> bool:
        """Create a savings goal"""
        query = """
        INSERT INTO SavingsGoals (user_id, name, target_amount, target_date, priority)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, name, target_amount, target_date, priority)) is not None

    def get_savings_goals(self, user_id: int) -> List[Dict]:
        """Get user's savings goals with progress"""
        query = """
        SELECT id, name, target_amount, current_amount, target_date, priority, 
               (current_amount / target_amount * 100) as progress_percentage,
               DATEDIFF(target_date, CURDATE()) as days_remaining
        FROM SavingsGoals 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY priority DESC, target_date ASC
        """
        results = self.execute_query(query, (user_id,), fetch_results=True)
        
        goals = []
        for result in results or []:
            goals.append({
                'id': result[0],
                'name': result[1],
                'target_amount': float(result[2]),
                'current_amount': float(result[3]),
                'target_date': result[4],
                'priority': result[5],
                'progress_percentage': float(result[6]) if result[6] else 0,
                'days_remaining': result[7] if result[7] else None
            })
        
        return goals

    def update_savings_goal_progress(self, goal_id: int, amount: float) -> bool:
        """Add to savings goal progress"""
        query = "UPDATE SavingsGoals SET current_amount = current_amount + %s WHERE id = %s"
        return self.execute_query(query, (amount, goal_id)) is not None

    # ...existing methods continue...


import mysql.connector
from mysql.connector import Error
import hashlib
import bcrypt
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict, Any

class DBManager:
    def __init__(self):
        self.connection = None
        self.current_user_id = None

    def connect(self):
        """Establish a connection to the MySQL database"""
        try:
            from config import DB_CONFIG
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
        except ImportError:
            print("Error: config.py not found. Please create it with your database configuration.")
            return False

    def disconnect(self):
        """Close the database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(self, username: str, password: str, currency_id: int = 1) -> bool:
        """Create a new user and default categories"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
                    
            hashed_password = self.hash_password(password)
            query = "INSERT INTO Users (username, hashed_password, currency_id) VALUES (%s, %s, %s)"
            user_id = self.execute_query(query, (username, hashed_password, currency_id), fetch_id=True)
            
            if user_id:
                self._create_default_categories(user_id)
                return True
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def _create_default_categories(self, user_id: int):
        """Create default categories for new user"""
        default_categories = [
            ('Food & Dining', 'expense'),
            ('Transportation', 'expense'),
            ('Shopping', 'expense'),
            ('Entertainment', 'expense'),
            ('Bills & Utilities', 'expense'),
            ('Healthcare', 'expense'),
            ('Salary', 'income'),
            ('Freelance', 'income'),
            ('Investment', 'income'),
            ('Other Income', 'income'),
        ]
        
        query = "INSERT INTO Categories (user_id, name, type) VALUES (%s, %s, %s)"
        for name, cat_type in default_categories:
            self.execute_query(query, (user_id, name, cat_type))

    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user_id if successful"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
                
        query = "SELECT id, hashed_password FROM Users WHERE username = %s"
        result = self.execute_query(query, (username,), fetch_results=True)
        
        if result and self.verify_password(password, result[0][1]):
            self.current_user_id = result[0][0]
            return self.current_user_id
        return None

    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user settings"""
        query = """
        SELECT u.theme, c.name, c.symbol, c.code, u.currency_id 
        FROM Users u 
        LEFT JOIN Currencies c ON u.currency_id = c.id 
        WHERE u.id = %s
        """
        result = self.execute_query(query, (user_id,), fetch_results=True)
        if result:
            return {
                'theme': result[0][0],
                'currency_name': result[0][1],
                'currency_symbol': result[0][2],
                'currency_code': result[0][3],
                'currency_id': result[0][4]
            }
        return {}

    def update_user_settings(self, user_id: int, theme: str = None, currency_id: int = None) -> bool:
        """Update user settings"""
        updates = []
        params = []
        
        if theme:
            updates.append("theme = %s")
            params.append(theme)
        if currency_id:
            updates.append("currency_id = %s")
            params.append(currency_id)
            
        if updates:
            query = f"UPDATE Users SET {', '.join(updates)} WHERE id = %s"
            params.append(user_id)
            return self.execute_query(query, params) is not None
        return True

    def add_transaction(self, user_id: int, transaction_type: str, amount: float, 
                       category_id: int, description: str, transaction_date: date, 
                       notes: str = None, attachment_path: str = None) -> bool:
        """Add a new transaction"""
        query = """
        INSERT INTO Transactions (user_id, type, amount, category_id, description, 
                                transaction_date, notes, attachment_path) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (user_id, transaction_type, amount, category_id, description, 
                 transaction_date, notes, attachment_path)
        return self.execute_query(query, params) is not None

    def get_transactions(self, user_id: int, month: int = None, year: int = None, 
                        limit: int = None) -> List[Tuple]:
        """Get transactions with optional filters"""
        query = """
        SELECT t.id, t.type, t.amount, c.name, t.description, t.transaction_date, 
               t.notes, t.attachment_path
        FROM Transactions t 
        JOIN Categories c ON t.category_id = c.id 
        WHERE t.user_id = %s
        """
        params = [user_id]
        
        if month and year:
            query += " AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s"
            params.extend([month, year])
            
        query += " ORDER BY t.transaction_date DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        return self.execute_query(query, params, fetch_results=True) or []

    def get_categories(self, user_id: int, category_type: str = None) -> List[Tuple]:
        """Get user categories"""
        query = "SELECT id, name, type FROM Categories WHERE user_id = %s"
        params = [user_id]
        
        if category_type:
            query += " AND type = %s"
            params.append(category_type)
            
        query += " ORDER BY name"
        return self.execute_query(query, params, fetch_results=True) or []

    def add_category(self, user_id: int, name: str, category_type: str, 
                    icon_path: str = None) -> bool:
        """Add a new category"""
        query = "INSERT INTO Categories (user_id, name, type, icon_path) VALUES (%s, %s, %s, %s)"
        return self.execute_query(query, (user_id, name, category_type, icon_path)) is not None

    def get_budget_summary(self, user_id: int, month: int, year: int) -> List[Dict]:
        """Get budget summary for a specific month"""
        query = """
        SELECT c.name, b.monthly_limit, 
               COALESCE(SUM(t.amount), 0) as spent
        FROM Categories c
        LEFT JOIN Budgets b ON c.id = b.category_id AND b.user_id = %s
        LEFT JOIN Transactions t ON c.id = t.category_id AND t.user_id = %s 
                  AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s
                  AND t.type = 'expense'
        WHERE c.user_id = %s AND c.type = 'expense'
        GROUP BY c.id, c.name, b.monthly_limit
        HAVING b.monthly_limit IS NOT NULL
        """
        results = self.execute_query(query, (user_id, user_id, month, year, user_id), fetch_results=True)
        
        budgets = []
        for result in results or []:
            budgets.append({
                'category': result[0],
                'limit': float(result[1]),
                'spent': float(result[2]),
                'remaining': float(result[1]) - float(result[2]),
                'percentage': (float(result[2]) / float(result[1])) * 100 if result[1] > 0 else 0
            })
        return budgets

    def set_budget(self, user_id: int, category_id: int, monthly_limit: float, 
                  start_date: date, end_date: date) -> bool:
        """Set or update budget for a category"""
        # Check if budget exists
        check_query = "SELECT id FROM Budgets WHERE user_id = %s AND category_id = %s"
        existing = self.execute_query(check_query, (user_id, category_id), fetch_results=True)
        
        if existing:
            # Update existing budget
            query = """
            UPDATE Budgets SET monthly_limit = %s, start_date = %s, end_date = %s 
            WHERE user_id = %s AND category_id = %s
            """
            params = (monthly_limit, start_date, end_date, user_id, category_id)
        else:
            # Create new budget
            query = """
            INSERT INTO Budgets (user_id, category_id, monthly_limit, start_date, end_date) 
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (user_id, category_id, monthly_limit, start_date, end_date)
            
        return self.execute_query(query, params) is not None

    def get_dashboard_data(self, user_id: int, month: int, year: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        # Total income and expenses
        query = """
        SELECT type, SUM(amount) 
        FROM Transactions 
        WHERE user_id = %s AND MONTH(transaction_date) = %s AND YEAR(transaction_date) = %s
        GROUP BY type
        """
        totals_result = self.execute_query(query, (user_id, month, year), fetch_results=True)
        
        income = expense = 0
        for result in totals_result or []:
            if result[0] == 'income':
                income = float(result[1])
            else:
                expense = float(result[1])
        
        # Category-wise expenses
        query = """
        SELECT c.name, SUM(t.amount) 
        FROM Transactions t 
        JOIN Categories c ON t.category_id = c.id 
        WHERE t.user_id = %s AND t.type = 'expense' 
              AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s
        GROUP BY c.name
        ORDER BY SUM(t.amount) DESC
        """
        category_expenses = self.execute_query(query, (user_id, month, year), fetch_results=True)
        
        return {
            'income': income,
            'expense': expense,
            'balance': income - expense,
            'category_expenses': [(cat, float(amt)) for cat, amt in (category_expenses or [])],
            'recent_transactions': self.get_transactions(user_id, limit=5)
        }

    def execute_query(self, query: str, params: tuple = None, fetch_results: bool = False, 
                     fetch_id: bool = False):
        """Enhanced execute_query method"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch_id:
                self.connection.commit()
                return cursor.lastrowid
            elif fetch_results:
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Error as e:
            print(f"Database error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()