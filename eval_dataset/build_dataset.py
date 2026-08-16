#!/usr/bin/env python3
"""
Build the two files the translation pipeline needs in order to be scored:

  eval_dataset/oks_schema_corpus.xml    the schema corpus that the RAG indexer
                                        ingests (configuration schema + object
                                        data + the OKS C++ API surface)
  eval_dataset/oks_eval_queries.jsonl   the stratified question -> OksQuery
                                        evaluation set, with gold IR, gold
                                        schema elements and expected results

Both are generated, never hand-edited, so they can be regenerated whenever
test_schema/ or test_data/ changes:

    python eval_dataset/build_dataset.py

The build fails loudly if any gold query names a class, attribute or
relationship that does not exist, or if a query that is supposed to match
something matches nothing. That check is the reason the dataset can be trusted
as ground truth.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import oks_model as M                      # noqa: E402
from query_specs import SPECS, Spec        # noqa: E402

SCHEMA_DIR = os.path.join(REPO_ROOT, "test_schema", "xml")
DATA_DIR = os.path.join(REPO_ROOT, "test_data")
CPP_API_SCHEMA = os.path.join(HERE, "oks_cpp_api.schema.xml")
LEGACY_EXAMPLES = os.path.join(REPO_ROOT, "oks_scraped", "oks_schema_examples.xml")

CORPUS_OUT = os.path.join(HERE, "oks_schema_corpus.xml")
QUERIES_OUT = os.path.join(HERE, "oks_eval_queries.jsonl")

DATASET_VERSION = "1.0"

# Human-readable grouping of the 46 configuration schema files, so each
# <example> in the corpus carries a caption a retriever can embed.
DOMAINS = {
    "core.schema.xml": "TDAQ core: partitions, segments, applications, computers, "
                       "software repositories, tags and resources. Every other schema builds on it.",
    "df.schema.xml": "Data flow: readout, event building, sub-farm input/output and the "
                     "data-collection applications.",
    "dqm.schema.xml": "Data-quality monitoring: algorithms, parameters, thresholds, "
                      "references, inputs and outputs.",
    "dqm_archive.schema.xml": "Data-quality archiving configuration.",
    "swrod.schema.xml": "Software ROD: FELIX inputs, fragment builders, event samplers "
                        "and the plugin libraries behind them.",
    "swrod_test.schema.xml": "Software ROD test configuration.",
    "alti.schema.xml": "ALTI timing/trigger module: BGo channels, cycles, deadtime, "
                       "pattern generator and TTC decoding.",
    "ltpi.schema.xml": "LTP interface module configuration.",
    "rcdltp.schema.xml": "RCD LTP module and busy handling.",
    "ttcvi.schema.xml": "TTCvi timing module configuration.",
    "hltsv.schema.xml": "High-level-trigger supervisor.",
    "HLTMPPU.schema.xml": "Multi-process HLT processing unit.",
    "dcm.schema.xml": "Data collection manager.",
    "aal.schema.xml": "ATLAS automation layer: actions, rules and agents.",
    "coca.schema.xml": "Configuration and calibration archiving.",
    "ddc.schema.xml": "DAQ/DCS communication.",
    "emon.schema.xml": "Event monitoring service.",
    "gnam.schema.xml": "GNAM monitoring framework.",
    "gnamDummyLib.schema.xml": "GNAM test library configuration.",
    "GnamSampler.schema.xml": "GNAM sampler configuration.",
    "log2ers.schema.xml": "Log-to-ERS forwarding.",
    "mda.schema.xml": "Monitoring data archiving.",
    "MonInfoGatherer.schema.xml": "Monitoring information gatherer applications and "
                                  "their match handlers.",
    "monsvc_config.schema.xml": "Monitoring service configuration.",
    "mucal.schema.xml": "Muon calibration stream.",
    "olc2hlt.schema.xml": "Online luminosity to HLT publishing.",
    "pbeast.schema.xml": "P-BEAST monitoring archive subscriptions.",
    "pudummy.schema.xml": "Dummy processing unit, used for testing.",
    "questNPSend.schema.xml": "QUEST network-processor sender.",
    "racks.schema.xml": "Rack layout.",
    "beamspotutils.schema.xml": "Beam-spot IS controller configuration.",
    "athena-mon.schema.xml": "Athena monitoring applications.",
    "siom.schema.xml": "SIOM module configuration.",
    "test-repository.schema.xml": "Test manager: tests, test policies, behaviours, "
                                  "failures and the executables that run them.",
    "RODBusy.schema.xml": "ROD busy module.",
    "ROSDescriptor.schema.xml": "Readout system descriptors.",
    "ROSTester.schema.xml": "Readout system tester.",
    "RobinNPModule.schema.xml": "RobinNP module.",
    "RobinNPDescriptorModule.schema.xml": "RobinNP descriptor module.",
    "NPDescriptor.schema.xml": "Network-processor descriptor.",
    "NP2lan.schema.xml": "Network processor to LAN bridge.",
    "PreloadedNP.schema.xml": "Preloaded network processor.",
    "EmulatedNP.schema.xml": "Emulated network processor.",
    "SuperDummyROS.schema.xml": "Dummy readout system.",
    "DFTriggerIn.schema.xml": "Data-flow trigger input.",
    "SFOng.schema.xml": "Next-generation sub-farm output.",
}

QUERY_GRAMMAR = """\
query          ::= "(" scope expr ")"
scope          ::= "this" | "all"                 ; this = class only, all = class + subclasses
expr           ::= attr_cmp | uid_cmp | rel_expr | and_expr | or_expr | not_expr
and_expr       ::= "and" expr expr+               ; two or more operands
or_expr        ::= "or"  expr expr+               ; two or more operands
not_expr       ::= "not" expr                     ; exactly one operand
attr_cmp       ::= "(" "\\"attr-name\\"" "\\"value\\"" op ")"
uid_cmp        ::= "(" "object-id" "\\"an-object-id\\"" "=" ")"
rel_expr       ::= "(" "\\"rel-name\\"" ("some"|"all") expr ")"
path_query     ::= "(" "path-to" "\\"dest-id@class\\"" path_expr ")"
path_expr      ::= "(" ("direct"|"nested") "\\"rel-name\\""+ path_expr? ")"
op             ::= "=" | "!=" | "~=" | "<" | "<=" | ">" | ">="

