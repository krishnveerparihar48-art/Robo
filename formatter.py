from datetime import datetime
import pytz

def get_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S IST")

def format_complete_job(job):
    title = job.get('title', 'Unknown Title')
    eligibility = job.get('eligibility', 'ℹ️ Details not available in notification')
    age = job.get('age_limit', 'ℹ️ Details not available in notification')
    salary = job.get('salary', 'ℹ️ Details not available in notification')
    dates = job.get('dates', 'ℹ️ Details not available in notification')
    fee = job.get('fee', 'ℹ️ Details not available in notification')
    selection = job.get('selection', 'ℹ️ Details not available in notification')
    posts = job.get('posts', 'ℹ️ Details not available in notification')
    source = job.get('source', 'Unknown Source')
    
    text = (
        f"📢 *{title}*\n\n"
        f"🎓 *Eligibility:* {eligibility}\n"
        f"🔞 *Age Limit:* {age}\n"
        f"💰 *Salary:* {salary}\n"
        f"📅 *Important Dates:* {dates}\n"
        f"💵 *Application Fee:* {fee}\n"
        f"📝 *Selection Process:* {selection}\n"
        f"🔢 *Total Posts:* {posts}\n\n"
        f"🌐 Source: {source}\n"
        f"🕒 Posted: {get_ist_time()}"
    )
    return text

def format_breaking_news(job):
    title = job.get('title', 'Unknown Title')
    source = job.get('source', 'Unknown Source')
    
    text = (
        f"🚨 *BREAKING NEWS* 🚨\n\n"
        f"*{title}*\n\n"
        f"New notification just released! Check details now.\n\n"
        f"🌐 Source: {source}\n"
        f"🕒 Posted: {get_ist_time()}"
    )
    return text

def format_last_3_days(job):
    title = job.get('title', 'Unknown Title')
    dates = job.get('dates', 'Check notification')
    
    text = (
        f"⏳ *LAST 3 DAYS LEFT* ⏳\n\n"
        f"*{title}*\n\n"
        f"Don't miss out! Applications closing soon.\n"
        f"📅 Dates: {dates}\n\n"
        f"🕒 {get_ist_time()}"
    )
    return text

def format_date_extended(job):
    title = job.get('title', 'Unknown Title')
    dates = job.get('dates', 'Check notification')
    
    text = (
        f"📅 *DATE EXTENDED* 📅\n\n"
        f"*{title}*\n\n"
        f"Good news! The application deadline has been extended.\n"
        f"📅 New Dates: {dates}\n\n"
        f"🕒 {get_ist_time()}"
    )
    return text

def format_final_day(job):
    title = job.get('title', 'Unknown Title')
    
    text = (
        f"⚠️ *FINAL DAY TODAY* ⚠️\n\n"
        f"*{title}*\n\n"
        f"Urgent! Apply before the portal closes today.\n\n"
        f"🕒 {get_ist_time()}"
    )
    return text
