"""Tests for Guitar Pro parser."""

from pathlib import Path
import pytest
from scripts.parse_gp import parse_gp_file, slugify


def test_slugify():
  """Verify string slugification."""
  assert slugify("Dream Theater - Dance of Eternity!") == "dream_theater_dance_of_eternity"
  assert slugify("") == "unknown"


def test_parse_gp_existing_sample():
  """Verify parsing an on-disk sample file produces valid structural keys."""
  gp_files = list(Path("data/raw/guitar_pro").glob("*.gp*"))
  assert len(gp_files) > 0, "Expected at least one raw Guitar Pro test file"
  sample = gp_files[0]
  data = parse_gp_file(sample)

  assert "track_id" in data
  assert "title" in data
  assert "artist" in data
  assert "measures" in data
  assert "total_measures" in data
  assert data["total_measures"] == len(data["measures"])

  # Check measure properties
  m1 = data["measures"][0]
  assert m1["measure_number"] == 1
  assert "/" in m1["time_signature"]
  assert m1["tempo_bpm"] > 0
