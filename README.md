# CSS-Project-A

Data analysis and visualization project focused on artists, lyrics sentiment, and migration/geographic context, with an interactive website deployed via GitHub Pages.

## Repository Structure

- `website/`: React + Vite frontend for interactive presentation.
- `data/`: generated CSVs, maps, and processed outputs.
- `lyrics_data/`: raw/extra lyrics JSON sources.
- `scripts/`: analysis pipelines and MusicBrainz network utilities.
- `notebooks/`: exploratory and explanatory notebooks.

## Local Setup

### 1) Python environment

From repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Website dependencies

```bash
cd website
npm install
```

## Run the Project

### Website (dev)

```bash
cd website
npm run dev
```

### Website (production preview)

```bash
cd website
npm run build
npm run preview
```

### Key Python scripts

From repo root:

```bash
python generate_charts.py
python translate_and_sentiment.py
python print_artists.py
python scripts/run_analysis.py
```

### MusicBrainz API smoke test

```bash
python scripts/musicbrainz_network/test_musicbrainz_api.py
```

## GitHub Pages

- Vite base path is configured in `website/vite.config.js` for repo pages.
- Deploy workflow is in `.github/workflows/deploy.yml` and triggers on pushes to `main`.

## Submission Checklist

- Python dependencies install successfully with `requirements.txt`.
- Website passes lint/build:

```bash
cd website
npm run lint
npm run build
```

- Notebook outputs are saved if required by your course rubric.
- Push your final branch and ensure GitHub Pages workflow passes.
