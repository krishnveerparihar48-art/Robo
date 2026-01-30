# 🚀 Government Job Updates Bot - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Get Your Bot Token (1 minute)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Govt Job Bot")
4. Choose a username (e.g., "my_govt_job_bot")
5. **Copy the BOT_TOKEN** provided

### Step 2: Get Your User ID & Channel ID (2 minutes)

1. Search for `@userinfobot`
2. Send any message
3. **Copy your USER_ID** (numeric, e.g., 123456789)

4. Create a new channel in Telegram
5. Add your bot as administrator
6. Forward any message from the channel to `@userinfobot`
7. **Copy the CHANNEL_ID** (negative number, e.g., -1001234567890)

### Step 3: Configure the Bot (1 minute)

Edit `config.py`:

```python
BOT_TOKEN = "paste_your_bot_token_here"
ADMIN_ID = 123456789  # Paste your USER_ID
CHANNEL_ID = -1001234567890  # Paste your CHANNEL_ID
CHANNEL_USERNAME = "@yourchannel"  # Your channel username
```

### Step 4: Install & Run (1 minute)

**Linux/Mac/Windows:**
```bash
pip install -r requirements.txt
python bot.py
```

**Termux (Android):**
```bash
chmod +x run.sh
bash run.sh
```

### Step 5: Test the Bot

1. Open Telegram and search for your bot
2. Send `/start`
3. Join your channel
4. Click "Verify Me"
5. Send `/latest` to see recent jobs

## ✅ That's it! Your bot is now running!

---

## 📋 Common Commands

**For Users:**
- `/start` - Start bot
- `/latest` - Latest jobs
- `/state up` - Jobs by state
- `/category bank` - Jobs by category
- `/help` - Help

**For Admin (your account only):**
- `/admin_stats` - View statistics
- `/admin_update` - Update job database
- `/admin_test` - Test channel posting

---

## 🔧 Need Help?

- **Setup issues:** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Testing:** See [TEST_GUIDE.md](TEST_GUIDE.md)
- **Full docs:** See [README.md](README.md)

---

## ⚠️ Important

- Never share your BOT_TOKEN
- Keep config.py private
- Bot must be admin in your channel
- Check logs/errors.log if issues occur

---

**Made with ❤️ for job seekers! 🎯**
