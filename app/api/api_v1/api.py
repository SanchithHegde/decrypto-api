"""
Aggregates routers for all endpoints for the API version 1.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import login, questions, users, utils

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(questions.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
