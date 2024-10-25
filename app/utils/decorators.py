from functools import wraps
from datetime import datetime
from time import time
# import logging

from flask import request, current_app, abort, flash, render_template
from flask_login import current_user


def log_action(action_name):
    """
    Decorator to log user actions

    Args:
        action_name (str): Name of the action being performed

    Usage:
        @log_action('view_dashboard')
        def dashboard():
            return render_template('dashboard.html')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get start time
            start_time = time()

            # Log the action
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action_name,
                "user_id": current_user.id if not current_user.is_anonymous else None,
                "username": (
                    current_user.username if not current_user.is_anonymous else None
                ),
                "ip_address": request.remote_addr,
                "user_agent": request.user_agent.string,
                "endpoint": request.endpoint,
                "method": request.method,
                "url": request.url,
                "args": dict(request.args),
                "form": dict(request.form) if request.form else None,
            }

            try:
                # Execute the route function
                response = f(*args, **kwargs)

                # Calculate execution time
                execution_time = time() - start_time

                # Add response info to log data
                log_data.update(
                    {
                        "status": "success",
                        "execution_time": execution_time,
                        "status_code": getattr(response, "status_code", 200),
                    }
                )

                current_app.logger.info(f"Action logged: {log_data}")
                return response

            except Exception as e:
                # Log error if something goes wrong
                log_data.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "execution_time": time() - start_time,
                    }
                )
                current_app.logger.error(f"Action error: {log_data}")
                raise

        return decorated_function

    return decorator


def performance_monitor():
    """
    Decorator to monitor route performance

    Usage:
        @performance_monitor()
        def slow_route():
            return render_template('slow_page.html')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time()
            response = f(*args, **kwargs)
            execution_time = time() - start_time

            if execution_time > current_app.config.get("SLOW_ROUTE_THRESHOLD", 1.0):
                current_app.logger.warning(
                    f"Slow route detected: {request.endpoint} took {execution_time:.2f} seconds"
                )

            return response

        return decorated_function

    return decorator


def require_role(role):
    """
    Decorator to require specific user role

    Args:
        role (str): Required role name

    Usage:
        @require_role('admin')
        def admin_only():
            return render_template('admin.html')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                current_app.logger.warning(
                    f"Unauthenticated user attempted to access {request.endpoint}"
                )
                return current_app.login_manager.unauthorized()

            if not hasattr(current_user, "role") or current_user.role != role:
                current_app.logger.warning(
                    f"User {current_user.username} attempted to access {request.endpoint} without {role} role"
                )
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True):
    """
    Decorator to set cache control headers

    Usage:
        @cache_control(max_age=300)  # Cache for 5 minutes
        def cacheable_route():
            return render_template('cached_page.html')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            if not isinstance(response, current_app.response_class):
                response = current_app.make_response(response)

            if no_cache:
                response.cache_control.no_cache = True
            if no_store:
                response.cache_control.no_store = True
            if must_revalidate:
                response.cache_control.must_revalidate = True
            if max_age is not None:
                response.cache_control.max_age = max_age

            return response

        return decorated_function

    return decorator


def validate_form(form_class):
    """
    Decorator to validate form data

    Args:
        form_class: WTForms form class to validate

    Usage:
        @validate_form(LoginForm)
        def login():
            # Form is already validated here
            return process_login(form)
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            form = form_class()
            if not form.validate_on_submit():
                current_app.logger.warning(
                    f"Form validation failed for {request.endpoint}: {form.errors}"
                )
                flash("Please correct the errors in the form.", "danger")
                return render_template(
                    f"{request.endpoint.replace('.', '/')}.html", form=form
                )
            return f(form, *args, **kwargs)

        return decorated_function

    return decorator
