#!/bin/bash
# File: GitPushUpdates.sh
# Path: AIDEV-Hub/Scripts/GitPushUpdates.sh
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-18
# Last Modified: 2025-03-18  3:30PM
# Description: Script to push updates to GitHub with formatted commit messages

# Stay in the current directory where the script is run from
# (assuming we're already in the AIDEV-Hub directory)
CURRENT_DIR=$(pwd)
echo "==== AIDEV-Hub Git Update ===="
echo "Current Directory: $CURRENT_DIR"
echo ""

# Check if this is a git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository. Make sure you're running this script from the AIDEV-Hub directory."
    exit 1
fi

# Default description includes date and time in 12-hour format
DEFAULT_DESC="Modifications $(date +"%m/%d/%y %I:%M%p")"

# Check if a custom description was provided
if [ $# -eq 0 ]; then
    # No arguments, use default description
    COMMIT_DESC="$DEFAULT_DESC"
else
    # Custom description provided
    COMMIT_DESC="$*"
fi

# Check if there are any changes to commit
if git status --porcelain | grep -q .; then
    # Show changes
    echo "Changes to be committed:"
    git status --short
    echo ""
    
    # Confirm commit
    echo "Commit message: $COMMIT_DESC"
    read -r -p "Proceed with commit and push? [Y/n] " CONFIRM
    
    if [[ "$CONFIRM" =~ ^[Nn] ]]; then
        echo "Operation cancelled."
        exit 0
    fi
    
    # Add all changes
    echo "Adding changes..."
    git add .
    
    # Commit with the selected description
    echo "Committing changes..."
    git commit -m "$COMMIT_DESC"
    
    # Push to GitHub
    echo "Pushing to GitHub..."
    git push
    
    echo ""
    echo "Changes successfully pushed to GitHub!"
    echo "Commit description: $COMMIT_DESC"
else
    echo "No changes detected. Nothing to commit."
fi

echo ""
echo "Done!"
