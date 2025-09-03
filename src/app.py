from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, date as dt_date
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time 

from src.config import courses
from src.scraper import scraper
from src import test
from src.models import db, init_db, CourseRequest, BugReport
from src.cache_service import TeeTimeCacheService
from src.util import (
    sched,
    traffic,
)

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
app.config['DEBUG'] = True

# Initialize database
init_db(app)


 # Initialize vars for caching
cache_tee_time_data = None
cache_tee_time_time = 0
CACHE_TTL = 30 * 60  # 30 minutes in seconds


def fetch_tee_times_from_db():
    # Replace with your actual DB query
    return TeeTimeCacheService.get_cached_tee_times(
        available_only=True
    )


# Initialize scheduler (only in main process)
# import os
# if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
try:
    scheduler = BackgroundScheduler(timezone='UTC')
    scheduler = sched.add_jobs(scheduler, app)  # Pass Flask app for context
    scheduler.start()
    print("✓ Scheduler started successfully")

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown() if scheduler else None)
except Exception as e:
    print(f"✗ Failed to start scheduler: {e}")
    import traceback
    print(traceback.format_exc())
    # Continue running without scheduler rather than crashing
    scheduler = None
# else:
#     print("Skipping scheduler initialization in reloader process")
#     scheduler = None


@app.route('/')
@traffic.rate_limit()
def index():
    return jsonify({
        "message": "Utah Golf Booking API",
        "endpoints": {
            "/api/teetimes": "Get ChronoGolf tee times",
            "/api/foreup_teetimes": "Get ForeUp tee times", 
            "/api/eaglewood_teetimes": "Get Eaglewood tee times",
            "/test_api/teetimes": "Get mock tee times for testing",
            "/api/cached_teetimes": "Get all cached tee times",
            "/api/cached_teetimes/<course_name>": "Get cached tee times for specific course",
            "/api/available_dates": "Get distinct available dates from cached tee times",
            "/api/course_requests": "Submit (POST) or get (GET) course requests",
            "/api/course_requests/<id>/mark_added": "Mark course request as added (PATCH)",
            "/api/file_a_bug": "Submit bug reports (POST)"
        }
    })


# @app.route('/api/eaglewood_teetimes', methods=['GET'])
# def get_eaglewood_tee_times():
#     date = request.args.get('date')
#     tee_times = scraper.eaglewood_tee_times(date)

#     # Cache the tee times
#     if tee_times:
#         TeeTimeCacheService.cache_tee_times(tee_times, 'eaglewood')

#     data_to_return = [tee_time.model_dump() for tee_time in tee_times]
#     return jsonify(data_to_return)


# @app.route('/api/foreup_teetimes', methods=['GET'])
# def get_foreup_tee_times():
#     date = request.args.get('date')
#     tee_times = scraper.foreup_tee_times(date)

#     # Cache the tee times
#     if tee_times:
#         TeeTimeCacheService.cache_tee_times(tee_times, 'foreup')

#     data_to_return = [tee_time.model_dump() for tee_time in tee_times]
#     return jsonify(data_to_return)


# @app.route('/api/chronogolf_teetimes', methods=['GET'])
# def get_chronogolf_tee_times():
#     date = "2025-09-01"
#     tee_times = scraper.chronogolf_tee_times(date)
#     # print(tee_times[0])
#     data_to_return = [tee_time.model_dump() for tee_time in tee_times]

#     return jsonify(data_to_return)


# @app.route('/api/teetimes', methods=['GET'])
# def get_all_tee_times():
#     date = request.args.get('date')

#     c_tee_times = scraper.chronogolf_tee_times(date)
#     # Cache the tee times
#     if c_tee_times:
#         TeeTimeCacheService.cache_tee_times(c_tee_times, 'chronogolf')

#     f_tee_times = scraper.foreup_tee_times(date)
#     # Cache the tee times
#     if f_tee_times:
#         TeeTimeCacheService.cache_tee_times(f_tee_times, 'foreup')

#     e_tee_times = scraper.eaglewood_tee_times(date)
#     # Cache the tee times
#     if e_tee_times:
#         TeeTimeCacheService.cache_tee_times(e_tee_times, 'eaglewood')

#     c_tee_times.extend(f_tee_times)
#     c_tee_times.extend(e_tee_times)

#     data_to_return = [tee_time.model_dump() for tee_time in c_tee_times]
#     return jsonify(data_to_return)


@app.route('/test_api/teetimes', methods=['GET'])
@traffic.rate_limit()
def test_get_all_tee_times():
    """
    This endpoint fetches a list of TeeTime objects and returns them as a JSON array.
    """

    tee_times_list = test.get_mock_tee_times()

    data_to_return = [tee_time.model_dump() for tee_time in tee_times_list]
    response = jsonify(data_to_return)

    return response


