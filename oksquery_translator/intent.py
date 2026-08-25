"""
intent.py — Intent Classification and Run Number Extraction
============================================================

Classifies user questions into one of four distinct intents:
  1. OKS_CURRENT_QUERY     — Queries about current/HEAD OKS configuration
  2. OKS_HISTORICAL_QUERY  — Queries about historical run/temporal configuration
  3. CERN_OUT_OF_SCOPE     — CERN/TDAQ questions outside OKS database querying
  4. GENERAL_OUT_OF_SCOPE  — Completely unrelated general queries

Also handles deterministic extraction of Run Numbers and Partitions from
natural-language questions and version strings.
"""

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from openai import OpenAI, APIStatusError, APIConnectionError


class Intent(str, Enum):
    OKS_CURRENT_QUERY = "OKS_CURRENT_QUERY"
    OKS_HISTORICAL_QUERY = "OKS_HISTORICAL_QUERY"
    CERN_OUT_OF_SCOPE = "CERN_OUT_OF_SCOPE"
    GENERAL_OUT_OF_SCOPE = "GENERAL_OUT_OF_SCOPE"


@dataclass
class IntentResult:
    """Container for intent classification and run extraction results."""
    intent: Intent
    run_number: Optional[int] = None
    partition: Optional[str] = "all_hosts"
    version_tag: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "intent": self.intent.value if isinstance(self.intent, Intent) else str(self.intent),
            "run_number": self.run_number,
            "partition": self.partition,
            "version_tag": self.version_tag,
            "message": self.message,
        }


# Standard out-of-scope and historical guidance messages
MSG_GENERAL_OUT_OF_SCOPE = (
    "I am an AI assistant specialized in CERN ATLAS TDAQ OKS Configuration Database queries. "
    "I cannot help with general questions. Please ask an OKS database question."
)

MSG_CERN_OUT_OF_SCOPE = (
    "I can only query OKS configuration databases (objects, classes, parameters, and historical run settings). "
    "I cannot execute DAQ control commands or edit system code. Please rephrase your request as an OKS database query."
)

MSG_HISTORICAL_MISSING_RUN = (
    "You asked for historical run configuration data, but did not specify a run number. "
    "Please provide a valid Run Number (e.g. Run 380689 or tag r380689@all_hosts)."
)


# ======================================================================
# Run Resolver
# ======================================================================

