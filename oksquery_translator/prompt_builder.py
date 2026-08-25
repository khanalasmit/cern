"""
prompt_builder.py — LLM Prompt Assembly
========================================

Constructs the complete prompt for LLM Call #1 (NL → OksQuery translation).
Combines:
  - OksQuery syntax rules (embedded verbatim)
  - Schema slice from schema_retrieval.py
  - Few-shot examples from few_shot.py
  - The user's question
"""

from .schema_retrieval import SchemaRetriever
from .few_shot import FewShotManager


# ---------------------------------------------------------------------------
# The OksQuery syntax reference, embedded verbatim in every prompt.
# Derived from breif.md Section 4.
# ---------------------------------------------------------------------------
OKSQUERY_SYNTAX_RULES = """\
=== OksQuery Syntax Rules ===

The OksQuery language is a LISP-style S-expression language used to filter
OKS (Object Kernel Support) configuration objects.

Top-level form:
  ( all | this  <expression> )
    all  → search this class AND all subclasses
    this → search ONLY this exact class

Expression types:

  Attribute comparison:
    ( "attribute-name" "value" <comparator> )
    Example: ( "InitTimeout" "2" > )

  Object ID comparison:
    ( object-id "object-identifier" = )
    Exact IDs use '='. The special match-all form uses:
    ( object-id "" != )

  Logical AND (requires >= 2 operands):
    ( and <expr1> <expr2> ... )
    Example: ( and ("InitTimeout" "30" =) ("ExitTimeout" "5" =) )

  Logical OR (requires >= 2 operands):
    ( or <expr1> <expr2> ... )
    Example: ( or ("Name" "app1" =) ("Name" "app2" =) )

  Logical NOT (exactly 1 operand):
    ( not <expr> )
    Example: ( not ("Name" "test" =) )

  Relationship traversal:
    ( "RelationshipName" some|all <sub-expression> )
      some → at least one related object matches
      all  → every related object matches
    Example: ( "RunsOn" some (object-id "lxplus001.cern.ch" =) )

Comparators:
  =    equal
  !=   not equal
  <    less than
  >    greater than
  <=   less or equal
  >=   greater or equal
  ~=   regex match (boost::regex_match, must match the WHOLE value)

HARD RULES you MUST obey:
  1. The scope token (all or this) appears ONCE, at the top level only.
  2. 'and'/'or' need >= 2 operands. 'not' needs exactly 1.
  3. Attribute names and relationship names are QUOTED STRINGS.
  4. Attribute and relationship names are STRICTLY CASE-SENSITIVE.
     You MUST copy the EXACT CamelCase / casing from the 'Relevant OKS Schema Context'
     (e.g., 'SubDetector', NOT 'Subdetector'; 'InitTimeout', NOT 'inittimeout'; 'RunsOn', NOT 'runs_on').
  5. Values are ALWAYS quoted strings, even numbers: "2" not 2.
  6. The attribute MUST exist on the target class (check the schema below).
     NEVER invent attributes like "Name" or "name" unless "Name" is explicitly listed under Attributes for that class.
     To match or filter on an object's identifier, use (object-id "..." =) or (object-id "" !=).
  7. object-id supports '=' for an exact ID. For an unqualified request to
     list every object in the target class, use ONLY the documented match-all
     pattern: (object-id "" !=).
  8. Tokens like #this.UID are compared literally (stored verbatim).
  9. Inside a relationship expression, attributes are evaluated against
     the RELATIONSHIP'S TARGET CLASS, not the outer class.
  10. ALWAYS prioritize the attributes and relationships listed under 'Relevant OKS Schema Context'
      over few-shot examples. If a few-shot example uses an attribute that is not in the live schema,
      look for a relationship (e.g. "Detector" instead of "SubDetector") or use (object-id "..." =).
  11. To match all objects of a class, use (all (object-id "" !=)).
  12. Run numbers (e.g. 'run 468836', 'run 380689') specify the temporal database configuration version and are handled automatically by the environment. Do NOT add run numbers as attributes or relationships in the OKS query string unless the schema explicitly declares an attribute for it.
"""

# ---------------------------------------------------------------------------
# Output format instructions (Legacy & JSON IR)
# ---------------------------------------------------------------------------
OUTPUT_FORMAT_INSTRUCTIONS = """\
=== Output Format ===

Output EXACTLY two lines, nothing else:
CLASS: <ClassName>
QUERY: <OksQuery string>

Examples of correct output:
CLASS: Executable
QUERY: (all ("InitTimeout" "2" >))

CLASS: BaseApplication
QUERY: (all (and ("InitTimeout" "30" =) ("ExitTimeout" "5" =)))

Do NOT add explanations, markdown formatting, code fences, or any other text.
Only the CLASS: and QUERY: lines.
"""

