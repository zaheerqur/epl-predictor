# EPL Match Outcome Predictor

A full-stack machine learning application that predicts the result of any English Premier League fixture, with calibrated win/draw/loss probabilities.

> **Status:** work in progress - deployment to Render and Netlify pending. Run locally using the instructions below.

---

## What it does

- **Predict** any home vs away fixture and get win/draw/loss probabilities with recent form context
- **Backtest** the model against every match of the held-out 2025–26 season with a running accuracy chart
- **Table** - live league standings for any season in the dataset
- **Teams** - per-team stats, home/away splits, and form for any season
- **Pipeline** - model architecture, feature importances, and training metadata

---

## Model

| | |
|---|---|
| Data | 11 seasons of EPL results (2015–2026) from football-data.co.uk |
| Features | 28 engineered - rolling form (5 & 10 game), H2H rates, season pts/game, goal differentials |
| Algorithm | HistGradientBoostingClassifier + Isotonic Calibration |
| Split | Seasons 2015–2025 train · 2025–26 held-out validation |
| Auto-retrain | GitHub Actions cron every Monday & Thursday - fetches new results, retrains, redeploys |

---

## Stack

**Backend** - Python, FastAPI, scikit-learn, pandas, pyarrow  
**Frontend** - Vue 3 (CDN, no build step), vanilla CSS  
**Infra** - Docker, Render (API), Netlify (frontend), GitHub Actions  

---

## Project structure

```
epl-predictor/
├── api/                  # FastAPI app
│   ├── main.py           # endpoints: /predict /standings /team /h2h /validation
│   ├── predictor.py      # inference + data access layer
│   └── schemas.py        # Pydantic models
├── ml/                   # ML pipeline
│   ├── ingest.py         # downloads CSVs from football-data.co.uk
│   ├── features.py       # feature engineering
│   ├── train.py          # model training + calibration
│   └── validate.py       # held-out season evaluation
├── frontend/
│   ├── index.html        # Vue 3 SPA (all 5 tabs)
│   └── assets/logos/     # local club badge PNGs
├── models/               # trained artifacts (committed)
├── data/processed/       # parquet files (committed)
├── .github/workflows/    # weekly data refresh action
├── Dockerfile
├── render.yaml
├── netlify.toml
└── pipeline.py           # runs full pipeline end-to-end
```

---

## Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full ML pipeline (downloads data, trains model)
python pipeline.py

# Start the API
uvicorn api.main:app --port 8000

# Open the frontend
open frontend/index.html
```

The frontend auto-detects local vs production and switches between `localhost:8000` and the Netlify proxy accordingly.

---

## Deployment (planned)

| Service | Purpose |
|---|---|
| Render | Docker web service - auto-deploys on push |
| Netlify | Static frontend - proxies `/api/*` to Render |
| GitHub Actions | Weekly cron - re-downloads match data, retrains model, commits artifacts |

Config files (`render.yaml`, `netlify.toml`, `.github/workflows/update-data.yml`) are ready - deployment in progress.