Notes grounded in src/query.cpp and include/oks/query.hpp:
  * the first token of a query must be 'all' or 'this'; anything else fails to parse
  * 'all' is overloaded: class scope at the top level, universal quantifier inside
    a relationship expression
  * '~=' is boost::regex_match, so the pattern must match the whole value; there is
    no glob operator
  * object-id supports '=' only
  * a value is always written as a quoted token; the attribute's declared type
    decides whether the comparison is numeric, boolean or lexicographic
  * a nested relationship expression is parsed against the relationship's
    class-type, not against the outer class
"""


# --------------------------------------------------------------------------
# File 1: the schema corpus
# --------------------------------------------------------------------------
def _indent(elem: ET.Element, level: int = 0) -> None:
    pad = "\n" + "  " * level
    if len(elem):
        if not (elem.text or "").strip():
            elem.text = pad + "  "
        for child in elem:
            _indent(child, level + 1)
        if not (elem[-1].tail or "").strip():
            elem[-1].tail = pad
    if level and not (elem.tail or "").strip():
        elem.tail = pad


def _inner_xml(path: str, root_tag: str) -> str:
    """Re-serialise a file's root element without its DOCTYPE and comments."""
    root = ET.parse(path).getroot()
    if root.tag != root_tag:
        found = root.find(f".//{root_tag}")
        if found is not None:
            root = found
    _indent(root)
    return ET.tostring(root, encoding="unicode").strip()


HEADER_COMMENT = """\
<!--
  oks_schema_corpus.xml
  =====================
  GENERATED FILE. Run `python eval_dataset/build_dataset.py` to rebuild it.

  The retrieval corpus for the translator pipeline. Each <example> carries a
  <caption> for semantic retrieval plus one or more <schema-file> / <data-file>
  blocks whose CDATA is a complete, parseable OKS document. The pipeline's
  indexer walks example/schema-file and chunks every <class>, so this file drops
  straight into HybridIndexer.ingest_xml and is a strict superset of
  oks_scraped/oks_schema_examples.xml.

  Three kinds of content:
    * configuration schema : the ATLAS TDAQ schema files under test_schema/xml
    * object data          : the objects under test_data, so object ids,
                             attribute values and references are retrievable,
                             not just class definitions
    * the OKS C++ API      : OksKernel, OksClass, OksObject, OksQuery and the
                             rest, expressed as OKS classes with <attribute>,
                             <relationship> and <method> elements, so API
                             questions are answerable from the same index

  A <query-grammar> block carries the S-expression grammar itself.
-->"""


