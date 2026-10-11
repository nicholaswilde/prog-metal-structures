---
name: prog-metal-scrape
description: >-
  Search and scrape Guitar Pro tabs and MIDI sequences for progressive metal artists.
  Prioritizes Guitar Pro tabs before MIDI, and local datasets before online archives.
---

# Progressive Metal Tab & MIDI Scraper

Runbook for retrieving musical transcriptions for ingestion.

## Workflow

1. **Scrape Guitar Pro Tabs (Priority 1)**:
   Search and download Guitar Pro tabs (.gp3, .gp4, .gp5) from tab repositories:
   ```bash
   uv run python scripts/scrape_gp.py --artist "<Artist>" --track "<Track>" --limit 3
   ```
   Or via Taskfile:
   ```bash
   task scrape-gp -- --artist "<Artist>" --track "<Track>" --limit 3
   ```

2. **Scrape MIDI Files (Priority 2 Fallback)**:
   If Guitar Pro files are unavailable, retrieve MIDI sequences:
   ```bash
   uv run python scripts/scrape_midi.py --query "<Query>" --limit 3
   ```
   Or via Taskfile:
   ```bash
   task scrape-midi -- --query "<Query>" --limit 3
   ```
   - Scraper automatically checks the local dataset `/home/nicholas/git/asigalov61/Tegridy-MIDI-Dataset` first.
   - Falls back to online archives (e.g. Metal-MIDI archive) if not found locally.
