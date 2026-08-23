# oksquery_translator

Text-to-OksQuery Translation Module for the ATLAS DAQ configuration system.

Designed to run on CERN lxplus with a sourced TDAQ release.

## Quick Start

```bash
# On lxplus, source the TDAQ release first
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env with your LLM API key

# Interactive CLI
python -m oksquery_translator.cli

# Programmatic usage
from oksquery_translator import answer
print(answer("Which test executables take longer than 2 seconds to initialise?"))
```
