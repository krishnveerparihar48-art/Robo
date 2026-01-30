"""
Database module for Government Job Updates Telegram Bot
Handles loading, saving, and managing job and user data
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import config

# Ensure directories exist
def initialize_directories():
    """Create necessary directories if they don't exist"""
    dirs = [config.DATABASE_DIR, config.LOGS_DIR, config.BACKUPS_DIR]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)

# Posted Jobs Database Functions
def load_posted_jobs():
    """
    Load posted jobs from JSON file
    
    Returns:
        dict: Dictionary of posted jobs with job_id as key
    """
    try:
        if os.path.exists(config.POSTED_JOBS_FILE):
            with open(config.POSTED_JOBS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        log_error(f"Error loading posted jobs: {str(e)}")
        return {}

def save_posted_jobs(jobs):
    """
    Save posted jobs to JSON file
    
    Args:
        jobs (dict): Dictionary of jobs to save
    """
    try:
        initialize_directories()
        with open(config.POSTED_JOBS_FILE, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log_error(f"Error saving posted jobs: {str(e)}")
        return False

def check_job_posted(job_id):
    """
    Check if a job has already been posted
    
    Args:
        job_id (str): Unique identifier for the job
        
    Returns:
        bool: True if job already posted, False otherwise
    """
    jobs = load_posted_jobs()
    return job_id in jobs

def add_posted_job(job_data):
    """
    Add a new job to the posted jobs database
    
    Args:
        job_data (dict): Job data dictionary containing:
            - job_id: Unique identifier
            - title: Job title
            - link: Application link
            - posted_date: Posting date
            - deadline: Application deadline
            - details: Complete job details dict
            - source: Source website
            
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        jobs = load_posted_jobs()
        job_id = job_data['job_id']
        
        jobs[job_id] = {
            'title': job_data.get('title', ''),
            'link': job_data.get('link', ''),
            'posted_date': job_data.get('posted_date', ''),
            'deadline': job_data.get('deadline', ''),
            'details': job_data.get('details', {}),
            'source': job_data.get('source', ''),
            'categories': job_data.get('categories', []),
            'last_notified': job_data.get('last_notified', {})
        }
        
        return save_posted_jobs(jobs)
    except Exception as e:
        log_error(f"Error adding posted job: {str(e)}")
        return False

def update_job_notification(job_id, notification_type):
    """
    Update the last notification time for a job
    
    Args:
        job_id (str): Job identifier
        notification_type (str): Type of notification (e.g., '3_days', 'final_day')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        jobs = load_posted_jobs()
        if job_id in jobs:
            if 'last_notified' not in jobs[job_id]:
                jobs[job_id]['last_notified'] = {}
            
            from datetime import datetime
            import pytz
            tz = pytz.timezone(config.TIMEZONE)
            now = datetime.now(tz).isoformat()
            
            jobs[job_id]['last_notified'][notification_type] = now
            return save_posted_jobs(jobs)
        return False
    except Exception as e:
        log_error(f"Error updating job notification: {str(e)}")
        return False

def get_jobs_deadline_soon(days=3):
    """
    Get jobs with deadlines approaching
    
    Args:
        days (int): Number of days to look ahead
        
    Returns:
        list: List of jobs with deadlines within the specified days
    """
    try:
        from datetime import datetime, timedelta
        import pytz
        
        jobs = load_posted_jobs()
        tz = pytz.timezone(config.TIMEZONE)
        now = datetime.now(tz)
        deadline_date = now + timedelta(days=days)
        
        upcoming_jobs = []
        for job_id, job in jobs.items():
            deadline_str = job.get('deadline', '')
            if deadline_str:
                try:
                    # Try to parse deadline
                    deadline = parse_deadline(deadline_str)
                    if deadline and now <= deadline <= deadline_date:
                        # Check if already notified
                        last_notified = job.get('last_notified', {}).get(f'{days}_days')
                        if not last_notified:
                            upcoming_jobs.append(job)
                except Exception as e:
                    log_error(f"Error parsing deadline for job {job_id}: {str(e)}")
                    continue
        
        return upcoming_jobs
    except Exception as e:
        log_error(f"Error getting upcoming deadline jobs: {str(e)}")
        return []

def get_jobs_deadline_today():
    """
    Get jobs with deadline today
    
    Returns:
        list: List of jobs with deadline today
    """
    try:
        from datetime import datetime, timedelta
        import pytz
        
        jobs = load_posted_jobs()
        tz = pytz.timezone(config.TIMEZONE)
        now = datetime.now(tz)
        today_end = now.replace(hour=23, minute=59, second=59)
        
        deadline_today = []
        for job_id, job in jobs.items():
            deadline_str = job.get('deadline', '')
            if deadline_str:
                try:
                    deadline = parse_deadline(deadline_str)
                    if deadline and now <= deadline <= today_end:
                        # Check if already notified
                        last_notified = job.get('last_notified', {}).get('final_day')
                        if not last_notified:
                            deadline_today.append(job)
                except Exception as e:
                    log_error(f"Error parsing deadline for job {job_id}: {str(e)}")
                    continue
        
        return deadline_today
    except Exception as e:
        log_error(f"Error getting today's deadline jobs: {str(e)}")
        return []

def get_latest_jobs(limit=5):
    """
    Get the most recently posted jobs
    
    Args:
        limit (int): Maximum number of jobs to return
        
    Returns:
        list: List of recent jobs
    """
    try:
        jobs = load_posted_jobs()
        # Sort by posted_date
        sorted_jobs = sorted(
            jobs.values(),
            key=lambda x: x.get('posted_date', ''),
            reverse=True
        )
        return sorted_jobs[:limit]
    except Exception as e:
        log_error(f"Error getting latest jobs: {str(e)}")
        return []

def get_jobs_by_state(state_name):
    """
    Get jobs related to a specific state
    
    Args:
        state_name (str): Name of the state
        
    Returns:
        list: List of jobs for the state
    """
    try:
        jobs = load_posted_jobs()
        state_jobs = []
        
        state_lower = state_name.lower()
        for job in jobs.values():
            title = job.get('title', '').lower()
            # Check if state name appears in title or details
            if state_lower in title or state_name in job.get('source', ''):
                state_jobs.append(job)
        
        return state_jobs[:config.JOBS_PER_FEED]
    except Exception as e:
        log_error(f"Error getting jobs by state: {str(e)}")
        return []

def get_jobs_by_category(category):
    """
    Get jobs by category
    
    Args:
        category (str): Job category
        
    Returns:
        list: List of jobs in the category
    """
    try:
        jobs = load_posted_jobs()
        category_jobs = []
        
        category_lower = category.lower()
        for job in jobs.values():
            categories = job.get('categories', [])
            title = job.get('title', '').lower()
            
            # Check if category matches
            if category_lower in [c.lower() for c in categories]:
                category_jobs.append(job)
            elif category_lower in title:
                category_jobs.append(job)
        
        return category_jobs[:config.JOBS_PER_FEED]
    except Exception as e:
        log_error(f"Error getting jobs by category: {str(e)}")
        return []

def parse_deadline(deadline_str):
    """
    Parse deadline string to datetime object
    
    Args:
        deadline_str (str): Deadline date string
        
    Returns:
        datetime or None: Parsed datetime object or None
    """
    try:
        from datetime import datetime
        import pytz
        
        # Try different date formats
        formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(deadline_str.split('T')[0], fmt)
                tz = pytz.timezone(config.TIMEZONE)
                return tz.localize(dt)
            except ValueError:
                continue
        
        return None
    except Exception as e:
        log_error(f"Error parsing deadline string: {str(e)}")
        return None

# Verified Users Database Functions
def load_verified_users():
    """
    Load verified users from JSON file
    
    Returns:
        dict: Dictionary of verified users with user_id as key
    """
    try:
        if os.path.exists(config.VERIFIED_USERS_FILE):
            with open(config.VERIFIED_USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        log_error(f"Error loading verified users: {str(e)}")
        return {}

def save_verified_users(users):
    """
    Save verified users to JSON file
    
    Args:
        users (dict): Dictionary of users to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        initialize_directories()
        with open(config.VERIFIED_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log_error(f"Error saving verified users: {str(e)}")
        return False

def add_verified_user(user_id, username=None, first_name=None):
    """
    Add or update a verified user
    
    Args:
        user_id (int): Telegram user ID
        username (str): Telegram username (optional)
        first_name (str): User's first name (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from datetime import datetime
        import pytz
        
        users = load_verified_users()
        tz = pytz.timezone(config.TIMEZONE)
        
        users[str(user_id)] = {
            'verified': True,
            'verify_date': datetime.now(tz).isoformat(),
            'username': username,
            'first_name': first_name,
            'status': 'active'
        }
        
        return save_verified_users(users)
    except Exception as e:
        log_error(f"Error adding verified user: {str(e)}")
        return False

def is_user_verified(user_id):
    """
    Check if a user is verified
    
    Args:
        user_id (int): Telegram user ID
        
    Returns:
        bool: True if verified, False otherwise
    """
    try:
        users = load_verified_users()
        user = users.get(str(user_id), {})
        return user.get('verified', False)
    except Exception as e:
        log_error(f"Error checking user verification: {str(e)}")
        return False

def get_verified_user_count():
    """
    Get total number of verified users
    
    Returns:
        int: Count of verified users
    """
    try:
        users = load_verified_users()
        return sum(1 for user in users.values() if user.get('verified', False))
    except Exception as e:
        log_error(f"Error getting verified user count: {str(e)}")
        return 0

def remove_verified_user(user_id):
    """
    Remove a user from verified users list
    
    Args:
        user_id (int): Telegram user ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        users = load_verified_users()
        if str(user_id) in users:
            del users[str(user_id)]
            return save_verified_users(users)
        return False
    except Exception as e:
        log_error(f"Error removing verified user: {str(e)}")
        return False

# Backup Functions
def backup_database():
    """
    Create backup of database files
    
    Returns:
        str: Path to backup file or None if failed
    """
    try:
        initialize_directories()
        from datetime import datetime
        import pytz
        
        tz = pytz.timezone(config.TIMEZONE)
        timestamp = datetime.now(tz).strftime('%Y%m%d_%H%M%S')
        
        backup_filename = f"backup_{timestamp}.json"
        backup_path = os.path.join(config.BACKUPS_DIR, backup_filename)
        
        # Create combined backup
        backup_data = {
            'backup_date': datetime.now(tz).isoformat(),
            'posted_jobs': load_posted_jobs(),
            'verified_users': load_verified_users()
        }
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Keep only last 10 backups
        cleanup_old_backups()
        
        log_action(f"Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        log_error(f"Error creating database backup: {str(e)}")
        return None

def cleanup_old_backups(keep_count=10):
    """
    Remove old backup files, keeping only the most recent ones
    
    Args:
        keep_count (int): Number of recent backups to keep
    """
    try:
        backup_files = []
        for file in os.listdir(config.BACKUPS_DIR):
            if file.startswith('backup_') and file.endswith('.json'):
                file_path = os.path.join(config.BACKUPS_DIR, file)
                backup_files.append((os.path.getmtime(file_path), file_path))
        
        # Sort by modification time (oldest first)
        backup_files.sort()
        
        # Remove old backups
        files_to_delete = len(backup_files) - keep_count
        for i in range(files_to_delete):
            try:
                os.remove(backup_files[i][1])
                log_action(f"Old backup removed: {backup_files[i][1]}")
            except Exception as e:
                log_error(f"Error removing old backup: {str(e)}")
    except Exception as e:
        log_error(f"Error cleaning up old backups: {str(e)}")

# Logging Functions
def log_action(message):
    """
    Log action to bot.log file
    
    Args:
        message (str): Message to log
    """
    try:
        initialize_directories()
        log_file = os.path.join(config.LOGS_DIR, 'bot.log')
        
        from datetime import datetime
        import pytz
        tz = pytz.timezone(config.TIMEZONE)
        timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Error logging action: {str(e)}")

def log_error(message):
    """
    Log error to errors.log file
    
    Args:
        message (str): Error message to log
    """
    try:
        initialize_directories()
        error_file = os.path.join(config.LOGS_DIR, 'errors.log')
        
        from datetime import datetime
        import pytz
        tz = pytz.timezone(config.TIMEZONE)
        timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        
        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] ERROR: {message}\n")
    except Exception as e:
        print(f"Error logging error: {str(e)}")

# Statistics Functions
def get_statistics():
    """
    Get bot statistics
    
    Returns:
        dict: Statistics dictionary
    """
    try:
        jobs = load_posted_jobs()
        users = load_verified_users()
        
        # Count jobs by source
        source_counts = {}
        for job in jobs.values():
            source = job.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_jobs_posted': len(jobs),
            'verified_users': get_verified_user_count(),
            'sources': source_counts,
            'last_backup': get_last_backup_time()
        }
    except Exception as e:
        log_error(f"Error getting statistics: {str(e)}")
        return {}

def get_last_backup_time():
    """
    Get the time of the most recent backup
    
    Returns:
        str or None: Backup timestamp or None
    """
    try:
        backup_files = []
        for file in os.listdir(config.BACKUPS_DIR):
            if file.startswith('backup_') and file.endswith('.json'):
                file_path = os.path.join(config.BACKUPS_DIR, file)
                backup_files.append(os.path.getmtime(file_path))
        
        if backup_files:
            from datetime import datetime
            return datetime.fromtimestamp(max(backup_files)).strftime('%Y-%m-%d %H:%M:%S')
        return None
    except Exception as e:
        return None

# Initialize on import
initialize_directories()
