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
from src.data.data_loader import get_next_race
from src.models.pipeline import run_inference

router = APIRouter(prefix="/predict", tags=["Prediction"])

# ---------------------------------------------------------------------------
# 2025 full driver lineup — used when no qualifying data is available yet
# driver = abbreviation (matches training data), name = display name
# ---------------------------------------------------------------------------
_GRID_2025 = [
    {"driver": "VER", "name": "Max Verstappen",    "team": "Red Bull",     "grid_position": 1},
    {"driver": "LAW", "name": "Liam Lawson",       "team": "Red Bull",     "grid_position": 2},
    {"driver": "NOR", "name": "Lando Norris",      "team": "McLaren",      "grid_position": 3},
    {"driver": "PIA", "name": "Oscar Piastri",     "team": "McLaren",      "grid_position": 4},
    {"driver": "LEC", "name": "Charles Leclerc",   "team": "Ferrari",      "grid_position": 5},
    {"driver": "HAM", "name": "Lewis Hamilton",    "team": "Ferrari",      "grid_position": 6},
    {"driver": "RUS", "name": "George Russell",    "team": "Mercedes",     "grid_position": 7},
    {"driver": "ANT", "name": "Kimi Antonelli",    "team": "Mercedes",     "grid_position": 8},
    {"driver": "ALO", "name": "Fernando Alonso",   "team": "Aston Martin", "grid_position": 9},
    {"driver": "STR", "name": "Lance Stroll",      "team": "Aston Martin", "grid_position": 10},
    {"driver": "GAS", "name": "Pierre Gasly",      "team": "Alpine",       "grid_position": 11},
    {"driver": "COL", "name": "Franco Colapinto",  "team": "Alpine",       "grid_position": 12},
    {"driver": "ALB", "name": "Alex Albon",        "team": "Williams",     "grid_position": 13},
    {"driver": "SAI", "name": "Carlos Sainz",      "team": "Williams",     "grid_position": 14},
    {"driver": "OCO", "name": "Esteban Ocon",      "team": "Haas",         "grid_position": 15},
    {"driver": "BEA", "name": "Oliver Bearman",    "team": "Haas",         "grid_position": 16},
    {"driver": "HUL", "name": "Nico Hulkenberg",   "team": "Sauber",       "grid_position": 17},
    {"driver": "BOR", "name": "Gabriel Bortoleto", "team": "Sauber",       "grid_position": 18},
    {"driver": "TSU", "name": "Yuki Tsunoda",      "team": "RB",           "grid_position": 19},
    {"driver": "HAD", "name": "Isack Hadjar",      "team": "RB",           "grid_position": 20},
]

# Static fallback when FastF1 schedule is unreachable
_FALLBACK_RACE = {
    "race": "Abu Dhabi Grand Prix",
    "circuit": "Yas Marina Circuit",
    "season": 2025,
    "round": 24,
    "track": "Abu Dhabi",
    "weather": "Dry",
    "temperature": 29,
}


def _resolve_default_race() -> dict:
    """Return the next upcoming race. Falls back to the Abu Dhabi GP if none found."""
    dynamic = get_next_race()
    return dynamic if dynamic is not None else dict(_FALLBACK_RACE)


@router.get("/latest", tags=["Prediction"])
def predict_latest(pipeline: dict = Depends(get_pipeline)):
    """Predict race outcomes for the next upcoming Grand Prix (full 20-car grid)."""
    race = _resolve_default_race()

    predictions = []
    for entry in _GRID_2025:
        result = run_inference(
            entry["driver"], entry["team"], race["track"],
            entry["grid_position"], race["weather"], race["temperature"],
            pipeline,
        )
        predictions.append({
            "driver":             entry["driver"],
            "driver_code":        entry["driver"],
            "driver_name":        entry["name"],
            "team":               entry["team"],
            "grid_position":      entry["grid_position"],
            "predicted_position": result["predicted_position"],
            "win_probability":    result["win_probability"],
            "podium_probability": result["podium_probability"],
        })

    predictions.sort(key=lambda x: x["predicted_position"])
    for i, p in enumerate(predictions):
        p["position"] = i + 1

    return {
        "race":        race["race"],
        "circuit":     race["circuit"],
        "season":      race["season"],
        "round":       race["round"],
        "timestamp":   datetime.now().isoformat(),
        "predictions": predictions,
        "model_used":  pipeline["model"].best_model_name,
        "data_source": pipeline.get("data_source", "unknown"),
        "training_rows": pipeline.get("training_rows", 0),
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
