# 03 — Historical Configuration Resolution (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Nothing here is taken from the `tdaq-09-03-00` investigation.

Paths are relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

---

## 1. Executive summary

**The run → configuration → revision chain is implemented in this release, end to end.**
This is the strongest result of the investigation, and it is better than the prompt's
conceptual flow assumed: the release does not merely *permit* historical access, it
**records the mapping at run-start time, in two independent places.**

When the run-number service allocates a run number, it:

1. reads the OKS **Git SHA** currently in use by the partition, from the Information Service;
2. writes it into the run-number database as the run row's `CONFIGVERSION` column, alongside
   `CONFIGNAME` (which configuration file) and `PARTITIONNAME`; and
3. **tags the OKS Git repository** with `r<run_number>@<partition>`.

So a historical configuration can be reached from a run number by *either* a database lookup
*or* — with no database at all — a Git tag whose name is derived arithmetically from the run
number.

```
run number ──► rn database row (CONFIGVERSION = Git SHA, CONFIGNAME = data file)
     │                                    rn/src/lib.cpp:149, :251-255, :274
     └────────► Git tag  "r<run>@<partition>"
                                          rn/src/lib.cpp:100-107, :314-317
                    │
                    ▼
          revision string  "tag:r<run>@<partition>"  (or "hash:<sha>")
          supplied as  oksconfig:<file>&version=…   OR  $TDAQ_DB_VERSION
                    │      oksconfig/src/OksConfiguration.cpp:150
                    │      oks/src/kernel.cpp:757, :925-958
                    ▼
          OksKernel::k_checkout_repository()          oks/src/kernel.cpp:5937
                    │      → oks-checkout.sh → git clone + git checkout
                    ▼
          load_schema() / load_data()  ──►  OksKernel  ──►  OksQuery
```

The one honest caveat: this release contains the **producers** of that mapping. It does not
contain a reader API that takes a run number and returns a configuration — see B1 §4 and the
expert questions in §14.

## 2. Historical configuration lifecycle

| Stage | Component | Evidence |
|---|---|---|
| A configuration is edited and committed | `OksKernel::commit_repository()` → `oks-commit.sh` | `oks/src/kernel.cpp:6127` |
| A partition starts; its OKS version is published to IS as `RunParams.ConfigVersion` | `daq::core::set_config_version()` | `dal/src/algorithms.cpp:3330+` |
| A run number is allocated; the version is captured and the repo tagged | `rn::RunNumber` | `rn/src/lib.cpp:149, :251-255, :314-317` |
| Later: a revision is checked out | `OksKernel` ctor / `update_repository()` → `oks-checkout.sh` / `oks-update.sh` | `oks/src/kernel.cpp:925-958`, `:6064` |
| The checked-out XML is loaded and queried | `load_schema`/`load_data`, `OksQuery` | document `02` §10 |

## 3. Run-to-configuration evidence

### The run-number database schema records the configuration

> `rn/src/create_db.sql:5–17`
> ```sql
> create table RunNumber (
>   Name           varchar2(16) not null,
>   RunNumber      number(10) not null,
>   StartAt        varchar2(24) not null,
>   Duration       number(10),
>   CreatedBy      varchar2(16) not null,
>   Host           varchar2(256) not null,
>   PartitionName  varchar2(256) not null,
>   ConfigSchema   number(10),
>   ConfigData     number(10),
>   Comments       varchar2(2000),
>   constraint     RunNumber_PK primary key (Name, RunNumber),
>   ...
> );
> ```

**Caution — the `.sql` file is out of date relative to the code.** The implementation writes
column names that this `CREATE TABLE` does not declare:

> `rn/src/lib.cpp:80–85`
> ```cpp
> const char * RunNumber::s_partition_name_column  = "PARTITIONNAME";
> const char * RunNumber::s_config_schema_column   = "CONFIGSCHEMA";
> const char * RunNumber::s_config_data_column     = "CONFIGDATA";
> const char * RunNumber::s_config_version_column  = "CONFIGVERSION";
> const char * RunNumber::s_config_name_column     = "CONFIGNAME";
> const char * RunNumber::s_comments_column        = "COMMENTS";
> ```

