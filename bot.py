"""
Main Government Job Updates Telegram Bot
Complete bot application with all features
"""

import logging
from datetime import datetime, timedelta
import pytz
import threading
import schedule
import time
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import config
import database
import scraper
import formatter
import admin

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables for scheduling
scheduler_running = False
monitor_thread = None

# ============================================================================
# PART A - INITIALIZATION
# ============================================================================

def initialize_bot():
    """Initialize bot application"""
    try:
        database.initialize_directories()
        database.log_action("Bot initialization started")
        
        # Create application
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        database.log_action("Bot application created successfully")
        return application
        
    except Exception as e:
        database.log_error(f"Error initializing bot: {str(e)}")
        raise

# ============================================================================
# PART B - CHANNEL VERIFICATION SYSTEM
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command with channel verification
    """
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        
        database.log_action(f"User {user_id} ({username}) used /start command")
        
        # Check if user is already verified
        if database.is_user_verified(user_id):
            welcome_msg = formatter.format_welcome_message(username)
            await update.message.reply_text(welcome_msg, parse_mode='Markdown')
            return
        
        # User not verified - show verification screen
        verification_msg = """🔐 *CHANNEL VERIFICATION REQUIRED*

━━━━━━━━━━━━━━━━━━━━━
⚠️ *You must join our channel to use this bot*
━━━━━━━━━━━━━━━━━━━━━

📢 *Benefits of joining:*
• Daily job updates
• Latest Sarkari Naukri notifications
• Deadline reminders
• Breaking job alerts
• State-wise job updates
━━━━━━━━━━━━━━━━━━━━━

👇 *Steps to verify:*

1️⃣ Click "📢 JOIN CHANNEL" button
2️⃣ Join the channel
3️⃣ Click "✅ VERIFY ME" button
4️⃣ Enjoy all bot features!

