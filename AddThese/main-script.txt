#!/usr/bin/env python
# File: Main.py
# Path: AIDEV-Deploy/Main.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:25PM
# Description: Main entry point for AIDEV-Deploy application

"""
AIDEV-Deploy: File Deployment System

This module serves as the main entry point for the AIDEV-Deploy application,
initializing components and starting either the CLI or GUI interface.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
ProjectRoot = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ProjectRoot)

from Utils.ConfigManager import ConfigManager
from Utils.LoggingManager import SetupLogging
from Core.DatabaseManager import DatabaseManager
from Core.TransactionManager import TransactionManager
from Core.BackupManager import BackupManager
from Core.ValidationEngine import ValidationEngine
from Core.DeploymentEngine import DeploymentEngine

def InitializeComponents(ConfigPath: str = None) -> dict:
    """
    Initialize all core components.
    
    Args:
        ConfigPath: Optional path to configuration file
        
    Returns:
        dict: Dictionary of initialized components
    """
    # Initialize configuration
    ConfigMgr = ConfigManager(ConfigPath)
    
    # Set up logging
    LoggingMgr = SetupLogging(ConfigPath=ConfigPath)
    Logger = LoggingMgr.GetLogger("Main")
    
    # Initialize database
    Logger.info("Initializing database...")
    DbManager = DatabaseManager()
    DbManager.InitializeDatabase()
    
    # Initialize transaction manager
    Logger.info("Initializing transaction manager...")
    TransManager = TransactionManager(DbManager)
    
    # Initialize backup manager
    Logger.info("Initializing backup manager...")
    BackupMgr = BackupManager(DbManager)
    
    # Initialize validation engine
    Logger.info("Initializing validation engine...")
    StandardVersion = ConfigMgr.GetConfigValue("validation.standards", "1.6")
    ValidEngine = ValidationEngine(StandardVersion)
    
    # Initialize deployment engine
    Logger.info("Initializing deployment engine...")
    DeployEngine = DeploymentEngine(
        DbManager, 
        TransManager, 
        BackupMgr,
        ValidEngine,
        ConfigMgr.GetConfigValue("backup.auto_backup", True)
    )
    
    Logger.info("All components initialized successfully")
    
    return {
        "config_manager": ConfigMgr,
        "logging_manager": LoggingMgr,
        "database_manager": DbManager,
        "transaction_manager": TransManager,
        "backup_manager": BackupMgr,
        "validation_engine": ValidEngine,
        "deployment_engine": DeployEngine
    }

def RunCLI(Components: dict) -> int:
    """
    Run the command-line interface.
    
    Args:
        Components: Dictionary of initialized components
        
    Returns:
        int: Exit code
    """
    Logger = Components["logging_manager"].GetLogger("CLI")
    Logger.info("Starting CLI interface")
    
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy: File Deployment System")
    Subparsers = Parser.add_subparsers(dest="command", help="Command to execute")
    
    # Deploy command
    DeployParser = Subparsers.add_parser("deploy", help="Deploy files")
    DeployParser.add_argument("--source", nargs="+", required=True, help="Source file paths")
    DeployParser.add_argument("--dest", nargs="+", required=True, help="Destination file paths")
    DeployParser.add_argument("--project", required=True, help="Project path")
    DeployParser.add_argument("--user", default="admin", help="User ID")
    DeployParser.add_argument("--description", help="Deployment description")
    DeployParser.add_argument("--nobackup", action="store_true", help="Disable automatic backup")
    
    # Validate command
    ValidateParser = Subparsers.add_parser("validate", help="Validate files")
    ValidateParser.add_argument("files", nargs="+", help="Files to validate")
    ValidateParser.add_argument("--standard", help="Standard version")
    
    # Backup command
    BackupParser = Subparsers.add_parser("backup", help="Create a backup")
    BackupParser.add_argument("--project", required=True, help="Project path")
    BackupParser.add_argument("--type", choices=["FULL", "PARTIAL", "CONFIG"], default="FULL", 
                          help="Backup type")
    
    # Restore command
    RestoreParser = Subparsers.add_parser("restore", help="Restore from backup")
    RestoreParser.add_argument("backup_id", help="Backup ID")
    RestoreParser.add_argument("--output", help="Restore output path")
    
    # List command
    ListParser = Subparsers.add_parser("list", help="List entities")
    ListParser.add_argument("entity", choices=["backups", "deployments"], help="Entity type to list")
    ListParser.add_argument("--project", help="Project path")
    ListParser.add_argument("--limit", type=int, default=10, help="Maximum number of items to show")
    
    # Initialize command
    InitParser = Subparsers.add_parser("init", help="Initialize the database")
    
    # Config command
    ConfigParser = Subparsers.add_parser("config", help="Manage configuration")
    ConfigParser.add_argument("--get", help="Get a configuration value")
    ConfigParser.add_argument("--set", help="Set a configuration value")
    ConfigParser.add_argument("--value", help="Value to set (used with --set)")
    ConfigParser.add_argument("--reset", action="store_true", help="Reset configuration to defaults")
    ConfigParser.add_argument("--list", action="store_true", help="List all configuration keys")
    ConfigParser.add_argument("--setup", action="store_true", help="Run interactive setup")
    
    # Parse args and handle commands
    Args = Parser.parse_args()
    
    try:
        if Args.command == "deploy":
            if len(Args.source) != len(Args.dest):
                print("Error: Number of source and destination files must match")
                return 1
            
            # Set auto_backup based on args
            Components["deployment_engine"].AutoBackup = not Args.nobackup
            
            Result = Components["deployment_engine"].DeployFiles(
                Args.source, Args.dest, Args.project, Args.user, Args.description
            )
            
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
        
        elif Args.command == "validate":
            ValidEngine = Components["validation_engine"]
            
            # Set standard version if provided
            if Args.standard:
                ValidEngine.StandardVersion = Args.standard
            
            for FilePath in Args.files:
                print(f"Validating: {FilePath}")
                Result = ValidEngine.ValidateFile(FilePath)
                
                print(f"Status: {Result['status']}")
                
                if Result["errors"]:
                    print("Errors:")
                    for Error in Result["errors"]:
                        print(f"  Line {Error['line']}: {Error['message']}")
                
                if Result["warnings"]:
                    print("Warnings:")
                    for Warning in Result["warnings"]:
                        print(f"  Line {Warning['line']}: {Warning['message']}")
                
                print()
        
        elif Args.command == "backup":
            BackupMgr = Components["backup_manager"]
            
            Result = BackupMgr.CreateBackup(Args.project, Args.type)
            
            print(f"Backup created: {Result['backup_id']}")
            print(f"Path: {Result['path']}")
            print(f"Size: {Result['size']} bytes")
            print(f"Files: {Result['file_count']}")
        
        elif Args.command == "restore":
            BackupMgr = Components["backup_manager"]
            
            Result = BackupMgr.RestoreFromBackup(Args.backup_id, Args.output)
            
            print(f"Restore {'successful' if Result else 'failed'}")
        
        elif Args.command == "list":
            if Args.entity == "backups":
                Backups = Components["backup_manager"].ListBackups(Args.project, Args.limit)
                
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
            
            elif Args.entity == "deployments":
                Deployments = Components["deployment_engine"].ListDeployments(
                    Args.project, limit=Args.limit
                )
                
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
        
        elif Args.command == "init":
            Components["database_manager"].InitializeDatabase()
            print("Database initialized successfully")
        
        elif Args.command == "config":
            ConfigMgr = Components["config_manager"]
            
            if Args.setup:
                from Utils.ConfigManager import SetupInteractive
                SetupInteractive()
                
            elif Args.get:
                Value = ConfigMgr.GetConfigValue(Args.get)
                print(f"{Args.get}: {Value}")
                
            elif Args.set:
                if Args.value is None:
                    print("Error: --value is required with --set")
                    return 1
                
                ConfigMgr.SetConfigValue(Args.set, Args.value)
                ConfigMgr.SaveConfig()
                print(f"Set {Args.set} to {Args.value}")
                
            elif Args.reset:
                ConfigMgr.ResetToDefaults()
                print("Configuration reset to defaults")
                
            elif Args.list:
                Keys = ConfigMgr.GetConfigKeys()
                for Key in sorted(Keys):
                    Value = ConfigMgr.GetConfigValue(Key)
                    print(f"{Key}: {Value}")
        
        else:
            Parser.print_help()
        
        return 0
        
    except Exception as E:
        Logger.error(f"Error: {E}", exc_info=True)
        print(f"Error: {E}")
        return 1

def RunGUI():
    """
    Run the graphical user interface.
    
    Returns:
        int: Exit code
    """
    print("GUI mode not yet implemented.")
    print("Please use the CLI mode for now.")
    return 1

def PrintBanner():
    """Print the application banner."""
    Banner = r"""
     _    ___ ___  _______     __    ___              _       
    / \  |_ _|   \| ____\ \   / /   |   \ ___ _ __  | | ___  _   _
   / _ \  | || |) |  _|  \ \ / /    | |) / -_) '_ \ | |/ _ \| | | |
  / ___ \ | ||  __/| |___  \ V /    |___/\___| .__/ | | (_) | |_| |
 /_/   \_\___|_|   |_____|  \_/             |_|    |_|\___/ \__, |
                                                            |___/ 
 
 File Deployment System with Validation and Rollback
 Version 0.1.0
 Standard: AIDEV-PascalCase-1.6
    """
    print(Banner)
    print()

def Main():
    """
    Main entry point for the application.
    
    Returns:
        int: Exit code
    """
    # Display banner
    PrintBanner()
    
    # Parse command line arguments
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy: File Deployment System")
    Parser.add_argument("--config", help="Path to configuration file")
    Parser.add_argument("--gui", action="store_true", help="Start in GUI mode")
    
    # Parse args before command subparsers
    Args, _ = Parser.parse_known_args()
    
    try:
        # Initialize components
        Components = InitializeComponents(Args.config)
        
        # Run in GUI or CLI mode
        if Args.gui:
            return RunGUI()
        else:
            return RunCLI(Components)
            
    except Exception as E:
        print(f"Initialization error: {E}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(Main())
