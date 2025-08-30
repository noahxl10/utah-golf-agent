from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os
from src.config import courses
from src.scraper import scraper
from src import test
from src.models import db, init_db
from src.cache_service import TeeTimeCacheService

app = Flask(__name__)
CORS(app, origins="*")
app.config['DEBUG'] = True

# Initialize database
init_db(app)


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
    date = request.args.get('date', '2025-09-01')
    tee_times = scraper.chronogolf_tee_times(date)
    
    # Cache the tee times
    if tee_times:
        TeeTimeCacheService.cache_tee_times(tee_times, 'chronogolf')
    
    data_to_return = [tee_time.model_dump() for tee_time in tee_times]
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
    date = request.args.get('date')
    available_only = request.args.get('available_only', 'true').lower() == 'true'
    
    cached_tee_times = TeeTimeCacheService.get_cached_tee_times(
        date=date, 
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
