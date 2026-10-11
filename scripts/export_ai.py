#!/usr/bin/env python3
"""AI training corpora and evaluation benchmark suite exporter.

Exports:
- data/ai/prog_metal_sft.jsonl (Instruction / SFT pairs in ChatML format)
- data/ai/prog_metal_knowledge_corpus.jsonl (RAG documents with structural metadata)
- data/ai/prog_metal_benchmark_suite.jsonl (Evaluation benchmark questions)
- data/ai/README.md (Documentation ledger)

Adheres strictly to 2-space indentation.
"""

from pathlib import Path
from typing import Any, Dict, List
import argparse
import json

SYSTEM_PROMPT = (
  "You are an expert computational musicologist specializing in progressive metal "
  "rhythm, odd-meter structures, tempo modulations, and musical architecture."
)


def load_complexity_map(processed_dir: Path) -> Dict[str, Dict[str, Any]]:
  """Load metric complexity analysis indexed by track_id."""
  comp_file = processed_dir / "analysis" / "metric_complexity.json"
  if not comp_file.exists():
    return {}
  try:
    data = json.loads(comp_file.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("tracks", [])
    return {r["track_id"]: r for r in rows if "track_id" in r}
  except Exception:
    return {}


def build_sft_dataset(processed_dir: Path) -> List[Dict[str, Any]]:
  """Generate ChatML instruction pairs for supervised fine-tuning."""
  track_files = sorted(f for f in processed_dir.glob("*.json") if f.is_file())
  complexity_map = load_complexity_map(processed_dir)
  records: List[Dict[str, Any]] = []

  for f in track_files:
    try:
      track = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
      continue

    track_id = track.get("track_id", f.stem)
    title = track.get("title", f.stem)
    artist = track.get("artist", "Unknown")
    album = track.get("album", "")
    measures = track.get("measures", [])
    total_measures = track.get("total_measures", len(measures))
    comp = complexity_map.get(track_id, {})

    unique_meters = comp.get("unique_meters")
    if unique_meters is None:
      meters_set = sorted(set(m.get("time_signature", "4/4") for m in measures))
      unique_meters = len(meters_set)
    else:
      meters_set = sorted(comp.get("meter_distribution", {}).keys()) or ["4/4"]

    metric_entropy = comp.get("metric_entropy", 0.0)
    shift_freq = comp.get("shift_frequency", 0.0)

    # Q&A 1: Metric Complexity Analysis
    records.append(
      {
        "messages": [
          {"role": "system", "content": SYSTEM_PROMPT},
          {
            "role": "user",
            "content": f"Analyze the metric complexity and rhythmic architecture of '{title}' by {artist}.",
          },
          {
            "role": "assistant",
            "content": (
              f"'{title}' by {artist}"
              + (f" (from the album '{album}')" if album else "")
              + f" features {total_measures} measures. "
              f"The track utilizes {unique_meters} distinct time signatures: {', '.join(meters_set)}. "
              f"It exhibits a metric entropy of {metric_entropy:.3f} bits with a meter shift frequency of {shift_freq:.4f} "
              f"shifts per measure."
            ),
          },
        ],
        "category": "metric_complexity",
        "track_id": track_id,
        "artist": artist,
      }
    )

    # Q&A 2: Meter Sequence Breakdown
    sample_meters = [m.get("time_signature", "4/4") for m in measures[:16]]
    records.append(
      {
        "messages": [
          {"role": "system", "content": SYSTEM_PROMPT},
          {
            "role": "user",
            "content": f"What is the opening meter progression for '{title}' by {artist}?",
          },
          {
            "role": "assistant",
            "content": (
              f"The opening measure sequence of '{title}' begins in {sample_meters[0] if sample_meters else '4/4'}. "
              f"The initial sequence across measures 1–{len(sample_meters)} is: {' -> '.join(sample_meters)}."
            ),
          },
        ],
        "category": "meter_sequence",
        "track_id": track_id,
        "artist": artist,
      }
    )

    # Q&A 3: Section Structure (if sections available)
    sections = track.get("sections", [])
    if sections:
      sec_desc = ", ".join(
        f"{s.get('name', 'Section')} (measures {s.get('start_measure')}-{s.get('end_measure')})"
        for s in sections
      )
      records.append(
        {
          "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
              "role": "user",
              "content": f"How is '{title}' by {artist} structurally segmented into sections?",
            },
            {
              "role": "assistant",
              "content": f"'{title}' is structured into {len(sections)} distinct architectural sections: {sec_desc}.",
            },
          ],
          "category": "section_structure",
          "track_id": track_id,
          "artist": artist,
        }
      )

  return records


