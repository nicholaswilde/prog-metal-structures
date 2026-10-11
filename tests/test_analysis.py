"""Tests for metric complexity calculations and transition matrices."""

import pytest
from scripts.analyze_structure import (
  calculate_metric_entropy,
  calculate_shift_frequency,
  build_transition_matrix,
  analyze_track,
)


def test_calculate_shift_frequency():
  """Verify meter shift frequency is transitions / (total_measures - 1)."""
  meters = ["4/4", "7/8", "7/8", "5/8", "4/4"]
  # Transitions occur at: 4/4->7/8, 7/8->5/8, 5/8->4/4 (3 transitions over 4 opportunities)
  freq = calculate_shift_frequency(meters)
  assert pytest.approx(freq, 0.01) == 0.75


def test_calculate_metric_entropy():
  """Verify Shannon entropy of meter distribution."""
  # Single uniform meter -> 0 entropy
  single_meter = ["4/4", "4/4", "4/4"]
  assert calculate_metric_entropy(single_meter) == 0.0

  # Two equal meters -> 1.0 bit
  two_equal = ["4/4", "7/8"]
  assert pytest.approx(calculate_metric_entropy(two_equal), 0.01) == 1.0


def test_build_transition_matrix():
  """Verify Markovian transition matrix construction and normalized probabilities."""
  meters = ["4/4", "7/8", "4/4", "7/8"]
  matrix = build_transition_matrix(meters)
  # From 4/4, 100% of transitions go to 7/8
  assert matrix["4/4"]["7/8"] == 1.0
  # From 7/8, 100% of transitions go to 4/4
  assert matrix["7/8"]["4/4"] == 1.0


def test_analyze_track():
  """Verify full analysis dictionary structure."""
  track_dict = {
    "track_id": "test_track",
    "title": "Test Title",
    "artist": "Test Artist",
    "total_measures": 4,
    "measures": [
      {"measure_number": 1, "time_signature": "4/4", "tempo_bpm": 120.0},
      {"measure_number": 2, "time_signature": "7/8", "tempo_bpm": 120.0},
      {"measure_number": 3, "time_signature": "7/8", "tempo_bpm": 120.0},
      {"measure_number": 4, "time_signature": "5/8", "tempo_bpm": 120.0},
    ]
  }
  result = analyze_track(track_dict)
  assert result["track_id"] == "test_track"
  assert "shift_frequency" in result
  assert "metric_entropy" in result
  assert "transition_matrix" in result
  assert "meter_distribution" in result
