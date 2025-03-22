# File: BackupManager.py
# Path: AIDEV-Deploy/Core/BackupManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  4:45PM
# Description: Manages project backups for safe deployment operations

"""
BackupManager Module

This module provides functionality for creating, managing, and restoring
project backups before deployment operations. It ensures that projects
can be safely rolled back in case of deployment failures.
"""

import os
import shutil
import tarfile
import tempfile
import hashlib
import datetime
import uuid
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

from Core.DatabaseManager import DatabaseManager

class BackupManager:
    """
    Manages project backups for the AIDEV-Deploy system.
    
    This class provides methods for creating, verifying, and restoring
    project backups to ensure safe deployment operations. It uses
    cryptographic validation to ensure backup integrity.
    
    Attributes:
        DatabaseManager: Instance of DatabaseManager for database operations
        BackupLocation: Directory where backups are stored
        DefaultBackupType: Default type of backup to create
        Compression: Whether to compress backups by default
    """
    
    # Backup types
    BACKUP_TYPES = {
        "FULL": "FULL",       # Complete project backup
        "PARTIAL": "PARTIAL", # Only files affected by deployment
        "CONFIG": "CONFIG"    # Configuration files only
    }
    
    def __init__(self, DbManager: Optional[DatabaseManager] = None, 
               BackupLocation: Optional[str] = None,
               DefaultBackupType: str = "FULL",
               Compression: bool = True):
        """
        Initialize the BackupManager.
        
        Args:
            DbManager: Optional DatabaseManager instance. If None, creates a new instance.
            BackupLocation: Directory where backups are stored. If None, uses default.
            DefaultBackupType: Default type of backup to create.
            Compression: Whether to compress backups by default.
        """
        self.DatabaseManager = DbManager or DatabaseManager()
        self.BackupLocation = BackupLocation or self._GetDefaultBackupLocation()
        self.DefaultBackupType = DefaultBackupType
        self.Compression = Compression
        
        # Ensure backup directory exists
        os.makedirs(self.BackupLocation, exist_ok=True)
        
        # Set up logging
        self.Logger = logging.getLogger("BackupManager")
    
    def _GetDefaultBackupLocation(self) -> str:
        """
        Get the default backup location.
        
        Returns:
            str: Path to the default backup location
        """
        BackupDir = os.path.join(str(Path.home()), ".AIDEV-Deploy", "backups")
        return BackupDir
    
    def CreateBackup(self, ProjectPath: str, BackupType: str = None, 
                  UserId: str = "admin", Description: str = None,
                  FilesToBackup: List[str] = None) -> Dict[str, Any]:
        """
        Create a backup of a project.
        
        Args:
            ProjectPath: Path to the project to back up
            BackupType: Type of backup to create (FULL, PARTIAL, CONFIG)
            UserId: ID of the user creating the backup
            Description: Optional description of the backup
            FilesToBackup: Optional list of specific files to back up
            
        Returns:
            Dict[str, Any]: Backup information including ID and path
        """
        if not os.path.exists(ProjectPath):
            raise ValueError(f"Project path does not exist: {ProjectPath}")
        
        # Use default backup type if none specified
        BackupType = BackupType or self.DefaultBackupType
        
        # Validate backup type
        if BackupType not in self.BACKUP_TYPES.values():
            raise ValueError(f"Invalid backup type: {BackupType}")
        
        # Generate backup ID and timestamp
        BackupId = str(uuid.uuid4())
        Timestamp = datetime.datetime.now()
        TimestampStr = Timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create backup name
        ProjectName = os.path.basename(os.path.normpath(ProjectPath))
        BackupName = f"{ProjectName}_{TimestampStr}_{BackupType.lower()}"
        BackupDirPath = os.path.join(self.BackupLocation, BackupName)
        
        # Create temporary directory for the backup
        TempBackupDir = os.path.join(tempfile.gettempdir(), BackupName)
        os.makedirs(TempBackupDir, exist_ok=True)
        
        # Determine files to back up
        FilesToBackup = FilesToBackup or self._GetFilesToBackup(ProjectPath, BackupType)
        
        # Process files
        self.Logger.info(f"Creating {BackupType} backup of {ProjectPath}")
        self.Logger.info(f"Backing up {len(FilesToBackup)} files")
        
        FileCount = 0
        for FilePath in FilesToBackup:
            # Get relative path for the file
            RelPath = os.path.relpath(FilePath, ProjectPath)
            DestPath = os.path.join(TempBackupDir, RelPath)
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(DestPath), exist_ok=True)
            
            # Copy file
            try:
                shutil.copy2(FilePath, DestPath)
                FileCount += 1
            except Exception as E:
                self.Logger.warning(f"Failed to backup file {FilePath}: {E}")
        
        # Create metadata
        Metadata = {
            "backup_id": BackupId,
            "project_name": ProjectName,
            "project_path": ProjectPath,
            "backup_type": BackupType,
            "timestamp": Timestamp.isoformat(),
            "file_count": FileCount,
            "user_id": UserId,
            "description": Description
        }
        
        # Write metadata to the backup
        MetadataPath = os.path.join(TempBackupDir, "metadata.json")
        with open(MetadataPath, 'w') as F:
            json.dump(Metadata, F, indent=2)
        
        # Calculate directory size and checksum
        Size = self._CalculateDirectorySize(TempBackupDir)
        Checksum = self._CalculateDirectoryChecksum(TempBackupDir)
        
        # Update metadata with size and checksum
        Metadata["size"] = Size
        Metadata["checksum"] = Checksum
        
        # Update the metadata file with complete information
        with open(MetadataPath, 'w') as F:
            json.dump(Metadata, F, indent=2)
        
        # Create final backup (compressed or not)
        FinalBackupPath = ""
        if self.Compression:
            # Create compressed archive
            ArchivePath = f"{BackupDirPath}.tar.gz"
            with tarfile.open(ArchivePath, "w:gz") as Tar:
                Tar.add(TempBackupDir, arcname=os.path.basename(TempBackupDir))
            FinalBackupPath = ArchivePath
        else:
            # Move the directory as-is
            shutil.move(TempBackupDir, BackupDirPath)
            FinalBackupPath = BackupDirPath
        
        # Store backup record in database
        self._StoreBackupRecord(BackupId, Metadata, FinalBackupPath)
        
        # Clean up temp directory if it still exists
        if os.path.exists(TempBackupDir):
            shutil.rmtree(TempBackupDir)
        
        self.Logger.info(f"Backup created: {FinalBackupPath}")
        
        # Return backup information
        return {
            "backup_id": BackupId,
            "path": FinalBackupPath,
            "timestamp": Timestamp.isoformat(),
            "type": BackupType,
            "size": Size,
            "file_count": FileCount,
            "checksum": Checksum
        }
    
    def _GetFilesToBackup(self, ProjectPath: str, BackupType: str) -> List[str]:
        """
        Determine which files to back up based on backup type.
        
        Args:
            ProjectPath: Path to the project
            BackupType: Type of backup to create
            
        Returns:
            List[str]: List of file paths to back up
        """
        FilesToBackup = []
        
        # For FULL backup, include all files
        if BackupType == self.BACKUP_TYPES["FULL"]:
            for Root, _, Files in os.walk(ProjectPath):
                # Skip .git directory and other hidden directories
                if os.path.basename(Root).startswith('.'):
                    continue
                
                # Skip .Exclude directory as specified
                if ".Exclude" in Root.split(os.path.sep):
                    continue
                
                for File in Files:
                    # Skip hidden files
                    if File.startswith('.'):
                        continue
                    
                    FilePath = os.path.join(Root, File)
                    FilesToBackup.append(FilePath)
        
        # For CONFIG backup, include only configuration files
        elif BackupType == self.BACKUP_TYPES["CONFIG"]:
            ConfigPatterns = ["*.config", "*.ini", "*.yaml", "*.yml", "*.json", 
                           "*.xml", "*.conf", "config*.*"]
            
            for Root, _, Files in os.walk(ProjectPath):
                for File in Files:
                    FilePath = os.path.join(Root, File)
                    
                    # Check if file matches config patterns
                    for Pattern in ConfigPatterns:
                        if self._MatchesPattern(File, Pattern):
                            FilesToBackup.append(FilePath)
                            break
        
        # For PARTIAL backup, this would typically be specific files
        # In this case, we'll default to a reasonable subset of files
        elif BackupType == self.BACKUP_TYPES["PARTIAL"]:
            # Add Python files by default as the most likely deployment targets
            for Root, _, Files in os.walk(ProjectPath):
                for File in Files:
                    FilePath = os.path.join(Root, File)
                    if File.endswith('.py'):
                        FilesToBackup.append(FilePath)
        
        return FilesToBackup
    
    def _MatchesPattern(self, Filename: str, Pattern: str) -> bool:
        """
        Check if a filename matches a pattern.
        
        Args:
            Filename: Filename to check
            Pattern: Pattern to match against (* is wildcard)
            
        Returns:
            bool: True if file matches pattern
        """
        # Simple wildcard matching
        if Pattern.startswith("*") and Pattern.endswith("*"):
            # *text*
            Return = Pattern[1:-1] in Filename
        elif Pattern.startswith("*"):
            # *.extension
            Return = Filename.endswith(Pattern[1:])
        elif Pattern.endswith("*"):
            # prefix*
            Return = Filename.startswith(Pattern[:-1])
        else:
            # exact match
            Return = Filename == Pattern
        
        return Return
    
    def _CalculateDirectorySize(self, DirPath: str) -> int:
        """
        Calculate the total size of a directory in bytes.
        
        Args:
            DirPath: Path to the directory
            
        Returns:
            int: Size in bytes
        """
        TotalSize = 0
        for Root, _, Files in os.walk(DirPath):
            for File in Files:
                FilePath = os.path.join(Root, File)
                TotalSize += os.path.getsize(FilePath)
        
        return TotalSize
    
    def _CalculateDirectoryChecksum(self, DirPath: str) -> str:
        """
        Calculate a checksum for a directory's contents.
        
        This creates a hash of all file contents and paths to ensure
        directory integrity can be verified.
        
        Args:
            DirPath: Path to the directory
            
        Returns:
            str: Checksum hash
        """
        Hasher = hashlib.sha256()
        
        # Get a sorted list of all files
        AllFiles = []
        for Root, _, Files in os.walk(DirPath):
            for File in Files:
                FilePath = os.path.join(Root, File)
                RelPath = os.path.relpath(FilePath, DirPath)
                AllFiles.append((RelPath, FilePath))
        
        # Sort by relative path for consistent checksums
        AllFiles.sort()
        
        # Process each file
        for RelPath, FilePath in AllFiles:
            # Add the relative path to the hash
            Hasher.update(RelPath.encode())
            
            # Read and hash file content in chunks to handle large files
            with open(FilePath, 'rb') as F:
                for Chunk in iter(lambda: F.read(4096), b''):
                    Hasher.update(Chunk)
        
        return Hasher.hexdigest()
    
    def _StoreBackupRecord(self, BackupId: str, Metadata: Dict[str, Any], BackupPath: str) -> None:
        """
        Store a backup record in the database.
        
        Args:
            BackupId: Unique ID for the backup
            Metadata: Backup metadata
            BackupPath: Path to the backup file or directory
        """
        try:
            # Insert into backups table
            self.DatabaseManager.ExecuteQuery(
                """
                INSERT INTO backups 
                (id, timestamp, project_path, backup_path, backup_type, 
                 size, file_count, user_id, verified, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    BackupId,
                    Metadata["timestamp"],
                    Metadata["project_path"],
                    BackupPath,
                    Metadata["backup_type"],
                    Metadata["size"],
                    Metadata["file_count"],
                    Metadata["user_id"],
                    False,  # Not verified initially
                    Metadata["checksum"]
                )
            )
            
            self.DatabaseManager.Connection.commit()
            
        except Exception as E:
            self.Logger.error(f"Failed to store backup record: {E}")
            raise RuntimeError(f"Failed to store backup record: {E}")
    
    def VerifyBackup(self, BackupId: str) -> bool:
        """
        Verify the integrity of a backup.
        
        Args:
            BackupId: ID of the backup to verify
            
        Returns:
            bool: True if backup is valid
        """
        # Get backup record from database
        BackupRecord = self.DatabaseManager.ExecuteQueryFetchOne(
            "SELECT * FROM backups WHERE id = ?",
            (BackupId,)
        )
        
        if not BackupRecord:
            raise ValueError(f"Backup not found: {BackupId}")
        
        BackupPath = BackupRecord["backup_path"]
        StoredChecksum = BackupRecord["checksum"]
        
        # Check if backup exists
        if not os.path.exists(BackupPath):
            self.Logger.error(f"Backup file not found: {BackupPath}")
            return False
        
        # Extract backup to temp directory if it's compressed
        TempDir = None
        DirectoryToVerify = BackupPath
        
        try:
            if BackupPath.endswith(".tar.gz"):
                TempDir = tempfile.mkdtemp()
                with tarfile.open(BackupPath, "r:gz") as Tar:
                    Tar.extractall(path=TempDir)
                
                # Get the extracted directory (should be the only one)
                Subdirs = [d for d in os.listdir(TempDir) if os.path.isdir(os.path.join(TempDir, d))]
                if Subdirs:
                    DirectoryToVerify = os.path.join(TempDir, Subdirs[0])
                else:
                    DirectoryToVerify = TempDir
            
            # Calculate checksum of the extracted content
            CalculatedChecksum = self._CalculateDirectoryChecksum(DirectoryToVerify)
            
            # Compare checksums
            if CalculatedChecksum != StoredChecksum:
                self.Logger.error(f"Backup checksum mismatch: {BackupId}")
                return False
            
            # Update verification status in database
            self.DatabaseManager.ExecuteQuery(
                "UPDATE backups SET verified = ? WHERE id = ?",
                (True, BackupId)
            )
            self.DatabaseManager.Connection.commit()
            
            self.Logger.info(f"Backup verified successfully: {BackupId}")
            return True
            
        except Exception as E:
            self.Logger.error(f"Backup verification failed: {E}")
            return False
            
        finally:
            # Clean up temp directory if it was created
            if TempDir and os.path.exists(TempDir):
                shutil.rmtree(TempDir)
    
    def ListBackups(self, ProjectPath: Optional[str] = None, Limit: int = 10) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            ProjectPath: Optional path to filter backups by project
            Limit: Maximum number of backups to return
            
        Returns:
            List[Dict[str, Any]]: List of backup records
        """
        Query = "SELECT * FROM backups"
        Parameters = ()
        
        if ProjectPath:
            Query += " WHERE project_path = ?"
            Parameters = (ProjectPath,)
        
        Query += " ORDER BY timestamp DESC LIMIT ?"
        Parameters = Parameters + (Limit,)
        
        Backups = self.DatabaseManager.ExecuteQueryFetchAll(Query, Parameters)
        return Backups
    
    def RestoreFromBackup(self, BackupId: str, RestorePath: Optional[str] = None) -> bool:
        """
        Restore a project from a backup.
        
        Args:
            BackupId: ID of the backup to restore
            RestorePath: Optional path to restore to (defaults to original path)
            
        Returns:
            bool: True if restoration was successful
        """
        # Get backup record from database
        BackupRecord = self.DatabaseManager.ExecuteQueryFetchOne(
            "SELECT * FROM backups WHERE id = ?",
            (BackupId,)
        )
        
        if not BackupRecord:
            raise ValueError(f"Backup not found: {BackupId}")
        
        BackupPath = BackupRecord["backup_path"]
        OriginalPath = BackupRecord["project_path"]
        
        # Determine restore path
        RestorePath = RestorePath or OriginalPath
        
        # Verify backup first
        if not self.VerifyBackup(BackupId):
            raise ValueError(f"Backup verification failed: {BackupId}")
        
        # Extract backup to temp directory if it's compressed
        TempDir = None
        
        try:
            if BackupPath.endswith(".tar.gz"):
                # Extract to temporary directory
                TempDir = tempfile.mkdtemp()
                with tarfile.open(BackupPath, "r:gz") as Tar:
                    Tar.extractall(path=TempDir)
                
                # Get the extracted directory (should be the only one)
                Subdirs = [d for d in os.listdir(TempDir) if os.path.isdir(os.path.join(TempDir, d))]
                if Subdirs:
                    ExtractedDir = os.path.join(TempDir, Subdirs[0])
                else:
                    ExtractedDir = TempDir
                
                # Copy content to restore path
                self._CopyDirectoryContents(ExtractedDir, RestorePath)
            else:
                # Backup is an uncompressed directory, copy directly
                self._CopyDirectoryContents(BackupPath, RestorePath)
            
            self.Logger.info(f"Restored backup {BackupId} to {RestorePath}")
            return True
            
        except Exception as E:
            self.Logger.error(f"Backup restoration failed: {E}")
            raise RuntimeError(f"Backup restoration failed: {E}")
            
        finally:
            # Clean up temp directory if it was created
            if TempDir and os.path.exists(TempDir):
                shutil.rmtree(TempDir)
    
    def _CopyDirectoryContents(self, SourceDir: str, DestDir: str) -> None:
        """
        Copy the contents of a directory to another directory.
        
        Args:
            SourceDir: Source directory path
            DestDir: Destination directory path
        """
        # Ensure destination directory exists
        os.makedirs(DestDir, exist_ok=True)
        
        # Copy content
        for Item in os.listdir(SourceDir):
            # Skip metadata.json
            if Item == "metadata.json":
                continue
            
            SourcePath = os.path.join(SourceDir, Item)
            DestPath = os.path.join(DestDir, Item)
            
            if os.path.isdir(SourcePath):
                # Create directory if it doesn't exist
                if not os.path.exists(DestPath):
                    os.makedirs(DestPath)
                # Recursively copy contents
                self._CopyDirectoryContents(SourcePath, DestPath)
            else:
                # Copy file
                shutil.copy2(SourcePath, DestPath)
    
    def DeleteBackup(self, BackupId: str) -> bool:
        """
        Delete a backup.
        
        Args:
            BackupId: ID of the backup to delete
            
        Returns:
            bool: True if deletion was successful
        """
        # Get backup record from database
        BackupRecord = self.DatabaseManager.ExecuteQueryFetchOne(
            "SELECT * FROM backups WHERE id = ?",
            (BackupId,)
        )
        
        if not BackupRecord:
            raise ValueError(f"Backup not found: {BackupId}")
        
        BackupPath = BackupRecord["backup_path"]
        
        try:
            # Delete backup file/directory
            if os.path.exists(BackupPath):
                if os.path.isdir(BackupPath):
                    shutil.rmtree(BackupPath)
                else:
                    os.remove(BackupPath)
            
            # Delete database record
            self.DatabaseManager.ExecuteQuery(
                "DELETE FROM backups WHERE id = ?",
                (BackupId,)
            )
            self.DatabaseManager.Connection.commit()
            
            self.Logger.info(f"Deleted backup: {BackupId}")
            return True
            
        except Exception as E:
            self.Logger.error(f"Failed to delete backup: {E}")
            return False
    
    def GetFileFromBackup(self, BackupId: str, RelativeFilePath: str) -> Optional[bytes]:
        """
        Extract a specific file from a backup.
        
        Args:
            BackupId: ID of the backup
            RelativeFilePath: Path to the file relative to the project root
            
        Returns:
            Optional[bytes]: File content or None if not found
        """
        # Get backup record from database
        BackupRecord = self.DatabaseManager.ExecuteQueryFetchOne(
            "SELECT * FROM backups WHERE id = ?",
            (BackupId,)
        )
        
        if not BackupRecord:
            raise ValueError(f"Backup not found: {BackupId}")
        
        BackupPath = BackupRecord["backup_path"]
        
        # Normalize the relative path (remove leading slash if present)
        if RelativeFilePath.startswith('/'):
            RelativeFilePath = RelativeFilePath[1:]
        
        # Handle compressed backup
        if BackupPath.endswith(".tar.gz"):
            try:
                with tarfile.open(BackupPath, "r:gz") as Tar:
                    # Get the name of the root directory in the archive
                    RootDir = Tar.getnames()[0].split('/')[0]
                    
                    # Full path within the archive
                    ArchivePath = os.path.join(RootDir, RelativeFilePath)
                    
                    # Check if the file exists in the archive
                    try:
                        File = Tar.extractfile(ArchivePath)
                        if File:
                            return File.read()
                    except KeyError:
                        pass
                    
                    return None
            except Exception as E:
                self.Logger.error(f"Failed to extract file from backup: {E}")
                return None
        else:
            # Uncompressed backup
            FilePath = os.path.join(BackupPath, RelativeFilePath)
            if os.path.exists(FilePath) and os.path.isfile(FilePath):
                with open(FilePath, 'rb') as F:
                    return F.read()
            
            return None

def Main():
    """Command-line interface for backup management."""
    import argparse
    
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy Backup Manager")
    Parser.add_argument("--create", action="store_true", help="Create a backup")
    Parser.add_argument("--verify", help="Verify a backup by ID")
    Parser.add_argument("--restore", help="Restore a backup by ID")
    Parser.add_argument("--list", action="store_true", help="List available backups")
    Parser.add_argument("--delete", help="Delete a backup by ID")
    Parser.add_argument("--project", help="Project path")
    Parser.add_argument("--type", choices=["FULL", "PARTIAL", "CONFIG"], 
                     default="FULL", help="Backup type")
    Parser.add_argument("--output", help="Restore output path")
    
    Args = Parser.parse_args()
    
    # Create backup manager
    Manager = BackupManager()
    
    try:
        if Args.create:
            if not Args.project:
                print("Error: --project is required for backup creation")
                return 1
            
            Backup = Manager.CreateBackup(Args.project, Args.type)
            print(f"Backup created: {Backup['backup_id']}")
            print(f"Path: {Backup['path']}")
            print(f"Size: {Backup['size']} bytes")
            print(f"Files: {Backup['file_count']}")
            
        elif Args.verify:
            Result = Manager.VerifyBackup(Args.verify)
            print(f"Backup verification {'successful' if Result else 'failed'}")
            
        elif Args.restore:
            if not Args.project and not Args.output:
                print("Error: Either --project or --output is required for restore")
                return 1
                
            Result = Manager.RestoreFromBackup(Args.restore, Args.output)
            print(f"Restore {'successful' if Result else 'failed'}")
            
        elif Args.list:
            Backups = Manager.ListBackups(Args.project)
            if not Backups:
                print("No backups found")
            else:
                print(f"Found {len(Backups)} backups:")
                for Backup in Backups:
                    print(f"  ID: {Backup['id']}")
                    print(f"  Date: {Backup['timestamp']}")
                    print(f"  Type: {Backup['backup_type']}")
                    print(f"  Project: {Backup['project_path']}")
                    print(f"  Verified: {'Yes' if Backup['verified'] else 'No'}")
                    print()
                    
        elif Args.delete:
            Result = Manager.DeleteBackup(Args.delete)
            print(f"Backup deletion {'successful' if Result else 'failed'}")
            
        else:
            print("No action specified. Use --help for usage information.")
    
    except Exception as E:
        print(f"Error: {E}")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(Main())
