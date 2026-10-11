#!/usr/bin/env python3
"""Catppuccin Mocha styled TUI Ingestion Runner for prog-metal-structures.

Uses rich to render stylish progress frames and track architecture statistics.
Strictly 2-space indentation.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
  from rich.console import Console
  from rich.panel import Panel
  from rich.table import Table
  from rich.text import Text
except ImportError:
  Console = None
  Panel = None
  Table = None
  Text = None

try:
  from scripts.parse_gp import parse_gp_file
  from scripts.parse_midi import parse_midi_file
except ImportError:
  from parse_gp import parse_gp_file
  from parse_midi import parse_midi_file

# Catppuccin Mocha Palette
MOCHA_BASE = "#1e1e2e"
MOCHA_MANTLE = "#181825"
MOCHA_SURFACE0 = "#313244"
MOCHA_TEXT = "#cdd6f4"
MOCHA_MAUVE = "#cba6f7"
MOCHA_BLUE = "#89b4fa"
MOCHA_TEAL = "#94e2d5"
MOCHA_GREEN = "#a6e3a1"
MOCHA_PEACH = "#fab387"


@dataclass
class TrackStats:
  total_measures: int
  time_sig_changes: int
  distinct_meters: List[str]


class IngestionTUI:
  """Renders parsing metrics in Catppuccin Mocha palette."""

  def __init__(self, console: Optional[Any] = None):
    if Console is None:
      raise ImportError("rich is required. Run `uv add rich`")
    self.console = console or Console()

  @staticmethod
  def compute_stats(track_data: Dict[str, Any]) -> TrackStats:
    """Calculate structural stats from parsed track architecture dict."""
    measures = track_data.get("measures", [])
    distinct_meters: List[str] = []
    changes = 0
    prev_meter = None

    for m in measures:
      ts = m.get("time_signature", "4/4")
      if ts not in distinct_meters:
        distinct_meters.append(ts)
      if prev_meter is not None and ts != prev_meter:
        changes += 1
      prev_meter = ts

    return TrackStats(
      total_measures=len(measures),
      time_sig_changes=changes,
      distinct_meters=distinct_meters
    )

  def display_track_panel(self, source_path: Path, track_data: Dict[str, Any], output_path: Path) -> None:
    """Render a Catppuccin Mocha card for an ingested track."""
    stats = self.compute_stats(track_data)

    content = Text()
    content.append("[+] INGESTION RUNNER\n\n", style=f"bold {MOCHA_TEXT}")

    content.append("Target: ", style=f"bold {MOCHA_MAUVE}")
    content.append(f"{source_path}\n", style=MOCHA_TEXT)

    content.append("Parsed: ", style=f"bold {MOCHA_BLUE}")
    content.append(
      f"{stats.time_sig_changes} time signature changes across {stats.total_measures} measures\n",
      style=MOCHA_TEXT
    )

    content.append("Detected meters: ", style=f"bold {MOCHA_TEAL}")
    content.append(f"{', '.join(stats.distinct_meters)}\n", style=MOCHA_TEXT)

    content.append("Output -> ", style=f"bold {MOCHA_GREEN}")
    content.append(f"{output_path}", style=MOCHA_TEXT)

    panel = Panel(
      content,
      title=f"[{MOCHA_PEACH}]Catppuccin Mocha Pipeline TUI[/{MOCHA_PEACH}]",
      border_style=MOCHA_SURFACE0,
      padding=(1, 2)
    )
    self.console.print(panel)


def run_pipeline(
  raw_gp_dir: Path = Path("data/raw/guitar_pro"),
  raw_midi_dir: Path = Path("data/raw/midi"),
  output_dir: Path = Path("data/processed")
) -> None:
  """Run ingestion on all raw files and display rich Catppuccin Mocha panels."""
  import json
  output_dir.mkdir(parents=True, exist_ok=True)
  tui = IngestionTUI()

  # 1. Process Guitar Pro tabs
  for gp_file in raw_gp_dir.glob("*"):
    if gp_file.suffix.lower() in {".gp3", ".gp4", ".gp5"}:
      try:
        data = parse_gp_file(gp_file)
        out_file = output_dir / f"{data['track_id']}.json"
        out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tui.display_track_panel(gp_file, data, out_file)
      except Exception as exc:
        tui.console.print(f"[{MOCHA_PEACH}][!] Error parsing {gp_file.name}: {exc}[/{MOCHA_PEACH}]")

  # 2. Process MIDI sequences
  for midi_file in raw_midi_dir.glob("*"):
    if midi_file.suffix.lower() in {".mid", ".midi"}:
      try:
        data = parse_midi_file(midi_file)
        out_file = output_dir / f"{data['track_id']}.json"
        out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tui.display_track_panel(midi_file, data, out_file)
      except Exception as exc:
        tui.console.print(f"[{MOCHA_PEACH}][!] Error parsing {midi_file.name}: {exc}[/{MOCHA_PEACH}]")


def main() -> None:
  parser = argparse.ArgumentParser(description="Catppuccin Mocha Ingestion Runner")
  parser.add_argument("--gp-dir", type=Path, default=Path("data/raw/guitar_pro"))
  parser.add_argument("--midi-dir", type=Path, default=Path("data/raw/midi"))
  parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
  args = parser.parse_args()

  run_pipeline(args.gp_dir, args.midi_dir, args.output_dir)


if __name__ == "__main__":
  main()
