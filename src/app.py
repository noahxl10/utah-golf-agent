from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, date as dt_date
import sys
import os
from src.config import courses
from src.scraper import scraper
from src import test
from src.models import db, init_db, CourseRequest
from src.cache_service import TeeTimeCacheService


app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
app.config['DEBUG'] = True

# Initialize database
init_db(app)


def current_date():
    return dt_date.today().strftime("%Y-%m-%d")


@app.route('/')
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
            "/api/course_requests": "Submit (POST) or get (GET) course requests",
            "/api/course_requests/<id>/mark_added": "Mark course request as added (PATCH)"
        }
    })


@app.route('/api/eaglewood_teetimes', methods=['GET'])
def get_eaglewood_tee_times():
    date = request.args.get('date', '2025-09-01')
    tee_times = scraper.eaglewood_tee_times(date)

    # Cache the tee times
    if tee_times:
        TeeTimeCacheService.cache_tee_times(tee_times, 'eaglewood')

    data_to_return = [tee_time.model_dump() for tee_time in tee_times]
    return jsonify(data_to_return)


@app.route('/api/foreup_teetimes', methods=['GET'])
def get_foreup_tee_times():
    date = request.args.get('date', '2025-09-01')
    tee_times = scraper.foreup_tee_times(date)

    # Cache the tee times
    if tee_times:
        TeeTimeCacheService.cache_tee_times(tee_times, 'foreup')

    data_to_return = [tee_time.model_dump() for tee_time in tee_times]
    return jsonify(data_to_return)


@app.route('/api/chronogolf_teetimes', methods=['GET'])
def get_chronogolf_tee_times():
    date = "2025-09-01"
    tee_times = scraper.chronogolf_tee_times(date)
    # print(tee_times[0])
    data_to_return = [tee_time.model_dump() for tee_time in tee_times]

    return jsonify(data_to_return)

@app.route('/api/teetimes', methods=['GET'])
def get_all_tee_times():
    date = request.args.get('date', '2025-09-02')
    
    c_tee_times = scraper.chronogolf_tee_times(date)
    # Cache the tee times
    if c_tee_times:
        TeeTimeCacheService.cache_tee_times(c_tee_times, 'chronogolf')

    f_tee_times = scraper.foreup_tee_times(date)
    # Cache the tee times
    if f_tee_times:
        TeeTimeCacheService.cache_tee_times(f_tee_times, 'foreup')

    e_tee_times = scraper.eaglewood_tee_times(date)
    # Cache the tee times
    if e_tee_times:
        TeeTimeCacheService.cache_tee_times(e_tee_times, 'eaglewood')

    c_tee_times.extend(f_tee_times)
    c_tee_times.extend(e_tee_times)

    data_to_return = [tee_time.model_dump() for tee_time in c_tee_times]
    return jsonify(data_to_return)


@app.route('/test_api/teetimes', methods=['GET'])
def test_get_all_tee_times():
    """
    This endpoint fetches a list of TeeTime objects and returns them as a JSON array.
    """

    tee_times_list = test.get_mock_tee_times()

    data_to_return = [tee_time.model_dump() for tee_time in tee_times_list]
    response = jsonify(data_to_return)

    return response


@app.route("/api/courses", methods=['GET'])
def get_course_list():
    course_list = [course for course in courses]
    response = jsonify(course_list)
    return response


@app.route('/api/cached_teetimes', methods=['GET'])
def get_all_cached_tee_times():
    """Get all cached tee times"""
    # date = request.args.get('date')

    date = current_date()

    available_only = request.args.get('available_only', 'true').lower() == 'true'

    cached_tee_times = TeeTimeCacheService.get_cached_tee_times(
        current_date=date,
        available_only=available_only
    )
    return jsonify(cached_tee_times)
    # return jsonify({
    #     'count': len(cached_tee_times),
    #     'tee_times': cached_tee_times
    # })


@app.route('/api/cached_teetimes/<course_name>', methods=['GET'])
def get_cached_tee_times_by_course(course_name):
    """Get cached tee times for a specific course"""
    date = request.args.get('date')
    available_only = request.args.get('available_only', 'true').lower() == 'true'

    cached_tee_times = TeeTimeCacheService.get_cached_tee_times(
        course_name=course_name,
        date=date,
        available_only=available_only
    )

    return jsonify({
        'course_name': course_name,
        'count': len(cached_tee_times),
        'tee_times': cached_tee_times
    })


@app.route('/api/cleanup_cache', methods=['POST'])
def cleanup_old_cache():
    """Clean up old cached tee times"""
    days_old = request.json.get('days_old', 1) if request.json else 1
    TeeTimeCacheService.cleanup_old_entries(days_old)

    return jsonify({
        'message': f'Cleaned up tee times older than {days_old} days'
    })


@app.route('/api/course_requests', methods=['POST'])
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
        # course_id=data.get('course_id')
    )
    # {
    #   course_name: 'asdf',
    #   phone_number: '(814) 969-9482',
    #   agree_to_notify: true,
    #   timestamp: '2025-09-01T18:18:19.921Z'
    # }
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Course request submitted successfully',
        'request': new_request.to_dict()
    }), 201


@app.route('/api/course_requests', methods=['GET'])
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
