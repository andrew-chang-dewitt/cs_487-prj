"""Router for status endpoint at root."""

from fastapi import status as status_code
from fastapi.routing import APIRouter

from .types import Status

status = APIRouter(tags=["API Status"])


@status.get(
    "/",
    status_code=status_code.HTTP_200_OK,
    response_model=Status,
    summary="Check API status.",
)
async def get_status():
    """Check status of api service."""
    return Status()
