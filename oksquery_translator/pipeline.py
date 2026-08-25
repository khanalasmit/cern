"""
pipeline.py — End-to-End Orchestrator
=======================================

Wires together all modules into a single ``answer()`` call:

    User NL → Schema Retrieval → Prompt → LLM Translation → Validate/Repair
    → Execute → LLM Interpretation → Final Answer
"""

import logging
import os
import re
import time
from typing import Dict, Optional

logger = logging.getLogger("oksquery_translator.pipeline")

from .schema_retrieval import SchemaRetriever
from .few_shot import FewShotManager
from .prompt_builder import PromptBuilder
from .translator import Translator
from .executor import Executor
from .interpreter import Interpreter
from .context import OksContext, OksContextBuilder
from .preprocessing import QueryPreprocessor
from .retrieval import SchemaSearchIndex
from .intent import (
    Intent,
    IntentResult,
    IntentClassifier,
    RunResolver,
    extract_run_and_partition,
    MSG_GENERAL_OUT_OF_SCOPE,
    MSG_CERN_OUT_OF_SCOPE,
    MSG_HISTORICAL_MISSING_RUN,
)


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
                 max_retries: int = 3,
                 intent_classifier: IntentClassifier = None,
                 run_resolver: RunResolver = None):
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
        intent_classifier : IntentClassifier, optional
            Custom intent classifier instance.
        run_resolver : RunResolver, optional
            Custom run resolver instance.
        """
        if repo_root is None:
            repo_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )

        # --- Initialise components ---
        self.intent_classifier = intent_classifier or IntentClassifier(
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
        )

        self.run_resolver = run_resolver or RunResolver(
            repo_root=repo_root,
        )

        self.context_builder = OksContextBuilder(
            data_file=data_file,
            schema_dir=schema_dir,
        )

        self.query_preprocessor = QueryPreprocessor()
        self.schema_index = SchemaSearchIndex()

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

        self.executor = Executor(data_file=data_file, repo_root=repo_root)

        self.interpreter = Interpreter(
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
        )

        self.data_file = data_file

    def answer(self, question: str, version: str = None,
               interpret: bool = True) -> Dict:
        """
        Full pipeline: natural-language question → clean answer.

        Parameters
        ----------
        question : str
            The user's natural-language question.
        version : str, optional
            Temporal version specifier (e.g. "hash:abc123",
            "date:2024-03-15", "tdaq-13-00-00", "tag:r380689@all_hosts").
        interpret : bool
            When true, make the second LLM call that turns results into prose.
            MCP callers should normally set this to false and let the host
            agent interpret the structured result.

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
            intent : str
            run_number : int or None
            partition : str or None
            version : str or None
            version_used : str or None
            schema_fingerprint : str
            oks_context_label : str
            ir : dict or None
        """
        t_pipeline_start = time.perf_counter()
        logger.info(f"=== [PIPELINE START] Question: {question!r} ===")

        # ------ Step 0: Intent Classification & Pre-Filtering ------
        t0 = time.perf_counter()
        intent_info = self.intent_classifier.classify(question)
        t0_elapsed = time.perf_counter() - t0

        logger.info(
            f"[LAYER 0 - Intent & Run Resolution] ({t0_elapsed:.3f}s) → "
            f"Intent={intent_info.intent.value}, Run={intent_info.run_number}, Partition={intent_info.partition or 'all_hosts'}"
        )

        # 0a. Out-of-scope early exit: GENERAL_OUT_OF_SCOPE
        if intent_info.intent == Intent.GENERAL_OUT_OF_SCOPE:
            msg = intent_info.message or MSG_GENERAL_OUT_OF_SCOPE
            logger.info(f"[LAYER 0 - Early Exit] GENERAL_OUT_OF_SCOPE")
            return {
                "status": "error",
                "answer": msg,
                "oks_query": "",
                "target_class": "",
                "result_count": 0,
                "results": [],
                "attempts": 0,
                "message": msg,
                "intent": intent_info.intent.value,
                "run_number": None,
                "partition": None,
                "version": None,
                "version_used": None,
                "schema_fingerprint": "",
                "oks_context_label": "",
            }

        # 0b. Out-of-scope early exit: CERN_OUT_OF_SCOPE
        if intent_info.intent == Intent.CERN_OUT_OF_SCOPE:
            msg = intent_info.message or MSG_CERN_OUT_OF_SCOPE
            logger.info(f"[LAYER 0 - Early Exit] CERN_OUT_OF_SCOPE")
            return {
                "status": "error",
                "answer": msg,
                "oks_query": "",
                "target_class": "",
                "result_count": 0,
                "results": [],
                "attempts": 0,
                "message": msg,
                "intent": intent_info.intent.value,
                "run_number": None,
                "partition": None,
                "version": None,
                "version_used": None,
                "schema_fingerprint": "",
                "oks_context_label": "",
            }

        # 0c. Historical run resolution and version precedence
        effective_version = version
        extracted_run = intent_info.run_number
        partition = intent_info.partition or "all_hosts"
        request_data_file = self.data_file
        request_release = None
        request_repository = None

        if intent_info.intent == Intent.OKS_HISTORICAL_QUERY:
            if version:
                if extracted_run is not None:
                    ver_run, _, _ = extract_run_and_partition(version)
                    if ver_run is not None and ver_run != extracted_run:
                        msg = (
                            f"Version conflict detected: Question specifies run {extracted_run}, "
                            f"but explicit version parameter was set to '{version}'. "
                            f"Please remove the conflicting version parameter or adjust your question."
                        )
                        logger.warning(f"Version Conflict: Question run {extracted_run} vs explicit version {version}")
                        return {
                            "status": "error",
                            "answer": msg,
                            "oks_query": "",
                            "target_class": "",
                            "result_count": 0,
                            "results": [],
                            "attempts": 0,
                            "message": msg,
                            "intent": intent_info.intent.value,
                            "run_number": extracted_run,
                            "partition": partition,
                            "version": version,
                            "version_used": version,
                            "schema_fingerprint": "",
                            "oks_context_label": "",
                        }
                else:
                    ver_run, ver_part, _ = extract_run_and_partition(version)
                    if ver_run is not None:
                        extracted_run = ver_run
                        partition = ver_part or partition
            else:
                if extracted_run is None:
                    msg = (
                        "You asked for historical run configuration data, but did not specify a run number. "
                        "Please provide a valid Run Number (e.g. Run 380689 or tag r380689@all_hosts)."
                    )
                    logger.warning("Historical query missing run number; halting before translation.")
                    return {
                        "status": "error",
                        "answer": msg,
                        "oks_query": "",
                        "target_class": "",
                        "result_count": 0,
                        "results": [],
                        "attempts": 0,
                        "message": msg,
                        "intent": intent_info.intent.value,
                        "run_number": None,
                        "partition": partition,
                        "version": None,
                        "version_used": None,
                        "schema_fingerprint": "",
                        "oks_context_label": "",
                    }

                if not self.run_resolver.validate_run_number(extracted_run, partition):
                    logger.warning(f"Run Validation: failed (Run Number {extracted_run} not found)")
                    msg = (
                        f"Run Number {extracted_run} was not found in the CERN Run Number Database or Git tags. "
                        f"Please verify the run number and enter a valid one (e.g. Run 380689)."
                    )
                    return {
                        "status": "error",
                        "answer": msg,
                        "oks_query": "",
                        "target_class": "",
                        "result_count": 0,
                        "results": [],
                        "attempts": 0,
                        "message": msg,
                        "intent": intent_info.intent.value,
                        "run_number": extracted_run,
                        "partition": partition,
                        "version": None,
                        "version_used": None,
                        "schema_fingerprint": "",
                        "oks_context_label": "",
                    }

                effective_version = self.run_resolver.resolve_version(extracted_run, partition)
                run_info = self.run_resolver.get_run_info(extracted_run)
                if run_info:
                    partition = run_info.get("partition") or partition
                    request_data_file = run_info.get("config_name") or request_data_file
                    request_release = run_info.get("release") or None
                    # Some RNDB integrations provide the exact Git URL.  Keep
                    # it intact; it is more authoritative than a family guess.
                    request_repository = run_info.get("repository") or None

                if effective_version is None:
                    archive_revision = (run_info or {}).get("version", "unknown")
                    msg = (
                        f"Run Number {extracted_run} uses legacy archive revision "
                        f"'{archive_revision}', not a Git/OKS version supported by this "
                        "translator. No query was executed, because it would otherwise "
                        "silently query the current configuration. Use a legacy CORAL/OKS "
                        "Archive resolver for this run."
                    )
                    logger.warning(msg)
                    return {
                        "status": "error", "answer": msg, "oks_query": "", "target_class": "",
                        "result_count": 0, "results": [], "attempts": 0, "message": msg,
                        "intent": intent_info.intent.value, "run_number": extracted_run,
                        "partition": partition, "version": None, "version_used": None,
                        "schema_fingerprint": "", "oks_context_label": "",
                    }
                logger.info(
                    f"[LAYER 0 - Version Resolution] Run {extracted_run} resolved → "
                    f"version={effective_version!r}, partition={partition!r}, release={request_release!r}, data_file={request_data_file!r}"
                )

        if extracted_run is None and effective_version:
            ver_run, ver_part, _ = extract_run_and_partition(effective_version)
            if ver_run is not None:
                extracted_run = ver_run
                partition = ver_part or partition

        # ------ Step 0d: Build immutable OksContext ------
        t1 = time.perf_counter()
        context_builder = self.context_builder
        if request_data_file != self.data_file:
            context_builder = OksContextBuilder(
                data_file=request_data_file,
                schema_dir=getattr(self.schema_retriever, "schema_dir", None),
            )
        oks_context = context_builder.build(version_tag=effective_version)
        t1_elapsed = time.perf_counter() - t1
        logger.info(
            f"[LAYER 1 - OksContext] ({t1_elapsed:.3f}s) → "
            f"identifier={oks_context.schema_identifier!r}, fingerprint={oks_context.schema_fingerprint!r}"
        )

        # Index schema under this fingerprint if not already cached
        if not self.schema_index.has_fingerprint(oks_context.schema_fingerprint):
            t_idx = time.perf_counter()
            from .schema import OksSchemaProvider
            schema_dir = getattr(self.schema_retriever, "schema_dir", None)
            sp = OksSchemaProvider(oks_context=oks_context, data_file=request_data_file, schema_dir=schema_dir)
            self.schema_index.build_from_schema_provider(sp)
            logger.info(f"[LAYER 2 - Schema Indexing] Indexed fingerprint '{oks_context.schema_fingerprint}' in {time.perf_counter() - t_idx:.3f}s")

        if self._requests_all_objects(question):
            return self._answer_all_objects(
                intent_info=intent_info,
                oks_context=oks_context,
                version=effective_version,
                run_number=extracted_run,
                partition=partition,
                data_file=request_data_file,
                release=request_release,
                repository=request_repository,
            )

        # ------ Step 0e: Query Preprocessing (Tokens & Hints) ------
        t_prep = time.perf_counter()
        query_analysis = self.query_preprocessor.analyze(question)
        retrieval_query = query_analysis.to_retrieval_query()
        logger.info(f"[LAYER 2 - Query Preprocessor] ({time.perf_counter() - t_prep:.3f}s) → retrieval_query={retrieval_query!r}")

        # ------ Step 1: Translate NL → OksQuery via AST Pipeline ------
        t_trans = time.perf_counter()
        translation = self.translator.translate(
            question,
            oks_context=oks_context,
            retrieval_query=retrieval_query,
            data_file=request_data_file,
        )
        t_trans_elapsed = time.perf_counter() - t_trans

        if translation["status"] != "success":
            logger.error(f"[LAYER 3 - Translation Failed] ({t_trans_elapsed:.3f}s): {translation.get('message')}")
            return {
                "status": "error",
                "answer": f"Translation failed: {translation.get('message', 'unknown error')}",
                "oks_query": "",
                "target_class": "",
                "result_count": 0,
                "results": [],
                "attempts": translation.get("attempts", 0),
                "message": translation.get("message", ""),
                "intent": intent_info.intent.value,
                "run_number": extracted_run,
                "partition": partition if extracted_run else None,
                "version": effective_version or "current",
                "version_used": effective_version or "current",
                "schema_fingerprint": oks_context.schema_fingerprint,
                "oks_context_label": oks_context.display_label,
                "ir": None,
            }

        target_class = translation["target_class"]
        oks_query = translation["oks_query"]
        attempts = translation.get("attempts", 1)
        ir_dump = translation.get("ir")
        logger.info(
            f"[LAYER 3 - Translation Complete] ({t_trans_elapsed:.3f}s, {attempts} attempt(s)) → "
            f"target_class={target_class!r}, oks_query={oks_query!r}"
        )

        # ------ Step 2: Execute the query via preserved Executor ------
        t_exec = time.perf_counter()
        exec_version = oks_context.version_tag or effective_version
        exec_result = self.executor.execute(
            target_class, oks_query, version=exec_version, data_file=request_data_file,
            release=request_release, partition=partition, repository=request_repository,
        )
        t_exec_elapsed = time.perf_counter() - t_exec

        if not exec_result.success:
            logger.error(f"[LAYER 4 - Execution Failed] ({t_exec_elapsed:.3f}s): {exec_result.message}")
            return {
                "status": "error",
                "answer": f"Query execution failed: {exec_result.message}",
                "oks_query": oks_query,
                "target_class": target_class,
                "result_count": 0,
                "results": [],
                "attempts": attempts,
                "message": exec_result.message,
                "intent": intent_info.intent.value,
                "run_number": extracted_run,
                "partition": partition if extracted_run else None,
                "version": effective_version or "current",
                "version_used": effective_version or "current",
                "schema_fingerprint": oks_context.schema_fingerprint,
                "oks_context_label": oks_context.display_label,
                "ir": ir_dump,
            }

        logger.info(
            f"[LAYER 4 - Execution Complete] ({t_exec_elapsed:.3f}s) → "
            f"Returned {exec_result.count} object(s)"
        )

        version_label = effective_version or "current"
        if not interpret:
            total_elapsed = time.perf_counter() - t_pipeline_start
            logger.info(
                f"=== [PIPELINE COMPLETE] Structured result in {total_elapsed:.3f}s "
                f"(Intent={t0_elapsed:.2f}s, Context={t1_elapsed:.2f}s, "
                f"Translation={t_trans_elapsed:.2f}s, Execution={t_exec_elapsed:.2f}s) ==="
            )
            return {
                "status": "success",
                "answer": "",
                "oks_query": oks_query,
                "target_class": target_class,
                "result_count": exec_result.count,
                "results": exec_result.objects,
                "attempts": attempts,
                "message": "",
                "intent": intent_info.intent.value,
                "run_number": extracted_run,
                "partition": partition if extracted_run else None,
                "version": version_label,
                "version_used": version_label,
                "schema_fingerprint": oks_context.schema_fingerprint,
                "oks_context_label": oks_context.display_label,
                "ir": ir_dump,
            }

        # ------ Step 3: Interpret the results ------
        t_interp = time.perf_counter()
        logger.info(
            f"[LAYER 5 - Interpretation Started] Generating natural-language summary for {exec_result.count} object(s)..."
        )
        interpretation = self.interpreter.interpret(
            question=question,
            target_class=target_class,
            oks_query=oks_query,
            objects=exec_result.objects,
            count=exec_result.count,
            version=version_label,
        )
        t_interp_elapsed = time.perf_counter() - t_interp
        logger.info(
            f"[LAYER 5 - Interpretation Complete] ({t_interp_elapsed:.3f}s)"
        )

        if (intent_info.intent == Intent.OKS_HISTORICAL_QUERY or effective_version not in (None, "current")) and extracted_run is not None:
            header = f"Run Number: {extracted_run}\nPartition: {partition}\n\n"
            if not interpretation.startswith("Run Number:"):
                interpretation = header + interpretation
        elif intent_info.intent == Intent.OKS_CURRENT_QUERY:
            header = "Configuration: Current / Default (HEAD)\n\n"
            if not interpretation.startswith("Configuration:"):
                interpretation = header + interpretation

        total_elapsed = time.perf_counter() - t_pipeline_start
        logger.info(
            f"=== [PIPELINE COMPLETE] Total time elapsed: {total_elapsed:.3f}s "
            f"(Intent={t0_elapsed:.2f}s, Context={t1_elapsed:.2f}s, Translation={t_trans_elapsed:.2f}s, "
            f"Execution={t_exec_elapsed:.2f}s, Interpretation={t_interp_elapsed:.2f}s) ==="
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
            "intent": intent_info.intent.value,
            "run_number": extracted_run,
            "partition": partition if extracted_run else None,
            "version": version_label,
            "version_used": version_label,
            "schema_fingerprint": oks_context.schema_fingerprint,
            "oks_context_label": oks_context.display_label,
            "ir": ir_dump,
        }


    @staticmethod
    def _requests_all_objects(question: str) -> bool:
        """Identify an unqualified request spanning every OKS class."""
        return bool(re.search(r"\b(?:all|every)\s+(?:OKS\s+)?objects?\b", question, re.IGNORECASE))

    def _answer_all_objects(self, *, intent_info: IntentResult, oks_context: OksContext,
                            version: Optional[str], run_number: Optional[int],
                            partition: str, data_file: str,
                            release: Optional[str] = None,
                            repository: Optional[str] = None) -> Dict:
        """Enumerate every concrete class for an explicit all-objects request."""
        query = '(all (object-id "" !=))'
        class_names = self.schema_retriever.get_class_list()
        objects, failures, total_count = [], [], 0
        display_limit = 1000
        for class_name in class_names:
            result = self.executor.execute(
                class_name, query, version=oks_context.version_tag or version,
                data_file=data_file, release=release, partition=partition,
                repository=repository,
            )
            if not result.success:
                failures.append(class_name)
                continue
            total_count += result.count
            for obj in result.objects:
                if len(objects) >= display_limit:
                    break
                obj = dict(obj)
                obj["class"] = class_name
                objects.append(obj)

        shown = len(objects)
        answer = f"Found {total_count} objects across {len(class_names) - len(failures)} OKS classes."
        if total_count > shown:
            answer += f" Showing the first {shown} objects."
        if failures:
            answer += f" {len(failures)} classes could not be queried."
        if run_number is not None:
            answer = f"Run Number: {run_number}\nPartition: {partition}\n\n" + answer
        else:
            answer = "Configuration: Current / Default (HEAD)\n\n" + answer

        return {
            "status": "success", "answer": answer, "oks_query": query,
            "target_class": "*", "result_count": total_count, "results": objects,
            "attempts": 0, "message": "", "intent": intent_info.intent.value,
            "run_number": run_number, "partition": partition if run_number else None,
            "version": version or "current", "version_used": version or "current",
            "schema_fingerprint": oks_context.schema_fingerprint,
            "oks_context_label": oks_context.display_label,
            "ir": None,
        }

    def translate_only(self, question: str, version: Optional[str] = None) -> Dict:
        """
        Translate without executing or interpreting.
        Useful for testing the translation layer alone.

        Returns the same dict as Translator.translate().
        """
        oks_context = self.context_builder.build(version_tag=version)
        query_analysis = self.query_preprocessor.analyze(question)
        retrieval_query = query_analysis.to_retrieval_query()
        return self.translator.translate(
            question,
            oks_context=oks_context,
            retrieval_query=retrieval_query,
        )


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
