# OKS Intelligent Query Agent

A Python proof of concept that converts natural-language questions into CERN OKS query expressions. It uses retrieved OKS schema context and few-shot examples to guide an OpenAI-compatible language model, then validates and serializes the result.

## Quick start

Requirements: Python 3.10 or newer and an API key for an OpenAI-compatible LLM provider.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r translator_module/requirements.txt
cp .env.example .env
```

Edit `.env` with your API key, model, and API base URL, then start the interactive CLI:

```bash
python translator_module/cli.py
```

Run the test suite from the repository root:

```bash
PYTHONPATH=translator_module python -m unittest discover -s translator_module/tests -v
```

## Configuration

`.env.example` documents the local configuration values:

| Variable | Purpose |
| --- | --- |
| `LLM_API_KEY` | API key for the selected LLM provider. |
| `LLM_MODEL` | Model identifier sent to that provider. |
| `LLM_BASE_URL` | OpenAI-compatible API base URL. |

Copy the example to `.env`; `.env` is intentionally ignored by Git. Do not put credentials in source files, notebooks, or issue comments.

## Repository layout

```text
translator_module/   Application source, CLI, dependency list, and unit tests
oks_scraped/         Curated OKS schema, examples, source material, and report
output/              Research collection scripts and extracted reference material
*.pdf                Project and OKS reference documents
```

The application expects `oks_scraped/oks_schema_examples.xml` and `oks_scraped/gold_pairs.jsonl` at their current paths. Keep those files alongside the source unless the application paths are updated too.

## Development notes

- Create a dedicated virtual environment in `.venv/`; it is ignored by Git.
- Keep generated caches, logs, and local editor settings untracked.
- Add dependencies to `translator_module/requirements.txt` and record why in the relevant change.
- Add or update tests under `translator_module/tests/` when changing query validation or serialization behavior.
