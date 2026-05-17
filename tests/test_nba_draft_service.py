import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
def test_import_draft_class_raises_on_invalid_year(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock
) -> None:
    """Year < 1947 raises ValueError."""
    with pytest.raises(ValueError):
        import_draft_class(1946, MagicMock())


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_merges_player_and_stats(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock
) -> None:
    """Both Player and NBACareerStats are merged for each row."""
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
def test_import_draft_class_commits_session(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock
) -> None:
    """Session is committed once after all rows are processed."""
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats()])
    session = MagicMock()

    import_draft_class(2000, session)

    session.commit.assert_called_once()


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_skips_player_without_player_id(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock
) -> None:
    """Rows with no player_id are skipped; no merge called."""
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats(player_id=None)])
    session = MagicMock()

    import_draft_class(2000, session)

    session.merge.assert_not_called()


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_logs_warning_for_missing_stats(
    mock_dl: MagicMock,
    mock_save: MagicMock,
    mock_parse: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Warning logged when a player has missing stat fields."""
    import logging

    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter([_make_stats(missing=["ws", "bpm"])])

    with caplog.at_level(logging.WARNING, logger="nba_draft_service"):
        import_draft_class(2000, MagicMock())

    assert any("missing stats" in r.message for r in caplog.records)


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_downloads_correct_url(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock, tmp_path: Path
) -> None:
    """Correct Basketball Reference URL is fetched for the given year."""
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
def test_import_draft_class_merges_multiple_players(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock
) -> None:
    """All players in the parsed result are merged."""
    mock_dl.return_value = _make_response()
    mock_parse.return_value = iter(
        [
            _make_stats("Kenyon Martin", "martike01"),
            _make_stats("Stromile Swift", "swifst01"),
        ]
    )
    session = MagicMock()

    import_draft_class(2000, session)

    assert session.merge.call_count == 4


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_raises_on_http_error(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock, tmp_path: Path
) -> None:
    """HTTPError from download_url propagates to caller."""
    mock_dl.side_effect = requests.HTTPError()

    with patch("nba_draft_service._DRAFT_HTML_DIR", tmp_path):
        with pytest.raises(requests.HTTPError):
            import_draft_class(2000, MagicMock())


@patch("nba_draft_service.get_draft_stats")
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url")
def test_import_draft_class_uses_cached_html(
    mock_dl: MagicMock, mock_save: MagicMock, mock_parse: MagicMock, tmp_path: Path
) -> None:
    """download_url and save_html not called when HTML already cached."""
    (tmp_path / "nba_draft_2000.html").write_text("<html/>")
    mock_parse.return_value = iter([])

    with patch("nba_draft_service._DRAFT_HTML_DIR", tmp_path):
        import_draft_class(2000, MagicMock())

    mock_dl.assert_not_called()
    mock_save.assert_not_called()
