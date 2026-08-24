# Renderer for 02-dune-dal.md: embeds full verbatim content of DUNE-DAQ/dal files.
# -*- coding: utf-8 -*-
import io, os

REPO = r"repo\dune-dal"
OUT = r"output\02-dune-dal.md"

def read(p):
    with io.open(os.path.join(REPO, p), "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()

def block(path, title=None, lang="cpp"):
    body = read(path)
    name = title if title else path
    return f"### `{name}`  \n*Local path: `repo/dune-dal/{path}`*\n\n```{lang}\n{body.rstrip(chr(10))}\n```\n\n"

def section(header):
    return f"\n## {header}\n\n"

parts = []

parts.append(section("Provenance"))
parts.append("""- **Source URL:** https://github.com/DUNE-DAQ/dal (branch `develop`)
- **Local mirror:** `repo/dune-dal/` (git clone, depth 1)
- **HEAD commit:** `6b0ba51b9f093e14f9878edf0ff884279cc7a087` (2024-07-17 10:30:51 -0500, "JCF: fix ambiguous line in tutorial")
- **Caption:** The DUNE DAQ `dal` (Data Access Library) package: the DUNE DAQ release of the OKS configuration system. It provides generated DAL classes (off the ATLAS `core` schema), algorithms, command-line tools, and Python bindings on top of `conffwk`/`okssystem`. This is the package the ReadTheDocs page `dune-daq-sw.readthedocs.io/en/latest/packages/dal/` documents.
- **Relationship to the task topic (GIT/version/hash):** the OKS/GIT version of a running partition's configuration is published via the Information Service and read back by `dal_get_config_version`; `get_config_version()` reads the `TDAQ_DB_VERSION` environment variable (set by `Partition::get_DBVersion()`, the DB version attribute of the `Partition` OKS class); `ConfigVersion` (an ISInfo class) carries the "OKS GIT SHA key used for given partition".

## Documentation

""")

parts.append(block("docs/README.md", "docs/README.md — \"An Introduction to OKS\"", "markdown"))
parts.append(block("docs/RELEASE_NOTES.md", "docs/RELEASE_NOTES.md", "markdown"))
parts.append("""> The `docs/Twiki.txt` file below is the original ATLAS TDAQ Twiki on the DAL package (DUNE header comment: "the following is the original ATLAS TDAQ Twiki; it is not guaranteed to be applicable to the DUNE DAQ refactor of this repository"). Its Basic Concepts section describes Partition/Segment/Application DAL classes, and it lists the `dal_get_config_version`/`dal_set_config_version` tools in the context of the OKS GIT-based configuration versioning (see "Config versioning" within). Full byte-content is preserved below.
""")
parts.append(block("docs/Twiki.txt", "docs/Twiki.txt (51 KB, original ATLAS TDAQ Twiki)", "text"))

parts.append(section("Include headers"))
parts.append(block("include/dal/ConfigVersion.hpp"))
parts.append(block("include/dal/util.hpp"))
parts.append(block("include/dal/app-config.hpp"))
parts.append(block("include/dal/seg-config.hpp"))
parts.append(block("include/dal/disabled-components.hpp"))
parts.append(block("include/dal/application-config.hpp"))

parts.append(section("Command-line tools (apps)"))
parts.append(block("apps/dal_get_config_version.cxx"))
parts.append(block("apps/dal_set_config_version.cxx"))
parts.append(block("src/exit_status.hpp"))
parts.append("""> Other apps in the repo (`dal_dump_apps.cxx`, `dal_dump_app_config.cxx`, `dal_dump_app_depends.cxx`, `dal_get_app_env.cxx`, `dal_print_hosts.cxx`, `dal_print_segments.cxx`, `dal_test_disabled.cxx`, `dal_test_get_config.cxx`, `dal_test_rw.cxx`, `dal_test_timeouts.cxx`, `dal_dump_apps_mt.cxx`) share the same style: Boost program_options parsing of `-p <partition>`, then calls into the `dunedaq::dal` algorithms. They are registered in `CMakeLists.txt` (below). `dal_test_rw.cxx` also exercises the OKS GIT interface: it clones/pulls the configuration git repository and reads the version with `dal::get_config_version` (`TDAQ_DB_VERSION` env var / `Partition::get_DBVersion()`). Their sources are preserved in the local clone (`repo/dune-dal/apps/`) and are available on GitHub; the two config-version tools plus `exit_status.hpp` are reproduced in full above because they are the topic-relevant ones.
""")

parts.append(section("Schemas (XML, DTD + classes)"))
parts.append(block("schema/dal/tutorial.schema.xml", lang="xml"))
parts.append("""> `core.schema.xml` is the DUNE copy of the ATLAS `core` schema — the full class hierarchy (83 KB). It is reproduced in full below (the renderer embeds its byte content); its header DTD is identical to the one in `tutorial.schema.xml` above. It declares classes such as `Partition`, `Segment`, `OnlineSegment`, `Computer`, `Application`, `RunControlApplication`, `Binary`, `SW_Repository`, `Tag`, `Variable` with Attributes, Relationships, and Methods (e.g. the `get_all_applications` Method on `Partition`, implemented in `src/algorithms.cpp`).
""")
parts.append(block("schema/dal/core.schema.xml", lang="xml"))

parts.append(section("Scripts and data"))
parts.append(block("scripts/tutorial.py", lang="python"))
parts.append(block("scripts/dal_testing.data.xml", lang="xml"))
parts.append(block("scripts/algorithm_tests.py", lang="python"))
parts.append(block("scripts/dal_dump_apps.py", lang="python"))
parts.append(block("scripts/dal_dump_app_config.py", lang="python"))

parts.append(section("Python bindings"))
parts.append(block("python/dal/__init__.py", lang="python"))
parts.append(block("pybindsrc/module.cpp"))
parts.append(block("pybindsrc/dal_classes.cpp"))
parts.append(block("pybindsrc/dal_pybind_utils.hpp"))
parts.append(block("pybindsrc/algorithm_test_bindings.cpp"))

parts.append(section("Core algorithms (generated DAL class algorithms)"))
parts.append("""> `src/algorithms.cpp` contains implementations of the algorithms for the generated DAL classes (attribute `Partition`/`Segment`/`Application`/... methods declared as Methods in `core.schema.xml`), including `is_compatible`, `get_partition`, `get_used_repositories`, `substitute_variables`, `SubstituteVariables::convert`, and the topic-relevant `get_config_version` (reads `TDAQ_DB_VERSION` process environment; see lines 3211-3232) plus `Partition::get_config_version()` and the environment variable `TDAQ_DB_VERSION` propagation (line 82, 802-803, where `Partition::get_DBVersion()` is injected into the application environment). Reproduced in full byte content below.
""")
parts.append(block("src/algorithms.cpp"))
parts.append(block("src/disabled-components.cpp"))
parts.append(block("src/test_circular_dependency.cpp"))
parts.append(block("src/test_circular_dependency.hpp"))

parts.append(section("Build configuration"))
parts.append(block("CMakeLists.txt", lang="cmake"))
parts.append(block("cmake/dalConfig.cmake.in", lang="cmake"))
parts.append(block("LICENSE", lang="text"))
parts.append(block("NOTICE", lang="text"))

doc = f"""# Source 2: DUNE-DAQ/dal (GitHub, public, branch `develop`)

> Generated {__import__('datetime').date.today().isoformat()} by an automated extraction renderer (`output/build_02.py`).
> Every code block below is the full byte-content of the named file, copied verbatim from the local clone.

{''.join(parts)}
"""
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
