from flask import render_template, current_app, request, jsonify
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException
import traceback

from app.models import db

__all__ = ["register_error_handlers"]


def register_error_handlers(app):
    """
    Register error handlers for the application.

    Args:
        app: Flask application instance
    """
    # 400 Bad Request
    app.register_error_handler(
        400,
        lambda e: _handle_error(
            e, "Bad Request", 400, template="errors/400.html", log_level="warning"
        ),
    )

    # 401 Unauthorized
    app.register_error_handler(
        401,
        lambda e: _handle_error(
            e, "Unauthorized", 401, template="errors/401.html", log_level="warning"
        ),
    )

    # 403 Forbidden
    app.register_error_handler(
        403,
        lambda e: _handle_error(
            e, "Forbidden", 403, template="errors/403.html", log_level="warning"
        ),
    )

    # 404 Not Found
    app.register_error_handler(
        404,
        lambda e: _handle_error(
            e,
            "Not Found",
            404,
            template="errors/404.html",
            log_level="info",
            log_msg=f"Page not found: {request.url}",
        ),
    )

    # 405 Method Not Allowed
    app.register_error_handler(
        405,
        lambda e: _handle_error(
            e,
            "Method Not Allowed",
            405,
            template="errors/405.html",
            log_level="warning",
            log_msg=f"Method not allowed: {request.method} {request.url}",
        ),
    )

    # 429 Too Many Requests
    app.register_error_handler(
        429,
        lambda e: _handle_error(
            e,
            "Too Many Requests",
            429,
            template="errors/429.html",
            log_level="warning",
            log_msg=f"Rate limit exceeded: {request.remote_addr}",
        ),
    )

    # 500 Internal Server Error
    app.register_error_handler(500, lambda e: _handle_server_error(e))

    # CSRF Error
    app.register_error_handler(
        CSRFError,
        lambda e: _handle_error(
            e,
            "CSRF token missing or invalid",
            400,
            template="errors/csrf_error.html",
            log_level="warning",
            log_msg="CSRF error occurred",
        ),
    )

    # Generic HTTP Exception
    app.register_error_handler(HTTPException, lambda e: _handle_http_error(e))

    # Catch-all Exception Handler
    app.register_error_handler(Exception, lambda e: _handle_exception(e))


def _handle_error(
    error, message, status_code, template, log_level="error", log_msg=None
):
    """
    Generic error handler

    Args:
        error: The error that occurred
        message: Error message for the response
        status_code: HTTP status code
        template: Template to render for HTML response
        log_level: Logging level to use
        log_msg: Optional custom log message
    """
    # Log the error
    log_func = getattr(current_app.logger, log_level)
    log_func(log_msg or f"{message}: {error}")

    # Return JSON for API requests
    if request.is_json:
        return jsonify(error=message), status_code

    # Return HTML for browser requests
    return render_template(template), status_code


def _handle_server_error(error):
    """Handle 500 Internal Server Error"""
    db.session.rollback()
    error_details = traceback.format_exc()
    current_app.logger.error(f"Server Error: {error}\n{error_details}")

    if request.is_json:
        return jsonify(error="Internal server error"), 500

    return render_template("errors/500.html"), 500


def _handle_http_error(error):
    """Handle general HTTP exceptions"""
    current_app.logger.error(f"HTTP error occurred: {error}")

    if request.is_json:
        return jsonify(error=str(error)), error.code

    return render_template("errors/generic.html", error=error), error.code


def _handle_exception(error):
    """Handle unhandled exceptions"""
    db.session.rollback()
    error_details = traceback.format_exc()
    current_app.logger.error(f"Unhandled exception: {error}\n{error_details}")

    if request.is_json:
        return jsonify(error="An unexpected error occurred"), 500

    return render_template("errors/500.html"), 500
