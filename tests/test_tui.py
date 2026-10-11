"""Tests for Catppuccin Mocha TUI runner."""

from pathlib import Path
from scripts.runner import IngestionTUI, TrackStats


def test_compute_track_stats():
  """Verify calculation of meter changes and distinct meters."""
  track_data = {
    "track_id": "test_track",
    "title": "Test Title",
    "artist": "Test Artist",
    "source_file": "test.gp5",
    "total_measures": 5,
    "measures": [
      {"measure_number": 1, "time_signature": "4/4", "tempo_bpm": 120.0},
      {"measure_number": 2, "time_signature": "7/8", "tempo_bpm": 120.0},
      {"measure_number": 3, "time_signature": "7/8", "tempo_bpm": 120.0},
      {"measure_number": 4, "time_signature": "5/8", "tempo_bpm": 120.0},
      {"measure_number": 5, "time_signature": "4/4", "tempo_bpm": 120.0},
    ]
  }
  stats = IngestionTUI.compute_stats(track_data)
  assert stats.total_measures == 5
  assert stats.time_sig_changes == 3  # (4/4 -> 7/8), (7/8 -> 5/8), (5/8 -> 4/4)
  assert stats.distinct_meters == ["4/4", "7/8", "5/8"]
