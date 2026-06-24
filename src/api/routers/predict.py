from datetime import datetime

from fastapi import APIRouter, Depends

from src.api.dependencies import get_pipeline
from src.api.schemas import (
    BatchPredictItem,
    BatchPredictRequest,
    BatchPredictResponse,
    PredictRequest,
    PredictResponse,
)
from src.models.pipeline import run_inference

router = APIRouter(prefix="/predict", tags=["Prediction"])

# ---------------------------------------------------------------------------
# Default race used by GET /predict/latest (Abu Dhabi GP 2025)
# ---------------------------------------------------------------------------
_DEFAULT_RACE = {
    "race": "Abu Dhabi Grand Prix",
    "circuit": "Yas Marina Circuit",
    "season": 2025,
    "round": 24,
    "track": "Abu Dhabi",
    "weather": "Dry",
    "temperature": 29,
}

_DEFAULT_GRID = [
    {"driver": "Verstappen", "team": "Red Bull",     "code": "VER", "grid_position": 1},
    {"driver": "Norris",     "team": "McLaren",       "code": "NOR", "grid_position": 2},
    {"driver": "Piastri",    "team": "McLaren",       "code": "PIA", "grid_position": 3},
    {"driver": "Leclerc",    "team": "Ferrari",       "code": "LEC", "grid_position": 4},
    {"driver": "Hamilton",   "team": "Ferrari",       "code": "HAM", "grid_position": 5},
    {"driver": "Russell",    "team": "Mercedes",      "code": "RUS", "grid_position": 6},
    {"driver": "Sainz",      "team": "Ferrari",       "code": "SAI", "grid_position": 7},
    {"driver": "Perez",      "team": "Red Bull",      "code": "PER", "grid_position": 8},
    {"driver": "Alonso",     "team": "Aston Martin",  "code": "ALO", "grid_position": 9},
    {"driver": "Stroll",     "team": "Aston Martin",  "code": "STR", "grid_position": 10},
]


@router.get("/latest", tags=["Prediction"])
def predict_latest(pipeline: dict = Depends(get_pipeline)):
    """Run predictions for the default race grid — consumed by the dashboard."""
    predictions = []
    for entry in _DEFAULT_GRID:
        result = run_inference(
            entry["driver"], entry["team"], _DEFAULT_RACE["track"],
            entry["grid_position"], _DEFAULT_RACE["weather"], _DEFAULT_RACE["temperature"],
            pipeline,
        )
        predictions.append({
            "driver":             entry["driver"],
            "driver_code":        entry["code"],
            "team":               entry["team"],
            "grid_position":      entry["grid_position"],
            "predicted_position": result["predicted_position"],
            "win_probability":    result["win_probability"],
            "podium_probability": result["podium_probability"],
        })

    predictions.sort(key=lambda x: x["predicted_position"])
    # Re-index to remove ties in display order
    for i, p in enumerate(predictions):
        p["position"] = i + 1

    return {
        "race":       _DEFAULT_RACE["race"],
        "circuit":    _DEFAULT_RACE["circuit"],
        "season":     _DEFAULT_RACE["season"],
        "round":      _DEFAULT_RACE["round"],
        "timestamp":  datetime.now().isoformat(),
        "predictions": predictions,
        "model_used": pipeline["model"].best_model_name,
    }


@router.post("", response_model=PredictResponse)
def predict(req: PredictRequest, pipeline: dict = Depends(get_pipeline)):
    result = run_inference(
        req.driver, req.team, req.track,
        req.grid_position, req.weather, req.temperature,
        pipeline,
    )
    return PredictResponse(
        driver=req.driver,
        team=req.team,
        track=req.track,
        grid_position=req.grid_position,
        predicted_position=result["predicted_position"],
        win_probability=result["win_probability"],
        podium_probability=result["podium_probability"],
        model_used=result["model_used"],
        timestamp=datetime.now().isoformat(),
    )


@router.post("/batch", response_model=BatchPredictResponse)
def batch_predict(req: BatchPredictRequest, pipeline: dict = Depends(get_pipeline)):
    items = []
    for driver_req in req.drivers:
        result = run_inference(
            driver_req.driver, driver_req.team, driver_req.track,
            driver_req.grid_position, driver_req.weather, driver_req.temperature,
            pipeline,
        )
        items.append(
            BatchPredictItem(
                driver=driver_req.driver,
                grid_position=driver_req.grid_position,
                predicted_position=result["predicted_position"],
                win_probability=result["win_probability"],
                podium_probability=result["podium_probability"],
            )
        )

    items.sort(key=lambda x: x.predicted_position)

    return BatchPredictResponse(
        predictions=items,
        total_drivers=len(items),
        best_model=pipeline["model"].best_model_name,
        timestamp=datetime.now().isoformat(),
    )
