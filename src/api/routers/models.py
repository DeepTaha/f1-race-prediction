from typing import List

from fastapi import APIRouter, Depends, Request

from src.api.dependencies import get_pipeline
from src.api.schemas import FeatureImportance, ModelPerformance
from src.models.pipeline import run_training_pipeline

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=List[ModelPerformance])
def model_performance(pipeline: dict = Depends(get_pipeline)):
    model = pipeline["model"]
    return [
        ModelPerformance(name=name, accuracy=round(acc, 4))
        for name, acc in model.results.items()
    ]


@router.get("/features", response_model=List[FeatureImportance])
def feature_importance(pipeline: dict = Depends(get_pipeline)):
    return [FeatureImportance(**f) for f in pipeline["feature_importances"]]


@router.post("/train")
def retrain(request: Request):
    """Retrain all models from scratch and hot-swap the active pipeline."""
    new_pipeline = run_training_pipeline()
    request.app.state.pipeline = new_pipeline
    model = new_pipeline["model"]
    return {
        "message": "Models retrained successfully",
        "best_model": model.best_model_name,
        "results": {k: round(v, 4) for k, v in model.results.items()},
    }