`CONFIGVERSION` and `CONFIGNAME` are used by the code but absent from `create_db.sql`.
The deployed schema is therefore **newer than the checked-in DDL**, and the DDL in this
release must not be treated as the authoritative table definition.
**Confidence for the columns: Confirmed** (code). **For the deployed DDL: Not established
from the new-release repository.**

### What the code writes into those columns

**`CONFIGVERSION` — the OKS Git SHA:**

> `rn/src/lib.cpp:148–150`
> ```cpp
> if(getenv("TDAQ_DB_VERSION") && getenv("TDAQ_DB_REPOSITORY") && !getenv("TDAQ_DB_USER_REPOSITORY")) {
>   m_config_version = daq::core::get_config_version(m_partition_name);
> }
> ```
> `rn/src/lib.cpp:251–256`
> ```cpp
> if(m_config_version.empty())
>   data[s_config_version_column].setNull(true);
> else
>   {
>     data[s_config_version_column].data<std::string>() = m_config_version;
>     tdaq_db_data_env = getenv("TDAQ_DB_DATA");
>   }
> ```

`daq::core::get_config_version()` reads IS object `RunParams.ConfigVersion`
(`dal/src/algorithms.cpp:3289,3292–3320`), whose schema states the value is the
**"OKS GIT SHA key used for given partition"** (`dal/data/is/oks-version.schema.xml`).

**`CONFIGNAME` — which configuration, as a repository-relative path:**

> `rn/src/lib.cpp:258–274` — takes `TDAQ_DB_DATA`, resolves it, strips the repository mapping
> directory prefix, and stores the remainder:
> ```cpp
> s.erase(0, OksKernel::get_repository_mapping_dir().size()+1);
> ...
> data[s_config_name_column].data<std::string>() = s;
> ```

**What this proves.** A row in the run-number database identifies, for one run: the
partition, the configuration *file* (repository-relative), and the exact configuration
*revision* (Git SHA). That is precisely the (configuration identity + revision) pair the
prompt's flow calls for. **Confidence: Confirmed.**

**Important negative.** The capture is **conditional**:
`TDAQ_DB_VERSION` **and** `TDAQ_DB_REPOSITORY` must be set, and `TDAQ_DB_USER_REPOSITORY`
must **not** be. If a run is taken from a user repository or without a pinned version,
`CONFIGVERSION` is written `NULL` (`rn/src/lib.cpp:252`). **Historical resolution is
therefore not guaranteed for every run** — an important limit for the MCP.
**Confidence: Confirmed.**

### The repository is tagged with the run number

> `rn/src/lib.cpp:87–113`
> ```cpp
> struct TagRepository
> {
>   const unsigned long m_run_number;
>   const std::string m_partition_name;
>   const std::string m_config_version;
>   ...
>   void operator()()
>     {
>       std::ostringstream tag;
>       tag << 'r' << m_run_number << '@' << m_partition_name;
>       OksKernel k(false, false, false, true, m_config_version.c_str());
>       k.tag_repository(tag.str());
>     }
> };
> ```
> `rn/src/lib.cpp:313–318`
> ```cpp
> if (!m_config_version.empty())
>   {
>     TagRepository tag(m_run_number, m_partition_name, m_config_version);
>     m_tag_thread = std::thread (tag);
>   }
> ```

**What this proves.** The tag name is **`r<run_number>@<partition_name>`**, applied to the
OKS Git repository at the run's configuration version. This is a *deterministic, derivable*
name: given a run number and partition, the MCP can construct the tag without consulting any
database. **Confidence: Confirmed.**

Two caveats, both Confirmed from the same code:
- Tagging happens on a **detached background thread** and failures are only reported as an
  ERS error (`rn::TagConfigRepositoryFailure`, `rn/src/lib.cpp:108–111`). A tag may therefore
  be **missing** for a run even when the DB row is correct.
- Tagging is skipped entirely when `m_config_version` is empty (§ above).

## 4. B1 — How is a run associated with a configuration?

