# WalletWhiz/database/db_manager.py

import sqlite3
import os

class DBManager:
    def __init__(self, db_path='walletwhiz.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,  -- 'income' or 'expense'
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                tag TEXT,
                notes TEXT,
                date TEXT NOT NULL
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                month TEXT NOT NULL
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                frequency TEXT NOT NULL,  -- 'weekly', 'monthly'
                next_date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_transaction(self, t_type, amount, category, tag, notes, date):
        self.cursor.execute("""
            INSERT INTO transactions (type, amount, category, tag, notes, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (t_type, amount, category, tag, notes, date))
        self.conn.commit()

    def get_transactions(self, limit=100):
        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def delete_transaction(self, transaction_id):
        self.cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()

    def update_transaction(self, transaction_id, t_type, amount, category, tag, notes, date):
        self.cursor.execute("""
            UPDATE transactions
            SET type = ?, amount = ?, category = ?, tag = ?, notes = ?, date = ?
            WHERE id = ?
        """, (t_type, amount, category, tag, notes, date, transaction_id))
        self.conn.commit()

    def add_budget(self, category, limit_amount, month):
        self.cursor.execute("""
            INSERT INTO budgets (category, limit_amount, month)
            VALUES (?, ?, ?)
        """, (category, limit_amount, month))
        self.conn.commit()

    def get_budget_for_month(self, month):
        self.cursor.execute("SELECT * FROM budgets WHERE month = ?", (month,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
