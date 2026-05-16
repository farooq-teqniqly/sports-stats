from collections.abc import Generator

from bs4 import BeautifulSoup


def get_draft_stats(filename: str, stats: list[str]) -> Generator[dict, None, None]:
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

        player_name = player_cell.get_text(strip=True)
        player_stats = {"player": player_name, "missing": []}

        for stat in stats_set:
            cell = row.find(attrs={"data-stat": stat})
            value = cell.get_text(strip=True) if cell else None
            player_stats[stat] = value
            if not value:
                player_stats["missing"].append(stat)

        yield player_stats
