import json
import os
from openai import OpenAI, APIStatusError, APIConnectionError
from pydantic import ValidationError
from rag.ingest import HybridIndexer
from rag.retrieve import Retriever
from .few_shot import FewShotManager
from .ir_validator import validate_ir
from .serializer import serialize_ir_to_oks

# The IR schema description embedded in the system prompt so the LLM knows
# exactly what JSON structure to produce.
IR_SCHEMA_DESCRIPTION = """\
The JSON IR (Intermediate Representation) you must produce follows this schema:

{
  "scope": "this" | "all",          // "this" = exact class only, "all" = class + subclasses
  "expression": <Expression>,
  "explanation": "A brief explanation of each query component"
}

Where <Expression> is ONE of:

1. Attribute comparison:
   {"type": "attribute_compare", "attribute": "<attr-name>", "operator": "<op>", "value": "<val>"}
   Operators: "=", "!=", "~=", "<", "<=", ">", ">="
   NOTE: value is ALWAYS a quoted string, even for numbers.

2. Object ID comparison:
   {"type": "object_id", "operator": "=", "object_id": "<id>"}

3. Relationship expression:
   {"type": "relationship", "name": "<rel-name>", "quantifier": "some" | "all", "expression": <Expression>}

4. Logical AND:
   {"type": "and", "operands": [<Expression>, <Expression>, ...]}  (at least 2 operands)

5. Logical OR:
   {"type": "or", "operands": [<Expression>, <Expression>, ...]}  (at least 2 operands)

6. Logical NOT:
   {"type": "not", "operand": <Expression>}
"""


class OksTranslator:
    def __init__(self,
                 schema_xml_path: str,
                 gold_pairs_path: str,
                 llm_api_key: str = None,
                 llm_base_url: str = None,
                 llm_model: str = None):

        # Initialize RAG
        self.indexer = HybridIndexer()
        self.indexer.ingest_xml(schema_xml_path)
        self.retriever = Retriever(self.indexer)

        # Initialize Few-Shot (share the encoder from the RAG indexer)
        self.few_shot_manager = FewShotManager(
            gold_pairs_path,
            encoder=self.indexer.encoder
        )

        # Initialize LLM Client
        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "mimo-v2.5-pro")
        api_key = llm_api_key or os.environ.get("LLM_API_KEY", "dummy")
        base_url = llm_base_url or os.environ.get("LLM_BASE_URL", "https://api.xiaomimimo.com/anthropic")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def translate(self, natural_language_query: str, max_retries: int = 1) -> dict:
        """Translates NL to OKS Query String via IR validation with a repair loop."""

        # 1. Retrieve Schema Context
        schema_context = self.retriever.get_schema_context(natural_language_query)

        # 2. Retrieve Few-Shot Examples
        few_shot_context = self.few_shot_manager.get_examples(natural_language_query)

        # 3. Build System Prompt
        system_prompt = f"""You are an expert in OKS (Object Kernel Support) query translation.
Your task is to translate natural language into a strictly formatted JSON Intermediate Representation (IR).

{IR_SCHEMA_DESCRIPTION}

{schema_context}

{few_shot_context}

IMPORTANT RULES:
- Return ONLY valid JSON matching the QueryIR schema above.
- Do NOT include markdown formatting (no ```json blocks), code fences, or explanatory text outside the JSON.
- All attribute/relationship names, object IDs, and values MUST come from the supplied schema context.
- Do NOT invent any class, attribute, relationship, or object ID.
- Include an "explanation" field with a brief breakdown of each query component.
- Use scope "all" unless the user explicitly says "this class only".
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language_query}
        ]

        last_error = None
        for attempt in range(1 + max_retries):
            # 4. LLM Generation
            try:
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.0
                )
            except APIStatusError as e:
                status = e.status_code
                if status == 404:
                    return {
                        "status": "error",
                        "message": (
                            f"LLM API returned 404 Not Found. "
                            f"Check your LLM_BASE_URL ('{self.client.base_url}') "
                            f"and LLM_MODEL ('{self.llm_model}') in .env. "
                            f"The endpoint or model may be incorrect or no longer available."
                        )
                    }
                elif status == 401 or status == 403:
                    return {
                        "status": "error",
                        "message": (
                            f"LLM API authentication failed (HTTP {status}). "
                            f"Check your LLM_API_KEY in .env."
                        )
                    }
                elif status == 429:
                    return {
                        "status": "error",
                        "message": "LLM API rate limit exceeded. Please wait and try again."
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"LLM API error (HTTP {status}): {e.message}"
                    }
            except APIConnectionError:
                return {
                    "status": "error",
                    "message": (
                        f"Could not connect to the LLM API at '{self.client.base_url}'. "
                        f"Check your network connection and LLM_BASE_URL in .env."
                    )
                }


            ir_json_str = response.choices[0].message.content

            # Strip potential markdown formatting
            ir_json_str = self._strip_markdown_fences(ir_json_str)

            try:
                ir_dict = json.loads(ir_json_str)

                # 5. Validation
                validated_ir = validate_ir(ir_dict)

                # 6. Serialization
                oks_query_str = serialize_ir_to_oks(validated_ir)

                return {
                    "status": "success",
                    "ir": ir_dict,
                    "oks_query": oks_query_str,
                    "explanation": ir_dict.get("explanation", "")
                }

            except json.JSONDecodeError as e:
                last_error = f"JSON parsing failed: {e}"
                error_feedback = (
                    f"Your previous response was not valid JSON. Error: {e}\n"
                    f"Raw output (first 500 chars): {ir_json_str[:500]}\n"
                    f"Please respond with ONLY valid JSON matching the IR schema."
                )
            except ValidationError as e:
                last_error = f"IR Validation failed: {e}"
                error_feedback = (
                    f"Your JSON was parseable but failed IR validation: {e}\n"
                    f"Please fix the errors and respond with ONLY valid JSON."
                )
            except Exception as e:
                last_error = str(e)
                error_feedback = f"Unexpected error: {e}\nPlease try again with valid JSON."

            # Repair: append the error as an assistant+user exchange for the retry
            if attempt < max_retries:
                messages.append({"role": "assistant", "content": ir_json_str})
                messages.append({"role": "user", "content": error_feedback})

        # All retries exhausted
        return {"status": "error", "message": f"Failed after {1 + max_retries} attempts. Last error: {last_error}"}

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove markdown code fences that LLMs sometimes wrap around JSON."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


if __name__ == "__main__":
    # Load API key from .env file
    from dotenv import dotenv_values
    env = dotenv_values(os.path.join(os.path.dirname(__file__), '..', '.env'))

    # Simple test run
    translator = OksTranslator(
        "d:/document/projects/minor/oks_scraped/oks_schema_examples.xml",
        "d:/document/projects/minor/oks_scraped/gold_pairs.jsonl",
        llm_api_key=env.get("LLM_API_KEY"),
        llm_base_url=env.get("LLM_BASE_URL"),
        llm_model=env.get("LLM_MODEL")
    )
    print("Executing query...")
    result = translator.translate("Find applications whose Timeout is greater than 50")
    print("\nResult:")
    print(json.dumps(result, indent=2))
