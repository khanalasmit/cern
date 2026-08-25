"""
schema_retrieval.py — Filter #1: Schema Slice Retrieval
========================================================

Pulls ONLY the relevant OKS schema slice for a given user question.
The LLM never sees the full schema — only 1-3 classes and their
attributes/relationships.

Works with three backends (tried in order):
  1. Python ``config`` module (preferred — structured, inheritance-resolved)
  2. ``oks_dump -c <Class> <data-file>`` CLI (fallback — parsed text)
  3. Raw XML grep on schema files (class-name discovery only)
"""

import logging
import os
import re
import subprocess
import shutil
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger("oksquery_translator.schema_retrieval")


# ---------------------------------------------------------------------------
# Common synonym mapping — maps natural-language keywords to candidate
# OKS class names.  This is a *hint* layer; the canonical class list is
# always loaded from the live schema.
# ---------------------------------------------------------------------------
_KEYWORD_TO_CLASSES = {
    "application":   ["Application", "BaseApplication", "RunControlApplication"],
    "applications":  ["Application", "BaseApplication", "RunControlApplication"],
    "executable":    ["Executable", "Binary"],
    "executables":   ["Executable", "Binary"],
    "binary":        ["Binary", "Executable"],
    "computer":      ["Computer"],
    "host":          ["Computer"],
    "machine":       ["Computer"],
    "segment":       ["Segment", "OnlineSegment"],
    "partition":     ["Partition"],
    "resource":      ["Resource", "ResourceBase"],
    "timeout":       ["BaseApplication", "Executable"],
    "inittimeout":   ["BaseApplication", "Executable"],
    "exittimeout":   ["BaseApplication", "Executable"],
    "initialise":    ["BaseApplication", "Executable"],
    "initialize":    ["BaseApplication", "Executable"],
    "trigger":       ["DFTriggerIn"],
    "readout":       ["ROSDescriptor", "ReadoutApplication"],
    "ros":           ["ROSDescriptor"],
    "repository":    ["SW_Repository"],
    "software":      ["SW_Object", "ComputerProgram"],
    "program":       ["ComputerProgram"],
    "tag":           ["Tag"],
    "variable":      ["Variable", "VariableSet"],
    "parameter":     ["Parameter"],
    "rack":          ["Rack", "RackBase"],
    "test":          ["Test", "Test4Class", "Test4Object", "ExecutableTest"],
    "control":       ["RunControlApplication", "RunControlApplicationBase"],
    "controller":    ["RunControlApplication", "RunControlApplicationBase"],
    "run":           ["RunControlApplication"],
    "rc":            ["RunControlApplication", "RunControlApplicationBase"],
    "gatherer":      ["MIGApplication"],
    "monitoring":    ["MIGApplication", "MIGConfiguration"],
    "infrastructure": ["InfrastructureBase"],
    "ipc":           ["IPCServiceApplication"],
    "service":       ["IPCServiceApplication"],
    "corba":         ["IPCServiceApplication"],
    "container":     ["Container"],
    "element":       ["Element"],
    "failure":       ["TestFailure"],
}