IR_SCHEMA_DESCRIPTION = """\
=== Output Format (JSON IR) ===

You MUST output ONLY a valid JSON object matching the following QueryIR schema:

{
  "target_class": "<ClassName>",
  "scope": "all" | "this",
  "expression": <Expression>,
  "explanation": "brief explanation"
}

Where <Expression> is EXACTLY ONE of:
1. Attribute comparison:
   {"type": "attribute_compare", "attribute": "<attr_name>", "operator": "<op>", "value": "<val>"}
   Operators: "=", "!=", "~=", "<", "<=", ">", ">="
   IMPORTANT: "value" MUST ALWAYS be a string (e.g. "2", "30", "test").
2. Object ID match:
   {"type": "object_id", "operator": "=", "object_id": "<id>"}
   For a match-all request, use {"type": "object_id", "operator": "!=", "object_id": ""}.
3. Relationship traversal:
   {"type": "relationship", "name": "<rel_name>", "quantifier": "some" | "all", "expression": <Expression>}
   NOTE: Nested expression is evaluated against the relationship's TARGET CLASS.
4. Logical AND:
   {"type": "and", "operands": [<Expression>, <Expression>, ...]}  (minimum 2 operands)
5. Logical OR:
   {"type": "or", "operands": [<Expression>, <Expression>, ...]}   (minimum 2 operands)
6. Logical NOT:
   {"type": "not", "operand": <Expression>}

CRITICAL RULES:
- Output ONLY valid JSON. Do NOT include markdown code fences (no ```json), commentary, or extra text.
- Use EXACT case-sensitive class, attribute, and relationship names from 'Relevant OKS Schema Context'.
- Scope "all" or "this" appears ONLY at the top level of QueryIR, NEVER inside expressions.
"""


