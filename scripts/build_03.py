# Renderer for 03-cern-gitlab.md: embeds full verbatim content of the four CERN GitLab OKS repos.
# -*- coding: utf-8 -*-
import io, os, re

ROOTS = {
    "oks": r"repo\cern-oks",
    "oks_utils": r"repo\cern-oks_utils",
    "swrod": r"repo\cern-swrod",
    "oks2coral": r"repo\cern-oks2coral",
}
OUT = r"output\03-cern-gitlab.md"

def read(repokey, p):
    with io.open(os.path.join(ROOTS[repokey], p), "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()

def block(repokey, path, lang="cpp"):
    body = read(repokey, path)
    return f"### `{path}`  \n*Local path: `repo/{repokey}/{path}`*\n\n```{lang}\n{body.rstrip(chr(10))}\n```\n\n"

def html_to_text(repokey, path):
    """Strip HTML tags and decode entities, preserving rough layout."""
    raw = read(repokey, path)
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", raw)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</(p|div|tr|h1|h2|h3|h4|li|table)>", "\n", s)
    s = re.sub(r"(?is)<td[^>]*>", " | ", s)
    s = re.sub(r"(?is)<[^>]+>", "", s)
    import html as H
    s = H.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()

def section(header):
    return f"\n## {header}\n\n"

def load_tags():
    with io.open(r"output\extracts\cern-oks-tags.txt", "r", encoding="utf-8", errors="replace") as f:
        lines = [l.strip() for l in f if l.strip()]
    tags = sorted({l.split("refs/tags/")[1] for l in lines if "refs/tags/" in l and not l.endswith("^{}")})
    return tags

parts = []
tags = load_tags()

parts.append(section("Provenance"))
parts.append("""The four repositories are the canonical ATLAS TDAQ OKS sources at CERN, cloned 2026-08-08 (git, depth 1):

| Repo | GitLab URL | Branch | HEAD commit | HEAD date |
|------|------------|--------|-------------|-----------|
| oks | https://gitlab.cern.ch/atlas-tdaq-software/oks | master | `bba5d25a6f4626b3a2bce4888cbc5bbff32da48c` | 2026-07-09 |
| oks_utils | https://gitlab.cern.ch/atlas-tdaq-software/oks_utils | master | `1761b535afc894f3f72c1595a53bdc7514b5ddbe` | 2025-08-18 |
| swrod | https://gitlab.cern.ch/atlas-tdaq-software/swrod | master | `f8a52efac6abd594209b2090eff807b11eb34574` | 2026-08-04 |
| oks2coral | https://gitlab.cern.ch/atlas-tdaq-software/oks2coral | master | `be046277b4fa16db855d14b463bce028905fd06f` | 2021-03-02 |

**Release-tag timeline of the `oks` repo (full list, {} tags, extracted from `git ls-remote --tags`):**
- Oldest OKS-era tags: `oks-02-07-02`, `oks-02-07-03`, `oks-02-08-04`, `oks-02-08-05`, then `oks-03-00-00` ... `oks-08-04-00` (the series documented in `doc/RELEASE_NOTES.md`; DUNE forked from `oks-08-03-04`, 2022-04-14).
- TDAQ-era tags: `tdaq-01-04-00_patch_02` ... `tdaq-01-09-01_patches_02`, `online-00-18-00`.
- The complete sorted list is preserved in `output/extracts/cern-oks-tags.txt`.
""".format(len(tags)))

