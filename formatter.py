"""
Job Formatter Module for Government Job Updates Telegram Bot
Formats job data into various message formats
"""

from datetime import datetime
import pytz
import config

def get_ist_timestamp():
    """
    Get current timestamp in IST
    
    Returns:
        str: Formatted timestamp
    """
    tz = pytz.timezone(config.TIMEZONE)
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S IST')

def format_section(label, value, emoji):
    """
    Format a job detail section
    
    Args:
        label (str): Section label
        value (str): Section value
        emoji (str): Section emoji
        
    Returns:
        str: Formatted section
    """
    if not value or value.strip() == '':
        return f"{emoji} **{label}:** ℹ️ Details not available in notification\n"
    return f"{emoji} **{label}:** {value.strip()}\n"

def format_complete_job(job_data):
    """
    Format complete job data in A-G structure with actual scraped data
    
    Args:
        job_data (dict): Job data dictionary
        
    Returns:
        str: Formatted job message
    """
    try:
        details = job_data.get('details', {})
        title = job_data.get('title', 'Job Vacancy')
        link = job_data.get('link', '')
        source = job_data.get('source', 'Unknown Source')
        posted_date = job_data.get('posted_date', '')
        
        # Build message with A-G sections
        message = f"""📣 *{title}*

━━━━━━━━━━━━━━━━━━━━━
📊 **VACANCY DETAILS**
━━━━━━━━━━━━━━━━━━━━━

{format_section('POST NAME', details.get('A', ''), '📌')}
{format_section('ELIGIBILITY / EDUCATION', details.get('B', ''), '🎓')}
{format_section('AGE LIMIT', details.get('C', ''), '📅')}
{format_section('SALARY / PAY SCALE', details.get('D', ''), '💰')}
{format_section('IMPORTANT DATES', details.get('E', ''), '🗓️')}
{format_section('APPLICATION FEE', details.get('F', ''), '💵')}
{format_section('SELECTION PROCESS', details.get('G', ''), '📝')

━━━━━━━━━━━━━━━━━━━━━
📍 *Source:* {source}
📅 *Posted:* {posted_date}
━━━━━━━━━━━━━━━━━━━━━

🔗 *For complete details, visit the official website*"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting job: {str(e)}"

def format_breaking_news(job_data):
    """
    Format job as breaking news with Apply Now button
    
    Args:
        job_data (dict): Job data dictionary
        
    Returns:
        str: Formatted breaking news message
    """
    try:
        title = job_data.get('title', 'New Job Vacancy')
        link = job_data.get('link', '')
        source = job_data.get('source', 'Unknown')
        
        # Extract key details from sections
        details = job_data.get('details', {})
        posts = details.get('A', 'Various Posts')
        deadline = details.get('E', 'Apply Soon')
        
        message = f"""🚨 *BREAKING JOB UPDATE*

📢 *{title}*

━━━━━━━━━━━━━━━━━━━━━
📌 **Vacancy:** {posts}
⏰ **Last Date:** {deadline}
━━━━━━━━━━━━━━━━━━━━━

📖 *Eligibility:* {details.get('B', 'See official notification')}
💰 *Salary:* {details.get('D', 'As per norms')}

━━━━━━━━━━━━━━━━━━━━━
📍 *Source:* {source}
🕐 *Updated:* {get_ist_timestamp()}
━━━━━━━━━━━━━━━━━━━━━

🔔 *Don't miss this opportunity! Apply Now!*"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting breaking news: {str(e)}"

def format_last_3_days(job_data):
    """
    Format job with last 3 days warning and Apply Now button
    
    Args:
        job_data (dict): Job data dictionary
        
    Returns:
        str: Formatted urgent message
    """
    try:
        title = job_data.get('title', 'Job Vacancy')
        link = job_data.get('link', '')
        source = job_data.get('source', 'Unknown')
        
        details = job_data.get('details', {})
        posts = details.get('A', 'Various Posts')
        deadline = details.get('E', 'Closing Soon')
        
        message = f"""⚠️ *URGENT - LAST 3 DAYS LEFT*

📢 *{title}*

━━━━━━━━━━━━━━━━━━━━━
⚡ *Application closing in 3 days!*
━━━━━━━━━━━━━━━━━━━━━

📌 **Vacancy:** {posts}
⏰ **Last Date:** {deadline}
━━━━━━━━━━━━━━━━━━━━━

🎓 *Eligibility:* {details.get('B', 'Check notification')}
💰 *Salary:* {details.get('D', 'As per rules')}

━━━━━━━━━━━━━━━━━━━━━
📍 *Source:* {source}
🔴 *Status:* *Apply Before Deadline!*
━━━━━━━━━━━━━━━━━━━━━

⏳ *Hurry! Time is running out!*"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting last 3 days: {str(e)}"

def format_date_extended(job_data):
    """
    Format job with date extension announcement and Apply Now button
    
    Args:
        job_data (dict): Job data dictionary
        
    Returns:
        str: Formatted date extension message
    """
    try:
        title = job_data.get('title', 'Job Vacancy')
        link = job_data.get('link', '')
        source = job_data.get('source', 'Unknown')
        
        details = job_data.get('details', {})
        posts = details.get('A', 'Various Posts')
        deadline = details.get('E', 'New Deadline Announced')
        
        message = f"""📅 *DATE EXTENSION ANNOUNCEMENT*

