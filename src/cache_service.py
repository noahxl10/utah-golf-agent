from datetime import datetime, timedelta
from typing import List
from src.models import db, TeeTimeCache
from src._typing.structs import TeeTime
from sqlalchemy import func, Integer, or_, and_
from sqlalchemy.sql.expression import cast
import pytz
from src.util import misc


class TeeTimeCacheService:
    """Service class for managing tee time cache operations"""

    @staticmethod
    def cache_tee_times(tee_times: List[TeeTime], provider: str = None):
        """
        Cache a list of tee times and update availability flags.
        
        Args:
            tee_times: List of TeeTime objects to cache
            provider: Optional provider name to override individual tee time provider
        """
        if not tee_times:
            return

        current_time = datetime.utcnow()

        # Step 1: Mark all existing entries as potentially unavailable
        # We'll mark them back as available if they appear in the new data
        for tee_time in tee_times:
            course_name = tee_time.course_name
            date = tee_time.date

            # Mark all existing entries for this course and date as unavailable initially
            existing_entries = TeeTimeCache.query.filter_by(
                course_name=course_name, date=date).all()

            for entry in existing_entries:
                entry.is_available = False
                entry.updated_at = current_time

        # Step 2: Process new tee times
        for tee_time in tee_times:
            # Extract players_available - this might need to be calculated
            # For now, we'll use a default or extract from restrictions/other fields
            players_available = getattr(tee_time, 'max_num_players', None) or \
                               getattr(tee_time, 'available_spots', None) or \
                               4  # Default to 4 players if not specified

            # Check if this exact tee time already exists
            existing_entry = TeeTimeCache.query.filter_by(
                course_name=tee_time.course_name,
                date=tee_time.date,
                start_time=tee_time.start_time_unf,
                players_available=players_available).first()

            if existing_entry:
                # Update existing entry - mark as available and update info
                existing_entry.is_available = tee_time.is_available
                existing_entry.green_fee = tee_time.green_fee
                existing_entry.price = tee_time.price
                existing_entry.half_cart = getattr(tee_time, 'half_cart', None)
                existing_entry.subtotal = tee_time.subtotal
                existing_entry.restrictions = tee_time.restrictions
                existing_entry.special_offer = getattr(tee_time,
                                                       'special_offer', False)
                existing_entry.last_seen_at = current_time
                existing_entry.updated_at = current_time

            else:
                # Create new entry
                new_entry = TeeTimeCache(
                    course_name=tee_time.course_name,
                    date=tee_time.date,
                    start_time=tee_time.start_time_unf,
                    players_available=players_available,
                    holes=tee_time.holes,
                    booking_url=tee_time.booking_url,
                    provider=provider or tee_time.provider,
                    green_fee=tee_time.green_fee,
                    half_cart=getattr(tee_time, 'half_cart', None),
                    price=tee_time.price,
                    subtotal=tee_time.subtotal,
                    restrictions=tee_time.restrictions,
                    special_offer=getattr(tee_time, 'special_offer', False),
                    is_available=tee_time.is_available,
                    last_seen_at=current_time)
                db.session.add(new_entry)

        # Commit all changes
        db.session.commit()
        print(f"Cached {len(tee_times)} tee times successfully")

    @staticmethod
    def get_cached_tee_times(course_name: str = None,
                             available_only: bool = True) -> List[dict]:
        """
        Retrieve cached tee times with optional filters.
        
        Args:
            course_name: Filter by course name
            date: Filter by date (YYYY-MM-DD format)
            available_only: Only return available tee times
            
        Returns:
            List of tee time dictionaries
        """
        query = TeeTimeCache.query

        if course_name:
            query = query.filter_by(course_name=course_name)
        # if current_date:
        #     query = query.filter(TeeTimeCache.date >= current_date)
        # if current_time:
        # mountain time
        # if available_only:
        #     query = query.filter_by(is_available=True)

        current_date = misc.current_date()

        cur_time = datetime.now(pytz.timezone('America/Denver'))
        # For tee times on today's date, filter by current time
        # For future dates, include all times
        query = query.filter(
            or_(
                TeeTimeCache.date
                > current_date,  # Future dates - include all times
                and_(
                    TeeTimeCache.date == current_date,  # Today's date
                    TeeTimeCache.start_time
                    >= cur_time.strftime("%H:%M"),  # Time >= current time
                    TeeTimeCache.is_available)))

        results = query.order_by(TeeTimeCache.date.asc(),
                                 TeeTimeCache.start_time.asc()).all()

        if results:
            print(f"Found {len(results)} cached tee times")
        else:
            print("No cached tee times found")

        return [result.to_dict() for result in results]

    @staticmethod
    def get_all_cached_tee_times(available_only: bool = True) -> List[dict]:
        """Get all cached tee times"""
        return TeeTimeCacheService.get_cached_tee_times(
            available_only=available_only)

    @staticmethod
    def get_available_dates() -> List[str]:
        """
        Get distinct available dates from cached tee times, filtered for current date or later.
        
        Returns:
            List of date strings in YYYY-MM-DD format
        """
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')

        # Query for distinct dates where tee times are available and date is today or later
        distinct_dates = db.session.query(TeeTimeCache.date)\
            .filter(TeeTimeCache.is_available == True)\
            .filter(TeeTimeCache.date >= today)\
            .distinct()\
            .order_by(TeeTimeCache.date)\
            .all()

        # Extract date strings from the query result tuples
        date_list = [date_tuple[0] for date_tuple in distinct_dates]

        print(f"Found {len(date_list)} available dates: {date_list}")
        return date_list

    @staticmethod
    def cleanup_old_entries(days_old: int = 1):
        """Remove tee times older than specified days"""
        cutoff_date = datetime.utcnow().date()

        old_entries = TeeTimeCache.query.filter(
            TeeTimeCache.date < cutoff_date.strftime('%Y-%m-%d')).all()

        for entry in old_entries:
            db.session.delete(entry)

        db.session.commit()
        print(f"Cleaned up {len(old_entries)} old tee time entries")
