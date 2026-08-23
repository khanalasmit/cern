"""
translator.py — LLM Call #1 + Validate/Repair Loop
====================================================

Orchestrates:
  1. Prompt construction (via prompt_builder)
  2. LLM call to generate CLASS + OksQuery string
  3. Response parsing
  4. Two-layer validation (via validator)
  5. Repair loop: feed error back to LLM and retry on failure
"""

import os
import re
from typing import Dict, Optional, Tuple

from openai import OpenAI, APIStatusError, APIConnectionError

from .prompt_builder import PromptBuilder
from .schema_retrieval import SchemaRetriever
from .validator import validate_query, syntax_precheck, align_query_to_schema


class Translator:
    """
    Manages LLM Call #1 (NL → OksQuery) with a validate/repair retry loop.

    Usage::

        translator = Translator(prompt_builder, data_file="daq/segments/setup.data.xml")
        result = translator.translate("Which executables have InitTimeout > 2?")
        if result["status"] == "success":
            print(result["oks_query"])
    """

    def __init__(self, prompt_builder: PromptBuilder,
                 schema_retriever: SchemaRetriever = None,
                 data_file: str = "daq/segments/setup.data.xml",
                 llm_api_key: str = None,
                 llm_base_url: str = None,
                 llm_model: str = None,
                 max_retries: int = 3):
        """
        Parameters
        ----------
        prompt_builder : PromptBuilder
            Builds system + user prompts.
        schema_retriever : SchemaRetriever, optional
            Used to generate schema hints in repair prompts.
        data_file : str
            OKS data file path (for oks_dump validation).
        llm_api_key, llm_base_url, llm_model : str, optional
            LLM provider configuration.  Falls back to environment variables.
        max_retries : int
            Maximum number of repair attempts after the first try.
        """
        self.prompt_builder = prompt_builder
        self.schema_retriever = schema_retriever
        self.data_file = data_file
        self.max_retries = max_retries

        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "mimo-v2.5-pro")
        api_key = llm_api_key or os.environ.get("LLM_API_KEY", "dummy")
        base_url = llm_base_url or os.environ.get("LLM_BASE_URL",
                                                    "https://api.xiaomimimo.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def translate(self, question: str) -> Dict:
        """
        Translate a natural-language question into a validated OksQuery.

        Returns
        -------
        dict with keys:
            status : "success" | "error"
            target_class : str (on success)
            oks_query : str (on success)
            attempts : int
            message : str (on error)
        """
        # Build the initial prompt
        system_prompt, user_prompt = self.prompt_builder.build(question)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        last_error = None
        for attempt in range(1 + self.max_retries):
            # --- LLM Call ---
            llm_result = self._call_llm(messages)
            if llm_result.get("error"):
                return {
                    "status": "error",
                    "message": llm_result["error"],
                    "attempts": attempt + 1,
                }

            raw_response = llm_result["content"]

            # --- Parse response ---
            target_class, oks_query = self._parse_response(raw_response)

            if not target_class or not oks_query:
                last_error = (
                    f"Could not parse CLASS/QUERY from LLM response. "
                    f"Raw output: {raw_response[:300]}"
                )
                if attempt < self.max_retries:
                    repair_msg = (
                        f"Your response could not be parsed. "
                        f"Raw output: {raw_response[:300]}\n\n"
                        f"Please output EXACTLY two lines:\n"
                        f"CLASS: <ClassName>\n"
                        f"QUERY: <OksQuery string>\n"
                        f"Nothing else."
                    )
                    messages.append({"role": "assistant", "content": raw_response})
                    messages.append({"role": "user", "content": repair_msg})
                    continue
                break

            # --- Auto-align schema casing (e.g. Subdetector -> SubDetector) ---
            if self.schema_retriever:
                target_class, oks_query = align_query_to_schema(
                    target_class, oks_query, self.schema_retriever
                )

            # --- Validate ---
            val_result = validate_query(target_class, oks_query, self.data_file)

            if val_result.valid:
                return {
                    "status": "success",
                    "target_class": target_class,
                    "oks_query": oks_query,
                    "attempts": attempt + 1,
                }

            # --- Validation failed — prepare repair ---
            last_error = val_result.message

            if attempt < self.max_retries:
                # Always build a schema hint for the repair prompt.
                # The schema shows the LLM the EXACT attribute and
                # relationship names so it can correct itself.
                schema_hint = ""
                if self.schema_retriever:
                    info = self.schema_retriever.get_class_info(target_class)
                    if info:
                        schema_hint = SchemaRetriever._format_class_info(info)

                    # If the error mentions a specific class (e.g. inside
                    # a relationship), fetch that class's schema too.
                    import re
                    err_class = re.search(
                        r'in class "([^"]+)"', val_result.message
                    )
                    if err_class:
                        mentioned = err_class.group(1)
                        if mentioned != target_class:
                            extra = self.schema_retriever.get_class_info(mentioned)
                            if extra:
                                schema_hint += "\n" + SchemaRetriever._format_class_info(extra)

                repair_msg = self.prompt_builder.build_repair_prompt(
                    question, target_class, oks_query,
                    val_result.message, schema_hint
                )
                messages.append({"role": "assistant",
                                 "content": f"CLASS: {target_class}\nQUERY: {oks_query}"})
                messages.append({"role": "user", "content": repair_msg})
            # else: fall through to error return

        return {
            "status": "error",
            "message": (f"Failed after {1 + self.max_retries} attempts. "
                        f"Last error: {last_error}"),
            "attempts": 1 + self.max_retries,
        }

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _call_llm(self, messages: list) -> dict:
        """
        Call the LLM and return {"content": str} or {"error": str}.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.0,
            )
            return {"content": response.choices[0].message.content}
        except APIStatusError as e:
            code = e.status_code
            if code == 404:
                return {"error": (
                    f"LLM API returned 404. Check LLM_BASE_URL "
                    f"('{self.client.base_url}') and LLM_MODEL "
                    f"('{self.llm_model}')."
                )}
            elif code in (401, 403):
                return {"error": f"LLM API auth failed (HTTP {code}). Check LLM_API_KEY."}
            elif code == 429:
                return {"error": "LLM API rate limited. Please wait and retry."}
            else:
                return {"error": f"LLM API error (HTTP {code}): {e.message}"}
        except APIConnectionError:
            return {"error": (
                f"Cannot connect to LLM API at '{self.client.base_url}'. "
                f"Check network and LLM_BASE_URL."
            )}
        except Exception as e:
            return {"error": f"Unexpected LLM error: {e}"}

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract CLASS and QUERY from the LLM's response.

        Expected format:
            CLASS: <ClassName>
            QUERY: <OksQuery string>

        Also handles common LLM quirks:
          - Extra whitespace / blank lines
          - Markdown code fences wrapping the output
          - Slight variations in labelling
        """
        # Strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```\w*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()

        target_class = None
        query = None

        for line in text.splitlines():
            line = line.strip()
            # Match CLASS: or Class: or class:
            m = re.match(r'^(?:CLASS|Class|class)\s*:\s*(.+)', line)
            if m:
                target_class = m.group(1).strip().strip('"').strip("'")
                continue

            # Match QUERY: or Query: or query:
            m = re.match(r'^(?:QUERY|Query|query)\s*:\s*(.+)', line)
            if m:
                query = m.group(1).strip()
                continue

        return target_class, query