@app.route("/api/courses", methods=['GET'])
@traffic.rate_limit()
def get_course_list():
    course_list = [course for course in courses]
    response = jsonify(course_list)
    return response


@app.route('/api/cached_teetimes', methods=['GET'])
@traffic.rate_limit()
def get_all_cached_tee_times():
    """Get all cached tee times"""
    # date = request.args.get('date')

    # date = misc.current_date()
    
    # available_only = request.args.get('available_only', 'true').lower() == 'true'

    global cached_tee_time_data, cache_tee_time_time
    now = time.time()

    if cached_tee_time_data is None or (now - cache_tee_time_time) > CACHE_TTL:
        cached_tee_time_data = fetch_tee_times_from_db()
        cache_tee_time_time = now

    return jsonify(cached_tee_time_data)
    # return jsonify({
    #     'count': len(cached_tee_times),
    #     'tee_times': cached_tee_times
    # })


@app.route('/api/cached_teetimes/<course_name>', methods=['GET'])
@traffic.rate_limit()
def get_cached_tee_times_by_course(course_name):
    """Get cached tee times for a specific course"""
    date = request.args.get('date')
    available_only = request.args.get('available_only', 'true').lower() == 'true'

    cached_tee_times = TeeTimeCacheService.get_cached_tee_times(
        course_name=course_name,
        available_only=available_only
    )

    return jsonify({
        'course_name': course_name,
        'count': len(cached_tee_times),
        'tee_times': cached_tee_times
    })


@app.route('/api/available_dates', methods=['GET'])
@traffic.rate_limit()
def get_available_dates():
    """Get distinct available dates from cached tee times"""
    available_dates = TeeTimeCacheService.get_available_dates()
    return jsonify(available_dates)


@app.route('/api/cleanup_cache', methods=['POST'])
@traffic.rate_limit()
def cleanup_old_cache():
    """Clean up old cached tee times"""
    days_old = request.json.get('days_old', 1) if request.json else 1
    TeeTimeCacheService.cleanup_old_entries(days_old)

    return jsonify({
        'message': f'Cleaned up tee times older than {days_old} days'
    })


@app.route('/api/course_requests', methods=['POST'])
@traffic.rate_limit()
def submit_course_request():
    """Submit a new course request"""
    data = request.get_json()

    if not data or not data.get('course_name') or not data.get('phone_number'):
        return jsonify({
            'error': 'Missing required fields: course_name and phone_number'
        }), 400

    new_request = CourseRequest(
        course_name=data.get("course_name"),
        phone_number=data.get("phone_number"),
        agree_to_notify=data.get('agree_to_notify', False),
        datetime_created=data.get("timestamp")
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        'message': 'Course request submitted successfully',
        'request': new_request.to_dict()
    }), 201


@app.route('/api/course_requests', methods=['GET'])
@traffic.rate_limit()
def get_course_requests():
    """Get all course requests"""
    added_only = request.args.get('added_only', 'false').lower() == 'true'

    query = CourseRequest.query
    if added_only:
        query = query.filter_by(is_added=True)

    requests = query.order_by(CourseRequest.datetime_created.desc()).all()

    return jsonify({
        'count': len(requests),
        'requests': [req.to_dict() for req in requests]
    })


@app.route('/api/course_requests/<int:request_id>/mark_added', methods=['PATCH'])
@traffic.rate_limit()
def mark_course_added(request_id):
    """Mark a course request as added to the site"""
    course_request = CourseRequest.query.get_or_404(request_id)

    course_request.is_added = True
    course_request.datetime_added_to_site = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Course request marked as added',
        'request': course_request.to_dict()
    })


@app.route('/api/bug-reports', methods=['POST'])
@traffic.rate_limit()
def file_a_bug():
    """Submit a bug report"""
    data = request.get_json()
    
    if not data or not data.get('description'):
        return jsonify({
            'error': 'Missing required field: description'
        }), 400
    
    # Get client IP address (handles proxy forwarding)
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_address = request.environ['REMOTE_ADDR']
    else:
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
    
    # Parse frontend timestamp if provided
    frontend_timestamp = None
    if data.get('timestamp'):
        try:
            from datetime import datetime
            frontend_timestamp = datetime.fromisoformat(data.get('timestamp').replace('Z', '+00:00'))
        except:
            pass  # If parsing fails, just use None
    
    new_bug_report = BugReport(
        description=data.get('description'),
        timestamp=frontend_timestamp,
        url=data.get('url'),
        user_agent=data.get('userAgent'),
        ip_address=ip_address
    )
    
    db.session.add(new_bug_report)
    db.session.commit()
    
    return jsonify({
        'message': 'Bug report submitted successfully',
        'report': new_bug_report.to_dict()
    }), 201
