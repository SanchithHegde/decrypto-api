# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=redefined-outer-name

import logging
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_db_session
from app.core.config import settings
from app.db.base_class import Base
from app.db.init_db import init_db
from app.logging_config import logging_dict_config
from app.main import app
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers

logging.config.dictConfig(logging_dict_config)
LOGGER = logging.getLogger(__name__)

# Use separate database for testing
assert settings.SQLALCHEMY_TEST_DATABASE_URI

engine = create_engine(
    settings.SQLALCHEMY_TEST_DATABASE_URI, pool_pre_ping=True, future=True
)
TestingSessionLocal = sessionmaker(autoflush=False, bind=engine, future=True)


def override_get_db_session() -> Generator:
    try:
        db_session = TestingSessionLocal()
        yield db_session

    finally:
        db_session.close()


@pytest.fixture(scope="session", autouse=True)
def create_tables() -> Generator:
    LOGGER.info("Creating tables")
    Base.metadata.create_all(bind=engine)  # pylint: disable=no-member
    LOGGER.info("Tables created")

    # Dependency overrides
    # Reference: https://fastapi.tiangolo.com/advanced/testing-database/
    app.dependency_overrides[get_db_session] = override_get_db_session

    LOGGER.info("Creating initial data")
    db_session = TestingSessionLocal()
    init_db(db_session)
    LOGGER.info("Initial data created")

    # Run tests
    yield

    LOGGER.info("Clearing data in tables")
    for table in reversed(Base.metadata.sorted_tables):  # pylint: disable=no-member
        db_session.execute(table.delete())
    db_session.commit()
    LOGGER.info("Tables cleared")


@pytest.fixture(scope="session")
def db_session() -> Generator:
    yield TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(
    client: TestClient, db_session: Session
) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db_session=db_session
    )
