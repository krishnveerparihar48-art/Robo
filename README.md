# Government Job Updates Telegram Bot

A production-ready Telegram bot that scrapes government job postings from multiple sources and publishes them to a Telegram channel in A-G format.

## Features

- ✅ Scrapes jobs from 3 primary sources (SarkariResult, FreeJobAlert, EmploymentNews)
- ✅ Stores jobs in SQLite database with duplicate detection
- ✅ Telegram bot with verification system
- ✅ Scheduled job posting every 3 hours
- ✅ A-G format job presentation
- ✅ Docker and systemd support
- ✅ Comprehensive logging

## Project Structure

```
bot/
  main.py              # Main bot application
scrapers/
  base_scraper.py      # Base scraper class
  sarkari_result.py    # SarkariResult scraper
  free_job_alert.py    # FreeJobAlert scraper
  employment_news.py   # EmploymentNews scraper
database/
  models.py            # SQLAlchemy models
  db.py                # Database operations
utils/
  formatter.py         # Message formatting
  processor.py         # Data processing
config/
  websites.yaml        # Website selectors configuration
logs/
  bot.log              # Bot logs
  scraper.log          # Scraper logs
  errors.log           # Error logs
  formatter.log        # Formatter logs
  processor.log        # Processor logs
  db.log               # Database logs
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Telegram Bot Token
- Telegram Channel ID

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/government-job-bot.git
   cd government-job-bot
   ```

2. **Run setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Edit .env file:**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Add your Telegram bot token and channel ID.

### Running the Bot

#### Development Mode
```bash
source venv/bin/activate
python bot/main.py
```

#### Production Mode (Docker)
```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

#### Production Mode (systemd)
```bash
# Copy service file
sudo cp bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start government-job-bot

# Enable auto-start
sudo systemctl enable government-job-bot

# View logs
sudo journalctl -u government-job-bot -f
```

## Bot Commands

- `/start` - Show welcome message and request verification
- `/verify` - Verify channel membership
- `/jobs` - Get latest 5 jobs
- `/help` - Show command reference
- `/status` - Show bot health status

## Configuration

Edit `config/websites.yaml` to configure:
- Website URLs
- CSS selectors for scraping
- Scraping priorities and delays

## Database

The bot uses SQLite by default. The database file `jobs.db` will be created automatically.

## Logging

All logs are stored in the `logs/` directory:
- `bot.log` - Main bot operations
- `scraper.log` - Web scraping activities
- `errors.log` - Error logs
- `formatter.log` - Message formatting
- `processor.log` - Data processing
- `db.log` - Database operations

## Deployment Checklist

- [ ] Set up Telegram bot and get token
- [ ] Create Telegram channel and get ID
- [ ] Configure .env file
- [ ] Test scrapers manually
- [ ] Test Telegram commands
- [ ] Set up scheduling
- [ ] Configure logging
- [ ] Deploy with Docker or systemd
- [ ] Set up monitoring

## Troubleshooting

### Common Issues

1. **Scraping fails**: Check if websites have changed their HTML structure
2. **Telegram errors**: Verify bot token and channel ID
3. **Database errors**: Check file permissions for jobs.db
4. **Scheduling issues**: Check system time and timezone settings

### Debugging

```bash
# Check bot logs
cat logs/bot.log

# Check scraper logs
cat logs/scraper.log

# Test database connection
python -c "from database.db import db_manager; print(db_manager.get_job_count())"
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers.