parts.append(section("1. `oks` — core OKS library (GitLab)"))
parts.append("""This is the current ATLAS TDAQ `oks` package (the DUNE fork is based on its `oks-08-03-04` tag). Files below are embedded in full: README, the complete release notes (documenting the GIT-integration history relevant to section G), the query grammar implementation (`oks/query.h` + `src/query.cpp`), the GIT repository utilities in `bin/` (built as `oks_clone_repository`, `oks_dump`, `oks_git_repository`, `oks_validate_repository`), the git-wrapper shell scripts `scripts/oks-*.sh`, and the test files.
""")
parts.append(block("oks", "README.md", "markdown"))
parts.append(block("oks", "doc/RELEASE_NOTES.md", "markdown"))
parts.append("""### Query grammar implementation
The complete `oks/query.h` header and `src/query.cpp` implementation are embedded below. Key facts extracted:
- Operator tokens (`src/query.cpp:15-31`): `or`, `and`, `not`, `some`, `this`, `all`, `object-id`, `=`, `!=`, `~=`, `<=`, `>=`, `<`, `>`, `path-to`, `direct`, `nested`.
- `OksQuery::RE = "~="` is the regular-expression comparator; `reg_exp_cmp` uses `boost::regex_match` (`src/query.cpp:57-59`).
- `path-to` queries are implemented by the `oks::QueryPath`/`QueryPathExpression` classes (`oks/query.h:328-399`) with `direct`/`nested` relationship-following.
""")
parts.append(block("oks", "oks/query.h"))
parts.append(block("oks", "src/query.cpp"))
parts.append("""### GIT repository utilities and scripts
`bin/oks_git_repository.cpp` prints `OksKernel::get_repository_root()` (i.e. the `TDAQ_DB_REPOSITORY` value); `bin/oks_clone_repository.cpp` clones an OKS config GIT repository; `bin/oks_dump.cpp` and `bin/oks_validate_repository.cpp` walk/validate the OKS files of a repository working area. The `scripts/oks-*.sh` shell scripts wrap git operations for OKS config databases: checkout, commit, copy, diff, edit-branch, import, log, status, tag, update, version.
""")
parts.append(block("oks", "bin/oks_clone_repository.cpp"))
parts.append(block("oks", "bin/oks_dump.cpp"))
parts.append(block("oks", "bin/oks_git_repository.cpp"))
parts.append(block("oks", "bin/oks_validate_repository.cpp"))
for sh in ["oks-checkout.sh","oks-commit.sh","oks-copy.sh","oks-diff.sh","oks-edit-branch.sh",
           "oks-import.sh","oks-log.sh","oks-status.sh","oks-tag.sh","oks-update.sh","oks-version.sh"]:
    parts.append(block("oks", f"scripts/{sh}", "sh"))
parts.append("""### Tests
`test/all_types.schema.xml` defines a schema exercising all OKS attribute types; `test/test.data.xml` is a data file for it (note the `oks-version` value `"oks-08-04-00-3-g816241d built "Aug 29 2024""` in its `<info>` element — the version is a git describe string); `test/test_update.cpp` tests the update-data functionality.
""")
parts.append(block("oks", "test/all_types.schema.xml", "xml"))
parts.append(block("oks", "test/test.data.xml", "xml"))
parts.append(block("oks", "test/test_update.cpp"))
parts.append("""### Java commit hook support
`jsrc/oks/CommitError.java` implements the OKS repository commit error handling for the OKS Java client library.
""")
parts.append(block("oks", "jsrc/oks/CommitError.java", "java"))
parts.append(block("oks", "jsrc/oks/TestCommitError.java", "java"))
parts.append(block("oks", "NOTICE", "text"))
parts.append(block("oks", "LICENSE", "text"))

parts.append(section("2. `oks_utils` — examples, tutorial, GUI help and docs (GitLab)"))
parts.append("""### The 16 API examples (`examples/*.cpp`)
Each example is a self-contained `main()` demonstrating one OKS API facet; all embedded verbatim below: `alloc.cpp` (OksAllocator use), `and_expression.cpp`, `attribute.cpp`, `class.cpp`, `comparator.cpp` (OksQuery::Comparator + equal_cmp), `data.cpp` (OksData), `index.cpp` (OksIndex), `kernel.cpp` (OksKernel + new_data), `method.cpp`, `not_expression.cpp`, `object.cpp`, `or_expression.cpp`, `profiler.cpp`, `query.cpp` (OksQuery from strings: `this (...)`/`all (...)`), `r_expression.cpp` (OksRelationshipExpression), `relationship.cpp`.
""")
for ex in ["alloc.cpp","and_expression.cpp","attribute.cpp","class.cpp","comparator.cpp","data.cpp",
           "index.cpp","kernel.cpp","method.cpp","not_expression.cpp","object.cpp","or_expression.cpp",
           "profiler.cpp","query.cpp","r_expression.cpp","relationship.cpp"]:
    parts.append(block("oks_utils", f"examples/{ex}"))
parts.append("""### `src/bin/oks_tutorial.cpp`
The canonical OKS tutorial program (Car / Manufacturer / Garage example classes).
""")
parts.append(block("oks_utils", "src/bin/oks_tutorial.cpp"))
parts.append("""### Online-help HTML pages (`data/online-help/data-editor/`)
The full HTML text content of the OKS Data Editor help pages, embedded verbatim: `Index.html`, `OksDataEditor.html`, `MainWindow.html`, `ClassWindow.html`, `ObjectWindow.html`, `ObjectCreation.html`, `DataFileWindow.html`, `QueryWindow.html`, `GraphicalWindow.html`, `ReplaceWindow.html`, `MessageLogWindow.html`. The `QueryWindow.html` page documents the query window and query grammar as shown in the OKS Data Editor GUI.
""")
for h in ["Index.html","OksDataEditor.html","MainWindow.html","ClassWindow.html","ObjectWindow.html",
          "ObjectCreation.html","DataFileWindow.html","QueryWindow.html","GraphicalWindow.html",
          "ReplaceWindow.html","MessageLogWindow.html"]:
    parts.append(block("oks_utils", f"data/online-help/data-editor/{h}", "html"))
