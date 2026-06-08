"""
Feature engineering for EPL match prediction.

Approach:
  1. Expand each match into two team-timeline rows (one per team).
  2. Compute rolling form stats with shift(1) so features reflect pre-match state.
  3. Compute H2H stats by iterating over grouped fixture pairs (O(pairs × matches_per_pair)).
  4. Join home/away team stats back onto the original match table.

Target variable: FTR  (H = Home Win, D = Draw, A = Away Win)
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

ROLL_WINDOWS = [5, 10]
STAT_COLS = ["pts", "gf", "ga", "sot"]

FEATURE_COLS = [
    # --- per-team rolling form ---
    "home_pts_roll5",  "home_pts_roll10",
    "home_gf_roll5",   "home_gf_roll10",
    "home_ga_roll5",   "home_ga_roll10",
    "home_sot_roll5",  "home_sot_roll10",
    "away_pts_roll5",  "away_pts_roll10",
    "away_gf_roll5",   "away_gf_roll10",
    "away_ga_roll5",   "away_ga_roll10",
    "away_sot_roll5",  "away_sot_roll10",
    # --- season-level ---
    "home_season_pts_pg", "home_season_gd",
    "away_season_pts_pg", "away_season_gd",
    # --- differentials (home minus away) ---
    "diff_pts_roll5",  "diff_pts_roll10",
    "diff_gf_roll5",   "diff_ga_roll5",
    "diff_season_pts_pg", "diff_season_gd",
    # --- head-to-head (last 5 meetings) ---
    "h2h_hw", "h2h_d", "h2h_aw", "h2h_n",
]


# ---------------------------------------------------------------------------
# 1. Team timeline
# ---------------------------------------------------------------------------

def _build_timeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand match data to one row per team per match.
    Adds: pts, gf, ga, sot, is_home.
    """
    has_sot = "HST" in df.columns and "AST" in df.columns

    home = df[["Date", "Season", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]].copy()
    home.rename(columns={"HomeTeam": "team", "AwayTeam": "opponent",
                          "FTHG": "gf", "FTAG": "ga"}, inplace=True)
    home["is_home"] = 1
    home["pts"] = home["FTR"].map({"H": 3, "D": 1, "A": 0})
    home["sot"] = df["HST"].values if has_sot else np.nan

    away = df[["Date", "Season", "AwayTeam", "HomeTeam", "FTAG", "FTHG", "FTR"]].copy()
    away.rename(columns={"AwayTeam": "team", "HomeTeam": "opponent",
                          "FTAG": "gf", "FTHG": "ga"}, inplace=True)
    away["is_home"] = 0
    away["pts"] = away["FTR"].map({"A": 3, "D": 1, "H": 0})
    away["sot"] = df["AST"].values if has_sot else np.nan

    tl = pd.concat([home, away], ignore_index=True)
    tl = tl.sort_values(["team", "Date"]).reset_index(drop=True)
    return tl


def _add_rolling(tl: pd.DataFrame) -> pd.DataFrame:
    """Add rolling and season-cumulative stats. shift(1) prevents leakage."""
    grp_team = tl.groupby("team")
    grp_ts   = tl.groupby(["team", "Season"])

    for col in STAT_COLS:
        for w in ROLL_WINDOWS:
            tl[f"{col}_roll{w}"] = (
                grp_team[col]
                .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
            )

    # Season expanding stats (reset at start of each season)
    tl["_season_pts_sum"] = grp_ts["pts"].transform(
        lambda x: x.shift(1).expanding().sum()
    )
    tl["_season_games"] = grp_ts["pts"].transform(
        lambda x: x.shift(1).expanding().count()
    )
    tl["season_pts_pg"] = tl["_season_pts_sum"] / tl["_season_games"].replace(0, np.nan)

    tl["_season_gf"] = grp_ts["gf"].transform(lambda x: x.shift(1).expanding().sum())
    tl["_season_ga"] = grp_ts["ga"].transform(lambda x: x.shift(1).expanding().sum())
    tl["season_gd"]  = tl["_season_gf"] - tl["_season_ga"]

    tl.drop(columns=["_season_pts_sum", "_season_games", "_season_gf", "_season_ga"],
            inplace=True)
    return tl


