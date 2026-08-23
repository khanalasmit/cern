# 01 — Release Inventory (new release: `tdaq-13-00-00`)

Rules governing this document: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.

> **This document replaces an earlier version.** The earlier version was written while the
> package directories were still empty and concluded that no package source existed for
> this release. That conclusion is withdrawn — see §8, which also corrects two specific
> evidence citations the earlier version got wrong.

---

## 0. Executive summary

The new-release material consists of two GitLab **superprojects** that carry only build
orchestration, CI configuration and a `.gitmodules` manifest. The packages themselves live
in ~220 separate Git repositories.

The pinned package revisions are recorded as **gitlinks in this repository's own index**
(not in `.gitmodules`, which stores only `path` and `url`). Those revisions have been
checked out from `https://gitlab.cern.ch/atlas-tdaq-software/` at exactly the pinned
commits, so this investigation runs against real source at the exact revisions of
`tdaq-13-00-00`.

- Release identifier: **`tdaq-13-00-00`**, paired with **`tdaq-common-13-00-00`** — Confirmed.
- Packages checked out: **202 / 203** (tdaq) and **18 / 18** (tdaq-common).
- One package, `felix-interface`, is not anonymously readable and remains a gap.
- The components this investigation needs are all present: `oks`, `config`, `oksconfig`,
  `dal`, `rdb`, `rdbconfig`, `oks_utils`, `dbe`, `oks2coral`, `webis_server`, and — in
  tdaq-common — `webdaq`.

**Confidence: Confirmed**, except where marked.

---

## 1. Exact new-release source trees

| Requested by prompt | Actual directory | Present |
|---|---|---|
| `Materials/tdaq-cmake-tdaq-13-00-00/` | `Materials/tdaq-cmake-tdaq-13-00-00/` | yes |
| `Materials/tdaq-common-cmake-13-00-00/` | `Materials/tdaq-common-cmake-13-00-00/` | yes |

The directory names follow the GitLab source-archive convention `<project>-<ref>`:
project `tdaq-cmake` at ref `tdaq-13-00-00`; project `tdaq-common-cmake` at ref
`tdaq-common-13-00-00`.

**Evidence that these are the GitLab superprojects named in the directory names:**

> `Materials/tdaq-cmake-tdaq-13-00-00/README.md`, lines 8–11:
> "The source code is at the [CERN Gitlab instance](https://gitlab.cern.ch/atlas-tdaq-software). It
> consists of ca. 200 git repositories that are structured via two top-level repositories using
> git submodules, tdaq-common and this one."

This proves the archive is the `tdaq-cmake` superproject and that package code lives in
separate repositories. **Confidence: Confirmed.**

## 2. Release / version information found inside the trees

The numeric version in the CMake files is a **placeholder**, not the release identity:

| Fact | Evidence | What it proves |
|---|---|---|
| Version is a build-time placeholder | `Materials/tdaq-cmake-tdaq-13-00-00/CMakeLists.txt:3` — `set(TDAQ_VERSION 99.0.0 CACHE STRING "TDAQ version number")` | `99.0.0` is a default overridden at build time. It is **not** the release version, and must not be cited as one. |
| Same for tdaq-common | `Materials/tdaq-common-cmake-13-00-00/CMakeLists.txt:3` — `set(TDAQ_COMMON_VERSION 99.0.0 ...)` | Same placeholder convention. |
| The real version is the **branch/ref name** | `Materials/tdaq-cmake-tdaq-13-00-00/.gitlab-ci.yml:110` — `TDAQ_VERSION: $CI_COMMIT_REF_NAME` | The release version *is* the Git ref the build runs on — i.e. `tdaq-13-00-00`. |
| tdaq-common ref is derived from it | `.gitlab-ci.yml:217` — `if test -z "${TDAQ_COMMON_VERSION}"; then TDAQ_COMMON_VERSION="tdaq-common-${TDAQ_VERSION#tdaq-}" ; fi` | `tdaq-13-00-00` ⇒ `tdaq-common-13-00-00`. This is what makes the two directory names a consistent pair. |
| External software stack | `Materials/tdaq-common-cmake-13-00-00/CMakeLists.txt:5` — `set(LCG_VERSION_CONFIG LCG_110 CACHE STRING ...)` | The release builds against **LCG_110**. |

**Release identifier used throughout this document set: `tdaq-13-00-00`. Confidence: Confirmed.**

## 3. Git commit / tag / revision information

**Confirmed, and this corrects the earlier version of this document.**

