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


    def run_get_all_tee_times(self):
        """Scheduled job to scrape and cache tee times from all providers"""
        job_name = "run_get_all_tee_times"
        logger.info(f"Starting scheduled job: {job_name}")

        # Use Flask app context if provided
        def _execute_job():
            try:
                current_date = misc.current_date()
                logger.info(f"Scraping tee times for date: {current_date}")

                # Scrape ChronoGolf
                c_tee_times = scraper.chronogolf_tee_times(current_date)
                if c_tee_times:
                    TeeTimeCacheService.cache_tee_times(c_tee_times, 'chronogolf')
                    logger.info(f"Cached {len(c_tee_times)} ChronoGolf tee times")
                else:
                    logger.warning("No ChronoGolf tee times found")

                # Scrape ForeUp
                f_tee_times = scraper.foreup_tee_times(current_date)
                if f_tee_times:
                    TeeTimeCacheService.cache_tee_times(f_tee_times, 'foreup')
                    logger.info(f"Cached {len(f_tee_times)} ForeUp tee times")
                else:
                    logger.warning("No ForeUp tee times found")

                # Scrape Eaglewood
                e_tee_times = scraper.eaglewood_tee_times(current_date)
                if e_tee_times:
                    TeeTimeCacheService.cache_tee_times(e_tee_times, 'eaglewood')
                    logger.info(f"Cached {len(e_tee_times)} Eaglewood tee times")
                else:
                    logger.warning("No Eaglewood tee times found")

                total_tee_times = len(c_tee_times or []) + len(f_tee_times or [])
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
            # Add more jobs here as needed:
            {
                'func': sj.run_get_all_tee_times,
                'trigger': 'interval',
                'hours': 12,
                'id': 'run_tee_times',
                'name': 'scrape_cache_tee_times',
                'replace_existing': True,
                'max_instances': 1,  # Prevent overlapping executions
                'start_date': datetime.now() + timedelta(minutes=5),  # Start immediately
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
