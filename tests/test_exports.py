from pathlib import Path
import json
import sqlite3
import pyarrow.parquet as pq
from scripts.export_datasets import export_sqlite, export_parquet


def test_export_sqlite(tmp_path: Path):
  """Verify SQLite database export creates normalized tables and indexes."""
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()
  artists_dir = processed_dir / "artists"
  artists_dir.mkdir()
  analysis_dir = processed_dir / "analysis"
  analysis_dir.mkdir()

  # Create mock track
  track_data = {
    "track_id": "opeth_deliverance",
    "title": "Deliverance",
    "artist": "Opeth",
    "album": "Deliverance",
    "year": 2002,
    "default_tempo_bpm": 120.0,
    "default_time_signature": "4/4",
    "total_measures": 2,
    "sections": [{"name": "Intro", "start_measure": 1, "end_measure": 2}],
    "measures": [
      {"measure_number": 1, "time_signature": "4/4", "tempo_bpm": 120.0, "section_name": "Intro"},
      {"measure_number": 2, "time_signature": "7/8", "tempo_bpm": 120.0, "section_name": "Intro"},
    ],
  }
  (processed_dir / "opeth_deliverance.json").write_text(json.dumps(track_data), encoding="utf-8")

  # Create mock artist
  artist_data = {
    "artist_id": "opeth",
    "name": "Opeth",
    "country": "Sweden",
    "formed_year": 1990,
    "genres": ["Progressive Death Metal"],
    "total_parsed_tracks": 1,
    "albums": [],
  }
  (artists_dir / "opeth.json").write_text(json.dumps(artist_data), encoding="utf-8")

  # Create mock analysis
  analysis_data = [
    {
      "track_id": "opeth_deliverance",
      "title": "Deliverance",
      "artist": "Opeth",
      "total_measures": 2,
      "unique_meters": 2,
      "shift_frequency": 0.5,
      "metric_entropy": 1.0,
      "meter_distribution": {"4/4": 0.5, "7/8": 0.5},
      "transition_matrix": {"4/4": {"7/8": 1.0}},
    }
  ]
  (analysis_dir / "metric_complexity.json").write_text(json.dumps(analysis_data), encoding="utf-8")

  db_path = tmp_path / "test.db"
  out = export_sqlite(processed_dir, db_path)
  assert out.exists()

  conn = sqlite3.connect(db_path)
  cur = conn.cursor()

  # Check tables exist
  cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
  tables = {r[0] for r in cur.fetchall()}
  assert {"tracks", "measures", "sections", "artists", "complexity_metrics"}.issubset(tables)

  # Check tracks row
  cur.execute("SELECT track_id, title, artist, total_measures FROM tracks")
  track_row = cur.fetchone()
  assert track_row == ("opeth_deliverance", "Deliverance", "Opeth", 2)

  # Check measures rows
  cur.execute("SELECT measure_number, time_signature FROM measures ORDER BY measure_number")
  measures = cur.fetchall()
  assert measures == [(1, "4/4"), (2, "7/8")]

  # Check artists row
  cur.execute("SELECT artist_id, name, country FROM artists")
  artist_row = cur.fetchone()
  assert artist_row == ("opeth", "Opeth", "Sweden")

  # Check complexity row
  cur.execute("SELECT track_id, metric_entropy FROM complexity_metrics")
  comp_row = cur.fetchone()
  assert comp_row == ("opeth_deliverance", 1.0)

  conn.close()


def test_export_parquet(tmp_path: Path):
  """Verify Parquet export writes tracks and measures with valid schema."""
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()

  track_data = {
    "track_id": "dream_theater_dance",
    "title": "Dance of Eternity",
    "artist": "Dream Theater",
    "album": "Metropolis Pt. 2",
    "year": 1999,
    "default_tempo_bpm": 130.0,
    "default_time_signature": "4/4",
    "total_measures": 1,
    "sections": [],
    "measures": [{"measure_number": 1, "time_signature": "7/8", "tempo_bpm": 130.0}],
  }
  (processed_dir / "dt_dance.json").write_text(json.dumps(track_data), encoding="utf-8")

  out_files = export_parquet(processed_dir, tmp_path)
  assert "tracks" in out_files and "measures" in out_files
  assert out_files["tracks"].exists()
  assert out_files["measures"].exists()

  # Read with pyarrow
  tracks_table = pq.read_table(out_files["tracks"])
  assert tracks_table.num_rows == 1
  assert "track_id" in tracks_table.column_names

  measures_table = pq.read_table(out_files["measures"])
  assert measures_table.num_rows == 1
  assert "time_signature" in measures_table.column_names
