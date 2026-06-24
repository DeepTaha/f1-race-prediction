"""
Central configuration — all tunables in one place.
Override any value with an environment variable.
"""

import os


class Settings:
    APP_NAME: str = "F1 Race Prediction API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "ML-powered Formula 1 race outcome predictions."

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    ARTIFACTS_DIR: str = os.getenv("ARTIFACTS_DIR", "artifacts")
    DATASET_DIR: str = os.getenv("DATASET_DIR", "dataset")

    # FastF1 / historical data
    FASTF1_CACHE_DIR: str = os.getenv("FASTF1_CACHE_DIR", "dataset/fastf1_cache")
    HISTORICAL_DATA_PATH: str = os.getenv("HISTORICAL_DATA_PATH", "dataset/historical_data.parquet")
    _data_years_raw: str = os.getenv("DATA_YEARS", "2021,2022,2023,2024,2025,2026")
    DATA_YEARS: list = [int(y.strip()) for y in _data_years_raw.split(",")]

    # Set to "true" to re-download FastF1 data even if parquet cache exists
    FORCE_DATA_REFRESH: bool = os.getenv("FORCE_DATA_REFRESH", "false").lower() == "true"
    # Set to "true" to retrain models even if artifacts/pipeline.pkl exists
    FORCE_RETRAIN: bool = os.getenv("FORCE_RETRAIN", "false").lower() == "true"

    # Saved pipeline artifact (models + encoders + lookup tables)
    PIPELINE_ARTIFACT_PATH: str = os.getenv("PIPELINE_ARTIFACT_PATH", "artifacts/pipeline.pkl")

    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Model hyper-parameters
    RF_N_ESTIMATORS: int = int(os.getenv("RF_N_ESTIMATORS", "100"))
    XGB_N_ESTIMATORS: int = int(os.getenv("XGB_N_ESTIMATORS", "100"))
    GB_N_ESTIMATORS: int = int(os.getenv("GB_N_ESTIMATORS", "100"))
    TEST_SIZE: float = float(os.getenv("TEST_SIZE", "0.2"))
    RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))


settings = Settings()
