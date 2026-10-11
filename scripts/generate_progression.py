#!/usr/bin/env python3
"""Generative sequence model for composing progressive metal meter progressions.

Trained on measure-level time signature transitions from ingested datasets.
Strictly 2-space indentation.
"""

import argparse
import collections
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
  from scripts.models import Measure, TrackArchitecture
except ImportError:
  from models import Measure, TrackArchitecture


class MeterSequenceGenerator:
  """N-gram statistical Markov sequence model for rhythmic progressions."""

  def __init__(self, order: int = 1, seed: Optional[int] = None):
    self.order = max(1, order)
    self.transitions: Dict[str, Dict[str, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
    self.start_meters: List[str] = []
    if seed is not None:
      random.seed(seed)

  def train(self, sequences: List[List[str]]) -> None:
    """Train transition probabilities on a corpus of meter sequences."""
    for seq in sequences:
      if not seq:
        continue
      self.start_meters.append(seq[0])
      for i in range(len(seq) - 1):
        src = seq[i]
        dst = seq[i + 1]
        self.transitions[src][dst] += 1

  def train_from_processed_dir(self, processed_dir: Path) -> int:
    """Load all processed track JSON datasets and train transitions."""
    sequences: List[List[str]] = []
    for f in processed_dir.glob("*.json"):
      try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if "measures" in data:
          seq = [m.get("time_signature", "4/4") for m in data["measures"]]
          if seq:
            sequences.append(seq)
      except Exception:
        pass
    self.train(sequences)
    return len(sequences)

  def next_meter(self, current: str) -> str:
    """Sample the next time signature according to learned distribution."""
    if current in self.transitions and self.transitions[current]:
      candidates = list(self.transitions[current].keys())
      weights = list(self.transitions[current].values())
      return random.choices(candidates, weights=weights, k=1)[0]
    # Fallback to random known start meter or default 4/4
    return random.choice(self.start_meters) if self.start_meters else "4/4"

  def generate(self, length: int = 32, seed_meter: Optional[str] = None) -> List[str]:
    """Generate a sequence of time signatures."""
    if length <= 0:
      return []

    current = seed_meter or (random.choice(self.start_meters) if self.start_meters else "4/4")
    result = [current]

    for _ in range(length - 1):
      current = self.next_meter(current)
      result.append(current)

    return result

  def generate_track_architecture(
    self,
    title: str = "Generated Prog Sequence",
    artist: str = "Algorithmic Ingestion Model",
    length: int = 32,
    default_tempo: float = 120.0,
    seed_meter: Optional[str] = None
  ) -> TrackArchitecture:
    """Generate a complete TrackArchitecture model instance."""
    progression = self.generate(length=length, seed_meter=seed_meter)
    measures: List[Measure] = []

    for idx, ts in enumerate(progression, start=1):
      measures.append(
        Measure(
          measure_number=idx,
          time_signature=ts,
          tempo_bpm=default_tempo
        )
      )

    slug_artist = artist.lower().replace(" ", "_")
    slug_title = title.lower().replace(" ", "_")
    track_id = f"{slug_artist}_{slug_title}"

    return TrackArchitecture(
      track_id=track_id,
      title=title,
      artist=artist,
      album="Algorithmic Compositions",
      total_measures=length,
      default_tempo_bpm=default_tempo,
      default_time_signature=progression[0] if progression else "4/4",
      measures=measures
    )


def main() -> None:
  parser = argparse.ArgumentParser(description="Generate novel progressive metal meter progressions")
  parser.add_argument(
    "--corpus-dir",
    type=Path,
    default=Path("data/processed"),
    help="Directory with processed track JSON datasets"
  )
  parser.add_argument(
    "--length",
    type=int,
    default=32,
    help="Number of measures to generate"
  )
  parser.add_argument(
    "--tempo",
    type=float,
    default=128.0,
    help="Default BPM tempo"
  )
  parser.add_argument(
    "--seed-meter",
    type=str,
    default="7/8",
    help="Initial time signature"
  )
  parser.add_argument(
    "--title",
    type=str,
    default="Synthesized Polymeter",
    help="Generated track title"
  )
  parser.add_argument(
    "--output-file",
    type=Path,
    default=None,
    help="Optional path to save generated JSON architecture"
  )
  args = parser.parse_args()

  gen = MeterSequenceGenerator(order=1)
  count = gen.train_from_processed_dir(args.corpus_dir)
  print(f"[*] Trained sequence generator on {count} ingested tracks.")

  track = gen.generate_track_architecture(
    title=args.title,
    artist="Prog Generator",
    length=args.length,
    default_tempo=args.tempo,
    seed_meter=args.seed_meter
  )

  print(f"\n[+] Generated: {track.title} ({track.total_measures} measures)")
  print(f"    Meters: {' -> '.join([m.time_signature for m in track.measures[:12]])}...")

  if args.output_file:
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(track.model_dump(), indent=2), encoding="utf-8")
    print(f"    Saved track architecture to: {args.output_file}")


if __name__ == "__main__":
  main()
