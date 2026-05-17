import requests
from pathlib import Path

from bs4 import BeautifulSoup
from requests import Response


def download_url(url: str, timeout: int = 30) -> Response:
    """Fetch a URL using a browser-like User-Agent header.

    Args:
        url: The URL to fetch. Must not be empty or blank.
        timeout: Request timeout in seconds. Defaults to 30.

    Returns:
        The HTTP response object.

    Raises:
        ValueError: If url is empty or blank.
        requests.HTTPError: If the response status indicates an error.
    """
    if not url or not url.strip():
        raise ValueError("url must not be empty")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    return response


def save_html(response: Response, filename: str) -> None:
    """Parse and pretty-print response HTML, then write it to a file.

    Args:
        response: A successful HTTP response containing HTML content.
        filename: Destination file path. Parent directories are created if absent.

    Raises:
        ValueError: If response is None or filename is empty or blank.
        requests.HTTPError: If the response status indicates an error.
    """
    if response is None:
        raise ValueError("response must not be None")

    if not filename or not filename.strip():
        raise ValueError("filename must not be empty")

    response.raise_for_status()

    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    soup = BeautifulSoup(response.content, "html.parser")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
