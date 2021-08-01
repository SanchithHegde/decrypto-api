"""
Utility functions to send emails and handling password reset.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import emails  # type: ignore
from emails.backend.smtp.exceptions import SMTPConnectNetworkError  # type: ignore
from emails.template import JinjaTemplate  # type: ignore
from jose import jwt  # type: ignore

from app import LOGGER
from app.core.config import settings
from app.core.security import JWT_SIGNATURE_ALGORITHM


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Send an email to the provided email address with the provided subject template,
    email HTML template, and context for rendering the email body.

    # Parameters:

    * `email_to`: Email address of the recipient.
    * `subject_template`: Jinja template string to derive the email subject from.
    * `html_template`: Jinja template string to render the email body from.
    * `environment`: Context used for rendering the email subject and the email body
      templates.
    """

    # Using None instead of default value {} for `environment` because an empty dict is
    # considered a "dangerous" default value, causing unexpected behavior.
    if environment is None:
        environment = {}

    assert settings.EMAILS_ENABLED, "No provided configuration for email variables"

    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "fail_silently": False,  # Raise exceptions if sending email fails
    }

    if settings.SMTP_TLS:
        smtp_options["tls"] = True

    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER

    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    try:
        response = message.send(to=email_to, render=environment, smtp=smtp_options)
        LOGGER.info("Email sent to %s. Response: %s", email_to, response)

    except SMTPConnectNetworkError as error:
        LOGGER.exception("Failed to send an email to %s: %s", email_to, error)
        raise


def send_test_email(email_to: str) -> None:
    """
    Send a test email to the provided email address.
    """

    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"

    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as file:
        template_str = file.read()

    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    """
    Send a reset password email to the provided email address.

    # Parameters:

    * `email_to`: Email address of the recipient.
    * `email`: User's registered email address (email address stored in the database).
    * `token`: Token used for creating the reset password link.
    """

    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"

    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as file:
        template_str = file.read()

    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    """
    Send a confirmation email about a user's account creation to the provided email
    address.

    # Parameters:

    * `email_to`: Email address of the recipient.
    * `username`: Username rendered in the email body. Should be same as `email_to`
      unless a separate "username" is stored in the database.
    * `password`: Password rendered in the email body.
    """

    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"

    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as file:
        template_str = file.read()

    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token for the provided email address.
    """

    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=JWT_SIGNATURE_ALGORITHM,
    )

    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verifies the password reset token and returns the email address of the user if
    successful, `None` if unsuccessful.
    """

    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[JWT_SIGNATURE_ALGORITHM]
        )

        return decoded_token["sub"]

    except jwt.JWTError:
        return None
