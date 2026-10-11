---
name: prog-metal-ingestion
description: >-
  Parse raw Guitar Pro and MIDI files into normalized JSON datasets, generate artist metadata, and validate against JSON schemas.
---

# Progressive Metal Ingestion Pipeline

Runbook for converting raw music transcription files into validated structural datasets.

## Pipeline Steps

1. **Parse Guitar Pro Files**:
   ```bash
   task parse-gp
   ```
   Parses all `.gp3`, `.gp4`, `.gp5` files from `data/raw/guitar_pro/` into `data/processed/<artist>_<title>.json`.

2. **Parse MIDI Files**:
   ```bash
   task parse-midi
   ```
   Parses all `.mid`, `.midi` files from `data/raw/midi/` into `data/processed/<artist>_<title>.json`.

3. **Build Artist Metadata Summaries**:
   ```bash
   task build-artists
   ```
   Aggregates ingested track architectures into `data/processed/artists/<artist_id>.json`.

4. **Verify Schema & Model Validation**:
   ```bash
   task test
   ```
   Executes pytest test suite verifying all processed tracks and artist metadata match `schemas/track_architecture.json` and `schemas/artist_metadata.json`.
