# oksquery_translator

Text-to-OksQuery Translation Module for the ATLAS DAQ configuration system.

Translates natural-language shifter and expert queries into valid CERN OKS query expressions (S-expressions), validates them against the live or local TDAQ schema, executes them via `oks_dump` or the Python `config` module, and produces interpreted English explanations.

---

## Step-by-Step Run Instructions

Follow the steps below to set up and run the module from scratch:

### 1. Sourcing TDAQ Release (CERN lxplus / CVMFS)

If running on CERN `lxplus` or a host with CVMFS access, source the ATLAS TDAQ release setup script to populate the OKS environment variables, `oks_dump` binary, and Python bindings:

```bash
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
```

> **Note:** If running in an offline development environment without CVMFS, the translator automatically falls back to local XML schemas (in `test_schema/` and `oks_scraped/`) and local validation.

---

### 2. Git Clone

Clone the repository and navigate into the project root directory:

```bash
git clone https://github.com/khanalasmit/cern.git
cd cern
```

---

### 3. Create Virtual Environment (`venv`)

Create an isolated Python 3.10+ virtual environment:

```bash
python3 -m venv .venv
```

*(On Windows, run: `python -m venv .venv`)*

---

### 4. Activate Virtual Environment

Activate the newly created virtual environment:

**Linux / CERN lxplus (Bash/Zsh):**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\.venv\Scripts\activate.bat
```

---

### 5. Install Dependencies

Install the required Python packages:

```bash
pip install -r oksquery_translator/requirements.txt
```

---

### 6. Configure Environment (`.env`)

Copy the example environment configuration file to `.env`:

```bash
cp oksquery_translator/.env.example oksquery_translator/.env
# (or cp .env.example .env from the repo root)
```

Edit `.env` to supply your LLM credentials and configuration:

```env
LLM_API_KEY=your_actual_api_key_here
LLM_BASE_URL=https://api.xiaomimimo.com/v1
LLM_MODEL=mimo-v2.5-pro
```

| Variable | Description |
|---|---|
| `LLM_API_KEY` | Your API key for an OpenAI-compatible LLM provider |
| `LLM_BASE_URL` | OpenAI-compatible Chat Completions API base URL |
| `LLM_MODEL` | Target model identifier (e.g. `mimo-v2.5-pro`, `gpt-4o`) |

---

### 7. Running the Application

#### A. Interactive CLI

Launch the interactive translation and query shell:

```bash
python -m oksquery_translator.cli
```

Inside the CLI prompt, you can use:
- **Direct Query**: Type any natural-language question (e.g. `Which applications have InitTimeout <= 30?`) to translate, validate, execute against OKS data, and interpret results.
- `translate <question>` — Translate and validate the query without executing it against live OKS data.
- `probe` — Re-run the environment probe (checks `oks_dump`, `config` module, active schema directories, and class counts).
- `version <v>` — Set temporal version for point-in-time configuration queries (e.g. `version 2024-03-01T12:00:00`).
- `exit` or `quit` — Exit the CLI.

#### B. Programmatic Usage (Python API)

You can import and use the pipeline directly in Python scripts:

```python
from oksquery_translator import answer, OksPipeline

# Quick one-liner answer
response = answer("Which test executables take longer than 2 seconds to initialise?")
print(response)

# Or instantiate the full pipeline object
pipeline = OksPipeline()
result = pipeline.answer("Find all ReadoutApplications running on segment TTCRX")
print(f"Target Class: {result['target_class']}")
print(f"OKS Query:    {result['oks_query']}")
print(f"Answer:       {result['answer']}")
```

#### C. Running Tests

Run the test suite with `pytest`:

```bash
python -m pytest oksquery_translator/tests -v
```
