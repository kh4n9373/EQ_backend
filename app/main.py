import asyncio
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import REGISTRY
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.api import router
from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging_config import setup_logging
from app.core.metrics_updater import start_metrics_updater

logger = logging.getLogger(__name__)

setup_logging()

app = FastAPI(
    title="EmoStagram API",
    version="1.0.0",
    description="Emotional Intelligence Instagram API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin,
    allow_credentials=True,  # Fixed typo: credentals -> credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    should_instrument_requests_inprogress=True,
)
instrumentator.instrument(app)
instrumentator.expose(app)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "errors": [str(exc)],
            "details": {"type": type(exc).__name__},
        },
    )


@app.get("/health")
def health_check():
    return {"success": True, "message": "Healthy", "data": {"status": "ok"}}


@app.get("/health/db")
def db_health_check():
    try:
        from app.core.database import engine

        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
            return {
                "success": True,
                "message": "Database healthy",
                "data": {"status": "connected"},
            }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "Database unhealthy",
                "data": {"error": str(e)},
            },
        )


app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info("Application_starting...")
    asyncio.create_task(start_metrics_updater())


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5001, reload=True)
