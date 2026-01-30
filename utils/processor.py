import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobProcessor:
    """Process and validate job data"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.strip().split())
        # Remove special characters except basic punctuation
        text = re.sub(r'[^\w\s.,;:!?\-\(\)\[\]\{\}]', '', text)
        return text
    
    @staticmethod
    def normalize_date(date_str: str) -> str:
        """Standardize date format"""
        if not date_str:
            return ""
        
        # Try to parse common date formats
        date_str = date_str.strip()
        
        # Remove ordinal suffixes (e.g., 1st, 2nd, 3rd, 4th)
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str, flags=re.IGNORECASE)
        
        # Convert to standard format if possible
        try:
            # Try parsing with common formats
            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%d %b %Y', '%d %B %Y', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%d-%m-%Y')
                except ValueError:
                    continue
        except Exception as e:
            logger.warning(f"Date normalization failed for '{date_str}': {e}")
        
        return date_str
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    @staticmethod
    def check_url_status(url: str, timeout: int = 10) -> bool:
        """Check if URL returns 200 status"""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"URL check failed for {url}: {e}")
            return False
    
    @staticmethod
    def extract_image_from_html(html: str) -> Optional[str]:
        """Extract image URL from HTML content"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img['src']
                if JobProcessor.validate_url(src):
                    return src
                
                # Try to make absolute URL if relative
                if src.startswith('/'):
                    # This would need a base URL, but we don't have it here
                    continue
            
            return None
        except Exception as e:
            logger.warning(f"Image extraction failed: {e}")
            return None
    
    @staticmethod
    def generate_url_hash(title: str, url: str) -> str:
        """Generate hash for duplicate detection"""
        hash_input = f"{title}{url}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()
    
    @staticmethod
    def is_job_expired(deadline: str) -> bool:
        """Check if job deadline has passed"""
        if not deadline:
            return False
        
        try:
            # Try to parse the deadline
            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%d %b %Y', '%d %B %Y', '%Y-%m-%d']:
                try:
                    deadline_date = datetime.strptime(deadline, fmt)
                    return deadline_date.date() < datetime.now().date()
                except ValueError:
                    continue
            
            # If we can't parse, assume it's not expired
            return False
        except Exception as e:
            logger.warning(f"Failed to check job expiration: {e}")
            return False
    
    @staticmethod
    def process_job_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw job data and normalize all fields"""
        processed = {
            'title': JobProcessor.normalize_text(raw_data.get('title', '')),
            'category_a': JobProcessor.normalize_text(raw_data.get('category_a', '')),
            'category_b': JobProcessor.normalize_text(raw_data.get('category_b', '')),
            'details_c': JobProcessor.normalize_text(raw_data.get('details_c', '')),
            'deadline_d': JobProcessor.normalize_date(raw_data.get('deadline_d', '')),
            'apply_link_e': raw_data.get('apply_link_e', ''),
            'source_f': raw_data.get('source_f', ''),
            'image_g': raw_data.get('image_g', ''),
        }
        
        # Generate URL hash for duplicate detection
        if processed['title'] and processed['apply_link_e']:
            processed['url_hash'] = JobProcessor.generate_url_hash(
                processed['title'], 
                processed['apply_link_e']
            )
        
        return processed
    
    @staticmethod
    def is_duplicate(job_data: Dict[str, Any], existing_hashes: set) -> bool:
        """Check if job is a duplicate"""
        if not job_data.get('url_hash'):
            return False
        
        return job_data['url_hash'] in existing_hashes
