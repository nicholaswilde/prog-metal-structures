from pathlib import Path
import json
from scripts.audit_gaps import audit_gaps, generate_gaps_report, write_gaps_report


def setup_mock_dataset(tmp_path: Path) -> Path:
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()
  artists_dir = processed_dir / "artists"
  artists_dir.mkdir()

  # Create mock artist with 2 albums
  artist = {
    "artist_id": "dream_theater",
    "name": "Dream Theater",
    "country": "United States",
    "formed_year": 1985,
    "genres": ["Progressive Metal"],
    "total_parsed_tracks": 2,
    "albums": [
      {
        "album_id": "images_and_words",
        "title": "Images and Words",
        "release_year": 1992,
        "total_tracks": 8,
        "parsed_tracks_count": 1,
        "track_ids": ["dream_theater_pull_me_under"],
      },
      {
        "album_id": "metropolis_pt_2",
        "title": "Metropolis Pt. 2: Scenes from a Memory",
        "release_year": 1999,
        "total_tracks": 12,
        "parsed_tracks_count": 1,
        "track_ids": ["dream_theater_dance_of_eternity"],
      },
    ],
  }
  (artists_dir / "dream_theater.json").write_text(json.dumps(artist), encoding="utf-8")

  # Create mock tracks
  track1 = {
    "track_id": "dream_theater_pull_me_under",
    "title": "Pull Me Under",
    "artist": "Dream Theater",
    "album": "Images and Words",
    "year": 1992,
    "default_tempo_bpm": 102.0,
    "default_time_signature": "4/4",
    "total_measures": 200,
    "sections": [{"name": "Intro", "start_measure": 1, "end_measure": 20}],
    "measures": [{"measure_number": 1, "time_signature": "4/4", "tempo_bpm": 102.0}],
  }
  (processed_dir / "dt_pull.json").write_text(json.dumps(track1), encoding="utf-8")

  track2 = {
    "track_id": "dream_theater_dance_of_eternity",
    "title": "The Dance of Eternity",
    "artist": "Dream Theater",
    "album": "",
    "year": None,
    "default_tempo_bpm": 0.0,
    "default_time_signature": "7/8",
    "total_measures": 120,
    "sections": [],
    "measures": [{"measure_number": 1, "time_signature": "7/8", "tempo_bpm": None}],
  }
  (processed_dir / "dt_dance.json").write_text(json.dumps(track2), encoding="utf-8")

  return processed_dir


def test_audit_gaps(tmp_path: Path):
  """Verify gap audit computes album completion rates and quality metrics."""
  processed_dir = setup_mock_dataset(tmp_path)
  stats = audit_gaps(processed_dir)

  assert stats["total_artists"] == 1
  assert stats["total_albums"] == 2
  assert stats["total_tracks_expected"] == 20
  assert stats["total_tracks_parsed"] == 2
  assert stats["overall_coverage_pct"] == 10.0

  # Check quality metrics
  quality = stats["quality"]
  assert quality["missing_album_count"] == 1
  assert quality["missing_sections_count"] == 1
  assert quality["missing_default_tempo_count"] == 1


def test_generate_gaps_report(tmp_path: Path):
  """Verify markdown report generation produces tables and summary."""
  processed_dir = setup_mock_dataset(tmp_path)
  stats = audit_gaps(processed_dir)
  report = generate_gaps_report(stats)

  assert "# Progressive Metal Dataset: Data Gap & Completeness Report" in report
  assert "Images and Words" in report
  assert "Metropolis Pt. 2: Scenes from a Memory" in report
  assert "Pull Me Under" in report or "Dream Theater" in report
  assert "Quality Metric" in report


def test_write_gaps_report(tmp_path: Path):
  """Verify write_gaps_report saves markdown file."""
  processed_dir = setup_mock_dataset(tmp_path)
  stats = audit_gaps(processed_dir)
  out_path = tmp_path / "docs" / "dataset_gaps.md"

  res_path = write_gaps_report(stats, out_path)
  assert res_path.exists()
  content = res_path.read_text(encoding="utf-8")
  assert "Images and Words" in content
