# 🤖 Government Job Updates Telegram Bot

A comprehensive Telegram bot for automatically monitoring and posting government job updates from multiple sources.

## ✨ Features

- **🌐 Multi-Website Scraping**: Automatically scrapes jobs from Sarkari Result, Free Job Alert, Employment News, and more
- **📢 Channel Verification**: Requires users to join channel before accessing features
- **🔔 Deadline Reminders**: Automatic notifications for jobs with 3 days remaining and final day alerts
- **🗺️ State Filtering**: Get jobs by state (UP, Bihar, Delhi, MP, Rajasthan, etc.)
- **📚 Category Filtering**: Browse jobs by category (Bank, Railway, SSC, UPSC, etc.)
- **🎯 Multiple Message Formats**: Breaking news, urgent alerts, complete details (A-G format)
- **🔗 Apply Now Buttons**: Direct links to official application pages
- **📊 Admin Panel**: Administrative commands for manual posting and statistics
- **💾 Database Backup**: Automatic daily backups with retention policy
- **🔄 Auto-Restart**: Continuously running with crash recovery
- **📝 Comprehensive Logging**: Detailed activity and error logs

## 📸 Screenshots

### Channel Verification
Users must join the channel to access bot features

### Job Notifications
Multiple formats for different scenarios:
- 🚨 Breaking News (new jobs)
- ⚠️ Urgent (3 days remaining)
- 🔴 Final Day (last day to apply)
- 📅 Date Extended (deadline extended)

### Complete Job Details
Full job information in A-G format:
- A: Post Name/Vacancy
- B: Eligibility/Education
- C: Age Limit
- D: Salary/Pay Scale
- E: Important Dates
- F: Application Fee
- G: Selection Process

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from @BotFather
- Telegram Channel for job updates

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   Edit `config.py` and add your credentials:
   ```python
   BOT_TOKEN = "your_bot_token_here"
   ADMIN_ID = 123456789  # Your Telegram user ID
   CHANNEL_ID = -1001234567890  # Your channel ID
   CHANNEL_USERNAME = "@yourchannel"
   ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```

### For Termux Users

```bash
bash run.sh
```

The script will automatically:
- Install Python if needed
- Install all dependencies
- Create necessary directories
- Start the bot with auto-restart

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

| Command | Description |
|---------|-------------|
| `/admin_post` | Manually post a job notification |
| `/admin_stats` | Show bot statistics |
| `/admin_update` | Force update job database |
| `/admin_test` | Test channel posting |
| `/admin_users` | Show verified user count |
| `/admin_backup` | Create manual backup |
| `/admin_help` | Show admin help |

## 📁 Project Structure

```
.
├── config.py           # Configuration settings
├── database.py         # Database operations
├── scraper.py          # Web scraping module
├── formatter.py        # Message formatting
├── bot.py              # Main bot application
├── admin.py            # Admin commands
├── run.sh              # Termux startup script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── README.md          # This file
├── SETUP_GUIDE.md     # Detailed setup guide
├── database/          # Database directory (auto-created)
│   ├── posted_jobs.json
│   └── verified_users.json
├── logs/              # Log files (auto-created)
│   ├── bot.log
│   └── errors.log
└── backups/           # Database backups (auto-created)
```

## ⚙️ Configuration

### Websites to Monitor

Edit `config.py` to add or modify websites:

```python
WEBSITES_TO_MONITOR = {
    "sarkari_result": {
        "name": "Sarkari Result",
        "url": "https://www.sarkariresult.com",
        "active": True
    },
    # Add more websites here
}
```

### State Websites

Add or modify state-specific job sources in `config.py`:

```python
STATE_WEBSITES = {
    "up": {
        "name": "Uttar Pradesh",
        "websites": ["https://www.upsssc.gov.in", "https://uppsc.up.nic.in"]
    },
    # Add more states here
}
```

### Scraping Settings

Adjust scraping behavior:

```python
SCRAPE_INTERVAL_HOURS = 3      # Scrape every 3 hours
REQUEST_DELAY_SECONDS = 3      # 3 second delay between requests
MAX_RETRIES = 3                 # Retry failed requests 3 times
REQUEST_TIMEOUT = 30            # 30 second timeout
```

## 🧪 Testing

### Test Bot Startup
```bash
python bot.py
```

### Test Scraping
```bash
python -c "import scraper; jobs = scraper.scrape_all_websites(); print(f'Found {len(jobs)} jobs')"
```

### Test Database
```bash
python -c "import database; print('Jobs:', len(database.load_posted_jobs()))"
```

### Test Channel Posting
Send `/admin_test` to your bot (admin only)

## 📊 Monitoring

### View Logs
```bash
# Bot activity
tail -f logs/bot.log

# Errors only
tail -f logs/errors.log
```

### Check Statistics
Use `/admin_stats` command

### Manual Backup
```bash
python -c "import database; database.backup_database()"
```

## 🔍 Troubleshooting

### Bot won't start
- Verify BOT_TOKEN is correct
- Install dependencies: `pip install -r requirements.txt`
- Check `logs/errors.log` for errors

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
- Verify CHANNEL_USERNAME is correct
- Check bot has `getChatMember` permission

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed troubleshooting.

## 🌐 Deployment

### Termux (Android)

```bash
pkg update && pkg upgrade
pkg install python git
chmod +x run.sh
bash run.sh
```

### Linux/Mac

```bash
pip install -r requirements.txt
python bot.py
```

### Windows

```bash
pip install -r requirements.txt
python bot.py
```

### Using Systemd (Linux)

Create `/etc/systemd/system/jobbot.service`:

```ini
[Unit]
Description=Government Job Updates Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable jobbot
sudo systemctl start jobbot
sudo systemctl status jobbot
```

## 🔒 Security

- Never share your BOT_TOKEN
- Keep ADMIN_ID private
- Don't commit `config.py` with real tokens to version control
- Use `.env` file for sensitive data
- Regularly review verified users list
- Keep dependencies updated

## 📝 Notes

- **Timezone**: All times are in IST (Asia/Kolkata)
- **Rate Limiting**: Bot adds delays between requests to respect servers
- **Duplicates**: Jobs are tracked by unique ID to avoid reposting
- **Backups**: Automatic backups created daily, keeps last 10
- **Logging**: All actions and errors are logged with timestamps

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📜 License

This project is provided as-is for educational purposes.

## 📞 Support

For issues or questions:
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- Review `logs/errors.log` for error details
- Ensure all prerequisites are met
- Verify configuration settings

## 🙏 Acknowledgments

- python-telegram-bot library
- BeautifulSoup4 for web scraping
- Schedule library for task scheduling
- All government job websites for providing employment opportunities

---

**Made with ❤️ for job seekers** 🎯

**Get your dream government job with timely updates!**
