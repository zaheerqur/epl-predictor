"""
FastAPI application for EPL Match Outcome Predictor.

Endpoints:
  GET  /teams                           → list of all teams
  GET  /seasons                         → list of available seasons
  POST /predict                         → win/draw/loss probabilities
  GET  /standings?season=               → league table
  GET  /team/{name}?season=             → team stats
  GET  /h2h/{home_team}/{away_team}     → head-to-head history
"""
import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Allow running from repo root or api/ directory
sys.path.insert(0, str(Path(__file__).parent))

import predictor
from schemas import (H2HRecord, PredictRequest, PredictResponse,
                     TeamStanding, TeamStats)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

app = FastAPI(
    title="EPL Match Predictor",
    description="Gradient-boosted ML model trained on 10 seasons of EPL data.",
    version="1.0.0",
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/teams", response_model=list[str])
def get_teams():
    return predictor.list_teams()


@app.get("/seasons", response_model=list[str])
def get_seasons():
    return predictor.list_seasons()


@app.post("/predict", response_model=PredictResponse)
def post_predict(req: PredictRequest):
    try:
        return predictor.predict(req.home_team, req.away_team)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/standings", response_model=list[TeamStanding])
def get_standings(season: str | None = Query(default=None)):
    return predictor.standings(season)


@app.get("/team/{name}", response_model=TeamStats)
def get_team(name: str, season: str | None = Query(default=None)):
    try:
        return predictor.team_stats(name, season)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/h2h/{home_team}/{away_team}", response_model=H2HRecord)
def get_h2h(home_team: str, away_team: str):
    try:
        return predictor.h2h(home_team, away_team)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/model/info")
def get_model_info():
    return predictor.model_info()


@app.get("/validation")
def get_validation():
    try:
        return predictor.validation_data()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
