from fastapi import APIRouter, Depends

from src.api.dependencies import get_pipeline

router = APIRouter(tags=["Data"])


@router.get("/drivers")
def list_drivers(pipeline: dict = Depends(get_pipeline)):
    return {"drivers": pipeline["drivers"]}


@router.get("/tracks")
def list_tracks(pipeline: dict = Depends(get_pipeline)):
    return {"tracks": pipeline["tracks"]}


@router.get("/teams")
def list_teams(pipeline: dict = Depends(get_pipeline)):
    return {"teams": pipeline["teams"]}
