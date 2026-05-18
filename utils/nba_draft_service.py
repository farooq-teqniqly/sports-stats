import logging
from pathlib import Path

from sqlalchemy.orm import Session

from models import NBACareerStats, Player
from download_utils import download_url, save_html
from stats_utils import get_draft_stats

logger = logging.getLogger(__name__)

_CAREER_STATS = ["ws", "ws_per_48", "bpm", "vorp"]
_PLAYER_STATS = ["pick_overall"]
_DRAFT_HTML_DIR = Path(__file__).parent.parent / "data" / "bball" / "drafts"


def import_draft_class(year: int, session: Session) -> None:
    """Download and persist NBA advanced stats for a draft class.

    Downloads the Basketball Reference draft page for the given year, parses
    advanced stats, and upserts player and stat records into the database.
    Players without a resolved player_id are skipped. Missing stat values
    trigger a warning log entry. All inserts are idempotent. If the HTML
    file for the given year is already cached locally, the download is skipped.

    Args:
        year: Draft year. Must be >= 1947.
        session: Active SQLAlchemy session. Caller owns the session lifecycle.

    Raises:
        ValueError: If year is less than 1947.
        requests.HTTPError: If the draft page download fails.
    """
    if year < 1947:
        raise ValueError(f"year must be >= 1947, got {year}")

    html_path = _DRAFT_HTML_DIR / f"nba_draft_{year}.html"

    if not html_path.exists():
        url = f"https://www.basketball-reference.com/draft/NBA_{year}.html"
        logger.info("Downloading NBA draft page for %d", year)
        response = download_url(url)
        save_html(response, str(html_path))
    else:
        logger.info("Using cached NBA draft page for %d", year)

    for stats in get_draft_stats(str(html_path), _CAREER_STATS + _PLAYER_STATS):
        player_id = stats.get("player_id")
        if not player_id:
            logger.warning("Skipping '%s' — no player_id resolved", stats.get("player"))
            continue

        missing_career = [s for s in stats["missing"] if s in _CAREER_STATS]
        if missing_career:
            logger.warning(
                "Player %s (%s) missing career stats: %s",
                stats["player"],
                player_id,
                missing_career,
            )

        missing_player = [s for s in stats["missing"] if s in _PLAYER_STATS]
        if missing_player:
            logger.info(
                "Player %s (%s) missing player stats (draft_position will be NULL): %s",
                stats["player"],
                player_id,
                missing_player,
            )

        session.merge(Player.from_draft_stats(stats, draft_year=year))
        session.merge(NBACareerStats.from_draft_stats(player_id, stats))

    session.commit()
