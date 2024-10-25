from flask import request, redirect, url_for, flash, current_app
from urllib.parse import urlparse, urljoin
from functools import wraps
from flask_login import current_user, logout_user
from datetime import datetime, timedelta


def is_safe_url(target):
    """
    Validate URL for safe redirect to prevent open redirect vulnerabilities

    Args:
        target: The URL to validate

    Returns:
        bool: True if the URL is safe, False otherwise
    """
    if target is None:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_client_ip():
    """
    Get client's IP address from request headers or remote address

    Returns:
        str: The client's IP address
    """
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr


def require_fresh_login(timeout_minutes=30):
    """
    Decorator to require recent login for sensitive operations

    Args:
        timeout_minutes (int): Number of minutes before requiring fresh login

    Returns:
        function: Decorated function requiring fresh login
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.url))

            last_login = getattr(current_user, "last_login", None)
            if not last_login or datetime.utcnow() - last_login > timedelta(
                minutes=timeout_minutes
            ):
                logout_user()
                flash("For your security, please log in again to continue.", "info")
                return redirect(url_for("auth.login", next=request.url))

            try:
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Error in protected route: {str(e)}")
                flash("An error occurred while processing your request.", "danger")
                return redirect(url_for("main.index"))

        return decorated_function

    return decorator


def check_content_security(content):
    """
    Check content for potential security issues

    Args:
        content (str): Content to check

    Returns:
        tuple: (is_safe, message) whether content is safe and any warning message
    """
    suspicious_patterns = [
        "<script",
        "javascript:",
        "data:text/html",
        "vbscript:",
        "onclick=",
        "onerror=",
        "onload=",
    ]

    content = content.lower()
    for pattern in suspicious_patterns:
        if pattern in content:
            return False, f"Suspicious content detected: {pattern}"
    return True, None


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent path traversal attacks

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    from werkzeug.utils import secure_filename
    import os

    # First use werkzeug's secure_filename
    safe_name = secure_filename(filename)

    # Additional sanitization
    safe_name = os.path.basename(safe_name)
    # Remove any potentially dangerous characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._-")

    return safe_name


def validate_password_strength(password):
    """
    Validate password strength

    Args:
        password (str): Password to validate

    Returns:
        tuple: (is_valid, message) whether password is valid and any error message
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, None


def generate_secure_token(length=32):
    """
    Generate a secure random token

    Args:
        length (int): Length of the token

    Returns:
        str: Secure random token
    """
    import secrets

    return secrets.token_urlsafe(length)


def mask_sensitive_data(data, fields_to_mask=None):
    """
    Mask sensitive data in logs or output

    Args:
        data (dict): Data containing sensitive information
        fields_to_mask (list): List of field names to mask

    Returns:
        dict: Data with sensitive fields masked
    """
    if fields_to_mask is None:
        fields_to_mask = {"password", "credit_card", "ssn", "token"}

    masked_data = data.copy()
    for field in fields_to_mask:
        if field in masked_data:
            masked_data[field] = "********"

    return masked_data
