from bs4 import BeautifulSoup
from requests import Response


def download_url(url: str) -> Response:
    import requests

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    return response

def save_html(response: Response, filename: str) -> None:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.content, "html.parser")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

def get_draft_stats(filename: str, stats: list[str]):
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
        player_stats = {"player": player_name}

        for stat in stats_set:
            cell = row.find(attrs={"data-stat": stat})
            player_stats[stat] = cell.get_text(strip=True) if cell else None

        yield player_stats

if (__name__ == "__main__"):
    response = download_url("https://www.basketball-reference.com/draft/NBA_2000.html")
    save_html(response, "../data/bball/drafts/nba_draft_2000.html")