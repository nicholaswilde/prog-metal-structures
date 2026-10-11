from pathlib import Path
import json
from scripts.export_ai import (
  build_sft_dataset,
  build_knowledge_corpus,
  build_benchmark_suite,
  export_ai_corpora,
)


def create_mock_track(processed_dir: Path) -> Path:
  """Helper to write mock track and complexity files."""
  track = {
    "track_id": "dream_theater_dance",
    "title": "Dance of Eternity",
    "artist": "Dream Theater",
    "album": "Metropolis Pt. 2",
    "year": 1999,
    "default_tempo_bpm": 130.0,
    "default_time_signature": "4/4",
    "total_measures": 3,
    "sections": [{"name": "Intro", "start_measure": 1, "end_measure": 3}],
    "measures": [
      {"measure_number": 1, "time_signature": "4/4", "tempo_bpm": 130.0, "section_name": "Intro"},
      {"measure_number": 2, "time_signature": "7/8", "tempo_bpm": 130.0, "section_name": "Intro"},
      {"measure_number": 3, "time_signature": "5/8", "tempo_bpm": 130.0, "section_name": "Intro"},
    ],
  }
  track_file = processed_dir / "dt_dance.json"
  track_file.write_text(json.dumps(track), encoding="utf-8")

  analysis_dir = processed_dir / "analysis"
  analysis_dir.mkdir(parents=True, exist_ok=True)
  analysis = [
    {
      "track_id": "dream_theater_dance",
      "title": "Dance of Eternity",
      "artist": "Dream Theater",
      "total_measures": 3,
      "unique_meters": 3,
      "shift_frequency": 0.6667,
      "metric_entropy": 1.585,
      "meter_distribution": {"4/4": 0.3333, "7/8": 0.3333, "5/8": 0.3333},
      "transition_matrix": {"4/4": {"7/8": 1.0}, "7/8": {"5/8": 1.0}},
    }
  ]
  (analysis_dir / "metric_complexity.json").write_text(json.dumps(analysis), encoding="utf-8")
  return track_file


def test_build_sft_dataset(tmp_path: Path):
  """Verify SFT training records conform to ChatML messages format."""
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()
  create_mock_track(processed_dir)

  sft_records = build_sft_dataset(processed_dir)
  assert len(sft_records) >= 2
  for rec in sft_records:
    assert "messages" in rec
    assert len(rec["messages"]) == 3
    assert rec["messages"][0]["role"] == "system"
    assert rec["messages"][1]["role"] == "user"
    assert rec["messages"][2]["role"] == "assistant"
    assert "category" in rec
    assert "track_id" in rec


def test_build_knowledge_corpus(tmp_path: Path):
  """Verify RAG knowledge documents have metadata and structured text."""
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()
  create_mock_track(processed_dir)

  corpus = build_knowledge_corpus(processed_dir)
  assert len(corpus) == 1
  doc = corpus[0]
  assert doc["id"] == "prog_doc_dream_theater_dance"
  assert "Dance of Eternity" in doc["title"]
  assert "metadata" in doc
  assert doc["metadata"]["artist"] == "Dream Theater"
  assert "7/8" in doc["text"]


def test_build_benchmark_suite(tmp_path: Path):
  """Verify benchmark prompts contain golden answers and eval types."""
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()
  create_mock_track(processed_dir)

  bench = build_benchmark_suite(processed_dir)
  assert len(bench) >= 2
  for q in bench:
    assert "id" in q
    assert "question" in q
    assert "golden_answer" in q
    assert "eval_type" in q
    assert "category" in q


def test_export_ai_corpora(tmp_path: Path):
  """Verify export creates all three JSONL files and README."""
  processed_dir = tmp_path / "processed"
  processed_dir.mkdir()
  create_mock_track(processed_dir)

  ai_dir = tmp_path / "ai"
  out = export_ai_corpora(processed_dir, ai_dir)

  assert out["sft"].exists()
  assert out["knowledge"].exists()
  assert out["benchmark"].exists()
  assert out["readme"].exists()

  # Check line validity
  sft_lines = out["sft"].read_text(encoding="utf-8").strip().split("\n")
  assert len(sft_lines) >= 2
  assert json.loads(sft_lines[0])["messages"]
