from pydantic import BaseModel
from typing import Literal


class PredictRequest(BaseModel):
    home_team: str
    away_team: str


class FormEntry(BaseModel):
    result: Literal["W", "D", "L"]
    goals_for: int
    goals_against: int
    opponent: str
    date: str


class PredictResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    prediction: Literal["Home Win", "Draw", "Away Win"]
    confidence: float
    home_form: list[FormEntry]
    away_form: list[FormEntry]


class TeamStanding(BaseModel):
    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: list[Literal["W", "D", "L"]]


class TeamStats(BaseModel):
    team: str
    season: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    points_per_game: float
    home_record: dict
    away_record: dict
    form: list[FormEntry]


class H2HRecord(BaseModel):
    home_team: str
    away_team: str
    matches: list[dict]
    home_wins: int
    draws: int
    away_wins: int
    home_goals: int
    away_goals: int
