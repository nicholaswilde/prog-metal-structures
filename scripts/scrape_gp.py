#!/usr/bin/env python3
"""Guitar Pro scraper targeting repositories like GProTab.net and local archives.

Prioritizes Guitar Pro tabs (.gp3, .gp4, .gp5) over MIDI files.
Adheres to 2-space indentation.
"""

import argparse
import re
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


def slugify(text: str) -> str:
  """Convert string to filesystem and identifier safe slug."""
  slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
  return re.sub(r"[-\s]+", "_", slug) or "unknown"


class GuitarProScraper:
  """Scraper for Guitar Pro files (.gp3, .gp4, .gp5)."""

  BASE_URL = "https://gprotab.net"

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
      },
    )

  def find_artist_slug(self, artist_name: str) -> Optional[str]:
    """Resolve artist name to gprotab.net artist slug."""
    clean_name = artist_name.strip()
    first_char = clean_name[0].lower() if clean_name else "a"
    if not first_char.isalpha():
      first_char = "0-9"

    index_url = f"{self.BASE_URL}/en/artists/{first_char}"
    try:
      resp = self.client.get(index_url)
      if resp.status_code != 200:
        return None
      soup = BeautifulSoup(resp.text, "html.parser")
      for a in soup.find_all("a"):
        text = a.text.strip().lower()
        if text == clean_name.lower():
          href = a.get("href", "")
          # format: /en/tabs/<artist-slug>
          return href.split("/")[-1]
    except Exception as exc:
      print(f"[!] Error resolving artist {artist_name}: {exc}")
    return None

  def list_artist_tabs(self, artist_slug: str) -> List[Dict[str, str]]:
    """List available song tabs for an artist."""
    url = f"{self.BASE_URL}/en/tabs/{artist_slug}"
    tabs = []
    try:
      resp = self.client.get(url)
      if resp.status_code != 200:
        return tabs
      soup = BeautifulSoup(resp.text, "html.parser")
      for a in soup.find_all("a"):
        href = a.get("href", "")
        if f"/en/tabs/{artist_slug}/" in href:
          title = a.text.strip()
          tabs.append({"title": title, "url": urljoin(self.BASE_URL, href)})
    except Exception as exc:
      print(f"[!] Error listing tabs for {artist_slug}: {exc}")
    return tabs

  def download_tab(self, tab_url: str, dest_filename: Optional[str] = None) -> Optional[Path]:
    """Download Guitar Pro file from tab page URL."""
    download_url = f"{tab_url}?download"
    try:
      resp = self.client.get(download_url)
      if resp.status_code != 200:
        print(f"[!] Failed to download from {download_url} (HTTP {resp.status_code})")
        return None

      # Determine filename from Content-Disposition or URL
      filename = dest_filename
      if not filename:
        cd = resp.headers.get("content-disposition", "")
        match = re.search(r'filename="?([^";]+)"?', cd)
        if match:
          filename = match.group(1)
        else:
          filename = f"{slugify(tab_url.split('/')[-1])}.gp5"

      dest_path = self.output_dir / filename
      dest_path.write_bytes(resp.content)
      print(f"[+] Downloaded GP tab: {dest_path.name} ({len(resp.content)} bytes)")
      return dest_path
    except Exception as exc:
      print(f"[!] Error downloading {tab_url}: {exc}")
      return None

  def scrape_artist_tracks(
    self, artist_name: str, track_filter: Optional[str] = None, max_tracks: int = 5
  ) -> List[Path]:
    """Search and download tabs for target artist with optional title filter."""
    print(f"[*] Locating Guitar Pro tabs for: {artist_name}")
    slug = self.find_artist_slug(artist_name)
    if not slug:
      # Try direct slug heuristic
      slug = slugify(artist_name).replace("_", "-")

    tabs = self.list_artist_tabs(slug)
    if not tabs:
      print(f"[!] No tabs found for artist: {artist_name} (slug: {slug})")
      return []

    print(f"[*] Found {len(tabs)} tabs for {artist_name}")
    downloaded: List[Path] = []

    for tab in tabs:
      if track_filter and track_filter.lower() not in tab["title"].lower():
        continue

      saved = self.download_tab(tab["url"])
      if saved:
        downloaded.append(saved)
      if len(downloaded) >= max_tracks:
        break
      time.sleep(1.0)  # Gentle rate limiting

    return downloaded


def main() -> None:
  parser = argparse.ArgumentParser(description="Scrape Guitar Pro tabs for progressive metal bands")
  parser.add_argument(
    "--artist",
    type=str,
    default="Dream Theater",
    help="Artist or band name (e.g. 'Dream Theater', 'Opeth')",
  )
  parser.add_argument(
    "--track", type=str, default=None, help="Filter by track title (e.g. 'Dance of Eternity')"
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/raw/guitar_pro"),
    help="Directory to store downloaded Guitar Pro files",
  )
  parser.add_argument("--limit", type=int, default=3, help="Maximum tabs to download")
  args = parser.parse_args()

  scraper = GuitarProScraper(output_dir=args.output_dir)
  results = scraper.scrape_artist_tracks(
    artist_name=args.artist, track_filter=args.track, max_tracks=args.limit
  )
  print(f"[*] Complete. Downloaded {len(results)} Guitar Pro files into {args.output_dir}")


if __name__ == "__main__":
  main()
