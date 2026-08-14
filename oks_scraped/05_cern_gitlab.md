# 05. CERN GitLab — the original OKS code and docs

All repositories below are public at **https://gitlab.cern.ch** (no login needed for browsing; anonymous `git clone` works over https):

| Repo       | URL | Local clone | Size |
|------------|-----|-------------|------|
| oks        | https://gitlab.cern.ch/atlas-tdaq-software/oks | `oks-atlas/` | 56 files |
| oks_utils  | https://gitlab.cern.ch/atlas-tdaq-software/oks_utils | `oks_utils/` | 260 files |
| swrod      | https://gitlab.cern.ch/atlas-tdaq-software/swrod | `swrod/` | 227 files |
| oks2coral  | https://gitlab.cern.ch/atlas-tdaq-software/oks2coral | `oks2coral/` | 16 files |

Plus the public release-notes site: **https://atlas-tdaq-sw-releases.web.cern.ch/**.

---

## 5.1 oks (CERN original)

- `doc/RELEASE_NOTES.md` — central document, covers tdaq-13-01-00 .. tdaq-01-01-00. Read this for query/archiving/git facts (see 5.4).
- `include/oks/*.h` — canonical headers (the DUNE fork is branched from tag `oks-08-03-04`).
- `test/` — `test_update.cpp` (how to update attrs/relations), `test.data.xml`, `all_types.schema.xml` (all copied to `repos/`).
- `scripts/*.sh` — `oks-commit.sh`, `oks-tag.sh`, `oks-checkout.sh`, `oks-import.sh`, `oks-copy.sh`, `oks-edit-branch.sh`.
- `jsrc/` — Java OKS (browse-only mirror): `CommitError.java`, `TestCommitError.java`.

## 5.2 oks_utils (tools + editors + archiving)

- `examples/` — the tutorial programs **query.cpp**, `comparator.cpp`, `and_expression.cpp`, `or_expression.cpp`, `not_expression.cpp`, `r_expression.cpp`, `index.cpp`, `kernel.cpp`, `object.cpp`, `relationship.cpp`, `class.cpp`, `attribute.cpp`, `method.cpp`, `data.cpp`, `alloc.cpp`, `profiler.cpp` — see `08_oks_query_examples.md` for their content.
- `src/bin/oks_tutorial.cpp` — self-contained tutorial building a "Car/Person" DB and making queries; good source of question/answer pairs.
- `src/xm-gui/` — OKS Data Editor (Motif) sources incl. query constructor dialogs.
- `data/online-help/data-editor/*.html` — GUI user manual (copied into `repos/online-help/`): `QueryWindow.html`, `ObjectWindow.html`, `DataFileWindow.html`, `ClassWindow.html`, `MainWindow.html`, `GraphicalWindow.html`, `ReplaceWindow.html`, `OksDataEditor.html`, etc. **QueryWindow.html documents the query builder** (attribute expressions, relationship expressions, and/or/not tree).
- `src/rlib/` — relational archiving library + `create_db.{oracle,mysql,sqlite}.sql`.
- `cgi/` — `oks-archive.pl` (web archive GUI), `getdata.sh`, `cmp_data_versions.sh`, `vtable.sh`.
- `src/xm-lib/default-parameters.schema.xml` — example schema (copied).

## 5.3 swrod — modern consumer of OKS (shifter-visible classes)

- `schema/swrod.schema.xml` (23.6 KB) — SW ROD config schema (copied to `repos/`):
  classes `SwRodApplication`, `SwRodConfiguration`, `SwRodRob`, `SwRodModule`, `SwRodInputLink`, `SwRodDataChannel`, `SwRodCustomProcessingLib`, `SwRodFragmentBuilder`, `SwRodGBTModeBuilder`, `SwRodFullModeBuilder`, `SwRodFelixInput`, `SwRodBufferInput`, `SwRodFileWriter`, `SwRodHLTRequestHandler`, `SwRodEventSampler`, `SwRodDebugStream`, `SwRodCustomProcessor`, `SwRodShredder`, `FelixLink`, ...
- `data/*.data.xml` — realistic config values (rob, input links per dma, hosts, modules...).
- `application/Configuration.cpp` + `main.cpp` — how a run-control FSM app reads the OKS config at startup.
- `doc/RELEASE_NOTES.md`, `README.md` (see 02 for conceptual level).

## 5.4 oks2coral — archiving bridge

- `src/oks2coral.cpp` — CLI which checks schema/data into an Oracle "OKS archive" (versions, tags).
- `data/oks-archive-info.xml` — the `ConfigVersions` schema class used to record "this run used version X" (copied).

## 5.5 What the release notes say (facts for the corpus)

From `oks-atlas/doc/RELEASE_NOTES.md`:

- **tdaq-13-01-00** (current master docs): repository "versions" can be addressed by **tag, commit hash, date** ("2026-06-15", "2 years 1 day 3 minutes ago"), branch; `OksKernel::import_file(to, from)`.
- **tdaq-12-00-00**: `update_data()` keeps layout; `save_data()` rewrites.
- **tdaq-11-02-00**: ordered multi-value attributes/relationships (sorted on save); aligned commit flushing.
- **tdaq-09-02-01**: postponed changes via git branches; `oks_clone_repository -b <branch> --version tag:...|hash:...|date:...`; the **run-number DB stores used config version**: `rn_ls -c "oracle://atonr_adg/rn_r" ... -a '%xml'` → columns `Version = hash:6800fe3... | Config Name = daq/partitions/all_hosts.data.xml`; the git repo is **tagged by run number and partition**: `oks_clone_repository --version tag:r380689@all_hosts`.
- **tdaq-09-01-00**: the CVS->git switch; `TDAQ_DB_REPOSITORY` (git urls), `TDAQ_DB_USER_REPOSITORY`, `TDAQ_DB_VERSION=hash:...|date:...`, `OKS_REPOSITORY_MAPPING_DIR`; files accessed by **repository filename**, e.g. `oks_data_editor daq/segments/setup.data.xml`; oks-git-on/off/status functions; gitlab mirror project `atlas-tdaq-oks` (read-only).
- **tdaq-08-03-01**: data file **format v2.2** is the "val inside tag" format (shown in 07/08).
- **tdaq-01-09-00 ... tdaq-01-02-00**: queries ~= regex comparator; path query syntax; object-id in query; archiving `OksSchema` + `Release` column; `oks_ls_data` etc.
- Back-end history: OWL->boost datetime, archiving versioning (base/incremental).

## 5.6 Release-notes web site

`https://atlas-tdaq-sw-releases.web.cern.ch/` — MkDocs site listing releases
tdaq-09-00-00 ... tdaq-13-00-00 + nightly. Points to
`https://gitlab.cern.ch/atlas-tdaq-software/admin/tdaq-release-notes`.
(Downloaded into `repos/` was *not* needed; pages are small markdown.)

## 5.7 Tags in the oks gitlab repo (via API)

Latest tags: `oks-08-04-00` (for tdaq-11-02-00, Nov 2023), `oks-08-03-04`
(tdaq-09-04-00, 2022 — **DUNE fork baseline**), `oks-08-03-03` (tdaq-09-03-00),
`oks-08-03-02-01`, … `oks-08-00-00` (git migration), `oks-07-00-08`…06-10-xx
(CVS-era). Source: `GET /api/v4/projects/atlas-tdaq-software%2Foks/repository/tags`.