def build_knowledge_corpus(processed_dir: Path) -> List[Dict[str, Any]]:
  """Generate narrative documents with structural metadata for RAG."""
  track_files = sorted(f for f in processed_dir.glob("*.json") if f.is_file())
  complexity_map = load_complexity_map(processed_dir)
  docs: List[Dict[str, Any]] = []

  for f in track_files:
    try:
      track = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
      continue

    track_id = track.get("track_id", f.stem)
    title = track.get("title", f.stem)
    artist = track.get("artist", "Unknown")
    album = track.get("album", "")
    year = track.get("year")
    measures = track.get("measures", [])
    total_measures = track.get("total_measures", len(measures))
    default_meter = track.get("default_time_signature", "4/4")
    default_tempo = track.get("default_tempo_bpm", 120.0)
    sections = track.get("sections", [])
    comp = complexity_map.get(track_id, {})

    unique_meters = comp.get("unique_meters")
    if unique_meters is None:
      meters_set = sorted(set(m.get("time_signature", "4/4") for m in measures))
    else:
      meters_set = sorted(comp.get("meter_distribution", {}).keys()) or [default_meter]

    metric_entropy = comp.get("metric_entropy", 0.0)
    shift_freq = comp.get("shift_frequency", 0.0)

    sec_lines = [
      f"- {s.get('name', 'Section')}: mm. {s.get('start_measure')}-{s.get('end_measure')}"
      for s in sections
    ]
    sec_text = (
      "\n".join(sec_lines) if sec_lines else "- Single continuous through-composed passage."
    )

    text = (
      f"# {title} — {artist}\n\n"
      f"**Album**: {album or 'Single/Transcription'} ({year or 'N/A'})\n"
      f"**Total Measures**: {total_measures}\n"
      f"**Default Meter**: {default_meter}\n"
      f"**Default Tempo**: {default_tempo} BPM\n"
      f"**Unique Time Signatures**: {len(meters_set)} ({', '.join(meters_set)})\n"
      f"**Metric Entropy**: {metric_entropy:.3f} bits\n"
      f"**Meter Shift Frequency**: {shift_freq:.4f} shifts/measure\n\n"
      f"## Formal Sections\n{sec_text}\n"
    )

    docs.append(
      {
        "id": f"prog_doc_{track_id}",
        "title": f"{title} by {artist} — Structural Analysis",
        "text": text,
        "metadata": {
          "track_id": track_id,
          "artist": artist,
          "album": album,
          "year": year,
          "total_measures": total_measures,
          "unique_meters": len(meters_set),
          "metric_entropy": metric_entropy,
        },
      }
    )

  return docs


def build_benchmark_suite(processed_dir: Path) -> List[Dict[str, Any]]:
  """Generate benchmark evaluation prompts with verified golden answers."""
  track_files = sorted(f for f in processed_dir.glob("*.json") if f.is_file())
  complexity_map = load_complexity_map(processed_dir)
  bench: List[Dict[str, Any]] = []

  idx = 1
  for f in track_files:
    try:
      track = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
      continue

    track_id = track.get("track_id", f.stem)
    title = track.get("title", f.stem)
    artist = track.get("artist", "Unknown")
    measures = track.get("measures", [])
    total_measures = track.get("total_measures", len(measures))
    default_meter = track.get("default_time_signature", "4/4")
    comp = complexity_map.get(track_id, {})

    unique_meters = comp.get("unique_meters")
    if unique_meters is None:
      meters_set = set(m.get("time_signature", "4/4") for m in measures)
      unique_meters = len(meters_set)
    metric_entropy = comp.get("metric_entropy", 0.0)

    # Q1: Unique meters count
    bench.append(
      {
        "id": f"prog_bench_{idx:03d}",
        "category": "unique_meters_count",
        "question": f"How many unique time signatures are used in '{title}' by {artist}?",
        "golden_answer": str(unique_meters),
        "eval_type": "exact_match",
      }
    )
    idx += 1

    # Q2: Default meter
    bench.append(
      {
        "id": f"prog_bench_{idx:03d}",
        "category": "default_meter",
        "question": f"What is the primary or default time signature of '{title}' by {artist}?",
        "golden_answer": str(default_meter),
        "eval_type": "exact_match",
      }
    )
    idx += 1

    # Q3: Total measures
    bench.append(
      {
        "id": f"prog_bench_{idx:03d}",
        "category": "total_measures",
        "question": f"How many total measures are in the transcription of '{title}' by {artist}?",
        "golden_answer": str(total_measures),
        "eval_type": "exact_match",
      }
    )
    idx += 1

    # Q4: Metric entropy (rounded to 3 decimal places)
    bench.append(
      {
        "id": f"prog_bench_{idx:03d}",
        "category": "metric_entropy",
        "question": f"What is the Shannon metric entropy (in bits) for '{title}' by {artist}?",
        "golden_answer": f"{metric_entropy:.3f}",
        "eval_type": "numeric_tolerance",
      }
    )
    idx += 1

  return bench