def _cdata(text: str) -> str:
    if "]]>" in text:
        raise ValueError("embedded document contains a CDATA terminator")
    return f"<![CDATA[\n{text}\n]]>"


def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _attr(text: str) -> str:
    return _esc(text).replace('"', "&quot;")


def build_corpus(schema: M.Schema, schema_files: List[str], data_files: List[str]) -> Tuple[str, Dict[str, int]]:
    stats = {"examples": 0, "schema_files": 0, "data_files": 0, "classes": 0, "objects": 0}
    out: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        HEADER_COMMENT,
        f'<training-examples corpus="oks-schema-corpus" version="{DATASET_VERSION}" '
        f'generated-by="eval_dataset/build_dataset.py">',
    ]

    # -- grammar --------------------------------------------------------
    out.append('\n  <example id="00-query-grammar" kind="grammar">')
    out.append("    <caption>" + _esc(
        "The OKS query language itself: scope tokens, comparators, boolean operators, "
        "relationship quantifiers and path-query syntax. The BNF is reconstructed; the "
        "authoritative sources are src/query.cpp and include/oks/query.hpp, quoted in "
        "docs/OKS_Grammar_Query_CppAPI_Reference.pdf."
    ) + "</caption>")
    out.append("    <query-grammar>" + _cdata(QUERY_GRAMMAR.rstrip()) + "</query-grammar>")
    out.append("  </example>")
    stats["examples"] += 1

    # -- configuration schema, one example per file ----------------------
    for rel in schema_files:
        base = os.path.basename(rel)
        classes = [c for c in schema.classes.values() if c.source_file == rel]
        caption = DOMAINS.get(base, "ATLAS TDAQ configuration schema.")
        names = ", ".join(sorted(c.name for c in classes)[:12])
        more = "" if len(classes) <= 12 else f", and {len(classes) - 12} more"
        out.append(f'\n  <example id="schema-{base[:-len(".schema.xml")]}" '
                   f'kind="configuration-schema" source="{_attr(rel)}" classes="{len(classes)}">')
        out.append("    <caption>" + _esc(
            f"{caption} Defines {len(classes)} class(es): {names}{more}. [Source: {rel}]"
        ) + "</caption>")
        body = _inner_xml(os.path.join(REPO_ROOT, *rel.split("/")), "oks-schema")
        out.append(f'    <schema-file name="{_attr(base)}" src="{_attr(rel)}">'
                   + _cdata(body) + "</schema-file>")
        out.append("  </example>")
        stats["examples"] += 1
        stats["schema_files"] += 1
        stats["classes"] += len(classes)

    # -- the C++ API surface ---------------------------------------------
    api_classes = len(ET.parse(CPP_API_SCHEMA).getroot().findall(".//class"))
    out.append(f'\n  <example id="schema-oks-cpp-api" kind="cpp-api-schema" '
               f'source="eval_dataset/oks_cpp_api.schema.xml" classes="{api_classes}">')
    out.append("    <caption>" + _esc(
        "The public OKS C++ API expressed in the OKS schema format: OksKernel, OksFile, "
        "OksClass, OksAttribute, OksRelationship, OksMethod, OksObject, OksData, OksIndex, "
        "OksQuery and the whole expression hierarchy (OksComparator, "
        "OksRelationshipExpression, OksNotExpression, OksAndExpression, OksOrExpression), "
        "plus QueryPath, OksRepositoryVersion and the error taxonomy. C++ data members appear "
        "as attributes, associations as relationships, and every documented public method as a "
        "method element carrying its verbatim prototype. This is what makes 'which call "
        "executes a parsed query?' answerable from the same index as 'which applications run "
        "on hostA?'. [Source: docs/OKS_Grammar_Query_CppAPI_Reference.pdf]"
    ) + "</caption>")
    out.append('    <schema-file name="oks_cpp_api.schema.xml" '
               'src="eval_dataset/oks_cpp_api.schema.xml">'
               + _cdata(_inner_xml(CPP_API_SCHEMA, "oks-schema")) + "</schema-file>")
    out.append("  </example>")
    stats["examples"] += 1
    stats["schema_files"] += 1
    stats["classes"] += api_classes

    # -- object data, one example per file -------------------------------
    db_counts = _objects_per_file(data_files)
    for rel in data_files:
        base = os.path.basename(rel)
        n = db_counts.get(rel, 0)
        if n == 0:
            continue
        out.append(f'\n  <example id="data-{base[:-len(".data.xml")]}" '
                   f'kind="configuration-data" source="{_attr(rel)}" objects="{n}">')
        out.append("    <caption>" + _esc(
            f"Concrete objects from the ATLAS TDAQ test configuration: {n} object(s) in {base}. "
            f"Object ids are what an (object-id \"ID\" =) term compares against, so these blocks "
            f"ground entity resolution as well as schema retrieval. [Source: {rel}]"
        ) + "</caption>")
        body = _inner_xml(os.path.join(REPO_ROOT, *rel.split("/")), "oks-data")
        out.append(f'    <data-file name="{_attr(base)}" src="{_attr(rel)}">'
                   + _cdata(body) + "</data-file>")
        out.append("  </example>")
        stats["examples"] += 1
        stats["data_files"] += 1
        stats["objects"] += n

    # -- carry the original curated examples forward ----------------------
    if os.path.isfile(LEGACY_EXAMPLES):
        legacy_root = ET.parse(LEGACY_EXAMPLES).getroot()
        for legacy in legacy_root.findall("example"):
            out.append(f'\n  <example id="legacy-{_attr(legacy.get("id", "example"))}" '
                       f'kind="curated-example" source="oks_scraped/oks_schema_examples.xml">')
            caption = legacy.find("caption")
            if caption is not None and caption.text:
                out.append("    <caption>" + _esc(" ".join(caption.text.split())) + "</caption>")
            for tag in ("schema-file", "data-file", "note"):
                for el in legacy.findall(tag):
                    if tag == "note":
                        out.append("    <note>" + _esc((el.text or "").strip()) + "</note>")
                        continue
                    attrs = "".join(f' {k}="{_attr(v)}"' for k, v in el.attrib.items())
                    out.append(f"    <{tag}{attrs}>" + _cdata((el.text or "").strip())
                               + f"</{tag}>")
                    stats[tag.replace("-", "_") + "s"] = stats.get(
                        tag.replace("-", "_") + "s", 0) + 1
            out.append("  </example>")
            stats["examples"] += 1

    out.append("\n</training-examples>")
    return "\n".join(out) + "\n", stats


