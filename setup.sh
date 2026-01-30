#!/bin/bash

# Setup script for Government Job Updates Telegram Bot

echo "🚀 Setting up Government Job Updates Telegram Bot..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID"
fi

# Initialize database
echo "🗃️  Initializing database..."
python -c "from database.db import db_manager; db_manager.initialize_database()"

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your Telegram bot token and channel ID"
echo "2. Run the bot with: python bot/main.py"
echo "3. For production, use: docker-compose up -d"