The pinned package revisions are **not** in `.gitmodules` — that file records only `path`
and `url` (relative URLs of the form `../<package>.git`). They are recorded as **gitlinks
(mode `160000`) in this repository's index**:

    $ git ls-files -s Materials/ | awk '$1=="160000"' | wc -l
    203        # tdaq packages
    $ git ls-files -s Materials/tdaq-common-cmake-13-00-00
    160000 e011c3ca5e9476b1f134309f068a2f7771f1ac63 0  Materials/tdaq-common-cmake-13-00-00

The `tdaq-common-cmake` superproject in turn pins its own 18 packages, readable via
`git submodule status` once checked out.

Pinned revisions of the packages this investigation depends on:

| Package | Pinned commit |
|---|---|
| `oks` | `df20fc0e236c97cbe947331689f7386fa9823f38` |
| `config` | `42030ebdd502ef6df097bd637d8b8d764e2040e4` |
| `oksconfig` | `c3221fb47c6813ac892d5563bbd19352073e10e2` |
| `dal` | `897ae981ba978ea229a4de835acf522a930c3b95` |
| `rdb` | `44974880a757825f1036b405a113e5fb622d28c5` |
| `rdbconfig` | `cc87dc24a270a533d790efddc3b43aa4207cc7b0` |
| `oks_utils` | `1761b535afc894f3f72c1595a53bdc7514b5ddbe` |
| `dbe` | `3dd750d2ff97fb7e6fcbcc4f90eda871aa360fd3` |
| `webis_server` | `75dbfcf79b46995412dd411ba894a113dec8829d` |
| `webdaq` (tdaq-common) | `a6a461b6153e19f68c1cc9783f5f92514b4148f7` |

The `oks` pin is dated **2026-07-08** (`git -C oks log -1 --date=iso`), which independently
confirms this is a recent release and not a re-tag of old code.

## 4. Top-level repository structure

`Materials/tdaq-cmake-tdaq-13-00-00/` contains, besides the 203 package directories:

| Entry | What it is |
|---|---|
| `CMakeLists.txt` | Superproject definition; `tdaq_project(tdaq ...)` with `USES tdaq-common` and the `EXTERNALS` list |
| `cmake/` | Build machinery — `modules/`, `variants/`, `customize/`, `template.spec.in` (RPM packaging) |
| `doc/BUILDING.md`, `doc/INSTALL.md` | The only prose documentation at superproject level |
| `.gitlab-ci.yml` | The authoritative build/release recipe |
| `.gitmodules` | 203 package declarations (`path` + relative `url`) |
| `CONTRIBUTORS`, `LICENSE`, `NOTICE`, `.labels` | Project metadata |

## 5. Major TDAQ components present

Counted over checked-out source (excluding `.git`): **1489 `.cpp`, 2729 `.h`, 112 `.hpp`,
774 `.py`, 1296 `.java`, 635 `.xml`, 205 `.sh`** files.

Components relevant to this investigation, all **Confirmed present with source**:

| Package | Role as evidenced (detail in later documents) |
|---|---|
| `oks` | The OKS kernel itself — `OksKernel`, `OksClass`, `OksObject`, `OksQuery`, XML I/O, and the Git repository scripts |
| `config` | `config::Configuration` — the backend-neutral configuration API, plus its **Boost.Python binding** and Java binding |
| `oksconfig` | The OKS backend of `config::Configuration` (`OksConfiguration`, `ROksConfiguration`) |
| `rdb` / `rdbconfig` | The RDB server and its `config` backend — the *live, running-partition* access path |
| `dal` | Generated data-access layer, the **core OKS schema** (`data/schema/core.schema.xml`), and `daq::core::get_config_version()` |
| `oks_utils` | OKS utility tooling |
| `dbe` | Database editor (GUI) — a configuration **mutation** tool |
| `oks2coral` | Archives OKS files into a CORAL/relational "OKS Archive", keyed by **run number** |
| `webis_server` | HTTP/JSON server; includes an OKS handler (`src/oks_handler.cpp`) |
| `webdaq` (tdaq-common) | Stand-alone HTTP/JSON **client** library, with an `oks::` namespace |

Note for later documents: there is **no package named `WebDAQ` in the tdaq superproject.**
`webdaq` lives in **tdaq-common**; the tdaq superproject instead contains `webdbe`,
`webemon` and `webis_server`. Any claim about "WebDAQ" must say which of these it means.

## 6. Separate tdaq-common source tree