def _objects_per_file(data_files: List[str]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for rel in data_files:
        path = os.path.join(REPO_ROOT, *rel.split("/"))
        out[rel] = len(ET.parse(path).getroot().findall(".//obj"))
    return out


# --------------------------------------------------------------------------
# File 2: the evaluation query set
# --------------------------------------------------------------------------
def build_queries(schema: M.Schema, db: M.Database) -> Tuple[List[Dict[str, Any]], List[str]]:
    rows: List[Dict[str, Any]] = []
    problems: List[str] = []
    seen_questions = set()
    counters: Dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}

    for index, spec in enumerate(SPECS, start=1):
        if spec.question in seen_questions:
            problems.append(f"[{index}] duplicate question: {spec.question!r}")
        seen_questions.add(spec.question)

        if spec.difficulty not in counters:
            problems.append(f"[{index}] unknown difficulty {spec.difficulty!r}")
            continue
        counters[spec.difficulty] += 1

        if not schema.has(spec.target_class):
            problems.append(f"[{index}] unknown target class {spec.target_class!r}")
            continue

        row: Dict[str, Any] = {
            "id": f"OKSQ-{index:03d}",
            "split": "eval",
            "difficulty": spec.difficulty,
            "question": spec.question,
            "target_class": spec.target_class,
            "scope": spec.scope,
            "constructs": spec.constructs,
        }

        ir = spec.ir
        if ir is not None:
            try:
                M.validate(ir, spec.target_class, schema)
            except M.IRError as exc:
                problems.append(f"[{index}] {spec.question!r}: {exc}")
                continue
            query_oks = M.serialize(ir)
            if spec.query_oks and spec.query_oks != query_oks:
                problems.append(f"[{index}] serialiser disagrees with the literal query")
                continue
            row["query_ir"] = ir
            row["query_oks"] = query_oks
            row["gold_schema_elements"] = M.schema_elements(ir, spec.target_class, schema)
            expected = M.execute(ir, spec.target_class, db)
            if not expected and not spec.allow_empty:
                problems.append(
                    f"[{index}] {spec.question!r}: gold query matches nothing "
                    f"({query_oks} on {spec.target_class}); mark allow_empty if intended"
                )
                continue
            row["expected_object_ids"] = expected
            row["expected_count"] = len(expected)
            row["ir_expressible"] = True
        else:
            if not spec.query_oks:
                problems.append(f"[{index}] neither an IR nor a literal query was supplied")
                continue
            row["query_ir"] = None
            row["query_oks"] = spec.query_oks
            row["gold_schema_elements"] = _path_query_elements(spec, schema, problems, index)
            row["expected_object_ids"] = None
            row["expected_count"] = None
            row["ir_expressible"] = False

        row["scope_class_count"] = 1 + len(schema.all_subclasses(spec.target_class))
        row["oks_dump_cmd"] = _oks_dump_cmd(spec, row["query_oks"])
        row["note"] = spec.note
        row["source_file"] = spec.source_file
        rows.append(row)

    if counters["easy"] == 0 or counters["medium"] == 0 or counters["hard"] == 0:
        problems.append(f"all three difficulty bands must be populated: {counters}")
    return rows, problems


