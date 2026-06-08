"""
Prediction engine: loads model artifacts once at startup, serves predictions.

For a given (home_team, away_team) pair, features are computed from the team's
most recent matches in the dataset — simulating what the model would see if the
match were played today.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from schemas import FormEntry, H2HRecord, PredictResponse, TeamStanding, TeamStats

log = logging.getLogger(__name__)

ROOT       = Path(__file__).parent.parent
MODELS_DIR = ROOT / "models"
DATA_DIR   = ROOT / "data" / "processed"

LABEL_MAP = {"H": "Home Win", "D": "Draw", "A": "Away Win"}


@lru_cache(maxsize=1)
def _load() -> tuple:
    """Load model + data once; cached for process lifetime."""
    model    = joblib.load(MODELS_DIR / "model.joblib")
    feat_cols = joblib.load(MODELS_DIR / "feature_cols.joblib")
    meta     = json.loads((MODELS_DIR / "meta.json").read_text())
    matches  = pd.read_parquet(DATA_DIR / "matches.parquet")
    features = pd.read_parquet(DATA_DIR / "features.parquet")

    # Sort once, keep latest season name
    matches  = matches.sort_values("Date").reset_index(drop=True)
    features = features.sort_values("Date").reset_index(drop=True)

    return model, feat_cols, meta, matches, features


def _latest_form(matches: pd.DataFrame, team: str, n: int = 5) -> list[FormEntry]:
    """Return last n match results for a team as FormEntry objects."""
    mask = (matches["HomeTeam"] == team) | (matches["AwayTeam"] == team)
    team_matches = matches[mask].sort_values("Date").tail(n)
    form = []
    for _, row in team_matches.iterrows():
        is_home = row["HomeTeam"] == team
        gf = int(row["FTHG"]) if is_home else int(row["FTAG"])
        ga = int(row["FTAG"]) if is_home else int(row["FTHG"])
        opp = row["AwayTeam"] if is_home else row["HomeTeam"]
        ftr = row["FTR"]
        if is_home:
            result = "W" if ftr == "H" else ("D" if ftr == "D" else "L")
        else:
            result = "W" if ftr == "A" else ("D" if ftr == "D" else "L")
        form.append(FormEntry(result=result, goals_for=gf, goals_against=ga,
                               opponent=opp, date=row["Date"].strftime("%Y-%m-%d")))
    return form


def _live_features(features: pd.DataFrame, home_team: str, away_team: str,
                   feat_cols: list[str]) -> np.ndarray:
    """
    Compute features for a hypothetical match by taking the latest available
    feature row where each team appears (home or away).
    """
    # Latest row where home_team was HOME — captures their home-perspective features
    home_rows = features[features["HomeTeam"] == home_team]
    away_rows = features[features["AwayTeam"] == away_team]

    if home_rows.empty or away_rows.empty:
        return np.full((1, len(feat_cols)), np.nan)

    home_row = home_rows.iloc[-1]
    away_row = away_rows.iloc[-1]

    # Build feature vector by picking home_* from the home team's last match
    # and away_* from the away team's last match, then recompute diffs.
    feat_vec = {}
    for col in feat_cols:
        if col.startswith("home_"):
            feat_vec[col] = home_row.get(col, np.nan)
        elif col.startswith("away_"):
            feat_vec[col] = away_row.get(col, np.nan)
        elif col.startswith("diff_"):
            base = col[5:]          # strip "diff_"
            feat_vec[col] = home_row.get(f"home_{base}", np.nan) - away_row.get(f"away_{base}", np.nan)
        elif col.startswith("h2h_"):
            # H2H from the perspective of the most recent direct meeting
            feat_vec[col] = home_row.get(col, np.nan)
        else:
            feat_vec[col] = home_row.get(col, np.nan)

    return np.array([[feat_vec.get(c, np.nan) for c in feat_cols]])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict(home_team: str, away_team: str) -> PredictResponse:
    model, feat_cols, meta, matches, features = _load()

    teams = set(meta["teams"])
    if home_team not in teams:
        raise ValueError(f"Unknown team: {home_team}")
    if away_team not in teams:
        raise ValueError(f"Unknown team: {away_team}")

    X = _live_features(features, home_team, away_team, feat_cols)
    proba = model.predict_proba(X)[0]

    classes     = meta["classes"]
    proba_idx   = meta["proba_idx"]
    h_prob = float(proba[proba_idx["H"]])
    d_prob = float(proba[proba_idx["D"]])
    a_prob = float(proba[proba_idx["A"]])

    pred_class  = classes[int(np.argmax(proba))]
    confidence  = float(np.max(proba))

    return PredictResponse(
        home_team=home_team,
        away_team=away_team,
        home_win_prob=round(h_prob, 4),
        draw_prob=round(d_prob, 4),
        away_win_prob=round(a_prob, 4),
        prediction=LABEL_MAP[pred_class],
        confidence=round(confidence, 4),
        home_form=_latest_form(matches, home_team),
        away_form=_latest_form(matches, away_team),
    )


def standings(season: str | None = None) -> list[TeamStanding]:
    _, _, meta, matches, _ = _load()
    if season is None:
        season = matches["Season"].iloc[-1]

    df = matches[matches["Season"] == season]
    table: dict[str, dict] = {}

    for _, row in df.iterrows():
        ht, at = row["HomeTeam"], row["AwayTeam"]
        hg, ag = int(row["FTHG"]), int(row["FTAG"])
        ftr = row["FTR"]

        for team, gf, ga, is_home in [(ht, hg, ag, True), (at, ag, hg, False)]:
            if team not in table:
                table[team] = dict(played=0, won=0, drawn=0, lost=0,
                                   gf=0, ga=0, pts=0, results=[])
            t = table[team]
            t["played"] += 1
            t["gf"] += gf
            t["ga"] += ga
            win_cond  = (is_home and ftr == "H") or (not is_home and ftr == "A")
            draw_cond = ftr == "D"
            if win_cond:
                t["won"]  += 1; t["pts"] += 3; t["results"].append("W")
            elif draw_cond:
                t["drawn"] += 1; t["pts"] += 1; t["results"].append("D")
            else:
                t["lost"] += 1; t["results"].append("L")

    rows = []
    for team, s in table.items():
        rows.append({**s, "team": team, "gd": s["gf"] - s["ga"]})

    rows.sort(key=lambda r: (-r["pts"], -r["gd"], -r["gf"]))

    return [
        TeamStanding(
            position=i + 1,
            team=r["team"],
            played=r["played"],
            won=r["won"],
            drawn=r["drawn"],
            lost=r["lost"],
            goals_for=r["gf"],
            goals_against=r["ga"],
            goal_difference=r["gd"],
            points=r["pts"],
            form=r["results"][-5:],
        )
        for i, r in enumerate(rows)
    ]


def team_stats(team: str, season: str | None = None) -> TeamStats:
    _, _, meta, matches, _ = _load()
    if season is None:
        season = matches["Season"].iloc[-1]

    teams = set(meta["teams"])
    if team not in teams:
        raise ValueError(f"Unknown team: {team}")

    df = matches[matches["Season"] == season]
    mask = (df["HomeTeam"] == team) | (df["AwayTeam"] == team)
    team_df = df[mask].sort_values("Date")

    stats = dict(played=0, won=0, drawn=0, lost=0, gf=0, ga=0, pts=0)
    home_rec = dict(played=0, won=0, drawn=0, lost=0, gf=0, ga=0, pts=0)
    away_rec = dict(played=0, won=0, drawn=0, lost=0, gf=0, ga=0, pts=0)
    form_entries = []

    for _, row in team_df.iterrows():
        is_home = row["HomeTeam"] == team
        gf = int(row["FTHG"]) if is_home else int(row["FTAG"])
        ga = int(row["FTAG"]) if is_home else int(row["FTHG"])
        opp = row["AwayTeam"] if is_home else row["HomeTeam"]
        ftr = row["FTR"]
        win  = (is_home and ftr == "H") or (not is_home and ftr == "A")
        draw = ftr == "D"
        pts_earned = 3 if win else (1 if draw else 0)
        result_char = "W" if win else ("D" if draw else "L")

        for d in [stats, home_rec if is_home else away_rec]:
            d["played"] += 1
            d["gf"] += gf
            d["ga"] += ga
            d["pts"] += pts_earned
            if win:   d["won"]   += 1
            elif draw: d["drawn"] += 1
            else:     d["lost"]  += 1

        form_entries.append(FormEntry(
            result=result_char, goals_for=gf, goals_against=ga,
            opponent=opp, date=row["Date"].strftime("%Y-%m-%d")
        ))

    ppg = round(stats["pts"] / stats["played"], 2) if stats["played"] else 0.0

    return TeamStats(
        team=team,
        season=season,
        played=stats["played"],
        won=stats["won"],
        drawn=stats["drawn"],
        lost=stats["lost"],
        goals_for=stats["gf"],
        goals_against=stats["ga"],
        goal_difference=stats["gf"] - stats["ga"],
        points=stats["pts"],
        points_per_game=ppg,
        home_record=home_rec,
        away_record=away_rec,
        form=form_entries[-5:],
    )


def h2h(home_team: str, away_team: str) -> H2HRecord:
    _, _, meta, matches, _ = _load()
    teams = set(meta["teams"])
    for t in [home_team, away_team]:
        if t not in teams:
            raise ValueError(f"Unknown team: {t}")

    mask = (
        ((matches["HomeTeam"] == home_team) & (matches["AwayTeam"] == away_team)) |
        ((matches["HomeTeam"] == away_team) & (matches["AwayTeam"] == home_team))
    )
    meetings = matches[mask].sort_values("Date", ascending=False)

    hw = d = aw = hg = ag = 0
    records = []
    for _, row in meetings.iterrows():
        if row["HomeTeam"] == home_team:
            h_goals, a_goals = int(row["FTHG"]), int(row["FTAG"])
            result = row["FTR"]
        else:
            h_goals, a_goals = int(row["FTAG"]), int(row["FTHG"])
            result = "H" if row["FTR"] == "A" else ("A" if row["FTR"] == "H" else "D")
        hg += h_goals; ag += a_goals
        if result == "H":   hw += 1
        elif result == "D": d  += 1
        else:               aw += 1
        records.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "season": row["Season"],
            "home_goals": h_goals,
            "away_goals": a_goals,
            "result": result,
        })

    return H2HRecord(
        home_team=home_team,
        away_team=away_team,
        matches=records[:10],
        home_wins=hw,
        draws=d,
        away_wins=aw,
        home_goals=hg,
        away_goals=ag,
    )


@lru_cache(maxsize=1)
def validation_data() -> dict:
    """Load validation.json once; cached for process lifetime."""
    path = MODELS_DIR / "validation.json"
    if not path.exists():
        raise FileNotFoundError("Run pipeline.py first — validation.json not found")
    return json.loads(path.read_text())


def list_teams() -> list[str]:
    _, _, meta, _, _ = _load()
    return sorted(meta["teams"])


def list_seasons() -> list[str]:
    _, _, _, matches, _ = _load()
    return sorted(matches["Season"].unique().tolist())


# Human-readable feature labels for the pipeline view
_FEAT_LABELS = {
    "home_pts_roll5":      "Home form — pts (last 5)",
    "home_pts_roll10":     "Home form — pts (last 10)",
    "home_gf_roll5":       "Home goals scored (last 5)",
    "home_gf_roll10":      "Home goals scored (last 10)",
    "home_ga_roll5":       "Home goals conceded (last 5)",
    "home_ga_roll10":      "Home goals conceded (last 10)",
    "home_sot_roll5":      "Home shots on target (last 5)",
    "home_sot_roll10":     "Home shots on target (last 10)",
    "away_pts_roll5":      "Away form — pts (last 5)",
    "away_pts_roll10":     "Away form — pts (last 10)",
    "away_gf_roll5":       "Away goals scored (last 5)",
    "away_gf_roll10":      "Away goals scored (last 10)",
    "away_ga_roll5":       "Away goals conceded (last 5)",
    "away_ga_roll10":      "Away goals conceded (last 10)",
    "away_sot_roll5":      "Away shots on target (last 5)",
    "away_sot_roll10":     "Away shots on target (last 10)",
    "home_season_pts_pg":  "Home season pts/game",
    "home_season_gd":      "Home season goal difference",
    "away_season_pts_pg":  "Away season pts/game",
    "away_season_gd":      "Away season goal difference",
    "diff_pts_roll5":      "Form differential (last 5)",
    "diff_pts_roll10":     "Form differential (last 10)",
    "diff_gf_roll5":       "Goals scored differential (5g)",
    "diff_ga_roll5":       "Goals conceded differential (5g)",
    "diff_season_pts_pg":  "Season pts/game differential",
    "diff_season_gd":      "Season GD differential",
    "h2h_hw":              "H2H home win rate",
    "h2h_d":               "H2H draw rate",
    "h2h_aw":              "H2H away win rate",
    "h2h_n":               "H2H meetings (count)",
}


def model_info() -> dict:
    model, feat_cols, meta, matches, _ = _load()

    # Permutation importances saved during training
    raw_importance = meta.get("feature_importance", [])
    feat_importance = [
        {"feature": fi["feature"],
         "label": _FEAT_LABELS.get(fi["feature"], fi["feature"]),
         "importance": fi["importance"]}
        for fi in raw_importance[:15]
        if fi["importance"] > 0
    ]

    # Distribution of outcomes across full dataset
    ftr = matches["FTR"].value_counts()
    baseline = {k: round(int(v) / len(matches), 4) for k, v in ftr.items()}

    return {
        "total_matches":    len(matches),
        "seasons":          sorted(matches["Season"].unique().tolist()),
        "n_seasons":        matches["Season"].nunique(),
        "n_features":       len(feat_cols),
        "train_seasons":    meta["train_seasons"],
        "test_seasons":     meta["test_seasons"],
        "test_accuracy":    meta["test_accuracy"],
        "test_log_loss":    meta["test_log_loss"],
        "baseline_home":    baseline.get("H", 0),
        "baseline_draw":    baseline.get("D", 0),
        "baseline_away":    baseline.get("A", 0),
        "feature_importance": feat_importance,
        "model_type":       "HistGradientBoostingClassifier + Isotonic Calibration",
        "pipeline_steps": [
            {"name": "Ingest",    "detail": f"{len(matches):,} matches - {matches['Season'].nunique()} seasons - football-data.co.uk"},
            {"name": "Features",  "detail": f"{len(feat_cols)} engineered features - rolling windows - H2H - temporal split"},
            {"name": "Train",     "detail": f"HistGBM - cv=5 calibration - {len(meta['train_seasons'])} train seasons"},
            {"name": "Serve",     "detail": "FastAPI - 6 endpoints - CORS - Pydantic validation"},
            {"name": "Deploy",    "detail": "Docker - docker-compose - Netlify (frontend) - Render (API)"},
        ],
    }
