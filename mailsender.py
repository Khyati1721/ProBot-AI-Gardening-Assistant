from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import os
import json
import base64
import uuid

from email.mime.text import MIMEText
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()


# =========================================================
# GOOGLE SCOPES
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]


# =========================================================
# GET SECRET
# =========================================================

def get_secret(name):

    # Streamlit Cloud
    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]

    except Exception:
        pass

    # Local .env
    return os.getenv(name)


# =========================================================
# GET GOOGLE CREDENTIALS
# =========================================================

def get_credentials():

    token_str = get_secret("GOOGLE_TOKEN_JSON")

    if not token_str:
        raise ValueError(
            "GOOGLE_TOKEN_JSON is missing. "
            "Add it to Streamlit Secrets."
        )

    try:
        token_data = json.loads(token_str)

    except json.JSONDecodeError:
        raise ValueError(
            "GOOGLE_TOKEN_JSON contains invalid JSON."
        )

    creds = Credentials.from_authorized_user_info(
        token_data,
        SCOPES
    )

    # Automatically refresh expired access token
    if creds.expired and creds.refresh_token:

        creds.refresh(Request())

    if not creds.valid:

        raise ValueError(
            "Google credentials are invalid or expired."
        )

    return creds


# =========================================================
# SEND EMAIL
# =========================================================

def send_email(to, subject, message_text):

    creds = get_credentials()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    message = MIMEText(message_text)

    message["to"] = to
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    body = {
        "raw": raw_message
    }

    service.users().messages().send(
        userId="me",
        body=body
    ).execute()

    return f"Email sent to {to}."


# =========================================================
# CREATE CALENDAR EVENT + GOOGLE MEET
# =========================================================

def create_event(
    summary,
    description,
    start_time,
    duration_minutes
):

    creds = get_credentials()

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    start_datetime = datetime.fromisoformat(
        start_time
    )

    end_datetime = (
        start_datetime
        + timedelta(minutes=duration_minutes)
    )

    event = {
        "summary": summary,

        "description": description,

        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },

        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },

        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4())
            }
        }
    }

    event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1
    ).execute()

    meet_link = event.get(
        "hangoutLink",
        "No Meet link created"
    )

    return (
        f"Event created: {event.get('htmlLink')}\n"
        f"Google Meet link: {meet_link}"
    )
