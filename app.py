from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config import settings
from api.api import api_router
from utils.logging import logger
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("AI Incident Triage API starting up...")
    yield
    logger.info("AI Incident Triage API shutting down...")

def create_application()->FastAPI:
    app= FastAPI(
         title=settings.title,
        lifespan=lifespan
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "status_code": 500}
        )
    
    return app


app = create_application()

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host=settings.host, port=port)
