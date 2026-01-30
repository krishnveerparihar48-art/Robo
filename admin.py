"""
Admin Commands Module for Government Job Updates Telegram Bot
Provides administrative functions for bot management
"""

from datetime import datetime
import pytz
import config
import database
import scraper
import formatter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

def is_admin(user_id):
    """
    Check if user is admin
    
    Args:
        user_id (int): Telegram user ID
        
    Returns:
        bool: True if admin, False otherwise
    """
    return user_id == config.ADMIN_ID

async def admin_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manually post a job notification
    
    Usage: /admin_post <title> <link> <deadline>
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        database.log_action(f"Admin {user_id} used /admin_post command")
        
        # Check arguments
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ *Invalid command format*\n\n"
                "Usage: /admin_post <title> <link> [deadline]",
                parse_mode='Markdown'
            )
            return
        
        title = context.args[0]
        link = context.args[1]
        deadline = context.args[2] if len(context.args) > 2 else ''
        
        # Create job data
        import hashlib
        job_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]
        
        # Scrape details
        job_details = scraper.scrape_job_details(link)
        
        job_data = {
            'job_id': job_id,
            'title': title,
            'link': link,
            'posted_date': datetime.now().strftime('%Y-%m-%d'),
            'deadline': deadline or job_details.get('E', ''),
            'source': 'Manual Post',
            'categories': scraper.determine_categories(title),
            'details': job_details
        }
        
        # Format as breaking news
        msg = formatter.format_breaking_news(job_data)
        
        # Post to channel
        keyboard = [[InlineKeyboardButton("🚀 APPLY NOW", url=link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=msg,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Save to database
            database.add_posted_job(job_data)
            
            await update.message.reply_text(
                f"✅ *Job posted successfully!*\n\n"
                f"Title: {title}\n"
                f"Job ID: {job_id}",
                parse_mode='Markdown'
            )
            
            database.log_action(f"Admin posted job manually: {title}")
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ *Error posting to channel*\n\n{str(e)}",
                parse_mode='Markdown'
            )
            database.log_error(f"Error in admin_post: {str(e)}")
        
    except Exception as e:
        database.log_error(f"Error in admin_post_command: {str(e)}")
        await update.message.reply_text("❌ An error occurred.")

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show bot statistics
    
    Usage: /admin_stats
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        database.log_action(f"Admin {user_id} used /admin_stats command")
        
        # Get statistics
        stats = database.get_statistics()
        
        # Build statistics message
        msg = f"""📊 *BOT STATISTICS*
━━━━━━━━━━━━━━━━━━━━━

📈 *Performance Metrics:*

• Total Jobs Posted: {stats.get('total_jobs_posted', 0)}
• Verified Users: {stats.get('verified_users', 0)}
• Last Backup: {stats.get('last_backup', 'Never')}

━━━━━━━━━━━━━━━━━━━━━
📊 *Jobs by Source:*
"""

        for source, count in stats.get('sources', {}).items():
            msg += f"• {source}: {count}\n"
        
        msg += """━━━━━━━━━━━━━━━━━━━━━
⚙️ *Configuration:*

• Scrape Interval: Every 3 hours
• Monitored Websites: """ + str(len(config.WEBSITES_TO_MONITOR)) + """
• States Covered: """ + str(len(config.STATE_WEBSITES)) + """
• Job Categories: """ + str(len(config.JOB_CATEGORIES)) + """

━━━━━━━━━━━━━━━━━━━━━
🕐 *Generated:* """ + datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S IST') + """
━━━━━━━━━━━━━━━━━━━━━"""
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in admin_stats_command: {str(e)}")
        await update.message.reply_text("❌ Error fetching statistics.")

async def admin_update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Force update job database by scraping all websites
    
    Usage: /admin_update
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        database.log_action(f"Admin {user_id} used /admin_update command")
        
        # Send status message
        status_msg = await update.message.reply_text(
            "🔄 *Starting manual job update...*\n\n"
            "This may take a few minutes...",
            parse_mode='Markdown'
        )
        
        # Scrape all websites
        jobs = scraper.scrape_all_websites()
        new_jobs = 0
        updated_jobs = 0
        
        for job in jobs:
            if not database.check_job_posted(job['job_id']):
                if database.add_posted_job(job):
                    new_jobs += 1
            else:
                updated_jobs += 1
        
        # Create backup
        backup_path = database.backup_database()
        
        # Update status message
        result_msg = f"""✅ *Job Database Updated*

━━━━━━━━━━━━━━━━━━━━━
📊 *Results:*

• New Jobs Added: {new_jobs}
• Existing Jobs: {updated_jobs}
• Total Processed: {len(jobs)}

━━━━━━━━━━━━━━━━━━━━━
💾 *Backup:* {backup_path.split('/')[-1] if backup_path else 'Failed'}
━━━━━━━━━━━━━━━━━━━━━

🕐 *Completed:* """ + datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S IST')
        
        await status_msg.edit_text(result_msg, parse_mode='Markdown')
        database.log_action(f"Admin update completed: {new_jobs} new jobs")
        
    except Exception as e:
        database.log_error(f"Error in admin_update_command: {str(e)}")
        await update.message.reply_text(f"❌ *Error updating database*\n\n{str(e)}", parse_mode='Markdown')

async def admin_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Test channel posting
    
    Usage: /admin_test [message]
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        database.log_action(f"Admin {user_id} used /admin_test command")
        
        # Get test message
        if context.args:
            test_msg = ' '.join(context.args)
        else:
            test_msg = """🧪 *TEST MESSAGE*

━━━━━━━━━━━━━━━━━━━━━
This is a test message from the admin panel.

🕐 *Time:* """ + datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S IST') + """
━━━━━━━━━━━━━━━━━━━━━

If you can see this, channel posting is working correctly!"""
        
        try:
            await context.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=test_msg,
                parse_mode='Markdown'
            )
            
            await update.message.reply_text(
                "✅ *Test message posted successfully!*\n\n"
                "Check the channel to verify.",
                parse_mode='Markdown'
            )
            
            database.log_action("Admin test message posted to channel")
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ *Error posting to channel*\n\n{str(e)}",
                parse_mode='Markdown'
            )
            database.log_error(f"Error in admin_test: {str(e)}")
        
    except Exception as e:
        database.log_error(f"Error in admin_test_command: {str(e)}")
        await update.message.reply_text("❌ An error occurred.")

async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show verified user count and details
    
    Usage: /admin_users
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        database.log_action(f"Admin {user_id} used /admin_users command")
        
        # Get verified users
        users = database.load_verified_users()
        verified_count = database.get_verified_user_count()
        
        # Count by status
        active_users = sum(1 for u in users.values() if u.get('status') == 'active')
        inactive_users = len(users) - active_users
        
        # Build message
        msg = f"""👥 *USER STATISTICS*
━━━━━━━━━━━━━━━━━━━━━

📊 *User Count:*

• Verified Users: {verified_count}
• Active Users: {active_users}
• Inactive Users: {inactive_users}
• Total Records: {len(users)}

━━━━━━━━━━━━━━━━━━━━━
📝 *Recent Users:*
"""

        # Show last 5 verified users
        recent_users = sorted(
            users.values(),
            key=lambda x: x.get('verify_date', ''),
            reverse=True
        )[:5]
        
        for user in recent_users:
            username = user.get('username', 'N/A')
            verify_date = user.get('verify_date', 'N/A')[:10]
            status_emoji = "✅" if user.get('status') == 'active' else "❌"
            msg += f"\n{status_emoji} @{username} - {verify_date}"
        
        msg += "\n━━━━━━━━━━━━━━━━━━━━━"
        msg += f"\n🕐 *Generated:* {datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S IST')}"
        msg += "\n━━━━━━━━━━━━━━━━━━━━━"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in admin_users_command: {str(e)}")
        await update.message.reply_text("❌ Error fetching user statistics.")

async def admin_backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Create manual backup
    
    Usage: /admin_backup
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        database.log_action(f"Admin {user_id} used /admin_backup command")
        
        await update.message.reply_text("💾 *Creating backup...*", parse_mode='Markdown')
        
        backup_path = database.backup_database()
        
        if backup_path:
            await update.message.reply_text(
                f"✅ *Backup created successfully!*\n\n"
                f"📁 File: `{backup_path}`\n"
                f"🕐 Time: {datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S IST')}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ *Backup creation failed*", parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in admin_backup_command: {str(e)}")
        await update.message.reply_text("❌ Error creating backup.")

async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show admin help
    
    Usage: /admin_help
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ *Access Denied*\n\nAdmin privileges required.", parse_mode='Markdown')
            return
        
        help_msg = """🔐 *ADMIN COMMANDS HELP*
━━━━━━━━━━━━━━━━━━━━━

📋 *Available Commands:*

🔸 */admin_post* - Manually post a job
   Usage: /admin_post <title> <link> [deadline]

🔸 */admin_stats* - Show bot statistics
   Displays: Total jobs, users, sources, etc.

🔸 */admin_update* - Force update job database
   Scrapes all websites and updates database

🔸 */admin_test* - Test channel posting
   Usage: /admin_test [message]

🔸 */admin_users* - Show user statistics
   Displays: Verified users, active users count

🔸 */admin_backup* - Create manual backup
   Creates a backup of all data

🔸 */admin_help* - Show this help message

━━━━━━━━━━━━━━━━━━━━━
⚠️ *IMPORTANT:*

• Only use admin commands from your verified account
• Back up data before making major changes
• Test updates in development first
• Monitor logs for errors

━━━━━━━━━━━━━━━━━━━━━
📞 *For issues, check:*
• logs/bot.log - Bot activity log
• logs/errors.log - Error log
━━━━━━━━━━━━━━━━━━━━━"""
        
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        
    except Exception as e:
        database.log_error(f"Error in admin_help_command: {str(e)}")
        await update.message.reply_text("❌ Error displaying admin help.")

# ============================================================================
# ADMIN COMMAND REGISTRATION
# ============================================================================

def register_admin_handlers(application):
    """
    Register all admin command handlers
    
    Args:
        application: Telegram application instance
    """
    from telegram.ext import CommandHandler
    
    application.add_handler(CommandHandler("admin_post", admin_post_command))
    application.add_handler(CommandHandler("admin_stats", admin_stats_command))
    application.add_handler(CommandHandler("admin_update", admin_update_command))
    application.add_handler(CommandHandler("admin_test", admin_test_command))
    application.add_handler(CommandHandler("admin_users", admin_users_command))
    application.add_handler(CommandHandler("admin_backup", admin_backup_command))
    application.add_handler(CommandHandler("admin_help", admin_help_command))
    
    print("Admin commands registered successfully")
