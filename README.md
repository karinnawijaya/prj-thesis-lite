# ArtWeave Backend

## Overview
This FastAPI backend provides painting sets, paintings per set, and an AI-generated connection summary between two selected paintings. It loads metadata from `Painting_Metadata_260127.csv` at startup and serves images from `assets/paintings/`.

## Set inference rule
If the metadata CSV does not include a set column (e.g., `set`, `collection`, `group`), the backend derives `set_id` from the image filename prefix before the first underscore or dash. For example, `A_01.jpg` becomes set `A`. If no image filename exists, it attempts the same prefix rule on the painting ID or title; otherwise, it falls back to `unknown`.

## Running locally
```bash
uvicorn fastapi_app:app --reload
```

The API expects `OPENAI_API_KEY` to be set for comparison summaries.