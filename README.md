# prog-metal-structures

<div align="center">

[![CI](https://github.com/nicholaswilde/prog-metal-structures/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaswilde/prog-metal-structures/actions)
[![Python](https://img.shields.io/badge/Python-3.10+-cba6f7?style=for-the-badge&logo=python&logoColor=1e1e2e&labelColor=181825)](https://www.python.org/)
[![Schema](https://img.shields.io/badge/JSON_Schema-Draft_2020--12-89b4fa?style=for-the-badge&logo=json&logoColor=1e1e2e&labelColor=181825)](schemas/)
[![Theme](https://img.shields.io/badge/Palette-Catppuccin_Mocha-fab387?style=for-the-badge&labelColor=181825)](https://github.com/catppuccin/catppuccin)
[![Dataset](https://img.shields.io/badge/Domain-Prog_Metal_Architecture-a6e3a1?style=for-the-badge&labelColor=181825)](#repository-purpose)

</div>

Dataset repository mapping the complex musical architecture—measure-level time signature shifts, tempo modulations, metric modulations, and recurring motifs—of progressive metal artists (e.g., Dream Theater, Opeth, Tool, Meshuggah, Haken, Animals as Leaders).

---

## Repository Purpose

Progressive metal features frequent odd meters (e.g., $7/8$, $13/8$, $19/16$), polymetric phrasing, and shifting tempos. `prog-metal-structures` normalizes raw tab and MIDI transcriptions into machine-readable JSON datasets following structured schemas to enable:

- Computational musicology and structural analysis
- Metric complexity indexing and visualization
- Transition-matrix modeling for meter shifts
- Training sequence models on odd-meter rhythmic progressions

---

## Directory Structure

```
prog-metal-structures/
├── data/
│   ├── raw/
│   │   ├── guitar_pro/       # Raw .gp3, .gp4, .gp5 files
│   │   └── midi/             # Raw .mid, .midi files
│   └── processed/            # Normalized JSON track architectures
├── schemas/
│   ├── track_architecture.json  # Schema for measures, meters, tempos, sections
│   └── artist_metadata.json     # Schema for discography and artist metadata
├── scripts/
│   ├── parse_gp.py           # Ingestion stub for Guitar Pro tabs
│   └── parse_midi.py         # Ingestion stub for MIDI sequences
└── README.md
```

---

## Ingestion Pipeline & Terminal UI

The ingestion pipeline reports parsing progress and structural statistics:

```
┌── [Catppuccin Mocha Pipeline TUI] ────────────────────────────────────────┐
│  Surface0 (#313244) │ Base (#1e1e2e) │ Text (#cdd6f4)                     │
├───────────────────────────────────────────────────────────────────────────┤
│  [+] INGESTION RUNNER                                                     │
│                                                                           │
│  [Mauve #cba6f7] Target: data/raw/guitar_pro/dance_of_eternity.gp5         │
│  [Blue  #89b4fa] Parsed: 138 time signature changes across 127 measures   │
│  [Teal  #94e2d5] Detected meters: 7/8, 5/8, 4/4, 11/8, 6/8, 3/4, 13/8     │
│  [Green #a6e3a1] Output -> data/processed/dream_theater_the_dance...json  │
└───────────────────────────────────────────────────────────────────────────┘
```

### Catppuccin Mocha Palette Reference

| Token | Hex | Role |
|---|---|---|
| Base | `#1e1e2e` | Terminal background |
| Mantle | `#181825` | Badge label background |
| Surface0 | `#313244` | Panel border / status frame |
| Text | `#cdd6f4` | Primary output text |
| Mauve | `#cba6f7` | Ingestion status & headers |
| Blue | `#89b4fa` | Measure metrics & parser IDs |
| Teal | `#94e2d5` | Time signature & meter classes |
| Green | `#a6e3a1` | Successful outputs & schema validation |
| Peach | `#fab387` | Accent labels & warnings |

---

## Schemas

All processed tracks and artist summaries validate against JSON Schema Draft 2020-12 specifications:

1. **[`schemas/track_architecture.json`](schemas/track_architecture.json)**:
   - Tracks metadata: `track_id`, `title`, `artist`, `album`, `year`
   - Overall metrics: `total_measures`, `default_tempo_bpm`, `default_time_signature`
   - High-level sections: `sections` array with start and end measure bounds
   - Measure sequence: measure-by-measure breakdown with `time_signature` (e.g. `7/8`), `tempo_bpm`, and section tags

2. **[`schemas/artist_metadata.json`](schemas/artist_metadata.json)**:
   - Artist details: `artist_id`, `name`, `country`, `formed_year`, `genres`
   - Coverage: `total_parsed_tracks`
   - Discography context: `albums` with track counts and ingested IDs

---

## Installation & Workflow Instructions

### 1. Requirements & Environment Setup

Manage dependencies and execute scripts using `uv`:

```bash
uv sync
```

Dependencies include `PyGuitarPro`, `music21`, `pydantic`, `jsonschema`, `httpx`, and `beautifulsoup4`.
*(Note: Python scripts strictly use 2-space indentation).*

### 2. Scraping Tab & MIDI Files (Guitar Pro First)

The pipeline prioritizes Guitar Pro tabs before MIDI files.

**Scrape Guitar Pro Tabs (Priority 1):**
```bash
uv run python scripts/scrape_gp.py --artist "Dream Theater" --track "Dance of Eternity" --limit 3
```

**Scrape / Ingest MIDI Sequences (Priority 2):**
Prioritizes the local Tegridy MIDI dataset before online fallback:
```bash
uv run python scripts/scrape_midi.py --query "Dream Theater" --limit 3
```

### 3. Parse Guitar Pro Files

Extract measure structures from raw Guitar Pro files into validated JSON:

```bash
uv run python scripts/parse_gp.py \
  --input-dir data/raw/guitar_pro \
  --output-dir data/processed
```

The script extracts:
- Measure numbers
- Time signature shifts per measure (numerator and denominator)
- Tempo markers (BPM)
- Section rehearsal markers

### 4. Parse MIDI Files

Extract measure structures from raw MIDI files into validated JSON:

```bash
uv run python scripts/parse_midi.py \
  --input-dir data/raw/midi \
  --output-dir data/processed
```

The script extracts:
- Time signatures (`music21.meter.TimeSignature`)
- Metronome markings (`music21.tempo.MetronomeMark`)
- Rehearsal marks and text expressions
- Normalized measure counts

## :balance_scale: License

[Apache License 2.0](LICENSE)

## :writing_hand: Author

This project was started in 2026 by [Nicholas Wilde](https://github.com/nicholaswilde/).
