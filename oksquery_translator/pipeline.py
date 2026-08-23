"""
pipeline.py — End-to-End Orchestrator
=======================================

Wires together all modules into a single ``answer()`` call:

    User NL → Schema Retrieval → Prompt → LLM Translation → Validate/Repair
    → Execute → LLM Interpretation → Final Answer
"""

import os
from typing import Dict, Optional

from .schema_retrieval import SchemaRetriever
from .few_shot import FewShotManager
from .prompt_builder import PromptBuilder
from .translator import Translator
from .executor import Executor
from .interpreter import Interpreter


class OksPipeline:
    """
    Complete NL → OksQuery → Execution → Answer pipeline.

    Usage::

        pipeline = OksPipeline()
        result = pipeline.answer("Which executables have InitTimeout > 2?")
        print(result["answer"])
        print(result["oks_query"])
    """

    def __init__(self, data_file: str = "daq/segments/setup.data.xml",
                 schema_dir: str = None,
                 repo_root: str = None,
                 llm_api_key: str = None,
                 llm_base_url: str = None,
                 llm_model: str = None,
                 max_retries: int = 3):
        """
        Parameters
        ----------
        data_file : str
            OKS data file path (repo-relative or absolute).
        schema_dir : str, optional
            Path to *.schema.xml directory.  Auto-detected if omitted.
        repo_root : str, optional
            Repository root for discovering few-shot files.
        llm_api_key, llm_base_url, llm_model : str, optional
            LLM provider configuration.
        max_retries : int
            Max repair attempts for the translation loop.
        """
        if repo_root is None:
            repo_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )

        # --- Initialise components ---
        self.schema_retriever = SchemaRetriever(
            data_file=data_file,
            schema_dir=schema_dir,
        )

        self.few_shot_manager = FewShotManager(repo_root=repo_root)

        self.prompt_builder = PromptBuilder(
            schema_retriever=self.schema_retriever,
            few_shot_manager=self.few_shot_manager,
        )

        self.translator = Translator(
            prompt_builder=self.prompt_builder,
            schema_retriever=self.schema_retriever,
            data_file=data_file,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            max_retries=max_retries,
        )

        self.executor = Executor(data_file=data_file)

        self.interpreter = Interpreter(
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
        )

        self.data_file = data_file

    def answer(self, question: str, version: str = None) -> Dict:
        """
        Full pipeline: natural-language question → clean answer.

        Parameters
        ----------
        question : str
            The user's natural-language question.
        version : str, optional
            Temporal version specifier (e.g. "hash:abc123",
            "date:2024-03-15", "tdaq-13-00-00").

        Returns
        -------
        dict with keys:
            status : "success" | "error"
            answer : str (the natural-language answer)
            oks_query : str (the generated OksQuery)
            target_class : str
            result_count : int
            results : list of dicts (matching objects)
            attempts : int (translation attempts)
            message : str (error message, if any)
        """
        # ------ Step 1: Translate NL → OksQuery ------
        translation = self.translator.translate(question)

        if translation["status"] != "success":
            return {
                "status": "error",
                "answer": f"Translation failed: {translation.get('message', 'unknown error')}",
                "oks_query": "",
                "target_class": "",
                "result_count": 0,
                "results": [],
                "attempts": translation.get("attempts", 0),
                "message": translation.get("message", ""),
            }

        target_class = translation["target_class"]
        oks_query = translation["oks_query"]
        attempts = translation.get("attempts", 1)

        # ------ Step 2: Execute the query ------
        exec_result = self.executor.execute(
            target_class, oks_query, version=version
        )

        if not exec_result.success:
            return {
                "status": "error",
                "answer": f"Query execution failed: {exec_result.message}",
                "oks_query": oks_query,
                "target_class": target_class,
                "result_count": 0,
                "results": [],
                "attempts": attempts,
                "message": exec_result.message,
            }

        # ------ Step 3: Interpret the results ------
        version_label = version or "current"
        interpretation = self.interpreter.interpret(
            question=question,
            target_class=target_class,
            oks_query=oks_query,
            objects=exec_result.objects,
            count=exec_result.count,
            version=version_label,
        )

        return {
            "status": "success",
            "answer": interpretation,
            "oks_query": oks_query,
            "target_class": target_class,
            "result_count": exec_result.count,
            "results": exec_result.objects,
            "attempts": attempts,
            "message": "",
        }

    def translate_only(self, question: str) -> Dict:
        """
        Translate without executing or interpreting.
        Useful for testing the translation layer alone.

        Returns the same dict as Translator.translate().
        """
        return self.translator.translate(question)


def answer(question: str, version: str = None, **kwargs) -> str:
    """
    Convenience function: one-call translation + execution + interpretation.

    Returns just the answer string.

    Usage::

        from oksquery_translator import answer
        print(answer("Which executables have InitTimeout > 2?"))
    """
    pipeline = OksPipeline(**kwargs)
    result = pipeline.answer(question, version=version)
    if result["status"] == "success":
        return result["answer"]
    return f"Error: {result.get('message', result.get('answer', 'unknown'))}"