def _path_query_elements(spec: Spec, schema: M.Schema, problems: List[str], index: int) -> Dict[str, List[str]]:
    """Relationship names of a path query, checked hop by hop against the schema."""
    import re

    classes = [spec.target_class]
    relationships: List[str] = []
    body = spec.query_oks.split("(direct", 1)[-1] if spec.query_oks else ""
    names = re.findall(r'"([^"@]+)"', body)
    current = spec.target_class
    for name in names:
        rel = schema.find_relationship(current, name)
        if rel is None:
            problems.append(
                f"[{index}] path query hop {name!r} does not exist on {current!r}"
            )
            break
        relationships.append(f"{rel.owner}.{name}")
        if rel.owner not in classes:
            classes.append(rel.owner)
        if rel.class_type not in classes:
            classes.append(rel.class_type)
        current = rel.class_type
    dest = re.search(r'path-to\s+"[^"@]+@([^"]+)"', spec.query_oks or "")
    if dest and dest.group(1) not in classes:
        classes.append(dest.group(1))
    return {"classes": sorted(classes), "attributes": [], "relationships": sorted(relationships)}


def _oks_dump_cmd(spec: Spec, query_oks: str) -> str:
    if not spec.ir_expressible:
        return f"oks_dump --path \"@{spec.target_class}\" '{query_oks}' <data-files>"
    return f"oks_dump --class {spec.target_class} --query '{query_oks}' <data-files>"


# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate only; do not write the output files")
    args = parser.parse_args()

    print("Loading test_schema/xml and test_data ...")
    schema, db, schema_files, data_files = M.load_repository(REPO_ROOT)
    print(f"  {len(schema.classes)} classes from {len(schema_files)} schema files")
    print(f"  {len(db.objects)} objects from {len(data_files)} data files")

    rows, problems = build_queries(schema, db)
    if problems:
        print("\nDataset validation failed:")
        for p in problems:
            print(f"  - {p}")
        return 1

    corpus, stats = build_corpus(schema, schema_files, data_files)

    bands: Dict[str, int] = {}
    constructs: Dict[str, int] = {}
    for r in rows:
        bands[r["difficulty"]] = bands.get(r["difficulty"], 0) + 1
        for c in r["constructs"]:
            constructs[c] = constructs.get(c, 0) + 1

    print(f"\nCorpus:  {stats['examples']} examples, {stats['schema_files']} schema blocks "
          f"({stats['classes']} classes), {stats['data_files']} data blocks "
          f"({stats['objects']} objects)")
    print(f"Queries: {len(rows)} rows  "
          + "  ".join(f"{k}={bands.get(k, 0)}" for k in ("easy", "medium", "hard")))
    executable = [r for r in rows if r["expected_count"] is not None]
    print(f"         {len(executable)} rows carry an expected result set "
          f"(median size {_median([r['expected_count'] for r in executable])})")
    print(f"         {len(rows) - len(executable)} path-query rows are not IR-expressible")
    print("         constructs: " + ", ".join(f"{k}:{v}" for k, v in sorted(constructs.items())))

    if args.check:
        print("\n--check: nothing written.")
        return 0

    with open(CORPUS_OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(corpus)
    with open(QUERIES_OUT, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nWrote {os.path.relpath(CORPUS_OUT, REPO_ROOT)} "
          f"({os.path.getsize(CORPUS_OUT) // 1024} KiB)")
    print(f"Wrote {os.path.relpath(QUERIES_OUT, REPO_ROOT)} "
          f"({os.path.getsize(QUERIES_OUT) // 1024} KiB)")
    return 0


def _median(values: List[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


if __name__ == "__main__":
    raise SystemExit(main())
