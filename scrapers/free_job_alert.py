from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

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

class FreeJobAlertScraper(BaseScraper):
    """Scraper for FreeJobAlert.com"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.selectors = config.get('selectors', {})
    
    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """Parse jobs from FreeJobAlert HTML"""
        jobs = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job list items
            job_list_selector = self.selectors.get('job_list', '.post.hentry')
            job_items = soup.select(job_list_selector)
            
            if not job_items:
                logger.warning("No job items found on FreeJobAlert")
                return jobs
            
            for item in job_items:
                try:
                    # Extract title
                    title_selector = self.selectors.get('title', 'h2.entry-title a')
                    title_element = item.select_one(title_selector)
                    title = title_element.get_text(strip=True) if title_element else "No Title"
                    
                    # Extract link
                    link_selector = self.selectors.get('link', 'a')
                    link_element = item.select_one(link_selector)
                    link = link_element['href'] if link_element and link_element.get('href') else ""
                    
                    # Make absolute URL
                    link = self.make_absolute_url(link)
                    
                    # Create job dictionary
                    job = {
                        'title': title,
                        'category_a': 'Government',
                        'category_b': 'FreeJobAlert',
                        'details_c': '',  # Details would require visiting the job page
                        'deadline_d': '',  # Deadline would require visiting the job page
                        'apply_link_e': link,
                        'source_f': 'FreeJobAlert.com',
                        'image_g': ''     # Image would require visiting the job page
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Failed to parse job item: {e}")
                    continue
            
            logger.info(f"Parsed {len(jobs)} jobs from FreeJobAlert")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to parse FreeJobAlert HTML: {e}")
            return []