✨ *{title}*

━━━━━━━━━━━━━━━━━━━━━
🎉 *Good News! Last Date Extended!*
━━━━━━━━━━━━━━━━━━━━━

📌 **Vacancy:** {posts}
⏰ **New Last Date:** {deadline}
━━━━━━━━━━━━━━━━━━━━━

🎓 *Eligibility:* {details.get('B', 'See notification')}
💰 *Salary:* {details.get('D', 'As per norms')}

━━━━━━━━━━━━━━━━━━━━━
📍 *Source:* {source}
🕐 *Updated:* {get_ist_timestamp()}
━━━━━━━━━━━━━━━━━━━━━

✅ *Now you have more time to apply!*"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting date extended: {str(e)}"

def format_final_day(job_data):
    """
    Format job as final day urgent notification with Apply Now button
    
    Args:
        job_data (dict): Job data dictionary
        
    Returns:
        str: Formatted final day message
    """
    try:
        title = job_data.get('title', 'Job Vacancy')
        link = job_data.get('link', '')
        source = job_data.get('source', 'Unknown')
        
        details = job_data.get('details', {})
        posts = details.get('A', 'Various Posts')
        deadline = details.get('E', 'Today!')
        
        message = f"""🔴 *FINAL DAY - APPLY TODAY!*

🚨 *{title}*

━━━━━━━━━━━━━━━━━━━━━
🔴 *LAST DAY TO APPLY - TODAY!*
━━━━━━━━━━━━━━━━━━━━━

📌 **Vacancy:** {posts}
⏰ **Deadline:** {deadline}
━━━━━━━━━━━━━━━━━━━━━

🎓 *Eligibility:* {details.get('B', 'Apply if eligible')}
💰 *Salary:* {details.get('D', 'As per rules')}

━━━━━━━━━━━━━━━━━━━━━
📍 *Source:* {source}
🔴 *Status:* *CLOSING TODAY!*
━━━━━━━━━━━━━━━━━━━━━

⏰ *Apply NOW before it's too late!*"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting final day: {str(e)}"

def format_job_list(jobs, title="📋 JOB LIST"):
    """
    Format a list of jobs for display
    
    Args:
        jobs (list): List of job dictionaries
        title (str): List title
        
    Returns:
        str: Formatted job list
    """
    try:
        if not jobs:
            return f"{title}\n\nℹ️ No jobs found at the moment. Please try again later."
        
        message = f"{title}\n\n"
        
        for idx, job in enumerate(jobs, 1):
            title_text = job.get('title', 'Job Vacancy')[:50]
            source = job.get('source', 'Unknown')
            posted_date = job.get('posted_date', '')
            
            message += f"{idx}. *{title_text}*\n"
            message += f"   📍 {source}\n"
            message += f"   📅 {posted_date}\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"📌 Total: {len(jobs)} jobs\n"
        message += "━━━━━━━━━━━━━━━━━━━━━"
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting job list: {str(e)}"

def format_categories_list():
    """
    Format list of available job categories
    
    Returns:
        str: Formatted categories list
    """
    try:
        message = "📚 *AVAILABLE JOB CATEGORIES*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for idx, category in enumerate(config.JOB_CATEGORIES, 1):
            message += f"{idx}. {category}\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━━━\n"
        message += "💡 *Use /category [name] to filter jobs*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━"
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting categories: {str(e)}"

def format_states_list():
    """
    Format list of available states
    
    Returns:
        str: Formatted states list
    """
    try:
        message = "🗺️ *AVAILABLE STATES*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for code, info in config.STATE_WEBSITES.items():
            message += f"• *{info['name']}* - /state {code}\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━━━\n"
        message += "💡 *Use /state [code] to view state jobs*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━"
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting states: {str(e)}"

def format_websites_list():
    """
    Format list of monitored websites
    
    Returns:
        str: Formatted websites list
    """
    try:
        message = "🌐 *MONITORED WEBSITES*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for site_key, site_info in config.WEBSITES_TO_MONITOR.items():
            status = "✅ Active" if site_info.get('active') else "❌ Inactive"
            message += f"• *{site_info['name']}*\n"
            message += f"  🔗 {site_info['url']}\n"
            message += f"  {status}\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━\n"
        message += "🔄 *Updated every 3 hours*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━"
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting websites: {str(e)}"

def format_welcome_message(username):
    """
    Format welcome message for verified users
    
    Args:
        username (str): Username of the user
        
    Returns:
        str: Formatted welcome message
    """
    try:
        display_name = f"@{username}" if username else "User"
        
        message = f"""🎉 *WELCOME TO GOVERNMENT JOB UPDATES BOT*

