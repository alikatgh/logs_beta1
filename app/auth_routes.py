from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from urllib.parse import urlparse
from .forms import RegistrationForm, LoginForm
from .models import User
from .database import db
from flask_login import login_user, logout_user, login_required, current_user

# Define the auth blueprint
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Please choose a different one.', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")
    if current_user.is_authenticated:
        print("User is already authenticated")
        return redirect(url_for('main.index'))

    form = LoginForm()
    print(f"CSRF Token: {form.csrf_token.current_token}")

    if request.method == 'POST':
        print("POST request received")
        print(f"Form data: {request.form}")

        if form.validate_on_submit():
            print("Form validated")
            user = User.query.filter_by(email=form.email.data).first()
            print(f"User found: {user}")
            if user and user.check_password(form.password.data):
                login_user(user)
                print(f"User {user.username} logged in successfully")
                print(
                    f"Is user authenticated? {current_user.is_authenticated}")
                flash('Logged in successfully.', 'success')
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('main.index')
                print(f"Redirecting to: {next_page}")
                return redirect(next_page)
            else:
                print("Invalid email or password")
                flash('Invalid email or password.', 'danger')
        else:
            print("Form not validated")
            print(f"Form errors: {form.errors}")

    # Move these prints outside the POST condition
    print(
        f"CSRF protection active: {current_app.config.get('WTF_CSRF_ENABLED', False)}")
    print(f"Secret key set: {'SECRET_KEY' in current_app.config}")
    print(
        f"Session cookie name: {current_app.config.get('SESSION_COOKIE_NAME')}")

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
