# File: DatabaseManager.py
# Path: AIDEV-Deploy/Core/DatabaseManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  4:15PM
# Description: Manages database operations for the AIDEV-Deploy system

"""
DatabaseManager Module

This module handles all database operations for the AIDEV-Deploy system,
including schema creation, transaction management, and query execution.
It provides a high-level interface for other components to interact with
the underlying SQLite database.
"""

import os
import sqlite3
import argparse
import json
import datetime
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

class DatabaseManager:
    """
    Manages database connections and operations for the AIDEV-Deploy system.
    
    This class provides methods for initializing the database schema,
    executing queries, and managing transactions. It ensures data consistency
    and provides error handling for database operations.
    
    Attributes:
        DatabasePath: Path to the SQLite database file
        Connection: Active SQLite connection
        Cursor: Database cursor for executing queries
        IsTransactionActive: Flag indicating if a transaction is in progress
    """
    
    def __init__(self, DatabasePath: str = None):
        """
        Initialize the DatabaseManager.
        
        Args:
            DatabasePath: Path to the SQLite database file. If None, uses default location.
        """
        self.DatabasePath = DatabasePath or self._GetDefaultDatabasePath()
        self.Connection = None
        self.Cursor = None
        self.IsTransactionActive = False
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.DatabasePath), exist_ok=True)
        
        # Connect to the database
        self._Connect()
    
    def _GetDefaultDatabasePath(self) -> str:
        """
        Get the default database path.
        
        Returns:
            str: Path to the default database location
        """
        AppDataDir = os.path.join(str(Path.home()), ".AIDEV-Deploy")
        os.makedirs(AppDataDir, exist_ok=True)
        return os.path.join(AppDataDir, "deploy.db")
    
    def _Connect(self) -> None:
        """
        Establish a connection to the SQLite database.
        """
        self.Connection = sqlite3.connect(self.DatabasePath)
        self.Connection.row_factory = sqlite3.Row
        self.Cursor = self.Connection.cursor()
    
    def Close(self) -> None:
        """
        Close the database connection.
        """
        if self.Connection:
            self.Connection.close()
            self.Connection = None
            self.Cursor = None
    
    def InitializeDatabase(self) -> None:
        """
        Create the database schema if it doesn't exist.
        This method creates all required tables for the AIDEV-Deploy system.
        """
        # Transactions table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            backup_id TEXT,
            project_path TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        # Files table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            original_name TEXT NOT NULL,
            source_path TEXT NOT NULL,
            destination_path TEXT NOT NULL,
            status TEXT NOT NULL,
            validation_status TEXT,
            checksum TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id)
        )
        ''')
        
        # Operations table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            file_id TEXT,
            operation_type TEXT NOT NULL,
            source_path TEXT,
            destination_path TEXT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id),
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
        ''')
        
        # Backups table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            project_path TEXT NOT NULL,
            backup_path TEXT NOT NULL,
            backup_type TEXT NOT NULL,
            size INTEGER NOT NULL,
            file_count INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            verified BOOLEAN NOT NULL DEFAULT 0,
            checksum TEXT
        )
        ''')
        
        # Users table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Permissions table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            permission_type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Validation Rules table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS validation_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_type TEXT NOT NULL,
            rule_pattern TEXT NOT NULL,
            standard TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        # Validation Results table
        self.Cursor.execute('''
        CREATE TABLE IF NOT EXISTS validation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            rule_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            line_number INTEGER,
            message TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (rule_id) REFERENCES validation_rules(id)
        )
        ''')
        
        # Commit the changes
        self.Connection.commit()
        
        # Insert default user if not exists
        self._InsertDefaultUser()
        
        # Insert default validation rules
        self._InsertDefaultValidationRules()
    
    def _InsertDefaultUser(self) -> None:
        """
        Insert a default user if no users exist in the database.
        """
        self.Cursor.execute("SELECT COUNT(*) FROM users")
        if self.Cursor.fetchone()[0] == 0:
            DefaultUserId = str(uuid.uuid4())
            CurrentTime = datetime.datetime.now().isoformat()
            
            self.Cursor.execute(
                "INSERT INTO users (id, username, created_at) VALUES (?, ?, ?)",
                (DefaultUserId, "admin", CurrentTime)
            )
            
            # Add admin permissions
            for Permission in ["VIEW_FILES", "VALIDATE_FILES", "DEPLOY_FILES", 
                              "MANAGE_BACKUPS", "MODIFY_CONFIG", "MANAGE_USERS"]:
                self.Cursor.execute(
                    "INSERT INTO permissions (user_id, permission_type) VALUES (?, ?)",
                    (DefaultUserId, Permission)
                )
            
            self.Connection.commit()
    
    def _InsertDefaultValidationRules(self) -> None:
        """
        Insert default validation rules if none exist.
        """
        self.Cursor.execute("SELECT COUNT(*) FROM validation_rules")
        if self.Cursor.fetchone()[0] == 0:
            # File header validation rule
            HeaderPattern = r'# File: .+\\.py\\n# Path: .+\\n# Standard: AIDEV-PascalCase-[0-9]+\\.[0-9]+\\n# Created: [0-9]{4}-[0-9]{2}-[0-9]{2}\\n# Last Modified: [0-9]{4}-[0-9]{2}-[0-9]{2}  [0-9]{1,2}:[0-9]{2}(?:AM|PM)\\n# Description: .+'
            
            self.Cursor.execute(
                "INSERT INTO validation_rules (rule_type, rule_pattern, standard, description) VALUES (?, ?, ?, ?)",
                ("FILE_HEADER", HeaderPattern, "AIDEV-PascalCase-1.6", "File header format validation")
            )
            
            # More validation rules can be added here
            
            self.Connection.commit()
    
    def BeginTransaction(self) -> None:
        """
        Begin a database transaction.
        """
        if not self.IsTransactionActive:
            self.Connection.execute("BEGIN TRANSACTION")
            self.IsTransactionActive = True
    
    def CommitTransaction(self) -> None:
        """
        Commit the current transaction.
        """
        if self.IsTransactionActive:
            self.Connection.commit()
            self.IsTransactionActive = False
    
    def RollbackTransaction(self) -> None:
        """
        Rollback the current transaction.
        """
        if self.IsTransactionActive:
            self.Connection.rollback()
            self.IsTransactionActive = False
    
    def ExecuteQuery(self, Query: str, Parameters: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query with parameters.
        
        Args:
            Query: SQL query string
            Parameters: Query parameters as a tuple
            
        Returns:
            sqlite3.Cursor: Query cursor result
        """
        return self.Cursor.execute(Query, Parameters)
    
    def ExecuteQueryFetchAll(self, Query: str, Parameters: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and fetch all results as a list of dictionaries.
        
        Args:
            Query: SQL query string
            Parameters: Query parameters as a tuple
            
        Returns:
            List[Dict[str, Any]]: Query results as a list of dictionaries
        """
        self.Cursor.execute(Query, Parameters)
        return [dict(row) for row in self.Cursor.fetchall()]
    
    def ExecuteQueryFetchOne(self, Query: str, Parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Execute a SQL query and fetch one result as a dictionary.
        
        Args:
            Query: SQL query string
            Parameters: Query parameters as a tuple
            
        Returns:
            Optional[Dict[str, Any]]: Query result as a dictionary or None
        """
        self.Cursor.execute(Query, Parameters)
        Row = self.Cursor.fetchone()
        return dict(Row) if Row else None
    
    def CreateBackup(self, BackupPath: str = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            BackupPath: Destination path for the backup file
            
        Returns:
            str: Path to the created backup file
        """
        if BackupPath is None:
            Timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            BackupPath = f"{self.DatabasePath}.{Timestamp}.backup"
        
        # Create a new database connection for backup
        BackupConnection = sqlite3.connect(BackupPath)
        self.Connection.backup(BackupConnection)
        BackupConnection.close()
        
        return BackupPath

def Main():
    """
    Command-line interface for database initialization and management.
    """
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy Database Manager")
    Parser.add_argument("--init", action="store_true", help="Initialize the database schema")
    Parser.add_argument("--backup", action="store_true", help="Create a database backup")
    Parser.add_argument("--path", help="Custom database path")
    
    Args = Parser.parse_args()
    
    # Create database manager
    Manager = DatabaseManager(Args.path)
    
    try:
        if Args.init:
            print(f"Initializing database at: {Manager.DatabasePath}")
            Manager.InitializeDatabase()
            print("Database schema initialized successfully.")
        
        if Args.backup:
            BackupPath = Manager.CreateBackup()
            print(f"Database backup created at: {BackupPath}")
    
    finally:
        Manager.Close()

if __name__ == "__main__":
    Main()