def export_ai_corpora(
  processed_dir: Path = Path("data/processed"),
  output_dir: Path = Path("data/ai"),
) -> Dict[str, Path]:
  """Export SFT dataset, knowledge corpus, benchmark suite, and documentation."""
  output_dir.mkdir(parents=True, exist_ok=True)

  sft_records = build_sft_dataset(processed_dir)
  knowledge_docs = build_knowledge_corpus(processed_dir)
  benchmark_suite = build_benchmark_suite(processed_dir)

  sft_path = output_dir / "prog_metal_sft.jsonl"
  knowledge_path = output_dir / "prog_metal_knowledge_corpus.jsonl"
  benchmark_path = output_dir / "prog_metal_benchmark_suite.jsonl"
  readme_path = output_dir / "README.md"

  with sft_path.open("w", encoding="utf-8") as fp:
    for rec in sft_records:
      fp.write(json.dumps(rec) + "\n")

  with knowledge_path.open("w", encoding="utf-8") as fp:
    for doc in knowledge_docs:
      fp.write(json.dumps(doc) + "\n")

  with benchmark_path.open("w", encoding="utf-8") as fp:
    for q in benchmark_suite:
      fp.write(json.dumps(q) + "\n")

  readme_content = f"""# Progressive Metal AI Training Corpora & Benchmark Suite

This directory contains curated machine learning datasets formatted for Large Language Model (LLM) instruction fine-tuning, Retrieval-Augmented Generation (RAG) vector embeddings, and evaluation benchmarking across progressive metal musical architectures.

---

## Files in this Dataset

### 1. `prog_metal_sft.jsonl` ({len(sft_records)} conversation pairs)
- **Format**: JSON Lines, ChatML / OpenAI message format (`messages`).
- **Use Case**: Supervised Fine-Tuning (SFT) for music analysis, meter prediction, and metric complexity reasoning.
- **Record Structure**:
  ```json
  {{
    "messages": [
      {{"role": "system", "content": "{SYSTEM_PROMPT}"}},
      {{"role": "user", "content": "Analyze the metric complexity of 'Dance of Eternity' by Dream Theater."}},
      {{"role": "assistant", "content": "..."}}
    ],
    "category": "metric_complexity",
    "track_id": "dream_theater_dance_of_eternity"
  }}
  ```

### 2. `prog_metal_knowledge_corpus.jsonl` ({len(knowledge_docs)} documents)
- **Format**: JSON Lines, structured markdown documents with metadata.
- **Use Case**: Vector database ingestion (Chroma, Qdrant, Pinecone), BM25 hybrid search, and semantic RAG retrieval.
- **Record Structure**:
  ```json
  {{
    "id": "prog_doc_dream_theater_dance_of_eternity",
    "title": "Dance of Eternity by Dream Theater — Structural Analysis",
    "text": "# Dance of Eternity — Dream Theater\\n\\n**Total Measures**: 127...",
    "metadata": {{
      "track_id": "dream_theater_dance_of_eternity",
      "artist": "Dream Theater",
      "metric_entropy": 2.45
    }}
  }}
  ```

### 3. `prog_metal_benchmark_suite.jsonl` ({len(benchmark_suite)} evaluation questions)
- **Format**: JSON Lines, question and ground-truth answer pairs with evaluation strategy.
- **Use Case**: Evaluating model domain understanding, factual recall of meter progressions, and hallucination rates.
- **Record Structure**:
  ```json
  {{
    "id": "prog_bench_001",
    "category": "unique_meters_count",
    "question": "How many unique time signatures are used in 'Dance of Eternity' by Dream Theater?",
    "golden_answer": "8",
    "eval_type": "exact_match"
  }}
  ```
"""
  readme_path.write_text(readme_content, encoding="utf-8")

  return {
    "sft": sft_path,
    "knowledge": knowledge_path,
    "benchmark": benchmark_path,
    "readme": readme_path,
  }


def main() -> None:
  """CLI entrypoint for AI corpora export."""
  parser = argparse.ArgumentParser(description="Export AI training corpora and benchmark suite")
  parser.add_argument(
    "--processed-dir",
    type=Path,
    default=Path("data/processed"),
    help="Processed directory path",
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/ai"),
    help="Output directory path for AI datasets",
  )
  args = parser.parse_args()

  out = export_ai_corpora(processed_dir=args.processed_dir, output_dir=args.output_dir)
  print(f"[+] Exported SFT pairs: {out['sft']}")
  print(f"[+] Exported RAG knowledge corpus: {out['knowledge']}")
  print(f"[+] Exported evaluation benchmark suite: {out['benchmark']}")
  print(f"[+] Updated documentation: {out['readme']}")


if __name__ == "__main__":
  main()
