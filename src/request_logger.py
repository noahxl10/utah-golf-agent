"""
Request logging service for tracking all external API calls to tee time providers.
"""
import time
from datetime import datetime
from typing import Optional, Dict, Any
from src.models import RequestLog, db


class RequestLogger:
    """Service for logging all external API requests to tee time providers"""
    
    @staticmethod
    def log_request(
        provider: str,
        endpoint: str,
        course: Optional[str] = None,
        response: Optional[Dict[Any, Any]] = None,
        error: Optional[str] = None,
        is_error: bool = False,
        status_code: Optional[int] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Log an API request to the database
        
        Args:
            provider: Provider name (chronogolf, eaglewood, foreup, etc)
            endpoint: Full URL endpoint called
            course: Course name (optional)
            response: Full API response JSON (optional)
            error: Error message if request failed (optional)
            is_error: Boolean flag indicating if request failed
            status_code: HTTP status code (optional)
            duration_ms: Request duration in milliseconds (optional)
        """
        # Skip logging if running in standalone mode
        import os
        if os.environ.get('STANDALONE_MODE'):
            return
            
        try:
            # Create the log entry
            log_entry = RequestLog(
                datetime=datetime.utcnow(),
                course=course,
                provider=provider,
                endpoint=endpoint,
                response=response,
                error=error,
                is_error=is_error,
                status_code=status_code,
                duration_ms=duration_ms
            )
            
            # Save to database
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            # Don't let logging errors break the main application
            print(f"Error logging request: {e}")
            try:
                db.session.rollback()
            except:
                pass

    @staticmethod
    def log_success(
        provider: str,
        endpoint: str,
        response: Dict[Any, Any],
        course: Optional[str] = None,
        status_code: int = 200,
        duration_ms: Optional[int] = None
    ) -> None:
        """Log a successful API request"""
        RequestLogger.log_request(
            provider=provider,
            endpoint=endpoint,
            course=course,
            response=response,
            error=None,
            is_error=False,
            status_code=status_code,
            duration_ms=duration_ms
        )

    @staticmethod
    def log_error(
        provider: str,
        endpoint: str,
        error: str,
        course: Optional[str] = None,
        status_code: Optional[int] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """Log a failed API request"""
        RequestLogger.log_request(
            provider=provider,
            endpoint=endpoint,
            course=course,
            response=None,
            error=error,
            is_error=True,
            status_code=status_code,
            duration_ms=duration_ms
        )


class RequestTimer:
    """Context manager for timing API requests"""
    
    def __init__(self):
        self.start_time = None
        self.duration_ms = None
    
    def __enter__(self):
        self.start_time = time.time() * 1000  # Convert to milliseconds
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.duration_ms = int((time.time() * 1000) - self.start_time)
    
    def get_duration(self) -> Optional[int]:
        """Get the request duration in milliseconds"""
        return self.duration_ms