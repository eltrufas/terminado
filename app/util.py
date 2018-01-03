from flask import current_app
from flask_mail import Message
import smtplib
import socket

def send_email(recipient, subject, html_message, text_message):
    mail_engine = current_app.extensions.get('mail', None)

    if not mail_engine:
        raise SendEmailError('Flask-Mail has not been initialized. Initialize Flask-Mail or disable USER_SEND_PASSWORD_CHANGED_EMAIL, USER_SEND_REGISTERED_EMAIL and USER_SEND_USERNAME_CHANGED_EMAIL')

    try:
        message = Message(subject,
                recipients=[recipient],
                html = html_message,
                body = text_message)
        mail_engine.send(message)

    except (socket.gaierror, socket.error) as e:
        raise SendEmailError('SMTP Connection error: Check your MAIL_SERVER and MAIL_PORT settings.')
    except smtplib.SMTPAuthenticationError:
        raise SendEmailError('SMTP Authentication error: Check your MAIL_USERNAME and MAIL_PASSWORD settings.')
