import logging
import asyncio
import threading
import schedule
import time
import json
import hashlib
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode

import config
import database
import scraper
import formatter
import admin

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs/bot.log'
)
logger = logging.getLogger(__name__)

# Global state
loop = None

def generate_job_id(link):
    return hashlib.md5(link.encode()).hexdigest()

# --- Part B: Channel Verification ---
async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        # If bot is not admin in channel or channel invalid, we might default to True or False
        # For this exercise, assume False if error (e.g. user not found)
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if database.is_user_verified(user.id):
        await send_welcome(update)
    else:
        await request_verification(update)

async def request_verification(update: Update):
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{config.CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("✅ VERIFY", callback_data="verify_check")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚠️ *CHANNEL VERIFICATION REQUIRED*\n\n"
        "To use this bot, you must join our official channel.",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def verify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    is_member = await check_membership(user.id, context)
    
    if is_member:
        database.add_verified_user(user.id)
        await query.message.edit_text("✅ Verification Successful!")
        await send_welcome_message(query.message)
    else:
        await query.message.reply_text("❌ You have not joined the channel yet. Please join and try again.")

async def send_welcome(update: Update):
    await send_welcome_message(update.message)

async def send_welcome_message(message):
    text = (
        "👋 *Welcome to Government Job Updates Bot!*\n\n"
        "Here are the available commands:\n"
        "/latest - Get top 5 latest jobs\n"
        "/websites - List monitored websites\n"
        "/help - Show help menu\n\n"
        "You will receive automatic updates for new jobs!"
    )
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# --- Part C: Commands ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_welcome(update)

async def latest_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not database.is_user_verified(update.effective_user.id):
        await request_verification(update)
        return

    jobs_data = database.load_posted_jobs()
    # Sort by posted date (assuming scraper adds timestamp, or we use posted_date)
    # The DB structure is {id: data}. Data has 'scraped_at'.
    sorted_jobs = sorted(jobs_data.values(), key=lambda x: x.get('scraped_at', ''), reverse=True)[:5]
    
    if not sorted_jobs:
        await update.message.reply_text("No jobs posted yet.")
        return

    for job in sorted_jobs:
        text = formatter.format_complete_job(job)
        keyboard = [[InlineKeyboardButton("🚀 APPLY NOW", url=job['link'])]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def websites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🌐 *Monitored Websites:*\n\n"
    for site in config.WEBSITES_TO_MONITOR:
        status = "✅" if site['enabled'] else "❌"
        text += f"{status} [{site['name']}]({site['url']})\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# --- Part F: Button Handlers ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "verify_check":
        await verify_handler(update, context)
    elif data.startswith("full_"):
        job_id = data.split("_")[1]
        await send_full_details(query, job_id)
    # 'Apply Now' is a URL button, so no callback needed usually, unless we track clicks.
    # But Telegram URL buttons open directly.

async def send_full_details(query, job_id):
    await query.answer()
    jobs = database.load_posted_jobs()
    job = jobs.get(job_id)
    if job:
        text = formatter.format_complete_job(job)
        keyboard = [[InlineKeyboardButton("🚀 APPLY NOW", url=job['link'])]]
        await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.message.reply_text("Job details not found.")

# --- Part D & E: Scheduler & Logic ---

async def post_job_to_channel(context, job, job_type="new"):
    # job_type: new, breaking, last3, extended, final
    
    if job_type == "new":
        text = formatter.format_complete_job(job)
    elif job_type == "breaking":
        text = formatter.format_breaking_news(job)
    elif job_type == "last3":
        text = formatter.format_last_3_days(job)
    elif job_type == "final":
        text = formatter.format_final_day(job)
    else:
        text = formatter.format_complete_job(job)
        
    job_id = generate_job_id(job['link'])
    
    buttons = [[InlineKeyboardButton("🚀 APPLY NOW", url=job['link'])]]
    if job_type != "new": # Add Full Details for short formats
        buttons.append([InlineKeyboardButton("📄 Full Details", callback_data=f"full_{job_id}")])
        
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await context.bot.send_message(
            chat_id=config.CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        logger.info(f"Posted job {job_id} to channel.")
        return True
    except Exception as e:
        logger.error(f"Failed to post to channel: {e}")
        return False

def scraper_task_logic(application):
    logger.info("Running scraper task...")
    try:
        jobs = scraper.get_all_jobs()
        logger.info(f"Scraper found {len(jobs)} jobs.")
        
        for job in jobs:
            job_id = generate_job_id(job['link'])
            if not database.is_job_posted(job_id):
                logger.info(f"New job found: {job.get('title')}")
                # Post to channel
                future = asyncio.run_coroutine_threadsafe(
                    post_job_to_channel(application, job, "new"),
                    application.loop
                )
                try:
                    success = future.result(timeout=10)
                    if success:
                        database.save_posted_job(job_id, job)
                except Exception as e:
                    logger.error(f"Error waiting for post future: {e}")
            else:
                logger.debug(f"Job already posted: {job_id}")
                
    except Exception as e:
        logger.error(f"Scraper task failed: {e}")

def parse_deadline(date_str):
    # Try to find a date pattern DD/MM/YYYY or DD-MM-YYYY
    matches = re.findall(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', date_str)
    if matches:
        d, m, y = matches[-1]
        try:
            return datetime(int(y), int(m), int(d))
        except ValueError:
            return None
    return None

def date_monitor_logic(application):
    logger.info("Running date monitor...")
    jobs = database.load_posted_jobs()
    now = datetime.now()
    
    for job_id, job in jobs.items():
        dates_text = job.get('dates', '')
        deadline = parse_deadline(dates_text)
        
        if not deadline:
            continue
            
        days_left = (deadline - now).days
        
        # We assume this runs daily, so we just check for exact matches
        if days_left == 3:
             asyncio.run_coroutine_threadsafe(
                post_job_to_channel(application, job, "last3"),
                application.loop
            )
        elif days_left == 0: # Today
             asyncio.run_coroutine_threadsafe(
                post_job_to_channel(application, job, "final"),
                application.loop
            )

def scheduler_thread(application):
    # Schedule scraper
    schedule.every(config.SCRAPE_INTERVAL_HOURS).hours.do(scraper_task_logic, application)
    
    # Schedule date monitor (daily)
    schedule.every().day.at("09:00").do(date_monitor_logic, application)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- Main ---

def main():
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", request_verification))
    application.add_handler(CommandHandler("latest", latest_jobs))
    application.add_handler(CommandHandler("websites", websites_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Admin Handlers
    application.add_handler(CommandHandler("admin_stats", admin.admin_stats))
    application.add_handler(CommandHandler("admin_users", admin.admin_users))
    application.add_handler(CommandHandler("admin_test", admin.admin_test))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Init DB
    database.init_db()
    
    # Start Scheduler Thread
    t = threading.Thread(target=scheduler_thread, args=(application,), daemon=True)
    t.start()
    
    # Start Polling
    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()