**Repository finding.** By the run-number service, at run-number allocation time, via three
recorded facts: `PARTITIONNAME`, `CONFIGNAME` (the data file) and `CONFIGVERSION` (the Git
SHA) — plus a Git tag `r<run>@<partition>`.

**Evidence.** `rn/src/lib.cpp:148–150, :251–256, :258–274, :313–318`;
`dal/src/algorithms.cpp:3292`; `dal/data/is/oks-version.schema.xml`.

**Execution/data flow.**
`RunControl` start → `rn::RunNumber` ctor → `daq::core::get_config_version(partition)` reads
IS `RunParams.ConfigVersion` → row inserted with `CONFIGVERSION`/`CONFIGNAME` → background
thread tags the OKS repo.

**Confidence: Confirmed** for the *writing* side.

**Missing information.** This release provides **no API that reads the mapping back**.
`rn/rn/rn.h` exposes `get_number()` and `set_comments()` — it is a run-number *allocator*,
not a run-metadata query service. `rn/src/ls.cpp` and `rn/cgi/rn.pl` list runs, but were not
traced far enough to establish a supported lookup interface.
**The reverse lookup "run number → CONFIGVERSION" is Not established from the new-release
repository** as a programmatic API. *What was searched:* `rn/` for read/query methods,
`dal/` and `config/` for run-number-aware functions. *What is missing:* a documented client
API, or the connection details for the run-number database (`TDAQ_RUN_NUMBER_CONNECT`,
`rn/src/lib.cpp:128`).

**Implication for the MCP prototype.** Two viable resolution strategies, in order of
preference:
1. **Git tag** — construct `r<run>@<partition>` and check out `TDAQ_DB_VERSION="tag:..."`.
   Needs only the OKS Git repository. Fails when the background tagging failed.
2. **Run-number DB** — query `CONFIGVERSION`/`CONFIGNAME` directly. Authoritative, but needs
   DB credentials and a schema that this release does not correctly document.

## 5. B2 — How is the exact configuration revision determined?

**Repository finding.** The revision is a **Git commit SHA**, and it is selected by the
`TDAQ_DB_VERSION` environment variable in `parameter:value` form.

**Evidence.**

> `oks/src/kernel.cpp:757–773`
> ```cpp
> OksKernel::parse_config_version(const char *version, std::string &param, std::string &val)
> {
>   if (version && *version)
>     if (const char *value = strchr(version, ':'))
>       { param.assign(version, value - version); val.assign(value + 1); }
>     else
>       throw std::runtime_error("bad OKS repository version value ... expecting parameter:value format");
> }
> ```
> `oks/src/kernel.cpp:930–958` — the constructor reads `TDAQ_DB_VERSION`, parses it, creates a
> temporary user repository, and calls `k_checkout_repository(param, val, branch_name)`.

The accepted parameters are **`tag`, `date`, `hash`**:

> `oks/oks/kernel.h:1657–1666` — `update_repository(const std::string& param, const std::string& val, RepositoryUpdateType)`,
> documented *"\param param  \"tag\", \"date\" or \"hash\""*.

and at the `config` layer the same three appear as an enum:

> `config/config/ConfigVersion.h:33–37`
> ```cpp
> enum QueryType { query_by_date, query_by_id, query_by_tag };
> ```

`config/config/ConfigVersion.h:47–52` states the id **is** a Git SHA.

There is a **second route to the same kernel argument**, which is preferable for a service:
`oksconfig` accepts the revision as a **connection-string parameter**.

> `oksconfig/src/OksConfiguration.cpp:150, :191–202`
> ```cpp
> const char s_version_str[] = "version=";
> ...
> else if (auto idx = token.find(s_version_str); idx == 0)
>   m_version = token.substr(sizeof(s_version_str)-1);
> ...
> m_kernel = new OksKernel(m_oks_kernel_silence, false, false, !m_oks_kernel_no_repo,
>                          m_version.empty() ? nullptr : m_version.c_str());
> ```

Spec grammar (`oksconfig/src/OksConfiguration.cpp:153–205`):

