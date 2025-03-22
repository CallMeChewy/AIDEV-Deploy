# File: DeploymentEngine.py
# Path: AIDEV-Deploy/Core/DeploymentEngine.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  4:55PM
# Description: Manages file deployment operations with atomic transactions

"""
DeploymentEngine Module

This module provides functionality for deploying files within a project while
ensuring operations are atomic and can be safely rolled back in case of failure.
It coordinates with TransactionManager and BackupManager to ensure safe deployments.
"""

import os
import shutil
import hashlib
import tempfile
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from Core.DatabaseManager import DatabaseManager
from Core.TransactionManager import TransactionManager
from Core.BackupManager import BackupManager
from Core.ValidationEngine import ValidationEngine

class DeploymentEngine:
    """
    Manages file deployment operations for the AIDEV-Deploy system.
    
    This class provides methods for safely deploying files to their target locations,
    ensuring that operations are atomic and can be rolled back in case of failure.
    It coordinates with other components for validation, backup, and transaction
    management.
    
    Attributes:
        DatabaseManager: Instance of DatabaseManager for database operations
        TransactionManager: Instance of TransactionManager for transaction handling
        BackupManager: Instance of BackupManager for backup operations
        ValidationEngine: Instance of ValidationEngine for file validation
        AutoBackup: Whether to automatically create backups before deployment
        BackupType: Type of backup to create before deployment
    """
    
    def __init__(self, DbManager: Optional[DatabaseManager] = None,
               TransManager: Optional[TransactionManager] = None,
               BackupMgr: Optional[BackupManager] = None,
               ValidEngine: Optional[ValidationEngine] = None,
               AutoBackup: bool = True,
               BackupType: str = "FULL"):
        """
        Initialize the DeploymentEngine.
        
        Args:
            DbManager: Optional DatabaseManager instance. If None, creates a new instance.
            TransManager: Optional TransactionManager instance. If None, creates a new instance.
            BackupMgr: Optional BackupManager instance. If None, creates a new instance.
            ValidEngine: Optional ValidationEngine instance. If None, creates a new instance.
            AutoBackup: Whether to automatically create backups before deployment.
            BackupType: Type of backup to create before deployment.
        """
        self.DatabaseManager = DbManager or DatabaseManager()
        self.TransactionManager = TransManager or TransactionManager(self.DatabaseManager)
        self.BackupManager = BackupMgr or BackupManager(self.DatabaseManager)
        self.ValidationEngine = ValidEngine or ValidationEngine()
        self.AutoBackup = AutoBackup
        self.BackupType = BackupType
        
        # Set up logging
        self.Logger = logging.getLogger("DeploymentEngine")
    
    def DeployFiles(self, SourceFiles: List[str], DestinationFiles: List[str], 
                  ProjectPath: str, UserId: str = "admin", 
                  Description: str = None) -> Dict[str, Any]:
        """
        Deploy a list of files to their destinations within a single transaction.
        
        Args:
            SourceFiles: List of source file paths
            DestinationFiles: List of destination file paths
            ProjectPath: Root path of the project
            UserId: ID of the user performing the deployment
            Description: Optional description of the deployment
            
        Returns:
            Dict[str, Any]: Deployment results including transaction ID and status
        """
        if len(SourceFiles) != len(DestinationFiles):
            raise ValueError("Source and destination file lists must have the same length")
        
        # Create a new transaction
        TransactionId = self.TransactionManager.CreateTransaction(UserId, ProjectPath, Description)
        self.Logger.info(f"Created transaction {TransactionId} for deployment")
        
        try:
            # Add files to transaction
            for SourcePath, DestPath in zip(SourceFiles, DestinationFiles):
                # Calculate checksum for later verification
                Checksum = self._CalculateFileChecksum(SourcePath)
                
                # Add file to transaction
                FileId = self.TransactionManager.AddFileToTransaction(
                    TransactionId, SourcePath, DestPath, Checksum
                )
                self.Logger.info(f"Added file to transaction: {SourcePath} -> {DestPath}")
            
            # Validate all files in the transaction
            ValidationResults = self.ValidateFiles(TransactionId)
            if not ValidationResults["all_valid"]:
                self.Logger.warning(f"Validation failed for some files in transaction {TransactionId}")
                self.TransactionManager.CloseTransaction(TransactionId)
                return {
                    "transaction_id": TransactionId,
                    "status": "VALIDATION_FAILED",
                    "validation_results": ValidationResults
                }
            
            # Create backup if enabled
            BackupId = None
            if self.AutoBackup:
                BackupResult = self.BackupManager.CreateBackup(
                    ProjectPath, self.BackupType, UserId, 
                    f"Pre-deployment backup for transaction {TransactionId}"
                )
                BackupId = BackupResult["backup_id"]
                self.Logger.info(f"Created backup {BackupId} before deployment")
            
            # Execute the transaction (deploy files)
            self.TransactionManager.ExecuteTransaction(
                TransactionId, BackupId, self._DeployFile
            )
            
            self.Logger.info(f"Successfully executed transaction {TransactionId}")
            return {
                "transaction_id": TransactionId,
                "status": "COMPLETED",
                "backup_id": BackupId
            }
            
        except Exception as E:
            # Transaction failure
            self.Logger.error(f"Transaction {TransactionId} failed: {E}")
            
            # Make sure the transaction is properly marked as failed
            try:
                self.TransactionManager.CloseTransaction(TransactionId)
            except:
                pass
            
            return {
                "transaction_id": TransactionId,
                "status": "FAILED",
                "error": str(E)
            }
    
    def ValidateFiles(self, TransactionId: str) -> Dict[str, Any]:
        """
        Validate all files in a transaction.
        
        Args:
            TransactionId: ID of the transaction
            
        Returns:
            Dict[str, Any]: Validation results
        """
        # Get files in transaction
        Files = self.TransactionManager.GetTransactionFiles(TransactionId)
        
        AllValid = True
        Results = {
            "all_valid": True,
            "files": {}
        }
        
        for File in Files:
            FileId = File["id"]
            SourcePath = File["source_path"]
            
            # Validate the file
            ValidationResult = self.ValidationEngine.ValidateFile(SourcePath)
            Status = ValidationResult["status"]
            
            # Update overall validation status
            if Status == "FAIL":
                AllValid = False
            
            # Store results for this file
            Results["files"][FileId] = {
                "path": SourcePath,
                "status": Status,
                "errors": ValidationResult.get("errors", []),
                "warnings": ValidationResult.get("warnings", [])
            }
        
        Results["all_valid"] = AllValid
        
        # Update transaction validation status
        self.TransactionManager.ValidateTransaction(
            TransactionId, lambda path: self.ValidationEngine.ValidateFile(path)
        )
        
        return Results
    
    def _DeployFile(self, SourcePath: str, DestinationPath: str) -> bool:
        """
        Deploy a single file to its destination.
        
        This is the callback function used by TransactionManager to execute
        file deployment operations.
        
        Args:
            SourcePath: Path to the source file
            DestinationPath: Path where the file should be deployed
            
        Returns:
            bool: True if deployment was successful
        """
        try:
            # Create destination directory if it doesn't exist
            DestDir = os.path.dirname(DestinationPath)
            os.makedirs(DestDir, exist_ok=True)
            
            # If destination exists, archive it first
            if os.path.exists(DestinationPath):
                self._ArchiveExistingFile(DestinationPath)
            
            # Copy the file
            shutil.copy2(SourcePath, DestinationPath)
            
            # Verify the copy
            SourceChecksum = self._CalculateFileChecksum(SourcePath)
            DestChecksum = self._CalculateFileChecksum(DestinationPath)
            
            if SourceChecksum != DestChecksum:
                raise ValueError(f"Checksum mismatch after deployment: {DestinationPath}")
            
            self.Logger.info(f"Deployed file: {SourcePath} -> {DestinationPath}")
            return True
            
        except Exception as E:
            self.Logger.error(f"Failed to deploy file {SourcePath} to {DestinationPath}: {E}")
            return False
    
    def _ArchiveExistingFile(self, FilePath: str) -> str:
        """
        Archive an existing file before it is replaced.
        
        Args:
            FilePath: Path to the file to archive
            
        Returns:
            str: Path to the archived file
        """
        if not os.path.exists(FilePath):
            return None
        
        # Create archive directory if it doesn't exist
        ArchiveDir = os.path.join(os.path.dirname(FilePath), ".archive")
        os.makedirs(ArchiveDir, exist_ok=True)
        
        # Generate archive filename with timestamp
        Timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        FileName = os.path.basename(FilePath)
        ArchivePath = os.path.join(ArchiveDir, f"{FileName}.{Timestamp}")
        
        # Copy the file to archive
        shutil.copy2(FilePath, ArchivePath)
        
        self.Logger.info(f"Archived file: {FilePath} -> {ArchivePath}")
        return ArchivePath
    
    def _CalculateFileChecksum(self, FilePath: str) -> str:
        """
        Calculate a checksum for a file.
        
        Args:
            FilePath: Path to the file
            
        Returns:
            str: Checksum hash
        """
        if not os.path.exists(FilePath):
            return None
        
        Hasher = hashlib.sha256()
        
        with open(FilePath, 'rb') as F:
            for Chunk in iter(lambda: F.read(4096), b''):
                Hasher.update(Chunk)
        
        return Hasher.hexdigest()
    
    def RollbackDeployment(self, TransactionId: str) -> bool:
        """
        Roll back a deployment transaction.
        
        Args:
            TransactionId: ID of the transaction to roll back
            
        Returns:
            bool: True if rollback was successful
        """
        try:
            # Get transaction info
            Status = self.TransactionManager.GetTransactionStatus(TransactionId)
            
            # Only completed or failed transactions can be rolled back
            if Status not in ["COMPLETED", "FAILED"]:
                raise ValueError(f"Cannot roll back transaction in state: {Status}")
            
            # Roll back the transaction
            Success = self.TransactionManager.RollbackTransaction(
                TransactionId, self._RollbackFile
            )
            
            if Success:
                self.Logger.info(f"Successfully rolled back transaction {TransactionId}")
            else:
                self.Logger.error(f"Failed to roll back transaction {TransactionId}")
            
            return Success
            
        except Exception as E:
            self.Logger.error(f"Error during rollback of transaction {TransactionId}: {E}")
            return False
    
    def _RollbackFile(self, DestinationPath: str) -> bool:
        """
        Roll back a file deployment by restoring the original file if available.
        
        Args:
            DestinationPath: Path to the deployed file
            
        Returns:
            bool: True if rollback was successful
        """
        try:
            # Check if the file exists
            if not os.path.exists(DestinationPath):
                self.Logger.warning(f"File to roll back does not exist: {DestinationPath}")
                return True  # Nothing to roll back
            
            # Check if there's an archived version
            ArchiveDir = os.path.join(os.path.dirname(DestinationPath), ".archive")
            FileName = os.path.basename(DestinationPath)
            
            if not os.path.exists(ArchiveDir):
                # No archive, simply remove the file
                os.remove(DestinationPath)
                self.Logger.info(f"Removed file during rollback: {DestinationPath}")
                return True
            
            # Find the most recent archived version (if any)
            ArchiveFiles = []
            for File in os.listdir(ArchiveDir):
                if File.startswith(FileName + "."):
                    ArchiveFiles.append(File)
            
            if not ArchiveFiles:
                # No archived version, remove the file
                os.remove(DestinationPath)
                self.Logger.info(f"Removed file during rollback: {DestinationPath}")
                return True
            
            # Sort by timestamp (newest first)
            ArchiveFiles.sort(reverse=True)
            LatestArchive = os.path.join(ArchiveDir, ArchiveFiles[0])
            
            # Restore the file
            shutil.copy2(LatestArchive, DestinationPath)
            
            # Clean up the archive file (optional)
            os.remove(LatestArchive)
            
            self.Logger.info(f"Restored file during rollback: {LatestArchive} -> {DestinationPath}")
            return True
            
        except Exception as E:
            self.Logger.error(f"Failed to roll back file {DestinationPath}: {E}")
            return False
    
    def GetDeploymentStatus(self, TransactionId: str) -> Dict[str, Any]:
        """
        Get the status of a deployment transaction.
        
        Args:
            TransactionId: ID of the transaction
            
        Returns:
            Dict[str, Any]: Deployment status information
        """
        try:
            # Get transaction status
            Status = self.TransactionManager.GetTransactionStatus(TransactionId)
            
            # Get files in transaction
            Files = self.TransactionManager.GetTransactionFiles(TransactionId)
            
            # Get transaction info
            TransactionInfo = self.DatabaseManager.ExecuteQueryFetchOne(
                "SELECT * FROM transactions WHERE id = ?",
                (TransactionId,)
            )
            
            if not TransactionInfo:
                raise ValueError(f"Transaction not found: {TransactionId}")
            
            # Get operations
            Operations = self.DatabaseManager.ExecuteQueryFetchAll(
                "SELECT * FROM operations WHERE transaction_id = ?",
                (TransactionId,)
            )
            
            # Prepare file status information
            FileStatus = []
            for File in Files:
                FileInfo = {
                    "id": File["id"],
                    "source": File["source_path"],
                    "destination": File["destination_path"],
                    "status": File["status"],
                    "validation_status": File["validation_status"]
                }
                
                # Add operations for this file
                FileOperations = [op for op in Operations if op["file_id"] == File["id"]]
                FileInfo["operations"] = FileOperations
                
                FileStatus.append(FileInfo)
            
            # Get backup information if available
            BackupInfo = None
            if TransactionInfo["backup_id"]:
                BackupInfo = self.DatabaseManager.ExecuteQueryFetchOne(
                    "SELECT * FROM backups WHERE id = ?",
                    (TransactionInfo["backup_id"],)
                )
            
            # Build result
            Result = {
                "transaction_id": TransactionId,
                "status": Status,
                "timestamp": TransactionInfo["timestamp"],
                "user_id": TransactionInfo["user_id"],
                "project_path": TransactionInfo["project_path"],
                "description": TransactionInfo["description"],
                "backup_id": TransactionInfo["backup_id"],
                "backup_info": BackupInfo,
                "files": FileStatus
            }
            
            return Result
            
        except Exception as E:
            self.Logger.error(f"Failed to get deployment status for {TransactionId}: {E}")
            raise RuntimeError(f"Failed to get deployment status: {E}")
    
    def ListDeployments(self, ProjectPath: Optional[str] = None, 
                      UserId: Optional[str] = None, 
                      Limit: int = 10) -> List[Dict[str, Any]]:
        """
        List deployment transactions.
        
        Args:
            ProjectPath: Optional path to filter by project
            UserId: Optional user ID to filter by user
            Limit: Maximum number of transactions to return
            
        Returns:
            List[Dict[str, Any]]: List of deployment transactions
        """
        Query = "SELECT * FROM transactions"
        Parameters = []
        WhereClause = []
        
        if ProjectPath:
            WhereClause.append("project_path = ?")
            Parameters.append(ProjectPath)
        
        if UserId:
            WhereClause.append("user_id = ?")
            Parameters.append(UserId)
        
        if WhereClause:
            Query += " WHERE " + " AND ".join(WhereClause)
        
        Query += " ORDER BY timestamp DESC LIMIT ?"
        Parameters.append(Limit)
        
        Transactions = self.DatabaseManager.ExecuteQueryFetchAll(Query, tuple(Parameters))
        
        # Enhance with file counts
        for Transaction in Transactions:
            TransactionId = Transaction["id"]
            
            # Count files
            FileCount = self.DatabaseManager.ExecuteQueryFetchOne(
                "SELECT COUNT(*) as count FROM files WHERE transaction_id = ?",
                (TransactionId,)
            )
            Transaction["file_count"] = FileCount["count"] if FileCount else 0
            
            # Count successful operations
            SuccessCount = self.DatabaseManager.ExecuteQueryFetchOne(
                "SELECT COUNT(*) as count FROM operations WHERE transaction_id = ? AND status = ?",
                (TransactionId, "COMPLETED")
            )
            Transaction["success_count"] = SuccessCount["count"] if SuccessCount else 0
        
        return Transactions

