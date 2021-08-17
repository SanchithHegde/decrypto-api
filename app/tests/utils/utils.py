# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

import random
import string
from typing import Dict

from httpx import AsyncClient

from app.core.config import settings


def random_int() -> int:
    return random.randint(1, 1_000_000)


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


async def get_superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data
    )
    tokens = response.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    return headers
