from fastapi import routing
from fastapi.responses import JSONResponse

router = routing.APIRouter()


@router.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
