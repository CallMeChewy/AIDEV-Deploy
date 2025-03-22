# AIDEV-PascalCase Standards 1.6
**Created: March 16, 2025 11:45 PM**
**Last Modified: March 16, 2025  11:45 PM**

[Context: Development_Standards]
[Pattern_Type: Naming_Convention]
[Implementation_Level: Project_Wide]
[Version: 1.6]

## Change Log from v1.5
- Added new core principle: "Interface Boundary Preservation"
- Expanded rules for handling standard library interface methods
- Added detailed examples showing standard library integration
- Clarified validation rules for variables inside override methods
- Improved documentation for common Python framework interactions

## Design Philosophy and Justification

[Context: Standards_Rationale] 
[Priority: Highest]

### Developer Fingerprint

The AIDEV-PascalCase standard serves as a distinct fingerprint of its creator's work—a visual signature that marks code with a sense of craftsmanship and individual style. Just as master typographers and printers developed recognizable styles, this coding standard carries forward that tradition into software development. This fingerprint:

1. **Establishes Provenance**: Makes code immediately recognizable to collaborators
2. **Reflects Craftsmanship**: Demonstrates attention to both function and form
3. **Honors Tradition**: Connects modern software development to traditional design arts
4. **Ensures Consistency**: Creates a unified visual language across projects

### Visual Clarity in Code

The AIDEV-PascalCase standard is founded on principles of typography and visual design. Code is not merely functional—it is a visual medium that developers interact with for extended periods. The choices made in this standard prioritize:

1. **Axis of Symmetry**: Code should exhibit balance and visual harmony, facilitating easier scanning and comprehension
2. **Character Distinction**: Each identifier should be visually distinct without relying on hard-to-discern characters
3. **Readability at Scale**: Standards must remain effective when viewing large codebases or printed materials
4. **Visual Hierarchy**: Different elements (classes, functions, variables) should have visual patterns that aid in rapid identification

### Practical Benefits

This standard offers several tangible benefits over conventional Python style guides:

