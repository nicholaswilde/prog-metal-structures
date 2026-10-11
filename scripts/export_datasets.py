#!/usr/bin/env python3
"""Unified relational SQLite and columnar Parquet dataset exporter.

Exports normalized processed datasets to:
- data/processed/prog_metal.db (SQLite)
- data/processed/tracks.parquet
- data/processed/measures.parquet

Adheres strictly to 2-space indentation.
"""

from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import sqlite3
import pyarrow as pa
import pyarrow.parquet as pq


def slugify(text: str) -> str:
  """Convert string to identifier slug."""
  import re

  slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
  return re.sub(r"[-\s]+", "_", slug) or "unknown"


def export_sqlite(
  processed_dir: Path = Path("data/processed"),
  db_path: Path = Path("data/processed/prog_metal.db"),
) -> Path:
  """Export processed JSON files into a normalized, indexed SQLite database."""
  db_path.parent.mkdir(parents=True, exist_ok=True)
  if db_path.exists():
    db_path.unlink()

  conn = sqlite3.connect(db_path)
  cur = conn.cursor()
  cur.execute("PRAGMA foreign_keys = ON;")

  # Create tables
  cur.execute("""
    CREATE TABLE artists (
      artist_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      country TEXT,
      formed_year INTEGER,
      genres TEXT,
      total_parsed_tracks INTEGER DEFAULT 0
    );
  """)

  cur.execute("""
    CREATE TABLE tracks (
      track_id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      artist_id TEXT,
      artist TEXT NOT NULL,
      album TEXT,
      year INTEGER,
      total_measures INTEGER NOT NULL,
      default_tempo_bpm REAL,
      default_time_signature TEXT,
      FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
    );
  """)

  cur.execute("""
    CREATE TABLE sections (
      section_id INTEGER PRIMARY KEY AUTOINCREMENT,
      track_id TEXT NOT NULL,
      name TEXT NOT NULL,
      start_measure INTEGER NOT NULL,
      end_measure INTEGER NOT NULL,
      FOREIGN KEY (track_id) REFERENCES tracks(track_id)
    );
  """)

  cur.execute("""
    CREATE TABLE measures (
      measure_id INTEGER PRIMARY KEY AUTOINCREMENT,
      track_id TEXT NOT NULL,
      measure_number INTEGER NOT NULL,
      time_signature TEXT NOT NULL,
      tempo_bpm REAL,
      section_name TEXT,
      FOREIGN KEY (track_id) REFERENCES tracks(track_id)
    );
  """)

  cur.execute("""
    CREATE TABLE complexity_metrics (
      track_id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      artist TEXT NOT NULL,
      total_measures INTEGER NOT NULL,
      unique_meters INTEGER NOT NULL,
      shift_frequency REAL NOT NULL,
      metric_entropy REAL NOT NULL,
      meter_distribution TEXT,
      transition_matrix TEXT,
      FOREIGN KEY (track_id) REFERENCES tracks(track_id)
    );
  """)

  # Insert artists
  artists_dir = processed_dir / "artists"
  if artists_dir.exists():
    for f in sorted(artists_dir.glob("*.json")):
      data = json.loads(f.read_text(encoding="utf-8"))
      cur.execute(
        """
        INSERT INTO artists (artist_id, name, country, formed_year, genres, total_parsed_tracks)
        VALUES (?, ?, ?, ?, ?, ?)
      """,
        (
          data.get("artist_id", f.stem),
          data.get("name", f.stem.replace("_", " ").title()),
          data.get("country"),
          data.get("formed_year"),
          json.dumps(data.get("genres", [])),
          data.get("total_parsed_tracks", 0),
        ),
      )

  # Insert tracks, sections, and measures
  track_files = sorted(f for f in processed_dir.glob("*.json") if f.is_file())
  for f in track_files:
    track = json.loads(f.read_text(encoding="utf-8"))
    track_id = track.get("track_id", f.stem)
    artist_name = track.get("artist", "Unknown")
    artist_id = slugify(artist_name)

    # Ensure artist exists in artists table if not present
    cur.execute("SELECT 1 FROM artists WHERE artist_id = ?", (artist_id,))
    if not cur.fetchone():
      cur.execute(
        """
        INSERT INTO artists (artist_id, name, total_parsed_tracks)
        VALUES (?, ?, ?)
      """,
        (artist_id, artist_name, 1),
      )

    cur.execute(
      """
      INSERT INTO tracks (
        track_id, title, artist_id, artist, album, year,
        total_measures, default_tempo_bpm, default_time_signature
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
        track_id,
        track.get("title", f.stem),
        artist_id,
        artist_name,
        track.get("album"),
        track.get("year"),
        track.get("total_measures", len(track.get("measures", []))),
        track.get("default_tempo_bpm"),
        track.get("default_time_signature"),
      ),
    )

    for sec in track.get("sections", []):
      cur.execute(
        """
        INSERT INTO sections (track_id, name, start_measure, end_measure)
        VALUES (?, ?, ?, ?)
      """,
        (
          track_id,
          sec.get("name", "Unknown"),
          sec.get("start_measure", 1),
          sec.get("end_measure", 1),
        ),
      )

    measure_rows = [
      (
        track_id,
        m.get("measure_number", idx + 1),
        m.get("time_signature", "4/4"),
        m.get("tempo_bpm"),
        m.get("section_name"),
      )
      for idx, m in enumerate(track.get("measures", []))
    ]
    cur.executemany(
      """
      INSERT INTO measures (track_id, measure_number, time_signature, tempo_bpm, section_name)
      VALUES (?, ?, ?, ?, ?)
    """,
      measure_rows,
    )

  # Insert complexity metrics
  comp_file = processed_dir / "analysis" / "metric_complexity.json"
  if comp_file.exists():
    comp_data = json.loads(comp_file.read_text(encoding="utf-8"))
    rows = comp_data if isinstance(comp_data, list) else comp_data.get("tracks", [])
    for row in rows:
      cur.execute(
        """
        INSERT OR REPLACE INTO complexity_metrics (
          track_id, title, artist, total_measures, unique_meters,
          shift_frequency, metric_entropy, meter_distribution, transition_matrix
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
        (
          row.get("track_id"),
          row.get("title"),
          row.get("artist"),
          row.get("total_measures", 0),
          row.get("unique_meters", 0),
          row.get("shift_frequency", 0.0),
          row.get("metric_entropy", 0.0),
          json.dumps(row.get("meter_distribution", {})),
          json.dumps(row.get("transition_matrix", {})),
        ),
      )

  # Create indexes
  cur.execute("CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist_id);")
  cur.execute("CREATE INDEX IF NOT EXISTS idx_measures_track ON measures(track_id);")
  cur.execute("CREATE INDEX IF NOT EXISTS idx_measures_meter ON measures(time_signature);")
  cur.execute("CREATE INDEX IF NOT EXISTS idx_sections_track ON sections(track_id);")

  conn.commit()
  conn.close()
  return db_path


def export_parquet(
  processed_dir: Path = Path("data/processed"),
  output_dir: Path = Path("data/processed"),
) -> Dict[str, Path]:
  """Export processed JSON tracks and measures into columnar Parquet files."""
  output_dir.mkdir(parents=True, exist_ok=True)
  track_files = sorted(f for f in processed_dir.glob("*.json") if f.is_file())

  tracks_records: List[Dict[str, Any]] = []
  measures_records: List[Dict[str, Any]] = []

  for f in track_files:
    track = json.loads(f.read_text(encoding="utf-8"))
    track_id = track.get("track_id", f.stem)
    artist = track.get("artist", "Unknown")
    album = track.get("album", "") or ""
    year = int(track["year"]) if track.get("year") else None
    default_tempo = float(track["default_tempo_bpm"]) if track.get("default_tempo_bpm") else None
    default_meter = track.get("default_time_signature") or "4/4"
    total_measures = int(track.get("total_measures", len(track.get("measures", []))))

    tracks_records.append(
      {
        "track_id": track_id,
        "title": track.get("title", f.stem),
        "artist": artist,
        "album": album,
        "year": year,
        "default_tempo_bpm": default_tempo,
        "default_time_signature": default_meter,
        "total_measures": total_measures,
        "sections_count": len(track.get("sections", [])),
      }
    )

    for idx, m in enumerate(track.get("measures", [])):
      measures_records.append(
        {
          "track_id": track_id,
          "measure_number": int(m.get("measure_number", idx + 1)),
          "time_signature": str(m.get("time_signature", "4/4")),
          "tempo_bpm": float(m["tempo_bpm"]) if m.get("tempo_bpm") is not None else None,
          "section_name": m.get("section_name"),
        }
      )

  tracks_table = pa.Table.from_pylist(tracks_records)
  measures_table = pa.Table.from_pylist(measures_records)

  tracks_path = output_dir / "tracks.parquet"
  measures_path = output_dir / "measures.parquet"

  pq.write_table(tracks_table, tracks_path, compression="snappy")
  pq.write_table(measures_table, measures_path, compression="snappy")

  return {"tracks": tracks_path, "measures": measures_path}


def main() -> None:
  """CLI entrypoint for exporting datasets."""
  parser = argparse.ArgumentParser(description="Export datasets to SQLite and Parquet")
  parser.add_argument("--sqlite", action="store_true", help="Export SQLite database only")
  parser.add_argument("--parquet", action="store_true", help="Export Parquet tables only")
  parser.add_argument(
    "--processed-dir",
    type=Path,
    default=Path("data/processed"),
    help="Processed directory path",
  )
  args = parser.parse_args()

  run_all = not (args.sqlite or args.parquet)

  if run_all or args.sqlite:
    db = export_sqlite(processed_dir=args.processed_dir)
    print(f"[+] Exported SQLite database: {db}")

  if run_all or args.parquet:
    files = export_parquet(processed_dir=args.processed_dir)
    print(f"[+] Exported Parquet tables: {files['tracks']}, {files['measures']}")


if __name__ == "__main__":
  main()
