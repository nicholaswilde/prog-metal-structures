"""Tests for MIDI parser."""

from pathlib import Path
import pytest
from scripts.parse_midi import parse_midi_file, slugify


def test_parse_midi_existing_sample():
  """Verify parsing an on-disk MIDI sample produces valid structural keys."""
  midi_files = list(Path("data/raw/midi").glob("*.mid*"))
  assert len(midi_files) > 0, "Expected at least one raw MIDI test file"
  sample = midi_files[0]
  data = parse_midi_file(sample)

  assert "track_id" in data
  assert "title" in data
  assert "measures" in data
  assert "total_measures" in data
  assert data["total_measures"] == len(data["measures"])

  # Check measure properties
  m1 = data["measures"][0]
  assert m1["measure_number"] == 1
  assert "/" in m1["time_signature"]
  assert m1["tempo_bpm"] > 0
