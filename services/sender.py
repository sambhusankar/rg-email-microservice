import resend

from config import RESEND_API_KEY, FROM_EMAIL

resend.api_key = RESEND_API_KEY


def send_email(to, subject, html_body):
    resend.Emails.send({
        "from": FROM_EMAIL,
        "to": to,
        "subject": subject,
        "html": html_body,
    })
