# File: TestValidation.py
# Path: AIDEV-Deploy/Tests/TestValidation.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:35PM
# Description: Tests for the ValidationEngine component

"""
TestValidation Module

This module contains tests for the ValidationEngine component to ensure
it correctly validates files according to the AIDEV-PascalCase-1.6 standard.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Add project root to path
ProjectRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ProjectRoot)

from Core.ValidationEngine import ValidationEngine

class TestValidationEngine(unittest.TestCase):
    """Test case for ValidationEngine."""
    
    def setUp(self):
        """Set up test environment."""
        self.ValidationEngine = ValidationEngine()
        self.TempDir = tempfile.TemporaryDirectory()
        self.TempPath = self.TempDir.name
    
    def tearDown(self):
        """Clean up test environment."""
        self.TempDir.cleanup()
    
    def test_validate_python_with_correct_header(self):
        """Test validating a Python file with correct header."""
        # Create a valid Python file
        ValidFilePath = os.path.join(self.TempPath, "ValidFile.py")
        with open(ValidFilePath, 'w') as File:
            File.write("""# File: ValidFile.py
# Path: Project/ValidFile.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:30PM
# Description: This is a valid Python file

\"\"\"
This is a valid Python file with a correct header.
\"\"\"

def ProcessData(InputString: str) -> str:
    \"\"\"
    Process the input string.
    
    Args:
        InputString: The string to process
        
    Returns:
        str: The processed string
    \"\"\"
    Result = InputString.upper()
    return Result
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(ValidFilePath)
        
        # Check results
        self.assertEqual(Result["status"], "PASS")
        self.assertEqual(len(Result["errors"]), 0)
        self.assertEqual(len(Result["warnings"]), 0)
    
    def test_validate_python_with_missing_header(self):
        """Test validating a Python file with missing header."""
        # Create a Python file with missing header
        InvalidFilePath = os.path.join(self.TempPath, "MissingHeader.py")
        with open(InvalidFilePath, 'w') as File:
            File.write("""
\"\"\"
This Python file has no header.
\"\"\"

def process_data(input_string):
    \"\"\"Process the input string.\"\"\"
    result = input_string.upper()
    return result
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(InvalidFilePath)
        
        # Check results
        self.assertEqual(Result["status"], "FAIL")
        self.assertTrue(any("header" in Error["message"].lower() for Error in Result["errors"]))
    
    def test_validate_python_with_incorrect_case(self):
        """Test validating a Python file with incorrect case in names."""
        # Create a Python file with incorrect case in function and variable names
        InvalidFilePath = os.path.join(self.TempPath, "IncorrectCase.py")
        with open(InvalidFilePath, 'w') as File:
            File.write("""# File: IncorrectCase.py
# Path: Project/IncorrectCase.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:30PM
# Description: This file has incorrect case in names

\"\"\"
This Python file has incorrect case in function and variable names.
\"\"\"

def process_data(input_string):
    \"\"\"Process the input string.\"\"\"
    result = input_string.upper()
    return result
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(InvalidFilePath)
        
        # Check results
        self.assertEqual(Result["status"], "FAIL")
        self.assertTrue(any("function" in Error["message"].lower() and "case" in Error["message"].lower() 
                          for Error in Result["errors"]))
    
    def test_validate_python_with_correct_case(self):
        """Test validating a Python file with correct case in names."""
        # Create a Python file with correct PascalCase
        ValidFilePath = os.path.join(self.TempPath, "CorrectCase.py")
        with open(ValidFilePath, 'w') as File:
            File.write("""# File: CorrectCase.py
# Path: Project/CorrectCase.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:30PM
# Description: This file has correct case in names

\"\"\"
This Python file has correct PascalCase in function and variable names.
\"\"\"

def ProcessData(InputString):
    \"\"\"
    Process the input string.
    
    Args:
        InputString: String to process
        
    Returns:
        Processed string
    \"\"\"
    Result = InputString.upper()
    return Result
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(ValidFilePath)
        
        # Check results - should pass or have only warnings
        self.assertNotEqual(Result["status"], "FAIL")
    
    def test_validate_python_with_syntax_error(self):
        """Test validating a Python file with syntax error."""
        # Create a Python file with syntax error
        InvalidFilePath = os.path.join(self.TempPath, "SyntaxError.py")
        with open(InvalidFilePath, 'w') as File:
            File.write("""# File: SyntaxError.py
# Path: Project/SyntaxError.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:30PM
# Description: This file has a syntax error

\"\"\"
This Python file has a syntax error.
\"\"\"

def ProcessData(InputString):
    \"\"\"Process the input string.\"\"\"
    Result = InputString.upper(
    return Result
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(InvalidFilePath)
        
        # Check results
        self.assertEqual(Result["status"], "FAIL")
        self.assertTrue(any("syntax" in Error["message"].lower() for Error in Result["errors"]))
    
    def test_validate_python_with_missing_docstring(self):
        """Test validating a Python file with missing docstring."""
        # Create a Python file with missing docstring
        FilePath = os.path.join(self.TempPath, "MissingDocstring.py")
        with open(FilePath, 'w') as File:
            File.write("""# File: MissingDocstring.py
# Path: Project/MissingDocstring.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:30PM
# Description: This file has missing docstrings

class DataProcessor:
    def ProcessData(self, InputString):
        Result = InputString.upper()
        return Result
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(FilePath)
        
        # Check results - should have docstring warnings
        self.assertTrue(any("docstring" in Warning["message"].lower() for Warning in Result["warnings"]))
    
    def test_validate_python_with_interface_methods(self):
        """Test validating a Python file with interface methods."""
        # Create a Python file with interface methods
        FilePath = os.path.join(self.TempPath, "InterfaceMethods.py")
        with open(FilePath, 'w') as File:
            File.write("""# File: InterfaceMethods.py
# Path: Project/InterfaceMethods.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-21
# Last Modified: 2025-03-21  5:30PM
# Description: This file has interface methods

\"\"\"
This Python file has interface methods which should maintain their original naming.
\"\"\"

import ast

class CustomVisitor(ast.NodeVisitor):
    \"\"\"Custom AST visitor implementation.\"\"\"
    
    def visit_ClassDef(self, Node):
        \"\"\"Visit a class definition node.\"\"\"
        ClassName = Node.name
        self.ProcessClass(ClassName)
        self.generic_visit(Node)
    
    def ProcessClass(self, ClassName):
        \"\"\"Process a class name.\"\"\"
        return ClassName.upper()
""")
        
        # Validate the file
        Result = self.ValidationEngine.ValidateFile(FilePath)
        
        # Check results - interface methods should not cause errors
        FunctionErrors = [Error for Error in Result["errors"] 
                        if "function" in Error["message"].lower() and "case" in Error["message"].lower()]
        
        # No errors for visit_ClassDef (interface method)
        self.assertFalse(any("visit_classdef" in Error["message"].lower() for Error in FunctionErrors))

if __name__ == "__main__":
    unittest.main()