class SchemaRetriever:
    """
    Retrieves a compact schema slice for a user question.

    On initialisation, builds and caches the full class list from the
    live TDAQ schema.  For each query, matches keywords to class names
    and returns a text block describing only the relevant classes'
    attributes and relationships.
    """

    def __init__(self, data_file: str = "daq/segments/setup.data.xml",
                 schema_dir: str = None):
        """
        Parameters
        ----------
        data_file : str
            OKS data file path (repo-relative or absolute).  Used for
            ``config.Configuration`` and ``oks_dump`` calls.
        schema_dir : str, optional
            Absolute path to the directory containing ``*.schema.xml``
            files.  Auto-detected from the TDAQ release if omitted.
        """
        self.data_file = data_file
        self.schema_dir = schema_dir or self._detect_schema_dir()
        self._class_list: Optional[List[str]] = None
        self._class_cache: Dict[str, dict] = {}
        # Cache negative lookups too.  The schema index may ask for the same
        # unavailable class twice (directly and through inheritance).
        self._missing_classes: set[str] = set()
        self._config_available = self._check_config_available()
        self._oks_dump_path = shutil.which("oks_dump")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def environment_probe(self) -> dict:
        """
        Step 1 from breif.md: Confirm the release path exists and
        oks_dump runs.  Build a list of all class names by scanning
        the schema files.

        Returns a dict with environment status and class count.
        """
        logger.info(
            "Schema probe: data_file=%r schema_dir=%r config_module=%s oks_dump=%r",
            self.data_file, self.schema_dir, self._config_available, self._oks_dump_path,
        )
        probe = {
            "oks_dump": self._oks_dump_path or "NOT FOUND",
            "config_module": "available" if self._config_available else "NOT available",
            "schema_dir": self.schema_dir or "NOT FOUND",
            "data_file": self.data_file,
            "class_count": 0,
            "classes": [],
        }

        # Probe: can we actually run oks_dump?
        if self._oks_dump_path:
            try:
                result = subprocess.run(
                    [self._oks_dump_path, "-f", self.data_file],
                    capture_output=True, text=True, timeout=15
                )
                probe["oks_dump_status"] = (
                    "OK" if result.returncode == 0
                    else f"exit {result.returncode}: {result.stderr.strip()[:200]}"
                )
            except Exception as e:
                probe["oks_dump_status"] = f"error: {e}"

        # Load classes
        classes = self.get_class_list()
        probe["class_count"] = len(classes)
        probe["classes"] = classes[:20]  # first 20 for display
        logger.info("Schema probe complete: %d classes discovered", len(classes))

        return probe

    def get_class_list(self) -> List[str]:
        """
        Return the cached list of all class names in the schema.

        Uses real runtime commands (db.classes(), oks_dump -f, grep)
        to discover classes from the live TDAQ environment.
        """
        if self._class_list is None:
            logger.info("Schema class list cache miss; discovering classes")
            self._class_list = self._load_class_list()
        else:
            logger.debug("Schema class list cache hit: %d classes", len(self._class_list))
        return self._class_list

    def get_class_info(self, class_name: str) -> Optional[dict]:
        """
        Return structured info for a class (attributes, relationships,
        superclasses).  Result is cached.

        Returns ``None`` if the class doesn't exist.
        """
        if class_name in self._class_cache:
            logger.debug("Schema class cache hit: %s", class_name)
            return self._class_cache[class_name]
        if class_name in self._missing_classes:
            logger.debug("Schema class negative-cache hit: %s", class_name)
            return None

        logger.debug("Loading schema details for class: %s", class_name)
        info = self._load_class_info(class_name)
        if info is not None:
            self._class_cache[class_name] = info
            logger.debug(
                "Loaded %s: %d attributes, %d relationships, %d superclasses",
                class_name, len(info.get("attributes", [])),
                len(info.get("relationships", [])), len(info.get("superclasses", [])),
            )
        else:
            self._missing_classes.add(class_name)
            logger.debug("Could not load schema details for class: %s", class_name)
        return info

    def get_schema_context(self, question: str, max_classes: int = 3) -> str:
        """
        Given a natural-language question, identify the relevant class(es)
        and return a formatted schema slice for prompt injection.
        """
        candidate_classes = self._match_classes(question, max_classes)
        logger.info("Schema slice: question=%r candidates=%s", question, candidate_classes)
        if not candidate_classes:
            return ("--- Relevant OKS Schema Context ---\n"
                    "No relevant classes could be identified from the question.\n"
                    "Available classes: " + ", ".join(self.get_class_list()[:30]) +
                    " ... (and more)\n---\n")

        context = "--- Relevant OKS Schema Context ---\n"
        for cls_name in candidate_classes:
            info = self.get_class_info(cls_name)
            if info is None:
                context += f"Class: {cls_name} (could not load details)\n---\n"
                continue
            context += self._format_class_info(info) + "---\n"

        return context

    # ------------------------------------------------------------------
    # Class matching
    # ------------------------------------------------------------------

    def _match_classes(self, question: str, max_classes: int) -> List[str]:
        """
        Match a user question to candidate OKS class names.

        PRIMARY STRATEGY: Match question tokens against the REAL class
        list loaded from the live schema (via db.classes() / oks_dump /
        grep).  This is the approach from breif.md Step 2.

        SECONDARY BOOST: Keyword synonym lookup for common terms like
        "host" → Computer, "control" → RunControlApplication.

        TERTIARY: Attribute-name scanning — if a question mentions a
        specific attribute name (e.g. "timeout"), find which classes
        actually HAVE that attribute by inspecting the live schema.

        Strategy order:
          1. Exact / substring match against real class names
          2. Keyword synonym boost
          3. Attribute-name scanning on matched + candidate classes
          4. Expand via relationships (if a match points to another class)
          5. Deduplicate and cap at max_classes
        """
        all_classes = self.get_class_list()
        question_lower = question.lower()
        tokens = set(re.findall(r'[a-zA-Z_]+', question_lower))

        candidates = []
        scored: Dict[str, int] = {}  # class → relevance score

        # ----------------------------------------------------------
        # 1. PRIMARY: Match tokens against real class names
        #    The class list comes from db.classes() / oks_dump / grep
        #    on the live schema — NOT from a hardcoded list.
        # ----------------------------------------------------------
        for cls in all_classes:
            cls_lower = cls.lower()
            # Split CamelCase into words for matching
            cls_words = set(w.lower() for w in re.findall(r'[A-Z][a-z]+|[a-z]+', cls))
            cls_words.add(cls_lower)

            for token in tokens:
                if len(token) < 2:
                    continue
                # Exact class name match (highest priority)
                if token == cls_lower:
                    scored[cls] = scored.get(cls, 0) + 10
                # Token is a substring of the class name
                elif len(token) >= 3 and token in cls_lower:
                    scored[cls] = scored.get(cls, 0) + 5
                # Token matches a CamelCase word in the class name
                elif token in cls_words:
                    scored[cls] = scored.get(cls, 0) + 7

        # ----------------------------------------------------------
        # 2. SECONDARY: Keyword synonym boost
        #    Supplementary hints for common NL terms that don't
        #    directly match class names.
        # ----------------------------------------------------------
        for token in tokens:
            if token in _KEYWORD_TO_CLASSES:
                for cls in _KEYWORD_TO_CLASSES[token]:
                    if cls in all_classes:
                        scored[cls] = scored.get(cls, 0) + 3

        # ----------------------------------------------------------
        # 3. TERTIARY: Attribute-name scanning
        #    If the question mentions a term that looks like an
        #    attribute name (e.g. "timeout", "name", "host"),
        #    inspect the top candidate classes' actual attributes
        #    to verify they have it — and scan a few more classes
        #    if the top candidates don't.
        # ----------------------------------------------------------
        # Attribute-like tokens (longer, possibly compound)
        attr_tokens = {t for t in tokens if len(t) >= 4}
        if attr_tokens:
            # Check the top candidates first
            top_candidates = sorted(scored, key=scored.get, reverse=True)[:5]
            for cls in top_candidates:
                info = self.get_class_info(cls)
                if not info:
                    continue
                for attr in info.get("attributes", []):
                    attr_lower = attr["name"].lower()
                    for token in attr_tokens:
                        if token in attr_lower:
                            scored[cls] = scored.get(cls, 0) + 4

        # ----------------------------------------------------------
        # 4. Sort by score and pick top candidates
        # ----------------------------------------------------------
        sorted_classes = sorted(scored, key=scored.get, reverse=True)
        candidates = sorted_classes[:max_classes]

        # ----------------------------------------------------------
        # 5. Expand via relationships
        #    If a matched class has relationships pointing to other
        #    classes, include those too (up to max_classes).
        # ----------------------------------------------------------
        expanded = list(candidates)
        for cls_name in candidates:
            info = self.get_class_info(cls_name)
            if info and len(expanded) < max_classes:
                for rel in info.get("relationships", []):
                    target = rel.get("target_class")
                    if target and target in all_classes and target not in expanded:
                        expanded.append(target)
                        if len(expanded) >= max_classes:
                            break

        selected = expanded[:max_classes]
        logger.debug(
            "Schema matching: tokens=%s scored=%s selected=%s",
            sorted(tokens),
            [(name, scored[name]) for name in sorted(scored, key=scored.get, reverse=True)[:10]],
            selected,
        )
        return selected

    # ------------------------------------------------------------------
    # Class list loading
    # ------------------------------------------------------------------

    def _load_class_list(self) -> List[str]:
        """Load the list of all class names from the schema."""
        # Strategy 1: Python config module
        if self._config_available:
            try:
                logger.debug("Class discovery backend: Python config module")
                import config as oks_config
                db = None
                last_err = None
                for prefix in ("oksconfig:", "oksconflibs:"):
                    try:
                        db = oks_config.Configuration(f"{prefix}{self.data_file}")
                        break
                    except Exception as e:
                        last_err = e
                        continue
                if db is None:
                    raise last_err or RuntimeError(f"Could not open {self.data_file}")
                classes = sorted(db.classes())
                if classes:
                    logger.info("Class discovery succeeded via config module: %d classes", len(classes))
                    return classes
            except Exception as exc:
                logger.debug("Class discovery via config module failed: %s", exc)

        # Strategy 2: grep schema XML files
        if self.schema_dir and os.path.isdir(self.schema_dir):
            logger.debug("Class discovery backend: schema XML (%s)", self.schema_dir)
            classes = self._grep_class_names(self.schema_dir)
            logger.info("Class discovery via schema XML: %d classes", len(classes))
            return classes

        # Strategy 3: oks_dump (list classes from a data file)
        if self._oks_dump_path:
            try:
                logger.debug("Class discovery backend: oks_dump (%s)", self._oks_dump_path)
                result = subprocess.run(
                    [self._oks_dump_path, self.data_file],
                    capture_output=True, text=True, timeout=30
                )
                # Parse class names from oks_dump output
                classes = set()
                for line in result.stdout.splitlines():
                    m = re.match(r'^Class\s+"([^"]+)"', line)
                    if m:
                        classes.add(m.group(1))
                if classes:
                    logger.info("Class discovery via oks_dump: %d classes", len(classes))
                    return sorted(classes)
            except Exception as exc:
                logger.debug("Class discovery via oks_dump failed: %s", exc)

        logger.warning("No schema class-discovery backend returned any classes")
        return []

    def _grep_class_names(self, schema_dir: str) -> List[str]:
        """Extract class names from *.schema.xml files via text parsing."""
        classes = set()
        for fname in os.listdir(schema_dir):
            if not fname.endswith(".schema.xml"):
                continue
            fpath = os.path.join(schema_dir, fname)
            try:
                tree = ET.parse(fpath)
                for cls_elem in tree.iter("class"):
                    name = cls_elem.get("name")
                    if name:
                        classes.add(name)
            except ET.ParseError:
                # Fallback: regex on raw text
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()
                    for m in re.finditer(r'<class\s+name="([^"]+)"', text):
                        classes.add(m.group(1))
                except Exception:
                    pass
        return sorted(classes)

    # ------------------------------------------------------------------
    # Class info loading
    # ------------------------------------------------------------------

    def _load_class_info(self, class_name: str) -> Optional[dict]:
        """Load attributes, relationships, superclasses for a class."""
        # XML is authoritative when present: it carries superclass links that
        # some config-module builds omit, which otherwise leaves valid
        # inherited members out of the LLM/validator schema context.
        if self.schema_dir:
            try:
                logger.debug("Schema details backend for %s: schema XML", class_name)
                info = self._load_class_info_xml(class_name)
                if info is not None:
                    return info
            except Exception as exc:
                logger.debug("Schema details via XML failed for %s: %s", class_name, exc)

        # Strategy 1: Python config module
        if self._config_available:
            try:
                logger.debug("Schema details backend for %s: Python config module", class_name)
                info = self._load_class_info_config(class_name)
                if info is not None:
                    return info
                logger.debug("Config module has no details for %s; trying fallback backends", class_name)
            except Exception as exc:
                logger.debug("Schema details via config module failed for %s: %s", class_name, exc)

        # Strategy 2: oks_dump
        if self._oks_dump_path:
            try:
                logger.debug("Schema details backend for %s: oks_dump", class_name)
                info = self._load_class_info_oks_dump(class_name)
                if info is not None:
                    return info
                logger.debug("oks_dump has no details for %s; trying XML fallback", class_name)
            except Exception as exc:
                logger.debug("Schema details via oks_dump failed for %s: %s", class_name, exc)

        # Strategy 3: XML parsing (only if the earlier XML attempt could not
        # load the class, e.g. a schema directory appeared later at runtime).
        if self.schema_dir:
            try:
                logger.debug("Schema details backend for %s: schema XML", class_name)
                return self._load_class_info_xml(class_name)
            except Exception as exc:
                logger.debug("Schema details via XML failed for %s: %s", class_name, exc)

        return None

    def _load_class_info_config(self, class_name: str) -> Optional[dict]:
        """Load class info via the Python config module."""
        import config as oks_config
        db = None
        last_err = None
        for prefix in ("oksconfig:", "oksconflibs:"):
            try:
                db = oks_config.Configuration(f"{prefix}{self.data_file}")
                break
            except Exception as e:
                last_err = e
                continue
        if db is None:
            raise last_err or RuntimeError(f"Could not open {self.data_file}")

        if class_name not in db.classes():
            return None

        attrs_raw = db.attributes(class_name)
        rels_raw = db.relations(class_name)

        # db.attributes() returns list of dicts/tuples depending on version
        attributes = []
        if isinstance(attrs_raw, dict):
            for aname, ainfo in attrs_raw.items():
                attributes.append({
                    "name": aname,
                    "type": str(ainfo.get("type", "")),
                    "range": str(ainfo.get("range", "")),
                    "init_value": str(ainfo.get("init-value", "")),
                    "is_multi_value": str(ainfo.get("is-multi-value", "no")),
                })
        elif isinstance(attrs_raw, (list, tuple)):
            for a in attrs_raw:
                if isinstance(a, dict):
                    attributes.append({
                        "name": a.get("name", ""),
                        "type": str(a.get("type", "")),
                        "range": str(a.get("range", "")),
                        "init_value": str(a.get("init-value", "")),
                        "is_multi_value": str(a.get("is-multi-value", "no")),
                    })
                elif isinstance(a, str):
                    attributes.append({"name": a, "type": "", "range": "",
                                       "init_value": "", "is_multi_value": "no"})

        relationships = []
        if isinstance(rels_raw, dict):
            for rname, rinfo in rels_raw.items():
                target = rinfo.get("class-type", "") if isinstance(rinfo, dict) else str(rinfo)
                relationships.append({"name": rname, "target_class": target})
        elif isinstance(rels_raw, (list, tuple)):
            for r in rels_raw:
                if isinstance(r, dict):
                    relationships.append({
                        "name": r.get("name", ""),
                        "target_class": r.get("class-type", ""),
                    })
                elif isinstance(r, str):
                    relationships.append({"name": r, "target_class": ""})

        return {
            "name": class_name,
            "superclasses": [],  # config module may not expose this directly
            "attributes": attributes,
            "relationships": relationships,
        }

    def _load_class_info_oks_dump(self, class_name: str) -> Optional[dict]:
        """Load class info by parsing oks_dump -c output."""
        result = subprocess.run(
            [self._oks_dump_path, "-c", class_name, self.data_file],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 4:  # class not found
            return None
        if result.returncode != 0:
            return None

        return self._parse_oks_dump_class_output(class_name, result.stdout)

    def _parse_oks_dump_class_output(self, class_name: str,
                                      output: str) -> dict:
        """Parse the text output of oks_dump -c <class> to extract schema."""
        attributes = []
        relationships = []
        superclasses = []

        lines = output.splitlines()
        section = None  # "attributes", "relationships", "superclasses"

        for line in lines:
            stripped = line.strip()

            # Detect section headers
            if "Attribute" in stripped and "name:" in stripped:
                # Single-line attribute: Attribute name:"X" type:"Y" ...
                m_name = re.search(r'name:"([^"]+)"', stripped)
                m_type = re.search(r'type:"([^"]+)"', stripped)
                m_range = re.search(r'range:"([^"]*)"', stripped)
                m_init = re.search(r'init-value:"([^"]*)"', stripped)
                m_multi = re.search(r'is-multi-value:"([^"]*)"', stripped)
                if m_name:
                    attributes.append({
                        "name": m_name.group(1),
                        "type": m_type.group(1) if m_type else "",
                        "range": m_range.group(1) if m_range else "",
                        "init_value": m_init.group(1) if m_init else "",
                        "is_multi_value": m_multi.group(1) if m_multi else "no",
                    })
            elif "Relationship" in stripped and "name:" in stripped:
                m_name = re.search(r'name:"([^"]+)"', stripped)
                m_target = re.search(r'class-type:"([^"]+)"', stripped)
                if m_name:
                    relationships.append({
                        "name": m_name.group(1),
                        "target_class": m_target.group(1) if m_target else "",
                    })
            elif "Superclass" in stripped:
                m = re.search(r'"([^"]+)"', stripped)
                if m:
                    superclasses.append(m.group(1))

        return {
            "name": class_name,
            "superclasses": superclasses,
            "attributes": attributes,
            "relationships": relationships,
        }

    def _load_class_info_xml(self, class_name: str) -> Optional[dict]:
        """Load class info by parsing *.schema.xml files directly."""
        if not self.schema_dir or not os.path.isdir(self.schema_dir):
            return None

        for fname in os.listdir(self.schema_dir):
            if not fname.endswith(".schema.xml"):
                continue
            fpath = os.path.join(self.schema_dir, fname)
            try:
                tree = ET.parse(fpath)
                for cls_elem in tree.iter("class"):
                    if cls_elem.get("name") != class_name:
                        continue

                    superclasses = [sc.get("name") for sc in cls_elem.findall(".//superclass")
                                    if sc.get("name")]
                    attributes = []
                    for a in cls_elem.findall(".//attribute"):
                        attributes.append({
                            "name": a.get("name", ""),
                            "type": a.get("type", ""),
                            "range": a.get("range", ""),
                            "init_value": a.get("init-value", ""),
                            "is_multi_value": a.get("is-multi-value", "no"),
                        })
                    relationships = []
                    for r in cls_elem.findall(".//relationship"):
                        relationships.append({
                            "name": r.get("name", ""),
                            "target_class": r.get("class-type", ""),
                        })

                    # Resolve inherited attributes/relationships from superclasses
                    for parent_name in superclasses:
                        parent_info = self._load_class_info_xml(parent_name)
                        if parent_info:
                            attributes.extend(parent_info.get("attributes", []))
                            relationships.extend(parent_info.get("relationships", []))

                    return {
                        "name": class_name,
                        "superclasses": superclasses,
                        "attributes": attributes,
                        "relationships": relationships,
                    }
            except ET.ParseError:
                continue

        return None

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format_class_info(info: dict) -> str:
        """Format a class info dict into a human-readable text block."""
        lines = [f"Class: {info['name']}"]
        if info.get("superclasses"):
            lines.append(f"Superclasses: {', '.join(info['superclasses'])}")

        if info.get("attributes"):
            lines.append("Attributes:")
            # Deduplicate by name
            seen = set()
            for attr in info["attributes"]:
                aname = attr["name"]
                if aname in seen:
                    continue
                seen.add(aname)
                parts = [aname]
                if attr.get("type"):
                    parts.append(f"type: {attr['type']}")
                if attr.get("range"):
                    parts.append(f"range: {attr['range']}")
                if attr.get("init_value"):
                    parts.append(f"init-value: {attr['init_value']}")
                if attr.get("is_multi_value") == "yes":
                    parts.append("multi-value: yes")
                lines.append(f"  - {parts[0]} ({', '.join(parts[1:])})" if len(parts) > 1
                             else f"  - {parts[0]}")

        if info.get("relationships"):
            lines.append("Relationships:")
            seen = set()
            for rel in info["relationships"]:
                rname = rel["name"]
                if rname in seen:
                    continue
                seen.add(rname)
                target = rel.get("target_class", "")
                lines.append(f"  - {rname} → {target}" if target else f"  - {rname}")

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # Environment detection
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_schema_dir() -> Optional[str]:
        """
        Auto-detect the schema directory from the TDAQ environment.
        Looks for oks_dump on PATH, then walks up to find the schema dir.
        """
        oks_dump = shutil.which("oks_dump")
        if oks_dump:
            # Typical path: .../installed/bin/oks_dump
            # Schema is at: .../installed/share/data/daq/schema/
            installed_dir = os.path.dirname(os.path.dirname(oks_dump))
            schema_dir = os.path.join(installed_dir, "share", "data", "daq", "schema")
            if os.path.isdir(schema_dir):
                return schema_dir

        # Try well-known CVMFS paths
        for release in ["tdaq-14-00-00", "tdaq-13-00-00"]:
            path = (f"/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/{release}"
                    f"/installed/share/data/daq/schema")
            if os.path.isdir(path):
                return path

        return None

    @staticmethod
    def _check_config_available() -> bool:
        """Check if the TDAQ Python config module is importable."""
        try:
            import config  # noqa: F401
            return True
        except ImportError:
            return False