parts.append("""### Release notes (HTML, converted to text)
The `doc/RELEASE_NOTES.tdaq-02-01-00.html` and `doc/RELEASE_NOTES.tdaq-04-00-00.html` pages record the oks_utils release notes for those TDAQ releases. Text extracted from HTML below.
""")
parts.append(f"#### `doc/RELEASE_NOTES.tdaq-02-01-00.html` (text-extracted)\n\n```text\n{html_to_text('oks_utils', 'doc/RELEASE_NOTES.tdaq-02-01-00.html')}\n```\n")
parts.append(f"#### `doc/RELEASE_NOTES.tdaq-04-00-00.html` (text-extracted)\n\n```text\n{html_to_text('oks_utils', 'doc/RELEASE_NOTES.tdaq-04-00-00.html')}\n```\n")
parts.append("""### Tests and misc
`tests/DAQ-Configuration.schema.xml` is the ATLAS DAQ-Configuration test schema; `tests/generate_data.cpp`, `tests/test_indexies.cpp`, `tests/time_tests.cpp`, `tests/test.sh`, `tests/do-tests`, `tests/make-sciplot-data` are the test programs; `src/lib/oks_access.cpp` and `oks/ral.h`/`src/lib/oks_ral.cpp` implement the RAL (Relational Access Layer, ~100 KB) for relational storage back-ends; `cmt/requirements` is the legacy CMT build description.
""")
parts.append(block("oks_utils", "tests/DAQ-Configuration.schema.xml", "xml"))
parts.append(block("oks_utils", "tests/generate_data.cpp"))
parts.append(block("oks_utils", "tests/test_indexies.cpp"))
parts.append(block("oks_utils", "tests/test.sh", "sh"))
parts.append(block("oks_utils", "cmt/requirements", "text"))

parts.append(section("3. `swrod` — Software Readout Driver (GitLab)"))
parts.append("""The SW ROD (Software Readout Driver) uses OKS/DUNE DAQ configuration for its data-link and module definitions (schema `schema/swrod.schema.xml`, data files in `data/`). `test/oks2json.cpp` shows OKS config being translated to JSON. Only the OKS-relevant subset is embedded.
""")
parts.append(block("swrod", "README.md", "markdown"))
parts.append(block("swrod", "doc/RELEASE_NOTES.md", "markdown"))
parts.append(block("swrod", "schema/swrod.schema.xml", "xml"))
parts.append(block("swrod", "data/SwRodTestPartition.data.xml", "xml"))
parts.append(block("swrod", "test/oks2json.cpp"))
parts.append(block("swrod", "LICENSE", "text"))

parts.append(section("4. `oks2coral` — OKS to Coral archiving (GitLab)"))
parts.append("""`oks2coral` archives OKS data into a relational (CORAL/MySQL/SQLite/Oracle) archive. `oks2coral/ConfigVersions.h` declares the archive-versioning interface; `src/oks2coral.cpp` is the main archiver; `scripts/oks2coral_mk_tmp_file.sh` builds the archive command. Release notes (HTML) converted to text below.
""")
parts.append(block("oks2coral", "oks2coral/ConfigVersions.h"))
parts.append(block("oks2coral", "src/oks2coral.cpp"))
parts.append(block("oks2coral", "scripts/oks2coral_mk_tmp_file.sh", "sh"))
for h in ["tdaq-01-06-00","tdaq-01-07-00","tdaq-01-08-03","tdaq-01-08-04","tdaq-01-09-01","tdaq-02-00-00"]:
    parts.append(f"#### `doc/RELEASE_NOTES.{h}.html` (text-extracted)\n\n```text\n{html_to_text('oks2coral', f'doc/RELEASE_NOTES.{h}.html')}\n```\n")

doc = f"""# Source 3: CERN GitLab OKS repositories (oks, oks_utils, swrod, oks2coral)

> Generated {__import__('datetime').date.today().isoformat()} by automated extraction renderer (`output/build_03.py`).
> All code blocks are full byte-content of the named files from the local clones (or HTML-to-text conversion where noted).

{''.join(parts)}
"""
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
