# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

with open('../sendgrid.env', 'r') as f:
    s = f.read()
    SENDGRID_API_KEY = s.split('=')[1].lstrip("'").rstrip("'")


def send_email(to_emails, subject, content):
    message = Mail(
        from_email='no-reply@ryenandvivekstartup.online',
        to_emails=to_emails,
        subject=subject,
        html_content=content)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(e.message)
        return False