from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs ):
    app=current_app._get_current_object()

    """send an email"""
    msg = Message(app.config['FOOTY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FOOTY_MAIL_SENDER'], recipients=[to])

    # we export the variable user into the template using the args dictionary
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thread_bg = Thread(target=send_async_email, args=[app, msg])
    thread_bg.start()
    return thread_bg