```
oksconfig:<file>[:<file>...][&<param>[;<param>...]]
    param ::= "norepo" | "version=" <tag|hash|date> ":" <value>
```

**Confidence: Confirmed.**

**Implication for the MCP prototype.** Revision selection is a **string**, fixed before the
kernel is constructed, and it can be supplied **per `Configuration` object** rather than
through the process-global environment. That distinction matters for a server handling
concurrent requests about different runs: `os.environ` would race, a connection string does
not. Prefer:

```python
config.Configuration(f"oksconfig:{config_name}&version=tag:r{run}@{partition}")
```

**Not established from the new-release repository:** whether `version=` is documented or
supported for external use. *Searched:* `oksconfig/doc/RELEASE_NOTES.md`,
`oksconfig/CMakeLists.txt`. *Missing:* any mention of the parameter.

## 6. B3 — Is Git authoritative for historical configuration?

The prompt asks these to be distinguished. Taking them one at a time:

| Claim | Verdict | Evidence |
|---|---|---|
| Configuration files exist in Git | **Confirmed** | `oks-checkout.sh` does `git clone` of `$(oks_git_repository)`, i.e. `TDAQ_DB_REPOSITORY` (`oks/scripts/oks-checkout.sh:16, :155`) |
| Git contains historical versions | **Confirmed** | `oks-log.sh:91` runs `git log ... --first-parent ${TDAQ_DB_BRANCH:-master} --name-only` and the output is parsed into `OksRepositoryVersion` records (`oks/src/kernel.cpp:6395–6484`) |
| Git revisions represent configuration versions | **Confirmed** | `config/config/ConfigVersion.h:47–52` — "The version unique ID is a repository hash (GIT SHA)" |
| A run maps to a specific Git revision | **Confirmed** | `rn/src/lib.cpp:149, :255` (SHA into `CONFIGVERSION`) and `:100–107` (tag `r<run>@<partition>`) |
| The application automatically resolves run → Git revision | **Not established from the new-release repository** | No code was found that takes a run number and returns a revision. The mapping is *written* by `rn`; nothing in this release *reads* it back. Searched: `rn/`, `dal/`, `config/`, `oks/` for run-number-keyed lookups. |

So: **Git is authoritative for the configuration content and its versions**, and the run→SHA
association is real and recorded — but the *automatic resolution* the prompt hypothesises is
a component the MCP project must supply.

## 7. B4 — Are schema and data XML versioned with configuration revisions?

**Repository finding. Yes — schema and data are files in the same Git repository, so they
share one revision history.**

**Evidence.** `oks-checkout.sh` clones the whole repository and checks out a single
tag/hash/date (`oks/scripts/oks-checkout.sh:154–233`); there is no separate schema
repository or schema-version parameter anywhere in `OksKernel`'s repository API
(`oks/oks/kernel.h:1586–1700`). `OksKernel::get_modified_files()` takes a single `version`
argument covering data files (`oks/oks/kernel.h:1564–1573`), and
`get_repository_versions_diff(sha1, sha2)` returns *files* changed between two revisions
(`oks/oks/kernel.h:1680`), without distinguishing schema from data.

**Confidence: Confirmed.**

**Implication for the MCP prototype.** One revision identifier pins **both** the schema and
the data. The MCP never needs to track a separate schema version — which also means schema
retrieved for an LLM must come from the *same* checkout as the data being queried
(see document `08`).

## 8. B5 — How is a historical revision retrieved?

**Repository finding.** By an ordinary `git clone` followed by an ordinary `git checkout`,
performed by a **shell script** that `OksKernel` invokes with `system()`.

**Evidence.**

> `oks/src/kernel.cpp:5945–5980`
> ```cpp
> std::string cmd("oks-checkout.sh");
> ...
> cmd.append(" -u "); cmd.append(get_user_repository_root());
> if (!param.empty()) { cmd.append(" --"); cmd.append(param); cmd.push_back(' ');
>                       cmd.push_back('"'); cmd.append(val); cmd.push_back('"'); }
> if (!branch_name.empty()) { cmd.append(" -b "); cmd.append(branch_name); }
> ...
> CommandOutput cmd_out("oks-checkout", this, cmd);
> cmd_out.check_command_status(system(cmd.c_str()));
> ```

