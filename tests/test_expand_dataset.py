"""Unit tests for dataset expansion workflow and automation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import respx

from scripts.discography import verify_discography
from scripts.expand_dataset import (
  SUPPORTED_EXTENSIONS,
  batch_download_tracks,
  find_best_tab_for_track,
  inspect_artist_tabs,
  run_pipeline_sync,
)


def test_supported_extensions():
  """Verify supported extensions set."""
  assert ".gp3" in SUPPORTED_EXTENSIONS
  assert ".gp4" in SUPPORTED_EXTENSIONS
  assert ".gp5" in SUPPORTED_EXTENSIONS
  assert ".gpx" not in SUPPORTED_EXTENSIONS


@respx.mock
def test_inspect_artist_tabs(tmp_path: Path):
  """Verify remote tab inspection identifies GP3/4/5 vs GPX formats."""
  # Mock artist index and listing
  respx.get("https://gprotab.net/en/artists/t").respond(
    200, html='<a href="/en/tabs/tool">Tool</a>'
  )
  respx.get("https://gprotab.net/en/tabs/tool").respond(
    200,
    html="""
    <a href="/en/tabs/tool/lateralus">Lateralus</a>
    <a href="/en/tabs/tool/schism">Schism</a>
    """,
  )
  # Mock download headers
  respx.head("https://gprotab.net/en/tabs/tool/lateralus?download").respond(
    200, headers={"content-disposition": 'attachment; filename="tool-lateralus.gp3"'}
  )
  respx.head("https://gprotab.net/en/tabs/tool/schism?download").respond(
    200, headers={"content-disposition": 'attachment; filename="tool-schism.gpx"'}
  )

  results = inspect_artist_tabs("Tool", output_dir=tmp_path)
  assert len(results) == 2
  assert results[0]["title"] == "Lateralus"
  assert results[0]["supported"] is True
  assert results[0]["extension"] == ".gp3"

  assert results[1]["title"] == "Schism"
  assert results[1]["supported"] is False
  assert "GPX" in results[1]["status"]


def test_find_best_tab_for_track():
  """Verify selection of supported GP5 version over GPX version."""
  mock_scraper = MagicMock()

  # Candidate 1: GPX, Candidate 2: GP5
  def mock_head(url, **kwargs):
    resp = MagicMock()
    if "ver-1" in url:
      resp.headers = {"content-disposition": 'attachment; filename="song.gpx"'}
    else:
      resp.headers = {"content-disposition": 'attachment; filename="song.gp5"'}
    return resp

  mock_scraper.client.head.side_effect = mock_head

  tabs = [
    {"title": "The Woven Web", "url": "https://gprotab.net/tab/the-woven-web-ver-1"},
    {"title": "The Woven Web 2", "url": "https://gprotab.net/tab/the-woven-web-ver-2"},
  ]

  best = find_best_tab_for_track(tabs, "The Woven Web", mock_scraper)
  assert best is not None
  selected_tab, ext = best
  assert ext == ".gp5"
  assert selected_tab["title"] == "The Woven Web 2"


def test_batch_download_tracks(tmp_path: Path):
  """Verify batch tab download handling."""
  with patch("scripts.expand_dataset.GuitarProScraper") as mock_scraper_cls:
    scraper = mock_scraper_cls.return_value
    scraper.find_artist_slug.return_value = "meshuggah"
    scraper.list_artist_tabs.return_value = [{"title": "Bleed", "url": "https://gprotab.net/bleed"}]

    # Mock head check for supported format
    mock_resp = MagicMock()
    mock_resp.headers = {"content-disposition": 'attachment; filename="meshuggah-bleed.gp4"'}
    scraper.client.head.return_value = mock_resp

    dest = tmp_path / "meshuggah-bleed.gp4"
    scraper.download_tab.return_value = dest

    files = batch_download_tracks("Meshuggah", ["Bleed"], output_dir=tmp_path)
    assert len(files) == 1
    assert files[0] == dest


def test_verify_discography(tmp_path: Path):
  """Verify discography completeness reporting on mock dataset."""
  # Write one complete and one incomplete track
  complete_track = tmp_path / "band_song_one.json"
  complete_track.write_text(
    '{"track_id": "band_one", "artist": "Band", "title": "Song One", "album": "Album A", "year": 2020}',
    encoding="utf-8",
  )

  incomplete_track = tmp_path / "band_song_two.json"
  incomplete_track.write_text(
    '{"track_id": "band_two", "artist": "Band", "title": "Song Two", "album": null, "year": null}',
    encoding="utf-8",
  )

  report = verify_discography(processed_dir=tmp_path)
  assert report["total_tracks"] == 2
  assert report["complete_tracks"] == 1
  assert report["missing_count"] == 1
  assert report["missing_tracks"][0]["title"] == "Song Two"


@patch("subprocess.run")
def test_run_pipeline_sync(mock_subproc):
  """Verify run_pipeline_sync executes all steps."""
  mock_subproc.return_value = MagicMock(returncode=0)
  ret = run_pipeline_sync()
  assert ret == 0
  assert mock_subproc.call_count == 8
