"""Tests for generative meter progression model under TDD."""

from scripts.generate_progression import MeterSequenceGenerator


def test_generator_training():
  """Verify sequence generator trains transitions from corpus."""
  corpus = [["4/4", "7/8", "7/8", "5/8", "4/4"], ["4/4", "13/8", "7/8", "4/4"]]
  gen = MeterSequenceGenerator(order=1)
  gen.train(corpus)
  assert "4/4" in gen.transitions
  assert "7/8" in gen.transitions["4/4"]
  assert "13/8" in gen.transitions["4/4"]


def test_generator_generate():
  """Verify generation produces requested measure count and valid time signatures."""
  corpus = [["4/4", "7/8", "6/8", "5/8", "4/4"]]
  gen = MeterSequenceGenerator(order=1)
  gen.train(corpus)

  progression = gen.generate(length=10, seed_meter="4/4")
  assert len(progression) == 10
  assert all("/" in ts for ts in progression)
  assert progression[0] == "4/4"


def test_generator_to_track_architecture():
  """Verify exported track architecture validates against Pydantic schema."""
  corpus = [["4/4", "7/8", "5/8", "4/4"]]
  gen = MeterSequenceGenerator(order=1)
  gen.train(corpus)

  track = gen.generate_track_architecture(
    title="Algorithmic Overture",
    artist="AI Prog Collective",
    length=16,
    default_tempo=135.0,
    seed_meter="4/4",
  )
  assert track.title == "Algorithmic Overture"
  assert len(track.measures) == 16
  assert track.total_measures == 16
  assert track.default_tempo_bpm == 135.0
