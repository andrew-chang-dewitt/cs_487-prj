"""Router for status endpoint at root."""

from dataclasses import dataclass

from fastapi import status as status_code
from fastapi.routing import APIRouter

from src.context import Context


@dataclass
class Status:
    """Status Response."""

    # pylint: disable=too-few-public-methods

    message: str = "The API is up."
    ok: bool = True


def create_status(_ctx: Context) -> APIRouter:
    """Create a account router & model with access to the given database."""
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

    return status
