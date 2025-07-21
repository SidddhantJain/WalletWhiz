#-- filepath: d:\Siddhant\projects\WalletWhiz\WalletWhiz\database\db_manager.py
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