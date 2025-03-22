# AIDEV-PascalCase Naming Conventions Clarification
**Created: March 15, 2025 6:40 PM**

## Introduction

This document clarifies the application of AIDEV-PascalCase standards to project, directory, and file names. These guidelines are intended to remove ambiguity and ensure consistent application of the standards throughout the entire development ecosystem.

## The Dash (-) Character in AIDEV-PascalCase

According to the AIDEV-PascalCase standards document, the dash character (-) should only be used in specific circumstances:

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
   2025-03-09          # Correct - standard date format
   ```

4. **Avoid in All Other Cases**:
   ```
   Process-Data        # Incorrect - use ProcessData instead
   User-Input          # Incorrect - use UserInput instead
   ```

## Acronym Handling

Acronyms within identifiers follow specific rules:

1. **Standard Acronyms**: Recognized acronyms (API, DB, GUI, etc.) should be all uppercase
   ```
   APIClient           # Correct
   DbConnection        # Incorrect - should be DBConnection
   ```

2. **Project-Specific Acronyms**: For custom acronyms like "AIDEV", there are two cases:
   
   a. **When used as a standalone identifier or at the beginning**:
      ```
      AIDEV-PascalCase  # Correct - when connecting with dash
      AIdevStandards    # Correct - when incorporated into a camel/pascal case identifier
      ```
   
   b. **When used within an identifier**:
      ```
      ModelAIDevTools   # Correct
      ModelAidevTools   # Incorrect
      ```

## Applying to Project Names

Project names should follow these conventions:

1. **Single Term Projects**:
   ```
   Calculator          # Correct
   calculator          # Incorrect
   ```

2. **Multi-Term Projects**:
   ```
   ModelManager        # Correct
   Model-Manager       # Incorrect
   modelManager        # Incorrect
   ```

3. **Projects with Acronyms**:
   ```
   DBConnector         # Correct
   DbConnector         # Incorrect
   APIClient           # Correct
   ```

4. **Projects with AIDEV Acronym**:
   ```
   AIdevLintingTest    # Correct - AIDEV incorporated into the identifier
   AIDEV-LintingTest   # Correct - Only when emphasizing separation
   AidevLintingTest    # Incorrect - AIDEV is a special term
   ```

## Directory Naming

Directories should follow the same conventions as project names:

1. **Standard Directories**:
   ```
   Core/               # Correct
   Utils/              # Correct
   ui_components/      # Incorrect - should be UIComponents/
   ```

2. **Feature Directories**:
   ```
   UserAuthentication/ # Correct
   user-auth/          # Incorrect
   ```

3. **Test Directories**:
   ```
   UnitTests/          # Correct
   unit_tests/         # Incorrect
   ```

## File Naming

Source files should follow the same conventions with appropriate extensions:

1. **Python Files**:
   ```
   ModelManager.py     # Correct
   model_manager.py    # Incorrect
   ```

2. **Configuration Files**:
   ```
   VSCodeSettings.json # Correct
   vscode_settings.json # Incorrect
   ```

3. **Documentation Files**:
   ```
   ProjectOverview.md  # Correct
   project_overview.md # Incorrect
   ```

4. **Special System Files**:
   Some system or configuration files have conventional names that should be preserved:
   ```
   .gitignore          # Keep as-is
   requirements.txt    # Keep as-is
   ```

## Common Pitfalls

1. **Mixed Conventions**: Avoid mixing snake_case and PascalCase
   ```
   User_Profile.py     # Incorrect - mixed convention
   UserProfile.py      # Correct
   ```

2. **Inconsistent Acronym Handling**: Be consistent with acronym capitalization
   ```
   ApiManager.py and DBConnection.py in the same project  # Inconsistent
   APIManager.py and DBConnection.py                      # Consistent
   ```

3. **Directory/File Name Mismatch**: Directory and file names should follow the same convention
   ```
   UserAuth/user_auth.py  # Inconsistent
   UserAuth/UserAuth.py   # Consistent
   ```

## Examples from Our Projects

### Correct Examples:
```
Project:  AIdevLintingTest
├── PylintPlugins/
│   ├── __init__.py
│   ├── AIdevChecker.py
├── Samples/
│   ├── GoodSample.py
│   ├── BadSample.py
├── SetupLinting.py
├── CreateRequirements.py
├── InstallLinting.sh
```

### Incorrect Examples:
```
Project:  aidev-linting-test   # Should be AIdevLintingTest
├── pylint_plugins/            # Should be PylintPlugins/
│   ├── __init__.py
│   ├── aidev_checker.py       # Should be AIdevChecker.py
├── samples/                   # Should be Samples/
│   ├── good_sample.py         # Should be GoodSample.py
│   ├── bad_sample.py          # Should be BadSample.py
├── setup_linting.py           # Should be SetupLinting.py
├── create_requirements.py     # Should be CreateRequirements.py
├── install_linting.sh         # Should be InstallLinting.sh
```

## Conclusion

Consistent application of the AIDEV-PascalCase standards across all aspects of a project, from code to directory structure to file names, creates a cohesive and visually harmonious development environment. These clarifications should help ensure that the standards are applied correctly and consistently throughout all project elements.

---

*"Code is not merely functional—it is a visual medium that developers interact with for extended periods. The choices made in these standards prioritize the axis of symmetry, character distinction, readability at scale, and visual hierarchy."*

— Herbert J. Bowers
