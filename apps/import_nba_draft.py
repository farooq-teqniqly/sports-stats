"""CLI app to download and persist NBA draft advanced stats."""

import argparse
import logging
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db_utils import build_engine
from nba_draft_service import import_draft_class

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _build_engine() -> Engine:
    """Create a SQLAlchemy Engine from environment variables."""
    sa_password = os.environ.get("SA_PASSWORD")
    if not sa_password:
        raise ValueError("SA_PASSWORD environment variable is not set")
    db_name = os.environ.get("DB_NAME", "sports_stats")
    return build_engine(sa_password, db_name)


def main() -> None:
    """Entry point for the NBA draft stats importer."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Download and persist NBA draft advanced stats from Basketball Reference."
    )
    parser.add_argument(
        "year",
        type=int,
        help="Draft year to import (e.g. 2000). Must be >= 1947.",
    )
    args = parser.parse_args()

    try:
        engine = _build_engine()
    except ValueError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    logger.info("Importing NBA draft class %d", args.year)

    try:
        with Session(engine) as session:
            import_draft_class(args.year, session)
    except (ValueError, requests.HTTPError) as exc:
        logger.error("%s", exc)
        sys.exit(1)

    logger.info("Done")


if __name__ == "__main__":
    main()
