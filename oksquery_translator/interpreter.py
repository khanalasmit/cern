"""
interpreter.py — LLM Call #2: Result Interpretation
=====================================================

Takes the filtered execution results and produces a clean,
human-readable natural-language answer for the user.
"""

import os
from typing import Dict, List, Optional

from openai import OpenAI, APIStatusError, APIConnectionError


INTERPRETER_SYSTEM_PROMPT = """\
You are an assistant that summarizes OKS query results for ATLAS DAQ operators.

Given a user's original question, the OksQuery that was executed, and the
matching configuration objects, provide a clear, concise answer.

Rules:
- State how many objects matched.
- List the matching object IDs and their most relevant attributes.
- If no objects matched, say so and suggest possible reasons.
- If a temporal version was queried, state which version was used.
- Use plain language. Do NOT output raw XML, code, or markdown formatting.
- Keep the answer compact — a few sentences or a short bullet list.
"""


class Interpreter:
    """
    LLM Call #2: transforms filtered query results into a clean answer.

    Usage::

        interp = Interpreter()
        answer = interp.interpret(
            question="Which executables have InitTimeout > 2?",
            target_class="Executable",
            oks_query='(all ("InitTimeout" "2" >))',
            objects=[{"id": "test_dummy", "attributes": {"InitTimeout": "3"}}],
            count=1,
            version="current"
        )
        print(answer)
    """

    def __init__(self, llm_api_key: str = None,
                 llm_base_url: str = None,
                 llm_model: str = None):
        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "mimo-v2.5-pro")
        api_key = llm_api_key or os.environ.get("LLM_API_KEY", "dummy")
        base_url = llm_base_url or os.environ.get("LLM_BASE_URL",
                                                    "https://api.xiaomimimo.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def interpret(self, question: str, target_class: str,
                  oks_query: str, objects: List[Dict],
                  count: int, version: str = "current") -> str:
        """
        Generate a natural-language answer from query results.

        Parameters
        ----------
        question : str
            The user's original question.
        target_class : str
            The OKS class that was queried.
        oks_query : str
            The OksQuery string that was executed.
        objects : list of dict
            Matching objects, each with "id" and "attributes" keys.
        count : int
            Total number of matching objects (may exceed len(objects) if
            truncated).
        version : str
            Which version/snapshot was queried.

        Returns
        -------
        str : The natural-language answer.
        """
        user_prompt = self._build_user_prompt(
            question, target_class, oks_query, objects, count, version
        )

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": INTERPRETER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except (APIStatusError, APIConnectionError, Exception) as e:
            # If the LLM call fails, produce a basic programmatic answer
            return self._fallback_answer(
                question, target_class, oks_query, objects, count, version
            )

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    @staticmethod
    def _build_user_prompt(question: str, target_class: str,
                           oks_query: str, objects: List[Dict],
                           count: int, version: str) -> str:
        """Build the user prompt for the interpretation LLM call."""
        lines = [
            f"Original question: {question}",
            f"Query executed: {oks_query}",
            f"Target class: {target_class}",
            f"Version queried: {version}",
            "",
        ]

        if not objects:
            lines.append("Results: No objects matched the query.")
        else:
            truncated = count > len(objects)
            lines.append(
                f"Results ({count} object{'s' if count != 1 else ''} matched"
                f"{', showing first ' + str(len(objects)) if truncated else ''}):"
            )
            for obj in objects:
                obj_id = obj.get("id", "?")
                attrs = obj.get("attributes", {})
                if attrs:
                    attr_str = ", ".join(
                        f"{k}={v}" for k, v in list(attrs.items())[:8]
                    )
                    lines.append(f"  - {obj_id}: {attr_str}")
                else:
                    lines.append(f"  - {obj_id}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Fallback (no LLM)
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_answer(question: str, target_class: str,
                         oks_query: str, objects: List[Dict],
                         count: int, version: str) -> str:
        """Produce a basic answer without the LLM."""
        if not objects:
            return (
                f"No {target_class} objects matched the query "
                f"{oks_query} (version: {version})."
            )

        lines = [
            f"Found {count} {target_class} object{'s' if count != 1 else ''} "
            f"matching the query (version: {version}):"
        ]
        for obj in objects[:20]:
            obj_id = obj.get("id", "?")
            attrs = obj.get("attributes", {})
            if attrs:
                attr_str = ", ".join(
                    f"{k}={v}" for k, v in list(attrs.items())[:5]
                )
                lines.append(f"  • {obj_id} ({attr_str})")
            else:
                lines.append(f"  • {obj_id}")

        if count > 20:
            lines.append(f"  ... and {count - 20} more.")

        return "\n".join(lines)
