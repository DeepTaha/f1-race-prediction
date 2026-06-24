"""
ML pipeline: training orchestration, persistence, and inference helpers.
"""

import os
import sys

import joblib
import pandas as pd

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
    "quali_strength",
    "driver_encoded",
    "team_encoded",
    "track_encoded",
    "weather_encoded",
]


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_pipeline(state: dict) -> None:
    """Persist the trained pipeline dict to disk."""
    os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(state, settings.PIPELINE_ARTIFACT_PATH)
    logger.info("Pipeline saved → %s", settings.PIPELINE_ARTIFACT_PATH)


def load_cached_pipeline() -> dict | None:
    """Load a previously saved pipeline from disk. Returns None if not found or stale."""
    path = settings.PIPELINE_ARTIFACT_PATH
    if not os.path.exists(path):
        return None
    try:
        state = joblib.load(path)
        if not isinstance(state, dict) or not state.get("is_trained"):
            return None
        logger.info("Loaded cached pipeline from %s", path)
        return state
    except Exception as exc:
        logger.warning("Could not load cached pipeline (%s) — will retrain", exc)
        return None


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

@timed(logger)
def run_training_pipeline(
    force_retrain: bool = False,
    force_data_refresh: bool = False,
) -> dict:
    """
    Build or restore the full prediction pipeline.

    - If a saved pipeline exists and force_retrain is False, loads it from disk.
    - Otherwise loads data (from parquet cache or FastF1), engineers features,
      trains all models, selects the best, saves the pipeline, and returns it.
    """
    if not force_retrain:
        cached = load_cached_pipeline()
        if cached is not None:
            return cached

    logger.info(
        "Training pipeline (force_retrain=%s, force_data_refresh=%s)",
        force_retrain,
        force_data_refresh,
    )

    loader = F1DataLoader(
        cache_dir=settings.FASTF1_CACHE_DIR,
        data_path=settings.HISTORICAL_DATA_PATH,
    )
    df = loader.load_historical_data(
        years=settings.DATA_YEARS,
        force_refresh=force_data_refresh,
    )

    fe = F1FeatureEngineer(df)
    processed = fe.get_processed_data()

    # Lookup tables used at inference time to fill per-driver / per-track stats
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

    # Sort chronologically so the train/test split respects time order
    processed = processed.sort_values("race_id").reset_index(drop=True)

    X = processed[FEATURE_COLS]
    y = processed["finish_position"] - 1  # XGBoost expects 0-indexed labels

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

    state = {
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
        "training_rows": len(processed),
        "data_source": "FastF1" if os.path.exists(settings.HISTORICAL_DATA_PATH) else "synthetic",
    }

    save_pipeline(state)
    return state


# ---------------------------------------------------------------------------
# Inference helpers
# ---------------------------------------------------------------------------

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

    predicted_position = int(best.predict(X_scaled)[0]) + 1  # shift back from 0-index

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
