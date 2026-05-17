import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from nba_draft_service import import_draft_class
from models import NBACareerStats, Player


def _make_response(status_code: int = 200) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.raise_for_status.side_effect = (
        None if status_code < 400 else requests.HTTPError(response=response)
    )
    return response


def _make_stats(
    player: str = "Kenyon Martin",
    player_id: str = "martike01",
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
def test_import_draft_class_raises_on_invalid_year(mock_dl, mock_save, mock_parse):
    with pytest.raises(ValueError):
        import_draft_class(1946, MagicMock())


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_merges_player_and_stats(mock_dl, mock_save, mock_parse):
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats()])
    session = MagicMock()

    import_draft_class(2000, session)

    merge_calls = session.merge.call_args_list
    assert len(merge_calls) == 2
    assert isinstance(merge_calls[0].args[0], Player)
    assert isinstance(merge_calls[1].args[0], NBACareerStats)


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_commits_session(mock_dl, mock_save, mock_parse):
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats()])
    session = MagicMock()

    import_draft_class(2000, session)

    session.commit.assert_called_once()


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_skips_player_without_player_id(mock_dl, mock_save, mock_parse):
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats(player_id=None)])
    session = MagicMock()

    import_draft_class(2000, session)

    session.merge.assert_not_called()


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_logs_warning_for_missing_stats(
    mock_dl, mock_save, mock_parse, caplog
):
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats(missing=["ws", "bpm"])])
    import logging

    with caplog.at_level(logging.WARNING, logger="nba_draft_service"):
        import_draft_class(2000, MagicMock())

    assert any("missing stats" in r.message for r in caplog.records)


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_downloads_correct_url(mock_dl, mock_save, mock_parse, tmp_path):
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([])

    with patch("nba_draft_service._DRAFT_HTML_DIR", tmp_path):
        import_draft_class(2000, MagicMock())

    mock_dl.assert_called_once_with(
        "https://www.basketball-reference.com/draft/NBA_2000.html"
    )


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_merges_multiple_players(mock_dl, mock_save, mock_parse):
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([
        _make_stats("Kenyon Martin", "martike01"),
        _make_stats("Stromile Swift", "swifst01"),
    ])
    session = MagicMock()

    import_draft_class(2000, session)

    assert session.merge.call_count == 4
