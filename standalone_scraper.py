#!/usr/bin/env python3
"""
Standalone scraper script that can run independently with direct database connection.
This allows running the scraper without Flask app context.
"""

import os
import sys
from datetime import date, datetime, timedelta
from typing import List, Optional
import argparse
import logging

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Disable request logging when running standalone to avoid Flask context errors
os.environ['STANDALONE_MODE'] = '1'

# Import scraper functions
from scraper import scraper

# Import database models and setup
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSON
import json

# Database connection setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query debugging
)

# Create session factory
Session = scoped_session(sessionmaker(bind=engine))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StandaloneCacheService:
    """Standalone cache service that works without Flask app context"""
    
    @staticmethod
    def cache_tee_times(tee_times: List, provider: str) -> int:
        """Cache tee times directly to database"""
        if not tee_times:
            return 0
            
        cached_count = 0
        
        # Process each tee time individually to avoid transaction issues
        for tee_time in tee_times:
            session = Session()
            try:
                # Convert TeeTime object to dict for database storage
                tee_time_dict = tee_time.dict() if hasattr(tee_time, 'dict') else tee_time
                
                # Convert lists and dicts to JSON strings for PostgreSQL
                holes_json = json.dumps(tee_time_dict.get('holes', [])) if tee_time_dict.get('holes') else '[]'
                restrictions_json = json.dumps(tee_time_dict.get('restrictions', [])) if tee_time_dict.get('restrictions') else '[]'
                raw_json_str = json.dumps(tee_time_dict.get('raw_json_response')) if tee_time_dict.get('raw_json_response') else None
                
                # Check if this tee time already exists
                existing_query = text("""
                    SELECT id FROM tee_time_cache 
                    WHERE course_name = :course_name 
                    AND date = :date 
                    AND start_time = :start_time
                    AND provider = :provider
                """)
                
                existing = session.execute(existing_query, {
                    'course_name': tee_time_dict.get('course_name'),
                    'date': tee_time_dict.get('date'),
                    'start_time': tee_time_dict.get('start_time_unf'),
                    'provider': provider
                }).fetchone()
                
                if existing:
                    # Update existing record
                    update_query = text("""
                        UPDATE tee_time_cache SET 
                            is_available = :is_available,
                            green_fee = :green_fee,
                            half_cart = :half_cart,
                            price = :price,
                            subtotal = :subtotal,
                            holes = :holes,
                            restrictions = :restrictions,
                            special_offer = :special_offer,
                            booking_url = :booking_url,
                            players_available = :players_available,
                            raw_json_response = :raw_json_response,
                            last_seen_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """)
                    
                    session.execute(update_query, {
                        'id': existing[0],
                        'is_available': tee_time_dict.get('is_available', True),
                        'green_fee': tee_time_dict.get('green_fee', 0),
                        'half_cart': tee_time_dict.get('half_cart', 0),
                        'price': tee_time_dict.get('price', 0),
                        'subtotal': tee_time_dict.get('subtotal', 0),
                        'holes': holes_json,
                        'restrictions': restrictions_json,
                        'special_offer': tee_time_dict.get('special_offer', False),
                        'booking_url': tee_time_dict.get('booking_url'),
                        'players_available': tee_time_dict.get('players_available', 4),
                        'raw_json_response': raw_json_str
                    })
                else:
                    # Insert new record
                    insert_query = text("""
                        INSERT INTO tee_time_cache (
                            course_name, date, start_time, provider,
                            is_available, green_fee, half_cart, price, subtotal,
                            holes, restrictions, special_offer, booking_url,
                            players_available, raw_json_response, created_at, 
                            last_seen_at, updated_at
                        ) VALUES (
                            :course_name, :date, :start_time, :provider,
                            :is_available, :green_fee, :half_cart, :price, :subtotal,
                            :holes, :restrictions, :special_offer, :booking_url,
                            :players_available, :raw_json_response, CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """)
                    
                    session.execute(insert_query, {
                        'course_name': tee_time_dict.get('course_name'),
                        'date': tee_time_dict.get('date'),
                        'start_time': tee_time_dict.get('start_time_unf'),
                        'provider': provider,
                        'is_available': tee_time_dict.get('is_available', True),
                        'green_fee': tee_time_dict.get('green_fee', 0),
                        'half_cart': tee_time_dict.get('half_cart', 0),
                        'price': tee_time_dict.get('price', 0),
                        'subtotal': tee_time_dict.get('subtotal', 0),
                        'holes': holes_json,
                        'restrictions': restrictions_json,
                        'special_offer': tee_time_dict.get('special_offer', False),
                        'booking_url': tee_time_dict.get('booking_url'),
                        'players_available': tee_time_dict.get('players_available', 4),
                        'raw_json_response': raw_json_str
                    })
                
                # Commit this individual tee time
                session.commit()
                cached_count += 1
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error caching tee time: {e}")
            finally:
                session.close()
        
        return cached_count


