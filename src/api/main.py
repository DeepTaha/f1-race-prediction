"""
F1 Race Prediction API — entry point.

Run from project root:
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import data, info, models, predict
from src.config import settings
from src.models.pipeline import run_training_pipeline
from src.utils.helpers import get_logger

logger = get_logger(__name__, settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s — training models...", settings.APP_NAME, settings.VERSION)
    app.state.pipeline = run_training_pipeline()
    logger.info("Ready. Docs → http://%s:%s/docs", settings.HOST, settings.PORT)
    yield
    del app.state.pipeline
    logger.info("Shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(info.router)
app.include_router(data.router)
app.include_router(models.router)
app.include_router(predict.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host=settings.HOST, port=settings.PORT, reload=True)
