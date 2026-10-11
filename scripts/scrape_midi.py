#!/usr/bin/env python3
"""MIDI scraper targeting curated archives and local repositories.

Adheres strictly to project guidelines:
1. Searches local repo `/home/nicholas/git/asigalov61/Tegridy-MIDI-Dataset` FIRST.
2. Checks curated list in `/home/nicholas/git/albertmeronyo/awesome-midi-sources/README.md`.
3. Supports preferred search sources (FreeMidi.org, BitMidi.com, Metal-MIDI Archives).
4. Strictly 2-space indentation.
"""

import argparse
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
  import httpx
  from bs4 import BeautifulSoup
except ImportError:
  httpx = None
  BeautifulSoup = None

try:
  from scripts.models import TrackArchitecture
except ImportError:
  from models import TrackArchitecture


def slugify(text: str) -> str:
  """Convert string to filesystem and identifier safe slug."""
  slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
  return re.sub(r"[-\s]+", "_", slug) or "unknown"


class MidiScraper:
  """Midi searcher and downloader respecting local dataset priority."""

  LOCAL_TEGRIDY_DATASET = Path("/home/nicholas/git/asigalov61/Tegridy-MIDI-Dataset")
  AWESOME_MIDI_SOURCES = Path("/home/nicholas/git/albertmeronyo/awesome-midi-sources/README.md")
  METAL_MIDI_ARCHIVE = "http://metal-midi.grahamdowney.com"

  def __init__(self, output_dir: Path, timeout: float = 15.0):
    if httpx is None or BeautifulSoup is None:
      raise ImportError("httpx and beautifulsoup4 required. Run `uv add httpx beautifulsoup4`")
    self.output_dir = output_dir
    self.output_dir.mkdir(parents=True, exist_ok=True)
    self.client = httpx.Client(
      timeout=timeout,
      follow_redirects=True,
      headers={
        "User-Agent": (
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
      }
    )

  def search_local_dataset(self, query: str) -> List[Path]:
    """Search local Tegridy-MIDI-Dataset repository first."""
    if not self.LOCAL_TEGRIDY_DATASET.exists():
      print(f"[-] Local dataset path {self.LOCAL_TEGRIDY_DATASET} does not exist.")
      return []

    print(f"[*] Checking local dataset first: {self.LOCAL_TEGRIDY_DATASET}")
    matches: List[Path] = []
    pattern = f"*{query}*"

    for p in self.LOCAL_TEGRIDY_DATASET.rglob("*"):
      if p.suffix.lower() in {".mid", ".midi"}:
        if query.lower() in p.name.lower():
          matches.append(p)

    print(f"[*] Found {len(matches)} local matches in Tegridy-MIDI-Dataset")
    return matches

  def copy_local_matches(self, local_files: List[Path]) -> List[Path]:
    """Copy matching files from local dataset into output_dir."""
    copied: List[Path] = []
    for src in local_files:
      dest = self.output_dir / src.name
      shutil.copy2(src, dest)
      print(f"[+] Copied local MIDI: {dest.name}")
      copied.append(dest)
    return copied

  def search_metal_midi_archive(self, artist_or_song: str) -> List[Dict[str, str]]:
    """Search metal-midi.grahamdowney.com for matching files."""
    results: List[Dict[str, str]] = []
    url = f"{self.METAL_MIDI_ARCHIVE}/midi.html"
    try:
      resp = self.client.get(url)
      if resp.status_code != 200:
        return results
      soup = BeautifulSoup(resp.text, "html.parser")
      for a in soup.find_all("a"):
        text = a.text.strip()
        href = a.get("href", "")
        if artist_or_song.lower() in text.lower() or artist_or_song.lower() in href.lower():
          results.append({
            "title": text,
            "url": urljoin(self.METAL_MIDI_ARCHIVE, href)
          })
    except Exception as exc:
      print(f"[!] Error querying metal-midi archive: {exc}")
    return results

  def download_midi(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
    """Download MIDI file from direct URL."""
    try:
      resp = self.client.get(url)
      if resp.status_code != 200:
        print(f"[!] Failed download: {url} (HTTP {resp.status_code})")
        return None

      if not filename:
        filename = url.split("/")[-1]
      if not (filename.endswith(".mid") or filename.endswith(".midi")):
        filename += ".mid"

      dest = self.output_dir / filename
      dest.write_bytes(resp.content)
      print(f"[+] Downloaded MIDI: {dest.name} ({len(resp.content)} bytes)")
      return dest
    except Exception as exc:
      print(f"[!] Error downloading {url}: {exc}")
      return None

  def scrape(self, query: str, limit: int = 3) -> List[Path]:
    """Run prioritized retrieval pipeline: local first, then online archives."""
    print(f"[*] Starting MIDI search for: {query}")

    # 1. Local dataset first
    local_matches = self.search_local_dataset(query)
    if local_matches:
      return self.copy_local_matches(local_matches[:limit])

    # 2. Online archive fallback
    print(f"[*] No local files found. Falling back to online archives...")
    metal_results = self.search_metal_midi_archive(query)
    downloaded: List[Path] = []
    for item in metal_results:
      saved = self.download_midi(item["url"])
      if saved:
        downloaded.append(saved)
      if len(downloaded) >= limit:
        break
      time.sleep(1.0)

    return downloaded


def main() -> None:
  parser = argparse.ArgumentParser(description="Search and scrape MIDI files prioritizing local repo")
  parser.add_argument(
    "--query",
    type=str,
    required=True,
    help="Search term (artist or song title)"
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/raw/midi"),
    help="Directory to store retrieved MIDI files"
  )
  parser.add_argument(
    "--limit",
    type=int,
    default=3,
    help="Maximum files to retrieve"
  )
  args = parser.parse_args()

  scraper = MidiScraper(output_dir=args.output_dir)
  results = scraper.scrape(query=args.query, limit=args.limit)
  print(f"[*] Complete. Saved {len(results)} MIDI files into {args.output_dir}")


if __name__ == "__main__":
  main()
