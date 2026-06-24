from typing import List

from fastapi import APIRouter, Depends, Query, Request

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
def retrain(
    request: Request,
    refresh_data: bool = Query(
        False,
        description="Re-download race data from FastF1 before retraining (slow on first run).",
    ),
):
    """Retrain all models and hot-swap the active pipeline.
    Pass ?refresh_data=true to also re-fetch historical data from FastF1.
    """
    new_pipeline = run_training_pipeline(force_retrain=True, force_data_refresh=refresh_data)
    request.app.state.pipeline = new_pipeline
    model = new_pipeline["model"]
    return {
        "message": "Models retrained successfully",
        "best_model": model.best_model_name,
        "results": {k: round(v, 4) for k, v in model.results.items()},
        "training_rows": new_pipeline.get("training_rows", 0),
        "data_source": new_pipeline.get("data_source", "unknown"),
    }
