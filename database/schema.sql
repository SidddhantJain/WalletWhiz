-- WalletWhiz Database Schema - Phase 1

-- Users table
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    currency_id INT,
    theme ENUM('light', 'dark') DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (currency_id) REFERENCES Currencies(id)
);

-- Currencies table (already exists, keeping for reference)
CREATE TABLE IF NOT EXISTS Currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5) NOT NULL,
    code VARCHAR(3) UNIQUE NOT NULL
);

-- Categories table
CREATE TABLE IF NOT EXISTS Categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    icon_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Transactions table
CREATE TABLE IF NOT EXISTS Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category_id INT NOT NULL,
    description VARCHAR(255),
    transaction_date DATE NOT NULL,
    notes TEXT,
    attachment_path VARCHAR(255),
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_schedule_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(id)
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

-- Insert default currencies
INSERT IGNORE INTO Currencies (name, symbol, code) VALUES
('US Dollar', '$', 'USD'),
('Indian Rupee', '₹', 'INR'),
('Euro', '€', 'EUR'),
('British Pound', '£', 'GBP'),
('Japanese Yen', '¥', 'JPY');

-- Insert default categories (will be added per user during registration)
-- These are templates that will be copied for each new user
