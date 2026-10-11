#!/usr/bin/env python3
"""Parse MIDI files (.mid, .midi) into structured track architecture JSON using music21."""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
  from music21 import converter, expressions, meter, tempo
except ImportError:
  converter = None
  expressions = None
  meter = None
  tempo = None


def slugify(text: str) -> str:
  """Convert string to filesystem and identifier safe slug."""
  slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
  return re.sub(r"[-\s]+", "_", slug) or "unknown"


def parse_midi_file(file_path: Path) -> Dict[str, Any]:
  """Extract meter and tempo events from a MIDI file using music21."""
  if converter is None:
    raise ImportError("music21 is required. Install via: pip install music21")

  score = converter.parse(str(file_path))

  title = file_path.stem
  if hasattr(score, "metadata") and score.metadata:
    if score.metadata.title:
      title = score.metadata.title
    artist = score.metadata.composer or "Unknown Artist"
  else:
    artist = "Unknown Artist"

  track_id = f"{slugify(artist)}_{slugify(title)}"

  # Ensure measures are partitioned
  primary_stream = score.parts[0] if getattr(score, "parts", None) and len(score.parts) > 0 else score
  measure_elements = list(primary_stream.getElementsByClass("Measure"))
  if not measure_elements:
    score_measured = score.makeMeasures()
    primary_stream = score_measured.parts[0] if getattr(score_measured, "parts", None) and len(score_measured.parts) > 0 else score_measured
    measure_elements = list(primary_stream.getElementsByClass("Measure"))

  measures_data: List[Dict[str, Any]] = []
  sections: List[Dict[str, Any]] = []
  current_section: Optional[Dict[str, Any]] = None

  current_ts = "4/4"
  current_bpm = 120.0

  # Scan global tempo / time signatures if present before measure 1
  for element in score.recurse():
    if isinstance(element, meter.TimeSignature):
      current_ts = f"{element.numerator}/{element.denominator}"
      break

  for element in score.recurse():
    if isinstance(element, tempo.MetronomeMark):
      bpm_val = element.getQuarterBPM() if hasattr(element, "getQuarterBPM") else getattr(element, "number", 120.0)
      if bpm_val:
        current_bpm = float(bpm_val)
        break

  for idx, m in enumerate(measure_elements, start=1):
    measure_num = getattr(m, "number", idx)
    if measure_num == 0 or measure_num is None:
      measure_num = idx

    # Check for local time signature changes
    ts_list = list(m.getElementsByClass(meter.TimeSignature))
    if ts_list:
      active_ts = ts_list[0]
      current_ts = f"{active_ts.numerator}/{active_ts.denominator}"
    elif getattr(m, "timeSignature", None):
      active_ts = m.timeSignature
      current_ts = f"{active_ts.numerator}/{active_ts.denominator}"

    # Check for tempo changes
    tempo_list = list(m.getElementsByClass(tempo.MetronomeMark))
    if tempo_list:
      bpm_val = tempo_list[0].getQuarterBPM() if hasattr(tempo_list[0], "getQuarterBPM") else getattr(tempo_list[0], "number", current_bpm)
      if bpm_val:
        current_bpm = float(bpm_val)

    # Check for rehearsal mark or text expression section label
    section_label = None
    rehearsal_marks = list(m.getElementsByClass(expressions.RehearsalMark))
    text_expressions = list(m.getElementsByClass(expressions.TextExpression))
    if rehearsal_marks and rehearsal_marks[0].text:
      section_label = rehearsal_marks[0].text.strip()
    elif text_expressions and text_expressions[0].content:
      section_label = text_expressions[0].content.strip()

    if section_label:
      if current_section is not None:
        current_section["end_measure"] = measure_num - 1
      current_section = {
        "label": section_label,
        "start_measure": measure_num
      }
      sections.append(current_section)

    measure_entry: Dict[str, Any] = {
      "measure_number": measure_num,
      "time_signature": current_ts,
      "tempo_bpm": round(current_bpm, 2)
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
    "album": "",
    "source_file": file_path.name,
    "source_format": file_path.suffix.lstrip(".").lower(),
    "total_measures": total_measures,
    "default_tempo_bpm": default_tempo,
    "default_time_signature": default_ts,
    "sections": sections,
    "measures": measures_data
  }


def process_directory(raw_dir: Path, output_dir: Path) -> List[Path]:
  """Iterate over MIDI files in raw_dir and save extracted JSON to output_dir."""
  output_dir.mkdir(parents=True, exist_ok=True)
  valid_exts = {".mid", ".midi"}
  created_files: List[Path] = []

  midi_files = [p for p in raw_dir.glob("*") if p.suffix.lower() in valid_exts]
  if not midi_files:
    print(f"[!] No MIDI files found in {raw_dir}")
    return created_files

  for midi_path in midi_files:
    try:
      print(f"[*] Parsing: {midi_path.name}")
      track_data = parse_midi_file(midi_path)
      out_path = output_dir / f"{track_data['track_id']}.json"
      with open(out_path, "w", encoding="utf-8") as f:
        json.dump(track_data, f, indent=2)
      print(f"    -> Saved architecture: {out_path.name} ({track_data['total_measures']} measures)")
      created_files.append(out_path)
    except Exception as exc:
      print(f"[!] Error parsing {midi_path.name}: {exc}")

  return created_files


def main() -> None:
  parser = argparse.ArgumentParser(description="Parse MIDI files into structural JSON using music21")
  parser.add_argument(
    "--input-dir",
    type=Path,
    default=Path("data/raw/midi"),
    help="Directory containing .mid/.midi files"
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/processed"),
    help="Directory to write processed JSON datasets"
  )
  args = parser.parse_args()

  process_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
  main()
