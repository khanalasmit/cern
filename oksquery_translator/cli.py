"""
cli.py — Interactive CLI for the OKS Query Translator
======================================================

Run with::

    python -m oksquery_translator.cli

Provides an interactive prompt where users can type natural-language
questions and receive translated OksQuery strings and answers.
"""

import json
import logging
import os
import sys

# Ensure the package is importable when running as __main__
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(MODULE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def _load_env():
    """Load .env file for LLM configuration."""
    try:
        from dotenv import load_dotenv
        for env_path in (
            os.path.join(MODULE_DIR, ".env"),
            os.path.join(REPO_ROOT, ".env"),
        ):
            if os.path.isfile(env_path):
                load_dotenv(env_path, override=True)
                return
    except ImportError:
        # Manual fallback
        for env_path in (
            os.path.join(MODULE_DIR, ".env"),
            os.path.join(REPO_ROOT, ".env"),
        ):
            if not os.path.isfile(env_path):
                continue
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            os.environ[key.strip()] = val.strip()
                return
            except Exception:
                continue


def _configure_debug_logging(enabled: bool) -> None:
    """Toggle detailed translator traces without affecting normal CLI output."""
    package_logger = logging.getLogger("oksquery_translator")
    package_logger.setLevel(logging.DEBUG if enabled else logging.WARNING)
    package_logger.propagate = False

    handler = next(
        (h for h in package_logger.handlers if getattr(h, "_oks_cli_trace", False)),
        None,
    )
    if handler is None:
        handler = logging.StreamHandler(sys.stderr)
        handler._oks_cli_trace = True
        handler.setFormatter(logging.Formatter("[TRACE %(name)s] %(levelname)s: %(message)s"))
        package_logger.addHandler(handler)


def main():
    """Entry point for the interactive CLI."""
    _load_env()
    debug_enabled = os.environ.get("OKS_TRANSLATOR_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    _configure_debug_logging(debug_enabled)

    # Check API key
    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print("WARNING: LLM_API_KEY is not set. Please configure .env first.")
        print("         Copy .env.example to .env and add your API key.\n")

    print("=" * 60)
    print("  OKS Query Translator — ATLAS DAQ Configuration")
    print("=" * 60)

    # Show LLM config
    print(f"  LLM model: {os.environ.get('LLM_MODEL', 'mimo-v2.5-pro')}")
    print(f"  LLM URL:   {os.environ.get('LLM_BASE_URL', 'https://api.xiaomimimo.com/v1')}")

    print()
    print("Commands:")
    print("  Type a question to translate and execute.")
    print("  'translate <question>' — translate only (no execution).")
    print("  'version <v>'          — set temporal version.")
    print("  'debug on' / 'debug off' — show/hide detailed pipeline and schema traces.")
    print("  'probe'                — re-run environment probe.")
    print("  'exit' / 'quit'        — exit.")
    print("-" * 60)

    # Initialise the pipeline
    print("\nInitializing pipeline...")
    try:
        from oksquery_translator.pipeline import OksPipeline
        pipeline = OksPipeline(repo_root=REPO_ROOT)
    except Exception as e:
        print(f"Failed to initialize pipeline: {e}")
        return

    # Run environment probe (breif.md Step 1)
    print("\n--- Environment Probe (breif.md Step 1) ---")
    probe = pipeline.schema_retriever.environment_probe()
    print(f"  oks_dump:    {probe['oks_dump']}")
    if "oks_dump_status" in probe:
        print(f"  oks_dump -f: {probe['oks_dump_status']}")
    print(f"  config mod:  {probe['config_module']}")
    print(f"  schema dir:  {probe['schema_dir']}")
    print(f"  data file:   {probe['data_file']}")
    print(f"  classes:     {probe['class_count']} discovered from live schema")
    if probe['classes']:
        print(f"  first 20:    {', '.join(probe['classes'][:20])}")

    example_count = pipeline.few_shot_manager.get_example_count()
    print(f"  few-shot:    {example_count} examples loaded")
    print(f"  Ready!\n")

    current_version = None

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() in ("debug on", "debug off"):
            debug_enabled = user_input.lower() == "debug on"
            _configure_debug_logging(debug_enabled)
            print(f"  Debug tracing {'enabled' if debug_enabled else 'disabled'}.\n")
            continue

        # Probe command
        if user_input.lower() == "probe":
            probe = pipeline.schema_retriever.environment_probe()
            print(f"\n--- Environment Probe ---")
            for k, v in probe.items():
                if k == "classes":
                    print(f"  {k}: {', '.join(v[:20])}")
                else:
                    print(f"  {k}: {v}")
            print()
            continue

        # Version command
        if user_input.lower().startswith("version "):
            version_arg = user_input[8:].strip()
            if version_arg.lower() in ("none", "current", "reset"):
                current_version = None
                print("  Temporal version reset to current.\n")
            else:
                current_version = version_arg
                print(f"  Temporal version set to: {current_version}\n")
            continue

        # Translate-only command
        if user_input.lower().startswith("translate "):
            question = user_input[10:].strip()
            if not question:
                print("  Usage: translate <your question>\n")
                continue
            print("  Translating...")
            result = pipeline.translate_only(question)
            print()
            if result["status"] == "success":
                print(f"  Target Class: {result['target_class']}")
                print(f"  OKS Query:    {result['oks_query']}")
                print(f"  Attempts:     {result.get('attempts', 1)}")
            else:
                print(f"  Error: {result.get('message', 'unknown')}")
            print()
            continue

        # Full pipeline
        question = user_input
        print("  Thinking...")

        result = pipeline.answer(question, version=current_version)

        print()
        print("=" * 60)
        if result["status"] == "success":
            print(f"  Intent:       {result.get('intent', 'OKS_CURRENT_QUERY')}")
            if result.get("run_number"):
                print(f"  Run Number:   {result['run_number']}")
                print(f"  Partition:    {result.get('partition', 'all_hosts')}")
            print(f"  Target Class: {result['target_class']}")
            print(f"  OKS Query:    {result['oks_query']}")
            print(f"  Attempts:     {result.get('attempts', 1)}")
            print(f"  Results:      {result['result_count']} object(s) matched")
            if result.get("version"):
                print(f"  Version:      {result['version']}")
            print("-" * 60)
            print()
            print(f"  {result['answer']}")
        else:
            if result.get("intent"):
                print(f"  Intent:       {result['intent']}")
            print(f"  Error: {result.get('answer', result.get('message', ''))}")
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
