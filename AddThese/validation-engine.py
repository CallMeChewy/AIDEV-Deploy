# File: ValidationEngine.py
# Path: AIDEV-Deploy/Core/ValidationEngine.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  4:35PM
# Description: Validates files against project standards including AIDEV-PascalCase-1.6

"""
ValidationEngine Module

This module provides validation capabilities for files against project standards,
particularly focusing on AIDEV-PascalCase-1.6 requirements. It validates file
headers, naming conventions, syntax, and other standard-specific requirements.
"""

import os
import re
import ast
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Set

class ValidationEngine:
    """
    Validates files against project standards.
    
    This class provides methods to validate files against the AIDEV-PascalCase-1.6
    standard and other project requirements, checking file headers, naming conventions,
    code structure, and more.
    
    Attributes:
        StandardVersion: Version of the AIDEV-PascalCase standard to validate against
        ValidationRules: Dictionary of validation rules and their patterns
    """
    
    def __init__(self, StandardVersion: str = "1.6"):
        """
        Initialize the ValidationEngine.
        
        Args:
            StandardVersion: Version of the AIDEV-PascalCase standard to validate against
        """
        self.StandardVersion = StandardVersion
        self.ValidationRules = self._InitializeValidationRules()
    
    def _InitializeValidationRules(self) -> Dict[str, Any]:
        """
        Initialize the validation rules for AIDEV-PascalCase standards.
        
        Returns:
            Dict[str, Any]: Dictionary of validation rules
        """
        Rules = {
            "FileHeader": {
                "pattern": r'# File: .+\.py\n# Path: .+\n# Standard: AIDEV-PascalCase-[0-9]+\.[0-9]+\n# Created: [0-9]{4}-[0-9]{2}-[0-9]{2}\n# Last Modified: [0-9]{4}-[0-9]{2}-[0-9]{2}  [0-9]{1,2}:[0-9]{2}(?:AM|PM)\n# Description: .+',
                "description": "File header format validation"
            },
            "ClassNaming": {
                "pattern": r'^[A-Z][a-zA-Z0-9]*$',
                "description": "Class names should use PascalCase"
            },
            "FunctionNaming": {
                "pattern": r'^[A-Z][a-zA-Z0-9]*$',
                "description": "Function and method names should use PascalCase"
            },
            "VariableNaming": {
                "pattern": r'^[A-Z][a-zA-Z0-9]*$',
                "description": "Variable names should use PascalCase"
            },
            "ConstantNaming": {
                "pattern": r'^[A-Z][A-Z0-9_]*$',
                "description": "Constants should use UPPERCASE_WITH_UNDERSCORES"
            },
            "SpecialTerms": {
                "terms": ["AI", "DB", "GUI", "API", "UI", "UX", "ID", "IO", "OS", "IP", "URL", "HTTP"],
                "description": "Special terms should preserve their capitalization"
            }
        }
        
        return Rules
    
    def ValidateFile(self, FilePath: str, ValidationTypes: List[str] = None) -> Dict[str, Any]:
        """
        Validate a file against project standards.
        
        Args:
            FilePath: Path to the file to validate
            ValidationTypes: List of validation types to perform. If None, performs all validations.
            
        Returns:
            Dict[str, Any]: Validation results with status, errors, and warnings
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Check file exists
        if not os.path.exists(FilePath):
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": 0,
                "message": f"File not found: {FilePath}",
                "rule": "FileExistence"
            })
            return Results
        
        # Determine file type and validate accordingly
        FileExtension = os.path.splitext(FilePath)[1].lower()
        
        if FileExtension == '.py':
            return self.ValidatePythonFile(FilePath, ValidationTypes)
        elif FileExtension in ['.md', '.txt']:
            return self.ValidateTextFile(FilePath, ValidationTypes)
        else:
            Results["status"] = "WARNING"
            Results["warnings"].append({
                "line": 0,
                "message": f"Unsupported file type for validation: {FileExtension}",
                "rule": "FileType"
            })
            return Results
    
    def ValidatePythonFile(self, FilePath: str, ValidationTypes: List[str] = None) -> Dict[str, Any]:
        """
        Validate a Python file against project standards.
        
        Args:
            FilePath: Path to the Python file
            ValidationTypes: List of validation types to perform. If None, performs all validations.
            
        Returns:
            Dict[str, Any]: Validation results with status, errors, and warnings
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Read file content
        try:
            with open(FilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
                Lines = Content.splitlines()
        except Exception as E:
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": 0,
                "message": f"Could not read file: {E}",
                "rule": "FileReadability"
            })
            return Results
        
        # Define validation functions to run
        ValidationFunctions = {
            "Syntax": self._ValidatePythonSyntax,
            "FileHeader": self._ValidateFileHeader,
            "Naming": self._ValidatePythonNaming,
            "ImportFormat": self._ValidateImportFormat,
            "Docstrings": self._ValidateDocstrings
        }
        
        # Determine which validations to run
        if ValidationTypes is None:
            ValidationTypes = list(ValidationFunctions.keys())
        
        # Run validations
        for ValidationType in ValidationTypes:
            if ValidationType in ValidationFunctions:
                ValidationFunc = ValidationFunctions[ValidationType]
                ValidationResults = ValidationFunc(FilePath, Content, Lines)
                
                # Update overall status
                if ValidationResults["status"] == "FAIL" and Results["status"] != "FAIL":
                    Results["status"] = "FAIL"
                elif ValidationResults["status"] == "WARNING" and Results["status"] == "PASS":
                    Results["status"] = "WARNING"
                
                # Add errors and warnings
                Results["errors"].extend(ValidationResults.get("errors", []))
                Results["warnings"].extend(ValidationResults.get("warnings", []))
        
        return Results
    
    def ValidateTextFile(self, FilePath: str, ValidationTypes: List[str] = None) -> Dict[str, Any]:
        """
        Validate a text file against project standards.
        
        Args:
            FilePath: Path to the text file
            ValidationTypes: List of validation types to perform. If None, performs all validations.
            
        Returns:
            Dict[str, Any]: Validation results with status, errors, and warnings
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # For now, we'll just do basic validation of text files
        # This can be expanded in the future for more specific validation
        
        try:
            with open(FilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
                Lines = Content.splitlines()
        except Exception as E:
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": 0,
                "message": f"Could not read file: {E}",
                "rule": "FileReadability"
            })
            return Results
        
        # Check for common markdown issues if it's a markdown file
        if FilePath.lower().endswith('.md'):
            # Check for proper heading hierarchy
            HeadingLevels = []
            for LineNum, Line in enumerate(Lines, 1):
                if Line.startswith('#'):
                    Level = 0
                    for Char in Line:
                        if Char == '#':
                            Level += 1
                        else:
                            break
                    
                    if HeadingLevels and Level > HeadingLevels[-1] + 1:
                        Results["warnings"].append({
                            "line": LineNum,
                            "message": f"Heading level jumps from {HeadingLevels[-1]} to {Level}",
                            "rule": "MarkdownHeadingHierarchy"
                        })
                    
                    HeadingLevels.append(Level)
        
        return Results
    
    def _ValidatePythonSyntax(self, FilePath: str, Content: str, Lines: List[str]) -> Dict[str, Any]:
        """
        Validate Python syntax.
        
        Args:
            FilePath: Path to the Python file
            Content: File content
            Lines: File content as list of lines
            
        Returns:
            Dict[str, Any]: Validation results
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        try:
            ast.parse(Content, filename=FilePath)
        except SyntaxError as E:
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": E.lineno,
                "message": f"Syntax error: {E}",
                "rule": "PythonSyntax"
            })
        
        return Results
    
    def _ValidateFileHeader(self, FilePath: str, Content: str, Lines: List[str]) -> Dict[str, Any]:
        """
        Validate file header against AIDEV-PascalCase standards.
        
        Args:
            FilePath: Path to the Python file
            Content: File content
            Lines: File content as list of lines
            
        Returns:
            Dict[str, Any]: Validation results
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Extract header (first 6 lines if they start with #)
        HeaderLines = []
        for Line in Lines[:6]:
            if Line.startswith('# '):
                HeaderLines.append(Line)
            else:
                break
        
        if len(HeaderLines) < 6:
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": 1,
                "message": "Incomplete file header. Headers should include File, Path, Standard, Created, Last Modified, and Description.",
                "rule": "FileHeader"
            })
            return Results
        
        # Join header lines
        Header = '\n'.join(HeaderLines)
        
        # Check header pattern
        if not re.match(self.ValidationRules["FileHeader"]["pattern"], Header):
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": 1,
                "message": "File header does not match required format.",
                "rule": "FileHeader"
            })
            
            # Additional checks for specific header components
            if not any(Line.startswith("# File:") for Line in HeaderLines):
                Results["errors"].append({
                    "line": 1,
                    "message": "Missing 'File:' in header.",
                    "rule": "FileHeader"
                })
            
            if not any(Line.startswith("# Path:") for Line in HeaderLines):
                Results["errors"].append({
                    "line": 2,
                    "message": "Missing 'Path:' in header.",
                    "rule": "FileHeader"
                })
            
            if not any(Line.startswith("# Standard: AIDEV-PascalCase") for Line in HeaderLines):
                Results["errors"].append({
                    "line": 3,
                    "message": "Missing or incorrect 'Standard:' in header.",
                    "rule": "FileHeader"
                })
            
            if not any(Line.startswith("# Created:") for Line in HeaderLines):
                Results["errors"].append({
                    "line": 4,
                    "message": "Missing 'Created:' in header.",
                    "rule": "FileHeader"
                })
            
            LastModifiedPattern = r'# Last Modified: [0-9]{4}-[0-9]{2}-[0-9]{2}  [0-9]{1,2}:[0-9]{2}(?:AM|PM)'
            if not any(re.match(LastModifiedPattern, Line) for Line in HeaderLines):
                Results["errors"].append({
                    "line": 5,
                    "message": "Missing or incorrect 'Last Modified:' in header. Format should be: YYYY-MM-DD  HH:MMAM/PM with exactly two spaces between date and time.",
                    "rule": "FileHeader"
                })
            
            if not any(Line.startswith("# Description:") for Line in HeaderLines):
                Results["errors"].append({
                    "line": 6,
                    "message": "Missing 'Description:' in header.",
                    "rule": "FileHeader"
                })
        
        # Check standard version
        StandardLine = next((Line for Line in HeaderLines if Line.startswith("# Standard:")), "")
        if StandardLine:
            VersionMatch = re.search(r'AIDEV-PascalCase-([0-9]+\.[0-9]+)', StandardLine)
            if VersionMatch:
                FileVersion = VersionMatch.group(1)
                if FileVersion != self.StandardVersion:
                    Results["warnings"].append({
                        "line": HeaderLines.index(StandardLine) + 1,
                        "message": f"File uses standard version {FileVersion}, but validation is using version {self.StandardVersion}.",
                        "rule": "StandardVersion"
                    })
        
        return Results
    
    def _ValidatePythonNaming(self, FilePath: str, Content: str, Lines: List[str]) -> Dict[str, Any]:
        """
        Validate Python naming conventions.
        
        Args:
            FilePath: Path to the Python file
            Content: File content
            Lines: File content as list of lines
            
        Returns:
            Dict[str, Any]: Validation results
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        try:
            # Parse the Python file
            Tree = ast.parse(Content, filename=FilePath)
            
            # Track code symbols for reference consistency
            Symbols = {}
            
            # Check class names
            for Node in ast.walk(Tree):
                if isinstance(Node, ast.ClassDef):
                    ClassName = Node.name
                    Symbols[ClassName] = {"type": "class", "line": Node.lineno}
                    
                    if not re.match(self.ValidationRules["ClassNaming"]["pattern"], ClassName):
                        # Skip classes that might be overriding standard library classes
                        if not self._IsLibraryOverride(Node):
                            Results["status"] = "FAIL"
                            Results["errors"].append({
                                "line": Node.lineno,
                                "message": f"Class name '{ClassName}' does not follow PascalCase convention.",
                                "rule": "ClassNaming"
                            })
                
                # Check function and method names
                elif isinstance(Node, ast.FunctionDef):
                    FunctionName = Node.name
                    Symbols[FunctionName] = {"type": "function", "line": Node.lineno}
                    
                    # Skip if it's a dunder method or an interface method
                    if not FunctionName.startswith('__') and not self._IsInterfaceMethod(Node):
                        if not re.match(self.ValidationRules["FunctionNaming"]["pattern"], FunctionName):
                            Results["status"] = "FAIL"
                            Results["errors"].append({
                                "line": Node.lineno,
                                "message": f"Function/method name '{FunctionName}' does not follow PascalCase convention.",
                                "rule": "FunctionNaming"
                            })
                
                # Check variable assignments
                elif isinstance(Node, ast.Assign):
                    for Target in Node.targets:
                        if isinstance(Target, ast.Name):
                            VariableName = Target.id
                            Symbols[VariableName] = {"type": "variable", "line": Target.lineno}
                            
                            # Skip builtins and module-level constants
                            if not VariableName.startswith('__') and not self._IsSystemElement(VariableName):
                                # Check if it's a constant (all caps)
                                if VariableName.isupper():
                                    if not re.match(self.ValidationRules["ConstantNaming"]["pattern"], VariableName):
                                        Results["status"] = "FAIL"
                                        Results["errors"].append({
                                            "line": Target.lineno,
                                            "message": f"Constant '{VariableName}' does not follow UPPERCASE_WITH_UNDERSCORES convention.",
                                            "rule": "ConstantNaming"
                                        })
                                else:
                                    # Regular variable
                                    if not re.match(self.ValidationRules["VariableNaming"]["pattern"], VariableName):
                                        Results["status"] = "FAIL"
                                        Results["errors"].append({
                                            "line": Target.lineno,
                                            "message": f"Variable '{VariableName}' does not follow PascalCase convention.",
                                            "rule": "VariableNaming"
                                        })
            
            # Check for special terms
            for LineNum, Line in enumerate(Lines, 1):
                for Term in self.ValidationRules["SpecialTerms"]["terms"]:
                    # Match the term with word boundaries
                    Matches = re.finditer(r'\b{0}\b'.format(Term.lower()), Line.lower())
                    for Match in Matches:
                        # Get the actual text from the original line
                        ActualTerm = Line[Match.start():Match.end()]
                        if ActualTerm != Term:
                            Results["warnings"].append({
                                "line": LineNum,
                                "message": f"Special term '{ActualTerm}' should be written as '{Term}'.",
                                "rule": "SpecialTerms"
                            })
        
        except Exception as E:
            Results["status"] = "FAIL"
            Results["errors"].append({
                "line": 0,
                "message": f"Error during naming validation: {str(E)}",
                "rule": "NamingAnalysis"
            })
        
        return Results
    
    def _ValidateImportFormat(self, FilePath: str, Content: str, Lines: List[str]) -> Dict[str, Any]:
        """
        Validate import statement formatting.
        
        Args:
            FilePath: Path to the Python file
            Content: File content
            Lines: File content as list of lines
            
        Returns:
            Dict[str, Any]: Validation results
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        ImportGroups = {
            "standard": [],
            "third_party": [],
            "application": []
        }
        
        CurrentGroup = None
        InImportSection = False
        ImportSectionStartLine = 0
        
        # Common standard library modules
        StandardLibs = set([
            "os", "sys", "re", "math", "time", "datetime", "json", "csv", "random",
            "argparse", "logging", "collections", "itertools", "functools", "pathlib",
            "sqlite3", "urllib", "http", "email", "xml", "html", "unittest", "threading",
            "multiprocessing", "subprocess", "socket", "ssl", "ftplib", "uuid", "hashlib",
            "base64", "shutil", "glob", "tempfile", "io", "pickle", "shelve", "configparser",
            "ast"
        ])
        
        for LineNum, Line in enumerate(Lines, 1):
            Line = Line.strip()
            
            # Check if we're at import statements
            if Line.startswith(("import ", "from ")) and not InImportSection:
                InImportSection = True
                ImportSectionStartLine = LineNum
            
            # Skip comments and empty lines
            if not Line or Line.startswith("#"):
                continue
            
            # Check for import statements
            if Line.startswith(("import ", "from ")):
                # Determine the import group
                if Line.startswith("from "):
                    Module = Line.split()[1].split(".")[0]
                else:
                    Module = Line.split()[1].split(".")[0]
                
                if Module in StandardLibs:
                    CurrentGroup = "standard"
                elif Module in ["Core", "GUI", "Utils", "Models"]:
                    CurrentGroup = "application"
                else:
                    CurrentGroup = "third_party"
                
                ImportGroups[CurrentGroup].append((LineNum, Line))
            
            # Check if we've moved past imports
            elif InImportSection and not Line.startswith(("import ", "from ")):
                # Check if there's a blank line between groups
                LastLines = set()
                for Group in ImportGroups.values():
                    if Group:
                        LastLine = Group[-1][0]
                        LastLines.add(LastLine)
                        
                        # Check the line after the last import in the group
                        if LastLine < len(Lines) and Lines[LastLine].strip():
                            Results["warnings"].append({
                                "line": LastLine + 1,
                                "message": "Import groups should be separated by blank lines.",
                                "rule": "ImportGroupSeparation"
                            })
                
                # Reset for the next potential import section
                InImportSection = False
                CurrentGroup = None
        
        # Check import group order (standard -> third-party -> application)
        if ImportGroups["standard"] and ImportGroups["third_party"]:
            LastStandardLine = ImportGroups["standard"][-1][0]
            FirstThirdPartyLine = ImportGroups["third_party"][0][0]
            
            if LastStandardLine > FirstThirdPartyLine:
                Results["warnings"].append({
                    "line": FirstThirdPartyLine,
                    "message": "Third-party imports should come after standard library imports.",
                    "rule": "ImportOrder"
                })
        
        if ImportGroups["third_party"] and ImportGroups["application"]:
            LastThirdPartyLine = ImportGroups["third_party"][-1][0]
            FirstAppLine = ImportGroups["application"][0][0]
            
            if LastThirdPartyLine > FirstAppLine:
                Results["warnings"].append({
                    "line": FirstAppLine,
                    "message": "Application imports should come after third-party imports.",
                    "rule": "ImportOrder"
                })
        
        return Results
    
    def _ValidateDocstrings(self, FilePath: str, Content: str, Lines: List[str]) -> Dict[str, Any]:
        """
        Validate docstring formatting and presence.
        
        Args:
            FilePath: Path to the Python file
            Content: File content
            Lines: File content as list of lines
            
        Returns:
            Dict[str, Any]: Validation results
        """
        Results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        try:
            Tree = ast.parse(Content, filename=FilePath)
            
            # Check module docstring
            if len(Tree.body) > 0 and not isinstance(Tree.body[0], ast.Expr) or \
               len(Tree.body) > 0 and isinstance(Tree.body[0], ast.Expr) and not isinstance(Tree.body[0].value, ast.Str):
                Results["warnings"].append({
                    "line": 1,
                    "message": "Module is missing a docstring.",
                    "rule": "ModuleDocstring"
                })
            
            # Check class and function docstrings
            for Node in ast.walk(Tree):
                if isinstance(Node, (ast.ClassDef, ast.FunctionDef)):
                    # Skip private methods and functions
                    if Node.name.startswith('_') and not Node.name.startswith('__'):
                        continue
                    
                    DocString = ast.get_docstring(Node)
                    if not DocString:
                        NodeType = "Class" if isinstance(Node, ast.ClassDef) else "Function/method"
                        Results["warnings"].append({
                            "line": Node.lineno,
                            "message": f"{NodeType} '{Node.name}' is missing a docstring.",
                            "rule": "DocstringPresence"
                        })
                    elif DocString:
                        # Check docstring format
                        DocStringLines = DocString.split('\n')
                        
                        # Check for empty line after docstring summary if multiline
                        if len(DocStringLines) > 1 and DocStringLines[1].strip():
                            Results["warnings"].append({
                                "line": Node.lineno + 1,
                                "message": f"Docstring for '{Node.name}' should have an empty line after the summary.",
                                "rule": "DocstringFormat"
                            })
                        
                        # Check for Args/Returns sections in function docstrings
                        if isinstance(Node, ast.FunctionDef) and len(Node.args.args) > 1 and not any("Args:" in Line for Line in DocStringLines):
                            Results["warnings"].append({
                                "line": Node.lineno + 1,
                                "message": f"Function '{Node.name}' has parameters but no 'Args:' section in docstring.",
                                "rule": "DocstringArgs"
                            })
                            
                        # Check if function has a return value (excluding None)
                        Returns = self._HasNonNoneReturn(Node)
                        if Returns and not any("Returns:" in Line for Line in DocStringLines):
                            Results["warnings"].append({
                                "line": Node.lineno + 1,
                                "message": f"Function '{Node.name}' has a return value but no 'Returns:' section in docstring.",
                                "rule": "DocstringReturns"
                            })
        
        except Exception as E:
            Results["warnings"].append({
                "line": 0,
                "message": f"Error during docstring validation: {str(E)}",
                "rule": "DocstringAnalysis"
            })
        
        return Results
    
    def _IsLibraryOverride(self, Node: ast.ClassDef) -> bool:
        """
        Check if a class is overriding a library class.
        
        Args:
            Node: The AST class definition node
            
        Returns:
            bool: True if the class is overriding a library class
        """
        # Check if the class inherits from library classes
        for Base in Node.bases:
            if isinstance(Base, ast.Name):
                BaseName = Base.id
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', BaseName):
                    return True
        
        return False
    
    def _IsInterfaceMethod(self, Node: ast.FunctionDef) -> bool:
        """
        Check if a function/method is an interface method that should maintain original naming.
        
        Args:
            Node: The AST function definition node
            
        Returns:
            bool: True if the function is an interface method
        """
        # Check for common interface methods
        if Node.name.startswith('visit_'):
            return True
        
        # Check for Django model methods
        if Node.name in ['save', 'delete', 'clean', 'validate_unique', 'get_absolute_url']:
            return True
        
        # Check for Flask routes
        if hasattr(Node, 'decorator_list'):
            for Decorator in Node.decorator_list:
                if isinstance(Decorator, ast.Call) and isinstance(Decorator.func, ast.Attribute):
                    if Decorator.func.attr == 'route':
                        return True
                    
        return False
    
    def _IsSystemElement(self, Name: str) -> bool:
        """
        Check if a name is a Python system element or keyword.
        
        Args:
            Name: The name to check
            
        Returns:
            bool: True if the name is a system element
        """
        # Python keywords and builtins
        Keywords = {
            "False", "None", "True", "and", "as", "assert", "async", "await", "break",
            "class", "continue", "def", "del", "elif", "else", "except", "finally",
            "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
            "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"
        }
        
        if Name in Keywords:
            return True
        
        # Check for dunder variables
        if Name.startswith('__') and Name.endswith('__'):
            return True
        
        return False
    
    def _HasNonNoneReturn(self, Node: ast.FunctionDef) -> bool:
        """
        Check if a function has a non-None return value.
        
        Args:
            Node: The AST function definition node
            
        Returns:
            bool: True if the function has a non-None return value
        """
        for SubNode in ast.walk(Node):
            if isinstance(SubNode, ast.Return) and SubNode.value is not None:
                if not isinstance(SubNode.value, ast.NameConstant) or SubNode.value.value is not None:
                    return True
        
        return False

def Main():
    """Command-line interface for file validation."""
    import argparse
    
    Parser = argparse.ArgumentParser(description="AIDEV-Deploy Validation Engine")
    Parser.add_argument("filepath", help="Path to the file to validate")
    Parser.add_argument("--standard", default="1.6", help="AIDEV-PascalCase standard version")
    
    Args = Parser.parse_args()
    
    Engine = ValidationEngine(Args.standard)
    Results = Engine.ValidateFile(Args.filepath)
    
    # Display results
    print(f"Validation Status: {Results['status']}")
    
    if Results["errors"]:
        print("\nErrors:")
        for Error in Results["errors"]:
            print(f"  Line {Error['line']}: {Error['message']}")
    
    if Results["warnings"]:
        print("\nWarnings:")
        for Warning in Results["warnings"]:
            print(f"  Line {Warning['line']}: {Warning['message']}")
    
    # Return status code
    return 0 if Results["status"] != "FAIL" else 1

if __name__ == "__main__":
    import sys
    sys.exit(Main())
