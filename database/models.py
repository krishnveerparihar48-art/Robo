from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()

class Job(Base):
    """Model for storing government job postings"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    category_a = Column(String(200))
    category_b = Column(String(200))
    details_c = Column(Text)
    deadline_d = Column(String(100))
    apply_link_e = Column(String(500), nullable=False)
    source_f = Column(String(200), nullable=False)
    image_g = Column(String(500))
    posted_at = Column(DateTime, default=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    url_hash = Column(String(64), unique=True, index=True)
    
    def __repr__(self):
        return f"<Job(title='{self.title}', source='{self.source_f}')>"
    
    def generate_url_hash(self):
        """Generate hash from title and apply link for duplicate detection"""
        hash_input = f"{self.title}{self.apply_link_e}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

class User(Base):
    """Model for storing Telegram users"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    verified = Column(Boolean, default=False)
    verification_timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, verified={self.verified})>"

class ProcessedSource(Base):
    """Model for tracking scraped sources"""
    __tablename__ = 'processed_sources'
    
    id = Column(Integer, primary_key=True)
    source_url = Column(String(500), unique=True, nullable=False)
    last_scraped = Column(DateTime)
    job_count = Column(Integer, default=0)
    status = Column(String(50), default='success')
    
    def __repr__(self):
        return f"<ProcessedSource(source_url='{self.source_url}', last_scraped={self.last_scraped})>"
