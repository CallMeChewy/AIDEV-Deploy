#!/bin/bash

# PushGitHub.sh - Script to automatically update a GitHub repository
# Usage: ./PushGitHub.sh [-a|--all] [-m "Custom commit message"]

# Exit on error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print error messages and exit
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Function to print success messages
success_message() {
    echo -e "${GREEN}$1${NC}"
}

# Function to print warning/info messages
info_message() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    error_exit "Git is not installed. Please install git first."
fi

# Check if we're inside a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    error_exit "Not a git repository. Please run this script from within a git repository."
fi

# Get the base project name (current folder name)
REPO_NAME=$(basename "$(pwd)")
info_message "Repository name: $REPO_NAME"

# Check if remote origin exists
if ! git remote get-url origin &> /dev/null; then
    info_message "Remote 'origin' not set. Checking if GitHub repository exists..."
    
    # Check if GitHub CLI is installed for a better experience
    if command -v gh &> /dev/null; then
        if gh auth status &> /dev/null; then
            # Check if repo exists on GitHub
            if ! gh repo view "$REPO_NAME" &> /dev/null; then
                info_message "Creating GitHub repository: $REPO_NAME..."
                gh repo create "$REPO_NAME" --public --source=. --remote=origin
            else
                info_message "GitHub repository exists but not connected. Connecting..."
                git remote add origin "https://github.com/$(gh api user | jq -r '.login')/$REPO_NAME.git"
            fi
        else
            info_message "GitHub CLI not authenticated. Please run 'gh auth login' first."
            error_exit "Please set remote origin manually: git remote add origin <github-url>"
        fi
    else
        error_exit "Remote 'origin' not set. Please set it manually: git remote add origin <github-url>"
    fi
fi

# Parse command line arguments
PUSH_ALL=false
COMMIT_MSG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            PUSH_ALL=true
            shift
            ;;
        -m|--message)
            if [[ -z "$2" || "$2" == -* ]]; then
                error_exit "No message provided with -m|--message option"
            fi
            COMMIT_MSG="$2"
            shift 2
            ;;
        -m=*|--message=*)
            COMMIT_MSG="${1#*=}"
            shift
            ;;
        *)
            # For backward compatibility, treat remaining args as commit message
            if [[ -z "$COMMIT_MSG" ]]; then
                COMMIT_MSG="$*"
                break
            else
                error_exit "Unknown option: $1"
            fi
            ;;
    esac
done

# Get current date and time in MM/DD/YY format and 12hr time
CURRENT_DATE=$(date +"%m/%d/%y")
CURRENT_TIME=$(date +"%I:%M %p")
DEFAULT_MSG="Updated: $CURRENT_DATE  $CURRENT_TIME"

# Use custom commit message if provided, otherwise use default
if [[ -z "$COMMIT_MSG" ]]; then
    COMMIT_MSG="$DEFAULT_MSG"
fi
info_message "Commit message: $COMMIT_MSG"

# Stage all changes
info_message "Staging changes..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    info_message "No changes to commit."
    exit 0
fi

# Commit changes
info_message "Committing changes..."
git commit -m "$COMMIT_MSG"

# Push to GitHub
info_message "Pushing to GitHub..."
if [[ "$PUSH_ALL" = true ]]; then
    info_message "Pushing all branches..."
    git push --all origin
else
    git push origin "$(git branch --show-current)"
fi

success_message "✅ Successfully pushed to GitHub repository: $REPO_NAME"
