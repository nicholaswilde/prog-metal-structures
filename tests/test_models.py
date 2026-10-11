"""Tests for models, scrapers, and parsers."""

import json
from pathlib import Path
import pytest
from scripts.models import Measure, Section, TrackArchitecture, ArtistMetadata


def test_models_validation():
  """Verify Pydantic models enforce schema rules."""
  section = Section(label="Intro", start_measure=1, end_measure=4)
  measure = Measure(measure_number=1, time_signature="7/8", tempo_bpm=120.0)
  track = TrackArchitecture(
    track_id="test_artist_test_song",
    title="Test Song",
    artist="Test Artist",
    sections=[section],
    measures=[measure],
  )
  assert track.track_id == "test_artist_test_song"
  assert len(track.measures) == 1
  assert track.measures[0].time_signature == "7/8"


def test_measure_time_signature_invalid():
  """Verify invalid time signatures are rejected."""
  with pytest.raises(ValueError):
    Measure(measure_number=1, time_signature="invalid", tempo_bpm=120.0)


def test_processed_tracks_validate_schema():
  """Verify all files in data/processed match TrackArchitecture schema."""
  import jsonschema

  schema = json.loads(Path("schemas/track_architecture.json").read_text(encoding="utf-8"))
  track_files = list(Path("data/processed").glob("*.json"))
  assert len(track_files) > 0, "Expected at least one processed track file"
  for f in track_files:
    data = json.loads(f.read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)
    model = TrackArchitecture.model_validate(data)
    assert model.total_measures == len(model.measures)


def test_processed_artists_validate_schema():
  """Verify all files in data/processed/artists match ArtistMetadata schema."""
  import jsonschema

  schema = json.loads(Path("schemas/artist_metadata.json").read_text(encoding="utf-8"))
  artist_files = list(Path("data/processed/artists").glob("*.json"))
  assert len(artist_files) > 0, "Expected at least one artist metadata file"
  for f in artist_files:
    data = json.loads(f.read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)
    model = ArtistMetadata.model_validate(data)
    assert model.total_parsed_tracks > 0