and the script itself:

> `oks/scripts/oks-checkout.sh:154–233`
> ```sh
> git clone -q -n "${git_repo}" .
> git config pull.rebase true
> command="git checkout -q -B ${branch}"
> if [ ! -z "${tag}" ]; then  $command tags/${tag}
> else
>   if [ ! -z "${date}" ]; then hash=$(git rev-list -1 --before="${date}" "${branch}") ; fi
>   if [ -z "${hash}" ] && git ls-remote --exit-code --heads origin "$branch" > /dev/null; then hash="origin/${branch}" ; fi
>   $command ${hash}
> fi
> ...
> echo "checkout oks version `git rev-parse HEAD`"
> ```

The resulting SHA is parsed back out of the script's stdout and stored:

> `oks/src/kernel.cpp:5991–5997`
> ```cpp
> static std::string version_prefix("checkout oks version ");
> std::string version = cmd_out.last_str();
> ...
> p_repository_version = version.substr(version_prefix.size());
> ```

**Confidence: Confirmed.**

**What this proves precisely.**
- Date-based selection is `git rev-list -1 --before=<date>` — "the last commit at or before
  that time", **not** an exact match. Its result depends on the branch.
- The default branch is `master` (`oks-checkout.sh:30`), overridable by `-b` /
  `TDAQ_DB_BRANCH` (`oks/src/kernel.cpp:951–953`).
- The checkout is into a **temporary user repository directory** created per kernel
  (`oks/src/kernel.cpp:945–948`), so historical access does not disturb anything shared.

## 9. B6 — How is the historical configuration loaded into OKS?

Once the checkout has happened in the constructor, loading is the *ordinary* path: there is
no separate "historical load" API. `load_schema()` / `load_data()` read files from the user
repository root (`oks/oks/kernel.h:543–556`), and `prepare_file_path()` resolves relative
names against `get_user_repository_root()` (`oks/src/kernel.cpp:776–796`).

**Confidence: Confirmed.**

**Implication for the MCP prototype.** Historical and current access differ **only** in the
value of `TDAQ_DB_VERSION`. The same query code serves both. This is what makes a read-only
historical prototype cheap.

## 10. B7 — Can multiple configurations coexist in one loaded database?

**Repository finding. Yes.** An `OksKernel` holds a *set of files* and a *set of classes*,
not a single "configuration". Multiple data files are loaded and tracked individually:
`OksKernel` exposes `load_data()`, `close_data()`, `set_active_data()`, and
`get_modified_files(std::set<OksFile*>&, ...)` (`oks/oks/kernel.h:1504–1573`), and OKS data
files may `include` other files (`OksKernel::get_includes()`, `oks/oks/kernel.h:1016`).

The unit that behaves like "a configuration" in the ATLAS sense is the **`Partition` object**
in the core schema (`dal/data/schema/core.schema.xml`), not the database file — and the
release ships several data files each declaring their own `Partition`
(e.g. `dqmf/data/DQM_test_partition.data.xml`, `TTCviModule/partitions/PartitionTTCvi.data.xml`).

**Confidence: Confirmed** for "multiple files and multiple `Partition` objects can coexist".

**Implication for the MCP prototype.** "Which configuration" is **two** parameters, not one:
the entry data file (`TDAQ_DB_DATA`, recorded per run as `CONFIGNAME`) *and* the partition
name. A query answered against the wrong partition object in a correctly-checked-out
revision would be silently wrong.

## 11. B8 — What prevents accidental modification of historical configurations?

**Repository finding. Nothing enforces read-only at the API level.** The protection is
structural, not a permission check.

**Evidence for the structural protection:**
- The checkout goes into a **temporary, per-kernel** user repository directory
  (`oks/src/kernel.cpp:945–948`; `create_user_repository_dir()`), which is cleaned up
  (`remove_user_repository_dir()`, `oks/src/kernel.cpp:6001`). Edits there are local.
