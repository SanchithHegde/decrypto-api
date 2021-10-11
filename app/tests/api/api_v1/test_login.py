# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.tests.utils.utils import random_email, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_get_access_token(client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data
    )
    tokens = response.json()

    assert response.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


async def test_not_get_access_token(client: AsyncClient) -> None:
    login_data = {
        "username": random_email(),
        "password": random_lower_string(),
    }
    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data
    )

    assert response.status_code == 400


async def test_use_access_token(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = await client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = response.json()

    assert response.status_code == 200
    assert "email" in result
