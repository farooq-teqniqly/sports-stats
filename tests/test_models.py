import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import NBACareerStats, Player


def test_player_from_draft_stats_happy_path():
    stats = {"player": "Kenyon Martin", "player_id": "martike01"}
    player = Player.from_draft_stats(stats, draft_year=2000)
    assert player.id == "martike01"
    assert player.name == "Kenyon Martin"
    assert player.draft_year == 2000


def test_player_from_draft_stats_no_draft_year():
    stats = {"player": "Kenyon Martin", "player_id": "martike01"}
    player = Player.from_draft_stats(stats)
    assert player.draft_year is None


def test_player_from_draft_stats_missing_player_id_raises():
    with pytest.raises(ValueError, match="player_id"):
        Player.from_draft_stats({"player": "Kenyon Martin"})


def test_player_from_draft_stats_missing_player_raises():
    with pytest.raises(ValueError, match="player"):
        Player.from_draft_stats({"player_id": "martike01"})


def test_nba_career_stats_from_draft_stats_numeric_conversion():
    stats = {"ws": "48.0", "ws_per_48": ".100", "bpm": "0.1", "vorp": "12.1"}
    cs = NBACareerStats.from_draft_stats("martike01", stats)
    assert cs.player_id == "martike01"
    assert cs.ws == 48.0
    assert cs.ws_48 == 0.1
    assert cs.bpm == 0.1
    assert cs.vorp == 12.1


def test_nba_career_stats_from_draft_stats_non_numeric_returns_none():
    stats = {"ws": "n/a", "ws_per_48": None, "bpm": None, "vorp": None}
    cs = NBACareerStats.from_draft_stats("martike01", stats)
    assert cs.ws is None


def test_nba_career_stats_from_draft_stats_empty_string_returns_none():
    stats = {"ws": "", "ws_per_48": "", "bpm": "", "vorp": ""}
    cs = NBACareerStats.from_draft_stats("martike01", stats)
    assert cs.ws is None
    assert cs.ws_48 is None
    assert cs.bpm is None
    assert cs.vorp is None


def test_nba_career_stats_from_draft_stats_missing_key_returns_none():
    cs = NBACareerStats.from_draft_stats("martike01", {})
    assert cs.ws is None
    assert cs.ws_48 is None
    assert cs.bpm is None
    assert cs.vorp is None