- Publishing a change requires an explicit, separate `commit_repository()` call that shells
  out to `oks-commit.sh` (`oks/src/kernel.cpp:6127`), and it **throws** if the repository
  roots are not configured (`oks/src/kernel.cpp:6122–6126`).
- A checkout at a tag or hash leaves Git in a state where the branch does not track origin,
  so a later push would not fast-forward. (Inference from `oks-checkout.sh:172`
  `git checkout -q -B ${branch} tags/${tag}` — **Strongly indicated**, not Confirmed:
  no code asserts this.)

**Evidence that no read-only mode exists:** `OksKernel`'s constructor has a
`bool allow_repository` flag but no read-only flag (`oks/oks/kernel.h:604`); `OksObject`'s
mutators (`SetValue`, `SetRelationshipValue`, `destroy`) are unconditional
(`oks/oks/object.h:601,937,1155`). Searched `oks/` and `config/` for `read_only`,
`readonly`, `const`-only access modes: no such mode found.

**Confidence: Confirmed** that no API-level read-only enforcement exists.

**Implication for the MCP prototype.** Read-only must be enforced **by the MCP itself** — by
not exposing mutating operations — because the libraries will not enforce it. See
document `04` §C4.

## 12. The second, distinct historical mechanism: the CORAL "OKS Archive"

This must not be conflated with the Git mechanism. `oks2coral` archives OKS **files** into a
CORAL relational store, keyed by run number, with **integer** version numbers:

> `oks2coral/oks2coral/ConfigVersions.h:15–19, :23–30`
> ```
> The class is used to store archive versions of the OKS database used for given run.
> ...
> int SchemaVersion;   // The version of the schema from OKS Archive.
> int DataVersion;     // The version of the data from OKS Archive.
> ```

It obtains the run number from IS (`oks2coral/src/oks2coral.cpp:217–233`, reading
`RunParams.RunParams`), or parses it from a filename with the convention
**`RunNumber.PartitionName.TimeStamp.data.xml`** (`oks2coral/src/oks2coral.cpp:238–258`),
and publishes `RunParams.ConfigVersions` back to IS
(`oks2coral/src/oks2coral.cpp:776–792`).

**What this proves.** There are **two** historical schemes in this release, with different
identifiers:

| Scheme | Version identity | Keyed by | Component |
|---|---|---|---|
| OKS Git repository | Git SHA / tag / date | partition, run (via tag & `CONFIGVERSION`) | `oks`, `rn` |
| CORAL "OKS Archive" | integer `SchemaVersion`/`DataVersion` | run number | `oks2coral` |

The `rn` table carries columns for **both** (`CONFIGSCHEMA`/`CONFIGDATA` integers *and*
`CONFIGVERSION` SHA — `rn/src/lib.cpp:81–83`), which indicates the integer scheme is the
older of the two and the SHA scheme the current one. That ordering is
**Strongly indicated**, not Confirmed — no document in the release states which supersedes
which.

**Implication for the MCP prototype.** Target the **Git** scheme. It is the one the current
code writes on every run, the one `config::Configuration` models
(`ConfigVersion.h`), and the one reachable without a CORAL dependency. Ask the experts
whether the CORAL archive is still populated (§14).

## 13. Confirmed facts

1. Configuration revisions are **Git commits**; the version id at the `config` layer is
   documented as a Git SHA. `config/config/ConfigVersion.h:47–52`.
2. Revision selection is `TDAQ_DB_VERSION="<tag|date|hash>:<value>"`, parsed by
   `OksKernel::parse_config_version()`. `oks/src/kernel.cpp:757, :930–940`.
3. Retrieval is ordinary `git clone` + `git checkout` via `oks-checkout.sh`, into a
   temporary per-kernel directory. `oks/src/kernel.cpp:5945–5997`; `oks/scripts/oks-checkout.sh:154–233`.
4. Schema and data share one revision (one repository, one checkout). §7.
5. At run start the OKS Git SHA is captured into the run-number DB as `CONFIGVERSION`, with
   `CONFIGNAME` and `PARTITIONNAME`. `rn/src/lib.cpp:149, :251–274`.
