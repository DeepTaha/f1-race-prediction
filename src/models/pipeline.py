"""
ML pipeline: training orchestration and inference helpers.
Kept in src/models/ so it stays close to the model code it wraps.
"""

import os
import sys

import pandas as pd

# Ensure project root is on sys.path when running outside of uvicorn
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import settings
from src.data.data_loader import F1DataLoader
from src.data.feature_engineer import F1FeatureEngineer
from src.models.train_models import F1PredictionModel
from src.utils.helpers import get_logger, timed

logger = get_logger(__name__, settings.LOG_LEVEL)

FEATURE_COLS: list[str] = [
    "grid_position",
    "temperature",
    "fastest_lap",
    "recent_form",
    "driver_win_rate",
    "dnf_rate",
    "driver_track_avg",
    "team_track_avg",
    "position_change",
    "quali_strength",
    "driver_encoded",
    "team_encoded",
    "track_encoded",
    "weather_encoded",
]


@timed(logger)
def run_training_pipeline() -> dict:
    """Load data, engineer features, train all models, return populated state."""
    loader = F1DataLoader()
    df = loader.load_sample_data()

    fe = F1FeatureEngineer(df)
    processed = fe.get_processed_data()

    # Pre-compute lookup tables used during inference
    driver_stats = (
        processed.groupby("driver")[
            ["recent_form", "driver_win_rate", "dnf_rate", "quali_strength"]
        ]
        .mean()
        .to_dict("index")
    )
    track_driver_avgs = (
        processed.groupby(["driver", "track"])["driver_track_avg"].mean().to_dict()
    )
    track_team_avgs = (
        processed.groupby(["team", "track"])["team_track_avg"].mean().to_dict()
    )
    global_means = processed[FEATURE_COLS].mean().to_dict()

    X = processed[FEATURE_COLS]
    # XGBoost requires 0-indexed labels; shift finish_position (1–20) → (0–19)
    y = processed["finish_position"] - 1

    model = F1PredictionModel(X, y)
    model.train_all_models()

    feature_importances: list[dict] = []
    best = model.best_model
    if hasattr(best, "feature_importances_"):
        raw = best.feature_importances_
        total = raw.sum() or 1.0
        feature_importances = sorted(
            [
                {"feature": col, "importance": round(float(imp / total), 4)}
                for col, imp in zip(FEATURE_COLS, raw)
            ],
            key=lambda x: x["importance"],
            reverse=True,
        )

    logger.info(
        "Best model: %s | Accuracies: %s",
        model.best_model_name,
        {k: round(v, 4) for k, v in model.results.items()},
    )

    return {
        "model": model,
        "feature_engineer": fe,
        "driver_stats": driver_stats,
        "track_driver_avgs": track_driver_avgs,
        "track_team_avgs": track_team_avgs,
        "global_means": global_means,
        "drivers": sorted(processed["driver"].unique().tolist()),
        "tracks": sorted(processed["track"].unique().tolist()),
        "teams": sorted(processed["team"].unique().tolist()),
        "feature_importances": feature_importances,
        "is_trained": True,
    }


def _safe_encode(label_encoder, value: str, fallback: int = 0) -> int:
    try:
        return int(label_encoder.transform([value])[0])
    except ValueError:
        logger.warning("Unseen label '%s' — using fallback encoding %d", value, fallback)
        return fallback


def build_feature_vector(
    driver: str,
    team: str,
    track: str,
    grid_position: int,
    weather: str,
    temperature: int,
    pipeline: dict,
) -> pd.DataFrame:
    """Build a single-row feature DataFrame ready for the scaler + model."""
    fe: F1FeatureEngineer = pipeline["feature_engineer"]
    d = pipeline["driver_stats"].get(driver, {})
    means = pipeline["global_means"]

    row = {
        "grid_position": grid_position,
        "temperature": temperature,
        "fastest_lap": 0,
        "recent_form": d.get("recent_form", means["recent_form"]),
        "driver_win_rate": d.get("driver_win_rate", means["driver_win_rate"]),
        "dnf_rate": d.get("dnf_rate", means["dnf_rate"]),
        "driver_track_avg": pipeline["track_driver_avgs"].get(
            (driver, track), means["driver_track_avg"]
        ),
        "team_track_avg": pipeline["track_team_avgs"].get(
            (team, track), means["team_track_avg"]
        ),
        "position_change": 0,
        "quali_strength": d.get("quali_strength", means["quali_strength"]),
        "driver_encoded": _safe_encode(fe.le_driver, driver),
        "team_encoded": _safe_encode(fe.le_team, team),
        "track_encoded": _safe_encode(fe.le_track, track),
        "weather_encoded": _safe_encode(fe.le_weather, weather),
    }

    return pd.DataFrame([row], columns=FEATURE_COLS)


def run_inference(
    driver: str,
    team: str,
    track: str,
    grid_position: int,
    weather: str,
    temperature: int,
    pipeline: dict,
) -> dict:
    """Run a single prediction. Returns position + probabilities."""
    model: F1PredictionModel = pipeline["model"]
    X = build_feature_vector(driver, team, track, grid_position, weather, temperature, pipeline)
    X_scaled = model.scaler.transform(X)
    best = model.best_model

    # Shift back from 0-indexed label to finish position (1–20)
    predicted_position = int(best.predict(X_scaled)[0]) + 1

    win_prob = 0.0
    podium_prob = 0.0
    if hasattr(best, "predict_proba"):
        proba = best.predict_proba(X_scaled)[0]
        classes = list(best.classes_)
        win_prob = float(proba[classes.index(0)]) if 0 in classes else 0.0
        podium_prob = sum(
            float(proba[classes.index(p)]) for p in [0, 1, 2] if p in classes
        )

    return {
        "predicted_position": predicted_position,
        "win_probability": round(win_prob, 4),
        "podium_probability": round(podium_prob, 4),
        "model_used": model.best_model_name,
    }
