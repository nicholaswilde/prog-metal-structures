#!/usr/bin/env python3
"""Dataset expansion assistant and workflow automation script.

Streamlines expanding the progressive metal dataset:
1. Inspects remote tab formats on gprotab.net (differentiating supported GP3/4/5 from GPX).
2. Downloads compatible tabs for requested artists and tracks.
3. Verifies canonical discography mappings.
4. Orchestrates the end-to-end ingestion, analysis, export, and gaps reporting pipeline.

Strictly 2-space indentation.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
  import httpx
except ImportError:
  httpx = None

try:
  from scripts.discography import normalize_title, verify_discography
  from scripts.scrape_gp import GuitarProScraper, slugify
except ImportError:
  from discography import normalize_title, verify_discography
  from scrape_gp import GuitarProScraper, slugify

SUPPORTED_EXTENSIONS = {".gp3", ".gp4", ".gp5"}


def inspect_artist_tabs(
  artist_name: str,
  output_dir: Optional[Path] = None,
  limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
  """Inspect remote tabs on gprotab.net and detect their file format compatibility."""
  target_dir = output_dir or Path("data/raw/guitar_pro")
  scraper = GuitarProScraper(target_dir)

  slug = scraper.find_artist_slug(artist_name)
  if not slug:
    print(f"[!] Artist '{artist_name}' not found on gprotab.net")
    return []

  raw_tabs = scraper.list_artist_tabs(slug)
  if limit:
    raw_tabs = raw_tabs[:limit]

  inspected: List[Dict[str, Any]] = []
  print(f"[*] Inspecting {len(raw_tabs)} tabs for '{artist_name}' on gprotab.net...")

  for tab in raw_tabs:
    title = tab["title"]
    url = tab["url"]
    download_url = f"{url}?download"
    ext = ".unknown"
    status = "UNKNOWN"

    try:
      resp = scraper.client.head(download_url, follow_redirects=True, timeout=5.0)
      cd = resp.headers.get("content-disposition", "")
      match = re.search(r'filename="?([^";]+)"?', cd)
      if match:
        orig_name = match.group(1)
        ext = Path(orig_name).suffix.lower()
      else:
        ext = Path(url.split("/")[-1]).suffix.lower() or ".unknown"
    except Exception:
      ext = ".err"

    is_supported = ext in SUPPORTED_EXTENSIONS
    status = (
      "SUPPORTED"
      if is_supported
      else ("UNSUPPORTED (GPX)" if ext == ".gpx" else f"UNSUPPORTED ({ext})")
    )

    inspected.append(
      {
        "title": title,
        "url": url,
        "extension": ext,
        "supported": is_supported,
        "status": status,
      }
    )

  return inspected


def find_best_tab_for_track(
  artist_tabs: List[Dict[str, str]],
  track_query: str,
  scraper: GuitarProScraper,
) -> Optional[Tuple[Dict[str, str], str]]:
  """Find the best compatible (GP3/4/5) tab version matching the track query."""
  clean_query = normalize_title(track_query)
  matched_tabs = []

  for tab in artist_tabs:
    clean_title = normalize_title(tab["title"])
    if clean_query in clean_title or clean_title in clean_query:
      matched_tabs.append(tab)

  if not matched_tabs:
    return None

  # Probe candidate tabs for format compatibility
  for candidate in matched_tabs:
    download_url = f"{candidate['url']}?download"
    try:
      resp = scraper.client.head(download_url, follow_redirects=True, timeout=5.0)
      cd = resp.headers.get("content-disposition", "")
      match = re.search(r'filename="?([^";]+)"?', cd)
      orig_name = match.group(1) if match else candidate["url"].split("/")[-1]
      ext = Path(orig_name).suffix.lower()
      if ext in SUPPORTED_EXTENSIONS:
        return candidate, ext
    except Exception:
      continue

  return None


def batch_download_tracks(
  artist_name: str,
  tracks: List[str],
  output_dir: Optional[Path] = None,
) -> List[Path]:
  """Download supported tabs for multiple tracks of a given artist."""
  target_dir = output_dir or Path("data/raw/guitar_pro")
  target_dir.mkdir(parents=True, exist_ok=True)
  scraper = GuitarProScraper(target_dir)

  slug = scraper.find_artist_slug(artist_name)
  if not slug:
    print(f"[!] Artist '{artist_name}' not found on gprotab.net")
    return []

  artist_tabs = scraper.list_artist_tabs(slug)
  downloaded_files: List[Path] = []
  artist_key = slugify(artist_name)

  for track in tracks:
    print(f"[*] Locating tab for '{artist_name}' — '{track}'...")
    best = find_best_tab_for_track(artist_tabs, track, scraper)
    if not best:
      print(f"[-] No compatible (GP3/4/5) tab found for '{track}'")
      continue

    tab, ext = best
    dest_filename = f"{artist_key}-{slugify(track)}{ext}"
    dest_path = target_dir / dest_filename

    if dest_path.exists():
      print(f"[=] Tab already exists: {dest_filename}")
      downloaded_files.append(dest_path)
      continue

    saved = scraper.download_tab(tab["url"], dest_filename)
    if saved:
      print(f"[+] Downloaded: {saved.name}")
      downloaded_files.append(saved)
    else:
      print(f"[!] Failed to download: {tab['title']}")

  return downloaded_files


def run_pipeline_sync() -> int:
  """Run the end-to-end dataset processing, analysis, export, and gaps update pipeline."""
  print("\n[*] Running end-to-end dataset pipeline sync...")
  steps = [
    ("task: parse-gp", [sys.executable, "scripts/parse_gp.py"]),
    ("task: parse-midi", [sys.executable, "scripts/parse_midi.py"]),
    ("task: build-artists", [sys.executable, "scripts/build_artist_metadata.py"]),
    ("task: analyze", [sys.executable, "scripts/analyze_structure.py"]),
    ("task: export:sqlite", [sys.executable, "scripts/export_datasets.py", "--sqlite"]),
    ("task: export:parquet", [sys.executable, "scripts/export_datasets.py", "--parquet"]),
    ("task: export:ai", [sys.executable, "scripts/export_ai.py"]),
    ("task: gaps:update", [sys.executable, "scripts/audit_gaps.py", "--update-docs"]),
  ]

  for name, cmd in steps:
    print(f"[*] Executing {name}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
      print(f"[!] Error in {name}:\n{res.stderr or res.stdout}")
      return res.returncode

  print("[+] End-to-end dataset pipeline sync completed successfully.")
  return 0


def main() -> int:
  """CLI entrypoint for dataset expansion."""
  parser = argparse.ArgumentParser(
    description="Automate progressive metal dataset expansion (inspect, download, verify, sync)."
  )
  parser.add_argument(
    "--artist", type=str, help="Artist name (e.g. 'Animals as Leaders', 'Meshuggah')"
  )
  parser.add_argument(
    "--tracks",
    type=str,
    help="Comma-separated track titles to download (e.g. 'CAFO,The Woven Web')",
  )
  parser.add_argument(
    "--inspect",
    action="store_true",
    help="Inspect available remote tabs on gprotab.net and show format compatibility",
  )
  parser.add_argument(
    "--download",
    action="store_true",
    help="Download supported tabs for the requested artist and tracks",
  )
  parser.add_argument(
    "--verify",
    action="store_true",
    help="Verify canonical discography metadata completeness",
  )
  parser.add_argument(
    "--sync",
    action="store_true",
    help="Run the complete end-to-end ingestion and export pipeline",
  )
  parser.add_argument(
    "--all",
    action="store_true",
    help="Execute full flow: download tabs, verify discography, and sync pipeline",
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/raw/guitar_pro"),
    help="Output directory for raw Guitar Pro tabs",
  )

  args = parser.parse_args()

  # 1. Inspect tabs
  if args.inspect:
    if not args.artist:
      print("[!] --artist is required for --inspect")
      return 1
    tabs = inspect_artist_tabs(args.artist, args.output_dir)
    print(f"\nAvailable tabs for '{args.artist}':")
    for t in tabs:
      marker = "[OK]" if t["supported"] else "[--]"
      print(f"  {marker} {t['title']:40} | Ext: {t['extension']:6} | Status: {t['status']}")
    return 0

  # 2. Download tabs
  if args.download or args.all:
    if not args.artist:
      print("[!] --artist is required for --download")
      return 1
    track_list = [t.strip() for t in args.tracks.split(",") if t.strip()] if args.tracks else []
    if not track_list:
      print("[!] --tracks <track1,track2,...> is required for --download")
      return 1

    downloaded = batch_download_tracks(args.artist, track_list, args.output_dir)
    print(f"[+] Downloaded {len(downloaded)} tabs for '{args.artist}'.")

  # 3. Verify discography mappings
  if args.verify or args.all:
    report = verify_discography()
    print(f"[*] Verified {report['total_tracks']} tracks: {report['complete_tracks']} complete.")
    if report["missing_count"] > 0:
      print(f"[!] Warning: {report['missing_count']} tracks missing discography mapping:")
      for item in report["missing_tracks"]:
        print(f"    - {item['file']}: {item['artist']} - {item['title']}")
      if not args.all:
        return 1

  # 4. Pipeline sync
  if args.sync or args.all:
    ret = run_pipeline_sync()
    if ret != 0:
      return ret

  if not (args.inspect or args.download or args.verify or args.sync or args.all):
    parser.print_help()

  return 0


if __name__ == "__main__":
  sys.exit(main())
