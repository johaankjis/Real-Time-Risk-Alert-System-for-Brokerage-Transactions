"""
Database configuration and connection management
Supports both PostgreSQL and SQLite for flexibility
"""

import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from contextlib import contextmanager

# Database configuration
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'postgresql' or 'sqlite'
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'risk_alert_system')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'risk_alert_system.db')


class DatabaseConnection:
    """Manages database connections with support for PostgreSQL and SQLite"""
    
    def __init__(self, db_type: str = DB_TYPE):
        self.db_type = db_type
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        if self.db_type == 'postgresql':
            self.connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
        else:  # sqlite
            self.connection = sqlite3.connect(SQLITE_DB_PATH)
            self.connection.row_factory = sqlite3.Row
            # Enable foreign keys for SQLite
            self.connection.execute("PRAGMA foreign_keys = ON")
        
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        if not self.connection:
            self.connect()
        
        if self.db_type == 'postgresql':
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = self.connection.cursor()
        
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()


def get_db_connection():
    """Factory function to get database connection"""
    db = DatabaseConnection()
    db.connect()
    return db


def initialize_sqlite_schema():
    """Initialize SQLite database with schema (PostgreSQL uses SQL scripts)"""
    if DB_TYPE != 'sqlite':
        return
    
    db = DatabaseConnection('sqlite')
    db.connect()
    
    # Read and execute schema
    with open('scripts/01_create_schema.sql', 'r') as f:
        schema_sql = f.read()
        # SQLite doesn't support some PostgreSQL syntax, adapt it
        schema_sql = schema_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        schema_sql = schema_sql.replace('DECIMAL(15, 2)', 'REAL')
        
        # Execute each statement separately
        for statement in schema_sql.split(';'):
            if statement.strip():
                try:
                    db.connection.execute(statement)
                except Exception as e:
                    print(f"Warning: {e}")
    
    # Read and execute seed data
    with open('scripts/02_seed_initial_data.sql', 'r') as f:
        seed_sql = f.read()
        for statement in seed_sql.split(';'):
            if statement.strip():
                try:
                    db.connection.execute(statement)
                except Exception as e:
                    print(f"Warning: {e}")
    
    db.connection.commit()
    db.close()
    print("SQLite database initialized successfully!")


if __name__ == "__main__":
    # Initialize database when run directly
    if DB_TYPE == 'sqlite':
        initialize_sqlite_schema()
        print(f"Database initialized at: {SQLITE_DB_PATH}")
    else:
        print("For PostgreSQL, run the SQL scripts manually:")
        print("  psql -U postgres -d risk_alert_system -f scripts/01_create_schema.sql")
        print("  psql -U postgres -d risk_alert_system -f scripts/02_seed_initial_data.sql")
