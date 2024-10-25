from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app import mail


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body):
    """Send email wrapper"""
    msg = Message(
        subject=subject, recipients=recipients, body=text_body, html=html_body
    )
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()


def send_password_reset_email(user):
    """Send password reset email to user"""
    token = user.get_reset_password_token()
    send_email(
        "Reset Your Password",
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )
