---
name: prog-metal-expansion
description: >-
  Systematic runbook and toolset for expanding the progressive metal dataset with new artists,
  albums, and tracks. Coordinates format inspection, batch scraping, discography mapping,
  and end-to-end pipeline synchronization.
---

# Progressive Metal Dataset Expansion

Standard operational runbook for adding new artists, concept albums, and multi-meter compositions to the repository.

## Workflow Overview

```
1. Audit Gaps (task gaps)
       ↓
2. Inspect Tab Formats (task dataset:inspect ARTIST="...")
       ↓
3. Batch Download (task dataset:expand -- --artist "..." --tracks "..." --download)
       ↓
4. Map Discography (scripts/discography.py & task discography:verify)
       ↓
5. Sync Ingestion Pipeline (task pipeline:sync)
       ↓
6. Pre-Commit Verification (task check)
```

---

## Step-by-Step Procedure

### 1. Identify Expansion Targets & Audit Gaps
Check current discography completeness and identify high-value albums and rhythmic suites:
```bash
task gaps
```
Review [`docs/dataset_gaps.md`](file:///home/nicholas/git/nicholaswilde/prog-metal-structures/docs/dataset_gaps.md) for target albums. Prioritize tracks that introduce novel metric features (polymeters, non-isochronous meters, frequent tempo changes).

### 2. Inspect Available Remote Tabs
Before downloading, inspect available tabs on `gprotab.net` to verify format compatibility:
```bash
task dataset:inspect ARTIST="Meshuggah"
```
Or via script:
```bash
uv run python scripts/expand_dataset.py --inspect --artist "Animals as Leaders"
```
> [!IMPORTANT]
> The ingestion engine (`guitarpro` / PyGuitarPro) parses **`.gp3`**, **`.gp4`**, and **`.gp5`** files.
> Guitar Pro 6 **`.gpx`** archives are unsupported. The inspect tool marks each candidate as `[OK] SUPPORTED` or `[--] UNSUPPORTED (GPX)`. When multiple versions exist (e.g. `Song` vs `Song 2` vs `Song 3`), pick a version with a supported extension.

### 3. Batch Download Supported Tabs
Download supported tabs directly into `data/raw/guitar_pro/`:
```bash
task dataset:expand -- --artist "Meshuggah" --tracks "New Millennium Cyanide Christ,Sane,Stengah" --download
```
The scraper automatically selects the best supported format and generates standardized filenames (`<artist_key>-<track_slug>.<ext>`).

### 4. Canonical Discography Registration
Open [`scripts/discography.py`](file:///home/nicholas/git/nicholaswilde/prog-metal-structures/scripts/discography.py) and ensure:
1. The artist is defined in `DISCOGRAPHY`.
2. The album exists under `albums` with its `release_year` and `total_tracks`.
3. The track is registered in `track_map`:
   ```python
   "track_title": ("Album Name", release_year),
   ```
Verify that all processed and raw tracks map to canonical metadata:
```bash
task discography:verify
```

### 5. Synchronize Ingestion Pipeline
Execute the complete end-to-end pipeline in a single command:
```bash
task pipeline:sync
```
This automatically runs:
- `task parse-gp` (parses raw `.gp3/.gp4/.gp5` tabs into `data/processed/*.json`)
- `task parse-midi` (parses raw `.mid` files if any)
- `task build-artists` (updates aggregated metadata in `data/processed/artists/`)
- `task analyze` (recalculates metric entropy, changes, and Markov matrices)
- `task export` (re-exports SQLite `prog_metal.db`, Parquet tables, and AI corpora)
- `task gaps:update` (refreshes coverage ledger in `docs/dataset_gaps.md`)

### 6. Verify & Commit
Run full quality pipeline:
```bash
task check
```
Verify tests pass, linting and spelling checks pass, and models validate against JSON schemas.
Commit following conventional commits:
```bash
rtk git add .
rtk git commit -m "feat(data): expand dataset with N tracks for <Artist> (<total> total)"
rtk git push origin main
```
