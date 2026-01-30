# 🧪 Government Job Updates Bot - Testing Guide

This guide provides step-by-step testing instructions for each module of the Government Job Updates Telegram Bot.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Module Testing](#module-testing)
3. [Integration Testing](#integration-testing)
4. [User Testing](#user-testing)
5. [Admin Testing](#admin-testing)

---

## Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output:**
- All packages install without errors
- No dependency conflicts

### 2. Create Test Configuration

```bash
# Test if config loads correctly
python -c "import config; print('Config loaded successfully')"
```

**Expected Output:**
```
Config loaded successfully
```

---

## Module Testing

### Test 1: Database Module

#### Test 1.1: Initialize Directories
```bash
python -c "import database; database.initialize_directories(); print('Directories initialized')"
```

**Expected Output:**
- No errors
- Directories created: `database/`, `logs/`, `backups/`

#### Test 1.2: Create Sample Job
```bash
python << 'EOF'
import database

job_data = {
    'job_id': 'test_job_001',
    'title': 'Test Job Vacancy',
    'link': 'https://example.com/apply',
    'posted_date': '2024-01-30',
    'deadline': '2024-02-15',
    'source': 'Test Source',
    'categories': ['Test Category'],
    'details': {
        'A': 'Test Post Name',
        'B': 'Test Eligibility',
        'C': 'Test Age Limit',
        'D': 'Test Salary',
        'E': 'Test Dates',
        'F': 'Test Fee',
        'G': 'Test Selection'
    }
}

result = database.add_posted_job(job_data)
print(f"Job added: {result}")
print(f"Total jobs: {len(database.load_posted_jobs())}")
EOF
```

**Expected Output:**
```
Job added: True
Total jobs: 1
```

#### Test 1.3: Check Duplicate Prevention
```bash
python << 'EOF'
import database

# Try to add same job again
job_data = {
    'job_id': 'test_job_001',  # Same ID
    'title': 'Test Job Vacancy',
    'link': 'https://example.com/apply',
    'posted_date': '2024-01-30',
    'deadline': '2024-02-15',
    'source': 'Test Source',
    'categories': ['Test Category'],
    'details': {}
}

is_posted = database.check_job_posted('test_job_001')
print(f"Already posted: {is_posted}")
EOF
```

**Expected Output:**
```
Already posted: True
```

#### Test 1.4: User Verification
```bash
python << 'EOF'
import database

# Add test user
result = database.add_verified_user(123456, 'testuser', 'Test User')
print(f"User added: {result}")

# Check verification
is_verified = database.is_user_verified(123456)
print(f"User verified: {is_verified}")

# Get user count
count = database.get_verified_user_count()
print(f"Total verified users: {count}")
EOF
```

**Expected Output:**
```
User added: True
User verified: True
Total verified users: 1
```

#### Test 1.5: Backup Creation
```bash
python -c "import database; backup_path = database.backup_database(); print(f'Backup created: {backup_path}')"
```

**Expected Output:**
- Returns path to backup file
- File exists in `backups/` directory

---

### Test 2: Scraper Module

#### Test 2.1: Test Request Function
```bash
python << 'EOF'
import scraper

response = scraper.make_request('https://www.google.com')
if response:
    print(f"Request successful: Status {response.status_code}")
else:
    print("Request failed")
EOF
```

**Expected Output:**
```
Request successful: Status 200
```

#### Test 2.2: Test Job ID Generation
```bash
python << 'EOF'
import scraper

job_id1 = scraper.generate_job_id('Test Job', 'https://example.com/1')
job_id2 = scraper.generate_job_id('Test Job', 'https://example.com/1')
job_id3 = scraper.generate_job_id('Test Job', 'https://example.com/2')

print(f"Job ID 1: {job_id1}")
print(f"Job ID 2: {job_id2}")
print(f"Job ID 3: {job_id3}")
print(f"Same job same ID: {job_id1 == job_id2}")
print(f"Different job different ID: {job_id1 != job_id3}")
EOF
```

**Expected Output:**
```
Job ID 1: <12-char hash>
Job ID 2: <12-char hash>
Job ID 3: <12-char hash>
Same job same ID: True
Different job different ID: True
```

#### Test 2.3: Test Category Determination
```bash
python << 'EOF'
import scraper

titles = [
    'Bank Clerk Recruitment 2024',
    'Railway Group D Vacancy',
    'SSC CGL Exam 2024',
    'UPSC Civil Services',
    'Police Constable Bharti'
]

for title in titles:
    categories = scraper.determine_categories(title)
    print(f"{title}: {categories}")
EOF
```

**Expected Output:**
```
Bank Clerk Recruitment 2024: ['Bank Jobs']
Railway Group D Vacancy: ['Railway Jobs']
SSC CGL Exam 2024: ['SSC Jobs']
UPSC Civil Services: ['UPSC Jobs']
Police Constable Bharti: ['Police Jobs']
```

#### Test 2.4: Test Scraper (with network)
```bash
python << 'EOF'
import scraper

print("Testing Sarkari Result scraper...")
jobs = scraper.scrape_sarkari_result()
print(f"Found {len(jobs)} jobs")

if jobs:
    print(f"First job: {jobs[0]['title'][:50]}...")
EOF
```

**Expected Output:**
- Either jobs found and displayed, or
- Uses cached jobs if scraping fails
- No crashes or unhandled exceptions

---

### Test 3: Formatter Module

#### Test 3.1: Test Complete Job Format
```bash
python << 'EOF'
import formatter

job_data = {
    'title': 'Test Job Vacancy - 100 Posts',
    'link': 'https://example.com/apply',
    'posted_date': '2024-01-30',
    'source': 'Test Website',
    'details': {
        'A': 'Clerk, Assistant - 100 Posts',
        'B': 'Graduate in any discipline',
        'C': '18-30 years',
        'D': 'Rs. 25,500-81,100/- per month',
        'E': 'Start: 01-02-2024, Last Date: 15-02-2024',
        'F': 'Rs. 100/- for General, Nil for SC/ST',
        'G': 'Written Exam, Interview'
    }
}

formatted = formatter.format_complete_job(job_data)
print(formatted)
EOF
```

**Expected Output:**
- Formatted message with A-G sections
- All sections show actual data (no placeholders)
- Proper formatting with emojis and sections

#### Test 3.2: Test Breaking News Format
```bash
python << 'EOF'
import formatter

job_data = {
    'title': 'New Job Alert - Apply Now',
    'link': 'https://example.com/apply',
    'source': 'Breaking News',
    'details': {
        'A': 'Various Posts',
        'B': '10th Pass',
        'C': '21-30 Years',
        'D': 'As per rules',
        'E': 'Apply Soon'
    }
}

formatted = formatter.format_breaking_news(job_data)
print(formatted)
EOF
```

**Expected Output:**
- Breaking news format with urgency
- Includes Apply Now button indicator
- Shows deadline

#### Test 3.3: Test Last 3 Days Format
```bash
python << 'EOF'
import formatter

job_data = {
    'title': 'Closing Soon Job',
    'link': 'https://example.com/apply',
    'source': 'Alert',
    'details': {
        'A': '100 Posts',
        'E': 'Closing in 3 days'
    }
}

formatted = formatter.format_last_3_days(job_data)
print(formatted)
EOF
```

**Expected Output:**
- Urgent warning message
- "3 days left" prominent
- Apply Now button indicator

#### Test 3.4: Test Final Day Format
```bash
python << 'EOF'
import formatter

job_data = {
    'title': 'Last Day Job',
    'link': 'https://example.com/apply',
    'source': 'Final Alert',
    'details': {
        'A': '50 Posts',
        'E': 'Today'
    }
}

formatted = formatter.format_final_day(job_data)
print(formatted)
EOF
```

**Expected Output:**
- Critical urgency message
- "TODAY" or "LAST DAY" prominent
- Strong call to action

#### Test 3.5: Test Job List Format
```bash
python << 'EOF'
import formatter

jobs = [
    {
        'title': 'Job One - 100 Posts',
        'source': 'Website 1',
        'posted_date': '2024-01-28'
    },
    {
        'title': 'Job Two - 50 Posts',
        'source': 'Website 2',
        'posted_date': '2024-01-29'
    }
]

formatted = formatter.format_job_list(jobs, "Test List")
print(formatted)
EOF
```

**Expected Output:**
- Formatted list with numbers
- Shows source and date
- Total count at bottom

---

## Integration Testing

### Test 4: Bot Commands

**Note:** These tests require a valid BOT_TOKEN in config.py

#### Test 4.1: Test Bot Initialization
```bash
python << 'EOF'
from telegram.ext import Application
import config

app = Application.builder().token(config.BOT_TOKEN).build()
print("Bot application created successfully")
EOF
```

**Expected Output:**
```
Bot application created successfully
```
**Error if:** BOT_TOKEN is invalid or missing

#### Test 4.2: Test Start Command Handler
```bash
python << 'EOF'
# Simulate start command logic
import database

# Mock user
user_id = 123456
username = 'testuser'

# Check if verified
is_verified = database.is_user_verified(user_id)
print(f"User verified: {is_verified}")

if not is_verified:
    print("Would show verification screen")
else:
    print("Would show welcome message")
EOF
```

**Expected Output:**
```
User verified: False
Would show verification screen
```

---

## User Testing

### Test 5: End-to-End User Flow

#### Test 5.1: Verification Flow
1. Start a chat with your bot
2. Send `/start`
3. **Expected:**
   - Channel verification screen appears
   - "Join Channel" button works
   - After joining, "Verify Me" button works
   - Welcome message appears after verification

#### Test 5.2: Browse Latest Jobs
1. Send `/latest`
2. **Expected:**
   - Shows 5 most recent jobs
   - Each job has Apply Now button
   - Jobs show title, source, and date

#### Test 5.3: State Filtering
1. Send `/states`
2. **Expected:** List of all states appears
3. Send `/state up`
4. **Expected:** Jobs from Uttar Pradesh appear

#### Test 5.4: Category Filtering
1. Send `/categories`
2. **Expected:** List of all categories appears
3. Send `/category bank jobs`
4. **Expected:** Bank-related jobs appear

#### Test 5.5: Help Command
1. Send `/help`
2. **Expected:**
   - Complete help message appears
   - All commands listed
   - Usage instructions provided

---

## Admin Testing

**Note:** Only runs from your ADMIN_ID account

### Test 6: Admin Commands

#### Test 6.1: Test Admin Stats
1. Send `/admin_stats`
2. **Expected:**
   - Total jobs posted
   - Verified users count
   - Jobs by source
   - Last backup time

#### Test 6.2: Test Admin Update
1. Send `/admin_update`
2. **Expected:**
   - Status message: "Starting manual job update..."
   - Scrapes all websites
   - Shows results (new jobs, existing jobs)
   - Backup created

#### Test 6.3: Test Admin Test
1. Send `/admin_test Test Message`
2. **Expected:**
   - Message posted to your channel
   - Confirmation in chat

#### Test 6.4: Test Admin Users
1. Send `/admin_users`
2. **Expected:**
   - Total verified users
   - Active/inactive count
   - Recent users list

#### Test 6.5: Test Admin Backup
1. Send `/admin_backup`
2. **Expected:**
   - Backup created message
   - Backup file path shown

---

## Automation Tests

### Test 7: Automated Test Suite

Create `test_bot.py`:

```python
#!/usr/bin/env python3
"""
Automated test suite for Government Job Updates Bot
"""

import sys

def run_tests():
    """Run all tests"""
    tests_passed = 0
    tests_failed = 0
    
    print("=" * 60)
    print("GOVERNMENT JOB UPDATES BOT - AUTOMATED TESTS")
    print("=" * 60)
    print()
    
    # Test 1: Imports
    print("[1/10] Testing imports...")
    try:
        import config
        import database
        import scraper
        import formatter
        print("✅ All imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Import failed: {e}")
        tests_failed += 1
    
    # Test 2: Config
    print("\n[2/10] Testing configuration...")
    try:
        assert hasattr(config, 'BOT_TOKEN')
        assert hasattr(config, 'ADMIN_ID')
        assert hasattr(config, 'CHANNEL_ID')
        assert hasattr(config, 'WEBSITES_TO_MONITOR')
        assert hasattr(config, 'JOB_CATEGORIES')
        print("✅ Configuration loaded")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        tests_failed += 1
    
    # Test 3: Database
    print("\n[3/10] Testing database...")
    try:
        database.initialize_directories()
        print("✅ Database initialized")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Database error: {e}")
        tests_failed += 1
    
    # Test 4: Job Operations
    print("\n[4/10] Testing job operations...")
    try:
        test_job = {
            'job_id': 'test_auto_001',
            'title': 'Auto Test Job',
            'link': 'https://test.com',
            'posted_date': '2024-01-30',
            'deadline': '2024-02-15',
            'source': 'Auto Test',
            'categories': ['Test'],
            'details': {}
        }
        database.add_posted_job(test_job)
        assert database.check_job_posted('test_auto_001')
        print("✅ Job operations work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Job operations error: {e}")
        tests_failed += 1
    
    # Test 5: User Operations
    print("\n[5/10] Testing user operations...")
    try:
        database.add_verified_user(999999, 'autotest', 'Auto Test')
        assert database.is_user_verified(999999)
        print("✅ User operations work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ User operations error: {e}")
        tests_failed += 1
    
    # Test 6: Scraper
    print("\n[6/10] Testing scraper...")
    try:
        import scraper
        job_id = scraper.generate_job_id('Test', 'https://test.com')
        assert len(job_id) == 12
        print("✅ Scraper functions work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        tests_failed += 1
    
    # Test 7: Formatter
    print("\n[7/10] Testing formatter...")
    try:
        test_job = {
            'title': 'Test Job',
            'link': 'https://test.com',
            'posted_date': '2024-01-30',
            'source': 'Test',
            'details': {
                'A': 'Test Post',
                'B': 'Test Eligibility',
                'C': 'Test Age',
                'D': 'Test Salary',
                'E': 'Test Dates',
                'F': 'Test Fee',
                'G': 'Test Process'
            }
        }
        formatted = formatter.format_complete_job(test_job)
        assert 'Test Job' in formatted
        print("✅ Formatter works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Formatter error: {e}")
        tests_failed += 1
    
    # Test 8: Backup
    print("\n[8/10] Testing backup...")
    try:
        database.backup_database()
        print("✅ Backup works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Backup error: {e}")
        tests_failed += 1
    
    # Test 9: Statistics
    print("\n[9/10] Testing statistics...")
    try:
        stats = database.get_statistics()
        assert 'total_jobs_posted' in stats
        assert 'verified_users' in stats
        print("✅ Statistics work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        tests_failed += 1
    
    # Test 10: Logs
    print("\n[10/10] Testing logging...")
    try:
        database.log_action("Test log entry")
        database.log_error("Test error entry")
        print("✅ Logging works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Logging error: {e}")
        tests_failed += 1
    
    # Summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/10")
    print(f"Tests Failed: {tests_failed}/10")
    print()
    
    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"⚠️ {tests_failed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
```

**Run automated tests:**
```bash
chmod +x test_bot.py
python test_bot.py
```

**Expected Output:**
```
============================================================
GOVERNMENT JOB UPDATES BOT - AUTOMATED TESTS
============================================================

[1/10] Testing imports...
✅ All imports successful

[2/10] Testing configuration...
✅ Configuration loaded

... (all tests pass) ...

============================================================
TEST SUMMARY
============================================================
Tests Passed: 10/10
Tests Failed: 0/10

🎉 ALL TESTS PASSED! 🎉
```

---

## Common Issues and Solutions

### Issue: Import Errors
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: Configuration Errors
**Solution:** Verify BOT_TOKEN, ADMIN_ID, CHANNEL_ID in config.py

### Issue: Scraping Fails
**Solution:** Check internet connection and website availability

### Issue: Database Errors
**Solution:** Ensure directories exist and are writable

### Issue: Permission Errors
**Solution:** Check file permissions for database/ and logs/

---

## Test Checklist

Use this checklist to verify all features:

- [ ] Configuration loads correctly
- [ ] Database operations work
- [ ] Scraper extracts job data
- [ ] Formatter creates proper messages
- [ ] Bot starts without errors
- [ ] /start command works
- [ ] Channel verification works
- [ ] /latest command shows jobs
- [ ] /state command filters by state
- [ ] /category command filters by category
- [ ] /help command shows help
- [ ] Admin commands accessible to admin only
- [ ] /admin_stats shows statistics
- [ ] /admin_update scrapes websites
- [ ] /admin_test posts to channel
- [ ] Scheduled scraping runs
- [ ] Deadline reminders work
- [ ] Backups are created
- [ ] Logs are written
- [ ] Auto-restart works

---

**Complete testing before deploying to production!** ✅
