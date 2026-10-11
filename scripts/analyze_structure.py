#!/usr/bin/env python3
"""Compute metric complexity metrics and Markovian transition matrices for parsed tracks.

Strictly 2-space indentation.
"""

import argparse
import collections
import json
import math
from pathlib import Path
from typing import Any, Dict, List


def calculate_shift_frequency(meters: List[str]) -> float:
  """Calculate the frequency of time signature shifts between adjacent measures."""
  if len(meters) <= 1:
    return 0.0
  shifts = sum(1 for i in range(len(meters) - 1) if meters[i] != meters[i + 1])
  return round(shifts / (len(meters) - 1), 4)


def calculate_metric_entropy(meters: List[str]) -> float:
  """Calculate Shannon entropy (in bits) of the time signature distribution."""
  if not meters:
    return 0.0
  total = len(meters)
  counts = collections.Counter(meters)
  entropy = 0.0
  for count in counts.values():
    prob = count / total
    if prob > 0:
      entropy -= prob * math.log2(prob)
  return round(entropy, 4)


def build_transition_matrix(meters: List[str]) -> Dict[str, Dict[str, float]]:
  """Build a normalized Markovian meter-transition probability matrix."""
  transitions: Dict[str, Dict[str, int]] = collections.defaultdict(
    lambda: collections.defaultdict(int)
  )

  for i in range(len(meters) - 1):
    src = meters[i]
    dest = meters[i + 1]
    transitions[src][dest] += 1

  matrix: Dict[str, Dict[str, float]] = {}
  for src, dest_counts in transitions.items():
    total_from_src = sum(dest_counts.values())
    matrix[src] = {}
    for dest, count in dest_counts.items():
      matrix[src][dest] = round(count / total_from_src, 4)

  return matrix


def analyze_track(track_dict: Dict[str, Any]) -> Dict[str, Any]:
  """Extract rhythmic & metric metrics for a parsed track."""
  measures = track_dict.get("measures", [])
  meters = [m.get("time_signature", "4/4") for m in measures]
  counts = collections.Counter(meters)
  total = len(meters)

  distribution = {k: round(v / total, 4) for k, v in counts.items()} if total else {}

  return {
    "track_id": track_dict.get("track_id", "unknown"),
    "title": track_dict.get("title", ""),
    "artist": track_dict.get("artist", ""),
    "total_measures": total,
    "unique_meters": len(counts),
    "shift_frequency": calculate_shift_frequency(meters),
    "metric_entropy": calculate_metric_entropy(meters),
    "meter_distribution": distribution,
    "transition_matrix": build_transition_matrix(meters),
  }


def analyze_directory(processed_dir: Path, output_file: Path) -> List[Dict[str, Any]]:
  """Analyze all track JSON files in processed_dir and write summary report."""
  results: List[Dict[str, Any]] = []

  for track_file in processed_dir.glob("*.json"):
    try:
      data = json.loads(track_file.read_text(encoding="utf-8"))
      if "measures" in data:
        metrics = analyze_track(data)
        results.append(metrics)
    except Exception as exc:
      print(f"[!] Error analyzing {track_file.name}: {exc}")

  output_file.parent.mkdir(parents=True, exist_ok=True)
  output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
  print(f"[+] Saved structural analysis for {len(results)} tracks to {output_file}")
  return results


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Analyze metric complexity and meter transition matrices"
  )
  parser.add_argument(
    "--input-dir",
    type=Path,
    default=Path("data/processed"),
    help="Directory containing processed track JSON datasets",
  )
  parser.add_argument(
    "--output-file",
    type=Path,
    default=Path("data/processed/analysis/metric_complexity.json"),
    help="Output JSON file for analysis results",
  )
  args = parser.parse_args()

  analyze_directory(args.input_dir, args.output_file)


if __name__ == "__main__":
  main()
