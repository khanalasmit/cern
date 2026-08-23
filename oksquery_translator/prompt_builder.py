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
    Note: object-id supports '=' operator ONLY.

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
  4. Values are ALWAYS quoted strings, even numbers: "2" not 2.
  5. The attribute MUST exist on the target class (check the schema below).
  6. object-id only supports '=' comparator.
  7. Tokens like #this.UID are compared literally (stored verbatim).
  8. Inside a relationship expression, attributes are evaluated against
     the RELATIONSHIP'S TARGET CLASS, not the outer class.
"""

# ---------------------------------------------------------------------------
# Output format instructions
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
              max_few_shot: int = 5) -> tuple:
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

        Returns
        -------
        (system_prompt, user_prompt) : tuple of str
        """
        # 1. Retrieve schema context
        schema_context = self.schema_retriever.get_schema_context(
            question, max_classes=max_schema_classes
        )

        # 2. Retrieve few-shot examples
        few_shot_context = self.few_shot_manager.get_examples(
            question, top_k=max_few_shot
        )

        # 3. Assemble system prompt
        system_prompt = (
            "You are an expert OKS query translator for the ATLAS TDAQ "
            "configuration system. Your task is to translate a natural-language "
            "question into a valid OksQuery string.\n\n"
            f"{OKSQUERY_SYNTAX_RULES}\n\n"
            f"{schema_context}\n\n"
            f"{few_shot_context}\n\n"
            f"{OUTPUT_FORMAT_INSTRUCTIONS}"
        )

        # 4. User prompt is simply the question
        user_prompt = question

        return system_prompt, user_prompt

    def build_repair_prompt(self, question: str, previous_class: str,
                            previous_query: str, error_message: str,
                            schema_hint: str = "") -> str:
        """
        Build a repair prompt to feed back to the LLM after a validation
        failure.  Includes the error message and optionally a schema hint
        (e.g. available attributes on a class).

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
            Additional schema info to help the LLM correct itself.

        Returns
        -------
        str : The repair prompt (sent as a user message).
        """
        parts = [
            "Your previous query was invalid.",
            f"CLASS: {previous_class}",
            f"QUERY: {previous_query}",
            "",
            f"Error from the OKS engine:\n  {error_message}",
        ]
        if schema_hint:
            parts.append(f"\n{schema_hint}")
        parts.append(
            "\nPlease fix the query. Output EXACTLY two lines: CLASS: and QUERY:"
        )
        return "\n".join(parts)
