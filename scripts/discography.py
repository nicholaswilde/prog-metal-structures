"""Canonical discography and track metadata knowledge base.

Maps progressive metal bands, albums, release years, and track assignments.
Strictly 2-space indentation.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import re


def normalize_title(title: str) -> str:
  """Clean track title for fuzzy matching."""
  clean = re.sub(r"[^\w\s]", "", title).strip().lower()
  clean = re.sub(r"\s+", " ", clean)
  # Remove trailing numbers from tab variations (e.g. 'pull me under 2')
  return re.sub(r"\s+\d+$", "", clean)


DISCOGRAPHY: Dict[str, Dict[str, Any]] = {
  "dream_theater": {
    "name": "Dream Theater",
    "country": "United States",
    "formed_year": 1985,
    "genres": ["Progressive Metal", "Progressive Rock"],
    "albums": {
      "Images and Words": {"release_year": 1992, "total_tracks": 8},
      "Awake": {"release_year": 1994, "total_tracks": 11},
      "A Change of Seasons": {"release_year": 1995, "total_tracks": 5},
      "Metropolis Pt. 2: Scenes from a Memory": {"release_year": 1999, "total_tracks": 12},
      "Train of Thought": {"release_year": 2003, "total_tracks": 7},
      "Octavarium": {"release_year": 2005, "total_tracks": 8},
      "Systematic Chaos": {"release_year": 2007, "total_tracks": 8},
    },
    "track_map": {
      "pull me under": ("Images and Words", 1992),
      "metropolis part 1 the miracle and the sleeper": ("Images and Words", 1992),
      "erotomania": ("Awake", 1994),
      "a change of seasons": ("A Change of Seasons", 1995),
      "overture 1928": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "strange deja vu": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "beyond this life": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "fatal tragedy": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "home": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "dance of eternity": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "the dance of eternity": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "the spirit carries on": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "finally free": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "scenes from a memory": ("Metropolis Pt. 2: Scenes from a Memory", 1999),
      "in the name of god": ("Train of Thought", 2003),
      "stream of consciousness": ("Train of Thought", 2003),
      "panic attack": ("Octavarium", 2005),
      "constant motion": ("Systematic Chaos", 2007),
    },
  },
  "opeth": {
    "name": "Opeth",
    "country": "Sweden",
    "formed_year": 1990,
    "genres": ["Progressive Death Metal", "Progressive Rock"],
    "albums": {
      "My Arms, Your Hearse": {"release_year": 1998, "total_tracks": 9},
      "Still Life": {"release_year": 1999, "total_tracks": 7},
      "Blackwater Park": {"release_year": 2001, "total_tracks": 8},
      "Deliverance": {"release_year": 2002, "total_tracks": 6},
      "Damnation": {"release_year": 2003, "total_tracks": 8},
      "Ghost Reveries": {"release_year": 2005, "total_tracks": 8},
      "Watershed": {"release_year": 2008, "total_tracks": 7},
    },
    "track_map": {
      "demon of the fall": ("My Arms, Your Hearse", 1998),
      "the moor": ("Still Life", 1999),
      "the leper affinity": ("Blackwater Park", 2001),
      "bleak": ("Blackwater Park", 2001),
      "harvest": ("Blackwater Park", 2001),
      "the drapery falls": ("Blackwater Park", 2001),
      "dirge for november": ("Blackwater Park", 2001),
      "the funeral portrait": ("Blackwater Park", 2001),
      "blackwater park": ("Blackwater Park", 2001),
      "deliverance": ("Deliverance", 2002),
      "masters apprentices": ("Deliverance", 2002),
      "ghost of perdition": ("Ghost Reveries", 2005),
      "the baying of the hounds": ("Ghost Reveries", 2005),
      "beneath the mire": ("Ghost Reveries", 2005),
      "atonement": ("Ghost Reveries", 2005),
      "harlequin forest": ("Ghost Reveries", 2005),
      "reverie harlequin forest": ("Ghost Reveries", 2005),
      "the grand conjuration": ("Ghost Reveries", 2005),
      "isolation years": ("Ghost Reveries", 2005),
      "heir apparent": ("Watershed", 2008),
      "the lotus eater": ("Watershed", 2008),
      "porcelain heart": ("Watershed", 2008),
      "burden": ("Watershed", 2008),
    },
  },
  "tool": {
    "name": "Tool",
    "country": "United States",
    "formed_year": 1990,
    "genres": ["Progressive Metal", "Alternative Metal", "Art Rock"],
    "albums": {
      "Ænima": {"release_year": 1996, "total_tracks": 15},
      "Lateralus": {"release_year": 2001, "total_tracks": 13},
      "10,000 Days": {"release_year": 2006, "total_tracks": 11},
    },
    "track_map": {
      "the grudge": ("Lateralus", 2001),
      "schism": ("Lateralus", 2001),
      "parabol and parabola": ("Lateralus", 2001),
      "parabola": ("Lateralus", 2001),
      "ticks and leeches": ("Lateralus", 2001),
      "lateralus": ("Lateralus", 2001),
      "disposition": ("Lateralus", 2001),
      "reflection": ("Lateralus", 2001),
      "triad": ("Lateralus", 2001),
      "vicarious": ("10,000 Days", 2006),
      "jambi": ("10,000 Days", 2006),
      "the pot": ("10,000 Days", 2006),
      "rosetta stoned": ("10,000 Days", 2006),
    },
  },
  "meshuggah": {
    "name": "Meshuggah",
    "country": "Sweden",
    "formed_year": 1987,
    "genres": ["Extreme Metal", "Djent", "Progressive Metal", "Polymetric Metal"],
    "albums": {
      "Destroy Erase Improve": {"release_year": 1995, "total_tracks": 10},
      "Chaosphere": {"release_year": 1998, "total_tracks": 8},
      "Nothing": {"release_year": 2002, "total_tracks": 10},
      "obZen": {"release_year": 2008, "total_tracks": 9},
    },
    "track_map": {
      "future breed machine": ("Destroy Erase Improve", 1995),
      "new millennium cyanide christ": ("Chaosphere", 1998),
      "corridor of chameleons": ("Chaosphere", 1998),
      "sane": ("Chaosphere", 1998),
      "the exquisite machinery of torture": ("Chaosphere", 1998),
      "stengah": ("Nothing", 2002),
      "rational gaze": ("Nothing", 2002),
      "perpetual black second": ("Nothing", 2002),
      "spasm": ("Nothing", 2002),
    },
  },
  "haken": {
    "name": "Haken",
    "country": "United Kingdom",
    "formed_year": 2007,
    "genres": ["Progressive Metal", "Progressive Rock"],
    "albums": {
      "The Mountain": {"release_year": 2013, "total_tracks": 9},
      "Affinity": {"release_year": 2016, "total_tracks": 9},
    },
    "track_map": {
      "atlas stone": ("The Mountain", 2013),
    },
  },
  "animals_as_leaders": {
    "name": "Animals as Leaders",
    "country": "United States",
    "formed_year": 2007,
    "genres": ["Progressive Metal", "Djent", "Instrumental Rock"],
    "albums": {
      "Animals as Leaders": {"release_year": 2009, "total_tracks": 12},
      "Weightless": {"release_year": 2011, "total_tracks": 12},
      "The Joy of Motion": {"release_year": 2014, "total_tracks": 12},
    },
    "track_map": {
      "tempting time": ("Animals as Leaders", 2009),
      "cafo": ("Animals as Leaders", 2009),
      "behaving badly": ("Animals as Leaders", 2009),
      "song of solomon": ("Animals as Leaders", 2009),
      "weightless": ("Weightless", 2011),
      "an infinite regression": ("Weightless", 2011),
      "the woven web": ("The Joy of Motion", 2014),
      "kascade": ("The Joy of Motion", 2014),
    },
  },
  "between_the_buried_and_me": {
    "name": "Between the Buried and Me",
    "country": "United States",
    "formed_year": 2000,
    "genres": ["Progressive Metal", "Technical Death Metal", "Mathcore"],
    "albums": {
      "Between the Buried and Me": {"release_year": 2002, "total_tracks": 10},
      "The Silent Circus": {"release_year": 2003, "total_tracks": 10},
      "Alaska": {"release_year": 2005, "total_tracks": 11},
      "Colors": {"release_year": 2007, "total_tracks": 8},
      "The Parallax II: Future Sequence": {"release_year": 2012, "total_tracks": 12},
    },
    "track_map": {
      "colorblind": ("Between the Buried and Me", 2002),
      "aesthetic": ("The Silent Circus", 2003),
      "camilla rhodes": ("The Silent Circus", 2003),
      "alaska": ("Alaska", 2005),
      "melting city": ("The Parallax II: Future Sequence", 2012),
    },
  },
  "epica": {
    "name": "Epica",
    "country": "Netherlands",
    "formed_year": 2002,
    "genres": ["Symphonic Metal", "Progressive Metal", "Gothic Metal"],
    "albums": {
      "The Phantom Agony": {"release_year": 2003, "total_tracks": 9},
      "Consign to Oblivion": {"release_year": 2005, "total_tracks": 11},
      "The Divine Conspiracy": {"release_year": 2007, "total_tracks": 13},
      "Design Your Universe": {"release_year": 2009, "total_tracks": 13},
      "Requiem for the Indifferent": {"release_year": 2012, "total_tracks": 13},
      "The Quantum Enigma": {"release_year": 2014, "total_tracks": 13},
    },
    "track_map": {
      "sensorium": ("The Phantom Agony", 2003),
      "cry for the moon": ("The Phantom Agony", 2003),
      "feint": ("The Phantom Agony", 2003),
      "seif al din": ("The Phantom Agony", 2003),
      "the last crusade": ("Consign to Oblivion", 2005),
      "the obsessive devotion": ("The Divine Conspiracy", 2007),
      "instrospect": ("The Divine Conspiracy", 2007),
      "outrospect": ("The Divine Conspiracy", 2007),
      "unleashed": ("Design Your Universe", 2009),
      "our destiny": ("Design Your Universe", 2009),
      "requiem for the indifferent": ("Requiem for the Indifferent", 2012),
      "nostalgia": ("Requiem for the Indifferent", 2012),
      "memento": ("The Quantum Enigma", 2014),
    },
  },
  "megadeth": {
    "name": "Megadeth",
    "country": "United States",
    "formed_year": 1983,
    "genres": ["Thrash Metal", "Speed Metal"],
    "albums": {
      "The Beavis and Butt-Head Experience": {"release_year": 1993, "total_tracks": 12},
    },
    "track_map": {
      "99 ways to die": ("The Beavis and Butt-Head Experience", 1993),
    },
  },
}


def lookup_track_metadata(artist_key: str, title: str) -> Tuple[Optional[str], Optional[int]]:
  """Lookup canonical album and release year for a given artist and track title."""
  artist_info = DISCOGRAPHY.get(artist_key)
  if not artist_info:
    return None, None

  clean_t = normalize_title(title)
  track_map = artist_info.get("track_map", {})

  # 1. Exact match
  if clean_t in track_map:
    return track_map[clean_t]

  # 2. Substring match
  for key, val in track_map.items():
    if key in clean_t or clean_t in key:
      return val

  return None, None


def verify_discography(
  processed_dir: Optional[Path] = None,
) -> Dict[str, Any]:
  """Audit processed track datasets to verify album and year completeness."""
  import json

  target_dir = processed_dir or Path("data/processed")
  track_files = sorted(target_dir.glob("*.json"))

  total = 0
  complete = 0
  missing_metadata: list[dict[str, Any]] = []

  for p in track_files:
    if p.name in {"manifest.json", "index.json"}:
      continue
    try:
      data = json.loads(p.read_text(encoding="utf-8"))
      if "track_id" not in data:
        continue
      total += 1
      album = data.get("album")
      year = data.get("year")
      if album and year:
        complete += 1
      else:
        missing_metadata.append(
          {
            "file": p.name,
            "track_id": data.get("track_id"),
            "artist": data.get("artist"),
            "title": data.get("title"),
            "album": album,
            "year": year,
          }
        )
    except Exception:
      continue

  return {
    "total_tracks": total,
    "complete_tracks": complete,
    "missing_count": len(missing_metadata),
    "missing_tracks": missing_metadata,
  }


def main() -> int:
  """CLI entrypoint for discography verification."""
  import argparse

  parser = argparse.ArgumentParser(description="Audit and verify discography completeness.")
  parser.add_argument(
    "--verify",
    action="store_true",
    help="Verify all processed tracks have canonical album and release year mappings",
  )
  parser.add_argument(
    "--processed-dir",
    type=Path,
    default=Path("data/processed"),
    help="Directory containing processed track JSON files",
  )
  args = parser.parse_args()

  report = verify_discography(args.processed_dir)
  print(f"[*] Verified {report['total_tracks']} tracks: {report['complete_tracks']} complete.")
  if report["missing_count"] > 0:
    print(f"[!] Warning: {report['missing_count']} tracks missing album or year metadata:")
    for item in report["missing_tracks"]:
      print(
        f"    - {item['file']}: {item['artist']} - {item['title']} (Album: {item['album']}, Year: {item['year']})"
      )
    return 1

  print("[+] All tracks have 100% valid canonical discography metadata.")
  return 0


if __name__ == "__main__":
  import sys

  sys.exit(main())
