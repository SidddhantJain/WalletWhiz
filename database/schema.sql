-- WalletWhiz Database Schema - Enhanced Version

-- Users table (enhanced)
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    currency_id INT,
    theme ENUM('light', 'dark', 'auto') DEFAULT 'light',
    profile_picture VARCHAR(255),
    notification_preferences JSON,
    security_settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (currency_id) REFERENCES Currencies(id)
);

-- Currencies table (already exists, keeping for reference)
CREATE TABLE IF NOT EXISTS Currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5) NOT NULL,
    code VARCHAR(3) UNIQUE NOT NULL
);

-- Categories table (enhanced)
CREATE TABLE IF NOT EXISTS Categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    icon_name VARCHAR(50) DEFAULT 'default',
    color VARCHAR(7) DEFAULT '#007bff',
    is_default BOOLEAN DEFAULT FALSE,
    parent_category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_category_id) REFERENCES Categories(id)
);

-- Transactions table (enhanced)
CREATE TABLE IF NOT EXISTS Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('income', 'expense', 'transfer') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    original_currency VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(10, 4) DEFAULT 1.0000,
    category_id INT NOT NULL,
    description VARCHAR(255),
    transaction_date DATE NOT NULL,
    notes TEXT,
    tags JSON,
    location VARCHAR(255),
    attachment_path VARCHAR(255),
    receipt_ocr_data JSON,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_schedule_id INT,
    template_id INT,
    confidence_score DECIMAL(3, 2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(id),
    INDEX idx_user_date (user_id, transaction_date),
    INDEX idx_category (category_id),
    INDEX idx_tags (tags)
);

-- Budgets table
CREATE TABLE IF NOT EXISTS Budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    monthly_limit DECIMAL(10, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(id)
);

-- New: Savings Goals
CREATE TABLE IF NOT EXISTS SavingsGoals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    target_amount DECIMAL(10, 2) NOT NULL,
    current_amount DECIMAL(10, 2) DEFAULT 0.00,
    target_date DATE,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- New: Transaction Templates
CREATE TABLE IF NOT EXISTS TransactionTemplates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    amount DECIMAL(10, 2),
    category_id INT NOT NULL,
    description VARCHAR(255),
    notes TEXT,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(id)
);

-- New: Shared Expenses
CREATE TABLE IF NOT EXISTS SharedExpenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    shared_with_user_id INT NOT NULL,
    share_amount DECIMAL(10, 2) NOT NULL,
    is_settled BOOLEAN DEFAULT FALSE,
    settled_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- New: Financial Insights
CREATE TABLE IF NOT EXISTS FinancialInsights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    insight_type ENUM('anomaly', 'trend', 'suggestion', 'achievement') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    data JSON,
    is_read BOOLEAN DEFAULT FALSE,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- New: Recurring Schedules
CREATE TABLE IF NOT EXISTS RecurringSchedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    template_id INT NOT NULL,
    frequency ENUM('daily', 'weekly', 'monthly', 'quarterly', 'yearly') NOT NULL,
    interval_value INT DEFAULT 1,
    start_date DATE NOT NULL,
    end_date DATE,
    next_occurrence DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES TransactionTemplates(id)
);

-- Enhanced default currencies
INSERT IGNORE INTO Currencies (name, symbol, code) VALUES
('US Dollar', '$', 'USD'),
('Indian Rupee', '₹', 'INR'),
('Euro', '€', 'EUR'),
('British Pound', '£', 'GBP'),
('Japanese Yen', '¥', 'JPY'),
('Canadian Dollar', 'C$', 'CAD'),
('Australian Dollar', 'A$', 'AUD'),
('Swiss Franc', 'Fr', 'CHF');

-- Insert default categories (will be added per user during registration)
-- These are templates that will be copied for each new user
