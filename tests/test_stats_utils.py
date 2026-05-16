import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from stats_utils import get_draft_stats

DRAFT_FILE = Path(__file__).parent.parent / "data" / "bball" / "drafts" / "nba_draft_2000.html"
STATS = ["ws", "ws_per_48", "bpm", "vorp"]


def test_get_draft_stats_yields_results():
    results = list(get_draft_stats(str(DRAFT_FILE), STATS))
    assert len(results) > 0


def test_get_draft_stats_contains_requested_stat_keys():
    results = list(get_draft_stats(str(DRAFT_FILE), STATS))
    for player in results:
        for stat in STATS:
            assert stat in player, f"'{stat}' missing for {player.get('player')}"


def test_get_draft_stats_values_populated():
    results = list(get_draft_stats(str(DRAFT_FILE), STATS))
    first = results[0]
    assert first["player"] == "Kenyon Martin"
    assert first["ws"] == "48.0"
    assert first["ws_per_48"] == ".100"
    assert first["bpm"] == "0.1"
    assert first["vorp"] == "12.1"


def test_get_draft_stats_unknown_stat_returns_none():
    results = list(get_draft_stats(str(DRAFT_FILE), ["ws", "nonexistent_stat"]))
    for player in results:
        assert player["nonexistent_stat"] is None


def test_get_draft_stats_empty_stats_yields_player_key_only():
    results = list(get_draft_stats(str(DRAFT_FILE), []))
    assert len(results) > 0
    for player in results:
        assert list(player.keys()) == ["player"]
