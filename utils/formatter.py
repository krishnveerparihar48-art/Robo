from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/formatter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobFormatter:
    """Format job data for Telegram messages"""
    
    @staticmethod
    def format_job_ag(job: Dict[str, Any]) -> str:
        """Format job in A-G format for Telegram"""
        try:
            # A: Title
            title = job.get('title', 'No Title')
            
            # B: Category
            category_a = job.get('category_a', '')
            category_b = job.get('category_b', '')
            category = f"{category_a} - {category_b}" if category_b else category_a
            category = category if category else "Not Specified"
            
            # C: Details
            details = job.get('details_c', 'No details available')
            
            # D: Deadline
            deadline = job.get('deadline_d', 'Not Specified')
            
            # E: Apply Link
            apply_link = job.get('apply_link_e', '#')
            
            # F: Source
            source = job.get('source_f', 'Unknown Source')
            
            # G: Image (not included in text format)
            image_url = job.get('image_g', '')
            
            # Format message
            message = (
                f"📢 *{title}*\n\n"
                f"📁 *Category*: {category}\n"
                f"📝 *Details*: {details}\n\n"
                f"📅 *Deadline*: {deadline}\n"
                f"🔗 *Apply*: {apply_link}\n"
                f"🌐 *Source*: {source}"
            )
            
            return message
        except Exception as e:
            logger.error(f"Failed to format job: {e}")
            return "Failed to format job data"
    
    @staticmethod
    def format_job_list(jobs: list) -> str:
        """Format multiple jobs for Telegram"""
        if not jobs:
            return "No jobs available at the moment."
        
        messages = []
        for job in jobs:
            messages.append(JobFormatter.format_job_ag(job))
        
        return "\n\n---\n\n".join(messages)
    
    @staticmethod
    def format_welcome_message() -> str:
        """Format welcome message"""
        return (
            "👋 *Welcome to Government Job Updates Bot!*\n\n"
            "Get the latest government job notifications directly in your Telegram.\n\n"
            "Please join our channel to receive updates and verify your access."
        )
    
    @staticmethod
    def format_help_message() -> str:
        """Format help message"""
        return (
            "📚 *Available Commands*:\n\n"
            "/start - Show welcome message\n"
            "/verify - Verify your channel membership\n"
            "/jobs - Get latest 5 jobs\n"
            "/help - Show this help message\n"
            "/status - Show bot status"
        )
    
    @staticmethod
    def format_status_message(job_count: int, verified_users: int, last_update: str) -> str:
        """Format bot status message"""
        return (
            f"📊 *Bot Status*\n\n"
            f"📋 *Total Jobs*: {job_count}\n"
            f"👥 *Verified Users*: {verified_users}\n"
            f"🔄 *Last Update*: {last_update}"
        )
    
    @staticmethod
    def format_verification_request() -> str:
        """Format verification request message"""
        return (
            "🔒 *Verification Required*\n\n"
            "Please join our Telegram channel and click the button below to verify your membership."
        )
