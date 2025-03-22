# File: RenameAddTheseFiles.py
# Path: SysUtils/RenameAddTheseFiles.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-20
# Last Modified: 2025-03-20  10:45AM
# Description: Utility to rename files based on their content

import os
import re
import shutil

def RenameFiles(SourceDir, DestDir):
    """
    Reads files from source directory, renames them based on content,
    and saves them to destination directory.
    
    Args:
        SourceDir (str): Source directory containing files to rename
        DestDir (str): Destination directory for renamed files
    """
    if not os.path.exists(DestDir):
        os.makedirs(DestDir)

    for Filename in os.listdir(SourceDir):
        SourcePath = os.path.join(SourceDir, Filename)

        if not os.path.isfile(SourcePath):
            continue

        try:
            with open(SourcePath, 'r', encoding='utf-8') as File:
                Content = File.read()

            # Determine file type and extract filename
            if Filename.endswith('.md'):  # Markdown file
                # Extract report header (first heading)
                NewFilename = ExtractMarkdownFilename(SourcePath, Filename)
            elif Filename.endswith('.py'):  # Python file
                # Extract filename from "# File:" line
                NewFilename = ExtractPythonFilename(SourcePath, Filename)
            else:
                # If not Markdown or Python, keep the original filename
                NewFilename = Filename

            # Handle duplicates
            DestPath = os.path.join(DestDir, NewFilename)
            if os.path.exists(DestPath):
                DestPath = HandleDuplicateFilename(DestDir, NewFilename)
                NewFilename = os.path.basename(DestPath)

            # Save the file
            shutil.copy2(SourcePath, DestPath)  # Copy with metadata
            print(f"Renamed '{Filename}' to '{NewFilename}' and saved to '{DestDir}'")

        except Exception as e:
            print(f"Error processing '{Filename}': {e}")

def ExtractMarkdownFilename(SourcePath, DefaultFilename):
    """
    Extract a filename from a Markdown file based on its first heading.
    
    Args:
        SourcePath (str): Path to the Markdown file
        DefaultFilename (str): Default filename to use if extraction fails
        
    Returns:
        str: Extracted filename with .md extension
    """
    with open(SourcePath, 'r', encoding='utf-8') as File:
        Content = File.read()
    
    Match = re.search(r'#\s+(.*)', Content)
    if Match:
        NewFilename = Match.group(1).strip()
    else:
        NewFilename = DefaultFilename  # Use original filename if no header found
    
    NewFilename = re.sub(r'[\\\\/*?"<>|:]', '-', NewFilename)
    if not NewFilename.endswith('.md'):
        NewFilename += '.md'
    
    return NewFilename

def ExtractPythonFilename(SourcePath, DefaultFilename):
    """
    Extract a filename from a Python file based on its "# File:" comment.
    
    Args:
        SourcePath (str): Path to the Python file
        DefaultFilename (str): Default filename to use if extraction fails
        
    Returns:
        str: Extracted filename with .py extension
    """
    with open(SourcePath, 'r', encoding='utf-8') as File:
        Content = File.read()
    
    Match = re.search(r'# File:\s*(.*).py', Content)
    if Match:
        NewFilename = Match.group(1).strip()
        NewFilename = NewFilename.replace('File-', '').strip()
        NewFilename = re.sub(r'[\\\\/*?"<>|:]', '-', NewFilename) + '.py'
    else:
        NewFilename = DefaultFilename  # Use original filename if no filename line found
    
    return NewFilename

def HandleDuplicateFilename(DestDir, Filename):
    """
    Handle duplicate filenames by appending an incremental number.
    
    Args:
        DestDir (str): Destination directory
        Filename (str): Original filename
        
    Returns:
        str: Path to a non-conflicting filename
    """
    BaseName, Ext = os.path.splitext(Filename)
    Counter = 1
    
    while True:
        NewFilename = f"{BaseName}_{Counter}{Ext}"
        DestPath = os.path.join(DestDir, NewFilename)
        
        if not os.path.exists(DestPath):
            return DestPath
        
        Counter += 1

def Main():
    """Main entry point for the application."""
    SourceDirectory = 'AddThese'
    DestinationDirectory = 'AddTheseNow'
    RenameFiles(SourceDirectory, DestinationDirectory)

if __name__ == "__main__":
    Main()
