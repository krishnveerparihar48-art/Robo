# Government Job Updates Telegram Bot - Complete Setup Guide

## 📋 Overview

A complete Telegram bot for government job updates with:
- Automatic job scraping from multiple websites
- Channel verification system
- Deadline reminders
- State and category filtering
- Admin commands
- Auto-restart capability

## 🚀 Quick Start

### Prerequisites

1. **Telegram Account**
2. **Bot Token** from @BotFather
3. **Telegram Channel** for job updates
4. **Python 3.8+** installed

### Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the **BOT_TOKEN** provided
5. Note your Telegram **USER_ID** from @userinfobot

### Step 2: Create Telegram Channel

1. Create a new channel in Telegram
2. Add your bot as administrator
3. Get your **CHANNEL_ID** using @userinfobot
4. Note your **CHANNEL_USERNAME**

### Step 3: Configure the Bot

1. Edit `config.py`:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ADMIN_ID = 123456789  # Your user ID
   CHANNEL_ID = -1001234567890  # Your channel ID
   CHANNEL_USERNAME = "@yourchannel"  # Your channel username
   ```

### Step 4: Install Dependencies

**For Linux/Mac/Windows:**
```bash
pip install -r requirements.txt
```

**For Termux:**
```bash
bash run.sh
```

### Step 5: Run the Bot

**Linux/Mac/Windows:**
```bash
python bot.py
```

**Termux:**
```bash
bash run.sh
```

## 📁 Project Structure

```
government-job-bot/
├── config.py              # Configuration file
├── database.py            # Database operations
├── scraper.py             # Web scraping module
├── formatter.py           # Message formatting
├── bot.py                 # Main bot application
├── admin.py               # Admin commands
├── run.sh                 # Termux startup script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── SETUP_GUIDE.md        # Setup instructions
├── database/             # Database directory (auto-created)
│   ├── posted_jobs.json  # Posted jobs database
│   └── verified_users.json # Verified users database
├── logs/                 # Log files (auto-created)
│   ├── bot.log           # Bot activity log
│   └── errors.log        # Error log
└── backups/              # Database backups (auto-created)
```

## 🔧 Configuration Details

### Bot Credentials (config.py)

```python
# Required - Get these from Telegram
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
ADMIN_ID = 123456789  # Your numeric Telegram user ID
CHANNEL_ID = -1001234567890  # Channel ID (negative number)
CHANNEL_USERNAME = "@yourchannel"  # Channel username
```

### Websites to Monitor

```python
WEBSITES_TO_MONITOR = {
    "sarkari_result": {
        "name": "Sarkari Result",
        "url": "https://www.sarkariresult.com",
        "active": True  # Set to False to disable
    },
    # Add more websites as needed
}
```

### Scraping Settings

```python
SCRAPE_INTERVAL_HOURS = 3      # How often to scrape (default: 3 hours)
REQUEST_DELAY_SECONDS = 3      # Delay between requests (default: 3 sec)
MAX_RETRIES = 3                 # Retry failed requests (default: 3)
REQUEST_TIMEOUT = 30            # Request timeout (default: 30 sec)
```

## 📱 User Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot and verify channel membership |
| `/verify` | Manually verify channel subscription |
| `/latest` | Get 5 most recent job updates |
| `/state [name]` | Get jobs by state (e.g., `/state up`) |
| `/category [type]` | Get jobs by category (e.g., `/category bank jobs`) |
| `/categories` | View all available job categories |
| `/states` | View all available states |
| `/websites` | View monitored websites |
| `/help` | Show help message |

## 🔐 Admin Commands

Only accessible to the configured ADMIN_ID:

| Command | Description |
|---------|-------------|
| `/admin_post <title> <link> [deadline]` | Manually post a job |
| `/admin_stats` | Show bot statistics |
| `/admin_update` | Force update job database |
| `/admin_test [message]` | Test channel posting |
| `/admin_users` | Show user statistics |
| `/admin_backup` | Create manual backup |
| `/admin_help` | Show admin help |

## 📊 Message Formats

### 1. Breaking News Format
For newly posted jobs with "Apply Now" button

### 2. Last 3 Days Format
Urgent notification for jobs closing in 3 days

### 3. Final Day Format
Critical alert for jobs closing today

### 4. Date Extended Format
Announcement when job deadline is extended

### 5. Complete Format (A-G)
Full job details with sections:
- A: Post Name/Vacancy
- B: Eligibility/Education
- C: Age Limit
- D: Salary/Pay Scale
- E: Important Dates
- F: Application Fee
- G: Selection Process

## 🧪 Testing

### Test 1: Bot Startup
```bash
python bot.py
```
**Expected:** Bot starts without errors, logs show "Bot polling started"

### Test 2: User Verification
1. Send `/start` to your bot
2. Join your channel
3. Click "Verify Me" button
**Expected:** Welcome message appears

### Test 3: Job Scraping
```bash
python -c "import scraper; jobs = scraper.scrape_all_websites(); print(f'Found {len(jobs)} jobs')"
```
**Expected:** Number of jobs found is printed

### Test 4: Channel Posting
1. Use `/admin_test` command
2. Check your channel
**Expected:** Test message appears in channel

### Test 5: Database Operations
```bash
python -c "import database; print('Jobs:', len(database.load_posted_jobs())); print('Users:', database.get_verified_user_count())"
```
**Expected:** Shows job and user counts

### Test 6: Admin Commands
1. Try `/admin_stats`
2. Try `/admin_users`
**Expected:** Statistics displayed (admin only)

## 🌐 Termux Deployment

### Complete Setup Commands

```bash
# Update Termux
pkg update && pkg upgrade

