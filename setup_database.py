import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect without specifying database
        config_no_db = DB_CONFIG.copy()
        db_name = config_no_db.pop('database')
        
        connection = mysql.connector.connect(**config_no_db)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created successfully")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables():
    """Create all required tables"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as schema_file:
            schema_commands = schema_file.read()
            
        # Split by semicolon and execute each command
        for command in schema_commands.split(';'):
            command = command.strip()
            if command:
                cursor.execute(command)
                
        connection.commit()
        print("All tables created successfully")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error creating tables: {e}")
    except FileNotFoundError:
        print("schema.sql file not found")

if __name__ == '__main__':
    print("Setting up WalletWhiz database...")
    create_database()
    create_tables()
    print("Database setup complete!")
