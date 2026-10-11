"""Pydantic data models for progressive metal track architectures and artist metadata.

Adheres strictly to schemas in `schemas/track_architecture.json` and `schemas/artist_metadata.json`.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Section(BaseModel):
  """Musical section bounds."""

  label: str = Field(description="Section name (e.g. Intro, Verse 1, Solo, Outro)")
  start_measure: int = Field(ge=1, description="1-indexed starting measure")
  end_measure: Optional[int] = Field(default=None, ge=1, description="1-indexed ending measure")


class Measure(BaseModel):
  """Measure-by-measure structural breakdown."""

  measure_number: int = Field(ge=1, description="1-indexed measure sequence number")
  time_signature: str = Field(
    pattern=r"^[0-9]+/[0-9]+$", description="Time signature fraction (e.g. 4/4, 7/8)"
  )
  tempo_bpm: float = Field(gt=0, description="Tempo in beats per minute")
  section_label: Optional[str] = Field(
    default=None, description="Active or newly starting section label"
  )
  notes: Optional[str] = Field(default=None, description="Structural annotations")


class TrackArchitecture(BaseModel):
  """Full track structural architecture model."""

  track_id: str = Field(description="Unique identifier for the track (slug)")
  title: str = Field(description="Track title")
  artist: str = Field(description="Artist or band name")
  album: Optional[str] = Field(default="", description="Album title")
  year: Optional[int] = Field(default=None, ge=1900, description="Release year")
  source_file: Optional[str] = Field(default=None, description="Source file name or path")
  source_format: Optional[Literal["gp3", "gp4", "gp5", "gpx", "gp", "midi", "mid"]] = Field(
    default=None, description="Original file format"
  )
  total_measures: Optional[int] = Field(
    default=None, ge=1, description="Total measure count in track"
  )
  default_tempo_bpm: Optional[float] = Field(default=None, gt=0, description="Initial tempo in BPM")
  default_time_signature: Optional[str] = Field(
    default=None, pattern=r"^[0-9]+/[0-9]+$", description="Initial time signature fraction"
  )
  sections: List[Section] = Field(
    default_factory=list, description="High-level musical section definitions"
  )
  measures: List[Measure] = Field(
    default_factory=list, description="Measure-by-measure structural architecture"
  )


class AlbumMetadata(BaseModel):
  """Album discography context."""

  album_id: Optional[str] = Field(default=None, description="Identifier for the album")
  title: str = Field(description="Album title")
  release_year: int = Field(ge=1900, description="Album release year")
  total_tracks: Optional[int] = Field(
    default=None, ge=1, description="Total tracks on released album"
  )
  parsed_tracks_count: int = Field(ge=0, description="Count of tracks ingested into dataset")
  track_ids: Optional[List[str]] = Field(
    default_factory=list, description="References to track IDs"
  )


class ArtistMetadata(BaseModel):
  """Artist and discography metadata model."""

  artist_id: str = Field(description="Unique identifier for the artist")
  name: str = Field(description="Band or artist name")
  country: Optional[str] = Field(default=None, description="Country of origin")
  formed_year: Optional[int] = Field(default=None, ge=1900, description="Year formed")
  genres: Optional[List[str]] = Field(default_factory=list, description="Associated genres")
  total_parsed_tracks: int = Field(ge=0, description="Total number of tracks parsed into dataset")
  albums: List[AlbumMetadata] = Field(default_factory=list, description="Album discography context")
