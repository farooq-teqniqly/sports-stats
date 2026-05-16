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

if (__name__ == "__main__"):
    response = download_url("https://www.basketball-reference.com/draft/NBA_2000.html")
    save_html(response, "../data/bball/drafts/nba_draft_2000.html")