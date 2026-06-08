"""
Pre-compute model predictions for every match in the held-out validation season (the latest season in the dataset).

Features in features.parquet are already computed with shift(1) so they reflect
the pre-match state — no data leakage. We simply run model.predict_proba on those rows.

Output: models/validation.json
"""
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

ROOT       = Path(__file__).parent.parent
MODELS_DIR = ROOT / "models"
DATA_DIR   = ROOT / "data" / "processed"

def validate() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # ── Load artifacts ──────────────────────────────────────────────────────
    model_path = MODELS_DIR / "model.joblib"
    feat_path  = MODELS_DIR / "feature_cols.joblib"
    meta_path  = MODELS_DIR / "meta.json"

    if not model_path.exists():
        raise FileNotFoundError("Run train.py first — model.joblib not found")

    model     = joblib.load(model_path)
    feat_cols = joblib.load(feat_path)
    meta      = json.loads(meta_path.read_text())

    proba_idx = meta["proba_idx"]   # {"H": 0, "D": 1, "A": 2} (or similar)
    h_idx = proba_idx["H"]
    d_idx = proba_idx["D"]
    a_idx = proba_idx["A"]

    # ── Load feature matrix ─────────────────────────────────────────────────
    features = pd.read_parquet(DATA_DIR / "features.parquet")
    VALIDATION_SEASON = features["Season"].max()
    val_df = features[features["Season"] == VALIDATION_SEASON].copy()
    val_df = val_df.sort_values("Date").reset_index(drop=True)

    if val_df.empty:
        raise ValueError(f"No matches found for season {VALIDATION_SEASON}")

    log.info(f"Validation season: {VALIDATION_SEASON} — {len(val_df)} matches")

    # ── Predict ─────────────────────────────────────────────────────────────
    X = val_df[feat_cols].values
    y_proba = model.predict_proba(X)          # (n, 3)
    y_pred  = model.predict(X)                # array of "H"/"D"/"A"

    # ── Assign gameweeks — use (ISO year, ISO week) to handle Jan roll-over ──
    iso = val_df["Date"].dt.isocalendar()
    year_weeks = list(zip(iso["year"].values, iso["week"].values))
    unique_yw  = sorted(set(year_weeks))
    yw_to_gw   = {yw: i + 1 for i, yw in enumerate(unique_yw)}
    gameweeks  = np.array([yw_to_gw[yw] for yw in year_weeks])

    # ── Build match records ─────────────────────────────────────────────────
    matches_out = []
    running_correct = 0

    for i, (_, row) in enumerate(val_df.iterrows()):
        actual    = str(row["FTR"])
        predicted = str(y_pred[i])
        correct   = actual == predicted
        if correct:
            running_correct += 1

        h_prob = float(y_proba[i, h_idx])
        d_prob = float(y_proba[i, d_idx])
        a_prob = float(y_proba[i, a_idx])
        confidence = float(max(h_prob, d_prob, a_prob))

        matches_out.append({
            "date":             row["Date"].strftime("%Y-%m-%d"),
            "gameweek":         int(gameweeks[i]),
            "home_team":        str(row["HomeTeam"]),
            "away_team":        str(row["AwayTeam"]),
            "home_goals":       int(row["FTHG"]),
            "away_goals":       int(row["FTAG"]),
            "actual":           actual,
            "predicted":        predicted,
            "correct":          correct,
            "home_win_prob":    round(h_prob, 4),
            "draw_prob":        round(d_prob, 4),
            "away_win_prob":    round(a_prob, 4),
            "confidence":       round(confidence, 4),
            "running_accuracy": round(running_correct / (i + 1), 4),
        })

    # ── Aggregate stats ──────────────────────────────────────────────────────
    total   = len(matches_out)
    correct = sum(1 for m in matches_out if m["correct"])
    accuracy = round(correct / total, 4) if total else 0.0

    by_outcome: dict[str, dict] = {}
    for outcome in ["H", "D", "A"]:
        subset = [m for m in matches_out if m["actual"] == outcome]
        n      = len(subset)
        c      = sum(1 for m in subset if m["correct"])
        by_outcome[outcome] = {
            "total":    n,
            "correct":  c,
            "accuracy": round(c / n, 4) if n else 0.0,
        }

    result = {
        "season":     VALIDATION_SEASON,
        "total":      total,
        "correct":    correct,
        "accuracy":   accuracy,
        "by_outcome": by_outcome,
        "matches":    matches_out,
    }

    out_path = MODELS_DIR / "validation.json"
    out_path.write_text(json.dumps(result, indent=2))

    log.info(f"Validation: {correct}/{total} = {accuracy:.1%}")
    log.info(f"  H: {by_outcome['H']['correct']}/{by_outcome['H']['total']} = {by_outcome['H']['accuracy']:.1%}")
    log.info(f"  D: {by_outcome['D']['correct']}/{by_outcome['D']['total']} = {by_outcome['D']['accuracy']:.1%}")
    log.info(f"  A: {by_outcome['A']['correct']}/{by_outcome['A']['total']} = {by_outcome['A']['accuracy']:.1%}")
    log.info(f"Saved → {out_path}")


if __name__ == "__main__":
    validate()
