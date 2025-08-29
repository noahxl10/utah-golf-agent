from dataclass import 


class BaseError(Exception):
    """ Base error """

    def __init__(self, message, provider=None, status_code=None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class RetryableAPIError(Exception):
    """Exception that should trigger retry"""
    pass


class NonRetryableAPIError(Exception):
    """Exception that should NOT trigger retry"""
    pass


class RequestError(BaseError):
    """ API rquest error """
    def __init__(self, message, provider):
        super().__init__(message, provider)


class RateLimitError(GolfAPIError):
    """ Exception raised when API rate limit is exceeded """
    def __init__(self, message="Rate limit exceeded", retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class CourseNotFoundError(GolfAPIError):
    """ Exception raised when a golf course isn't found """
    def __init__(self, course_id, provider=None):
        message = f"Course not found: {course_id}"
        super().__init__(message, provider)
        self.course_id = course_id
