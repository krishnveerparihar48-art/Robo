#!/bin/bash

# ============================================================================
# Government Job Updates Telegram Bot - Termux Startup Script
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Government Job Updates Bot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================================================
# Step 1: Check Python Installation
# ============================================================================

echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"

if ! command -v python &> /dev/null; then
    echo -e "${RED}Python not found. Installing Python...${NC}"
    pkg install python -y
else
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}Python $PYTHON_VERSION installed${NC}"
fi

# ============================================================================
# Step 2: Update and Upgrade Packages
# ============================================================================

echo -e "${YELLOW}[2/6] Updating packages...${NC}"
pkg update -y
pkg upgrade -y

# ============================================================================
# Step 3: Install Required Dependencies
# ============================================================================

echo -e "${YELLOW}[3/6] Installing Python dependencies...${NC}"

# Install required system packages
pkg install -y git libjpeg-turbo zlib

# Install Python packages
echo "Installing python-telegram-bot..."
pip install python-telegram-bot --quiet

echo "Installing beautifulsoup4..."
pip install beautifulsoup4 --quiet

echo "Installing requests..."
pip install requests --quiet

echo "Installing schedule..."
pip install schedule --quiet

echo "Installing pytz..."
pip install pytz --quiet

echo -e "${GREEN}All dependencies installed successfully${NC}"

# ============================================================================
# Step 4: Create Necessary Directories
# ============================================================================

echo -e "${YELLOW}[4/6] Creating directories...${NC}"

# Create database directory
if [ ! -d "database" ]; then
    mkdir -p database
    echo "Created database directory"
else
    echo "Database directory already exists"
fi

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "Created logs directory"
else
    echo "Logs directory already exists"
fi

# Create backups directory
if [ ! -d "backups" ]; then
    mkdir -p backups
    echo "Created backups directory"
else
    echo "Backups directory already exists"
fi

# ============================================================================
# Step 5: Initialize Database Files
# ============================================================================

echo -e "${YELLOW}[5/6] Initializing database files...${NC}"

# Create posted_jobs.json if not exists
if [ ! -f "database/posted_jobs.json" ]; then
    echo '{}' > database/posted_jobs.json
    echo "Created posted_jobs.json"
else
    echo "posted_jobs.json already exists"
fi

# Create verified_users.json if not exists
if [ ! -f "database/verified_users.json" ]; then
    echo '{}' > database/verified_users.json
    echo "Created verified_users.json"
else
    echo "verified_users.json already exists"
fi

# ============================================================================
# Step 6: Check Configuration
# ============================================================================

echo -e "${YELLOW}[6/6] Checking configuration...${NC}"

# Check if config.py exists and has valid token
if [ -f "config.py" ]; then
    if grep -q "YOUR_BOT_TOKEN_HERE" config.py; then
        echo -e "${RED}WARNING: BOT_TOKEN not configured in config.py${NC}"
        echo "Please edit config.py and add your bot token from @BotFather"
        echo ""
        read -p "Press Enter to continue anyway or Ctrl+C to exit..."
    else
        echo -e "${GREEN}Configuration file found${NC}"
    fi
else
    echo -e "${RED}ERROR: config.py not found${NC}"
    exit 1
fi

# ============================================================================
# Start Bot with Auto-Restart
# ============================================================================

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Bot...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Auto-restart loop
while true; do
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] Starting bot...${NC}"
    
    # Run bot
    python bot.py
    
    # If bot exits, wait and restart
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}Bot stopped normally${NC}"
        break
    else
        echo -e "${RED}Bot crashed with exit code: $EXIT_CODE${NC}"
        echo -e "${YELLOW}Restarting in 10 seconds...${NC}"
        sleep 10
    fi
done

echo ""
echo -e "${BLUE}Bot shutdown complete${NC}"
