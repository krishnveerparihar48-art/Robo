import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from database.models import Base, Job, User, ProcessedSource
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.connect()
    
    def connect(self):
        """Initialize database connection"""
        try:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
            self.engine = create_engine(database_url)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"Connected to database: {database_url}")
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def initialize_database(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def add_job(self, job_data: dict) -> Job:
        """Add a new job to the database"""
        session = self.Session()
        try:
            # Check for duplicates
            existing_job = self.get_job_by_hash(job_data.get('url_hash'))
            if existing_job:
                logger.info(f"Job already exists (duplicate): {job_data.get('title')}")
                return existing_job
            
            job = Job(
                title=job_data['title'],
                category_a=job_data.get('category_a', ''),
                category_b=job_data.get('category_b', ''),
                details_c=job_data.get('details_c', ''),
                deadline_d=job_data.get('deadline_d', ''),
                apply_link_e=job_data['apply_link_e'],
                source_f=job_data['source_f'],
                image_g=job_data.get('image_g', ''),
                url_hash=job_data.get('url_hash', '')
            )
            
            if not job.url_hash:
                job.url_hash = job.generate_url_hash()
            
            session.add(job)
            session.commit()
            logger.info(f"Added new job: {job.title}")
            return job
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to add job: {e}")
            raise
        finally:
            session.close()
    
    def get_job_by_hash(self, url_hash: str) -> Job:
        """Get job by URL hash"""
        session = self.Session()
        try:
            return session.query(Job).filter_by(url_hash=url_hash).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get job by hash: {e}")
            raise
        finally:
            session.close()
    
    def get_recent_jobs(self, limit: int = 5) -> list[Job]:
        """Get most recent jobs"""
        session = self.Session()
        try:
            return session.query(Job).order_by(Job.posted_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get recent jobs: {e}")
            raise
        finally:
            session.close()
    
    def get_job_count(self) -> int:
        """Get total number of jobs in database"""
        session = self.Session()
        try:
            return session.query(Job).count()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get job count: {e}")
            raise
        finally:
            session.close()
    
    def add_user(self, user_id: int) -> User:
        """Add or update a user"""
        session = self.Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id)
                session.add(user)
            session.commit()
            logger.info(f"Added/updated user: {user_id}")
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to add user: {e}")
            raise
        finally:
            session.close()
    
    def verify_user(self, user_id: int) -> User:
        """Verify a user"""
        session = self.Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.verified = True
                user.verification_timestamp = datetime.utcnow()
                session.commit()
                logger.info(f"Verified user: {user_id}")
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to verify user: {e}")
            raise
        finally:
            session.close()
    
    def get_verified_users_count(self) -> int:
        """Get number of verified users"""
        session = self.Session()
        try:
            return session.query(User).filter_by(verified=True).count()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get verified users count: {e}")
            raise
        finally:
            session.close()
    
    def update_processed_source(self, source_url: str, job_count: int, status: str = 'success') -> ProcessedSource:
        """Update processed source information"""
        session = self.Session()
        try:
            source = session.query(ProcessedSource).filter_by(source_url=source_url).first()
            if not source:
                source = ProcessedSource(source_url=source_url)
                session.add(source)
            
            source.last_scraped = datetime.utcnow()
            source.job_count = job_count
            source.status = status
            session.commit()
            logger.info(f"Updated processed source: {source_url}")
            return source
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update processed source: {e}")
            raise
        finally:
            session.close()
    
    def get_last_scraped_time(self, source_url: str) -> datetime:
        """Get last scraped time for a source"""
        session = self.Session()
        try:
            source = session.query(ProcessedSource).filter_by(source_url=source_url).first()
            return source.last_scraped if source else None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get last scraped time: {e}")
            raise
        finally:
            session.close()

# Initialize database
db_manager = DatabaseManager()
db_manager.initialize_database()
