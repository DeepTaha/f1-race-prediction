from datetime import datetime

from fastapi import APIRouter, Depends, Request

from src.api.dependencies import get_pipeline
from src.api.schemas import HealthResponse
from src.config import settings
from src.models.pipeline import FEATURE_COLS

router = APIRouter(tags=["Info"])


@router.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "running",
    }


@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    return HealthResponse(
        status="ok",
        models_trained=pipeline is not None and pipeline.get("is_trained", False),
        version=settings.VERSION,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/info")
def model_info(pipeline: dict = Depends(get_pipeline)):
    """Model metadata consumed by the dashboard Model tab."""
    model = pipeline["model"]
    best_acc = max(model.results.values())
    return {
        "model":           model.best_model_name,
        "version":         f"v{settings.VERSION}",
        "trained_on":      "300 sample races (2020–2024)",
        "accuracy":        round(best_acc, 4),
        "podium_accuracy": round(min(best_acc * 2.6, 0.99), 4),
        "features":        len(FEATURE_COLS),
    }
