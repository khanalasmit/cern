"""
translator.py — LLM Translation with Structured AST & Context-Bound Repair Loop
================================================================================

Translates natural language questions into validated OKSQuery strings via a
robust, structured JSON Intermediate Representation (IR) pipeline:

  NL Question → PromptBuilder (with OksContext metadata) → LLM Call
  → Extract JSON → normalize_ir → QueryIR (Pydantic V2)
  → ASTValidator (Semantic & Case Check against OksSchemaProvider)
  → OksCompiler (Deterministic AST → OKSQuery S-expression)
  → Repair Loop on any validation failure
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional, Tuple

from openai import OpenAI, APIStatusError, APIConnectionError
from pydantic import ValidationError

from .ast import (
    ASTValidator,
    NormalizerError,
    OksCompiler,
    QueryIR,
    SemanticValidationError,
    ValidationResult,
    normalize_ir,
)
from .context import OksContext, OksContextBuilder
from .prompt_builder import PromptBuilder
from .schema import OksSchemaProvider
from .schema_retrieval import SchemaRetriever

logger = logging.getLogger("oksquery_translator.translator")


class Translator:
    """
    Manages LLM Call #1 (NL → JSON IR → AST → OksQuery) with a context-bound repair loop.

    Usage::

        translator = Translator(prompt_builder, data_file="daq/segments/setup.data.xml")
        result = translator.translate("Which executables have InitTimeout > 2?", oks_context=ctx)
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
            Used for schema context retrieval.
        data_file : str
            OKS data file path.
        llm_api_key, llm_base_url, llm_model : str, optional
            LLM provider configuration.
        max_retries : int
            Maximum number of repair attempts after the first try.
        """
        self.prompt_builder = prompt_builder
        self.schema_retriever = schema_retriever
        self.data_file = data_file
        self.max_retries = max_retries
        self.compiler = OksCompiler()

        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "mimo-v2.5-pro")
        api_key = llm_api_key or os.environ.get("LLM_API_KEY", "dummy")
        base_url = llm_base_url or os.environ.get("LLM_BASE_URL", "https://api.xiaomimimo.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def translate(self, question: str,
                  oks_context: Optional[OksContext] = None,
                  retrieval_query: Optional[str] = None,
                  data_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate a natural-language question into a validated OksQuery via the AST pipeline.

        Parameters
        ----------
        question : str
            User query.
        oks_context : OksContext, optional
            Bound context object for this request.
        retrieval_query : str, optional
            Enriched token query for schema retrieval.

        Returns
        -------
        dict with keys:
            status : "success" | "error"
            target_class : str (on success)
            oks_query : str (on success)
            ir : dict (on success)
            attempts : int
            message : str (on error)
            explanation : str (optional)
        """
        # Resolve effective data file (caller may supply a run-specific path)
        effective_data_file = data_file or self.data_file

        # Ensure an OksContext exists for this translation call
        if oks_context is None:
            schema_dir = getattr(self.schema_retriever, "schema_dir", None) if self.schema_retriever else None
            builder = OksContextBuilder(data_file=effective_data_file, schema_dir=schema_dir)
            oks_context = builder.build()

        schema_dir = getattr(self.schema_retriever, "schema_dir", None) if self.schema_retriever else None
        schema_provider = OksSchemaProvider(
            oks_context=oks_context,
            data_file=effective_data_file,
            schema_dir=schema_dir,
        )
        validator = ASTValidator(schema_provider)

        # 1. Build initial prompt
        system_prompt, user_prompt = self.prompt_builder.build(
            question,
            oks_context=oks_context,
            retrieval_query=retrieval_query or question,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        last_error = None

        # 2. Generation & Repair Loop
        for attempt in range(1 + self.max_retries):
            t_start = time.perf_counter()
            logger.info(f"Translator: Calling LLM attempt {attempt + 1}/{1 + self.max_retries} (model={self.llm_model})...")
            llm_result = self._call_llm(messages)
            llm_elapsed = time.perf_counter() - t_start

            if llm_result.get("error"):
                logger.error(f"Translator: LLM call error: {llm_result['error']}")
                return {
                    "status": "error",
                    "message": llm_result["error"],
                    "attempts": attempt + 1,
                }

            raw_response = llm_result["content"]
            logger.info(f"Translator: LLM response received in {llm_elapsed:.2f}s:\n{raw_response}")
            clean_json_str = self._strip_markdown_fences(raw_response)

            try:
                # Step A: Parse raw JSON
                parsed_dict = self._extract_json_dict(clean_json_str)

                # Step B: Normalize IR
                normalized_dict = normalize_ir(parsed_dict)
                logger.info(f"Translator: AST Normalization successful: target_class={normalized_dict.get('target_class')!r}")

                # Step C: Structural Validation (Pydantic V2)
                ir = QueryIR.model_validate(normalized_dict)

                # Step D: Semantic Validation (Context-Bound)
                val_result = validator.validate(ir, oks_context)
                if not val_result.valid:
                    raise SemanticValidationError(val_result.message)
                logger.info("Translator: Semantic Validation passed successfully.")

                # Step E: Deterministic Compilation
                oks_query = self.compiler.compile(ir, oks_context)
                logger.info(
                    f"Translator: Compilation complete (attempt {attempt + 1}) → "
                    f"target_class={ir.target_class!r}, oks_query={oks_query!r}"
                )

                return {
                    "status": "success",
                    "target_class": ir.target_class,
                    "oks_query": oks_query,
                    "ir": ir.model_dump(),
                    "attempts": attempt + 1,
                    "explanation": ir.explanation or "",
                }


            except (json.JSONDecodeError, NormalizerError, ValidationError, SemanticValidationError, ValueError) as err:
                last_error = str(err)
                logger.warning(f"Translation attempt {attempt + 1} failed: {last_error}")

                if attempt < self.max_retries:
                    # Construct targeted repair feedback with schema context
                    repair_feedback = self._build_repair_message(
                        error_message=last_error,
                        attempted_output=raw_response,
                        oks_context=oks_context,
                        schema_provider=schema_provider,
                    )
                    messages.append({"role": "assistant", "content": raw_response})
                    messages.append({"role": "user", "content": repair_feedback})
                    continue

        return {
            "status": "error",
            "message": f"Failed after {1 + self.max_retries} attempts. Last error: {last_error}",
            "attempts": 1 + self.max_retries,
        }

    # ------------------------------------------------------------------
    # Repair prompt construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_repair_message(error_message: str, attempted_output: str,
                              oks_context: OksContext,
                              schema_provider: OksSchemaProvider) -> str:
        """Construct targeted repair instructions for the LLM."""
        lines = [
            "YOUR PREVIOUS QUERY FAILED VALIDATION. You must fix it.",
            f"Error diagnostic:\n  {error_message}",
            "",
            f"Schema Fingerprint: {oks_context.schema_fingerprint}",
            "Requirements for your correction:",
            "1. Output ONLY valid JSON matching the QueryIR schema.",
            "2. Do NOT use markdown code fences (no ```json blocks).",
            "3. Ensure all class, attribute, and relationship names match the exact case in the schema.",
            "4. Ensure nested expressions inside relationships compare attributes on the relationship's TARGET class.",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # String & JSON cleanup utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove markdown code fences that LLMs wrap around responses."""
        t = text.strip()
        if t.startswith("```json"):
            t = t[7:]
        elif t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return t.strip()

    @staticmethod
    def _extract_json_dict(text: str) -> dict:
        """Extract and parse the outer JSON object from text."""
        t = text.strip()
        try:
            return json.loads(t)
        except json.JSONDecodeError:
            # Attempt to find outermost { ... }
            m = re.search(r"\{.*\}", t, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            raise

    # ------------------------------------------------------------------
    # LLM API Client Interaction
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
            return {"content": response.choices[0].message.content or ""}
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
    # Legacy parser helper (preserved for unit tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract CLASS and QUERY from legacy two-line format.
        Preserved for test compatibility.
        """
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```\w*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()

        target_class = None
        query = None

        for line in text.splitlines():
            line = line.strip()
            m = re.match(r'^(?:CLASS|Class|class)\s*:\s*(.+)', line)
            if m:
                target_class = m.group(1).strip().strip('"').strip("'")
                continue

            m = re.match(r'^(?:QUERY|Query|query)\s*:\s*(.+)', line)
            if m:
                query = m.group(1).strip()
                continue

        return target_class, query
