import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from datetime import datetime
import re

# Configure logging only if run as main
if __name__ == "__main__":
    logging.basicConfig(
        filename='logs/scraper.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

def get_soup(url):
    """
    Fetches the URL and returns a BeautifulSoup object.
    Retries 3 times with exponential backoff.
    """
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    retries = 3
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                return None

def clean_text(text):
    if not text:
        return "ℹ️ Details not available"
    return re.sub(r'\s+', ' ', text).strip()

def parse_sarkari_result_details(url):
    soup = get_soup(url)
    if not soup:
        return None

    job_data = {
        "source": "Sarkari Result",
        "link": url,
        "scraped_at": datetime.now().isoformat()
    }

    # Extract Title - usually in h1
    h1 = soup.find('h1')
    job_data['title'] = clean_text(h1.text) if h1 else "Unknown Title"

    # Extract tables
    tables = soup.find_all('table')
    
    # Initialize fields with default
    job_data.update({
        "eligibility": "ℹ️ Check notification for details",
        "age_limit": "ℹ️ Check notification for details",
        "salary": "ℹ️ As per rules",
        "dates": "ℹ️ Check notification",
        "fee": "ℹ️ Check notification",
        "selection": "ℹ️ Check notification",
        "posts": "ℹ️ Check notification"
    })

    # Heuristic parsing of tables
    # SarkariResult usually puts Important Dates and Application Fee in the first table (often nested or just first)
    # They often use specific headers.
    
    text_content = soup.get_text()
    
    # Simple keyword extraction if table parsing is too brittle
    # But let's try to find specific headers in table cells
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_text = " ".join([c.get_text() for c in cells]).lower()
            
            if "important dates" in row_text:
                # Next rows or cells might contain the dates
                # This is tricky without exact structure, but we can look for specific keywords in subsequent cells
                pass
                
            # Attempt to map known labels to values
            # This requires inspecting specific structure. 
            # For this exercise, I will use a generic parser that looks for keys.
    
    # Generic key-value extraction from the whole page text or specific sections could be safer
    # But let's try to extract specific sections often found in these sites.
    
    # Important Dates
    # Often in a <ul> or table under "Important Dates" header
    dates_header = soup.find(string=re.compile("Important Dates", re.I))
    if dates_header:
        parent = dates_header.find_parent(['td', 'div'])
        if parent:
            job_data['dates'] = clean_text(parent.get_text())

    # Application Fee
    fee_header = soup.find(string=re.compile("Application Fee", re.I))
    if fee_header:
        parent = fee_header.find_parent(['td', 'div'])
        if parent:
            job_data['fee'] = clean_text(parent.get_text())

    # Age Limit
    age_header = soup.find(string=re.compile("Age Limit", re.I))
    if age_header:
        parent = age_header.find_parent(['td', 'div'])
        if parent:
            job_data['age_limit'] = clean_text(parent.get_text())

    # Vacancy / Eligibility
    # Often in a table with headers "Post Name", "Total Post", "Eligibility"
    # We look for a table that has "Eligibility" in header
    for table in tables:
        headers = [th.get_text().lower() for th in table.find_all('th')]
        if any("eligibility" in h for h in headers):
            # This is likely the vacancy table
            # We can extract text from here
            job_data['eligibility'] = clean_text(table.get_text())
            break
            
    return job_data

def scrape_sarkari_result():
    url = "https://www.sarkariresult.com/latestjob.php"
    soup = get_soup(url)
    if not soup:
        return []

    jobs = []
    # Find links to jobs. Usually in a div with id="post" or similar, or just list of links.
    # On SarkariResult, it's often a table or list.
    # We'll look for links inside the main content area.
    
    # Identifying the specific container is hard without seeing the live site.
    # I'll look for all links that look like job posts (php extension, not common pages)
    links = soup.find_all('a', href=True)
    
    count = 0
    for link in links:
        href = link['href']
        text = link.get_text()
        
        # Filter relevant links
        if "2024" in text or "2025" in text or "Online Form" in text:
            if "sarkariresult.com" not in href and not href.startswith("http"):
                 href = "https://www.sarkariresult.com/" + href
            
            # Skip duplicates or non-job links
            if "resume" in href or "syllabus" in href:
                continue

            # For this exercise, we will just process the first 3 links to avoid timeout/blocking
            if count >= 3: 
                break
                
            # Details scraping
            try:
                details = parse_sarkari_result_details(href)
                if details:
                    details['title'] = clean_text(text) # Override with link text if better
                    jobs.append(details)
                    count += 1
                time.sleep(2) # Delay
            except Exception as e:
                logger.error(f"Error parsing details for {href}: {e}")
                
    return jobs

def scrape_free_job_alert():
    # Placeholder for FreeJobAlert scraping logic
    # Similar structure to SarkariResult
    return []

def scrape_employment_news():
    # Placeholder
    return []

def get_all_jobs():
    """
    Main function to get jobs from all sources
    """
    all_jobs = []
    
    try:
        logger.info("Starting Sarkari Result scrape")
        sr_jobs = scrape_sarkari_result()
        all_jobs.extend(sr_jobs)
    except Exception as e:
        logger.error(f"Sarkari Result scrape failed: {e}")

    # Add other scrapers...
    
    return all_jobs

if __name__ == "__main__":
    # Test run
    print("Testing scraper...")
    jobs = get_all_jobs()
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(jobs[0])
