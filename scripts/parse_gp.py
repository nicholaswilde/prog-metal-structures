#!/usr/bin/env python3
"""Parse Guitar Pro tabs (.gp3, .gp4, .gp5) into structured track architecture JSON."""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
  import guitarpro
except ImportError:
  guitarpro = None

try:
  from scripts.discography import lookup_track_metadata
except ImportError:
  from discography import lookup_track_metadata


def slugify(text: str) -> str:
  """Convert string to filesystem and identifier safe slug."""
  slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
  return re.sub(r"[-\s]+", "_", slug) or "unknown"


def parse_gp_file(file_path: Path) -> Dict[str, Any]:
  """Extract measure-by-measure meter, tempo, and sections from Guitar Pro file."""
  if guitarpro is None:
    raise ImportError("PyGuitarPro is required. Install via: pip install PyGuitarPro")

  song = guitarpro.parse(str(file_path))

  raw_title = song.title.strip().strip("\"'") if getattr(song, "title", None) else ""
  raw_artist = song.artist.strip().strip("\"'") if getattr(song, "artist", None) else ""

  # Normalize common title and artist misspellings in tabs
  if "millenium" in raw_title.lower():
    raw_title = re.sub(r"millenium", "millennium", raw_title, flags=re.IGNORECASE)
  if "dream theather" in raw_artist.lower():
    raw_artist = "Dream Theater"
  elif raw_artist.lower() in {"tosin abasi", "tosin"}:
    raw_artist = "Animals as Leaders"

  # Fallback to file name stem if artist or title is missing
  if not raw_artist or raw_artist.lower() in {"unknown", "unknown artist"} or not raw_title:
    stem = file_path.stem
    matched = False
    for candidate in [
      "dream-theater",
      "dream_theater",
      "animals-as-leaders",
      "animals_as_leaders",
      "between-the-buried-and-me",
      "between_the_buried_and_me",
      "meshuggah",
    ]:
      if stem.startswith(candidate + "-"):
        if not raw_artist or raw_artist.lower() in {"unknown", "unknown artist"}:
          raw_artist = candidate.replace("-", " ").replace("_", " ").title()
        if not raw_title:
          raw_title = stem[len(candidate) + 1 :].replace("_", " ").title()
        matched = True
        break
    if not matched:
      parts = stem.split("-", 1)
      if len(parts) == 2:
        if not raw_artist or raw_artist.lower() in {"unknown", "unknown artist"}:
          raw_artist = parts[0].replace("_", " ").title()
        if not raw_title:
          raw_title = parts[1].replace("_", " ").title()
      elif not raw_artist:
        raw_artist = "Unknown Artist"

  # Clean leading artist prefix from title (e.g. "Meshuggah - Spasm")
  if raw_artist and raw_title.lower().startswith(f"{raw_artist.lower()} - "):
    raw_title = raw_title[len(raw_artist) + 3 :].strip()

  title = (raw_title or file_path.stem.replace("_", " ").title()).strip().strip("\"'")
  artist = raw_artist
  artist_key = slugify(artist)
  canonical_album, canonical_year = lookup_track_metadata(artist_key, title)
  album = canonical_album or (
    song.album.strip().strip("\"'") if getattr(song, "album", None) else ""
  )
  year = canonical_year
  track_id = f"{artist_key}_{slugify(title)}"

  measures_data: List[Dict[str, Any]] = []
  sections: List[Dict[str, Any]] = []
  current_section: Optional[Dict[str, Any]] = None

  current_tempo: float = 120.0
  current_ts: str = "4/4"

  for header in song.measureHeaders:
    measure_num = getattr(header, "number", len(measures_data) + 1)

    if hasattr(header, "tempo") and header.tempo is not None:
      current_tempo = float(header.tempo.value)

    if hasattr(header, "timeSignature") and header.timeSignature is not None:
      ts_num = header.timeSignature.numerator
      ts_den = header.timeSignature.denominator.value
      current_ts = f"{ts_num}/{ts_den}"

    section_label = None
    if getattr(header, "marker", None) and header.marker.title:
      section_label = header.marker.title.strip()
      if current_section is not None:
        current_section["end_measure"] = measure_num - 1
      current_section = {"label": section_label, "start_measure": measure_num}
      sections.append(current_section)

    measure_entry: Dict[str, Any] = {
      "measure_number": measure_num,
      "time_signature": current_ts,
      "tempo_bpm": round(current_tempo, 2),
    }

    if section_label:
      measure_entry["section_label"] = section_label

    measures_data.append(measure_entry)

  if current_section is not None and measures_data:
    current_section["end_measure"] = measures_data[-1]["measure_number"]

  total_measures = len(measures_data)
  default_ts = measures_data[0]["time_signature"] if measures_data else "4/4"
  default_tempo = measures_data[0]["tempo_bpm"] if measures_data else 120.0

  return {
    "track_id": track_id,
    "title": title,
    "artist": artist,
    "album": album,
    "year": year,
    "source_file": file_path.name,
    "source_format": file_path.suffix.lstrip(".").lower(),
    "total_measures": total_measures,
    "default_tempo_bpm": default_tempo,
    "default_time_signature": default_ts,
    "sections": sections,
    "measures": measures_data,
  }


def process_directory(raw_dir: Path, output_dir: Path) -> List[Path]:
  """Iterate over Guitar Pro files in raw_dir and save extracted JSON to output_dir."""
  output_dir.mkdir(parents=True, exist_ok=True)
  valid_exts = {".gp3", ".gp4", ".gp5"}
  created_files: List[Path] = []

  gp_files = [p for p in raw_dir.glob("*") if p.suffix.lower() in valid_exts]
  if not gp_files:
    print(f"[!] No Guitar Pro files found in {raw_dir}")
    return created_files

  for gp_path in gp_files:
    try:
      print(f"[*] Parsing: {gp_path.name}")
      track_data = parse_gp_file(gp_path)
      out_path = output_dir / f"{track_data['track_id']}.json"
      with open(out_path, "w", encoding="utf-8") as f:
        json.dump(track_data, f, indent=2)
      print(f"    -> Saved architecture: {out_path.name} ({track_data['total_measures']} measures)")
      created_files.append(out_path)
    except Exception as exc:
      print(f"[!] Error parsing {gp_path.name}: {exc}")

  return created_files


def main() -> None:
  parser = argparse.ArgumentParser(description="Parse Guitar Pro tab files into structural JSON")
  parser.add_argument(
    "--input-dir",
    type=Path,
    default=Path("data/raw/guitar_pro"),
    help="Directory containing .gp3/.gp4/.gp5 files",
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/processed"),
    help="Directory to write processed JSON datasets",
  )
  args = parser.parse_args()

  process_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
  main()
