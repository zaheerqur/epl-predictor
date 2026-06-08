"""
Download and combine 10 seasons of EPL match data from football-data.co.uk.
Produces data/processed/matches.parquet with normalized team names and dates.
"""
import logging
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# 11 seasons: 2015-16 → 2025-26
SEASONS = [
    ("1516", "2015-16"), ("1617", "2016-17"), ("1718", "2017-18"),
    ("1819", "2018-19"), ("1920", "2019-20"), ("2021", "2020-21"),
    ("2122", "2021-22"), ("2223", "2022-23"), ("2324", "2023-24"),
    ("2425", "2024-25"), ("2526", "2025-26"),
]

BASE_URL = "https://www.football-data.co.uk/mmz4281"

# Minimum columns required
REQUIRED = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
# Nice-to-have (shots, corners — not always present in older seasons)
OPTIONAL = ["HS", "AS", "HST", "AST", "HC", "AC"]

# football-data.co.uk name quirks across different seasons
_ALIASES: dict[str, str] = {
    "Man United":            "Man United",
    "Manchester United":     "Man United",
    "Wolverhampton Wanderers": "Wolves",
    "Nott'm Forest":         "Nott'm Forest",
    "Nottingham Forest":     "Nott'm Forest",
    "Brighton & Hove Albion": "Brighton",
    "Sheffield Utd":         "Sheffield United",
    "Huddersfield":          "Huddersfield",
    "Cardiff":               "Cardiff",
    "Stoke":                 "Stoke",
    "Swansea":               "Swansea",
    "Middlesbrough":         "Middlesbrough",
}


def _norm(name: str) -> str:
    return _ALIASES.get(name, name)


def _download(code: str, label: str) -> pd.DataFrame | None:
    path = RAW_DIR / f"E0_{code}.csv"
    if not path.exists():
        url = f"{BASE_URL}/{code}/E0.csv"
        log.info(f"Downloading {label}...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        path.write_bytes(r.content)
    else:
        log.info(f"Cached   {label}")

    df = pd.read_csv(path, encoding="latin-1")

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        log.warning(f"{label} missing {missing}, skipping")
        return None

    cols = REQUIRED + [c for c in OPTIONAL if c in df.columns]
    df = df[cols].copy()
    df = df.dropna(subset=REQUIRED)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    df["Season"] = label
    df["HomeTeam"] = df["HomeTeam"].map(_norm)
    df["AwayTeam"] = df["AwayTeam"].map(_norm)

    # Cast goals to int
    df["FTHG"] = df["FTHG"].astype(int)
    df["FTAG"] = df["FTAG"].astype(int)

    log.info(f"         {len(df)} matches")
    return df


def ingest() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    frames = [f for code, label in SEASONS if (f := _download(code, label)) is not None]
    combined = pd.concat(frames, ignore_index=True).sort_values("Date").reset_index(drop=True)

    out = PROCESSED_DIR / "matches.parquet"
    combined.to_parquet(out, index=False)
    log.info(f"Saved {len(combined)} total matches → {out}")
    return combined


if __name__ == "__main__":
    df = ingest()
    print(df.tail())
    print(f"\nTeams: {sorted(df['HomeTeam'].unique())}")
