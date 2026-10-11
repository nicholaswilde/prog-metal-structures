"""Tests for Guitar Pro and MIDI scrapers using respx to mock HTTP."""

from pathlib import Path
import pytest
import respx
import httpx
from scripts.scrape_gp import GuitarProScraper
from scripts.scrape_midi import MidiScraper


@respx.mock
def test_scrape_gp_artist_and_tabs(tmp_path: Path):
  """Verify Guitar Pro scraper resolves artist, lists tabs, and downloads file."""
  scraper = GuitarProScraper(output_dir=tmp_path)

  # Mock artist index page
  index_html = '<html><body><a href="/en/tabs/dream-theater">Dream Theater</a></body></html>'
  respx.get("https://gprotab.net/en/artists/d").respond(200, text=index_html)

  # Mock artist tabs page
  tabs_html = (
    '<html><body>'
    '<a href="/en/tabs/dream-theater/the-dance-of-eternity">The Dance of Eternity</a>'
    '</body></html>'
  )
  respx.get("https://gprotab.net/en/tabs/dream-theater").respond(200, text=tabs_html)

  # Mock download endpoint
  respx.get("https://gprotab.net/en/tabs/dream-theater/the-dance-of-eternity?download").respond(
    200,
    content=b"GP5 DUMMY CONTENT",
    headers={"Content-Disposition": 'attachment; filename="dance.gp5"'}
  )

  results = scraper.scrape_artist_tracks(
    artist_name="Dream Theater",
    track_filter="Dance",
    max_tracks=1
  )

  assert len(results) == 1
  assert results[0].name == "dance.gp5"
  assert results[0].read_bytes() == b"GP5 DUMMY CONTENT"


@respx.mock
def test_scrape_midi_fallback(tmp_path: Path):
  """Verify MIDI scraper falls back to online archive when not in local dataset."""
  scraper = MidiScraper(output_dir=tmp_path)

  # Mock metal midi archive page
  archive_html = (
    '<html><body>'
    '<a href="midi/test/test_song.mid">Test Song</a>'
    '</body></html>'
  )
  respx.get("http://metal-midi.grahamdowney.com/midi.html").respond(200, text=archive_html)

  # Mock direct download
  respx.get("http://metal-midi.grahamdowney.com/midi/test/test_song.mid").respond(
    200,
    content=b"MIDI DUMMY DATA"
  )

  # Scrape non-local song query
  results = scraper.scrape(query="Test Song", limit=1)
  assert len(results) == 1
  assert results[0].name == "test_song.mid"
  assert results[0].read_bytes() == b"MIDI DUMMY DATA"