Hello, {display_name}! 👋

You are now verified and can access all features!

━━━━━━━━━━━━━━━━━━━━━
✅ *VERIFICATION STATUS: VERIFIED*
━━━━━━━━━━━━━━━━━━━━━

📋 *AVAILABLE COMMANDS:*

🔸 /latest - Get latest 5 job updates
🔸 /state [name] - Get jobs by state
🔸 /category [type] - Get jobs by category
🔸 /categories - View all job categories
🔸 /states - View all available states
🔸 /websites - View monitored websites
🔸 /help - Get help with bot usage
━━━━━━━━━━━━━━━━━━━━━

📢 *FEATURES:*

✨ Latest Sarkari Naukri updates
✨ State-wise job notifications
✨ Category-wise job filtering
✨ Deadline reminders (3 days, final day)
✨ Breaking job alerts
━━━━━━━━━━━━━━━━━━━━━

🔔 *Stay updated with daily job notifications!*

💡 *Type /help to see detailed usage instructions*"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting welcome: {str(e)}"

def format_help_message():
    """
    Format help message with detailed instructions
    
    Returns:
        str: Formatted help message
    """
    try:
        message = """📖 *GOVERNMENT JOB UPDATES BOT - HELP*

━━━━━━━━━━━━━━━━━━━━━
🤖 *BOT COMMANDS*
━━━━━━━━━━━━━━━━━━━━━

🔸 */start* - Start the bot and verify channel membership
🔸 */verify* - Verify channel subscription
🔸 */latest* - Get 5 most recent job updates
🔸 */state [name]* - Get jobs for specific state
   Example: /state up, /state bihar
🔸 */category [type]* - Get jobs by category
   Example: /category bank jobs, /category ssc jobs
🔸 */categories* - View all available job categories
🔸 */states* - View all available states
🔸 */websites* - View monitored websites
🔸 */help* - Show this help message

━━━━━━━━━━━━━━━━━━━━━
📋 *JOB NOTIFICATION FORMATS*
━━━━━━━━━━━━━━━━━━━━━

🚨 *Breaking News* - For newly posted jobs
⚠️ *Last 3 Days* - Jobs closing in 3 days
🔴 *Final Day* - Jobs closing today
📅 *Date Extended* - When deadline is extended
📊 *Complete Details* - Full job information (A-G)

━━━━━━━━━━━━━━━━━━━━━
🔘 *BUTTON ACTIONS*
━━━━━━━━━━━━━━━━━━━━━

🚀 *APPLY NOW* - Opens official application link
📋 *FULL DETAILS* - Shows complete job information
📰 *LATEST JOBS* - Shows 5 most recent jobs
❓ *HELP* - Shows this help menu

━━━━━━━━━━━━━━━━━━━━━
⚙️ *BOT FEATURES*
━━━━━━━━━━━━━━━━━━━━━

✅ Automatic job scraping every 3 hours
✅ Deadline reminders (3 days & final day)
✅ Duplicate job filtering
✅ Multiple website monitoring
✅ State & category filtering
✅ IST timezone support
✅ Error handling & logging

━━━━━━━━━━━━━━━━━━━━━
💡 *TIPS*
━━━━━━━━━━━━━━━━━━━━━

• Join our channel to access all features
• Check daily for new job updates
• Use Apply Now button to visit official website
• Enable notifications to never miss updates
• Use category filters for specific job types

━━━━━━━━━━━━━━━━━━━━━
📞 *NEED SUPPORT?*
━━━━━━━━━━━━━━━━━━━━━

For any issues or queries, contact the admin.
Channel: @Roboallbotchannel

━━━━━━━━━━━━━━━━━━━━━
*Happy Job Hunting!* 🎯"""
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting help: {str(e)}"

def format_statistics(stats):
    """
    Format bot statistics for display
    
    Args:
        stats (dict): Statistics dictionary
        
    Returns:
        str: Formatted statistics message
    """
    try:
        message = "📊 *BOT STATISTICS*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        message += f"📈 *Total Jobs Posted:* {stats.get('total_jobs_posted', 0)}\n"
        message += f"👥 *Verified Users:* {stats.get('verified_users', 0)}\n\n"
        
        message += "📊 *Jobs by Source:*\n"
        for source, count in stats.get('sources', {}).items():
            message += f"  • {source}: {count}\n"
        
        message += f"\n💾 *Last Backup:* {stats.get('last_backup', 'Never')}\n"
        message += "\n━━━━━━━━━━━━━━━━━━━━━"
        
        return message
        
    except Exception as e:
        return f"❌ Error formatting statistics: {str(e)}"
