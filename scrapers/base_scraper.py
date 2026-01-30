import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import random
import logging
from urllib.parse import urljoin
from database.models import Job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaseScraper:
    """Base class for all web scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('url', '')
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        ]
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def fetch_page(self, url: str, retry: int = 0) -> str:
        """Fetch webpage with retry logic"""
        max_retries = self.config.get('max_retries', 3)
        delay = self.config.get('delay', 5)
        
        if retry >= max_retries:
            logger.error(f"Max retries reached for {url}")
            return ""
        
        try:
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            
            logger.info(f"Fetching {url} (attempt {retry + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                time.sleep(delay)  # Respect rate limiting
                return response.text
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                time.sleep(delay * 2)  # Longer delay before retry
                return self.fetch_page(url, retry + 1)
                
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            time.sleep(delay * 2)
            return self.fetch_page(url, retry + 1)
    
    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """Parse jobs from HTML (to be implemented by child classes)"""
        raise NotImplementedError("parse_jobs method must be implemented by child class")
    
    def scrape(self) -> List[Job]:
        """Main scraping method"""
        try:
            html = self.fetch_page(self.base_url)
            if not html:
                logger.error(f"Failed to fetch {self.base_url}")
                return []
            
            raw_jobs = self.parse_jobs(html)
            jobs = []
            
            for raw_job in raw_jobs:
                try:
                    job = Job(
                        title=raw_job.get('title', ''),
                        category_a=raw_job.get('category_a', ''),
                        category_b=raw_job.get('category_b', ''),
                        details_c=raw_job.get('details_c', ''),
                        deadline_d=raw_job.get('deadline_d', ''),
                        apply_link_e=raw_job.get('apply_link_e', ''),
                        source_f=self.config.get('name', 'unknown'),
                        image_g=raw_job.get('image_g', ''),
                    )
                    
                    # Generate URL hash
                    if job.title and job.apply_link_e:
                        job.url_hash = job.generate_url_hash()
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Failed to create job from raw data: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from {self.base_url}")
            return jobs
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []
    
    def make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if not url:
            return ""
        
        if url.startswith('http'):
            return url
        
        return urljoin(self.base_url, url)