**Yes — present and checked out.** `Materials/tdaq-common-cmake-13-00-00/` pins 18
packages, all obtained: `CTPfragment`, `DQConfMaker`, `EventApps`, `EventStorage`,
`HistogramStyles`, `MuCalDecode`, `TDAQCExternal`, `TDAQCRelease`, `circ`, `cmake_tdaq`,
`compression`, `df_ef_interface`, `dqm_algorithm_helper`, `dqm_core`, `eformat`, `ers`,
`hltinterface`, **`webdaq`**.

## 7. Build-system information

- **CMake**, minimum 3.16.0 for tdaq (`CMakeLists.txt:1`) and 3.26.0 for tdaq-common.
- A TDAQ-specific CMake layer: `find_package(TDAQ)` with `tdaq_project()`,
  `tdaq_add_library()`, `tdaq_add_executable()`, `tdaq_add_python_package()`,
  `tdaq_add_test()` — supplied by `cmake_tdaq` in tdaq-common.
- Externals declared at `CMakeLists.txt:13–21`, including `mysql`, `oracle`, `Qt5`, `Qt6`,
  `XercesC`, `sqlite`, `tbb`, `java`, `protobuf`, `zeromq`, `numpy`, `cython`, `swig`,
  `Catch2`, `git`, `gssapi`, `cx_oracle`, `oracledb`.
- CI drives releases through `cmake_tdaq/bin/build_stack` (`.gitlab-ci.yml:222`), building
  tdaq-common first, then tdaq, and producing RPMs per `CMTCONFIG`.

**The presence of `git` in the EXTERNALS list is relevant later**: OKS shells out to `git`
at runtime (see document `03`/`06`), so `git` is a genuine runtime dependency, not only a
build-time one.

## 8. Documentation available inside the new release

- Superproject: `doc/BUILDING.md`, `doc/INSTALL.md`, `README.md`.
- Per package: `doc/RELEASE_NOTES.md` (current) plus archived per-release HTML notes —
  e.g. `config/doc/` carries notes back to `tdaq-01-01-00`.
- `oks/README.md` describes OKS itself and links the
  [DaqHltOks TWiki](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltOks) — an **external**
  resource, not repository evidence.
- `webis_server/doc/openapi.yaml` — a machine-readable HTTP API specification.
- `webis_server/doc/api-coverage.md`.

### Corrections to the earlier version of this document

Two citations in the earlier version do not hold against the actual files, and any
downstream reasoning that used them should be re-derived:

| Earlier claim | Actual file content |
|---|---|
| `CMakeLists.txt:3` sets `TDAQ_VERSION 13.0.0`, proving the release version | The file sets `99.0.0` — a placeholder. The release identity comes from the Git ref (§2). |
| tdaq-common builds against `LCG_109a` | `tdaq-common-cmake-13-00-00/CMakeLists.txt:5` sets `LCG_110`. |

The earlier claim that submodule revisions were unavailable is also withdrawn (§3).

## 9. What remains not established

- **`felix-interface`** — pinned in the index but not anonymously readable
  (`HTTP Basic: Access denied`). Anything depending on it is
  **Not established from the new-release repository.**
- **The ATLAS production configuration database is not in this release.** This needs to be
  stated carefully, because the release *does* ship a lot of OKS XML:

  | Category | Count (excluding `test/`, `tests/`) |
  |---|---|
  | `*.schema.xml` | 103 |
  | `*.data.xml` | 219 |

  These are **package-provided schema and example/fragment data**, contributed by the
  packages that define them — the largest contributors being `ResourceManager` (43),
  `PartitionMaker` (20), `DAQAssistant` (20), `siom` (14), `swrod` (12), `dqmf` (10).
  Several do declare `Partition` objects — e.g.
  `dqmf/data/DQM_test_partition.data.xml`, `emon/data/EMON_test_partition.data.xml`,
  `TTCviModule/partitions/PartitionTTCvi.data.xml` — but these are **test and
  detector-module example partitions shipped with their packages**, not the operational
  ATLAS partition database.

  The operational database lives in a **separate OKS Git repository** named at runtime by
  `TDAQ_DB_REPOSITORY` (see documents `03` and `06`). Its contents, its history, and its
  hosting location are **Not established from the new-release repository.**

  *What was searched:* all 220 checked-out packages, for `*.data.xml` and `*.schema.xml`,
  and for files declaring `class="Partition"`. *What is missing:* any file in this release
  that is, or points at, the real ATLAS configuration repository.
