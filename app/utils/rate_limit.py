from flask import current_app
from flask_login import current_user
from functools import wraps
from time import time
from .security import get_client_ip
import logging


class RateLimiter:
    """Rate limiting implementation using in-memory storage"""

    def __init__(self, key_prefix, limit, period):
        """
        Initialize rate limiter

        Args:
            key_prefix (str): Prefix for rate limit key
            limit (int): Number of allowed requests
            period (int): Time period in seconds
        """
        self.key_prefix = key_prefix
        self.limit = limit
        self.period = period
        self._logger = logging.getLogger(__name__)

    def _get_storage(self):
        """Get or initialize rate limit storage"""
        if not hasattr(current_app, "rate_limit_storage"):
            current_app.rate_limit_storage = {}
        return current_app.rate_limit_storage

    def _clean_old_entries(self, storage, key, now):
        """Remove expired entries from storage"""
        if key in storage:
            storage[key] = [t for t in storage[key] if t > now - self.period]
        else:
            storage[key] = []

    def is_rate_limited(self, key):
        """
        Check if the request is rate limited

        Args:
            key (str): Identifier for the rate limit check

        Returns:
            bool: True if rate limited, False otherwise
        """
        try:
            storage = self._get_storage()
            now = time()
            key = f"{self.key_prefix}:{key}"

            # Clean up old entries
            self._clean_old_entries(storage, key, now)

            # Check limit
            if len(storage[key]) >= self.limit:
                self._logger.warning(
                    f"Rate limit exceeded for key: {key}, "
                    f"attempts: {len(storage[key])}, limit: {self.limit}"
                )
                return True

            # Add new timestamp
            storage[key].append(now)
            return False

        except Exception as e:
            self._logger.error(
                f"Rate limit error for key {key}: {str(e)}", exc_info=True
            )
            return False  # Fail open on error

    def get_remaining_requests(self, key):
        """
        Get number of remaining requests allowed

        Args:
            key (str): Identifier for the rate limit check

        Returns:
            tuple: (remaining requests, seconds until reset)
        """
        try:
            storage = self._get_storage()
            now = time()
            key = f"{self.key_prefix}:{key}"

            self._clean_old_entries(storage, key, now)

            remaining = max(0, self.limit - len(storage[key]))
            if storage[key]:
                reset_time = min(storage[key]) + self.period - now
            else:
                reset_time = 0

            return remaining, int(reset_time)

        except Exception as e:
            self._logger.error(
                f"Error getting remaining requests for key {key}: {str(e)}",
                exc_info=True,
            )
            return 0, 0


def create_rate_limit_response(remaining, reset_time, limit):
    """
    Create a rate limit exceeded response

    Args:
        remaining (int): Number of remaining requests
        reset_time (int): Seconds until rate limit reset
        limit (int): Rate limit value

    Returns:
        tuple: Response text and headers dictionary
    """
    response_text = "Rate limit exceeded. Please try again later."
    headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time),
        "Retry-After": str(reset_time),
    }
    return response_text, headers


def rate_limit(key_prefix, limit=5, period=300):
    """
    Rate limiting decorator

    Args:
        key_prefix (str): Prefix for rate limit key (e.g., 'login', 'register')
        limit (int): Number of allowed requests
        period (int): Time period in seconds

    Returns:
        function: Decorated function with rate limiting
    """
    limiter = RateLimiter(key_prefix, limit, period)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                identifier = (
                    str(current_user.id)
                    if getattr(current_user, "is_authenticated", False)
                    else get_client_ip()
                )

                if limiter.is_rate_limited(identifier):
                    remaining, reset_time = limiter.get_remaining_requests(identifier)
                    response_text, headers = create_rate_limit_response(
                        remaining, reset_time, limit
                    )

                    current_app.logger.warning(
                        f"Rate limit exceeded for {key_prefix} by {identifier}. "
                        f"Remaining: {remaining}, Reset in: {reset_time}s"
                    )

                    # Create response using make_response from current_app
                    response = current_app.make_response(response_text)
                    response.status_code = 429

                    # Add headers to response
                    for key, value in headers.items():
                        response.headers[key] = value

                    return response

                return f(*args, **kwargs)

            except Exception as e:
                current_app.logger.error(
                    f"Rate limit decorator error: {str(e)}", exc_info=True
                )
                return f(*args, **kwargs)  # Fail open on error

        return decorated_function

    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, message="Rate limit exceeded", remaining=0, reset_time=0):
        self.message = message
        self.remaining = remaining
        self.reset_time = reset_time
        super().__init__(self.message)
