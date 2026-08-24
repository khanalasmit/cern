# OKS Intelligent Query Agent

A Python proof of concept and complete translation module that converts natural-language questions into CERN OKS query expressions. It uses retrieved OKS schema context and few-shot examples to guide an OpenAI-compatible language model, then validates, executes (via `oks_dump` or Python `config`), and explains the result.

---

## Quick Start / Run Instructions

Follow the complete setup and run sequence below:

### 1. Sourcing TDAQ Release (CERN lxplus / CVMFS)

If running on CERN `lxplus` or any machine with CVMFS mounted, source the ATLAS TDAQ release setup script:

```bash
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
```

*(If running locally without CVMFS, the pipeline automatically falls back to bundled schema XML files in `test_schema/` and `oks_scraped/`.)*

---

### 2. Git Clone

Clone the repository and switch into the workspace directory:

```bash
git clone https://github.com/khanalasmit/cern.git
cd cern
```

---

### 3. Create Virtual Environment (`venv`)

Create a Python 3.10+ virtual environment:

```bash
python3 -m venv .venv
```

*(On Windows: `python -m venv .venv`)*

---

### 4. Activate Virtual Environment

Activate the virtual environment:

- **Linux / CERN lxplus:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

---

### 5. Install Dependencies

Install the package dependencies:

```bash
pip install -r oksquery_translator/requirements.txt
```

---

### 6. Configure Environment (`.env`)

Copy the example environment configuration to `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your LLM provider credentials:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.xiaomimimo.com/v1
LLM_MODEL=mimo-v2.5-pro
```

| Variable | Purpose |
| --- | --- |
| `LLM_API_KEY` | API key for the selected LLM provider. |
| `LLM_MODEL` | Model identifier sent to that provider. |
| `LLM_BASE_URL` | OpenAI-compatible API base URL. |

> `.env` is ignored by Git. Do not commit API credentials to version control.

---

### 7. Running the Application

#### A. Interactive CLI

Start the interactive natural-language translation shell:

```bash
python -m oksquery_translator.cli
```

Available commands inside the CLI:
- **Natural Language Question**: Type your question directly (e.g. `Which test executables take longer than 2 seconds to initialise?`).
- `translate <question>` — Translate and validate the query without executing it.
- `probe` — Run environment detection for OKS binaries, schema directories, and class counts.
- `version <timestamp>` — Set point-in-time temporal versioning for historical queries.
- `exit` / `quit` — Exit the prompt.

#### B. Programmatic Usage

```python
from oksquery_translator import answer, OksPipeline

# Simple one-liner query
print(answer("Which test executables take longer than 2 seconds to initialise?"))

# Using the pipeline instance
pipeline = OksPipeline()
result = pipeline.answer("Which ReadoutApplications run on host lxplus001?")
print(result["oks_query"])
print(result["answer"])
```

#### C. Running the Test Suite

Run the unit and integration tests from the repository root:

```bash
python -m pytest oksquery_translator/tests -v
```

---

## Repository Layout

```text
oksquery_translator/  Core translation package (RAG schema retriever, few-shot, LLM translator, validator, executor, CLI)
eval_dataset/         Schema corpus and evaluation query set, plus dataset generation tools
test_schema/          ATLAS TDAQ OKS schema files (XML and derived inventories)
test_data/            ATLAS TDAQ OKS data files (concrete configuration objects)
oks_scraped/          Curated OKS schema, gold pairs, and reference material
output/               Research collection scripts and reference logs
docs/                 Project documentation and architecture guides
```

---

## Evaluation

`eval_dataset/` holds the two files the pipeline is scored against:

- `oks_schema_corpus.xml` — the retrieval corpus (454 configuration classes, 825 objects, and the OKS C++ API as 22 OKS classes).
- `oks_eval_queries.jsonl` — 144 shifter questions stratified easy/medium/hard, each with ground-truth `OksQuery`, schema elements, and expected result set.

Regenerate evaluation datasets with:

```bash
python eval_dataset/build_dataset.py
```

See [`eval_dataset/README.md`](eval_dataset/README.md) for field reference and metric definitions, and [`docs/guides/rag.md`](docs/guides/rag.md) for the retrieval architecture.
