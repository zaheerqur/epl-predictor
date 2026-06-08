"""
Run the full ML pipeline end-to-end.
Usage: python pipeline.py [--skip-ingest] [--skip-features]
"""
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent / "ml"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-ingest",   action="store_true")
    parser.add_argument("--skip-features", action="store_true")
    args = parser.parse_args()

    if not args.skip_ingest:
        log.info("═══ Step 1/3: Ingesting data ═══")
        import ingest
        ingest.ingest()
    else:
        log.info("Skipping ingest.")

    if not args.skip_features:
        log.info("═══ Step 2/3: Engineering features ═══")
        import pandas as pd
        from pathlib import Path as P
        from features import build_features
        df = pd.read_parquet(P(__file__).parent / "data" / "processed" / "matches.parquet")
        build_features(df)
    else:
        log.info("Skipping features.")

    log.info("═══ Step 3/4: Training model ═══")
    import train
    train.train()

    log.info("═══ Step 4/4: Validating on 2025-26 season ═══")
    import validate
    validate.validate()

    log.info("\n✓ Pipeline complete. Start the API with:")
    log.info("  uvicorn api.main:app --reload --port 8000")
    log.info("\nOpen frontend/index.html in your browser.")


if __name__ == "__main__":
    main()