# Install Python
pkg install python git

# Clone or copy project files
# (Assuming you're in the project directory)

# Make startup script executable
chmod +x run.sh

# Run the bot
bash run.sh
```

### Keep Bot Running in Background

```bash
# Using tmux
pkg install tmux
tmux new -s jobbot
bash run.sh
# Press Ctrl+B, then D to detach

# To reattach
tmux attach -t jobbot
```

### Auto-Start on Termux Boot

Create `~/.termux/boot/jobbot.sh`:
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/government-job-bot
bash run.sh
```

## 🔍 Troubleshooting

### Bot won't start
- Check BOT_TOKEN is correct
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check logs in `logs/errors.log`

### Scraping fails
- Check internet connection
- Verify website URLs are accessible
- Check logs for specific errors

### Channel posting fails
- Verify CHANNEL_ID is correct
- Ensure bot is admin in channel
- Check bot permissions

### Verification fails
- Ensure user has joined the channel
- Check CHANNEL_USERNAME is correct
- Verify bot has `getChatMember` permission

### Database errors
- Ensure `database/` directory exists and is writable
- Check file permissions
- Try deleting and recreating JSON files

## 📊 Monitoring

### View Logs
```bash
# Bot activity
tail -f logs/bot.log

# Errors only
tail -f logs/errors.log
```

### Check Statistics
Use `/admin_stats` command or check database directly:
```bash
python -c "import database; print(database.get_statistics())"
```

### Manual Backup
```bash
python -c "import database; database.backup_database()"
```

## 🔄 Updating

1. Stop the bot
2. Pull latest changes (if using git)
3. Update dependencies: `pip install -r requirements.txt --upgrade`
4. Update config.py if needed
5. Run database backup
6. Restart bot: `python bot.py`

## 📝 Notes

- **Timezone:** All times are in IST (Asia/Kolkata)
- **Rate Limiting:** Bot adds delays between requests to respect servers
- **Duplicates:** Jobs are tracked by unique ID to avoid reposting
- **Backups:** Automatic backups created daily, keeps last 10
- **Logging:** All actions and errors are logged with timestamps

## 🔒 Security

- Never share your BOT_TOKEN
- Keep ADMIN_ID private
- Don't commit config.py with real tokens to version control
- Use `.env` file for sensitive data (optional)
- Regularly review verified users list

## 📞 Support

For issues or questions:
- Check `logs/errors.log` for error details
- Review this README and SETUP_GUIDE.md
- Ensure all prerequisites are met
- Verify configuration settings

## 📜 License

This project is provided as-is for educational purposes.

---

**Happy Job Hunting!** 🎯
