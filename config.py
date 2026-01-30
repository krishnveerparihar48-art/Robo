import os

# Telegram Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = os.getenv("ADMIN_ID", "YOUR_ADMIN_ID") # Can be string or int
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_channel_id")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "your_channel_username")

# Web Scraping Config
WEBSITES_TO_MONITOR = [
    {
        "name": "Sarkari Result",
        "url": "https://www.sarkariresult.com/latestjob.php",
        "enabled": True
    },
    {
        "name": "Free Job Alert",
        "url": "https://www.freejobalert.com/government-jobs/",
        "enabled": True
    }
    # Employment News is often a PDF or physical paper, checking online portal
]

STATE_WEBSITES = {
    "UP": "http://up.gov.in",
    "Bihar": "http://bihar.gov.in",
    # Add more as needed
}

JOB_CATEGORIES = [
    "Bank",
    "SSC",
    "Railways",
    "UPSC",
    "Defense",
    "Teaching",
    "Engineering",
    "Medical",
    "Police"
]

# Database Files
POSTED_JOBS_FILE = "posted_jobs.json"
VERIFIED_USERS_FILE = "verified_users.json"

# Scheduler Config
SCRAPE_INTERVAL_HOURS = 3
