from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import difflib
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


ID_CANDIDATES = ["id", "painting_id", "object_id", "artwork_id", "image_id"]
SET_CANDIDATES = ["set", "set_id", "collection", "group", "bundle"]
TITLE_CANDIDATES = ["title", "name", "artwork_title"]
ARTIST_CANDIDATES = ["artist", "creator", "painter"]
YEAR_CANDIDATES = ["year", "date", "date_year", "year_created", "creation_year"]
IMAGE_CANDIDATES = [
    "image",
    "image_file",
    "filename",
    "file",
    "img",
    "image_filename",
    "image_path",
]


@dataclass(frozen=True)
class PaintingRecord:
    id: str
    set_id: str
    title: str
    artist: str
    year: Optional[str]
    image_filename: Optional[str]
    metadata: Dict[str, Any]

    @property
    def image_url(self) -> Optional[str]:
        if not self.image_filename:
            return None
        return f"/static/paintings/{self.image_filename}"


@dataclass(frozen=True)
class PaintingSet:
    set_id: str
    paintings: List[PaintingRecord]


class PaintingStore:
    def __init__(self, records: Dict[str, PaintingRecord]) -> None:
        self._records = records
        self._sets: Dict[str, List[PaintingRecord]] = {}
        for record in records.values():
            self._sets.setdefault(record.set_id, []).append(record)

    @property
    def sets(self) -> Dict[str, List[PaintingRecord]]:
        return self._sets

    def get(self, painting_id: str) -> PaintingRecord:
        if painting_id not in self._records:
            raise KeyError(painting_id)
        return self._records[painting_id]

    @classmethod
    def from_csv(cls, csv_path: str, paintings_dir: Path) -> "PaintingStore":
        df = pd.read_csv(csv_path)
        df.columns = [normalize_header(col) for col in df.columns]
        columns = set(df.columns)

        id_col = find_column(columns, ID_CANDIDATES)
        title_col = find_column(columns, TITLE_CANDIDATES)
        artist_col = find_column(columns, ARTIST_CANDIDATES)
        year_col = find_column(columns, YEAR_CANDIDATES)
        set_col = find_column(columns, SET_CANDIDATES)
        image_col = find_column(columns, IMAGE_CANDIDATES)

        image_index = build_image_index(paintings_dir)
        records: Dict[str, PaintingRecord] = {}
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            painting_id = normalize_value(row_dict.get(id_col)) if id_col else None
            if not painting_id:
                painting_id = f"row_{idx + 1}"

            title = normalize_value(row_dict.get(title_col)) if title_col else ""
            artist = normalize_value(row_dict.get(artist_col)) if artist_col else ""
            year = normalize_value(row_dict.get(year_col)) if year_col else None

            image_value = normalize_value(row_dict.get(image_col)) if image_col else None
            image_filename = resolve_image_filename(
                image_value,
                painting_id,
                title,
                image_index,
            )

            set_id = normalize_value(row_dict.get(set_col)) if set_col else None
            if not set_id:
                set_id = infer_set_id(image_value, painting_id, title)

            metadata = build_metadata(
                row_dict,
                exclude={
                    id_col,
                    title_col,
                    artist_col,
                    year_col,
                    set_col,
                    image_col,
                },
            )

            records[painting_id] = PaintingRecord(
                id=painting_id,
                set_id=set_id,
                title=title or "Untitled",
                artist=artist or "Unknown",
                year=year,
                image_filename=image_filename,
                metadata=metadata,
            )

        return cls(records)


def normalize_header(header: Any) -> str:
    return str(header).strip().lower().replace(" ", "_")


def find_column(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def normalize_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return None
    return text


def infer_set_id(image_value: Optional[str], painting_id: str, title: str) -> str:
    for candidate in (image_value, painting_id, title):
        prefix = extract_prefix(candidate)
        if prefix:
            return prefix
    return "unknown"


def extract_prefix(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    stem = Path(str(value)).stem
    for separator in ("_", "-"):
        if separator in stem:
            prefix = stem.split(separator, 1)[0]
            if prefix:
                return prefix
    return None


def build_image_index(paintings_dir: Path) -> Dict[str, Dict[str, str]]:
    index = {
        "filename": {},
        "stem": {},
        "slug": {},
    }
    if not paintings_dir.exists():
        return index

    for file in paintings_dir.iterdir():
        if not file.is_file() or file.name.startswith("."):
            for row in rows:
    if not isinstance(row, dict):
        continue

    if not row.get(id_field):
        continue
        filename = file.name
        stem = file.stem
        slug = slugify(stem)
        index["filename"][filename.lower()] = filename
        index["stem"][stem.lower()] = filename
        if slug:
            index["slug"][slug] = filename

    return index


def resolve_image_filename(
    image_value: Optional[str],
    painting_id: str,
    title: str,
    image_index: Dict[str, Dict[str, str]],
) -> Optional[str]:
    for candidate in (image_value, painting_id, title):
        resolved = match_image_candidate(candidate, image_index)
        if resolved:
            return resolved
    return None


def match_image_candidate(
    candidate: Optional[str], image_index: Dict[str, Dict[str, str]]
) -> Optional[str]:
    if not candidate:
        return None
    raw_name = Path(str(candidate)).name
    filename = image_index["filename"].get(raw_name.lower())
    if filename:
        return filename

    stem = Path(raw_name).stem
    filename = image_index["stem"].get(stem.lower())
    if filename:
        return filename

    slug = slugify(stem)
    if slug:
        return image_index["slug"].get(slug)
    return None


def build_metadata(row: Dict[str, Any], exclude: Iterable[Optional[str]]) -> Dict[str, Any]:
    excluded = {key for key in exclude if key}
    metadata: Dict[str, Any] = {}
    for key, value in row.items():
        if key in excluded:
            continue
        cleaned = normalize_value(value)
        if cleaned is None:
            continue
        metadata[key] = cleaned
    return metadata


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in value)
    return "-".join(part for part in cleaned.split() if part)