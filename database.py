import json
import os
import shutil
from datetime import datetime
from config import POSTED_JOBS_FILE, VERIFIED_USERS_FILE

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except IOError:
        return False

# Posted Jobs Management
def load_posted_jobs():
    return load_json(POSTED_JOBS_FILE)

def save_posted_job(job_id, job_data):
    jobs = load_posted_jobs()
    jobs[job_id] = job_data
    save_json(POSTED_JOBS_FILE, jobs)

def is_job_posted(job_id):
    jobs = load_posted_jobs()
    return job_id in jobs

# User Management
def load_verified_users():
    return load_json(VERIFIED_USERS_FILE)

def add_verified_user(user_id):
    users = load_verified_users()
    users[str(user_id)] = {
        "verified": True,
        "verify_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    save_json(VERIFIED_USERS_FILE, users)

def is_user_verified(user_id):
    users = load_verified_users()
    user = users.get(str(user_id))
    if user and user.get("verified"):
        return True
    return False

def get_verified_user_count():
    users = load_verified_users()
    return len(users)

# Backup
def backup_database():
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if os.path.exists(POSTED_JOBS_FILE):
        shutil.copy2(POSTED_JOBS_FILE, os.path.join(backup_dir, f"posted_jobs_{timestamp}.json"))
        
    if os.path.exists(VERIFIED_USERS_FILE):
        shutil.copy2(VERIFIED_USERS_FILE, os.path.join(backup_dir, f"verified_users_{timestamp}.json"))

# Initialization
def init_db():
    if not os.path.exists(POSTED_JOBS_FILE):
        save_json(POSTED_JOBS_FILE, {})
    if not os.path.exists(VERIFIED_USERS_FILE):
        save_json(VERIFIED_USERS_FILE, {})
