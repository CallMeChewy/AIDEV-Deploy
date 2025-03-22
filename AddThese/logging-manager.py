# File: LoggingManager.py
# Path: AIDEV-Deploy/Utils/LoggingManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:15PM
# Description: Manages logging for the AIDEV-Deploy system

"""
LoggingManager Module

This module provides centralized logging functionality for the AIDEV-Deploy system,
with configurable output formats, log rotation, and multiple output destinations.
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from Utils.ConfigManager import ConfigManager

class LoggingManager:
    """
    Manages logging for the AIDEV-Deploy system.
    
    This class configures and initializes the Python logging system,
    providing consistent logging across all components with configurable
    output formats, log rotation, and multiple output destinations.
    
    Attributes:
        ConfigManager: Instance of ConfigManager for configuration
        LogDir: Directory where log files are stored
        LogLevel: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        FileHandler: Log file handler
        ConsoleHandler: Console output handler
    """
    
    # Log format strings
    CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    FILE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Log colors for console output
    LOG_COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, ConfigManager: Optional[ConfigManager] = None,
               LogDir: Optional[str] = None,
               LogLevel: Optional[str] = None,
               EnableConsole: bool = True,
               EnableFile: bool = True,
               ColorOutput: bool = True):
        """
        Initialize the LoggingManager.
        
        Args:
            ConfigManager: Optional ConfigManager instance. If None, creates a new instance.
            LogDir: Directory where log files are stored. If None, uses default.
            LogLevel: Logging level. If None, uses value from config.
            EnableConsole: Whether to enable console output
            EnableFile: Whether to enable file output
            ColorOutput: Whether to enable colored console output
        """
        self.ConfigManager = ConfigManager or ConfigManager()
        self.LogDir = LogDir or self._GetDefaultLogDir()
        self.LogLevel = LogLevel or self.ConfigManager.GetConfigValue("general.log_level", "INFO")
        self.FileHandler = None
        self.ConsoleHandler = None
        
        # Ensure log directory exists
        os.makedirs(self.LogDir, exist_ok=True)
        
        # Configure root logger
        RootLogger = logging.getLogger()
        RootLogger.setLevel(self._GetLogLevel(self.LogLevel))
        
        # Remove any existing handlers
        for Handler in RootLogger.handlers[:]:
            RootLogger.removeHandler(Handler)
        
        # Configure console output
        if EnableConsole:
            self._SetupConsoleHandler(ColorOutput)
        
        # Configure file output
        if EnableFile:
            self._SetupFileHandler()
    
    def _GetDefaultLogDir(self) -> str:
        """
        Get the default log directory.
        
        Returns:
            str: Default log directory path
        """
        LogDir = os.path.join(str(Path.home()), ".AIDEV-Deploy", "logs")
        return LogDir
    
    def _GetLogLevel(self, LevelName: str) -> int:
        """
        Convert a log level name to its numeric value.
        
        Args:
            LevelName: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            int: Numeric log level
        """
        Level = logging.getLevelName(LevelName.upper())
        if not isinstance(Level, int):
            return logging.INFO
        return Level
    
    def _SetupConsoleHandler(self, ColorOutput: bool) -> None:
        """
        Set up console logging handler.
        
        Args:
            ColorOutput: Whether to enable colored output
        """
        self.ConsoleHandler = logging.StreamHandler(sys.stdout)
        self.ConsoleHandler.setLevel(self._GetLogLevel(self.LogLevel))
        
        if ColorOutput and sys.stdout.isatty():
            # Use colored output
            Formatter = self._ColoredFormatter(self.CONSOLE_FORMAT, self.DATE_FORMAT)
        else:
            # Use plain output
            Formatter = logging.Formatter(self.CONSOLE_FORMAT, self.DATE_FORMAT)
        
        self.ConsoleHandler.setFormatter(Formatter)
        logging.getLogger().addHandler(self.ConsoleHandler)
    
    def _SetupFileHandler(self) -> None:
        """
        Set up file logging handler with rotation.
        """
        LogFile = os.path.join(self.LogDir, "aidev-deploy.log")
        
        # Create rotating file handler (10MB max size, keep 10 backup files)
        self.FileHandler = logging.handlers.RotatingFileHandler(
            LogFile, maxBytes=10*1024*1024, backupCount=10
        )
        self.FileHandler.setLevel(self._GetLogLevel(self.LogLevel))
        
        Formatter = logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT)
        self.FileHandler.setFormatter(Formatter)
        
        logging.getLogger().addHandler(self.FileHandler)
    
    class _ColoredFormatter(logging.Formatter):
        """
        Custom formatter for colored console output.
        """
        
        def __init__(self, Format: str, DateFormat: str):
            """
            Initialize the colored formatter.
            
            Args:
                Format: Log format string
                DateFormat: Date format string
            """
            super().__init__(Format, DateFormat)
        
        def format(self, Record: logging.LogRecord) -> str:
            """
            Format a log record with colors.
            
            Args:
                Record: Log record to format
                
            Returns:
                str: Formatted log message with colors
            """
            LevelName = Record.levelname
            Message = super().format(Record)
            
            if LevelName in LoggingManager.LOG_COLORS:
                Message = (
                    LoggingManager.LOG_COLORS[LevelName] + 
                    Message + 
                    LoggingManager.LOG_COLORS['RESET']
                )
            
            return Message
    
    def GetLogger(self, Name: str) -> logging.Logger:
        """
        Get a logger with the specified name.
        
        Args:
            Name: Logger name
            
        Returns:
            logging.Logger: Logger instance
        """
        return logging.getLogger(Name)
    
    def SetLogLevel(self, Level: str) -> None:
        """
        Set the log level for all handlers.
        
        Args:
            Level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        NumericLevel = self._GetLogLevel(Level)
        self.LogLevel = Level.upper()
        
        # Update root logger level
        logging.getLogger().setLevel(NumericLevel)
        
        # Update handler levels
        if self.ConsoleHandler:
            self.ConsoleHandler.setLevel(NumericLevel)
        
        if self.FileHandler:
            self.FileHandler.setLevel(NumericLevel)
    
    def AddFileHandler(self, Filename: str, Level: str = None) -> logging.Handler:
        """
        Add an additional file handler for specialized logging.
        
        Args:
            Filename: Log file name
            Level: Log level name. If None, uses the default level.
            
        Returns:
            logging.Handler: The created file handler
        """
        LogFile = os.path.join(self.LogDir, Filename)
        
        # Create file handler
        Handler = logging.FileHandler(LogFile)
        Handler.setLevel(self._GetLogLevel(Level or self.LogLevel))
        
        Formatter = logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT)
        Handler.setFormatter(Formatter)
        
        logging.getLogger().addHandler(Handler)
        return Handler
    
    def GetLogFilePath(self) -> str:
        """
        Get the path to the main log file.
        
        Returns:
            str: Path to the log file
        """
        return os.path.join(self.LogDir, "aidev-deploy.log")
    
    def ArchiveLogs(self) -> str:
        """
        Archive current logs to a timestamped directory.
        
        Returns:
            str: Path to the archive directory
        """
        Timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ArchiveDir = os.path.join(self.LogDir, f"archive_{Timestamp}")
        os.makedirs(ArchiveDir, exist_ok=True)
        
        # Close current file handler to release the file
        if self.FileHandler:
            self.FileHandler.close()
            logging.getLogger().removeHandler(self.FileHandler)
        
        # Copy log files to archive directory
        for Filename in os.listdir(self.LogDir):
            if Filename.endswith(".log"):
                SourcePath = os.path.join(self.LogDir, Filename)
                DestPath = os.path.join(ArchiveDir, Filename)
                
                try:
                    with open(SourcePath, 'rb') as Source:
                        with open(DestPath, 'wb') as Dest:
                            Dest.write(Source.read())
                except Exception as E:
                    print(f"Failed to archive log file {Filename}: {E}")
        
        # Recreate file handler
        self._SetupFileHandler()
        
        return ArchiveDir

def SetupLogging(LogLevel: str = None, ConfigPath: str = None) -> LoggingManager:
    """
    Set up logging for the application.
    
    Args:
        LogLevel: Optional log level override
        ConfigPath: Optional path to configuration file
        
    Returns:
        LoggingManager: Configured logging manager
    """
    ConfigMgr = ConfigManager(ConfigPath)
    Manager = LoggingManager(ConfigMgr, LogLevel=LogLevel)
    
    # Get a logger for this module
    Logger = Manager.GetLogger("LoggingSetup")
    Logger.info("Logging system initialized")
    
    return Manager

if __name__ == "__main__":
    # Setup logging when run directly
    Manager = SetupLogging()
    
    # Example usage
    Logger = Manager.GetLogger("LoggingManagerTest")
    Logger.debug("This is a debug message")
    Logger.info("This is an info message")
    Logger.warning("This is a warning message")
    Logger.error("This is an error message")
    Logger.critical("This is a critical message")
    
    print(f"Log file: {Manager.GetLogFilePath()}")
