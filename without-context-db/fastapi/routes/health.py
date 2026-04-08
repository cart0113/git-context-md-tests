from fastapi.routing import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
