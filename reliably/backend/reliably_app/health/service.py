from typing import Dict

from fastapi import APIRouter, FastAPI, status

from reliably_app.health import schemas

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: FastAPI) -> None:
    web.include_router(router, prefix="/health", include_in_schema=False)


@router.get(
    "",
    response_model=schemas.Health,
    status_code=status.HTTP_200_OK,
    description="Health of the application",
    tags=["Token"],
    summary="Health of the application",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Health,
            "description": "Ok Response",
        }
    },
)
async def index() -> Dict[str, str]:
    return {"status": "ok"}
