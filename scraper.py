"""
Web Scraper Module for Government Job Updates Telegram Bot
Scrapes job data from various government job websites
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import config
import database

# Headers to mimic browser requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def make_request(url, max_retries=None):
    """
    Make HTTP request with retry logic
    
    Args:
        url (str): URL to request
        max_retries (int): Maximum number of retries (default from config)
        
    Returns:
        Response or None: Response object or None if failed
    """
    if max_retries is None:
        max_retries = config.MAX_RETRIES
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        except Exception as e:
            database.log_error(f"Request failed (attempt {attempt + 1}/{max_retries}) for {url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue
    
    return None

def generate_job_id(title, link):
    """
    Generate unique job ID from title and link
    
    Args:
        title (str): Job title
        link (str): Job link
        
    Returns:
        str: Unique job ID
    """
    import hashlib
    content = f"{title}{link}".encode('utf-8')
    return hashlib.md5(content).hexdigest()[:12]

def scrape_sarkari_result():
    """
    Scrape job listings from Sarkari Result website
    
    Returns:
        list: List of job dictionaries
    """
    try:
        database.log_action("Starting Sarkari Result scraping")
        
        url = "https://www.sarkariresult.com"
        response = make_request(url)
        
        if not response:
            database.log_error("Failed to fetch Sarkari Result main page")
            return get_cached_jobs("sarkari_result")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # Find job listing sections
        # Look for links that typically contain job postings
        job_sections = soup.find_all('div', class_='box') or soup.find_all('div', class_='post')
        
        if not job_sections:
            # Alternative: Look for all links in the main content
            job_sections = soup.find_all('a', href=True)
        
        for section in job_sections[:20]:  # Limit to first 20 jobs
            try:
                if hasattr(section, 'get_text'):
                    title = section.get_text(strip=True)
                else:
                    title = section.get('title', '').strip()
                
                if hasattr(section, 'get'):
                    link = section.get('href', '')
                else:
                    link = section
                
                # Filter for relevant job links
                if (title and 
                    link and 
                    any(keyword in title.lower() for keyword in ['vacancy', 'recruitment', 'exam', 'result', 'admit card', 'apply', 'online']) and
                    not any(skip in title.lower() for skip in ['answer key', 'admit card', 'result'])):
                    
                    # Get full URL if relative
                    if link and not link.startswith('http'):
                        link = url + link
                    
                    # Scrape job details
                    job_details = scrape_job_details(link)
                    
                    job_id = generate_job_id(title, link)
                    
                    # Check if already posted
                    if database.check_job_posted(job_id):
                        continue
                    
                    job = {
                        'job_id': job_id,
                        'title': title,
                        'link': link,
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'deadline': job_details.get('deadline', ''),
                        'source': 'Sarkari Result',
                        'categories': determine_categories(title),
                        'details': job_details
                    }
                    
                    jobs.append(job)
                    database.log_action(f"Found job: {title[:50]}...")
                    
            except Exception as e:
                database.log_error(f"Error parsing job section: {str(e)}")
                continue
        
        database.log_action(f"Sarkari Result scraping completed: {len(jobs)} jobs found")
        
        # Add delay before next request
        time.sleep(config.REQUEST_DELAY_SECONDS)
        
        return jobs
        
    except Exception as e:
        database.log_error(f"Error in scrape_sarkari_result: {str(e)}")
        return get_cached_jobs("sarkari_result")

def scrape_job_details(url):
    """
    Scrape detailed job information from a job page
    
    Args:
        url (str): Job page URL
        
    Returns:
        dict: Job details dictionary with sections A-G
    """
    try:
        response = make_request(url)
        if not response:
            return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            'A': '',  # Post Name/Vacancy
            'B': '',  # Eligibility/Education
            'C': '',  # Age Limit
            'D': '',  # Salary/Pay Scale
            'E': '',  # Important Dates
            'F': '',  # Application Fee
            'G': ''   # Selection Process/How to Apply
        }
        
        # Try to find job details in common patterns
        text_content = soup.get_text()
        
        # Extract Post Name
        post_match = re.search(r'(?:Post Name|Vacancy|Posts?)[:\s]*([^\n]+)', text_content, re.IGNORECASE)
        if post_match:
            details['A'] = post_match.group(1).strip()
        
        # Extract Eligibility
        eligibility_match = re.search(r'(?:Eligibility|Qualification|Education|Qualification)[:\s]*([^\n]+(?:\n[^A-Z]{1,50}){0,3})', text_content, re.IGNORECASE)
        if eligibility_match:
            details['B'] = eligibility_match.group(1).strip()
        
        # Extract Age Limit
        age_match = re.search(r'(?:Age Limit|Age)[:\s]*([^\n]+)', text_content, re.IGNORECASE)
        if age_match:
            details['C'] = age_match.group(1).strip()
        
        # Extract Salary
        salary_match = re.search(r'(?:Salary|Pay Scale|Pay Level)[:\s]*([^\n]+(?:\n[^A-Z]{1,50}){0,2})', text_content, re.IGNORECASE)
        if salary_match:
            details['D'] = salary_match.group(1).strip()
        
        # Extract Important Dates
        date_match = re.search(r'(?:Important Dates|Dates)[:\s]*([^\n]+(?:\n[^\n]+){0,5})', text_content, re.IGNORECASE)
        if date_match:
            dates_text = date_match.group(1).strip()
            # Try to extract deadline
            deadline_match = re.search(r'(?:Last Date|Closing Date|Deadline)[:\s]*([^\n]+)', dates_text, re.IGNORECASE)
            if deadline_match:
                details['E'] = dates_text
            else:
                details['E'] = dates_text
        
        # Extract Application Fee
        fee_match = re.search(r'(?:Application Fee|Fee)[:\s]*([^\n]+(?:\n[^\n]+){0,3})', text_content, re.IGNORECASE)
        if fee_match:
            details['F'] = fee_match.group(1).strip()
        
        # Extract Selection Process
        selection_match = re.search(r'(?:Selection Process|How to Apply)[:\s]*([^\n]+(?:\n[^\n]+){0,5})', text_content, re.IGNORECASE)
        if selection_match:
            details['G'] = selection_match.group(1).strip()
        
        # If details are empty, try alternate patterns
        if not any(details.values()):
            details = extract_details_alternate(soup)
        
        return details
        
    except Exception as e:
        database.log_error(f"Error scraping job details from {url}: {str(e)}")
        return {}

def extract_details_alternate(soup):
    """
    Extract job details using alternative patterns
    
    Args:
        soup (BeautifulSoup): Parsed HTML
        
    Returns:
        dict: Job details dictionary
    """
    details = {
        'A': '', 'B': '', 'C': '', 'D': '', 'E': '', 'F': '', 'G': ''
    }
    
    try:
        # Look for tables with job information
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    if 'post' in key and not details['A']:
                        details['A'] = value
                    elif 'eligibility' in key or 'qualification' in key and not details['B']:
                        details['B'] = value
                    elif 'age' in key and not details['C']:
                        details['C'] = value
                    elif 'salary' in key or 'pay' in key and not details['D']:
                        details['D'] = value
                    elif 'date' in key and not details['E']:
                        details['E'] = value
                    elif 'fee' in key and not details['F']:
                        details['F'] = value
                    elif 'selection' in key and not details['G']:
                        details['G'] = value
        
        # Look for lists
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if 'post' in text.lower() and not details['A']:
                    details['A'] = text
                elif 'qualification' in text.lower() and not details['B']:
                    details['B'] = text
                elif 'age' in text.lower() and not details['C']:
                    details['C'] = text
        
    except Exception as e:
        database.log_error(f"Error in alternate detail extraction: {str(e)}")
    
    return details

def scrape_free_job_alert():
    """
    Scrape job listings from Free Job Alert website
    
    Returns:
        list: List of job dictionaries
    """
    try:
        database.log_action("Starting Free Job Alert scraping")
        
        url = "https://www.freejobalert.com"
        response = make_request(url)
        
        if not response:
            database.log_error("Failed to fetch Free Job Alert main page")
            return get_cached_jobs("free_job_alert")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # Look for job listings
        job_links = soup.find_all('a', href=True)
        
        for link in job_links[:30]:
            try:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Filter for job postings
                if (title and 
                    href and 
                    any(keyword in title.lower() for keyword in ['vacancy', 'recruitment', 'apply online', 'latest']) and
                    len(title) > 20):
                    
                    # Get full URL
                    if not href.startswith('http'):
                        href = url + href
                    
                    # Scrape details
                    job_details = scrape_job_details(href)
                    
                    job_id = generate_job_id(title, href)
                    
                    if database.check_job_posted(job_id):
                        continue
                    
                    job = {
                        'job_id': job_id,
                        'title': title,
                        'link': href,
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'deadline': job_details.get('deadline', ''),
                        'source': 'Free Job Alert',
                        'categories': determine_categories(title),
                        'details': job_details
                    }
                    
                    jobs.append(job)
                    database.log_action(f"Found job: {title[:50]}...")
                    
            except Exception as e:
                database.log_error(f"Error parsing Free Job Alert link: {str(e)}")
                continue
        
        database.log_action(f"Free Job Alert scraping completed: {len(jobs)} jobs found")
        
        time.sleep(config.REQUEST_DELAY_SECONDS)
        
        return jobs
        
    except Exception as e:
        database.log_error(f"Error in scrape_free_job_alert: {str(e)}")
        return get_cached_jobs("free_job_alert")

def scrape_employment_news():
    """
    Scrape job listings from Employment News website
    
    Returns:
        list: List of job dictionaries
    """
    try:
        database.log_action("Starting Employment News scraping")
        
        url = "https://www.employmentnews.gov.in"
        response = make_request(url)
        
        if not response:
            database.log_error("Failed to fetch Employment News main page")
            return get_cached_jobs("employment_news")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # Look for job listings
        job_items = soup.find_all(['div', 'article'], class_=['job', 'vacancy', 'post'])
        
        if not job_items:
            job_items = soup.find_all('a', href=True)
        
        for item in job_items[:25]:
            try:
                if hasattr(item, 'find'):
                    title_elem = item.find(['h2', 'h3', 'h4']) or item
                    title = title_elem.get_text(strip=True)
                else:
                    title = item.get_text(strip=True)
                
                if hasattr(item, 'get'):
                    link = item.get('href', '')
                else:
                    link = item
                
                # Filter for job postings
                if (title and 
                    link and 
                    any(keyword in title.lower() for keyword in ['vacancy', 'recruitment', 'application', 'job', 'post']) and
                    len(title) > 15):
                    
                    # Get full URL
                    if link and not link.startswith('http'):
                        link = url + link
                    
                    # Scrape details
                    job_details = scrape_job_details(link)
                    
                    job_id = generate_job_id(title, link)
                    
                    if database.check_job_posted(job_id):
                        continue
                    
                    job = {
                        'job_id': job_id,
                        'title': title,
                        'link': link,
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'deadline': job_details.get('deadline', ''),
                        'source': 'Employment News',
                        'categories': determine_categories(title),
                        'details': job_details
                    }
                    
                    jobs.append(job)
                    database.log_action(f"Found job: {title[:50]}...")
                    
            except Exception as e:
                database.log_error(f"Error parsing Employment News item: {str(e)}")
                continue
        
        database.log_action(f"Employment News scraping completed: {len(jobs)} jobs found")
        
        time.sleep(config.REQUEST_DELAY_SECONDS)
        
        return jobs
        
    except Exception as e:
        database.log_error(f"Error in scrape_employment_news: {str(e)}")
        return get_cached_jobs("employment_news")

def determine_categories(title):
    """
    Determine job categories based on title
    
    Args:
        title (str): Job title
        
    Returns:
        list: List of relevant categories
    """
    title_lower = title.lower()
    categories = []
    
    category_keywords = {
        'Bank Jobs': ['bank', 'ibps', 'sbi', 'rbi', 'banker', 'po', 'clerk'],
        'Railway Jobs': ['railway', 'rpf', 'rrb', 'rail'],
        'SSC Jobs': ['ssc', 'cgl', 'chsl', 'mts', 'gd'],
        'UPSC Jobs': ['upsc', 'ias', 'ips', 'ifs', 'civil service'],
        'Police Jobs': ['police', 'constable', 'si', 'bharti', 'defense'],
        'Teaching Jobs': ['teacher', 'lecturer', 'professor', 'school', 'education', 'tgt', 'pgt'],
        'Engineering Jobs': ['engineer', 'je', 'ae', 'engineering', 'technical', 'civil', 'mechanical'],
        'Medical Jobs': ['doctor', 'medical', 'nurse', 'hospital', 'health', 'mbbs', 'bds'],
        'Defense Jobs': ['army', 'navy', 'air force', 'military', 'defence'],
        '10th Pass Jobs': ['10th', 'matric', 'high school', 'secondary'],
        '12th Pass Jobs': ['12th', 'intermediate', 'hsc', 'higher secondary'],
        'Graduate Jobs': ['graduate', 'graduation', 'bachelor', 'b.a.', 'b.com', 'b.sc'],
        'Diploma Jobs': ['diploma', 'polytechnic'],
        'ITI Jobs': ['iti', 'vocational']
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in title_lower for keyword in keywords):
            categories.append(category)
    
    if not categories:
        categories.append('Sarkari Naukri')
    
    return categories

def get_cached_jobs(source):
    """
    Get previously cached jobs when scraping fails
    
    Args:
        source (str): Source website name
        
    Returns:
        list: List of cached jobs from the source
    """
    try:
        all_jobs = database.load_posted_jobs()
        cached = [job for job in all_jobs.values() if job.get('source') == source]
        
        if cached:
            database.log_action(f"Using {len(cached)} cached jobs from {source}")
            return cached[-5:]  # Return last 5 jobs
        
        return []
    except Exception as e:
        database.log_error(f"Error getting cached jobs: {str(e)}")
        return []

def scrape_all_websites():
    """
    Scrape all configured websites
    
    Returns:
        list: Combined list of jobs from all sources
    """
    all_jobs = []
    
    # Scrape each active website
    if config.WEBSITES_TO_MONITOR.get('sarkari_result', {}).get('active'):
        try:
            jobs = scrape_sarkari_result()
            all_jobs.extend(jobs)
        except Exception as e:
            database.log_error(f"Sarkari Result scraping failed: {str(e)}")
    
    if config.WEBSITES_TO_MONITOR.get('free_job_alert', {}).get('active'):
        try:
            jobs = scrape_free_job_alert()
            all_jobs.extend(jobs)
        except Exception as e:
            database.log_error(f"Free Job Alert scraping failed: {str(e)}")
    
    if config.WEBSITES_TO_MONITOR.get('employment_news', {}).get('active'):
        try:
            jobs = scrape_employment_news()
            all_jobs.extend(jobs)
        except Exception as e:
            database.log_error(f"Employment News scraping failed: {str(e)}")
    
    database.log_action(f"Total jobs scraped from all websites: {len(all_jobs)}")
    return all_jobs

def scrape_by_state(state_code):
    """
    Scrape jobs for a specific state
    
    Args:
        state_code (str): State code (e.g., 'up', 'bihar')
        
    Returns:
        list: List of jobs for the state
    """
    try:
        state_info = config.STATE_WEBSITES.get(state_code)
        if not state_info:
            database.log_error(f"Invalid state code: {state_code}")
            return []
        
        jobs = []
        for url in state_info.get('websites', []):
            try:
                database.log_action(f"Scraping state website: {url}")
                response = make_request(url)
                
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for job links
                    job_links = soup.find_all('a', href=True)
                    
                    for link in job_links[:15]:
                        try:
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if (title and href and 
                                any(keyword in title.lower() for keyword in ['vacancy', 'recruitment', 'job', 'notification']) and
                                len(title) > 10):
                                
                                if not href.startswith('http'):
                                    href = url + href
                                
                                job_details = scrape_job_details(href)
                                job_id = generate_job_id(title, href)
                                
                                if not database.check_job_posted(job_id):
                                    job = {
                                        'job_id': job_id,
                                        'title': title,
                                        'link': href,
                                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                        'deadline': job_details.get('E', ''),
                                        'source': f"{state_info['name']} Government",
                                        'categories': determine_categories(title),
                                        'details': job_details
                                    }
                                    jobs.append(job)
                                    
                            except Exception as e:
                                continue
                                
                time.sleep(config.REQUEST_DELAY_SECONDS)
                
            except Exception as e:
                database.log_error(f"Error scraping {url}: {str(e)}")
                continue
        
        database.log_action(f"Found {len(jobs)} jobs for {state_info['name']}")
        return jobs
        
    except Exception as e:
        database.log_error(f"Error in scrape_by_state: {str(e)}")
        return []

# Main scraping function
def run_scheduled_scrape():
    """
    Run scheduled scraping and post new jobs
    Returns count of new jobs found
    """
    try:
        database.log_action("Starting scheduled scraping")
        jobs = scrape_all_websites()
        new_jobs = 0
        
        for job in jobs:
            # Add to database
            if database.add_posted_job(job):
                new_jobs += 1
                database.log_action(f"New job saved: {job['title'][:50]}...")
        
        database.log_action(f"Scheduled scraping completed: {new_jobs} new jobs")
        return new_jobs
        
    except Exception as e:
        database.log_error(f"Error in scheduled scraping: {str(e)}")
        return 0
