from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
import formatter
import hashlib
from config import ADMIN_ID, CHANNEL_ID
import logging
import datetime

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

def generate_job_id(link):
    return hashlib.md5(link.encode()).hexdigest()

async def admin_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    # Expected format: /admin_post Title | Link | Source
    if not context.args:
        await update.message.reply_text("Usage: /admin_post Title | Link | Source")
        return

    content = " ".join(context.args)
    parts = [p.strip() for p in content.split('|')]
    
    if len(parts) < 2:
         await update.message.reply_text("❌ Invalid format. Use: Title | Link | Source (optional)")
         return
         
    title = parts[0]
    link = parts[1]
    source = parts[2] if len(parts) > 2 else "Manual Post"
    
    job_data = {
        "title": title,
        "link": link,
        "source": source,
        "scraped_at": datetime.datetime.now().isoformat(),
        # Add placeholders for other fields to avoid formatter errors
        "eligibility": "Check link",
        "age_limit": "Check link",
        "salary": "Check link",
        "dates": "Check link",
        "fee": "Check link",
        "selection": "Check link",
        "posts": "Check link"
    }
    
    text = formatter.format_complete_job(job_data)
    keyboard = [[InlineKeyboardButton("🚀 APPLY NOW", url=link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Save to DB
        job_id = generate_job_id(link)
        database.save_posted_job(job_id, job_data)
        
        await update.message.reply_text("✅ Job posted successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error posting job: {e}")


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    users_count = database.get_verified_user_count()
    posted_jobs = len(database.load_posted_jobs())
    
    text = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 Verified Users: {users_count}\n"
        f"📝 Posted Jobs: {posted_jobs}\n"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
        
    count = database.get_verified_user_count()
    await update.message.reply_text(f"👥 Total Verified Users: {count}")

async def admin_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    await update.message.reply_text("✅ Bot is running and responding.")

async def admin_force_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This would trigger the scraper manually
    # We need access to the scraper function which is in bot.py or we can call scraper directly
    # But the posting logic is in bot.py.
    # We'll just reply for now, or trigger via a shared mechanism if possible.
    # For simplicity, we'll suggest using the scheduler or just say "started".
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
        
    await update.message.reply_text("⚠️ Force update not fully linked from external module. Use /admin_test.")
