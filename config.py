"""
Configuration file for Government Job Updates Telegram Bot
"""

# Bot Credentials
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual bot token from @BotFather
ADMIN_ID = 123456789  # Replace with your Telegram user ID
CHANNEL_ID = -1001234567890  # Replace with your channel ID (negative number)
CHANNEL_USERNAME = "@Roboallbotchannel"  # Your channel username

# Websites to Monitor
WEBSITES_TO_MONITOR = {
    "sarkari_result": {
        "name": "Sarkari Result",
        "url": "https://www.sarkariresult.com",
        "active": True
    },
    "free_job_alert": {
        "name": "Free Job Alert",
        "url": "https://www.freejobalert.com",
        "active": True
    },
    "employment_news": {
        "name": "Employment News",
        "url": "https://www.employmentnews.gov.in",
        "active": True
    }
}

# State-wise Websites Mapping
STATE_WEBSITES = {
    "up": {
        "name": "Uttar Pradesh",
        "websites": ["https://www.upsssc.gov.in", "https://uppsc.up.nic.in"]
    },
    "bihar": {
        "name": "Bihar",
        "websites": ["https://www.bssc.bih.nic.in", "https://bpsc.bih.nic.in"]
    },
    "delhi": {
        "name": "Delhi",
        "websites": ["https://delhi.gov.in", "https://dsssb.delhi.gov.in"]
    },
    "mp": {
        "name": "Madhya Pradesh",
        "websites": ["https://www.vyapam.nic.in", "https://mppsc.nic.in"]
    },
    "rajasthan": {
        "name": "Rajasthan",
        "websites": ["https://rsmssb.rajasthan.gov.in", "https://rpsc.rajasthan.gov.in"]
    },
    "punjab": {
        "name": "Punjab",
        "websites": ["https://www.punjab.gov.in", "https://ppsc.gov.in"]
    },
    "maharashtra": {
        "name": "Maharashtra",
        "websites": ["https://www.maharashtra.gov.in", "https://mahampsc.mahaonline.gov.in"]
    },
    "karnataka": {
        "name": "Karnataka",
        "websites": ["https://www.karnataka.gov.in", "https://kpsc.kar.nic.in"]
    },
    "tamilnadu": {
        "name": "Tamil Nadu",
        "websites": ["https://www.tn.gov.in", "https://tnpsc.gov.in"]
    },
    "kerala": {
        "name": "Kerala",
        "websites": ["https://www.kerala.gov.in", "https://keralapsc.gov.in"]
    },
    "westbengal": {
        "name": "West Bengal",
        "websites": ["https://www.wb.gov.in", "https://wbpsc.gov.in"]
    },
    "gujarat": {
        "name": "Gujarat",
        "websites": ["https://www.gujarat.gov.in", "https://gpsc.gujarat.gov.in"]
    },
    "andhra": {
        "name": "Andhra Pradesh",
        "websites": ["https://www.ap.gov.in", "https://appsc.gov.in"]
    },
    "telangana": {
        "name": "Telangana",
        "websites": ["https://www.telangana.gov.in", "https://tspsc.gov.in"]
    },
    "odisha": {
        "name": "Odisha",
        "websites": ["https://odisha.gov.in", "https://opsc.gov.in"]
    },
    "haryana": {
        "name": "Haryana",
        "websites": ["https://haryana.gov.in", "https://hssc.gov.in"]
    },
    "rajasthan": {
        "name": "Rajasthan",
        "websites": ["https://rsmssb.rajasthan.gov.in", "https://rpsc.rajasthan.gov.in"]
    },
    "jk": {
        "name": "Jammu & Kashmir",
        "websites": ["https://jkssb.nic.in", "https://jkpsc.nic.in"]
    },
    "uttarakhand": {
        "name": "Uttarakhand",
        "websites": ["https://uksssc.gov.in", "https://ukpsc.gov.in"]
    },
    "assam": {
        "name": "Assam",
        "websites": ["https://assam.gov.in", "https://apsc.nic.in"]
    }
}

# Job Categories
JOB_CATEGORIES = [
    "Sarkari Naukri",
    "Bank Jobs",
    "Railway Jobs",
    "SSC Jobs",
    "UPSC Jobs",
    "Police Jobs",
    "Teaching Jobs",
    "Engineering Jobs",
    "Medical Jobs",
    "Defense Jobs",
    "State Government Jobs",
    "Central Government Jobs",
    "PSU Jobs",
    "IT Jobs",
    "10th Pass Jobs",
    "12th Pass Jobs",
    "Graduate Jobs",
    "Post Graduate Jobs",
    "Diploma Jobs",
    "ITI Jobs"
]

# Scraping Configuration
SCRAPE_INTERVAL_HOURS = 3
REQUEST_DELAY_SECONDS = 3
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Timezone
TIMEZONE = "Asia/Kolkata"

# File Paths
DATABASE_DIR = "database"
POSTED_JOBS_FILE = "database/posted_jobs.json"
VERIFIED_USERS_FILE = "database/verified_users.json"
LOGS_DIR = "logs"
BACKUPS_DIR = "backups"

# Message Formats
MESSAGE_LIMIT = 4096  # Telegram message length limit
JOBS_PER_FEED = 5
