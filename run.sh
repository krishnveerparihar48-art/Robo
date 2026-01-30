#!/bin/bash

# Configuration
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$DIR/venv"
LOG_DIR="$DIR/logs"
BACKUP_DIR="$DIR/backups"

# Ensure directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$BACKUP_DIR"

echo "Directory: $DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 could not be found. Please install it (pkg install python)."
    exit 1
fi

# Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate Venv
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install Dependencies
echo "Installing dependencies..."
pip install -r "$DIR/requirements.txt"

# Run Bot with Auto-Restart
echo "Starting Bot..."
while true; do
    python "$DIR/bot.py"
    
    EXIT_CODE=$?
    echo "Bot stopped with exit code $EXIT_CODE. Restarting in 5 seconds..."
    sleep 5
done
