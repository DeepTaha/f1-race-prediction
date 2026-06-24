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

    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    # Model hyper-parameters (passed through to training)
    RF_N_ESTIMATORS: int = int(os.getenv("RF_N_ESTIMATORS", "100"))
    XGB_N_ESTIMATORS: int = int(os.getenv("XGB_N_ESTIMATORS", "100"))
    GB_N_ESTIMATORS: int = int(os.getenv("GB_N_ESTIMATORS", "100"))
    TEST_SIZE: float = float(os.getenv("TEST_SIZE", "0.2"))
    RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))


settings = Settings()
