#!/bin/bash
# File: CodebaseSummary.sh
# Path: OllamaModelEditor/CodebaseSummary.sh
# Created: 2025-03-14
# Description: Generate a comprehensive codebase snapshot in a structured format

# Create timestamp for the output filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="CodebaseSummary_${TIMESTAMP}.txt"

# Ensure script has execution permissions
if [[ ! -x "$0" ]]; then
    chmod +x "$0"
    echo "Added execute permissions to script"
fi

# Check if the tree command is available
if ! command -v tree &> /dev/null; then
    echo "Error: The 'tree' command is required but not found. Please install it first."
    exit 1
fi

# Start generating the file
echo "Generating codebase summary to ${OUTPUT_FILE}..."

# Create temp files for building the summary
TEMP_DIR=$(mktemp -d)
HEADER_FILE="${TEMP_DIR}/header.txt"
STRUCTURE_FILE="${TEMP_DIR}/structure.txt"
FILES_LIST="${TEMP_DIR}/files_list.txt"
FILES_CONTENT="${TEMP_DIR}/files_content.txt"

# Create the header
cat > "$HEADER_FILE" << 'EOF'
This file is a comprehensive codebase snapshot for the OllamaModelEditor project, generated to facilitate analysis and development.

================================================================
File Summary
================================================================

Purpose:
--------
This document provides a consolidated view of the project's Python source code, 
excluding any files specified in the .gitignore file. It serves as a reference 
for developers, making it easier to understand the codebase structure and 
functionality in a single document.

File Format:
------------
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A separator line (================)
  b. The file path (File: path/to/file)
  c. Another separator line
  d. The full contents of the file
  e. A blank line
5. List of Progeam Files

EOF

# Generate directory structure using tree
echo "Generating directory structure..."
tree -f . > "$STRUCTURE_FILE"

# Create the files section header
echo "================================================================" > "$FILES_CONTENT"
echo "Files" >> "$FILES_CONTENT"
echo "================================================================" >> "$FILES_CONTENT"
echo "" >> "$FILES_CONTENT"

# Find all Python files, respecting .gitignore and excluding .venv
echo "Finding Python files..."
find . -name "*.py" -type f -not -path "./.venv/*" -not -path "./CurrentMods/*" -not -path "./SimpleTest.py" -not -path "./test_pyside.py" | sort > "$FILES_LIST"

# Process each Python file
echo "Processing Python files..."
while read -r FILE; do
    if [ -f "$FILE" ]; then
        echo "================" >> "$FILES_CONTENT"
        echo "File: ${FILE:2}" >> "$FILES_CONTENT"
        echo "================" >> "$FILES_CONTENT"
        cat "$FILE" >> "$FILES_CONTENT"
        echo "" >> "$FILES_CONTENT"
    fi
done < "$FILES_LIST"

# Combine all parts into the final file
cat "$HEADER_FILE" > "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
echo "Directory Structure" >> "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
cat "$STRUCTURE_FILE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
cat "$FILES_CONTENT" >> "$OUTPUT_FILE"

echo "Codebase summary generated: ${OUTPUT_FILE}"

# Clean up temporary files
echo "It contains $(grep -c "^File: " "$OUTPUT_FILE") Python files."

# List Python files included
echo "" >> "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
echo "List of Program Files" >> "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Python files included:" >> "$OUTPUT_FILE"
PY_FILES=$(cat "$FILES_LIST")
echo "$PY_FILES" >> "$OUTPUT_FILE"

# Count the number of Python files
NUM_PY_FILES=$(wc -l < "$FILES_LIST")

echo "" >> "$OUTPUT_FILE"
echo "There are ${NUM_PY_FILES} Python (.py) files included in the Files section of the CodebaseSummary document." >> "$OUTPUT_FILE"

# Clean up temporary files
rm -rf "$TEMP_DIR"