━━━━━━━━━━━━━━━━━━━━━"""

        keyboard = [
            [
                InlineKeyboardButton("📢 JOIN CHANNEL", url=f"https://t.me/{config.CHANNEL_USERNAME.lstrip('@')}")
            ],
            [
                InlineKeyboardButton("✅ VERIFY ME", callback_data=f"verify_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(verification_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in start_command: {str(e)}")
        await update.message.reply_text("❌ An error occurred. Please try again.")

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle verify button callback - check channel membership
    """
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        
        await query.answer()
        
        database.log_action(f"User {user_id} ({username}) requested verification")
        
        # Check channel membership
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=config.CHANNEL_ID,
                user_id=user_id
            )
            
            status = chat_member.status
            
            # Check if user is member, administrator, or owner
            if status in ['member', 'administrator', 'creator']:
                # User is verified
                database.add_verified_user(user_id, username, first_name)
                database.log_action(f"User {user_id} ({username}) verified successfully")
                
                welcome_msg = formatter.format_welcome_message(username)
                main_keyboard = [
                    [KeyboardButton("📋 Latest Jobs")],
                    [KeyboardButton("🗺️ States"), KeyboardButton("📚 Categories")],
                    [KeyboardButton("❓ Help")]
                ]
                reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
                
                await query.edit_message_text(
                    "✅ *VERIFICATION SUCCESSFUL!*\n\n" + welcome_msg,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                # User not joined
                error_msg = """❌ *VERIFICATION FAILED*

━━━━━━━━━━━━━━━━━━━━━
⚠️ *You have not joined the channel yet*
━━━━━━━━━━━━━━━━━━━━━

👇 *Please complete these steps:*

1️⃣ Click "📢 JOIN CHANNEL" button below
2️⃣ Join the channel @Roboallbotchannel
3️⃣ Then click "✅ VERIFY ME" again

━━━━━━━━━━━━━━━━━━━━━"""

                keyboard = [
                    [
                        InlineKeyboardButton("📢 JOIN CHANNEL", url=f"https://t.me/{config.CHANNEL_USERNAME.lstrip('@')}")
                    ],
                    [
                        InlineKeyboardButton("✅ VERIFY ME", callback_data=f"verify_{user_id}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(error_msg, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            database.log_error(f"Error checking channel membership: {str(e)}")
            await query.edit_message_text(
                "❌ *Error checking verification status*\n\nPlease try again later.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        database.log_error(f"Error in verify_callback: {str(e)}")

# ============================================================================
# PART C - BOT COMMANDS
# ============================================================================

async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /latest command - show 5 most recent jobs"""
    try:
        user_id = update.effective_user.id
        
        if not database.is_user_verified(user_id):
            await send_verification_required(update)
            return
        
        database.log_action(f"User {user_id} requested latest jobs")
        
        jobs = database.get_latest_jobs(5)
        jobs_list = formatter.format_job_list(jobs, "📰 LATEST 5 JOB UPDATES")
        
        # Create inline keyboard for each job
        keyboard = []
        for job in jobs:
            job_id = job.get('job_id', '')
            link = job.get('link', '')
            keyboard.append([InlineKeyboardButton("🚀 APPLY NOW", url=link)])
        
        keyboard.append([InlineKeyboardButton("📋 FULL DETAILS", callback_data=f"details_latest")])
        keyboard.append([InlineKeyboardButton("❓ HELP", callback_data="help")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(jobs_list, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in latest_command: {str(e)}")
        await update.message.reply_text("❌ Error fetching latest jobs.")

async def state_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /state command - show jobs by state"""
    try:
        user_id = update.effective_user.id
        
        if not database.is_user_verified(user_id):
            await send_verification_required(update)
            return
        
        # Get state name from command argument
        if not context.args:
            states_msg = formatter.format_states_list()
            await update.message.reply_text(states_msg, parse_mode='Markdown')
            return
        
        state_code = context.args[0].lower()
        database.log_action(f"User {user_id} requested jobs for state: {state_code}")
        
        # Check if state is valid
        if state_code not in config.STATE_WEBSITES:
            await update.message.reply_text(
                f"❌ *Invalid state code: {state_code}*\n\n"
                f"Use /states to see available states.",
                parse_mode='Markdown'
            )
            return
        
        # Get jobs for the state
        jobs = database.get_jobs_by_state(config.STATE_WEBSITES[state_code]['name'])
        
        if not jobs:
            # Try scraping for the state
            scraped_jobs = scraper.scrape_by_state(state_code)
            for job in scraped_jobs:
                database.add_posted_job(job)
            jobs = scraped_jobs
        
        jobs_list = formatter.format_job_list(jobs, f"🗺️ JOBS IN {config.STATE_WEBSITES[state_code]['name'].upper()}")
        
        await update.message.reply_text(jobs_list, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in state_command: {str(e)}")
        await update.message.reply_text("❌ Error fetching state jobs.")

async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /category command - show jobs by category"""
    try:
        user_id = update.effective_user.id
        
        if not database.is_user_verified(user_id):
            await send_verification_required(update)
            return
        
        # Get category from command argument
        if not context.args:
            categories_msg = formatter.format_categories_list()
            await update.message.reply_text(categories_msg, parse_mode='Markdown')
            return
        
        category = ' '.join(context.args)
        database.log_action(f"User {user_id} requested jobs for category: {category}")
        
        jobs = database.get_jobs_by_category(category)
        jobs_list = formatter.format_job_list(jobs, f"📚 JOBS IN CATEGORY: {category.upper()}")
        
        await update.message.reply_text(jobs_list, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in category_command: {str(e)}")
        await update.message.reply_text("❌ Error fetching category jobs.")

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /categories command - show all categories"""
    try:
        user_id = update.effective_user.id
        
        if not database.is_user_verified(user_id):
            await send_verification_required(update)
            return
        
        categories_msg = formatter.format_categories_list()
        await update.message.reply_text(categories_msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in categories_command: {str(e)}")

async def states_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /states command - show all states"""
    try:
        user_id = update.effective_user.id
        
        if not database.is_user_verified(user_id):
            await send_verification_required(update)
            return
        
        states_msg = formatter.format_states_list()
        await update.message.reply_text(states_msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in states_command: {str(e)}")

async def websites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /websites command - show monitored websites"""
    try:
        user_id = update.effective_user.id
        
        if not database.is_user_verified(user_id):
            await send_verification_required(update)
            return
        
        websites_msg = formatter.format_websites_list()
        await update.message.reply_text(websites_msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in websites_command: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    try:
        help_msg = formatter.format_help_message()
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in help_command: {str(e)}")

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /verify command - manual verification"""
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        database.log_action(f"User {user_id} ({username}) used /verify command")
        
        # Check channel membership
        chat_member = await context.bot.get_chat_member(
            chat_id=config.CHANNEL_ID,
            user_id=user_id
        )
        
        if chat_member.status in ['member', 'administrator', 'creator']:
            database.add_verified_user(user_id, username, update.effective_user.first_name)
            await update.message.reply_text(
                "✅ *Verification Successful!* 🎉\n\n"
                "You can now use all bot features. Use /help to see available commands.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ *Not Verified*\n\n"
                "Please join the channel first:\n"
                f"https://t.me/{config.CHANNEL_USERNAME.lstrip('@')}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        database.log_error(f"Error in verify_command: {str(e)}")
        await update.message.reply_text("❌ Error verifying user.")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def send_verification_required(update: Update):
    """Send verification required message"""
    msg = """🔐 *VERIFICATION REQUIRED*

━━━━━━━━━━━━━━━━━━━━━
You must join our channel to use this bot.

📢 Channel: @Roboallbotchannel
━━━━━━━━━━━━━━━━━━━━━

Use /start to verify your membership."""
    
    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=f"https://t.me/{config.CHANNEL_USERNAME.lstrip('@')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================================================
# PART F - BUTTON HANDLERS
# ============================================================================

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline button callbacks"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.answer()
        
        data = query.data
        database.log_action(f"User {user_id} clicked button: {data}")
        
        # Handle different button actions
        if data == "help":
            help_msg = formatter.format_help_message()
            await query.edit_message_text(help_msg, parse_mode='Markdown')
        
        elif data == "details_latest":
            jobs = database.get_latest_jobs(1)
            if jobs:
                job = jobs[0]
                complete_msg = formatter.format_complete_job(job)
                keyboard = [
                    [InlineKeyboardButton("🚀 APPLY NOW", url=job.get('link', ''))],
                    [InlineKeyboardButton("📰 LATEST JOBS", callback_data="latest")],
                    [InlineKeyboardButton("❓ HELP", callback_data="help")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(complete_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
        elif data == "latest":
            jobs = database.get_latest_jobs(5)
            jobs_list = formatter.format_job_list(jobs, "📰 LATEST 5 JOB UPDATES")
            await query.edit_message_text(jobs_list, parse_mode='Markdown')
        
        elif data.startswith("apply_"):
            job_id = data.replace("apply_", "")
            # Apply now button is handled by URL button, this is backup
            await query.edit_message_text("🚀 *Opening application link...*", parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in button_callback_handler: {str(e)}")

# ============================================================================
# PART D - WEBSITE SCRAPING SCHEDULER
# ============================================================================

def post_to_channel(message, link=None):
    """
    Post message to channel with Apply Now button
    
    Args:
        message (str): Message to post
        link (str): Optional link for Apply Now button
    """
    try:
        import asyncio
        from telegram import Bot
        
        bot = Bot(token=config.BOT_TOKEN)
        
        async def send_message():
            keyboard = []
            if link:
                keyboard.append([InlineKeyboardButton("🚀 APPLY NOW", url=link)])
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            await bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        asyncio.run(send_message())
        database.log_action("Message posted to channel successfully")
        return True
        
    except Exception as e:
        database.log_error(f"Error posting to channel: {str(e)}")
        return False

def scheduled_scrape():
    """Scheduled scraping function - runs every 3 hours"""
    try:
        database.log_action("Starting scheduled scraping")
        
        # Scrape all websites
        jobs = scraper.scrape_all_websites()
        new_jobs = 0
        
        for job in jobs:
            # Check if already posted
            if not database.check_job_posted(job['job_id']):
                # Format and post to channel
                breaking_msg = formatter.format_breaking_news(job)
                link = job.get('link', '')
                
                if post_to_channel(breaking_msg, link):
                    # Save to database
                    if database.add_posted_job(job):
                        new_jobs += 1
                        database.log_action(f"New job posted: {job['title'][:50]}...")
        
        database.log_action(f"Scheduled scraping completed: {new_jobs} new jobs posted")
        
        # Create backup after scraping
        database.backup_database()
        
    except Exception as e:
        database.log_error(f"Error in scheduled scraping: {str(e)}")

def start_scheduler():
    """Start the scraping scheduler"""
    global scheduler_running
    
    if not scheduler_running:
        # Schedule scraping every 3 hours
        schedule.every(config.SCRAPE_INTERVAL_HOURS).hours.do(scheduled_scrape)
        
        # Run once immediately
        scheduled_scrape()
        
        scheduler_running = True
        database.log_action("Scheduler started successfully")

def run_scheduler():
    """Run the scheduler in a continuous loop"""
    start_scheduler()
    
    while scheduler_running:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            database.log_error(f"Error in scheduler loop: {str(e)}")
            time.sleep(60)

# ============================================================================
# PART E - LAST DATE MONITORING
# ============================================================================

def check_deadlines():
    """Check for jobs with approaching deadlines and post reminders"""
    try:
        database.log_action("Checking job deadlines")
        
        # Check jobs with 3 days remaining
        jobs_3_days = database.get_jobs_deadline_soon(3)
        for job in jobs_3_days:
            try:
                msg = formatter.format_last_3_days(job)
                link = job.get('link', '')
                
                if post_to_channel(msg, link):
                    job_id = job.get('job_id', '')
                    database.update_job_notification(job_id, '3_days')
                    database.log_action(f"3-day reminder posted: {job['title'][:50]}...")
                    
                # Add delay between posts
                time.sleep(5)
            except Exception as e:
                database.log_error(f"Error posting 3-day reminder: {str(e)}")
        
        # Check jobs with deadline today
        jobs_today = database.get_jobs_deadline_today()
        for job in jobs_today:
            try:
                msg = formatter.format_final_day(job)
                link = job.get('link', '')
                
                if post_to_channel(msg, link):
                    job_id = job.get('job_id', '')
                    database.update_job_notification(job_id, 'final_day')
                    database.log_action(f"Final day reminder posted: {job['title'][:50]}...")
                    
                time.sleep(5)
            except Exception as e:
                database.log_error(f"Error posting final day reminder: {str(e)}")
        
        database.log_action("Deadline check completed")
        
    except Exception as e:
        database.log_error(f"Error checking deadlines: {str(e)}")

def start_deadline_monitor():
    """Start the deadline monitoring thread"""
    def monitor_loop():
        while True:
            try:
                # Check deadlines once daily
                check_deadlines()
                # Sleep 24 hours
                time.sleep(24 * 60 * 60)
            except Exception as e:
                database.log_error(f"Error in deadline monitor loop: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    database.log_action("Deadline monitor thread started")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main function to run the bot"""
    try:
        database.log_action("=" * 50)
        database.log_action("Government Job Updates Bot Starting...")
        database.log_action("=" * 50)
        
        # Initialize bot
        application = initialize_bot()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("verify", verify_command))
        application.add_handler(CommandHandler("latest", latest_command))
        application.add_handler(CommandHandler("state", state_command))
        application.add_handler(CommandHandler("category", category_command))
        application.add_handler(CommandHandler("categories", categories_command))
        application.add_handler(CommandHandler("states", states_command))
        application.add_handler(CommandHandler("websites", websites_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Register admin command handlers
        admin.register_admin_handlers(application)
        
        # Register callback query handler
        application.add_handler(CallbackQueryHandler(button_callback_handler))
        application.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_"))
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        database.log_action("Scheduler thread started")
        
        # Start deadline monitor
        start_deadline_monitor()
        
        # Start the bot
        database.log_action("Bot polling started")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        database.log_action("Bot stopped by user")
    except Exception as e:
        database.log_error(f"Fatal error in main: {str(e)}")
        # Auto-restart
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