def run_chronogolf_scraper(target_date: str) -> int:
    """Run ChronoGolf scraper and cache results"""
    logger.info(f"Scraping ChronoGolf tee times for {target_date}")
    
    try:
        tee_times = scraper.chronogolf_tee_times(target_date)
        if tee_times:
            cached_count = StandaloneCacheService.cache_tee_times(tee_times, 'chronogolf')
            logger.info(f"Cached {cached_count} ChronoGolf tee times")
            return cached_count
        else:
            logger.warning("No ChronoGolf tee times found")
            return 0
    except Exception as e:
        logger.error(f"Error scraping ChronoGolf: {e}")
        return 0


def run_foreup_scraper(target_date: str) -> int:
    """Run ForeUp scraper and cache results"""
    logger.info(f"Scraping ForeUp tee times for {target_date}")
    
    try:
        tee_times = scraper.foreup_tee_times(target_date)
        if tee_times:
            cached_count = StandaloneCacheService.cache_tee_times(tee_times, 'foreup')
            logger.info(f"Cached {cached_count} ForeUp tee times")
            return cached_count
        else:
            logger.warning("No ForeUp tee times found")
            return 0
    except Exception as e:
        logger.error(f"Error scraping ForeUp: {e}")
        return 0


def run_eaglewood_scraper(target_date: str) -> int:
    """Run Eaglewood scraper and cache results"""
    logger.info(f"Scraping Eaglewood tee times for {target_date}")
    
    try:
        tee_times = scraper.eaglewood_tee_times(target_date)
        if tee_times:
            cached_count = StandaloneCacheService.cache_tee_times(tee_times, 'eaglewood')
            logger.info(f"Cached {cached_count} Eaglewood tee times")
            return cached_count
        else:
            logger.warning("No Eaglewood tee times found")
            return 0
    except Exception as e:
        logger.error(f"Error scraping Eaglewood: {e}")
        return 0


def run_all_scrapers(target_date: str) -> dict:
    """Run all scrapers and return results"""
    logger.info(f"Starting scraper run for {target_date}")
    
    results = {
        'chronogolf': run_chronogolf_scraper(target_date),
        'foreup': run_foreup_scraper(target_date),
        'eaglewood': run_eaglewood_scraper(target_date)
    }
    
    total_cached = sum(results.values())
    logger.info(f"Scraper run completed. Total tee times cached: {total_cached}")
    logger.info(f"Results: {results}")
    
    return results


def test_database_connection():
    """Test the database connection"""
    try:
        session = Session()
        result = session.execute(text("SELECT 1")).fetchone()
        Session.remove()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Standalone Golf Tee Time Scraper')
    parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD). Defaults to today.')
    parser.add_argument('--days-ahead', type=int, default=0, 
                       help='Number of days ahead from today to scrape (default: 0)')
    parser.add_argument('--provider', choices=['chronogolf', 'foreup', 'eaglewood', 'all'],
                       default='all', help='Which provider to scrape (default: all)')
    parser.add_argument('--test-db', action='store_true', 
                       help='Test database connection and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Test database connection if requested
    if args.test_db:
        success = test_database_connection()
        sys.exit(0 if success else 1)
    
    # Determine target date
    if args.date:
        target_date = args.date
        # Validate date format
        try:
            datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        base_date = datetime.now().date()
        target_date = (base_date + timedelta(days=args.days_ahead)).strftime('%Y-%m-%d')
    
    logger.info(f"Target date: {target_date}")
    
    # Test database connection first
    if not test_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    # Run scraper(s)
    try:
        if args.provider == 'all':
            results = run_all_scrapers(target_date)
            total = sum(results.values())
            print(f"\n✅ Scraping completed successfully!")
            print(f"📊 Results: {results}")
            print(f"🎯 Total tee times cached: {total}")
            
        elif args.provider == 'chronogolf':
            count = run_chronogolf_scraper(target_date)
            print(f"\n✅ ChronoGolf scraping completed! Cached {count} tee times")
            
        elif args.provider == 'foreup':
            count = run_foreup_scraper(target_date)
            print(f"\n✅ ForeUp scraping completed! Cached {count} tee times")
            
        elif args.provider == 'eaglewood':
            count = run_eaglewood_scraper(target_date)
            print(f"\n✅ Eaglewood scraping completed! Cached {count} tee times")
            
    except KeyboardInterrupt:
        logger.info("Scraper interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()