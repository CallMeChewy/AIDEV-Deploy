# File: TransactionManager.py
# Path: AIDEV-Deploy/Core/TransactionManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  4:25PM
# Description: Manages deployment transactions with atomic operations

"""
TransactionManager Module

This module provides transaction management for file deployment operations,
ensuring that all operations are performed atomically (all succeed or all fail).
It tracks transaction state, manages rollback capabilities, and coordinates
with other components like BackupManager and ValidationEngine.
"""

import os
import uuid
import datetime
import json
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from Core.DatabaseManager import DatabaseManager

# Transaction states
TRANSACTION_STATES = {
    "INITIALIZED": "INITIALIZED",
    "VALIDATED": "VALIDATED",
    "IN_PROGRESS": "IN_PROGRESS",
    "COMPLETED": "COMPLETED", 
    "FAILED": "FAILED",
    "ROLLED_BACK": "ROLLED_BACK"
}

class TransactionManager:
    """
    Manages file deployment transactions with rollback capabilities.
    
    This class ensures that file deployment operations are atomic,
    with proper validation, execution, and rollback capabilities.
    It coordinates with the DatabaseManager to persist transaction state.
    
    Attributes:
        DatabaseManager: Instance of DatabaseManager for database operations
        CurrentTransactionId: ID of the active transaction, if any
    """
    
    def __init__(self, DbManager: Optional[DatabaseManager] = None):
        """
        Initialize the TransactionManager.
        
        Args:
            DbManager: Optional DatabaseManager instance. If None, creates a new instance.
        """
        self.DatabaseManager = DbManager or DatabaseManager()
        self.CurrentTransactionId = None
    
    def CreateTransaction(self, UserId: str, ProjectPath: str, Description: str = None) -> str:
        """
        Create a new transaction and return its ID.
        
        Args:
            UserId: ID of the user creating the transaction
            ProjectPath: Path to the project being deployed
            Description: Optional description of the transaction
            
        Returns:
            str: ID of the newly created transaction
        """
        TransactionId = str(uuid.uuid4())
        Timestamp = datetime.datetime.now().isoformat()
        
        self.DatabaseManager.BeginTransaction()
        try:
            self.DatabaseManager.ExecuteQuery(
                """
                INSERT INTO transactions 
                (id, timestamp, user_id, status, project_path, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (TransactionId, Timestamp, UserId, TRANSACTION_STATES["INITIALIZED"], 
                 ProjectPath, Description)
            )
            self.DatabaseManager.CommitTransaction()
            self.CurrentTransactionId = TransactionId
            return TransactionId
        except Exception as E:
            self.DatabaseManager.RollbackTransaction()
            raise RuntimeError(f"Failed to create transaction: {E}")
    
    def GetTransactionStatus(self, TransactionId: str) -> str:
        """
        Get the current status of a transaction.
        
        Args:
            TransactionId: ID of the transaction
            
        Returns:
            str: Current status of the transaction
        """
        Result = self.DatabaseManager.ExecuteQueryFetchOne(
            "SELECT status FROM transactions WHERE id = ?",
            (TransactionId,)
        )
        if not Result:
            raise ValueError(f"Transaction {TransactionId} not found")
        
        return Result["status"]
    
    def UpdateTransactionStatus(self, TransactionId: str, Status: str) -> None:
        """
        Update the status of a transaction.
        
        Args:
            TransactionId: ID of the transaction
            Status: New status for the transaction (use TRANSACTION_STATES constants)
        """
        if Status not in TRANSACTION_STATES.values():
            raise ValueError(f"Invalid transaction status: {Status}")
        
        self.DatabaseManager.ExecuteQuery(
            "UPDATE transactions SET status = ? WHERE id = ?",
            (Status, TransactionId)
        )
        self.DatabaseManager.Connection.commit()
    
    def AddFileToTransaction(self, TransactionId: str, SourcePath: str, 
                           DestinationPath: str, Checksum: str = None) -> str:
        """
        Add a file to a transaction.
        
        Args:
            TransactionId: ID of the transaction
            SourcePath: Path to the source file
            DestinationPath: Path where the file will be deployed
            Checksum: Optional file checksum
            
        Returns:
            str: ID of the file entry
        """
        # Check transaction status
        Status = self.GetTransactionStatus(TransactionId)
        if Status not in [TRANSACTION_STATES["INITIALIZED"], TRANSACTION_STATES["VALIDATED"]]:
            raise ValueError(f"Cannot add file to transaction in {Status} state")
        
        FileId = str(uuid.uuid4())
        OriginalName = os.path.basename(SourcePath)
        
        self.DatabaseManager.ExecuteQuery(
            """
            INSERT INTO files
            (id, transaction_id, original_name, source_path, destination_path, status, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (FileId, TransactionId, OriginalName, SourcePath, DestinationPath, 
             "PENDING", Checksum)
        )
        self.DatabaseManager.Connection.commit()
        
        return FileId
    
    def GetTransactionFiles(self, TransactionId: str) -> List[Dict[str, Any]]:
        """
        Get all files in a transaction.
        
        Args:
            TransactionId: ID of the transaction
            
        Returns:
            List[Dict[str, Any]]: List of file entries
        """
        return self.DatabaseManager.ExecuteQueryFetchAll(
            "SELECT * FROM files WHERE transaction_id = ?",
            (TransactionId,)
        )
    
    def ValidateTransaction(self, TransactionId: str, 
                          ValidationCallback: Callable[[str], Dict[str, Any]]) -> bool:
        """
        Validate all files in a transaction.
        
        Args:
            TransactionId: ID of the transaction
            ValidationCallback: Function to validate a file and return results
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        # Check transaction status
        Status = self.GetTransactionStatus(TransactionId)
        if Status != TRANSACTION_STATES["INITIALIZED"]:
            raise ValueError(f"Cannot validate transaction in {Status} state")
        
        Files = self.GetTransactionFiles(TransactionId)
        if not Files:
            raise ValueError(f"Transaction {TransactionId} has no files to validate")
        
        AllValid = True
        
        self.DatabaseManager.BeginTransaction()
        try:
            for File in Files:
                FileId = File["id"]
                SourcePath = File["source_path"]
                
                # Validate the file
                ValidationResult = ValidationCallback(SourcePath)
                ValidationStatus = ValidationResult.get("status", "FAIL")
                
                # Update file validation status
                self.DatabaseManager.ExecuteQuery(
                    "UPDATE files SET validation_status = ? WHERE id = ?",
                    (ValidationStatus, FileId)
                )
                
                # Store validation results
                if "errors" in ValidationResult or "warnings" in ValidationResult:
                    self._StoreValidationResults(FileId, ValidationResult)
                
                # Update validation success flag
                if ValidationStatus == "FAIL":
                    AllValid = False
            
            # Update transaction status
            NewStatus = TRANSACTION_STATES["VALIDATED"] if AllValid else TRANSACTION_STATES["INITIALIZED"]
            self.UpdateTransactionStatus(TransactionId, NewStatus)
            
            self.DatabaseManager.CommitTransaction()
            return AllValid
        except Exception as E:
            self.DatabaseManager.RollbackTransaction()
            self.UpdateTransactionStatus(TransactionId, TRANSACTION_STATES["INITIALIZED"])
            raise RuntimeError(f"Validation failed: {E}")
    
    def _StoreValidationResults(self, FileId: str, ValidationResult: Dict[str, Any]) -> None:
        """
        Store validation results in the database.
        
        Args:
            FileId: ID of the file
            ValidationResult: Validation results dictionary
        """
        Timestamp = datetime.datetime.now().isoformat()
        
        # Process errors
        for Error in ValidationResult.get("errors", []):
            self.DatabaseManager.ExecuteQuery(
                """
                INSERT INTO validation_results
                (file_id, rule_id, status, line_number, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (FileId, Error.get("rule_id", 0), "FAIL", 
                 Error.get("line", 0), Error.get("message", ""), Timestamp)
            )
        
        # Process warnings
        for Warning in ValidationResult.get("warnings", []):
            self.DatabaseManager.ExecuteQuery(
                """
                INSERT INTO validation_results
                (file_id, rule_id, status, line_number, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (FileId, Warning.get("rule_id", 0), "WARNING", 
                 Warning.get("line", 0), Warning.get("message", ""), Timestamp)
            )
    
    def ExecuteTransaction(self, TransactionId: str, BackupId: Optional[str] = None,
                         ExecuteCallback: Callable[[str, str], bool] = None) -> bool:
        """
        Execute a transaction by deploying all validated files.
        
        Args:
            TransactionId: ID of the transaction
            BackupId: Optional ID of a backup created before execution
            ExecuteCallback: Function to execute file deployment
            
        Returns:
            bool: True if execution succeeded, False otherwise
        """
        # Check transaction status
        Status = self.GetTransactionStatus(TransactionId)
        if Status != TRANSACTION_STATES["VALIDATED"]:
            raise ValueError(f"Cannot execute transaction in {Status} state")
        
        # Update transaction status to in progress
        self.UpdateTransactionStatus(TransactionId, TRANSACTION_STATES["IN_PROGRESS"])
        
        # Update backup ID if provided
        if BackupId:
            self.DatabaseManager.ExecuteQuery(
                "UPDATE transactions SET backup_id = ? WHERE id = ?",
                (BackupId, TransactionId)
            )
            self.DatabaseManager.Connection.commit()
        
        Files = self.GetTransactionFiles(TransactionId)
        CompletedOperations = []
        
        try:
            for File in Files:
                FileId = File["id"]
                SourcePath = File["source_path"]
                DestinationPath = File["destination_path"]
                
                # Skip files that failed validation
                if File["validation_status"] == "FAIL":
                    continue
                
                # Record operation
                OperationId = self._RecordOperation(
                    TransactionId, FileId, "DEPLOY", SourcePath, DestinationPath
                )
                
                # Execute deployment
                Success = True
                if ExecuteCallback:
                    Success = ExecuteCallback(SourcePath, DestinationPath)
                
                if Success:
                    # Update file status
                    self.DatabaseManager.ExecuteQuery(
                        "UPDATE files SET status = ? WHERE id = ?",
                        ("DEPLOYED", FileId)
                    )
                    
                    # Update operation status
                    self.DatabaseManager.ExecuteQuery(
                        "UPDATE operations SET status = ? WHERE id = ?",
                        ("COMPLETED", OperationId)
                    )
                    
                    CompletedOperations.append(OperationId)
                else:
                    # Update operation status
                    self.DatabaseManager.ExecuteQuery(
                        "UPDATE operations SET status = ? WHERE id = ?",
                        ("FAILED", OperationId)
                    )
                    
                    raise RuntimeError(f"Failed to deploy file: {SourcePath}")
                
                self.DatabaseManager.Connection.commit()
            
            # All operations succeeded
            self.UpdateTransactionStatus(TransactionId, TRANSACTION_STATES["COMPLETED"])
            return True
            
        except Exception as E:
            # Roll back completed operations
            if CompletedOperations:
                self._RollbackOperations(CompletedOperations)
            
            self.UpdateTransactionStatus(TransactionId, TRANSACTION_STATES["FAILED"])
            raise RuntimeError(f"Transaction execution failed: {E}")
    
    def _RecordOperation(self, TransactionId: str, FileId: str, OperationType: str,
                       SourcePath: str, DestinationPath: str) -> str:
        """
        Record an operation in the database.
        
        Args:
            TransactionId: ID of the transaction
            FileId: ID of the file
            OperationType: Type of operation
            SourcePath: Source file path
            DestinationPath: Destination file path
            
        Returns:
            str: ID of the recorded operation
        """
        OperationId = str(uuid.uuid4())
        Timestamp = datetime.datetime.now().isoformat()
        
        self.DatabaseManager.ExecuteQuery(
            """
            INSERT INTO operations
            (id, transaction_id, file_id, operation_type, source_path, destination_path, 
             timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (OperationId, TransactionId, FileId, OperationType, SourcePath, 
             DestinationPath, Timestamp, "IN_PROGRESS")
        )
        
        return OperationId
    
    def _RollbackOperations(self, OperationIds: List[str], 
                          RollbackCallback: Callable[[str], bool] = None) -> bool:
        """
        Roll back completed operations.
        
        Args:
            OperationIds: List of operation IDs to roll back
            RollbackCallback: Function to execute operation rollback
            
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        for OperationId in OperationIds:
            Operation = self.DatabaseManager.ExecuteQueryFetchOne(
                """
                SELECT o.*, f.destination_path 
                FROM operations o
                JOIN files f ON o.file_id = f.id
                WHERE o.id = ?
                """,
                (OperationId,)
            )
            
            if not Operation:
                continue
            
            # Record rollback operation
            RollbackId = self._RecordOperation(
                Operation["transaction_id"], Operation["file_id"], 
                "ROLLBACK", None, Operation["destination_path"]
            )
            
            # Execute rollback
            Success = True
            if RollbackCallback:
                Success = RollbackCallback(Operation["destination_path"])
            
            if Success:
                # Update operation status
                self.DatabaseManager.ExecuteQuery(
                    "UPDATE operations SET status = ? WHERE id = ?",
                    ("ROLLED_BACK", OperationId)
                )
                
                # Update rollback operation status
                self.DatabaseManager.ExecuteQuery(
                    "UPDATE operations SET status = ? WHERE id = ?",
                    ("COMPLETED", RollbackId)
                )
            else:
                # Update rollback operation status
                self.DatabaseManager.ExecuteQuery(
                    "UPDATE operations SET status = ? WHERE id = ?",
                    ("FAILED", RollbackId)
                )
                
                return False
            
            self.DatabaseManager.Connection.commit()
        
        return True
    
    def RollbackTransaction(self, TransactionId: str, 
                          RollbackCallback: Callable[[str], bool] = None) -> bool:
        """
        Roll back a transaction.
        
        Args:
            TransactionId: ID of the transaction
            RollbackCallback: Function to execute operation rollback
            
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        # Get completed operations
        Operations = self.DatabaseManager.ExecuteQueryFetchAll(
            """
            SELECT id FROM operations 
            WHERE transaction_id = ? AND status = ? AND operation_type = ?
            """,
            (TransactionId, "COMPLETED", "DEPLOY")
        )
        
        OperationIds = [op["id"] for op in Operations]
        
        if self._RollbackOperations(OperationIds, RollbackCallback):
            self.UpdateTransactionStatus(TransactionId, TRANSACTION_STATES["ROLLED_BACK"])
            return True
        else:
            return False
    
    def CloseTransaction(self, TransactionId: str = None) -> None:
        """
        Close the specified transaction or the current transaction.
        
        Args:
            TransactionId: Optional ID of the transaction to close
        """
        if TransactionId is None:
            TransactionId = self.CurrentTransactionId
        
        if TransactionId:
            # Check if transaction is still active
            Status = self.GetTransactionStatus(TransactionId)
            if Status == TRANSACTION_STATES["IN_PROGRESS"]:
                self.UpdateTransactionStatus(TransactionId, TRANSACTION_STATES["FAILED"])
            
            if TransactionId == self.CurrentTransactionId:
                self.CurrentTransactionId = None

def Main():
    """Command-line interface for testing transaction management."""
    import argparse
    
    Parser = argparse.ArgumentParser(description="Transaction Manager CLI")
    Parser.add_argument("--create", action="store_true", help="Create a new transaction")
    Parser.add_argument("--user", default="admin", help="User ID")
    Parser.add_argument("--project", required=True, help="Project path")
    
    Args = Parser.parse_args()
    
    Manager = TransactionManager()
    
    if Args.create:
        TransactionId = Manager.CreateTransaction(Args.user, Args.project)
        print(f"Created transaction: {TransactionId}")
        print(f"Status: {Manager.GetTransactionStatus(TransactionId)}")

if __name__ == "__main__":
    Main()
