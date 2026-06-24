"""
FastAPI dependency: injects the trained pipeline state into route handlers.
"""

from fastapi import HTTPException, Request


def get_pipeline(request: Request) -> dict:
    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None or not pipeline.get("is_trained"):
        raise HTTPException(status_code=503, detail="Models not yet trained")
    return pipeline
