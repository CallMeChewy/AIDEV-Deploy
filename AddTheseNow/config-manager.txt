# File: ConfigManager.py
# Path: AIDEV-Deploy/Utils/ConfigManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:05PM
# Description: Manages configuration for the AIDEV-Deploy system

"""
ConfigManager Module

This module provides configuration management for the AIDEV-Deploy system,
allowing loading, saving, and validation of configuration settings from
YAML files with type checking and default values.
"""

import os
import yaml
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Type, TypeVar, cast

T = TypeVar('T')

class ConfigManager:
    """
    Manages configuration settings for the AIDEV-Deploy system.
    
    This class loads, saves, and validates configuration settings from
    YAML files, providing type checking, default values, and environment
    variable overrides.
    
    Attributes:
        ConfigPath: Path to the configuration file
        Config: Dictionary of configuration settings
        DefaultConfig: Dictionary of default configuration settings
        TypeMap: Dictionary mapping configuration keys to expected types
    """
    
    def __init__(self, ConfigPath: Optional[str] = None):
        """
        Initialize the ConfigManager.
        
        Args:
            ConfigPath: Path to the configuration file. If None, uses default location.
        """
        self.ConfigPath = ConfigPath or self._GetDefaultConfigPath()
        self.Config = {}
        self.DefaultConfig = self._CreateDefaultConfig()
        self.TypeMap = self._CreateTypeMap()
        
        # Set up logging
        self.Logger = logging.getLogger("ConfigManager")
        
        # Load configuration
        self.LoadConfig()
    
    def _GetDefaultConfigPath(self) -> str:
        """
        Get the default configuration file path.
        
        Returns:
            str: Default configuration file path
        """
        AppDataDir = os.path.join(str(Path.home()), ".AIDEV-Deploy")
        os.makedirs(AppDataDir, exist_ok=True)
        return os.path.join(AppDataDir, "config.yaml")
    
    def _CreateDefaultConfig(self) -> Dict[str, Any]:
        """
        Create the default configuration.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            # General Configuration
            "general": {
                "project_root": str(Path.home() / "projects"),
                "debug_mode": False,
                "log_level": "INFO",
                "theme": "system"
            },
            
            # Database Configuration
            "database": {
                "path": os.path.join(str(Path.home()), ".AIDEV-Deploy", "database.db"),
                "backup_interval": 7  # days
            },
            
            # Backup Configuration
            "backup": {
                "location": os.path.join(str(Path.home()), ".AIDEV-Deploy", "backups"),
                "compression": True,
                "retention_count": 10,
                "auto_backup": True
            },
            
            # Validation Configuration
            "validation": {
                "standards": "AIDEV-PascalCase-1.6",
                "strict_mode": False,
                "auto_validation": True
            },
            
            # Ollama Configuration (if used)
            "ollama": {
                "model": "codellama:13b-instruct",
                "api_endpoint": "http://localhost:11434/api",
                "gpu_enabled": True,
                "gpu_id": 0,
                "max_tokens": 2048
            },
            
            # User Interface
            "ui": {
                "max_recent_projects": 10,
                "autosave_interval": 300,  # seconds
                "diff_colors": {
                    "addition": "#CCFFCC",
                    "deletion": "#FFCCCC",
                    "change": "#FFFFCC"
                }
            },
            
            # Security
            "security": {
                "require_authentication": True,
                "session_timeout": 3600,  # seconds
                "restricted_directories": [
                    "/etc",
                    "/var",
                    "/usr"
                ]
            }
        }
    
    def _CreateTypeMap(self) -> Dict[str, Type]:
        """
        Create a map of configuration keys to their expected types.
        
        Returns:
            Dict[str, Type]: Type map for configuration validation
        """
        return {
            "general.project_root": str,
            "general.debug_mode": bool,
            "general.log_level": str,
            "general.theme": str,
            
            "database.path": str,
            "database.backup_interval": int,
            
            "backup.location": str,
            "backup.compression": bool,
            "backup.retention_count": int,
            "backup.auto_backup": bool,
            
            "validation.standards": str,
            "validation.strict_mode": bool,
            "validation.auto_validation": bool,
            
            "ollama.model": str,
            "ollama.api_endpoint": str,
            "ollama.gpu_enabled": bool,
            "ollama.gpu_id": int,
            "ollama.max_tokens": int,
            
            "ui.max_recent_projects": int,
            "ui.autosave_interval": int,
            "ui.diff_colors.addition": str,
            "ui.diff_colors.deletion": str,
            "ui.diff_colors.change": str,
            
            "security.require_authentication": bool,
            "security.session_timeout": int,
            "security.restricted_directories": list
        }
    
    def LoadConfig(self) -> None:
        """
        Load configuration from file.
        
        If the file doesn't exist, creates it with default values.
        Merges loaded configuration with defaults to ensure all required values exist.
        """
        # Start with default configuration
        self.Config = self.DefaultConfig.copy()
        
        # Check if the config file exists
        if not os.path.exists(self.ConfigPath):
            self.Logger.info(f"Configuration file not found, creating: {self.ConfigPath}")
            self.SaveConfig()
            return
        
        try:
            # Load configuration from file
            with open(self.ConfigPath, 'r') as File:
                LoadedConfig = yaml.safe_load(File)
            
            if LoadedConfig:
                # Merge loaded configuration with defaults
                self._MergeConfig(self.Config, LoadedConfig)
            
            # Validate configuration
            self._ValidateConfig()
            
            self.Logger.info(f"Loaded configuration from: {self.ConfigPath}")
            
        except Exception as E:
            self.Logger.error(f"Failed to load configuration: {E}")
            # Revert to defaults
            self.Config = self.DefaultConfig.copy()
    
    def SaveConfig(self) -> None:
        """
        Save configuration to file.
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.ConfigPath), exist_ok=True)
            
            # Save configuration to file
            with open(self.ConfigPath, 'w') as File:
                yaml.dump(self.Config, File, default_flow_style=False)
            
            self.Logger.info(f"Saved configuration to: {self.ConfigPath}")
            
        except Exception as E:
            self.Logger.error(f"Failed to save configuration: {E}")
    
    def _MergeConfig(self, Base: Dict[str, Any], Override: Dict[str, Any]) -> None:
        """
        Recursively merge configuration dictionaries.
        
        Args:
            Base: Base configuration (will be modified)
            Override: Overriding configuration values
        """
        for Key, Value in Override.items():
            if Key in Base:
                if isinstance(Base[Key], dict) and isinstance(Value, dict):
                    self._MergeConfig(Base[Key], Value)
                else:
                    Base[Key] = Value
            else:
                Base[Key] = Value
    
    def _ValidateConfig(self) -> None:
        """
        Validate configuration types and values.
        
        Raises:
            ValueError: If a configuration value has an invalid type
        """
        for Key, ExpectedType in self.TypeMap.items():
            Value = self.GetConfigValue(Key)
            
            if Value is not None and not isinstance(Value, ExpectedType):
                # Try to convert the value to the expected type
                try:
                    ConvertedValue = ExpectedType(Value)
                    self.SetConfigValue(Key, ConvertedValue)
                    self.Logger.warning(f"Converted {Key} from {type(Value)} to {ExpectedType}")
                except Exception:
                    self.Logger.warning(
                        f"Invalid type for {Key}: expected {ExpectedType.__name__}, got {type(Value).__name__}"
                    )
                    # Reset to default value
                    DefaultValue = self.GetDefaultConfigValue(Key)
                    if DefaultValue is not None:
                        self.SetConfigValue(Key, DefaultValue)
                        self.Logger.warning(f"Reset {Key} to default value: {DefaultValue}")
    
    def GetConfigValue(self, Key: str, DefaultValue: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            Key: Configuration key (using dot notation)
            DefaultValue: Default value if key doesn't exist
            
        Returns:
            Any: Configuration value or default
        """
        # Check for environment variable override
        EnvVarName = f"AIDEV_DEPLOY_{Key.upper().replace('.', '_')}"
        EnvValue = os.environ.get(EnvVarName)
        if EnvValue is not None:
            # Convert to appropriate type
            ExpectedType = self.TypeMap.get(Key)
            if ExpectedType:
                try:
                    return ExpectedType(EnvValue)
                except Exception:
                    self.Logger.warning(f"Failed to convert environment variable {EnvVarName}")
        
        # Get from configuration
        Config = self.Config
        KeyParts = Key.split('.')
        
        for Part in KeyParts:
            if isinstance(Config, dict) and Part in Config:
                Config = Config[Part]
            else:
                return DefaultValue
        
        return Config
    
    def GetDefaultConfigValue(self, Key: str) -> Any:
        """
        Get a default configuration value by key.
        
        Args:
            Key: Configuration key (using dot notation)
            
        Returns:
            Any: Default configuration value or None
        """
        Config = self.DefaultConfig
        KeyParts = Key.split('.')
        
        for Part in KeyParts:
            if isinstance(Config, dict) and Part in Config:
                Config = Config[Part]
            else:
                return None
        
        return Config
    
    def SetConfigValue(self, Key: str, Value: Any) -> None:
        """
        Set a configuration value by key.
        
        Args:
            Key: Configuration key (using dot notation)
            Value: Value to set
        """
        # Validate the type
        ExpectedType = self.TypeMap.get(Key)
        if ExpectedType and not isinstance(Value, ExpectedType):
            try:
                Value = ExpectedType(Value)
            except Exception:
                raise TypeError(
                    f"Invalid type for {Key}: expected {ExpectedType.__name__}, got {type(Value).__name__}"
                )
        
        # Set the value
        Config = self.Config
        KeyParts = Key.split('.')
        LastPart = KeyParts[-1]
        
        for Part in KeyParts[:-1]:
            if Part not in Config:
                Config[Part] = {}
            Config = Config[Part]
        
        Config[LastPart] = Value
    
    def GetSectionConfig(self, Section: str) -> Dict[str, Any]:
        """
        Get an entire section of the configuration.
        
        Args:
            Section: Section name (top-level key)
            
        Returns:
            Dict[str, Any]: Section configuration
        """
        return self.Config.get(Section, {}).copy()
    
    def ResetToDefaults(self) -> None:
        """
        Reset configuration to default values.
        """
        self.Config = self.DefaultConfig.copy()
        self.SaveConfig()
        self.Logger.info("Reset configuration to defaults")
    
    def GetConfigKeys(self) -> List[str]:
        """
        Get all configuration keys using dot notation.
        
        Returns:
            List[str]: List of configuration keys
        """
        def FlattenDict(D: Dict[str, Any], Prefix: str = "") -> List[str]:
            Result = []
            for Key, Value in D.items():
                FullKey = f"{Prefix}.{Key}" if Prefix else Key
                if isinstance(Value, dict):
                    Result.extend(FlattenDict(Value, FullKey))
                else:
                    Result.append(FullKey)
            return Result
        
        return FlattenDict(self.Config)

def SetupInteractive() -> None:
    """Run interactive configuration setup."""
    print("\nAIDEV-Deploy Configuration Setup")
    print("==============================\n")
    
    Manager = ConfigManager()
    
    # General configuration
    print("General Configuration:")
    ProjectRoot = input(f"Project root directory [{Manager.GetConfigValue('general.project_root')}]: ")
    if ProjectRoot:
        Manager.SetConfigValue('general.project_root', ProjectRoot)
    
    Theme = input(f"UI theme (system, light, dark) [{Manager.GetConfigValue('general.theme')}]: ")
    if Theme and Theme in ['system', 'light', 'dark']:
        Manager.SetConfigValue('general.theme', Theme)
    
    # Backup configuration
    print("\nBackup Configuration:")
    BackupLocation = input(f"Backup location [{Manager.GetConfigValue('backup.location')}]: ")
    if BackupLocation:
        Manager.SetConfigValue('backup.location', BackupLocation)
    
    AutoBackup = input(f"Enable automatic backups (y/n) [{Manager.GetConfigValue('backup.auto_backup')}]: ")
    if AutoBackup.lower() in ['y', 'n']:
        Manager.SetConfigValue('backup.auto_backup', AutoBackup.lower() == 'y')
    
    # Validation configuration
    print("\nValidation Configuration:")
    ValidationStandard = input(f"Validation standard [{Manager.GetConfigValue('validation.standards')}]: ")
    if ValidationStandard:
        Manager.SetConfigValue('validation.standards', ValidationStandard)
    
    StrictMode = input(f"Enable strict validation mode (y/n) [{Manager.GetConfigValue('validation.strict_mode')}]: ")
    if StrictMode.lower() in ['y', 'n']:
        Manager.SetConfigValue('validation.strict_mode', StrictMode.lower() == 'y')
    
    # Ollama configuration (if used)
    print("\nOllama Configuration (if used):")
    EnableOllama = input("Enable Ollama integration (y/n): ")
    if EnableOllama.lower() == 'y':
        OllamaModel = input(f"Ollama model [{Manager.GetConfigValue('ollama.model')}]: ")
        if OllamaModel:
            Manager.SetConfigValue('ollama.model', OllamaModel)
        
        OllamaEndpoint = input(f"Ollama API endpoint [{Manager.GetConfigValue('ollama.api_endpoint')}]: ")
        if OllamaEndpoint:
            Manager.SetConfigValue('ollama.api_endpoint', OllamaEndpoint)
    
    # Save configuration
    Manager.SaveConfig()
    print("\nConfiguration saved successfully!")
    print(f"Configuration file: {Manager.ConfigPath}")

def Main():
    """Command-line interface for configuration management."""
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy Configuration Manager")
    Parser.add_argument("--get", help="Get a configuration value")
    Parser.add_argument("--set", help="Set a configuration value")
    Parser.add_argument("--value", help="Value to set (used with --set)")
    Parser.add_argument("--reset", action="store_true", help="Reset configuration to defaults")
    Parser.add_argument("--list", action="store_true", help="List all configuration keys")
    Parser.add_argument("--setup", action="store_true", help="Run interactive setup")
    Parser.add_argument("--path", help="Configuration file path")
    
    Args = Parser.parse_args()
    
    # Create config manager
    Manager = ConfigManager(Args.path)
    
    try:
        if Args.setup:
            SetupInteractive()
            
        elif Args.get:
            Value = Manager.GetConfigValue(Args.get)
            print(f"{Args.get}: {Value}")
            
        elif Args.set:
            if Args.value is None:
                print("Error: --value is required with --set")
                return 1
            
            Manager.SetConfigValue(Args.set, Args.value)
            Manager.SaveConfig()
            print(f"Set {Args.set} to {Args.value}")
            
        elif Args.reset:
            Manager.ResetToDefaults()
            print("Configuration reset to defaults")
            
        elif Args.list:
            Keys = Manager.GetConfigKeys()
            for Key in sorted(Keys):
                Value = Manager.GetConfigValue(Key)
                print(f"{Key}: {Value}")
            
        else:
            print("No action specified. Use --help for usage information.")
    
    except Exception as E:
        print(f"Error: {E}")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(Main())
