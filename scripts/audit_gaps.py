#!/usr/bin/env python3
"""Dataset completeness and gap audit tool.

Audits parsed tracks against album discographies and computes structural completeness metrics.
Generates docs/dataset_gaps.md documentation ledger.

Adheres strictly to 2-space indentation.
"""

from pathlib import Path
from typing import Any, Dict, List
import argparse
import json


def audit_gaps(processed_dir: Path = Path("data/processed")) -> Dict[str, Any]:
  """Audit album coverage and attribute completeness across processed tracks."""
  artists_dir = processed_dir / "artists"
  album_records: List[Dict[str, Any]] = []
  total_artists = 0
  total_tracks_expected = 0
  total_tracks_parsed_discography = 0

  if artists_dir.exists():
    for f in sorted(artists_dir.glob("*.json")):
      try:
        artist_data = json.loads(f.read_text(encoding="utf-8"))
      except Exception:
        continue

      total_artists += 1
      artist_name = artist_data.get("name", f.stem.replace("_", " ").title())
      albums = artist_data.get("albums", [])

      for alb in albums:
        title = alb.get("title", "Unknown Album")
        year = alb.get("release_year")
        total = alb.get("total_tracks", 0)
        parsed = alb.get("parsed_tracks_count", len(alb.get("track_ids", [])))
        missing = max(0, total - parsed)
        coverage_pct = round((parsed / total) * 100, 1) if total > 0 else 0.0

        total_tracks_expected += total
        total_tracks_parsed_discography += parsed

        album_records.append(
          {
            "artist": artist_name,
            "album": title,
            "year": year,
            "total_tracks": total,
            "parsed_tracks": parsed,
            "missing_tracks": missing,
            "coverage_pct": coverage_pct,
          }
        )

  # Audit individual track quality
  track_files = sorted(f for f in processed_dir.glob("*.json") if f.is_file())
  total_tracks_parsed = len(track_files)

  missing_album = 0
  missing_year = 0
  missing_default_tempo = 0
  missing_sections = 0
  missing_measures = 0

  for f in track_files:
    try:
      track = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
      continue

    if not track.get("album"):
      missing_album += 1
    if not track.get("year"):
      missing_year += 1
    if not track.get("default_tempo_bpm") or track.get("default_tempo_bpm") <= 0:
      missing_default_tempo += 1
    if not track.get("sections"):
      missing_sections += 1
    if not track.get("measures"):
      missing_measures += 1

  overall_coverage = (
    round((total_tracks_parsed_discography / total_tracks_expected) * 100, 1)
    if total_tracks_expected > 0
    else 0.0
  )

  return {
    "total_artists": total_artists,
    "total_albums": len(album_records),
    "total_tracks_expected": total_tracks_expected,
    "total_tracks_parsed": total_tracks_parsed,
    "total_tracks_parsed_discography": total_tracks_parsed_discography,
    "overall_coverage_pct": overall_coverage,
    "albums": album_records,
    "quality": {
      "total_tracks_checked": total_tracks_parsed,
      "missing_album_count": missing_album,
      "missing_year_count": missing_year,
      "missing_default_tempo_count": missing_default_tempo,
      "missing_sections_count": missing_sections,
      "missing_measures_count": missing_measures,
    },
  }


