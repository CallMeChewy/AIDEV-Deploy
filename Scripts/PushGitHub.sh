#!/bin/bash

# PushGitHub.sh - Script to automatically update a GitHub repository
# Usage: ./PushGitHub.sh [-a|--all] [-i|--initial] [-r|--repo "repo_name"] [-m "Custom commit message"]

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
    info_message "Not a git repository. Initializing git repository..."
    git init
    info_message "Git repository initialized."
fi

# Parse command line arguments
PUSH_ALL=false
COMMIT_MSG=""
INITIAL_COMMIT=false
CUSTOM_REPO=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            PUSH_ALL=true
            shift
            ;;
        -i|--initial)
            INITIAL_COMMIT=true
            shift
            ;;
        -r|--repo)
            if [[ -z "$2" || "$2" == -* ]]; then
                error_exit "No repository name provided with -r|--repo option"
            fi
            CUSTOM_REPO="$2"
            shift 2
            ;;
        -r=*|--repo=*)
            CUSTOM_REPO="${1#*=}"
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

# Get the base project name (current folder name)
if [[ -z "$CUSTOM_REPO" ]]; then
    REPO_NAME=$(basename "$(pwd)")
else
    REPO_NAME="$CUSTOM_REPO"
fi
info_message "Repository name: $REPO_NAME"

# Make sure there's a default branch (for new repos)
if ! git rev-parse --verify HEAD &> /dev/null; then
    info_message "No commits yet. This appears to be a new repository."
    INITIAL_COMMIT=true
fi

# Check if remote origin exists or if it's incorrect
if ! git remote get-url origin &> /dev/null || git remote get-url origin | grep -v "$REPO_NAME" > /dev/null; then
    if git remote get-url origin &> /dev/null; then
        CURRENT_REMOTE=$(git remote get-url origin)
        info_message "Current remote: $CURRENT_REMOTE"
        info_message "Repository name mismatch. Updating remote..."
        git remote remove origin
    else
        info_message "Remote 'origin' not set. Checking if GitHub repository exists..."
    fi
    
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
            info_message "Attempting to add remote manually..."
            # Try to get username from git config
            GIT_USER=$(git config --get user.name)
            if [[ -n "$GIT_USER" ]]; then
                git remote add origin "https://github.com/$GIT_USER/$REPO_NAME.git"
                info_message "Added remote: https://github.com/$GIT_USER/$REPO_NAME.git"
                info_message "If this is incorrect, please set it manually with: git remote set-url origin <github-url>"
            else
                error_exit "Please set remote origin manually: git remote add origin <github-url>"
            fi
        fi
    else
        # Try to add remote based on GitHub username from Git config
        GIT_USER=$(git config --get user.name)
        if [[ -n "$GIT_USER" ]]; then
            git remote add origin "https://github.com/$GIT_USER/$REPO_NAME.git"
            info_message "Added remote: https://github.com/$GIT_USER/$REPO_NAME.git"
            info_message "If this is incorrect, please set it manually with: git remote set-url origin <github-url>"
        else
            error_exit "Remote 'origin' not set. Please set it manually: git remote add origin <github-url>"
        fi
    fi
fi

# Get current date and time in MM/DD/YY format and 12hr time
CURRENT_DATE=$(date +"%m/%d/%y")
CURRENT_TIME=$(date +"%I:%M %p")

# Set appropriate default message
if [[ "$INITIAL_COMMIT" = true ]]; then
    DEFAULT_MSG="Initial commit"
else
    DEFAULT_MSG="Updated: $CURRENT_DATE  $CURRENT_TIME"
fi

# Use custom commit message if provided, otherwise use default
if [[ -z "$COMMIT_MSG" ]]; then
    COMMIT_MSG="$DEFAULT_MSG"
fi
info_message "Commit message: $COMMIT_MSG"

# Stage all changes
info_message "Staging changes..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet && [[ "$INITIAL_COMMIT" != true ]]; then
    # For non-initial commits, check if there are any untracked files
    if [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
        info_message "No changes to commit."
        exit 0
    else
        info_message "Found untracked files. Adding according to gitignore rules..."
    fi
fi

# Commit changes
info_message "Committing changes..."
git commit -m "$COMMIT_MSG"

# Push to GitHub
info_message "Pushing to GitHub..."
if [[ "$INITIAL_COMMIT" = true ]]; then
    info_message "Setting up initial branch and pushing..."
    # Ensure we have a branch name (default to main if not set)
    BRANCH_NAME=$(git branch --show-current)
    if [[ -z "$BRANCH_NAME" ]]; then
        BRANCH_NAME="main"
        git checkout -b "$BRANCH_NAME"
    fi
    git push -u origin "$BRANCH_NAME"
elif [[ "$PUSH_ALL" = true ]]; then
    info_message "Pushing all branches..."
    git push --all origin
else
    git push origin "$(git branch --show-current)"
fi

success_message "✅ Successfully pushed to GitHub repository: $REPO_NAME"