1. **Rapid Visual Parsing**: PascalCase creates clear word boundaries without sacrificing visual flow, unlike snake_case where underscores can be difficult to see, especially in printed code or certain fonts
2. **Consistency Across Languages**: Maintains visual consistency when working in multi-language environments (JavaScript, C#, Java, etc.)
3. **Reduced Eye Strain**: Eliminates the need to focus on low-visibility characters like underscores
4. **Clear Scope Identification**: Variable scopes and types can be more easily distinguished
5. **Enhanced Refactoring**: Makes variable names more visually distinct during search-and-replace operations

## Core Principles

[Context: Fundamental_Rules]
[Priority: Highest]

### 1. Capitalization Immutability

[Pattern: Name_Preservation]

```python
# Once capitalized, a name's format becomes immutable
ExistingName = "Value"    # Will always remain "ExistingName"
```

### 2. Special Terms Recognition

[Pattern: Reserved_Terms]
[Priority: High]

```
Preserved Terms:
- AI  (Artificial Intelligence)
- DB  (Database)
- GUI (Graphical User Interface)
- API (Application Programming Interface)
- UI  (User Interface)
- UX  (User Experience)
- ID  (Identifier)
- IO  (Input/Output)
- OS  (Operating System)
- IP  (Internet Protocol)
- URL (Uniform Resource Locator)
- HTTP (Hypertext Transfer Protocol)
```

### 3. System Element Preservation

[Pattern: System_Preservation]

```python
# Python keywords and system elements remain lowercase
def FunctionName():    # System-level element
    pass               # Python keyword
```

### 4. Interface Boundary Preservation

[Pattern: Interface_Preservation]
[Priority: High]

```python
# Methods that override standard library or framework interfaces must maintain
# their original naming conventions to ensure compatibility

# AST Visitor Pattern
class CustomVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, Node):  # Maintains library interface naming
        ClassName = Node.name        # Custom variable follows PascalCase
        return self.ProcessClass(ClassName)  # Custom method follows PascalCase

# Django Class-Based View
class UserView(View):
    def get(self, request):  # Django method override
        UserID = request.GET.get('id')  # Custom variable follows PascalCase
        return self.RenderUserProfile(UserID)  # Custom method follows PascalCase
```

### 5. Timestamp Documentation

[Pattern: Time_Tracking]

```python
# File: Example.py
# Path: Project/Component/Example.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-16
# Last Modified: 2025-03-16  11:45PM
# Description: Brief description of the file's purpose
```

Note the exactly two spaces between the date and time in the Last Modified timestamp.

### 6. Symbol Reference Consistency

[Pattern: Reference_Consistency]
[Priority: Highest]

```python
# All references to a symbol must be consistent throughout the codebase
UserName = GetUserInput()
ProcessInput(UserName)   # Not processInput(UserName) or ProcessInput(userName)
```

## Character Usage Guidelines

[Context: Visual_Design]
[Priority: High]

### Dash (-) Character Usage

[Pattern: Dash_Constraints]

The dash character impairs visual balance and should be used only in specific circumstances:

1. **Joining Acronyms with Words**:

   ```
   AIDEV-PascalCase    # Correct - connects acronym to words
   Model-Manager       # Incorrect - use ModelManager instead
   ```
2. **Sequential or Enumerated Elements**:

   ```
   Page-2-Section-3    # Correct - represents a sequence
   PG2-SEC3            # Correct - abbreviated sequence
   ```
3. **Standard Date Formats**:

   ```
   2025-03-16          # Correct - standard date format
   ```
4. **Avoid in All Other Cases**:

   ```
   Process-Data        # Incorrect - use ProcessData instead
   User-Input          # Incorrect - use UserInput instead
   ```

### Underscore (_) Character Usage

[Pattern: Underscore_Constraints]

The underscore character has poor visibility and should be limited to:

1. **Constants (ALL_CAPS)**:

   ```python
   MAX_RETRY_COUNT = 5    # Correct - constant with underscore separation
   DEFAULT_TIMEOUT = 30   # Correct - constant with underscore separation
   ```
2. **Pattern Markers in Comments/Documentation**:

   ```python
   # [Pattern: Name_Preservation]  # Correct - used in metadata/documentation
   ```
3. **Global Variable Prefixing (Optional)**:

   ```python
   g_ActiveUsers = []     # Correct - 'g' prefix for global variable
   _GlobalConfig = {}     # Alternative - underscore prefix
   ```
4. **Standard Library Interface Methods**:

   ```python
   def visit_ClassDef(self, Node):  # Correct - preserves AST visitor interface
   ```
5. **Avoid in All Other Cases**:

   ```python
   process_data()         # Incorrect - use ProcessData() instead
   user_input             # Incorrect - use UserInput instead
   ```

## Implementation Rules

[Context: Practical_Application]

### Module Declaration

[Pattern: Standard_Header]

```python
# File: ModuleName.py
# Path: Project/Component/ModuleName.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-16
# Last Modified: 2025-03-16  11:45PM
# Description: Brief description of module functionality
```

### Import Statement Formatting

[Pattern: Import_Declaration]

Import statements follow Python conventions but should be organized in a specific order:

```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party library imports
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow

# Application imports
from Core.ConfigManager import ConfigManager
from Utils.ValidationUtils import ValidateInput
```

Group imports by type with a single blank line between groups. Within each group, order alphabetically. For multi-line imports, align the imported elements for visual clarity.

### Variable Naming

[Pattern: Variable_Declaration]

All variables, including function parameters, should use PascalCase:

```python
class ExampleClass:
    def ProcessData(self, InputText: str, MaxLength: int = 100) -> None:
        self.CurrentValue = InputText[:MaxLength]
        self.LastModified = self.GetTimestamp()
        
        # Local variables use PascalCase as well
        ResultString = f"Processed: {self.CurrentValue}"
        return ResultString
```

### Function and Method Naming

[Pattern: Function_Declaration]

All custom functions and methods should use PascalCase without underscore prefixes:

```python
def ProcessInput(Data: dict, DefaultMode: str = "Standard") -> str:
    """Process the input data and return a formatted string."""
    Result = FormatData(Data, Mode=DefaultMode)
    return Result
```

### Standard Library Interface Methods

[Pattern: Interface_Method]

Methods that override standard library or framework interfaces must maintain their original naming conventions to ensure compatibility:

```python
# AST visitor pattern
def visit_ClassDef(self, Node):
    """Process a class definition node."""
    # Use PascalCase for your own variables
    ClassName = Node.name
    BaseClasses = Node.bases
    
    # Call your custom methods with PascalCase
    return self.ProcessClass(ClassName, BaseClasses)

# Django model hooks
def save(self, *args, **kwargs):
    """Override Django model save method."""
    # Use PascalCase for your own variables
    CurrentTime = datetime.now()
    self.UpdatedAt = CurrentTime
    
    # Call parent method with original naming
    super().save(*args, **kwargs)
    
    # Call your custom methods with PascalCase
    self.LogChange(CurrentTime)
```

### Class Naming

[Pattern: Class_Declaration]

```python
class DataProcessor:
    """A class that processes various types of data."""
  
    def __init__(self):
        self.ProcessedItems = 0
```

### Constants

[Pattern: Constant_Declaration]

Constants should be defined using ALL_CAPS with underscore separation:

```python
MAX_ITEMS = 100               # Module-level constant
DEFAULT_TIMEOUT = 30          # Module-level constant
COLOR_DARK_BACKGROUND = QColor(53, 53, 53)  # GUI color constants

class Config:
    API_KEY = "abc123"        # Class-level constant
    DEFAULT_RETRY_COUNT = 3   # Class-level constant
```

### Global Variables

[Pattern: Global_Variable]

```python
g_ActiveSessions = {}   # Global with 'g' prefix
_GlobalRegistry = []    # Alternative style with underscore
```

### GUI-Specific Naming

[Pattern: GUI_Element_Naming]

GUI elements should follow PascalCase with their element type included in the name:

```python
# Widgets
MainWindow = QMainWindow()
SettingsButton = QPushButton("Settings")
UserNameLabel = QLabel("Username:")
PasswordInput = QLineEdit()

# Layouts
MainLayout = QVBoxLayout()
ButtonsLayout = QHBoxLayout()

# Actions and connections
SaveAction = QAction("Save", self)
SaveAction.triggered.connect(self.SaveDocument)

# Colors
BackgroundColor = QColor(240, 240, 240)
HighlightColor = QColor(42, 130, 218)
```

## Common Framework Integration Patterns

[Context: Framework_Integration]
[Priority: Medium]

### AST Module

```python
class CustomVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, Node):  # Standard library method
        ClassName = Node.name        # Your variable -> PascalCase
        ParentClasses = []           # Your variable -> PascalCase
        
        for Base in Node.bases:      # Base is your variable -> PascalCase
            ParentClasses.append(self.GetClassName(Base))  # Your method -> PascalCase
            
        return self.ProcessClass(ClassName, ParentClasses)  # Your method -> PascalCase
```

### Django Framework

```python
class UserProfile(models.Model):
    name = models.CharField(max_length=100)  # Django model field
    email = models.EmailField(unique=True)   # Django model field
    
    def save(self, *args, **kwargs):  # Django method override
        CurrentTime = timezone.now()   # Your variable -> PascalCase
        self.UpdateLog(CurrentTime)    # Your method -> PascalCase
        super().save(*args, **kwargs)  # Call to Django method
        
    def UpdateLog(self, Timestamp):    # Your method -> PascalCase
        LogEntry = f"Updated user {self.name} at {Timestamp}"  # Your variable -> PascalCase
        logger.info(LogEntry)
```

### Flask Framework

```python
@app.route('/users/<user_id>')  # Flask decorator with its parameters
def get_user(user_id):          # Flask endpoint function
    UserID = int(user_id)       # Your variable -> PascalCase
    UserData = FetchUser(UserID)  # Your variable and method -> PascalCase
    return jsonify(UserData)
```

### SQLAlchemy ORM

```python
class User(Base):
    __tablename__ = 'users'  # SQLAlchemy attribute
    
    id = Column(Integer, primary_key=True)     # SQLAlchemy field
    username = Column(String, unique=True)     # SQLAlchemy field
    
    def __repr__(self):                        # Python dunder method
        UserString = f"User({self.username})"  # Your variable -> PascalCase
        return UserString
```

## Docstring Formatting

[Pattern: Documentation_Format]

Docstrings should be comprehensive and follow a consistent format:

### Module Docstrings

```python
"""
Module for handling configuration data.

This module provides functionality to load, save, and validate
configuration settings for the application.
"""
```

### Class Docstrings

```python
class ConfigManager:
    """A class that manages application configuration.
    
    This class provides methods for loading configuration from files,
    saving configuration to files, and validating configuration values.
    
    Attributes:
        DefaultConfig: The default configuration dictionary
        ConfigPath: Path to the configuration file
        IsModified: Flag indicating if config has been modified
    """
```

### Method Docstrings

```python
def ProcessData(self, InputData: dict, ValidateOnly: bool = False) -> bool:
    """Process the input data and update internal state.
    
    Args:
        InputData: Dictionary containing data to process
        ValidateOnly: If True, only validate but don't process
    
    Returns:
        bool: True if processing was successful, False otherwise
    
    Raises:
        ValueError: If InputData is not properly formatted
    """
```

## Module Organization

[Pattern: Code_Organization]

Modules should be organized in a consistent structure:

```python
# File header with timestamp information
# Module docstring

# Imports (organized as described above)

# Constants

# Global variables

# Classes
class MainClass:
    """Class docstring."""
    # Class constants
    
    # Initialization methods
    def __init__(self):
        pass
    
    # Public methods
    
    # Private methods

# Functions outside classes

# Main entry point (if applicable)
def Main():
    pass

if __name__ == "__main__":
    Main()
```

## Special Cases

[Pattern: Edge_Case_Handling]

### 1. Compound Special Terms

```python
AIConfig      # Correct
DbConnection  # Incorrect - should be DBConnection
GuiWindow     # Incorrect - should be GUIWindow
```

### 2. System Integration

```python
__init__.py   # System file - preserved
requirements.txt  # Configuration file - preserved
```

### 3. Multi-Word Variables

```python
UserInputValue  # Correct - each word capitalized
UserinputValue  # Incorrect - inconsistent capitalization
```

### 4. Parameters and Arguments

Function parameters follow the same PascalCase convention as all other variables:

```python
def CalculateTotal(PriceList: list, TaxRate: float = 0.08) -> float:
    """Calculate the total price including tax."""
    Subtotal = sum(PriceList)
    Total = Subtotal * (1 + TaxRate)
    return Total
```

When calling functions, maintain variable naming consistency:

```python
# Variables used as arguments should follow PascalCase
ItemPrices = [10.99, 24.50, 5.75]
LocalTaxRate = 0.095
FinalTotal = CalculateTotal(PriceList=ItemPrices, TaxRate=LocalTaxRate)
```

## File Naming

[Pattern: File_Naming]
[Priority: High]

All Python source files should follow PascalCase naming:

```
# Correct file names
DataProcessor.py
UserManager.py
ConfigSettings.py

# Incorrect file names
data_processor.py
user-manager.py
configsettings.py
```

When converting file names from kebab-case or snake_case to PascalCase:

```
parameter-editor-patch.py → ParameterEditorPatch.py
user_authentication.py → UserAuthentication.py
```

## Implementation and Tooling Guidelines

[Context: Automated_Enforcement]
[Priority: High]

### Symbol Tracking Requirements

Any implementation of this standard should track all symbol references throughout the codebase:

1. **Symbol Table Construction**: Tools must build a complete symbol table for each module
2. **Reference Tracking**: All references to a symbol must be identified and updated consistently
3. **Context Awareness**: Tools must differentiate between identical strings that represent different symbols

### Interface Method Detection

Validators must be able to distinguish between:

1. **Custom Methods**: Which should follow PascalCase
2. **Interface Override Methods**: Which should maintain original naming
3. **Framework-Specific Methods**: Which should maintain framework conventions

This can be implemented by:

1. **Class Inheritance Analysis**: Checking what classes a module extends
2. **Method Pattern Matching**: Recognizing patterns like `visit_*` for AST visitors
3. **Framework Detection**: Identifying imports from known frameworks (Django, Flask, etc.)

### Database Approach for Analysis

Complex codebases benefit from a database-driven approach to standards enforcement:

1. **Symbol Database**: Store all symbols, their types, and locations in a queryable database
2. **Dependency Mapping**: Track symbol dependencies and references
3. **Scope Awareness**: Maintain information about variable scopes and visibility
4. **Multi-file Analysis**: Consider cross-file symbol references

### Timestamp Format Specification

The "Last Modified" timestamp must adhere to this exact format:
```
# Last Modified: YYYY-MM-DD  HH:MM{AM|PM}
```

Note the following requirements:
1. **Double Space**: Exactly two spaces between the date and time
2. **12-hour Format**: Time must use 12-hour format with AM/PM suffix
3. **No Seconds**: Hours and minutes only, no seconds
4. **No Zero Padding**: No leading zero in hours (e.g., 9:30AM not 09:30AM)

## AI-Assisted Development Guidelines

[Context: AI_Integration]
[Priority: Medium]

When using AI assistants to generate or modify code:

1. **Upfront Standards Declaration**: Provide the AIDEV-PascalCase standard reference at the beginning of the session
2. **Incremental Validation**: Validate each code segment for compliance before proceeding
3. **Symbol Tracking**: Maintain a list of named symbols (variables, functions, classes) and ensure consistent naming
4. **Prompt Engineering**: Use prompts that explicitly mention naming conventions
5. **Framework Context**: Inform the AI about which frameworks you're using to ensure proper interface method handling

### Example AI Instruction

```
Please follow AIDEV-PascalCase Standards 1.6 for this code:
- Class names in PascalCase (e.g., DataProcessor)
- Custom function and method names in PascalCase (e.g., ProcessData)
- Standard library interface methods should maintain their original naming (e.g., visit_ClassDef)
- All variables should use PascalCase, even inside interface methods (e.g., UserInput)
- Constants in UPPERCASE_WITH_UNDERSCORES (e.g., MAX_RETRY_COUNT)
- File names in PascalCase (e.g., DataProcessor.py)
- Two spaces between date and time in timestamps
```

## Contextual References

[Pattern: Context_Awareness]
[Priority: High]

When modifying variables or functions, all references must be updated consistently:

```python
# INCORRECT - inconsistent references
UserName = GetInputFromConsole()
ProcessData(userName)  # Inconsistent capitalization
DisplayResults(UserName)

# CORRECT - consistent references
UserName = GetInputFromConsole()
ProcessData(UserName)
DisplayResults(UserName)
```

Special attention is required for references in:

1. **F-strings and String Literals**:
   ```python
   # When variable InputFile is renamed to InputFile, all references must update
   LogMessage = f"Processing file {InputFile} with options {Options}"
   ```

2. **Function and Method Calls**:
   ```python
   # When function process_data is renamed to ProcessData
   Result = ProcessData(InputValue)  # Not process_data(InputValue)
   ```

3. **Keyword Arguments**:
   ```python
   # When parameter input_text is renamed to InputText
   ParseDocument(InputText="sample")  # Not input_text="sample"
   ```

## Real-World Examples

### 1. AST Visitor with Program Variables

```python
class CustomVisitor(ast.NodeVisitor):
    def __init__(self):
        self.ClassCount = 0           # Your variable -> PascalCase
        self.FunctionCount = 0        # Your variable -> PascalCase
        self.Results = {}             # Your variable -> PascalCase
    
    def visit_ClassDef(self, Node):   # AST interface method -> original naming
        ClassName = Node.name         # Your variable -> PascalCase
        self.ClassCount += 1
        self.ProcessClassMembers(Node)  # Your method -> PascalCase
        self.generic_visit(Node)        # AST method -> original naming
    
    def visit_FunctionDef(self, Node): # AST interface method -> original naming
        FunctionName = Node.name       # Your variable -> PascalCase
        self.FunctionCount += 1
        self.Results[FunctionName] = self.AnalyzeFunction(Node)  # Your method -> PascalCase
        self.generic_visit(Node)       # AST method -> original naming
    
    def ProcessClassMembers(self, ClassNode):  # Your method -> PascalCase
        MemberCount = len(ClassNode.body)      # Your variable -> PascalCase
        return MemberCount
    
    def AnalyzeFunction(self, FunctionNode):   # Your method -> PascalCase
        ArgCount = len(FunctionNode.args.args) # Your variable -> PascalCase
        return {
            "Arguments": ArgCount,                    # Your dictionary key -> regular string
            "LineCount": self.CountLines(FunctionNode)  # Your method -> PascalCase
        }
    
    def CountLines(self, Node):      # Your method -> PascalCase
        EndLine = Node.end_lineno    # Your variable -> PascalCase
        StartLine = Node.lineno      # Your variable -> PascalCase
        return EndLine - StartLine + 1
```

### 2. Django Model with Program Variables

```python
class UserProfile(models.Model):
    username = models.CharField(max_length=100)    # Django field
    email = models.EmailField(unique=True)         # Django field
    
    def save(self, *args, **kwargs):               # Django method
        CurrentTime = timezone.now()               # Your variable -> PascalCase
        IsNewUser = not self.pk                    # Your variable -> PascalCase
        
        super().save(*args, **kwargs)              # Call to parent method
        
        if IsNewUser:
            self.CreateDefaultSettings()           # Your method -> PascalCase
        self.LogUserActivity("profile_updated", CurrentTime)  # Your method -> PascalCase
    
    def CreateDefaultSettings(self):               # Your method -> PascalCase
        DefaultTheme = "light"                     # Your variable -> PascalCase
        Settings = UserSettings(user=self, theme=DefaultTheme)  # Your variable -> PascalCase
        Settings.save()
    
    def LogUserActivity(self, ActivityType, Timestamp):  # Your method -> PascalCase
        LogEntry = UserLog(                        # Your variable -> PascalCase
            user=self,
            activity_type=ActivityType,            # Your parameter -> PascalCase
            timestamp=Timestamp                    # Your parameter -> PascalCase
        )
        LogEntry.save()
```

## Final Notes

The AIDEV-PascalCase 1.6 standard recognizes the need to balance visual clarity and distinction with the practical reality of working with Python's standard libraries and frameworks. By maintaining PascalCase for custom program variables even within interface methods, the standard achieves its goal of making developer-created elements immediately recognizable while still ensuring compatibility with the broader Python ecosystem.

---

Last Updated: 2025-03-16
Status: Active
Version: 1.6
