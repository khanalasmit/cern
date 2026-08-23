import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys

# Running ``python cli.py`` makes this directory importable, but not its
# parent.  Add the repository root so absolute ``translator_module.*``
# imports used by the agent resolve without requiring a different command.
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(MODULE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def _parse_revision_date(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and require an explicit timezone."""

    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid ISO-8601 date: {value!r}"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            "date must include a timezone offset, for example +05:45 or Z"
        )
    return parsed


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Translate natural-language questions into OKS queries."
    )
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--commit-hash", help="query schema from a Git commit")
    selector.add_argument("--tag", help="query schema from a Git tag")
    selector.add_argument(
        "--date",
        type=_parse_revision_date,
        help="query the newest commit at or before an ISO-8601 timestamp",
    )
    selector.add_argument("--run-id", help="query the commit mapped to a domain run ID")
    parser.add_argument(
        "--repo",
        default=REPO_ROOT,
        help="Git repository containing the historical OKS files",
    )
    parser.add_argument(
        "--ref",
        default="main",
        help="Git ref used for date-based resolution (default: main)",
    )
    parser.add_argument(
        "--run-map",
        help="JSON file mapping run IDs to Git commits",
    )
    parser.add_argument(
        "--schema-path",
        default="oks_scraped/oks_schema_examples.xml",
        help="repository-relative schema wrapper path",
    )
    parser.add_argument(
        "--gold-pairs",
        default="oks_scraped/gold_pairs.jsonl",
        help="working-tree or repository-relative few-shot examples path",
    )
    parser.add_argument(
        "--data-path",
        action="append",
        help=(
            "repository-relative historical OKS data file; repeat the option "
            "for multiple files (defaults to test_data/**/*.data.xml)"
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="execute each translated query against the selected historical snapshot",
    )
    parser.add_argument(
        "--target-class",
        help="override the target class emitted by the translator during execution",
    )
    parser.add_argument(
        "--oks-dump-executable",
        default="oks_dump",
        help="oks_dump executable or absolute path (default: oks_dump)",
    )
    parser.add_argument(
        "--execution-timeout",
        type=float,
        default=60.0,
        help="maximum seconds allowed for one oks_dump call (default: 60)",
    )
    return parser


def build_revision_request(args):
    from translator_module.revision import RevisionRequest

    return RevisionRequest(
        commit_hash=args.commit_hash,
        tag=args.tag,
        date=args.date,
        run_id=args.run_id,
        ref=args.ref,
    )


def _is_historical_request(args) -> bool:
    return any((args.commit_hash, args.tag, args.date, args.run_id))


def _working_tree_path(root: Path, configured_path: str) -> Path:
    path = Path(configured_path).expanduser()
    return path if path.is_absolute() else root / path


def _create_translator(args, llm_api_key, llm_base_url, llm_model):
    """Create a translator and optional execution snapshot."""

    from translator_module.agent.translator import OksTranslator

    repository = Path(args.repo).expanduser().resolve()
    gold_pairs_path = _working_tree_path(repository, args.gold_pairs)

    if not _is_historical_request(args):
        schema_path = _working_tree_path(repository, args.schema_path)
        return OksTranslator(
            str(schema_path),
            str(gold_pairs_path),
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
        ), None, None

    from translator_module.revision import (
        GitRevisionResolver,
        GitRevisionSource,
        RunRevisionRegistry,
    )

    registry = None
    if args.run_id:
        if not args.run_map:
            raise ValueError("--run-id requires --run-map")
        registry = RunRevisionRegistry.from_json(args.run_map)

    resolved = GitRevisionResolver(repository, run_registry=registry).resolve(
        build_revision_request(args)
    )
    source = GitRevisionSource(repository, resolved.commit)
    if not source.exists(args.schema_path):
        raise FileNotFoundError(
            f"historical schema path is missing in {resolved.commit}: "
            f"{args.schema_path}"
        )

    translator = OksTranslator(
        schema_xml_path=None,
        gold_pairs_path=str(gold_pairs_path),
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        llm_model=llm_model,
        schema_source=source,
        schema_paths=[args.schema_path],
        revision=resolved.commit,
    )

    snapshot = None
    if args.execute:
        from translator_module.revision import SnapshotBuilder

        snapshot = SnapshotBuilder().build(
            source,
            resolved,
            schema_paths=[args.schema_path],
            data_paths=args.data_path,
        )

    return translator, resolved, snapshot


def main(argv=None):
    args = build_argument_parser().parse_args(argv)

    if args.execute and not _is_historical_request(args):
        print("Failed to initialize the translator: --execute requires a historical revision selector.")
        return 2

    # Load environment variables
    try:
        from dotenv import load_dotenv
        for env_path in (os.path.join(MODULE_DIR, '.env'), os.path.join(REPO_ROOT, '.env')):
            if os.path.isfile(env_path):
                load_dotenv(env_path, override=True)
                break
    except ImportError:
        # Fallback: manual .env parsing if python-dotenv is not installed
        for env_path in (os.path.join(MODULE_DIR, '.env'), os.path.join(REPO_ROOT, '.env')):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, val = line.split('=', 1)
                            os.environ[key.strip()] = val.strip()
                break
            except FileNotFoundError:
                continue

    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_base_url = os.environ.get("LLM_BASE_URL")
    llm_model = os.environ.get("LLM_MODEL")

    if not llm_api_key or llm_api_key == "your_api_key_here":
        print("Warning: It looks like your LLM_API_KEY is not set correctly in the .env file.")
        print("Please update it before running queries.")
        print("-" * 50)

    print("Initializing OKS Intelligent Query Agent...")

    try:
        translator, resolved_revision, snapshot = _create_translator(
            args,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
        )
    except Exception as e:
        print(f"Failed to initialize the translator: {e}")
        return 2

    if resolved_revision is not None:
        print(
            "Using historical Git revision "
            f"{resolved_revision.commit} ({resolved_revision.requested_as})."
        )
    else:
        print("Using the current working-tree schema.")

    print("Ready! Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("\nEnter your query: ")
            if query.lower().strip() in ['exit', 'quit']:
                print("Goodbye!")
                break
            if not query.strip():
                continue

            print("Thinking...")
            result = translator.translate(query)

            print("\n" + "=" * 60)
            if result.get("status") == "success":
                print("  OKS Query (copy-paste ready):")
                print(f"  {result.get('oks_query')}")
                print("-" * 60)

                explanation = result.get("explanation", "")
                if explanation:
                    print(f"\n  Explanation:\n  {explanation}")
                    print("-" * 60)

                print(f"\n  IR (Intermediate Representation):")
                ir = result.get("ir", {})
                # Print IR without the explanation field to avoid duplication
                ir_display = {k: v for k, v in ir.items() if k != "explanation"}
                print(f"  {json.dumps(ir_display, indent=2)}")

                if args.execute:
                    from translator_module.execution import (
                        HistoricalExecutionContext,
                        OksDumpExecutor,
                    )

                    target_class = args.target_class or ir.get("target_class")
                    execution_context = HistoricalExecutionContext(
                        snapshot=snapshot,
                        oks_query=result["oks_query"],
                        target_class=target_class,
                    )
                    execution_result = OksDumpExecutor(
                        executable=args.oks_dump_executable,
                        timeout=args.execution_timeout,
                    ).execute(execution_context)
                    print("-" * 60)
                    print(
                        "\n  Historical execution output "
                        f"(revision {execution_result.revision}):"
                    )
                    print(execution_result.stdout or "  (oks_dump returned no output)")
                    if execution_result.stderr:
                        print("\n  oks_dump diagnostics:")
                        print(execution_result.stderr)
            else:
                print(f"  Error: {result.get('message')}")
            print("=" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    raise SystemExit(main())
