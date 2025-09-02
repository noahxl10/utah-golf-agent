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
    start_time = db.Column(db.String(25),
                           nullable=False)  # ISO format with timezone
    players_available = db.Column(
        db.Integer, nullable=True)  # Can be null if not specified

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
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Compound unique constraint as requested
    __table_args__ = (UniqueConstraint('course_name',
                                       'date',
                                       'start_time',
                                       'players_available',
                                       name='unique_tee_time_slot'), )

    def __repr__(self):
        return f'<TeeTimeCache {self.course_name} on {self.date} at {self.start_time}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id':
            self.id,
            'course_name':
            self.course_name,
            'date':
            self.date,
            'start_time_unf':
            self.start_time,
            'start_time':
            self.start_time,  # For compatibility with frontend
            'players_available':
            self.players_available,
            'holes':
            self.holes,
            'booking_url':
            self.booking_url,
            'provider':
            self.provider,
            'green_fee':
            self.green_fee,
            'half_cart':
            self.half_cart,
            'price':
            self.price,
            'subtotal':
            self.subtotal,
            'restrictions':
            self.restrictions or [],
            'special_offer':
            self.special_offer or False,
            'is_available':
            self.is_available,
            'created_at':
            self.created_at.isoformat() if self.created_at else None,
            'updated_at':
            self.updated_at.isoformat() if self.updated_at else None,
            'last_seen_at':
            self.last_seen_at.isoformat() if self.last_seen_at else None
        }


class CourseRequest(db.Model):
    __tablename__ = 'course_requests'

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    agree_to_notify = db.Column(db.Boolean, default=False)
    is_added = db.Column(db.Boolean, default=False)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)
    datetime_added_to_site = db.Column(db.DateTime, nullable=True)
    course_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<CourseRequest {self.course_name} by {self.phone_number}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id':
            self.id,
            'course_name':
            self.course_name,
            'phone_number':
            self.phone_number,
            'agree_to_notify':
            self.agree_to_notify, 
            'is_added':
            self.is_added,
            'datetime_created':
            self.datetime_created.isoformat()
            if self.datetime_created else None,
            'datetime_added_to_site':
            self.datetime_added_to_site.isoformat()
            if self.datetime_added_to_site else None,
            'course_id':
            self.course_id
        }


class BugReport(db.Model):
    __tablename__ = 'bug_reports'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=True)  # Frontend provided timestamp
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # Backend timestamp
    url = db.Column(db.String(500), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 can be up to 45 chars

    def __repr__(self):
        return f'<BugReport {self.id} from {self.ip_address}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'url': self.url,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address
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
