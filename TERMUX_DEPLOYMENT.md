# 📱 Government Job Updates Bot - Termux Complete Deployment Guide

Complete step-by-step guide to deploy the Government Job Updates Telegram Bot on Android using Termux.

## 📋 Prerequisites

- Android phone (Android 5.0+)
- Termux app installed from F-Droid or GitHub
- Stable internet connection
- Telegram account

---

## 🚀 Step-by-Step Deployment

### Step 1: Install Termux

**IMPORTANT:** Install from F-Droid (not Play Store)

1. Enable F-Droid repository
2. Install Termux from F-Droid
3. Open Termux

### Step 2: Update Termux Packages

```bash
pkg update && pkg upgrade
```

**Expected:** Packages update successfully

### Step 3: Install Required Packages

```bash
pkg install python git curl wget
```

**Expected:** Python, git, curl, wget installed

### Step 4: Create Project Directory

```bash
cd ~
mkdir government-job-bot
cd government-job-bot
pwd
```

**Expected:** `/data/data/com.termux/files/home/government-job-bot`

### Step 5: Get Bot Files

**Option A: If you have the files:**

```bash
# Copy all files to this directory
# Or use: termux-setup-storage to access storage
```

**Option B: Clone from Git (if available):**

```bash
git clone <your-repo-url> .
```

**Option C: Download directly:**

```bash
# Download each file using curl or wget
curl -O https://your-server/config.py
curl -O https://your-server/database.py
# ... repeat for all files
```

### Step 6: Make Script Executable

```bash
chmod +x run.sh
```

### Step 7: Configure the Bot

#### 7.1 Edit config.py

```bash
nano config.py
```

**Edit these values:**

```python
BOT_TOKEN = "paste_your_bot_token_here"
ADMIN_ID = 123456789  # Your Telegram user ID
CHANNEL_ID = -1001234567890  # Your channel ID
CHANNEL_USERNAME = "@yourchannel"
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

#### 7.2 Get Your Credentials

**To get BOT_TOKEN:**
1. Open Telegram → @BotFather
2. `/newbot`
3. Follow instructions
4. Copy the token

**To get ADMIN_ID:**
1. Open Telegram → @userinfobot
2. Send any message
3. Copy the numeric ID

**To get CHANNEL_ID:**
1. Create a channel in Telegram
2. Add your bot as admin
3. Forward channel message to @userinfobot
4. Copy the negative number

### Step 8: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed python-telegram-bot beautifulsoup4 requests schedule pytz ...
```

### Step 9: Create Storage Access (Optional)

If you want to access device storage:

```bash
termux-setup-storage
```

This allows you to access files in `/sdcard/`

### Step 10: Test the Bot

```bash
python bot.py
```

**Expected Output:**
```
[2024-01-30 HH:MM:SS] ==================================================
[2024-01-30 HH:MM:SS] Government Job Updates Bot Starting...
[2024-01-30 HH:MM:SS] ==================================================
[2024-01-30 HH:MM:SS] Bot initialization started
[2024-01-30 HH:MM:SS] Bot application created successfully
[2024-01-30 HH:MM:SS] Scheduler thread started
[2024-01-30 HH:MM:SS] Deadline monitor thread started
[2024-01-30 HH:MM:SS] Bot polling started
```

**If successful:**
- Bot is running
- Send `/start` to your bot
- Bot should respond

**If errors:**
- Check BOT_TOKEN is correct
- Check internet connection
- See logs/errors.log

---

## 🔧 Running the Bot in Background

### Option 1: Using tmux (Recommended)

```bash
# Install tmux
pkg install tmux

# Create new session
tmux new -s jobbot

# Run bot
bash run.sh

# Detach (keep bot running)
# Press: Ctrl+B, then D

# Reattach to see bot
tmux attach -t jobbot
```

### Option 2: Using screen

```bash
# Install screen
pkg install screen

# Create session
screen -S jobbot

# Run bot
bash run.sh

# Detach
# Press: Ctrl+A, then D

# Reattach
screen -r jobbot
```

### Option 3: Using nohup

```bash
nohup bash run.sh > bot_output.log 2>&1 &

# Check if running
ps aux | grep python

# Stop bot
kill <process_id>
```

---

## 🔄 Auto-Start on Boot (Optional)

### Method 1: Using Termux:Boot

1. Install Termux:Boot from F-Droid
2. Create boot script:

```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/jobbot.sh
```

Add this content:

```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/government-job-bot
bash run.sh
```

Make executable:

```bash
chmod +x ~/.termux/boot/jobbot.sh
```

3. Open Termux:Boot app
4. Click "Add" → "run"
5. Enter: `termux -r jobbot.sh`

### Method 2: Using Tasker or Automate

Create a task that runs:
```bash
am start -n com.termux/.app.RunCommandService -a com.termux.RUN_COMMAND -e com.termux.RUN_COMMAND_PATH '/data/data/com.termux/files/home/.termux/boot/jobbot.sh'
```