def Main():
    """Command-line interface for deployment operations."""
    import argparse
    
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy Deployment Engine")
    Parser.add_argument("--deploy", action="store_true", help="Deploy files")
    Parser.add_argument("--rollback", help="Roll back a transaction by ID")
    Parser.add_argument("--status", help="Get deployment status by transaction ID")
    Parser.add_argument("--list", action="store_true", help="List recent deployments")
    Parser.add_argument("--source", nargs="+", help="Source file paths")
    Parser.add_argument("--dest", nargs="+", help="Destination file paths")
    Parser.add_argument("--project", required=True, help="Project path")
    Parser.add_argument("--user", default="admin", help="User ID")
    Parser.add_argument("--nobackup", action="store_true", help="Disable automatic backup")
    
    Args = Parser.parse_args()
    
    # Create deployment engine
    Engine = DeploymentEngine(AutoBackup=not Args.nobackup)
    
    try:
        if Args.deploy:
            if not Args.source or not Args.dest:
                print("Error: --source and --dest are required for deployment")
                return 1
            
            if len(Args.source) != len(Args.dest):
                print("Error: Number of source and destination files must match")
                return 1
            
            Result = Engine.DeployFiles(Args.source, Args.dest, Args.project, Args.user)
            
            print(f"Deployment status: {Result['status']}")
            print(f"Transaction ID: {Result['transaction_id']}")
            
            if Result['status'] == "VALIDATION_FAILED":
                print("\nValidation issues:")
                for FileId, FileInfo in Result["validation_results"]["files"].items():
                    if FileInfo["status"] != "PASS":
                        print(f"  File: {FileInfo['path']}")
                        print(f"  Status: {FileInfo['status']}")
                        
                        if FileInfo["errors"]:
                            print("  Errors:")
                            for Error in FileInfo["errors"]:
                                print(f"    Line {Error['line']}: {Error['message']}")
                        
                        if FileInfo["warnings"]:
                            print("  Warnings:")
                            for Warning in FileInfo["warnings"]:
                                print(f"    Line {Warning['line']}: {Warning['message']}")
                        
                        print()
            
        elif Args.rollback:
            Result = Engine.RollbackDeployment(Args.rollback)
            print(f"Rollback {'successful' if Result else 'failed'}")
            
        elif Args.status:
            Status = Engine.GetDeploymentStatus(Args.status)
            print(f"Transaction: {Status['transaction_id']}")
            print(f"Status: {Status['status']}")
            print(f"Time: {Status['timestamp']}")
            print(f"User: {Status['user_id']}")
            print(f"Project: {Status['project_path']}")
            
            if Status['backup_id']:
                print(f"Backup: {Status['backup_id']}")
            
            print(f"\nFiles ({len(Status['files'])}):")
            for File in Status['files']:
                print(f"  Source: {File['source']}")
                print(f"  Destination: {File['destination']}")
                print(f"  Status: {File['status']}")
                print(f"  Validation: {File['validation_status']}")
                print()
            
        elif Args.list:
            Deployments = Engine.ListDeployments(Args.project, Args.user)
            
            if not Deployments:
                print("No deployments found")
            else:
                print(f"Found {len(Deployments)} deployments:")
                for Deployment in Deployments:
                    print(f"  ID: {Deployment['id']}")
                    print(f"  Time: {Deployment['timestamp']}")
                    print(f"  Status: {Deployment['status']}")
                    print(f"  Files: {Deployment['file_count']}")
                    print(f"  Successful Operations: {Deployment['success_count']}")
                    print()
            
        else:
            print("No action specified. Use --help for usage information.")
    
    except Exception as E:
        print(f"Error: {E}")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(Main())