class PromptBuilder:
    """
    Assembles the complete prompt for LLM Call #1 (translation).

    Usage::

        builder = PromptBuilder(schema_retriever, few_shot_manager)
        system_prompt, user_prompt = builder.build(question)
    """

    def __init__(self, schema_retriever: SchemaRetriever,
                 few_shot_manager: FewShotManager):
        self.schema_retriever = schema_retriever
        self.few_shot_manager = few_shot_manager

    def build(self, question: str, max_schema_classes: int = 3,
              max_few_shot: int = 5, oks_context=None,
              retrieval_query: str = None) -> tuple:
        """
        Build the (system_prompt, user_prompt) pair for the translation LLM.

        Parameters
        ----------
        question : str
            The user's natural-language question.
        max_schema_classes : int
            Maximum number of classes to include in the schema slice.
        max_few_shot : int
            Maximum number of few-shot examples to include.
        oks_context : OksContext, optional
            Resolved context metadata block.
        retrieval_query : str, optional
            Enriched query token string for schema retrieval.

        Returns
        -------
        (system_prompt, user_prompt) : tuple of str
        """
        # 1. Retrieve schema context
        lookup_q = retrieval_query or question
        schema_context = self.schema_retriever.get_schema_context(
            lookup_q, max_classes=max_schema_classes
        )

        # 2. Retrieve few-shot examples
        few_shot_context = self.few_shot_manager.get_examples(
            question, top_k=max_few_shot
        )

        # 3. Context metadata block
        context_meta = oks_context.to_prompt_metadata() if (oks_context and hasattr(oks_context, "to_prompt_metadata")) else ""

        # 4. Assemble system prompt
        prompt_parts = [
            "You are an expert OKS query translator for the ATLAS TDAQ configuration system.\n"
            "Your task is to translate a natural-language question into a strictly formatted JSON Intermediate Representation (IR).",
            OKSQUERY_SYNTAX_RULES,
        ]
        if context_meta:
            prompt_parts.append(context_meta)
        if schema_context:
            prompt_parts.append(schema_context)
        if few_shot_context:
            prompt_parts.append(few_shot_context)
        prompt_parts.append(IR_SCHEMA_DESCRIPTION)

        system_prompt = "\n\n".join(prompt_parts)

        # 5. User prompt is the question
        user_prompt = question

        return system_prompt, user_prompt

    def build_repair_prompt(self, question: str, previous_class: str,
                            previous_query: str, error_message: str,
                            schema_hint: str = "") -> str:
        """
        Build a repair prompt to feed back to the LLM after a validation
        failure.  Parses the oks_dump error to provide targeted guidance,
        detects case mismatches, relationship alternatives, and close matches,
        and includes the full schema of the class.

        Parameters
        ----------
        question : str
            Original user question.
        previous_class : str
            The class name from the failed attempt.
        previous_query : str
            The OksQuery string that failed validation.
        error_message : str
            The error message (stderr from oks_dump, or syntax checker).
        schema_hint : str, optional
            Full schema of the class (attributes + relationships).

        Returns
        -------
        str : The repair prompt (sent as a user message).
        """
        import re

        parts = [
            "YOUR PREVIOUS QUERY FAILED. You MUST fix it.",
            f"CLASS: {previous_class}",
            f"QUERY: {previous_query}",
            "",
            f"Error from the OKS engine:",
            f"  {error_message}",
            "",
        ]

        # Extract available attribute/relationship names from schema_hint if present
        available_attrs = []
        available_rels = []
        if schema_hint:
            for line in schema_hint.splitlines():
                line = line.strip()
                if line.startswith("- ") and "(" in line:
                    attr_name = line[2:].split("(")[0].strip()
                    if attr_name:
                        available_attrs.append(attr_name)
                elif line.startswith("- ") and "→" in line:
                    rel_name = line[2:].split("→")[0].strip()
                    if rel_name:
                        available_rels.append(rel_name)
                elif line.startswith("- "):
                    item_name = line[2:].strip()
                    if item_name:
                        available_attrs.append(item_name)

        # Parse the error to give targeted guidance
        rel_missing = re.search(
            r"can't find relationship \"([^\"]+)\" in class \"([^\"]+)\"",
            error_message
        )
        attr_missing = re.search(
            r"can't find attribute \"([^\"]+)\" in class \"([^\"]+)\"",
            error_message
        )
        class_missing = re.search(
            r"can't find class \"([^\"]+)\"",
            error_message
        )

        if rel_missing:
            bad_name = rel_missing.group(1)
            on_class = rel_missing.group(2)
            # Check case-mismatch
            case_match = next((r for r in available_rels if r.lower() == bad_name.lower()), None)
            if case_match:
                parts.append(
                    f">>> CRITICAL CASE-SENSITIVITY ERROR: You wrote relationship \"{bad_name}\", "
                    f"but the exact casing on class \"{on_class}\" is \"{case_match}\"."
                )
                parts.append(
                    f">>> In OKS, casing must match EXACTLY. Replace \"{bad_name}\" with \"{case_match}\"."
                )
            else:
                # Check close matches
                close = [r for r in available_rels if bad_name.lower() in r.lower() or r.lower() in bad_name.lower()]
                parts.append(
                    f">>> THE PROBLEM: You used relationship \"{bad_name}\" but "
                    f"it does NOT exist on class \"{on_class}\"."
                )
                if close:
                    parts.append(f">>> Did you mean one of these relationships: {', '.join(close)}?")
                parts.append(
                    f">>> You MUST use one of the EXACT relationship names "
                    f"listed in the schema below. Do NOT guess or abbreviate."
                )
        elif attr_missing:
            bad_name = attr_missing.group(1)
            on_class = attr_missing.group(2)
            # Check case-mismatch
            case_match = next((a for a in available_attrs if a.lower() == bad_name.lower()), None)
            if case_match:
                parts.append(
                    f">>> CRITICAL CASE-SENSITIVITY ERROR: You wrote attribute \"{bad_name}\", "
                    f"but the exact casing on class \"{on_class}\" is \"{case_match}\"."
                )
                parts.append(
                    f">>> In OKS, casing must match EXACTLY. Replace \"{bad_name}\" with \"{case_match}\"."
                )
            else:
                # Check if there is a relationship with a matching or similar name
                rel_match = next((r for r in available_rels if bad_name.lower() in r.lower() or r.lower() in bad_name.lower()), None)
                if rel_match:
                    parts.append(
                        f">>> THE PROBLEM: \"{bad_name}\" is NOT an attribute on class \"{on_class}\", "
                        f"but there is a RELATIONSHIP named \"{rel_match}\"."
                    )
                    parts.append(
                        f">>> Try using relationship traversal instead: (\"{rel_match}\" some (object-id \"...\" =))"
                    )
                else:
                    close = [a for a in available_attrs if bad_name.lower() in a.lower() or a.lower() in bad_name.lower()]
                    parts.append(
                        f">>> THE PROBLEM: You used attribute \"{bad_name}\" but "
                        f"it does NOT exist on class \"{on_class}\"."
                    )
                    if bad_name.lower() in ("name", "id"):
                        parts.append(
                            f">>> HINT: Class \"{on_class}\" may not have a \"{bad_name}\" attribute. "
                            f"To match on object identifier, use (object-id \"...\" =)."
                        )
                    if close:
                        parts.append(f">>> Did you mean one of these attributes: {', '.join(close)}?")
                    parts.append(
                        f">>> You MUST use one of the EXACT attribute names "
                        f"listed in the schema below. Do NOT guess or abbreviate."
                    )
        elif class_missing:
            bad_class = class_missing.group(1)
            parts.append(
                f">>> THE PROBLEM: Class \"{bad_class}\" does not exist. "
                f"Use a different class name from the available schema."
            )

        if schema_hint:
            parts.append("")
            parts.append("=== CORRECT SCHEMA FOR THIS CLASS (use ONLY these names) ===")
            parts.append(schema_hint)
            parts.append("=== END OF SCHEMA ===")

        parts.append("")
        parts.append(
            "Fix the query using ONLY the attribute/relationship names "
            "from the schema above. Output EXACTLY two lines:"
        )
        parts.append("CLASS: <ClassName>")
        parts.append("QUERY: <OksQuery string>")

        return "\n".join(parts)
