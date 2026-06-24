"""
Pydantic request/response schemas for the F1 Prediction API.
"""

from typing import List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    driver: str = Field(..., examples=["Verstappen"])
    team: str = Field(..., examples=["Red Bull"])
    track: str = Field(..., examples=["Monza"])
    grid_position: int = Field(..., ge=1, le=20, examples=[3])
    weather: str = Field("Dry", examples=["Dry"])
    temperature: int = Field(25, ge=10, le=45, examples=[28])


class PredictResponse(BaseModel):
    driver: str
    team: str
    track: str
    grid_position: int
    predicted_position: int
    win_probability: float
    podium_probability: float
    model_used: str
    timestamp: str


class BatchPredictRequest(BaseModel):
    drivers: List[PredictRequest]


class BatchPredictItem(BaseModel):
    driver: str
    grid_position: int
    predicted_position: int
    win_probability: float
    podium_probability: float


class BatchPredictResponse(BaseModel):
    predictions: List[BatchPredictItem]
    total_drivers: int
    best_model: str
    timestamp: str


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ModelPerformance(BaseModel):
    name: str
    accuracy: float


class FeatureImportance(BaseModel):
    feature: str
    importance: float


# ---------------------------------------------------------------------------
# Info
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    models_trained: bool
    version: str
    timestamp: str