6. The OKS repository is **tagged `r<run>@<partition>`** at run start. `rn/src/lib.cpp:100–107, :313–318`.
7. Capture and tagging are **conditional and best-effort**; `CONFIGVERSION` may be NULL and
   the tag may be missing. `rn/src/lib.cpp:148, :252, :108–111`.
8. Loading a historical revision uses the ordinary load path. §9.
9. No API-level read-only protection exists. §11.
10. A second, integer-versioned CORAL archive exists (`oks2coral`). §12.

## 14. Unknowns and questions for ATLAS/TDAQ experts

**Not established from the new-release repository:**

1. **Programmatic run → revision lookup.** Nothing reads back the mapping `rn` writes.
   *Searched:* `rn/`, `config/`, `dal/`, `oks/`. *Missing:* a client API and the
   `TDAQ_RUN_NUMBER_CONNECT` endpoint.
2. **The identity and hosting of the OKS configuration repository.** `TDAQ_DB_REPOSITORY` is
   read at runtime; no default value appears in the release. See document `06`.
3. **Whether the `r<run>@<partition>` tags actually exist in the production repository**, and
   whether they are pruned. The code creates them best-effort on a background thread.
4. **Whether the deployed `RunNumber` table matches the code's column names**, given
   `create_db.sql` is stale (§3).
5. **Whether the CORAL OKS Archive is still populated**, or is superseded by the Git scheme.

**Questions for the meeting:**

- Is there a supported service or API to resolve *run number → OKS Git SHA*, or should the
  MCP read the run-number database directly? What are the access credentials and endpoint?
- Are `r<run>@<partition>` tags reliably present for physics runs? Is relying on them
  acceptable, given tagging is best-effort on a background thread?
- Which repository is `TDAQ_DB_REPOSITORY` in production, and can a read-only MCP service be
  granted clone access?
- Is the CORAL "OKS Archive" (`oks2coral`) still in use, or historical?
- For runs where `CONFIGVERSION` is NULL, is there any other way to recover the configuration?

## 15. Evidence index

| File | Symbols / lines |
|---|---|
| `rn/src/lib.cpp` | column names :80–85; `TagRepository` :87–113; version capture :148–150; DB write :251–256; `CONFIGNAME` :258–274; tag trigger :313–318 |
| `rn/src/create_db.sql` | `RunNumber` table :5–17 (stale — see §3) |
| `rn/rn/rn.h` | `RunNumber` class :63–142; `get_number()` :112 |
| `dal/src/algorithms.cpp` | `get_config_version()` :3289–3327; `set_config_version()` :3330+ |
| `dal/data/is/oks-version.schema.xml` | IS class `ConfigVersion`, attribute `Version` |
| `oks/src/kernel.cpp` | `get_repository_root` :330–373; `parse_config_version` :757–773; ctor version handling :925–958; `k_checkout_repository` :5937–5997; `update_repository` :6064; `commit_repository` :6127; `tag_repository` :6278; `get_repository_versions_diff` :6315; `get_repository_versions` :6395–6484 |
| `oks/oks/kernel.h` | ctor :604; `OksRepositoryVersion` :516–531; `get_modified_files` :1564–1573; repository API :1586–1700 |
| `oks/scripts/oks-checkout.sh` | arg parsing :44–110; `git clone` :155; `git checkout` :172–206; version echo :233 |
| `oks/scripts/oks-log.sh` | `git fetch --all` :81–82; `git log --first-parent --name-only` :90–91 |
| `oks/scripts/oks-update.sh` | `git checkout` :138–181; `git rev-list --before` :157 |
| `config/config/ConfigVersion.h` | `QueryType` :33–37; SHA-is-id :47–52 |
| `config/config/Configuration.h` | `get_versions()` / `get_changes()` :1258–1283 |
| `oks2coral/oks2coral/ConfigVersions.h` | archive versions :15–30 |
| `oks2coral/src/oks2coral.cpp` | run number from IS :217–233; filename convention :238–258; IS check-in :776–792 |
| `dal/data/schema/core.schema.xml` | class `Partition` |