# ---------------------------------------------------------------------------
# 2. H2H
# ---------------------------------------------------------------------------

def _compute_h2h(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each match, compute H2H stats from the last 5 prior meetings.
    Groups by canonical fixture pair so we iterate over ~190 pairs × ~50 matches each.
    """
    df = df.sort_values("Date").reset_index(drop=True)
    df["_pair"] = df.apply(
        lambda r: "__".join(sorted([r["HomeTeam"], r["AwayTeam"]])), axis=1
    )

    hw_list, d_list, aw_list, n_list = (np.full(len(df), np.nan),) * 4
    hw_list = np.full(len(df), np.nan)
    d_list  = np.full(len(df), np.nan)
    aw_list = np.full(len(df), np.nan)
    n_list  = np.zeros(len(df), dtype=int)

    for _, grp in df.groupby("_pair"):
        grp = grp.sort_values("Date")
        positions = list(grp.index)

        for rank, idx in enumerate(positions):
            prev = grp.iloc[:rank].tail(5)
            n = len(prev)
            if n == 0:
                continue
            ht = df.at[idx, "HomeTeam"]
            hw = d = aw = 0
            for _, pm in prev.iterrows():
                if pm["HomeTeam"] == ht:
                    if pm["FTR"] == "H":   hw += 1
                    elif pm["FTR"] == "D": d  += 1
                    else:                  aw += 1
                else:
                    # reversed fixture: ht was away in that match
                    if pm["FTR"] == "H":   aw += 1
                    elif pm["FTR"] == "D": d  += 1
                    else:                  hw += 1
            hw_list[idx] = hw / n
            d_list[idx]  = d  / n
            aw_list[idx] = aw / n
            n_list[idx]  = n

    return pd.DataFrame({"h2h_hw": hw_list, "h2h_d": d_list,
                          "h2h_aw": aw_list, "h2h_n": n_list})


# ---------------------------------------------------------------------------
# 3. Build full feature matrix
# ---------------------------------------------------------------------------

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Building team timeline...")
    tl = _build_timeline(df)
    tl = _add_rolling(tl)

    # Cols to join for each team role
    stat_cols = (
        [f"{s}_roll{w}" for s in STAT_COLS for w in ROLL_WINDOWS]
        + ["season_pts_pg", "season_gd"]
    )

    # Join home team stats: key = (HomeTeam, Date)
    home_lookup = tl[["Date", "team"] + stat_cols].copy()
    home_lookup.columns = ["Date", "HomeTeam"] + [f"home_{c}" for c in stat_cols]

    # Join away team stats: key = (AwayTeam, Date)
    away_lookup = tl[["Date", "team"] + stat_cols].copy()
    away_lookup.columns = ["Date", "AwayTeam"] + [f"away_{c}" for c in stat_cols]

    df_sorted = df.sort_values("Date").reset_index(drop=True)
    out = df_sorted.merge(home_lookup, on=["Date", "HomeTeam"], how="left")
    out = out.merge(away_lookup, on=["Date", "AwayTeam"], how="left")

    # Differential features
    for base in ["pts_roll5", "pts_roll10", "gf_roll5", "ga_roll5",
                  "season_pts_pg", "season_gd"]:
        out[f"diff_{base}"] = out[f"home_{base}"] - out[f"away_{base}"]

    log.info("Computing H2H features...")
    h2h = _compute_h2h(df_sorted)
    out = pd.concat([out.reset_index(drop=True), h2h], axis=1)

    out_path = PROCESSED_DIR / "features.parquet"
    out.to_parquet(out_path, index=False)
    log.info(f"Saved {len(out)} feature rows → {out_path}")
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    df = pd.read_parquet(PROCESSED_DIR / "matches.parquet")
    features = build_features(df)
    print(features[FEATURE_COLS].describe())
    print(f"\nNull rate:\n{features[FEATURE_COLS].isnull().mean().sort_values(ascending=False).head(10)}")
