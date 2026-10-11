#!/usr/bin/env python3
"""Aggregate parsed track files into artist metadata summaries matching schemas/artist_metadata.json.

Strictly 2-space indentation.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

try:
  from scripts.models import AlbumMetadata, ArtistMetadata, TrackArchitecture
except ImportError:
  from models import AlbumMetadata, ArtistMetadata, TrackArchitecture

ARTIST_KNOWLEDGE = {
  "dream_theater": {
    "name": "Dream Theater",
    "country": "United States",
    "formed_year": 1985,
    "genres": ["Progressive Metal", "Progressive Rock"],
    "albums": {
      "Images and Words": {"release_year": 1992, "total_tracks": 8},
      "Metropolis Pt. 2: Scenes from a Memory": {"release_year": 1999, "total_tracks": 12}
    }
  },
  "opeth": {
    "name": "Opeth",
    "country": "Sweden",
    "formed_year": 1990,
    "genres": ["Progressive Death Metal", "Progressive Rock"],
    "albums": {
      "Ghost Reveries": {"release_year": 2005, "total_tracks": 8},
      "Blackwater Park": {"release_year": 2001, "total_tracks": 8}
    }
  },
  "tool": {
    "name": "Tool",
    "country": "United States",
    "formed_year": 1990,
    "genres": ["Progressive Metal", "Alternative Metal", "Art Rock"],
    "albums": {
      "Lateralus": {"release_year": 2001, "total_tracks": 13},
      "Ænima": {"release_year": 1996, "total_tracks": 15}
    }
  },
  "meshuggah": {
    "name": "Meshuggah",
    "country": "Sweden",
    "formed_year": 1987,
    "genres": ["Extreme Metal", "Djent", "Progressive Metal", "Polymetric Metal"],
    "albums": {
      "Destroy Erase Improve": {"release_year": 1995, "total_tracks": 10},
      "obZen": {"release_year": 2008, "total_tracks": 9}
    }
  },
  "haken": {
    "name": "Haken",
    "country": "United Kingdom",
    "formed_year": 2007,
    "genres": ["Progressive Metal", "Progressive Rock"],
    "albums": {
      "The Mountain": {"release_year": 2013, "total_tracks": 9},
      "Affinity": {"release_year": 2016, "total_tracks": 9}
    }
  },
  "animals_as_leaders": {
    "name": "Animals as Leaders",
    "country": "United States",
    "formed_year": 2007,
    "genres": ["Progressive Metal", "Djent", "Instrumental Rock"],
    "albums": {
      "Weightless": {"release_year": 2011, "total_tracks": 12},
      "The Joy of Motion": {"release_year": 2014, "total_tracks": 12}
    }
  },
  "between_the_buried_and_me": {
    "name": "Between the Buried and Me",
    "country": "United States",
    "formed_year": 2000,
    "genres": ["Progressive Metal", "Technical Death Metal", "Mathcore"],
    "albums": {
      "Alaska": {"release_year": 2005, "total_tracks": 11},
      "Colors": {"release_year": 2007, "total_tracks": 8}
    }
  },
  "epica": {
    "name": "Epica",
    "country": "Netherlands",
    "formed_year": 2002,
    "genres": ["Symphonic Metal", "Progressive Metal", "Gothic Metal"],
    "albums": {
      "The Phantom Agony": {"release_year": 2003, "total_tracks": 9},
      "Consign to Oblivion": {"release_year": 2005, "total_tracks": 11},
      "Design Your Universe": {"release_year": 2009, "total_tracks": 13},
      "Requiem for the Indifferent": {"release_year": 2012, "total_tracks": 13}
    }
  }
}


def build_artist_metadata(processed_dir: Path, output_dir: Path) -> List[Path]:
  """Scan processed track JSON files and generate artist metadata records."""
  output_dir.mkdir(parents=True, exist_ok=True)
  tracks_by_artist: Dict[str, List[TrackArchitecture]] = {}

  for track_file in processed_dir.glob("*.json"):
    try:
      data = json.loads(track_file.read_text(encoding="utf-8"))
      track = TrackArchitecture.model_validate(data)
      # slugify artist key
      artist_key = track.track_id.split("_")[0]
      if "dream_theater" in track.track_id:
        artist_key = "dream_theater"
      elif "opeth" in track.track_id:
        artist_key = "opeth"
      elif "tool" in track.track_id:
        artist_key = "tool"
      elif "meshuggah" in track.track_id:
        artist_key = "meshuggah"
      elif "haken" in track.track_id:
        artist_key = "haken"
      elif "animals_as_leaders" in track.track_id:
        artist_key = "animals_as_leaders"
      elif "between_the_buried_and_me" in track.track_id:
        artist_key = "between_the_buried_and_me"

      tracks_by_artist.setdefault(artist_key, []).append(track)
    except Exception as exc:
      print(f"[!] Skipping {track_file.name}: {exc}")

  created_files: List[Path] = []

  for artist_key, tracks in tracks_by_artist.items():
    info = ARTIST_KNOWLEDGE.get(artist_key, {
      "name": tracks[0].artist,
      "country": "Unknown",
      "formed_year": 1990,
      "genres": ["Progressive Metal"],
      "albums": {}
    })

    albums_map: Dict[str, List[str]] = {}
    for t in tracks:
      album_name = t.album if t.album else "Single / Tab Transcription"
      albums_map.setdefault(album_name, []).append(t.track_id)

    album_models: List[AlbumMetadata] = []
    for alb_name, track_ids in albums_map.items():
      known_alb = info.get("albums", {}).get(alb_name, {})
      album_models.append(
        AlbumMetadata(
          album_id=alb_name.lower().replace(" ", "_"),
          title=alb_name,
          release_year=known_alb.get("release_year", 2000),
          total_tracks=known_alb.get("total_tracks", len(track_ids)),
          parsed_tracks_count=len(track_ids),
          track_ids=track_ids
        )
      )

    artist_meta = ArtistMetadata(
      artist_id=artist_key,
      name=info["name"],
      country=info["country"],
      formed_year=info["formed_year"],
      genres=info["genres"],
      total_parsed_tracks=len(tracks),
      albums=album_models
    )

    out_file = output_dir / f"{artist_key}.json"
    out_file.write_text(json.dumps(artist_meta.model_dump(), indent=2), encoding="utf-8")
    print(f"[+] Saved artist metadata: {out_file.name} ({artist_meta.total_parsed_tracks} tracks)")
    created_files.append(out_file)

  return created_files


def main() -> None:
  parser = argparse.ArgumentParser(description="Generate artist metadata summaries")
  parser.add_argument(
    "--processed-dir",
    type=Path,
    default=Path("data/processed"),
    help="Directory containing parsed track architectures"
  )
  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("data/processed/artists"),
    help="Directory to save artist metadata files"
  )
  args = parser.parse_args()

  build_artist_metadata(args.processed_dir, args.output_dir)


if __name__ == "__main__":
  main()
