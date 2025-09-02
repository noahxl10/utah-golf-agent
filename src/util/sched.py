import inspect
import logging
from flask import Flask
from datetime import datetime, timedelta

from src.scraper import scraper
from src.cache_service import TeeTimeCacheService
from src.util import misc
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging for scheduled jobs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScheduledJobs:

    def __init__(self, app: Flask = None):
        self.app = app


    def test_job(self):
        print("TEST JOB RAN")


    def run_get_all_tee_times(self, days_offset=0):
        """Scheduled job to scrape and cache tee times from all providers"""
        job_name = f"run_get_all_tee_times_+{days_offset}_days"
        logger.info(f"Starting scheduled job: {job_name}")

        # Use Flask app context if provided
        def _execute_job():
            try:
                # Calculate target date based on offset
                base_date = datetime.now().date()
                target_date = base_date + timedelta(days=days_offset)
                target_date_str = target_date.strftime('%Y-%m-%d')

                logger.info(f"Scraping tee times for date: {target_date_str} (offset: +{days_offset} days)")

                # Scrape ChronoGolf
                c_tee_times = scraper.chronogolf_tee_times(target_date_str)
                if c_tee_times:
                    TeeTimeCacheService.cache_tee_times(c_tee_times, 'chronogolf')
                    logger.info(f"Cached {len(c_tee_times)} ChronoGolf tee times")
                else:
                    logger.warning("No ChronoGolf tee times found")

                # Scrape ForeUp
                f_tee_times = scraper.foreup_tee_times(target_date_str)
                if f_tee_times:
                    TeeTimeCacheService.cache_tee_times(f_tee_times, 'foreup')
                    logger.info(f"Cached {len(f_tee_times)} ForeUp tee times")
                else:
                    logger.warning("No ForeUp tee times found")

                # Scrape Eaglewood
                e_tee_times = scraper.eaglewood_tee_times(target_date_str)
                if e_tee_times:
                    TeeTimeCacheService.cache_tee_times(e_tee_times, 'eaglewood')
                    logger.info(f"Cached {len(e_tee_times)} Eaglewood tee times")
                else:
                    logger.warning("No Eaglewood tee times found")

                total_tee_times = len(c_tee_times or []) + len(f_tee_times or []) + len(e_tee_times or [])
                logger.info(f"Job {job_name} completed successfully. Total tee times: {total_tee_times}")
                return True

            except Exception as e:
                logger.error(f"Job {job_name} failed with error: {str(e)}", exc_info=True)
                return False

        # Execute with or without Flask context
        if self.app:
            with self.app.app_context():
                return _execute_job()
        else:
            return _execute_job()


def add_jobs(scheduler: BackgroundScheduler, app: Flask = None) -> BackgroundScheduler:
    """Add scheduled jobs to the scheduler with explicit registration"""

    try:
        sj = ScheduledJobs(app)

        # Explicitly register jobs instead of auto-discovery
        # This prevents accidentally scheduling unwanted methods
        jobs_to_register = [
            {
                'func': sj.test_job,
                'trigger': 'interval',
                'hours': 1,
                'id': 'test',
                'name': 'test_run',
                'replace_existing': True,  # Handle conflicts gracefully
                'max_instances': 1,  # Prevent overlapping executions
                'start_date': datetime.now() + timedelta(seconds=10),  # Start immediately
                # 'start_date': datetime.now(),  # Start immediately
            },
            # CURRENT DAY RUN
            {
                'func': lambda: sj.run_get_all_tee_times(days_offset=0),
                'trigger': 'interval',
                'hours': 3,
                'id': 'run_tee_times_TODAY',
                'name': 'scrape_cache_tee_times_TODAY',
                'replace_existing': True,
                'max_instances': 1,  # Prevent overlapping executions
            },
             # CURRENT DAY + 1 DAY (E.G. TOMORROW)
            {
                'func': lambda: sj.run_get_all_tee_times(days_offset=1),
                'trigger': 'interval',
                'hours': 12,
                'id': 'run_tee_times_TOMORROW',
                'name': 'scrape_cache_tee_times_TOMORROW',
                'replace_existing': True,
                'max_instances': 1,  # Prevent overlapping executions
            },
             # CURRENT DATE + 2 DAYS (E.G. DAY AFTER TOMORROW)
            {
                'func': lambda: sj.run_get_all_tee_times(days_offset=2),
                'trigger': 'interval',
                'hours': 24,
                'id': 'run_tee_times_DAY_AFTER_TOMORROW',
                'name': 'scrape_cache_tee_times_DAY_AFTER_TOMORROW',
                'replace_existing': True,
                'max_instances': 1,  # Prevent overlapping executions
            }
        ]

        # Register each job
        for job_config in jobs_to_register:
            try:
                scheduler.add_job(**job_config)
                logger.info(f"✓ Added job: {job_config['name']} (ID: {job_config['id']})")
            except Exception as job_error:
                logger.error(f"✗ Failed to add job {job_config['id']}: {job_error}")

        logger.info(f"Successfully registered {len(jobs_to_register)} scheduled jobs")

    except Exception as e:
        logger.error(f"Failed to add jobs to scheduler: {e}")
        raise  # Re-raise so caller can handle appropriately

    return scheduler
