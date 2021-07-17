"""
Application-wide configuration.
"""

import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    """
    Settings for various aspects of the application, allowing values to be overridden by
    environment variables.
    """

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://subdomain.example.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(  # pylint: disable=no-self-argument,no-self-use
        cls, origins: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """
        Assemble CORS origins.
        """

        if isinstance(origins, str) and not origins.startswith("["):
            return [i.strip() for i in origins.split(",")]

        if isinstance(origins, (list, str)):
            return origins

        raise ValueError(origins)

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(  # pylint: disable=no-self-argument,no-self-use
        cls, connection_str: Optional[str], values: Dict[str, Any]
    ) -> Any:
        """
        Assemble database connection string.
        """

        if isinstance(connection_str, str):
            return connection_str

        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(  # pylint: disable=no-self-argument,no-self-use
        cls, project_name: Optional[str], values: Dict[str, Any]
    ) -> str:
        """
        Returns project name.
        """

        if not project_name:
            return values["PROJECT_NAME"]

        return project_name

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(  # pylint: disable=no-self-argument,no-self-use
        cls, _: bool, values: Dict[str, Any]
    ) -> bool:
        """
        Returns `True` if emails are to be enabled.

        SMTP_HOST, SMTP_PORT and EMAILS_FROM_EMAIL need to be set to enable emails.
        """

        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_NAME: str
    USERS_OPEN_REGISTRATION: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """
        Class used to control the behavior of pydantic for the parent class
        (`Settings`).

        * `case_sensitive` enforces that environment variable names must match field
          names.
        * `env_file` specifies the path to the ".env" file to read the environment
          variables from.
        * `env_file_encoding` specifies the encoding for the ".env" file.
        """

        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "UTF-8"


settings = Settings()
