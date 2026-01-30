#!/usr/bin/env python3
"""
Quick verification script for Government Job Updates Telegram Bot
Run this to verify your setup is correct before starting the bot
"""

import sys

def verify_imports():
    """Verify all required packages are installed"""
    print("🔍 Verifying Python packages...")
    packages = [
        'telegram',
        'bs4',
        'requests',
        'schedule',
        'pytz',
        'json',
        'logging',
        'datetime',
        'threading',
        'hashlib',
        'time',
        'os',
        'pathlib'
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package} - NOT FOUND")
            return False
    return True

def verify_files():
    """Verify all required files exist"""
    print("\n🔍 Verifying required files...")
    required_files = [
        'config.py',
        'database.py',
        'scraper.py',
        'formatter.py',
        'bot.py',
        'admin.py',
        'run.sh',
        'requirements.txt'
    ]
    
    all_exist = True
    for file in required_files:
        try:
            with open(file, 'r'):
                pass
            print(f"  ✅ {file}")
        except FileNotFoundError:
            print(f"  ❌ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist

def verify_config():
    """Verify configuration is properly set"""
    print("\n🔍 Verifying configuration...")
    try:
        import config
        
        checks = [
            ('BOT_TOKEN', 'Your bot token'),
            ('ADMIN_ID', 'Your admin user ID'),
            ('CHANNEL_ID', 'Your channel ID'),
            ('CHANNEL_USERNAME', 'Your channel username')
        ]
        
        config_ok = True
        for attr, desc in checks:
            value = getattr(config, attr, None)
            if value and 'YOUR' not in str(value) and 'your' not in str(value).lower():
                print(f"  ✅ {attr} - {desc} configured")
            else:
                print(f"  ⚠️  {attr} - {desc} needs to be set")
                config_ok = False
        
        # Check websites and states
        if config.WEBSITES_TO_MONITOR:
            print(f"  ✅ {len(config.WEBSITES_TO_MONITOR)} websites configured")
        
        if config.STATE_WEBSITES:
            print(f"  ✅ {len(config.STATE_WEBSITES)} states configured")
        
        if config.JOB_CATEGORIES:
            print(f"  ✅ {len(config.JOB_CATEGORIES)} categories configured")
        
        return config_ok
        
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return False

def verify_database():
    """Verify database can be initialized"""
    print("\n🔍 Verifying database...")
    try:
        import database
        
        # Initialize directories
        database.initialize_directories()
        print("  ✅ Directories initialized")
        
        # Test file operations
        database.load_posted_jobs()
        print("  ✅ Can read posted_jobs.json")
        
        database.load_verified_users()
        print("  ✅ Can read verified_users.json")
        
        # Test logging
        database.log_action("Test log entry")
        print("  ✅ Can write logs")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def verify_scraper():
    """Verify scraper functions work"""
    print("\n🔍 Verifying scraper...")
    try:
        import scraper
        
        # Test job ID generation
        job_id = scraper.generate_job_id('Test', 'https://test.com')
        if len(job_id) == 12:
            print("  ✅ Job ID generation works")
        else:
            print("  ❌ Job ID generation issue")
            return False
        
        # Test category determination
        categories = scraper.determine_categories('Bank Clerk Recruitment')
        if 'Bank Jobs' in categories:
            print("  ✅ Category determination works")
        else:
            print("  ❌ Category determination issue")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def verify_formatter():
    """Verify formatter functions work"""
    print("\n🔍 Verifying formatter...")
    try:
        import formatter
        
        # Test help message
        help_msg = formatter.format_help_message()
        if help_msg and len(help_msg) > 100:
            print("  ✅ Help message formatting works")
        else:
            print("  ❌ Help message issue")
            return False
        
        # Test complete job format
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
        if 'Test Job' in formatted and 'Test Post' in formatted:
            print("  ✅ Job formatting works")
        else:
            print("  ❌ Job formatting issue")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def verify_bot():
    """Verify bot can be initialized (without starting)"""
    print("\n🔍 Verifying bot initialization...")
    try:
        from telegram.ext import Application
        import config
        
        # Create application (this doesn't start the bot)
        app = Application.builder().token(config.BOT_TOKEN).build()
        print("  ✅ Bot application can be created")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all verifications"""
    print("=" * 60)
    print("🤖 GOVERNMENT JOB UPDATES BOT - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    results = []
    
    # Run all verifications
    results.append(("Python Packages", verify_imports()))
    results.append(("Required Files", verify_files()))
    results.append(("Configuration", verify_config()))
    results.append(("Database", verify_database()))
    results.append(("Scraper", verify_scraper()))
    results.append(("Formatter", verify_formatter()))
    results.append(("Bot Initialization", verify_bot()))
    
    # Print summary
    print()
    print("=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Result: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Your bot is ready to run! 🎉")
        print()
        print("🚀 Start the bot with:")
        print("   python bot.py")
        print()
        print("   Or on Termux:")
        print("   bash run.sh")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("💡 Common issues:")
        print("   • Install missing packages: pip install -r requirements.txt")
        print("   • Configure config.py with your BOT_TOKEN, ADMIN_ID, CHANNEL_ID")
        print("   • Ensure all files are in the same directory")
        return 1

if __name__ == '__main__':
    sys.exit(main())
