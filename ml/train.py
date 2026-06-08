"""
Train the EPL match outcome classifier.

Pipeline:
  - Temporal train/test split: first 8 seasons train, last 2 test (no leakage)
  - HistGradientBoostingClassifier handles NaN natively (early-season matches have no form yet)
  - CalibratedClassifierCV (isotonic) to get well-calibrated win/draw/loss probabilities
  - Saves: models/model.joblib  models/meta.json
"""
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, log_loss
from sklearn.preprocessing import LabelEncoder

from features import FEATURE_COLS, PROCESSED_DIR

log = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Last season held out for test/validation
TEST_SEASONS = {"2025-26"}

LABEL_ORDER = ["H", "D", "A"]   # consistent probability index


def load_data() -> pd.DataFrame:
    path = PROCESSED_DIR / "features.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Run ml/features.py first: {path}")
    return pd.read_parquet(path)


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[~df["Season"].isin(TEST_SEASONS)].copy()
    test  = df[df["Season"].isin(TEST_SEASONS)].copy()
    log.info(f"Train: {len(train)} matches | Test: {len(test)} matches")
    return train, test


def train() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    df = load_data()

    train_df, test_df = split(df)

    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["FTR"].values
    X_test  = test_df[FEATURE_COLS].values
    y_test  = test_df["FTR"].values

    log.info("Training HistGradientBoostingClassifier...")
    base = HistGradientBoostingClassifier(
        max_iter=400,
        max_depth=5,
        learning_rate=0.05,
        min_samples_leaf=20,
        l2_regularization=0.1,
        class_weight="balanced",
        random_state=42,
    )

    # Isotonic calibration on a held-out fold of the training data
    model = CalibratedClassifierCV(base, method="isotonic", cv=5)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    classes = list(model.classes_)

    acc = accuracy_score(y_test, y_pred)
    ll  = log_loss(y_test, y_proba, labels=classes)

    # Class breakdown
    for cls in classes:
        mask = y_test == cls
        cls_acc = accuracy_score(y_test[mask], y_pred[mask])
        log.info(f"  {cls}: {mask.sum()} samples, {cls_acc:.3f} acc")

    log.info(f"\nTest accuracy : {acc:.4f}")
    log.info(f"Test log-loss : {ll:.4f}")
    log.info(f"Baseline (H)  : {(y_test == 'H').mean():.4f}")
    log.info(f"Baseline (D)  : {(y_test == 'D').mean():.4f}")
    log.info(f"Baseline (A)  : {(y_test == 'A').mean():.4f}")

    # Permutation importance on test set (works with any estimator)
    log.info("Computing permutation importance...")
    perm = permutation_importance(model, X_test, y_test, n_repeats=10,
                                  random_state=42, n_jobs=-1)
    feat_importance = [
        {"feature": FEATURE_COLS[i],
         "importance": round(float(perm.importances_mean[i]), 5)}
        for i in np.argsort(perm.importances_mean)[::-1]
    ]
    log.info(f"Top feature: {feat_importance[0]['feature']} ({feat_importance[0]['importance']:.4f})")

    # Probability order: ensure H / D / A columns are consistent
    proba_idx = {c: i for i, c in enumerate(classes)}

    # Save artifacts
    joblib.dump(model, MODELS_DIR / "model.joblib")
    joblib.dump(FEATURE_COLS, MODELS_DIR / "feature_cols.joblib")

    meta = {
        "feature_cols": FEATURE_COLS,
        "classes": classes,
        "label_order": LABEL_ORDER,
        "proba_idx": proba_idx,
        "test_accuracy": round(acc, 4),
        "test_log_loss": round(ll, 4),
        "train_seasons": sorted(train_df["Season"].unique().tolist()),
        "test_seasons": sorted(test_df["Season"].unique().tolist()),
        "teams": sorted(df["HomeTeam"].unique().tolist()),
        "feature_importance": feat_importance,
    }
    (MODELS_DIR / "meta.json").write_text(json.dumps(meta, indent=2))

    log.info(f"Model saved → {MODELS_DIR}/model.joblib")
    log.info(f"Meta  saved → {MODELS_DIR}/meta.json")


if __name__ == "__main__":
    train()
