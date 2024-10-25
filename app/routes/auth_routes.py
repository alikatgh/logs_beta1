from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    session,
)
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user

# Change to relative imports
from . import auth  # Import auth blueprint
from ..forms import (
    RegistrationForm,
    LoginForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from ..models import User, db
from ..utils.security import is_safe_url, get_client_ip
from ..utils.rate_limit import rate_limit
from ..utils.email import send_password_reset_email


def log_auth_event(event_type, user=None, success=True, details=None):
    """Log authentication related events"""
    event_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": get_client_ip(),
        "user_agent": request.user_agent.string,
        "username": user.username if user else None,
        "success": success,
        "details": details,
    }
    current_app.logger.info(f"Auth event: {event_data}")


@auth.route("/register", methods=["GET", "POST"])
@rate_limit("register", limit=5, period=3600)  # 5 attempts per hour
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user exists
            if User.query.filter(
                db.or_(
                    User.email == form.email.data.lower(),
                    User.username == form.username.data.lower(),
                )
            ).first():
                flash("Email or username already exists.", "danger")
                log_auth_event("registration_failed", details="User already exists")
                return render_template("auth/register.html", form=form)

            # Create new user
            new_user = User(
                username=form.username.data.lower(), email=form.email.data.lower()
            )
            new_user.set_password(form.password.data)

            db.session.add(new_user)
            db.session.commit()

            log_auth_event("registration_success", user=new_user)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            flash("An error occurred during registration.", "danger")
            return render_template("auth/register.html", form=form), 500

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
@rate_limit("login", limit=5, period=300)  # 5 attempts per 5 minutes
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data.lower()).first()

            if user and user.check_password(form.password.data):
                if not user.is_active:
                    flash("This account has been deactivated.", "danger")
                    log_auth_event(
                        "login_failed", user=user, details="Account deactivated"
                    )
                    return render_template("auth/login.html", form=form)

                # Successful login
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()

                # Clear any failed login attempts
                session.pop("login_attempts", None)

                log_auth_event("login_success", user=user)
                flash("Welcome back!", "success")

                # Handle redirect
                next_page = request.args.get("next")
                if not next_page or not is_safe_url(next_page):
                    next_page = url_for("main.index")

                return redirect(next_page)
            else:
                # Failed login attempt
                login_attempts = session.get("login_attempts", 0) + 1
                session["login_attempts"] = login_attempts

                if login_attempts >= 5:
                    flash("Too many failed attempts. Please try again later.", "danger")
                    log_auth_event("login_failed", details="Too many attempts")
                else:
                    flash("Invalid email or password.", "danger")
                    log_auth_event("login_failed", details="Invalid credentials")

        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash("An error occurred during login.", "danger")
            return render_template("auth/login.html", form=form), 500

    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    if current_user.is_authenticated:
        user = current_user
        logout_user()
        log_auth_event("logout", user=user)

        # Clear session
        session.clear()

        flash("You have been logged out successfully.", "info")

    return redirect(url_for("auth.login"))


@auth.route("/reset-password-request", methods=["GET", "POST"])
@rate_limit("password_reset", limit=3, period=3600)  # 3 attempts per hour
def reset_password_request():
    """Handle password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Send password reset email
            send_password_reset_email(user)
            flash("Check your email for password reset instructions.", "info")
            log_auth_event("password_reset_request", user=user)
        else:
            flash("Check your email for password reset instructions.", "info")
            log_auth_event(
                "password_reset_request_invalid_email", details=form.email.data
            )

        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password_request.html", form=form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
@rate_limit("password_reset_confirm", limit=3, period=3600)
def reset_password(token):
    """Handle password reset confirmation"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.verify_reset_password_token(token)
    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.", "success")
        log_auth_event("password_reset_success", user=user)
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


# Error handlers
@auth.errorhandler(429)
def too_many_requests(e):
    """Handle rate limit exceeded"""
    flash("Too many attempts. Please try again later.", "danger")
    return render_template("auth/error.html", error="Rate limit exceeded"), 429


@auth.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    db.session.rollback()
    current_app.logger.error(f"Internal error: {str(e)}")
    return render_template("auth/error.html", error="Internal server error"), 500
