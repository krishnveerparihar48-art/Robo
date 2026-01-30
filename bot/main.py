import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import yaml
from typing import List, Dict, Any

# Import local modules
from database.db import db_manager
from database.models import Job
from utils.formatter import JobFormatter
from utils.processor import JobProcessor
from scrapers.sarkari_result import SarkariResultScraper
from scrapers.free_job_alert import FreeJobAlertScraper
from scrapers.employment_news import EmploymentNewsScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
load_dotenv()

# Load websites configuration
with open('config/websites.yaml', 'r') as f:
    websites_config = yaml.safe_load(f)

# Initialize scrapers
scrapers = {
    'sarkari_result': SarkariResultScraper(websites_config['websites']['sarkari_result']),
    'free_job_alert': FreeJobAlertScraper(websites_config['websites']['free_job_alert']),
    'employment_news': EmploymentNewsScraper(websites_config['websites']['employment_news'])
}

class GovernmentJobBot:
    """Main Telegram bot class"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        self.scheduler = BackgroundScheduler()
        self.application = None
        self.bot = None
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in environment variables")
        
        if not self.channel_id:
            raise ValueError("TELEGRAM_CHANNEL_ID not set in environment variables")
    
    def initialize(self):
        """Initialize bot and scheduler"""
        try:
            # Initialize Telegram application
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = Bot(token=self.bot_token)
            
            # Set up command handlers
            self.setup_handlers()
            
            # Set up scheduler
            self.setup_scheduler()
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            raise
    
    def setup_handlers(self):
        """Set up command handlers"""
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('verify', self.verify_command))
        self.application.add_handler(CommandHandler('jobs', self.jobs_command))
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(CommandHandler('status', self.status_command))
    
    def setup_scheduler(self):
        """Set up background scheduler"""
        # Job posting every 3 hours
        self.scheduler.add_job(
            self.post_jobs_to_channel,
            IntervalTrigger(hours=3),
            id='post_jobs',
            name='Post jobs to channel',
            replace_existing=True
        )
        
        # Scraping check every 1 hour
        self.scheduler.add_job(
            self.scrape_and_store_jobs,
            IntervalTrigger(hours=1),
            id='scrape_jobs',
            name='Scrape and store jobs',
            replace_existing=True
        )
        
        # Health check every 30 minutes
        self.scheduler.add_job(
            self.health_check,
            IntervalTrigger(minutes=30),
            id='health_check',
            name='Health check',
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Scheduler started")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user_id = update.effective_user.id
            
            # Add user to database
            db_manager.add_user(user_id)
            
            # Send welcome message
            welcome_message = JobFormatter.format_welcome_message()
            await update.message.reply_text(welcome_message, parse_mode='Markdown')
            
            # Request verification
            verification_message = JobFormatter.format_verification_request()
            await update.message.reply_text(verification_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Start command failed: {e}")
            await update.message.reply_text("Sorry, an error occurred. Please try again later.")
    
    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /verify command"""
        try:
            user_id = update.effective_user.id
            
            # In a real implementation, we would check if the user is a member of the channel
            # For this MVP, we'll just verify them automatically
            user = db_manager.verify_user(user_id)
            
            if user and user.verified:
                await update.message.reply_text("✅ You have been verified successfully!")
            else:
                await update.message.reply_text("❌ Verification failed. Please join our channel and try again.")
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            await update.message.reply_text("Sorry, an error occurred during verification.")
    
    async def jobs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /jobs command"""
        try:
            # Get recent jobs
            recent_jobs = db_manager.get_recent_jobs(limit=5)
            
            if not recent_jobs:
                await update.message.reply_text("No jobs available at the moment.")
                return
            
            # Format jobs
            job_messages = []
            for job in recent_jobs:
                job_data = {
                    'title': job.title,
                    'category_a': job.category_a,
                    'category_b': job.category_b,
                    'details_c': job.details_c,
                    'deadline_d': job.deadline_d,
                    'apply_link_e': job.apply_link_e,
                    'source_f': job.source_f,
                    'image_g': job.image_g
                }
                job_messages.append(JobFormatter.format_job_ag(job_data))
            
            # Send jobs
            for message in job_messages:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Jobs command failed: {e}")
            await update.message.reply_text("Sorry, an error occurred while fetching jobs.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            help_message = JobFormatter.format_help_message()
            await update.message.reply_text(help_message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Help command failed: {e}")
            await update.message.reply_text("Sorry, an error occurred.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get bot status
            job_count = db_manager.get_job_count()
            verified_users = db_manager.get_verified_users_count()
            last_update = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Format status message
            status_message = JobFormatter.format_status_message(
                job_count=job_count,
                verified_users=verified_users,
                last_update=last_update
            )
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Status command failed: {e}")
            await update.message.reply_text("Sorry, an error occurred while fetching status.")
    
    async def post_jobs_to_channel(self):
        """Post jobs to Telegram channel"""
        try:
            # Get recent jobs
            recent_jobs = db_manager.get_recent_jobs(limit=5)
            
            if not recent_jobs:
                logger.info("No jobs to post to channel")
                return
            
            # Format jobs
            job_messages = []
            for job in recent_jobs:
                job_data = {
                    'title': job.title,
                    'category_a': job.category_a,
                    'category_b': job.category_b,
                    'details_c': job.details_c,
                    'deadline_d': job.deadline_d,
                    'apply_link_e': job.apply_link_e,
                    'source_f': job.source_f,
                    'image_g': job.image_g
                }
                job_messages.append(JobFormatter.format_job_ag(job_data))
            
            # Post jobs to channel
            for message in job_messages:
                try:
                    await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"Posted job to channel: {job.title}")
                except TelegramError as e:
                    logger.error(f"Failed to post job to channel: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to post jobs to channel: {e}")
    
    def scrape_and_store_jobs(self):
        """Scrape jobs from all sources and store in database"""
        try:
            all_jobs = []
            
            # Scrape from all sources
            for scraper_name, scraper in scrapers.items():
                try:
                    logger.info(f"Scraping from {scraper_name}")
                    jobs = scraper.scrape()
                    all_jobs.extend(jobs)
                    logger.info(f"Found {len(jobs)} jobs from {scraper_name}")
                except Exception as e:
                    logger.error(f"Failed to scrape from {scraper_name}: {e}")
                    continue
            
            # Process and store jobs
            if all_jobs:
                for job in all_jobs:
                    try:
                        # Convert Job object to dict for processing
                        job_data = {
                            'title': job.title,
                            'category_a': job.category_a,
                            'category_b': job.category_b,
                            'details_c': job.details_c,
                            'deadline_d': job.deadline_d,
                            'apply_link_e': job.apply_link_e,
                            'source_f': job.source_f,
                            'image_g': job.image_g,
                            'url_hash': job.url_hash
                        }
                        
                        # Process job data
                        processed_job = JobProcessor.process_job_data(job_data)
                        
                        # Check if expired
                        if JobProcessor.is_job_expired(processed_job['deadline_d']):
                            logger.info(f"Skipping expired job: {processed_job['title']}")
                            continue
                        
                        # Add to database
                        db_manager.add_job(processed_job)
                        
                    except Exception as e:
                        logger.error(f"Failed to process job: {e}")
                        continue
            
            logger.info(f"Scraping completed. Total jobs processed: {len(all_jobs)}")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
    
    def health_check(self):
        """Perform health check"""
        try:
            job_count = db_manager.get_job_count()
            verified_users = db_manager.get_verified_users_count()
            
            logger.info(
                f"Health check: {job_count} jobs, {verified_users} verified users, "
                f"scheduler running: {self.scheduler.running}"
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    def run(self):
        """Run the bot"""
        try:
            logger.info("Starting bot...")
            self.application.run_polling()
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the bot gracefully"""
        try:
            logger.info("Shutting down bot...")
            self.scheduler.shutdown()
            if self.application:
                self.application.shutdown()
            logger.info("Bot shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == '__main__':
    try:
        # Initialize bot
        bot = GovernmentJobBot()
        bot.initialize()
        
        # Run bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        bot.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
