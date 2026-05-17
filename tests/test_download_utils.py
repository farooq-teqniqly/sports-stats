import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from download_utils import download_url, save_html


def make_response(
    status_code: int = 200, content: bytes = b"<html></html>"
) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.content = content
    response.raise_for_status.side_effect = (
        None if status_code < 400 else requests.HTTPError(response=response)
    )
    return response


def test_download_url_raises_on_empty_url():
    with pytest.raises(ValueError):
        download_url("")


def test_download_url_raises_on_blank_url():
    with pytest.raises(ValueError):
        download_url("   ")


def test_save_html_raises_on_none_response():
    with pytest.raises(ValueError):
        save_html(None, "out.html")


def test_save_html_raises_on_empty_filename():
    with pytest.raises(ValueError):
        save_html(make_response(), "")


def test_save_html_raises_on_blank_filename():
    with pytest.raises(ValueError):
        save_html(make_response(), "   ")


def test_save_html_raises_on_failed_response():
    with pytest.raises(requests.HTTPError):
        save_html(make_response(status_code=404), "out.html")


def test_save_html_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "a" / "b" / "out.html"
    save_html(make_response(), str(out_file))
    assert out_file.exists()


def test_save_html_writes_file(tmp_path):
    out_file = tmp_path / "out.html"
    save_html(make_response(content=b"<html><body></body></html>"), str(out_file))
    assert out_file.read_text(encoding="utf-8").strip() != ""
