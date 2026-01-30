from telegram import Update
from telegram.ext import ContextTypes
import database
from config import ADMIN_ID
import logging

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

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
