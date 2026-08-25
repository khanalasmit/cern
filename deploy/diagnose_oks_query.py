#!/usr/bin/env python3
"""Diagnose an OKS query directly on the TDAQ host.

This deliberately bypasses the LLM, MCP transport, and agent UI.  It answers
the most useful first question when an agent reports zero matches: does the
selected OKS data file contain the requested object/attribute at all?
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

# When this file is invoked as ``python deploy/diagnose_oks_query.py``, Python
# places ``deploy/`` rather than the repository root on sys.path.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from oksquery_translator.executor import Executor


DEFAULT_CLASSES = (
    "Application",
    "BaseApplication",
    "RunControlApplication",
    "RunControlApplicationBase",
    "IPCServiceApplication",
    "ReadoutApplication",
    "Executable",
)


def _configuration_db(data_file: str):
    """Open the live config binding, if either supported prefix works."""
    try:
        import config
    except ImportError:
        return None

    for prefix in ("oksconfig:", "oksconflibs:"):
        try:
            return config.Configuration(f"{prefix}{data_file}")
        except Exception:
            continue
    return None


def _configuration_classes(data_file: str) -> List[str]:
    """Try to discover live class names without requiring an LLM."""
    db = _configuration_db(data_file)
    if db is None:
        return []
    try:
        return sorted(str(name) for name in db.classes())
    except Exception:
        return []


def _configuration_scan(
    data_file: str,
    classes: Iterable[str],
    object_query: str,
    attribute_query: str,
):
    """Scan all classes in one config process instead of spawning 2N tools."""
    db = _configuration_db(data_file)
    if db is None:
        return None

    object_matches = []
    attribute_matches = []
    attribute_errors = []
    for class_name in classes:
        try:
            for obj in list(db.get_objs(class_name, object_query)):
                object_matches.append((class_name, obj.UID()))
        except Exception:
            # object-id is universal, but an unusual class proxy should not
            # prevent the remaining classes from being checked.
            continue

        try:
            for obj in list(db.get_objs(class_name, attribute_query)):
                attribute_matches.append((class_name, obj.UID()))
        except Exception as exc:
            attribute_errors.append((class_name, str(exc)))

    return object_matches, attribute_matches, attribute_errors


def _run_probe(
    oks_dump: str,
    class_name: str,
    query: str,
    data_file: str,
    timeout: int,
) -> tuple[int, str, str, list[dict]]:
    command = [oks_dump, "-c", class_name, "-q", query, data_file]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return 124, "timeout", "oks_dump timed out", []
    except OSError as exc:
        return 127, "start_error", str(exc), []

    objects = Executor._parse_oks_dump_output(completed.stdout, class_name)
    if completed.returncode in (0, 5):
        status = "match" if objects else "valid_query_no_match"
    elif completed.returncode in (3, 4):
        status = "query_or_class_error"
    else:
        status = "execution_error"
    detail = completed.stderr.strip()
    return completed.returncode, status, detail, objects


def _print_probe(
    label: str,
    oks_dump: str,
    class_name: str,
    query: str,
    data_file: str,
    timeout: int,
) -> bool:
    return_code, status, detail, objects = _run_probe(
        oks_dump, class_name, query, data_file, timeout
    )
    print(f"[{label}] class={class_name}")
    print(f"query: {query}")
    print(f"exit_code: {return_code}")
    print(f"status: {status}")
    if detail:
        print(f"stderr: {detail[:800]}")
    print(f"match_count: {len(objects)}")
    for obj in objects[:20]:
        print(f"id: {obj.get('id')}")
        for key, value in obj.get("attributes", {}).items():
            print(f"  {key}: {value}")
    print()
    return bool(objects)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether an OKS object or attribute exists in the selected data file."
    )
    parser.add_argument(
        "--data-file",
        default=os.environ.get("OKS_DATA_FILE", "daq/segments/setup.data.xml"),
        help="Approved OKS data file (default: OKS_DATA_FILE or setup.data.xml)",
    )
    parser.add_argument(
        "--object-id",
        default="rc_trigger_1",
        help="Exact object ID to find (default: rc_trigger_1)",
    )
    parser.add_argument(
        "--attribute",
        default="Name",
        help="Attribute to test for exact equality (default: Name)",
    )
    parser.add_argument(
        "--value",
        default=None,
        help="Attribute value; defaults to --object-id",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        default=list(DEFAULT_CLASSES),
        help="Candidate classes to probe",
    )
    parser.add_argument(
        "--all-classes",
        action="store_true",
        help="Discover classes with config and probe every discovered class",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Timeout per native oks_dump probe in seconds",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    oks_dump = shutil.which("oks_dump")
    if not oks_dump:
        print("ERROR: oks_dump is not on PATH. Source the TDAQ setup.sh first.", file=sys.stderr)
        return 2
    if args.timeout < 1:
        print("ERROR: --timeout must be positive", file=sys.stderr)
        return 2

    data_file = args.data_file
    value = args.value if args.value is not None else args.object_id
    classes: Iterable[str] = args.classes
    if args.all_classes:
        discovered = _configuration_classes(data_file)
        if discovered:
            classes = discovered
        else:
            print(
                "WARNING: config could not discover all classes; using candidate classes.",
                file=sys.stderr,
            )

    classes = sorted(set(classes))
    print("=== OKS diagnostic (no LLM and no MCP transport) ===")
    print(f"data_file: {data_file}")
    print(f"oks_dump: {oks_dump}")
    print(f"TDAQ_DB_PATH: {os.environ.get('TDAQ_DB_PATH', '<unset>')}")
    print(f"TDAQ_DB_VERSION: {os.environ.get('TDAQ_DB_VERSION', '<unset>')}")
    print(f"candidate_class_count: {len(classes)}")
    print(f"object_id: {args.object_id}")
    print(f"attribute: {args.attribute}")
    print(f"attribute_value: {value}")
    print()

    object_query = f'(all (object-id "{args.object_id}" =))'
    attribute_query = f'(all ("{args.attribute}" "{value}" =))'
    object_matches = 0
    attribute_matches = 0
    attribute_errors = 0

    if args.all_classes:
        config_scan = _configuration_scan(
            data_file, classes, object_query, attribute_query
        )
        if config_scan is not None:
            object_rows, attribute_rows, attribute_error_rows = config_scan
            print("[all-class scan] backend=config (single process)")
            print(f"object_id_matches: {len(object_rows)}")
            for class_name, object_id in object_rows:
                print(f"  {class_name}: {object_id}")
            print(f"attribute_matches: {len(attribute_rows)}")
            for class_name, object_id in attribute_rows:
                print(f"  {class_name}: {object_id}")
            print(f"attribute_query_errors: {len(attribute_error_rows)}")
            for class_name, detail in attribute_error_rows[:10]:
                print(f"  {class_name}: {detail[:500]}")
            print()

            # Use native oks_dump only for confirmed matches so the output has
            # the same attributes an MCP response would expose.
            for class_name in sorted({row[0] for row in object_rows}):
                _print_probe(
                    "native object-id match",
                    oks_dump,
                    class_name,
                    object_query,
                    data_file,
                    args.timeout,
                )
            for class_name in sorted({row[0] for row in attribute_rows}):
                _print_probe(
                    "native attribute match",
                    oks_dump,
                    class_name,
                    attribute_query,
                    data_file,
                    args.timeout,
                )

            print("=== Conclusion ===")
            print(f"classes_with_object_id_match: {len({row[0] for row in object_rows})}")
            print(f"attribute_match_count: {len(attribute_rows)}")
            print(f"attribute_query_errors: {len(attribute_error_rows)}")
            if not object_rows and not attribute_rows:
                print(
                    "No matching record was found in the selected data file/version. "
                    "This is a valid empty-data result, not an MCP transport failure."
                )
            if attribute_error_rows:
                print(
                    "The attribute predicate is not valid for at least some live "
                    "classes. A tutorial/few-shot Name example may not apply here."
                )
            return 0

    for class_name in classes:
        if _print_probe(
            "object-id exact", oks_dump, class_name, object_query, data_file, args.timeout
        ):
            object_matches += 1

        return_code, status, detail, objects = _run_probe(
            oks_dump, class_name, attribute_query, data_file, args.timeout
        )
        if objects:
            attribute_matches += len(objects)
            print(f"[attribute exact] class={class_name}")
            print(f"query: {attribute_query}")
            print(f"exit_code: {return_code}")
            print(f"status: {status}")
            print(f"match_count: {len(objects)}")
            for obj in objects[:20]:
                print(f"id: {obj.get('id')}")
            print()
        elif return_code in (3, 4):
            attribute_errors += 1
            print(f"[attribute exact] class={class_name}")
            print(f"query: {attribute_query}")
            print(f"exit_code: {return_code}")
            print(f"status: {status}")
            print(f"stderr: {detail[:800]}")
            print()

    print("=== Conclusion ===")
    print(f"classes_with_object_id_match: {object_matches}")
    print(f"attribute_match_count: {attribute_matches}")
    print(f"attribute_query_errors: {attribute_errors}")
    if object_matches == 0 and attribute_matches == 0:
        print(
            "No matching record was found in the selected data file/version "
            "among the probed classes. This is a valid empty-data result, "
            "not evidence that the MCP transport failed."
        )
    elif object_matches > 0:
        print(
            "The exact object exists. Prefer object-id equality when the user "
            "names an OKS object and the live schema has no Name attribute."
        )
    if attribute_errors:
        print(
            "At least one class rejected the Name predicate. Compare the "
            "stderr with the live schema; a few-shot/tutorial Name example "
            "may not apply to this release/class."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
