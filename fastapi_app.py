from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from data_store import PaintingRecord, PaintingStore

from openai import OpenAI


DATASET_FILE = "Painting_Metadata_260127.csv"
PAINTINGS_DIR = Path("assets/paintings")


class HealthResponse(BaseModel):
    ok: bool


class SetInfo(BaseModel):
    set_id: str
    label: str
    count: int


class SetsResponse(BaseModel):
    sets: List[SetInfo]


class PaintingSummary(BaseModel):
    id: str
    title: str
    artist: str
    year: Optional[str]
    image_url: Optional[str]
    alt: str
    metadata: Dict[str, Any]


class PaintingsResponse(BaseModel):
    set_id: str
    paintings: List[PaintingSummary]


class CompareRequest(BaseModel):
    painting_a_id: str = Field(..., min_length=1)
    painting_b_id: str = Field(..., min_length=1)


class CompareArtwork(BaseModel):
    id: str
    title: str
    artist: str
    year: Optional[str]
    image_url: Optional[str]


class CompareOverview(BaseModel):
    artworkA: CompareArtwork
    artworkB: CompareArtwork
    summary: str


class CompareResponse(BaseModel):
    overview: CompareOverview


app = FastAPI(title="ArtWeave API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/paintings", StaticFiles(directory=PAINTINGS_DIR), name="paintings")

store: Optional[PaintingStore] = None


@app.on_event("startup")
def startup_event() -> None:
    global store
    store = PaintingStore.from_csv(DATASET_FILE, PAINTINGS_DIR)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True)


@app.get("/api/sets", response_model=SetsResponse)
def list_sets() -> SetsResponse:
    if store is None:
        raise HTTPException(status_code=500, detail="Painting store not initialized.")
    sets: List[SetInfo] = []
    for set_id, paintings in sorted(store.sets.items(), key=lambda item: item[0]):
        label = f"Set {set_id}"
        sets.append(SetInfo(set_id=set_id, label=label, count=len(paintings)))
    return SetsResponse(sets=sets)


@app.get("/api/paintings", response_model=PaintingsResponse)
def list_paintings(set_id: str = Query(..., alias="set_id")) -> PaintingsResponse:
    if store is None:
        raise HTTPException(status_code=500, detail="Painting store not initialized.")
    paintings = store.sets.get(set_id)
    if paintings is None:
        raise HTTPException(status_code=404, detail="Set not found.")
    payload = [painting_to_summary(painting) for painting in paintings]
    return PaintingsResponse(set_id=set_id, paintings=payload)


@app.post("/api/compare", response_model=CompareResponse)
def compare_paintings(payload: CompareRequest) -> CompareResponse:
    if store is None:
        raise HTTPException(status_code=500, detail="Painting store not initialized.")
    if payload.painting_a_id == payload.painting_b_id:
        raise HTTPException(status_code=400, detail="Painting IDs must differ.")

    painting_a = resolve_painting(payload.painting_a_id)
    painting_b = resolve_painting(payload.painting_b_id)

    summary = generate_summary(painting_a, painting_b)
    overview = CompareOverview(
        artworkA=painting_to_compare(painting_a),
        artworkB=painting_to_compare(painting_b),
        summary=summary,
    )
    return CompareResponse(overview=overview)


def resolve_painting(painting_id: str) -> PaintingRecord:
    if store is None:
        raise HTTPException(status_code=500, detail="Painting store not initialized.")
    try:
        return store.get(painting_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Painting not found.") from exc


def painting_to_summary(painting: PaintingRecord) -> PaintingSummary:
    alt = painting.title
    if painting.artist and painting.artist != "Unknown":
        alt = f"{painting.title} by {painting.artist}"
    return PaintingSummary(
        id=painting.id,
        title=painting.title,
        artist=painting.artist,
        year=painting.year,
        image_url=painting.image_url,
        alt=alt,
        metadata=painting.metadata,
    )


def painting_to_compare(painting: PaintingRecord) -> CompareArtwork:
    return CompareArtwork(
        id=painting.id,
        title=painting.title,
        artist=painting.artist,
        year=painting.year,
        image_url=painting.image_url,
    )


def generate_summary(painting_a: PaintingRecord, painting_b: PaintingRecord) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4o-mini",
        temperature=0.2,
        input=[
            {
                "role": "system",
                "content": "You are an art historian who writes concise connection summaries.",
            },
            {
                "role": "user",
                "content": (
                    "Write a short paragraph connecting these two paintings. "
                    "Focus on shared themes, stylistic links, and contrasts. "
                    "Avoid bullet points.\n\n"
                    f"Painting A: {painting_a.title} by {painting_a.artist}"
                    f" ({painting_a.year or 'unknown year'}).\n"
                    f"Painting B: {painting_b.title} by {painting_b.artist}"
                    f" ({painting_b.year or 'unknown year'})."
                ),
            },
        ],
    )
    return response.output_text.strip()
