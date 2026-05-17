import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from nba_draft_service import import_draft_class


def _make_response(status_code: int = 200) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.raise_for_status.side_effect = (
        None if status_code < 400 else requests.HTTPError(response=response)
    )
    return response


def _make_stats(
    player: str = "Kenyon Martin",
    player_id: str | None = "martike01",
    missing: list | None = None,
) -> dict:
    return {
        "player": player,
        "player_id": player_id,
        "missing": missing or [],
        "ws": "48.0",
        "ws_per_48": ".100",
        "bpm": "0.1",
        "vorp": "12.1",
    }


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_skips_player_without_player_id(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock, tmp_path: Path
) -> None:
    """Rows with no player_id are silently skipped; session.merge never called."""
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats(player_id=None)])
    session = MagicMock()

    with patch("nba_draft_service._DRAFT_HTML_DIR", tmp_path):
        import_draft_class(2000, session)

    session.merge.assert_not_called()


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_logs_warning_for_missing_stats(
    mock_dl: MagicMock,
    mock_save: MagicMock,
    mock_parse: MagicMock,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Warning is logged when a player row has missing stat fields."""
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats(missing=["ws", "bpm"])])

    with patch("nba_draft_service._DRAFT_HTML_DIR", tmp_path):
        with caplog.at_level(logging.WARNING, logger="nba_draft_service"):
            import_draft_class(2000, MagicMock())

    assert any("missing stats" in r.message for r in caplog.records)


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_downloads_correct_url(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock, tmp_path: Path
) -> None:
    """Correct Basketball Reference URL is constructed for the given year."""
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([])

    with patch("nba_draft_service._DRAFT_HTML_DIR", tmp_path):
        import_draft_class(2000, MagicMock())

    mock_dl.assert_called_once_with(
        "https://www.basketball-reference.com/draft/NBA_2000.html"
    )