---

## 📊 Monitoring the Bot

### View Logs in Real-time

```bash
# Bot activity
tail -f logs/bot.log

# Errors only
tail -f logs/errors.log

# Both files
tail -f logs/bot.log logs/errors.log
```

### Check Bot Status

```bash
# Check if bot process is running
ps aux | grep python

# Check for errors
cat logs/errors.log | tail -20

# Check recent activity
cat logs/bot.log | tail -20
```

### Test Bot Functionality

```bash
# Test database
python -c "import database; print('Jobs:', len(database.load_posted_jobs()))"

# Test scraper
python -c "import scraper; jobs = scraper.scrape_all_websites(); print('Found:', len(jobs))"

# Test formatter
python -c "import formatter; print(formatter.format_help_message())"
```

---

## 🛠️ Maintenance

### Update the Bot

```bash
# Stop the bot (Ctrl+C or kill)
cd ~/government-job-bot

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart
bash run.sh
```

### Create Manual Backup

```bash
cd ~/government-job-bot
python -c "import database; database.backup_database()"
```

### Clear Old Logs

```bash
# Clear bot.log
> logs/bot.log

# Clear errors.log
> logs/errors.log
```

### Cleanup Old Backups (keeps last 10)

```bash
cd ~/government-job-bot/backups
ls -t | tail -n +11 | xargs rm -f
```

---

## 🐛 Troubleshooting

### Bot won't start

**Problem:** Permission denied or module not found

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

### Bot crashes immediately

**Problem:** Configuration error

**Solution:**
```bash
# Check config.py
python -c "import config; print('OK')"

# Check logs
cat logs/errors.log
```

### Scraping fails

**Problem:** Network or website issues

**Solution:**
```bash
# Test internet
ping google.com

# Test website access
curl https://www.sarkariresult.com

# Check scraper logs
cat logs/bot.log | grep -i scrap
```

### Channel posting fails

**Problem:** Bot not admin or wrong ID

**Solution:**
```bash
# Test channel access
python -c "from telegram import Bot; import config; bot = Bot(token=config.BOT_TOKEN); print(bot.get_chat(config.CHANNEL_ID))"

# Make sure bot is admin in channel
# Double-check CHANNEL_ID in config.py
```

### Bot stops after some time

**Problem:** Termux killed by Android

**Solution:**
```bash
# Use tmux or screen (see above)
# Or add to Termux:Boot for auto-restart
```

### Storage permission errors

**Problem:** Can't write to disk

**Solution:**
```bash
# Check directory permissions
ls -la

# Fix permissions
chmod 755 database logs backups

# Run with storage access
termux-setup-storage
```

### Out of memory errors

**Problem:** Phone running out of RAM

**Solution:**
```bash
# Clear caches
rm -rf ~/.cache/pip/*

# Close other apps
# Use swap (advanced)
```

---

## 📱 Termux Tips

### Keep Termux Alive

- Add Termux to battery optimization whitelist
- Use "Background" permission in Android settings
- Use tmux/screen to keep sessions

### Secure Your Bot

```bash
# Make config.py read-only
chmod 600 config.py

# Don't share your files
# Use git only for code, not config with tokens
```

### Optimize Performance

```bash
# Limit log file size
echo "Keep logs small" > README.txt

# Periodic cleanup (add to cron if available)
# Delete old backups weekly
```

---

## 📚 Useful Commands

```bash
# Quick restart
cd ~/government-job-bot && bash run.sh

# Quick status check
ps aux | grep python | grep -v grep

# Quick error check
tail -20 logs/errors.log

# Quick activity check
tail -20 logs/bot.log

# Quick backup
cd ~/government-job-bot && python -c "import database; database.backup_database()"

# Quick test
cd ~/government-job-bot && python -c "import scraper; print('Jobs:', len(scraper.scrape_all_websites()))"
```

---

## ✅ Deployment Checklist

- [ ] Termux installed
- [ ] Packages updated
- [ ] Python and git installed
- [ ] Bot files copied
- [ ] run.sh made executable
- [ ] config.py configured
- [ ] Dependencies installed
- [ ] Bot tested successfully
- [ ] tmux installed (for background)
- [ ] Bot running in background
- [ ] Auto-start configured (optional)
- [ ] Logs monitored
- [ ] Backup tested

---

## 🎯 Final Notes

1. **Always keep your bot token private**
2. **Regularly check logs for errors**
3. **Create backups before making changes**
4. **Test thoroughly after updates**
5. **Monitor bot performance regularly**

---

## 📞 Support

If you encounter issues:
1. Check logs/errors.log
2. Review this guide
3. Check SETUP_GUIDE.md
4. Check TEST_GUIDE.md

---

**Happy Job Hunting!** 🎉

**Deployed on Termux with ease!** 📱✨
