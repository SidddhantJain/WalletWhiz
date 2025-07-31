# config.py

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "rootr",      # <<< IMPORTANT: Replace with your MySQL username
    "password": "siddhant", # <<< IMPORTANT: Replace with your MySQL password
    "database": "walletwhiz_db"
}

# UI Configuration
UI_CONFIG = {
    "app_name": "WalletWhiz",
    "version": "2.0.0",
    "default_theme": "light",
    "animation_duration": 300,
    "chart_colors": {
        "primary": "#667eea",
        "secondary": "#764ba2", 
        "success": "#4CAF50",
        "danger": "#F44336",
        "warning": "#FF9800",
        "info": "#2196F3"
    },
    "gradients": {
        "sidebar": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #667eea, stop:1 #764ba2)",
        "header": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff9a9e, stop:1 #fad0c4)",
        "card_green": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049)",
        "card_red": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F44336, stop:1 #d32f2f)",
        "card_blue": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976d2)",
        "card_orange": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF9800, stop:1 #f57c00)"
    }
}