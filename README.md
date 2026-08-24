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

## Historical queries

Translation against an older schema is selected with one revision selector:

```bash
python translator_module/cli.py \
  --commit-hash <full-or-short-sha> \
  --repo G:/path/to/oks-repository
```

The CLI also accepts `--tag`, `--date <ISO-8601-with-timezone>`, or
`--run-id <id> --run-map <json-file>`. Historical schema and few-shot files
are read from that Git revision without checking out the working tree.

To execute the translated query against historical data, add `--execute`:

```bash
python translator_module/cli.py \
  --commit-hash <sha> \
  --repo G:/path/to/oks-repository \
  --execute \
  --target-class Application \
  --data-path test_data/application.data.xml \
  --oks-dump-executable /path/to/oks_dump \
  --execution-format json
```

Repeat `--data-path` for multiple files. If omitted, the CLI discovers
`test_data/**/*.data.xml` in the selected revision. Execution is opt-in and
requires the native `oks_dump` executable; without it, the CLI still supports
historical translation and reports a clear execution error. The `json` format
emits revision, repository, schema/data paths, command arguments, return code,
and the native stdout/stderr without attempting to reinterpret native output.

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
eval_dataset/        Schema corpus and evaluation query set, plus the builder that generates them
test_schema/         ATLAS TDAQ OKS schema files (XML and a derived JSON inventory)
test_data/           ATLAS TDAQ OKS data files (concrete objects)
oks_scraped/         Curated OKS schema, examples, source material, and report
output/              Research collection scripts and extracted reference material
docs/                Project and OKS reference documents, architecture diagram
```

The application expects `oks_scraped/oks_schema_examples.xml` and `oks_scraped/gold_pairs.jsonl` at their current paths. Keep those files alongside the source unless the application paths are updated too.

## Evaluation

`eval_dataset/` holds the two files the pipeline is scored against:

- `oks_schema_corpus.xml` — the retrieval corpus (454 configuration classes, 825 objects, and the OKS C++ API as 22 OKS classes). Drop-in for `HybridIndexer.ingest_xml`.
- `oks_eval_queries.jsonl` — 144 shifter questions stratified easy/medium/hard, each with the ground-truth `OksQuery`, its IR, the gold schema elements and the expected result set.

Regenerate them after changing `test_schema/`, `test_data/` or `eval_dataset/query_specs.py`:

```bash
python eval_dataset/build_dataset.py
```

See [`eval_dataset/README.md`](eval_dataset/README.md) for the field reference and metric definitions, and [`rag.md`](rag.md) for the retrieval architecture they measure.

## Development notes

- Create a dedicated virtual environment in `.venv/`; it is ignored by Git.
- Keep generated caches, logs, and local editor settings untracked.
- Add dependencies to `translator_module/requirements.txt` and record why in the relevant change.
- Add or update tests under `translator_module/tests/` when changing query validation or serialization behavior.
