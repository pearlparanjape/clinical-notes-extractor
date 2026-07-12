# Clinical Notes Extractor

Extracts structured patient information from unstructured clinical notes using an LLM (Claude), with schema validation and error handling so the output can be trusted rather than assumed correct.

> ⚠️ **Work in progress.** Demographics extraction is implemented and working; the remaining categories (symptoms, comorbidities, medications, blood tests) and the evaluation are actively being built. See the [Roadmap](#roadmap).

## Goal

Clinical notes are written as free text — abbreviations, narrative prose, values buried in sentences, fields simply omitted. This project turns that unstructured text into **structured, validated data** that downstream systems can actually use.

The target categories are:

- **Demographics** — sex, age, weight, height, BMI *(implemented)*
- **Symptoms** — including negated ("denies chest pain") and implicit findings *(implemented)*
- **Comorbidities** — active, historical, and family history *(planned)*
- **Medications** — name, dose, route, frequency *(planned)*
- **Blood tests** — test name, value, unit, timeframe *(planned)*

Every field not stated in the note is returned as null rather than fabricated.

## Why this is hard

An LLM can read the text, but its output is unreliable: it may return malformed JSON, hallucinate values, or produce the wrong type. This project treats the LLM as an untrusted component and wraps it in layers that catch those failures:

- **Schema validation** (Pydantic) rejects output that doesn't match the expected types.
- **Structured error capture** records the failure stage (`json_parse` vs `validation`) and the raw model response, so failures are analyzable instead of lost.
- **A swappable client seam** lets the same pipeline run against the real API or a stand-in for testing, with no other code changes.

## What it extracts (currently)

Demographics are the implemented category:

| Field | Type | Notes |
|---|---|---|
| `sex` | string | "male" / "female", or null if not stated |
| `age` | number | in years; may be fractional for infants (e.g. 0.03 for ~11 days old) |
| `weight_kg` | number | kilograms; converted from imperial if needed |
| `height_cm` | number | centimeters; converted if needed |
| `bmi` | number | body mass index |

## Prerequisites

Before setting up, you need the following installed:

- **Python 3.12+** — developed with Python 3.12.13.
- **Poetry** — for dependency management (developed with Poetry 2.4).
- **An Anthropic API key** — the pipeline calls the Claude API. Get one from [console.anthropic.com](https://console.anthropic.com).

### Installing the tools

**Poetry** — install using the [official installer](https://python-poetry.org/docs/#installation).
Do **not** use `pip install poetry`: Poetry manages its own dependencies and should stay
isolated from your project environments, or the two can conflict.

**Python 3.12** — [pyenv](https://github.com/pyenv/pyenv#installation) is recommended for
managing the Python version. On macOS:

```bash
brew install pyenv
pyenv install 3.12.13
pyenv local 3.12.13
```

On Windows or Linux, see the [pyenv installation guide](https://github.com/pyenv/pyenv#installation).

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/paranjapeap5-lab/clinical-notes-extractor.git
   cd clinical-notes-extractor
   ```

2. **Install dependencies:**
   ```bash
   make install
   ```
   (This runs `poetry install`, which creates a virtual environment and installs everything.)

3. **Add your API key.** Create a file named `.env` in the project root:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
   This file is gitignored and must never be committed.

## Usage

Run the pipeline:
```bash
PYTHONPATH=. poetry run python -m src.pipeline
```

This loads a sample of clinical notes, extracts demographics from each, and writes three files to `data/`:

- `original.csv` — the input notes
- `demographics.csv` — the extracted fields only
- `combined.csv` — both, side by side

### Configuration

All settings live in `src/config.py`:

| Setting | Purpose |
|---|---|
| `DATASET` | source dataset path |
| `NOTE_COLUMN` | which column holds the note text |
| `N_NOTES` | how many notes to process |
| `RANDOM_STATE` | seed for reproducible random sampling |
| `MODEL` | which Claude model to use |

Change any setting there without touching the pipeline logic.

## Development

This project uses Black (formatting) and flake8 (linting), enforced automatically via a pre-commit hook.

```bash
make format   # auto-fix formatting with Black
make lint     # check formatting + linting (does not modify files)
```

The pre-commit hook runs these checks on every commit and blocks the commit if they fail. To set it up after cloning:
```bash
poetry run pre-commit install
```

## How it handles failures

The extractor never crashes on a bad note. Each note produces one of:

- **Success** -> `{"status": "ok", "data": {...}}`
- **Failure** -> `{"status": "error", "stage": ..., "error": ..., "raw": ...}`

The `stage` distinguishes a JSON parsing failure from a schema validation failure — different problems with different causes. The raw model response is kept for debugging. In a batch run, failures are recorded (in the terminal and the output) while the run continues, so one problematic note never loses the rest.

## Project structure

```
clinical-notes-extractor/
├── src/
│   ├── config.py          # all settings in one place
│   ├── schemas.py         # Pydantic models — the source of truth for output shape
│   ├── claude_client.py   # real Claude API client
│   ├── fake_client.py     # stand-in client for testing (no API calls)
│   ├── extractor.py       # prompt -> call -> parse -> validate; returns structured result
│   └── pipeline.py        # load -> extract -> save three CSVs
├── data/                  # outputs (gitignored)
├── Makefile
├── pyproject.toml
├── .env                   # API key (gitignored, never committed)
└── README.md
```

## Data

Designed for the [`AGBonnet/augmented-clinical-notes`](https://huggingface.co/datasets/AGBonnet/augmented-clinical-notes) dataset — de-identified clinical case notes derived from PubMed Central case studies, loaded directly from Hugging Face.

**Do not use real, identifiable patient data with this tool.** It is for research and de-identified public data only.

## Roadmap

🚧 *In progress — items are checked off as they land.*


- [X] Additional fields: symptoms (with negation handling), comorbidities, medications, blood tests
- [ ] Span grounding to catch hallucinated findings
- [ ] Evaluation against hand-labeled ground truth (precision / recall per field)
- [ ] Robust batch processing (checkpointing, resume) for the full dataset
- [ ] Model comparison across cost / quality / latency

## Limitations

This is a research and portfolio project — **not a medical device**. Extraction is imperfect; do not use it for clinical decisions. The LLM can make mistakes the validation layer does not catch (e.g. a plausible-but-wrong value). Accuracy has not yet been formally measured (see roadmap).

## License

MIT — see [LICENSE](LICENSE).
