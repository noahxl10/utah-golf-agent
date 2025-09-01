from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import UniqueConstraint
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

class TeeTimeCache(db.Model):
    __tablename__ = 'tee_time_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format
    start_time = db.Column(db.String(25), nullable=False)  # ISO format with timezone
    players_available = db.Column(db.Integer, nullable=True)  # Can be null if not specified
    
    # Additional tee time information
    holes = db.Column(db.JSON)  # Store as JSON array [9, 18]
    booking_url = db.Column(db.String(500))
    provider = db.Column(db.String(50))
    green_fee = db.Column(db.Float)
    half_cart = db.Column(db.Float)
    price = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    restrictions = db.Column(db.JSON)  # Store as JSON array
    special_offer = db.Column(db.Boolean, default=False)
    
    # Availability tracking
    is_available = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Compound unique constraint as requested
    __table_args__ = (
        UniqueConstraint('course_name', 'date', 'start_time', 'players_available', 
                        name='unique_tee_time_slot'),
    )
    
    def __repr__(self):
        return f'<TeeTimeCache {self.course_name} on {self.date} at {self.start_time}>'


class CourseRequest(db.Model):
    __tablename__ = 'course_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    is_added = db.Column(db.Boolean, default=False)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)
    datetime_added_to_site = db.Column(db.DateTime, nullable=True)
    course_id = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<CourseRequest {self.course_name} by {self.phone_number}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'course_name': self.course_name,
            'phone_number': self.phone_number,
            'is_added': self.is_added,
            'datetime_created': self.datetime_created.isoformat() if self.datetime_created else None,
            'datetime_added_to_site': self.datetime_added_to_site.isoformat() if self.datetime_added_to_site else None,
            'course_id': self.course_id
        }
    

def init_db(app):
    """Initialize the database with Flask app context"""
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    from flask import Flask
    test_app = Flask(__name__)
    init_db(test_app)