def generate_gaps_report(stats: Dict[str, Any]) -> str:
  """Format audit statistics into a GitHub-flavored Markdown report."""
  total_art = stats["total_artists"]
  total_alb = stats["total_albums"]
  exp = stats["total_tracks_expected"]
  parsed = stats["total_tracks_parsed"]
  coverage = stats["overall_coverage_pct"]
  quality = stats["quality"]

  # Sort albums by lowest coverage percentage, then most missing tracks
  sorted_albums = sorted(
    stats["albums"],
    key=lambda x: (x["coverage_pct"], -x["missing_tracks"]),
  )

  album_rows: List[str] = []
  for a in sorted_albums:
    status = "**COMPLETE**" if a["missing_tracks"] == 0 else f"{a['missing_tracks']} missing"
    album_rows.append(
      f"| {a['artist']} | {a['album']} | {a['year'] or 'N/A'} | "
      f"{a['parsed_tracks']} / {a['total_tracks']} | {a['coverage_pct']}% | {status} |"
    )
  albums_table = "\n".join(album_rows) if album_rows else "| None | - | - | - | - | - |"

  def q_pct(missing: int) -> str:
    total = quality["total_tracks_checked"]
    if total == 0:
      return "100.0%"
    return f"{round(((total - missing) / total) * 100, 1)}%"

  total_checked = quality["total_tracks_checked"]

  return (
    f"""# Progressive Metal Dataset: Data Gap & Completeness Report

**Overall Discography Coverage**: {coverage}%
**Parsed Tracks**: {parsed} | **Expected Discography Tracks**: {exp}
**Tracked Artists**: {total_art} | **Tracked Albums**: {total_alb}

---

## 1. Discography Coverage by Album

| Artist | Album | Year | Parsed / Total | Coverage % | Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
{albums_table}

---

## 2. Structural & Attribute Quality Metrics

| Quality Metric | Tracks Checked | Complete | Missing | Completeness % | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Album Title** | {total_checked} | {total_checked - quality["missing_album_count"]} | {quality["missing_album_count"]} | {q_pct(quality["missing_album_count"])} | {"**OK**" if quality["missing_album_count"] == 0 else "Needs Review"} |
| **Release Year** | {total_checked} | {total_checked - quality["missing_year_count"]} | {quality["missing_year_count"]} | {q_pct(quality["missing_year_count"])} | {"**OK**" if quality["missing_year_count"] == 0 else "Needs Review"} |
| **Default Tempo (BPM)** | {total_checked} | {total_checked - quality["missing_default_tempo_count"]} | {quality["missing_default_tempo_count"]} | {q_pct(quality["missing_default_tempo_count"])} | {"**OK**" if quality["missing_default_tempo_count"] == 0 else "Needs Review"} |
| **Formal Section Breakdown** | {total_checked} | {total_checked - quality["missing_sections_count"]} | {quality["missing_sections_count"]} | {q_pct(quality["missing_sections_count"])} | {"**OK**" if quality["missing_sections_count"] == 0 else "Backlog Target"} |
| **Measure Sequence Data** | {total_checked} | {total_checked - quality["missing_measures_count"]} | {quality["missing_measures_count"]} | {q_pct(quality["missing_measures_count"])} | {"**OK**" if quality["missing_measures_count"] == 0 else "Critical"} |

---

## 3. High-Priority Ingestion Backlog

Top albums recommended for upcoming ingestion batches based on missing track counts:

"""
    + "\n".join(
      f"{idx + 1}. **{a['artist']} — *{a['album']}***: {a['parsed_tracks']}/{a['total_tracks']} parsed ({a['missing_tracks']} tracks remaining)"
      for idx, a in enumerate(sorted_albums[:8])
      if a["missing_tracks"] > 0
    )
    + "\n"
  )


def write_gaps_report(
  stats: Dict[str, Any], output_path: Path = Path("docs/dataset_gaps.md")
) -> Path:
  """Write markdown report to disk."""
  output_path.parent.mkdir(parents=True, exist_ok=True)
  report = generate_gaps_report(stats)
  output_path.write_text(report, encoding="utf-8")
  return output_path


def main() -> None:
  """CLI entrypoint for dataset gap auditor."""
  parser = argparse.ArgumentParser(description="Audit dataset completeness and album gaps")
  parser.add_argument(
    "--processed-dir",
    type=Path,
    default=Path("data/processed"),
    help="Processed directory path",
  )
  parser.add_argument(
    "--output",
    type=Path,
    default=Path("docs/dataset_gaps.md"),
    help="Path for generated Markdown report",
  )
  parser.add_argument(
    "--update-docs",
    action="store_true",
    help="Save report to docs/dataset_gaps.md",
  )
  parser.add_argument(
    "--json",
    action="store_true",
    help="Output raw JSON statistics",
  )
  args = parser.parse_args()

  stats = audit_gaps(processed_dir=args.processed_dir)

  if args.json:
    print(json.dumps(stats, indent=2))
    return

  if args.update_docs or not args.json:
    path = write_gaps_report(stats, output_path=args.output)
    print(f"[+] Dataset gaps report generated: {path}")

  print(
    f"[*] Overall Coverage: {stats['overall_coverage_pct']}% across {stats['total_albums']} albums"
  )
  print(
    f"[*] Parsed Tracks: {stats['total_tracks_parsed']} / Expected: {stats['total_tracks_expected']}"
  )


if __name__ == "__main__":
  main()
