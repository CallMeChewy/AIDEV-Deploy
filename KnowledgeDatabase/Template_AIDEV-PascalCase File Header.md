# AIDEV-PascalCase File Header Template
**Created: March 17, 2025 8:45 AM**
**Last Modified: March 17, 2025  8:45 AM**

## Current Standard Header Format

```python
# File: {FileName}.py
# Path: {ProjectName}/{ModulePath}/{FileName}.py
# Standard: AIDEV-PascalCase-1.6
# Created: YYYY-MM-DD
# Last Modified: YYYY-MM-DD  HH:MM{AM|PM}
# Description: {BriefDescription}
```

## Important Notes

1. **Version Number**: Always use the current standards version (currently 1.6)

2. **Timestamp Format Requirements**:
   - Exactly two spaces between date and time in the "Last Modified" line
   - 12-hour time format with AM/PM suffix (not 24-hour)
   - No leading zero in hours (e.g., 9:30AM not 09:30AM)
   - No seconds in the time

3. **When to Update**:
   - Update the "Last Modified" timestamp EVERY time you modify the file
   - Do not update the "Created" date once it's set

4. **Path Format**:
   - Use forward slashes (/) in the path even on Windows
   - Include the project name as the first component
   - Be consistent with directory naming

5. **Description Guidelines**:
   - Keep the description brief but informative (one line)
   - Focus on the purpose of the file, not implementation details
   - Begin with a verb (e.g., "Manages", "Implements", "Provides")

## Examples

### Module File Example:

```python
# File: DatabaseManager.py
# Path: AIDEV-Validate/Database/DatabaseManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-16
# Last Modified: 2025-03-17  8:45AM
# Description: Manages database operations for tracking files, symbols, and violations
```

### Main File Example:

```python
# File: Main.py
# Path: AIDEV-Validate/Main.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-16
# Last Modified: 2025-03-17  8:45AM
# Description: Main entry point for the AIDEV-Validate tool
```

## Automated Validation

The FileScanner module validates headers with the following regex pattern:

```python
HeaderPattern = r'# File: .+\.py\n# Path: .+\n# Standard: AIDEV-PascalCase-[0-9]+\.[0-9]+\n# Created: [0-9]{4}-[0-9]{2}-[0-9]{2}\n# Last Modified: [0-9]{4}-[0-9]{2}-[0-9]{2}  [0-9]{1,2}:[0-9]{2}(?:AM|PM)\n# Description: .+'
```

## Using with AI Assistants

When working with AI assistants, include the following instructions:

1. "Please update all file headers to match the current AIDEV-PascalCase-1.6 format"
2. "Remember to update the Last Modified timestamp to the current date and time"
3. "Keep the Created date as is unless creating a new file"

These instructions help ensure consistency across all project files and maintain an accurate modification history.

---

*Note: This template should be updated whenever a new version of the AIDEV-PascalCase standard is released.*