class RunResolver:
    """
    Validates ATLAS run numbers and resolves them using the CERN Run Number
    Database (rn_ls) and Git tags.
    """

    def __init__(self, repo_root: str = None, default_partition: str = "all_hosts",
                 known_valid_runs: Optional[set] = None):
        self.repo_root = repo_root or os.getcwd()
        self.default_partition = default_partition
        self.known_valid_runs = known_valid_runs
        self._cached_runs: dict = {}

    def validate_run_number(self, run_number: int, partition: str = None) -> bool:
        """
        Validate whether a run number is a valid ATLAS experiment run.
        Checks:
          1. Explicit known_valid_runs set if provided.
          2. CERN Run Number Database via:
             rn_ls -c "oracle://atonr_adg/rn_r" -w "ATLAS_RUN_NUMBER" -n <run> -m <run>
          3. Git tags in repository via 'git tag -l'.
        """
        if run_number is None or not isinstance(run_number, int) or run_number <= 0:
            return False

        if self.known_valid_runs is not None:
            return run_number in self.known_valid_runs

        partition = partition or self.default_partition

        # 1. Authoritative check: CERN Run Number Database (rn_ls)
        import shutil
        import subprocess

        rn_ls_path = shutil.which("rn_ls")
        if rn_ls_path:
            rndb_info = self.query_rndb(run_number)
            if rndb_info is not None:
                self._cached_runs[run_number] = rndb_info
                return True
            # rn_ls was executed and confirmed run does NOT exist
            return False

        # 2. Check local Git tags if git is available
        try:
            cmd = ["git", "tag", "-l", f"r{run_number}*"]
            res = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                return True
        except Exception:
            pass

        return False

    def query_rndb(self, run_number: int) -> Optional[dict]:
        """
        Query the CERN Run Number Database using rn_ls.
        Command syntax:
          rn_ls -c "oracle://atonr_adg/rn_r" -w "ATLAS_RUN_NUMBER" -n <run> -m <run>
        """
        import shutil
        import subprocess

        rn_ls_path = shutil.which("rn_ls")
        if not rn_ls_path:
            return None

        db_conn = os.environ.get("TDAQ_RNDB_CONNECT_STRING", "oracle://atonr_adg/rn_r")
        schema = os.environ.get("TDAQ_RNDB_SCHEMA", "ATLAS_RUN_NUMBER")
        cmd = [
            rn_ls_path,
            "-c", db_conn,
            "-w", schema,
            "-n", str(run_number),
            "-m", str(run_number)
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode != 0:
                return None

            # Parse table output
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.startswith("|") and not line.startswith("| Name") and not line.startswith("|===") and not line.startswith("|---"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 9:
                        name, num, start_at, duration, release, user, host, part, version = parts[:9]
                        if num == str(run_number):
                            return {
                                "run_number": int(num),
                                "name": name,
                                "partition": part,
                                "version": version,
                                "release": release,
                                "host": host,
                                "config_name": parts[9] if len(parts) > 9 else "",
                            }
        except Exception:
            pass

        return None

    @staticmethod
    def is_supported_version(version: Optional[str]) -> bool:
        """Return whether *version* can be applied by the OKS backends."""
        return bool(version and version.startswith(("hash:", "date:", "tag:")))

    def get_run_info(self, run_number: int) -> Optional[dict]:
        """Return Run Number DB metadata cached during validation, if available."""
        return self._cached_runs.get(run_number)

    def resolve_version(self, run_number: int, partition: str = None) -> Optional[str]:
        """
        Resolve a run number and partition into a temporal version specifier.
        If rn_ls provided an exact supported version (e.g. hash:ce4ceda7...),
        return it.  A legacy numeric archive revision (for example ``46.97``)
        is *not* a Git/OKS version and must never be passed through: doing so
        would leave the OKS environment unchanged and accidentally query HEAD.

        When no Run Number DB record was used (for example an explicitly
        supplied known run), retain the tag fallback.
        """
        if run_number in self._cached_runs:
            run_info = self._cached_runs[run_number]
            cached_ver = run_info.get("version")
            if self.is_supported_version(cached_ver):
                return cached_ver
            if cached_ver:
                return None
            part = run_info.get("partition") or partition or self.default_partition
            if part:
                return f"tag:r{run_number}@{part}"

        part = partition or self.default_partition
        return f"tag:r{run_number}@{part}"



# ======================================================================
# Run Number & Partition Extraction
# ======================================================================

def extract_run_and_partition(text: str, default_partition: str = "all_hosts") -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Extract run number and partition name from natural language text or tags.

    Supports patterns:
      - r380689@all_hosts / r380689@ATLAS
      - r380689 / r380689? / r5000
      - run 380689 / Run 380689 / RUN 380689 / run 5000
      - run number 380689 / run_number=380689 / run_number: 380689 / run #380689
      - run is 380689 / run = 380689 / run: 380689 / run-380689
      - run 380689 in partition ATLAS / run 380689 partition all_hosts

    Does NOT falsely match:
      - "Which host has 32 GB RAM?"
      - "Which applications run on host lxplus001?"

    Returns
    -------
    (run_number, partition, version_tag) : Tuple[Optional[int], Optional[str], Optional[str]]
        version_tag will be formatted as "tag:r<run>@<partition>" if run_number is found.
    """
    if not text:
        return None, default_partition, None

    # Check for partition explicitly mentioned in the text (e.g. 'partition ATLAS', 'in partition all_hosts', '@ATLAS')
    partition = default_partition
    m_part_explicit = re.search(r'\b(?:in\s+partition|partition\s*(?:is|=|:)?)\s*([A-Za-z0-9_\-]+)\b', text, re.IGNORECASE)
    if m_part_explicit:
        partition = m_part_explicit.group(1)

    # Pattern 1: explicit tag format with partition: r<run>@<partition> or run:<run>@<partition> or tag:r<run>@<partition>
    m_tag = re.search(r'(?:^|[^\w])(?:tag:)?r(\d{1,8})@([A-Za-z0-9_\-]+)', text, re.IGNORECASE)
    if m_tag:
        run_num = int(m_tag.group(1))
        partition = m_tag.group(2)
        version_tag = f"tag:r{run_num}@{partition}"
        return run_num, partition, version_tag

    # Pattern 2: standalone tag format: r<run> (e.g. r380689, r5000)
    # Must be preceded by non-word or start, and followed by non-digit/word boundary
    m_rtag = re.search(r'(?:^|[^\w])r(\d{1,8})(?=[^\w]|$)', text, re.IGNORECASE)
    if m_rtag:
        run_num = int(m_rtag.group(1))
        version_tag = f"tag:r{run_num}@{partition}"
        return run_num, partition, version_tag

    # Pattern 3: explicit 'run [number|#|no] [is|=|:|#|-] <num>' or 'run <num>' or 'run#<num>' or 'run<num>'
    m_run = re.search(
        r'\b(?:run\s*number|run_number|run\s*no\.?|run\s*#|run)\s*(?:=|:|\s+is\s+|\s*#\s*|\s*-\s*|\s*|\s+)\s*(\d{1,8})\b',
        text,
        re.IGNORECASE
    )
    if m_run:
        start, end = m_run.span(1)
        after = text[end:]
        m_part = re.match(r'^@([A-Za-z0-9_\-]+)', after)
        if m_part:
            partition = m_part.group(1)

        run_num = int(m_run.group(1))
        version_tag = f"tag:r{run_num}@{partition}"
        return run_num, partition, version_tag

    return None, default_partition, None


# ======================================================================
# Intent Classification Prompt
# ======================================================================

INTENT_SYSTEM_PROMPT = """\
You are an intent classifier for an assistant dedicated to querying the CERN ATLAS TDAQ OKS Configuration Database.

Your job is to classify the user's input into EXACTLY ONE of four categories:

1. OKS_CURRENT_QUERY
   - The user is asking about the current / default OKS configuration database.
   - Examples:
     * "Which hosts run ROSDescriptor?"
     * "List all computers."
     * "Which applications are configured?"
     * "Show all segments."
     * "Which host has 32 GB RAM?"
     * "Find executables with InitTimeout > 5."

2. OKS_HISTORICAL_QUERY
   - The user is asking about an OKS configuration from a past experiment run or historical state.
   - Note: "run" might refer to an ATLAS experiment run number (e.g. run 380689, r380689) or temporal concepts like "previous run", "yesterday's run", "past configuration".
   - Examples:
     * "What was InitTimeout in run 380689?"
     * "What host did ROS run on in run 380689?"
     * "What configuration was used in the previous run?"
     * "Show segment configuration for r380689@all_hosts"
     * "What was the timeout in run 454833?"

3. CERN_OUT_OF_SCOPE
   - CERN or ATLAS TDAQ related questions that are NOT about querying the OKS configuration database.
   - Examples:
     * "How do I run cm_setup?"
     * "How do I source TDAQ?"
     * "Restart the ATLAS DAQ partition."
     * "Write a C++ program for ROS."
     * "Modify this TDAQ source code."
     * "How does the LHC beam control work?"

4. GENERAL_OUT_OF_SCOPE
   - General knowledge, coding outside TDAQ OKS, conversational chatter, or completely unrelated questions.
   - Examples:
     * "What is the recipe for chocolate cake?"
     * "Who won the World Cup?"
     * "Write me a poem."
     * "What is the capital of France?"

CRITICAL RULES:
- Notice that in "Which applications run on host lxplus001?" or "Which host has 32 GB RAM?", the word "run" is a verb meaning execute, NOT an experiment run number. This is OKS_CURRENT_QUERY.
- If the question asks about past runs without giving a number (e.g. "previous run"), classify as OKS_HISTORICAL_QUERY with run_number=null.
- Output MUST be valid JSON with keys: "intent", "run_number" (integer or null), "partition" (string or null).
"""


class IntentClassifier:
    """
    Classifies natural-language input into one of 4 intents and extracts run/partition info.

    Usage::

        classifier = IntentClassifier()
        result = classifier.classify("What was InitTimeout in run 380689?")
        print(result.intent)       # Intent.OKS_HISTORICAL_QUERY
        print(result.run_number)   # 380689
        print(result.partition)    # "all_hosts"
        print(result.version_tag)  # "tag:r380689@all_hosts"
    """

    def __init__(self,
                 llm_api_key: str = None,
                 llm_base_url: str = None,
                 llm_model: str = None,
                 default_partition: str = "all_hosts"):
        """
        Parameters
        ----------
        llm_api_key, llm_base_url, llm_model : str, optional
            LLM provider configuration. Reuses standard environment variables.
        default_partition : str
            Default partition name when none is specified.
        """
        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "mimo-v2.5-pro")
        api_key = llm_api_key or os.environ.get("LLM_API_KEY", "dummy")
        base_url = llm_base_url or os.environ.get("LLM_BASE_URL", "https://api.xiaomimimo.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.default_partition = default_partition

    def classify(self, question: str) -> IntentResult:
        """
        Classify the intent of a question and extract run metadata.

        Parameters
        ----------
        question : str
            User natural language question.

        Returns
        -------
        IntentResult
        """
        question_clean = question.strip() if question else ""
        if not question_clean:
            return IntentResult(
                intent=Intent.GENERAL_OUT_OF_SCOPE,
                message=MSG_GENERAL_OUT_OF_SCOPE,
            )

        # 1. Deterministic run number / partition extraction
        det_run, det_part, det_tag = extract_run_and_partition(
            question_clean, default_partition=self.default_partition
        )

        # 2. Call LLM for intent classification
        llm_intent, llm_run, llm_part = self._call_llm_classifier(question_clean)

        # 3. Consolidate results
        final_intent = llm_intent
        final_run = det_run if det_run is not None else llm_run
        final_part = det_part or llm_part or self.default_partition

        # If deterministic run number was found, it strongly confirms historical intent if query looks like OKS
        if final_run is not None and final_intent not in (Intent.GENERAL_OUT_OF_SCOPE, Intent.CERN_OUT_OF_SCOPE):
            final_intent = Intent.OKS_HISTORICAL_QUERY

        version_tag = None
        if final_run is not None:
            version_tag = f"tag:r{final_run}@{final_part}"

        # 4. Attach appropriate messaging
        message = None
        if final_intent == Intent.GENERAL_OUT_OF_SCOPE:
            message = MSG_GENERAL_OUT_OF_SCOPE
        elif final_intent == Intent.CERN_OUT_OF_SCOPE:
            message = MSG_CERN_OUT_OF_SCOPE
        elif final_intent == Intent.OKS_HISTORICAL_QUERY and final_run is None:
            message = MSG_HISTORICAL_MISSING_RUN

        return IntentResult(
            intent=final_intent,
            run_number=final_run,
            partition=final_part,
            version_tag=version_tag,
            message=message,
        )

    def _call_llm_classifier(self, question: str) -> Tuple[Intent, Optional[int], Optional[str]]:
        """Call LLM to get structured classification."""
        user_prompt = f"Question: {question}\n\nProvide JSON response:"

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
            )
            raw_content = response.choices[0].message.content.strip()
            return self._parse_llm_json(raw_content)
        except Exception:
            # Fallback heuristic when LLM fails or is unavailable
            return self._heuristic_fallback(question)

    def _parse_llm_json(self, raw_content: str) -> Tuple[Intent, Optional[int], Optional[str]]:
        """Parse JSON response from LLM."""
        # Strip markdown fences if present
        text = raw_content.strip()
        if text.startswith("```"):
            text = re.sub(r'^```\w*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()

        try:
            data = json.loads(text)
            intent_str = str(data.get("intent", "")).upper()
            try:
                intent = Intent(intent_str)
            except ValueError:
                intent = Intent.OKS_CURRENT_QUERY

            run_num = data.get("run_number")
            if run_num is not None:
                try:
                    run_num = int(run_num)
                except (ValueError, TypeError):
                    run_num = None

            partition = data.get("partition")
            if partition and isinstance(partition, str):
                partition = partition.strip()
            else:
                partition = None

            return intent, run_num, partition
        except json.JSONDecodeError:
            # Fallback extraction from raw string
            for member in Intent:
                if member.value in text:
                    return member, None, None
            return Intent.OKS_CURRENT_QUERY, None, None

    def _heuristic_fallback(self, question: str) -> Tuple[Intent, Optional[int], Optional[str]]:
        """Fast rule-based fallback if LLM is offline or unreachable."""
        q_lower = question.lower()

        # Check general out-of-scope keywords
        general_keywords = [
            "cake", "recipe", "world cup", "poem", "capital of", "weather",
            "cook", "football", "movie", "song", "joke"
        ]
        if any(w in q_lower for w in general_keywords):
            return Intent.GENERAL_OUT_OF_SCOPE, None, None

        # Check CERN out-of-scope keywords
        cern_oos_keywords = [
            "cm_setup", "source tdaq", "restart", "reboot", "c++", "compile",
            "git clone", "git push", "beam control", "lhc schedule"
        ]
        if any(w in q_lower for w in cern_oos_keywords):
            return Intent.CERN_OUT_OF_SCOPE, None, None

        # Check historical indicators
        det_run, det_part, _ = extract_run_and_partition(question, self.default_partition)
        if det_run is not None:
            return Intent.OKS_HISTORICAL_QUERY, det_run, det_part

        historical_phrases = ["previous run", "last run", "yesterday's run", "past run", "earlier run", "in run "]
        if any(p in q_lower for p in historical_phrases):
            return Intent.OKS_HISTORICAL_QUERY, None, det_part

        # Default to current OKS query
        return Intent.OKS_CURRENT_QUERY, None, None
