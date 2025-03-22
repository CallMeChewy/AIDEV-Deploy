# AIDEV-Deploy: File Deployment System

**A secure, GUI-based transaction management system for automating file deployment with comprehensive validation, backup, and rollback capabilities.**

## Project Overview

AIDEV-Deploy is a deployment management system designed to ensure safe, consistent deployment of files within project folders while maintaining compliance with the AIDEV-PascalCase-1.6 standard. This tool provides transaction-based deployments with validation, rollback capabilities, and comprehensive auditing.

### Core Features

- **Transaction-Based Deployment**: Atomic operations with rollback capabilities
- **Standards Validation**: Automated validation against AIDEV-PascalCase-1.6
- **Visual Diff**: Side-by-side comparison of source and destination files
- **Automatic Backups**: Pre-deployment project backups
- **Ollama Integration**: AI-assisted validation and error correction
- **Multi-User Support**: Role-based permissions and concurrent operations
- **Comprehensive Logging**: Detailed action tracking and reporting

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PySide6 for GUI components (optional, CLI works without it)
- SQLite for data storage (included with Python)
- Ollama (optional) for AI assistance

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CallMeChewy/AIDEV-Deploy.git
   cd AIDEV-Deploy
   ```

2. Install dependencies:
   ```bash
   pip install -r Requirements.txt
   ```

3. Initialize the database:
   ```bash
   python Main.py init
   ```

4. Configure the application (optional):
   ```bash
   python Main.py config --setup
   ```

## Usage

AIDEV-Deploy can be used in both command-line and GUI modes.

### Command-Line Interface

#### Deploying Files

```bash
python Main.py deploy --source file1.py file2.py --dest /project/file1.py /project/file2.py --project /path/to/project
```

#### Validating Files

```bash
python Main.py validate file1.py file2.py
```

#### Creating a Backup

```bash
python Main.py backup --project /path/to/project
```

#### Restoring from Backup

```bash
python Main.py restore <backup_id> --output /path/to/restore
```

#### Listing Backups or Deployments

```bash
python Main.py list backups --project /path/to/project
python Main.py list deployments --project /path/to/project
```

### GUI Mode (Coming Soon)

```bash
python Main.py --gui
```

## System Architecture

### Core Components

- **TransactionManager**: Ensures atomic file operations
- **ValidationEngine**: Validates files against project standards
- **BackupManager**: Handles project backups and restoration
- **DeploymentEngine**: Manages file deployment operations
- **OllamaClient**: Integrates with Ollama for AI assistance
- **DatabaseManager**: Manages persistent storage of operations

### Utility Components

- **ConfigManager**: Manages application configuration
- **LoggingManager**: Provides centralized logging

## Development

### Project Structure

```
AIDEV-Deploy/
├── Core/                    # Core system components
│   ├── DatabaseManager.py
│   ├── TransactionManager.py
│   ├── ValidationEngine.py
│   ├── BackupManager.py
│   ├── DeploymentEngine.py
│   └── __init__.py
├── GUI/                     # User interface components
│   └── __init__.py
├── Utils/                   # Utility functions and helpers
│   ├── ConfigManager.py
│   ├── LoggingManager.py
│   └── __init__.py
├── Models/                  # Data models
│   └── __init__.py
├── Tests/                   # Test suite
│   └── TestValidation.py
├── Main.py                  # Application entry point
├── Requirements.txt         # Dependencies
└── README.md                # This file
```

### Running Tests

```bash
python -m unittest discover Tests
```

## AIDEV-PascalCase-1.6 Standard

This project follows the AIDEV-PascalCase-1.6 standard for code style and structure. Key aspects include:

- **PascalCase** for class names, function names, and variables
- **UPPERCASE_WITH_UNDERSCORES** for constants
- Standardized file header format with creation and modification timestamps
- Preservation of standard library interface method names
- Special term capitalization (AI, DB, GUI, etc.)
- Comprehensive docstrings with Args and Returns sections

## Contributing

Contributions to AIDEV-Deploy are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes following the AIDEV-PascalCase-1.6 standard
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project is part of the ProjectHimalaya ecosystem of AI-human collaborative development tools.
- Thanks to Herbert J. Bowers for the concept and design philosophy.

---

*"Code is not merely functional—it is a visual medium that developers interact with for extended periods. The choices made in these standards prioritize the axis of symmetry, character distinction, readability at scale, and visual hierarchy."*

— Herbert J. Bowers
