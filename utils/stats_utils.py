from collections.abc import Generator
from pathlib import Path

from bs4 import BeautifulSoup


def get_draft_stats(filename: str, stats: list[str]) -> Generator[dict, None, None]:
    """Yield per-player stat dictionaries parsed from a saved Basketball Reference draft page.

    Each yielded dict contains a ``player`` key, a ``player_id`` key (e.g. ``martike01``
    extracted from the player anchor href), a ``missing`` list of stats with no recorded
    value, and one key per requested stat mapped to its string value or None.

    Args:
        filename: Path to a saved Basketball Reference draft HTML file.
        stats: List of ``data-stat`` attribute names to extract (e.g. ``["pts", "trb"]``).

    Yields:
        A dict per player row with keys: ``player``, ``player_id``, ``missing``, and one key per stat.
    """
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table", {"id": "stats"})
    stats_set = set(stats)

    for row in table.find("tbody").find_all("tr"):
        if "thead" in row.get("class", []):
            continue

        player_cell = row.find("td", {"data-stat": "player"})
        if not player_cell:
            continue

        anchor = player_cell.find("a")
        player_id = Path(anchor["href"]).stem if anchor else None
        player_name = player_cell.get_text(strip=True)
        player_stats = {"player": player_name, "player_id": player_id, "missing": []}

        for stat in stats_set:
            cell = row.find(attrs={"data-stat": stat})
            value = cell.get_text(strip=True) if cell else None
            player_stats[stat] = value
            if not value:
                player_stats["missing"].append(stat)

        yield player_stats
