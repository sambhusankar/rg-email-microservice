import os

import resend

from config import RESEND_API_KEY, FROM_EMAIL, FROM_NAME

resend.api_key = RESEND_API_KEY

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
LOGO_CID = "roomgrub-logo"


def _logo_attachment():
    with open(LOGO_PATH, "rb") as f:
        content = list(f.read())
    return {
        "filename": "logo.png",
        "content": content,
        "content_type": "image/png",
        "content_id": LOGO_CID,
    }


def send_email(to, subject, html_body, attachments=None):
    params = {
        "from": f"{FROM_NAME} <{FROM_EMAIL}>",
        "to": to,
        "subject": subject,
        "html": html_body,
    }
    all_attachments = list(attachments) if attachments else []
    if f"cid:{LOGO_CID}" in html_body:
        all_attachments.append(_logo_attachment())
    if all_attachments:
        params["attachments"] = all_attachments

    resend.Emails.send(params)
