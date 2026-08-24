# 06 — Git and Configuration Repository Access (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

---

## 1. Executive summary

**The configuration system uses ordinary Git, through the `git` command-line binary, via
shell scripts. It does not use any Git hosting provider's API, and it does not link any Git
library.**

This is a strong negative result, and the prompt specifically warns against getting it
wrong. Stated precisely:

- **No provider API.** Searching the OKS/config/DAL/run-number source for `gitlab`, `gitea`,
  `github`, `bitbucket` returns **zero hits**.
- **No Git library.** `oks` links `daq_tokens`, `osw`, `ers`, Boost, `tbbmalloc`,
  `stdc++fs`, `pam` — no `libgit2` or equivalent anywhere in the release.
- **Plain `git` subprocesses.** `OksKernel` builds a command string and calls `system()`;
  the target is one of eleven `oks-*.sh` scripts that run `git clone`, `git checkout`,
  `git log`, `git diff`, `git pull -r`, `git rev-list`, `git tag`.
- **The repository is just a URL.** `TDAQ_DB_REPOSITORY` may hold *several* URLs separated
  by `|`, and `OKS_GIT_PROTOCOL` selects which one by prefix — a **protocol** switch
  (https / ssh / file), **not** a provider abstraction.

The correct conclusion for the MCP is therefore the one the prompt cautions toward:
**an MCP server needs Git clone/checkout access to a repository URL — nothing more, and
specifically not a GitLab API client.**

## 2. Git architecture

```
 config::Configuration                        (no Git code)
        │
 OksKernel  ── builds command string ──► system()          oks/src/kernel.cpp:5978-5980
        │                                    │
        │                                    ▼
        │                            oks-checkout.sh   ─┐
        │                            oks-update.sh      │
        │                            oks-commit.sh      ├─► /usr/bin/git
        │                            oks-tag.sh         │
        │                            oks-log.sh         │
        │                            oks-diff.sh       ─┘
        │                                    │
        └──── parses stdout back ◄───────────┘          oks/src/kernel.cpp:5991-5997
```

The eleven scripts (`oks/scripts/`, installed by `tdaq_add_scripts(scripts/*)` —
`oks/CMakeLists.txt:18`):

`oks-checkout.sh`, `oks-commit.sh`, `oks-copy.sh`, `oks-diff.sh`, `oks-edit-branch.sh`,
`oks-import.sh`, `oks-log.sh`, `oks-status.sh`, `oks-tag.sh`, `oks-update.sh`,
`oks-version.sh`.

**Evidence that C++ invokes them as subprocesses:**

> `oks/src/kernel.cpp:5945` — `std::string cmd("oks-checkout.sh");`
> `oks/src/kernel.cpp:5978–5979`
> ```cpp
> CommandOutput cmd_out("oks-checkout", this, cmd);
> cmd_out.check_command_status(system(cmd.c_str()));
> ```

and the other entry points build their commands the same way:
`oks-copy.sh` (`:6021`), `oks-update.sh` (`:6064`), `oks-commit.sh` (`:6127`),
`oks-tag.sh` (`:6278`), `oks-diff.sh` (`:6325`), `oks-log.sh` (`:6397`).

**Results come back by parsing stdout**, not through an API:

> `oks/src/kernel.cpp:5991–5997`
> ```cpp
> static std::string version_prefix("checkout oks version ");
> std::string version = cmd_out.last_str();
> std::string::size_type pos = version.find(version_prefix);
> if (pos == 0) p_repository_version = version.substr(version_prefix.size());
> else throw oks::RepositoryOperationFailed("checkout", "cannot read oks version");
> ```
> matching `oks/scripts/oks-checkout.sh:233` — ``echo "checkout oks version `git rev-parse HEAD`"``

and for the version log:

> `oks/src/kernel.cpp:6427` — an error if the *"git log"* pattern is not found in
> `oks-log.sh` output; `:6484` — an error on an unexpected line.

**Confidence: Confirmed.**

**Implication.** The integration contract between OKS and Git is **textual and fragile**:
C++ parses human-oriented script output. An MCP that shells out to the same scripts inherits
that fragility; an MCP that calls `OksKernel` (through `config`) lets OKS do the parsing.
This is an argument for the `pyconfig` boundary recommended in document `05`.

## 3. Provider evidence

### F1 — Which Git hosting provider is evidenced?

**None, in the code.**

*What was searched:* case-insensitive `gitlab|gitea|github|bitbucket` across
`oks/src`, `oks/oks`, `oks/bin`, `oks/scripts`, `config/src`, `config/config`, `dal/src`,
`rn/src`. **Result: zero matches.**

The only provider references in the release are in **project metadata**, not configuration
code — the superproject `README.md` names
`https://gitlab.cern.ch/atlas-tdaq-software` as where *the TDAQ software source* lives, and
`.gitmodules` uses relative URLs (`../<package>.git`) for the *software* packages. **That is
the software repository, not the OKS configuration repository.** Conflating the two is
exactly the error the prompt warns about.

**Confidence: Confirmed** that the configuration-access code is provider-agnostic.

**The identity of the production OKS configuration repository is
Not established from the new-release repository.** *Searched:* every `.sh` in `oks/scripts/`,
`oks/src/kernel.cpp`, `oks/bin/*.cpp`, and all CMake files for a default or example value of
`TDAQ_DB_REPOSITORY`. *Missing:* any default; the value is supplied entirely by the runtime
environment.

### F2 — Ordinary Git, provider REST API, provider SDK, or Git library?

**Ordinary Git, through the CLI.**

| Candidate | Verdict | Evidence |
|---|---|---|
| Provider REST API | **No** | No provider names; no HTTP client in `oks` (`oks/CMakeLists.txt:7–12` links no curl) |
| Provider SDK | **No** | Same |
| Git library (libgit2 etc.) | **No** | Searched `oks`, `config`, `dal` for `libgit2`, `git2`: zero hits. `oks` links only `daq_tokens osw tdaq-common::ers Boost::thread Boost::date_time ${TBBMALLOC} stdc++fs pam` (`oks/CMakeLists.txt:9–12`) |
| Ordinary `git` CLI | **Yes** | §2, and the raw commands in §4 |

Corroborating: `git` is declared as a release **external**
(`CMakeLists.txt:13–21`, `EXTERNALS ... git`), consistent with a runtime binary dependency.

**Confidence: Confirmed.**

### F3 — How are historical revisions accessed?

By `git checkout` of a tag, a commit hash, or a date-derived hash — see document `03` §8.
The raw operations, quoted from the scripts:

| Operation | Command | Location |
|---|---|---|
| Clone | `git clone -q -n "${git_repo}" .` | `oks-checkout.sh:155` |
| Configure rebase pulls | `git config pull.rebase true` | `oks-checkout.sh:164` |
| Checkout tag | `git checkout -q -B ${branch} tags/${tag}` | `oks-checkout.sh:172, :174` |
| Date → hash | `hash=$(git rev-list -1 --before="${date}" "${branch}")` | `oks-checkout.sh:191` |
| Default to remote head | `git ls-remote --exit-code --heads origin "$branch"` then `hash="origin/${branch}"` | `oks-checkout.sh:200–203` |
| Report revision | `git rev-parse HEAD` | `oks-checkout.sh:233` |
| Update | `git checkout` with `--discard`/merge options; `git rev-list -1 --before` | `oks-update.sh:138–181` |
| History | `git fetch --all` then `git log -m --date=raw --pretty=format:"%H\|%an\|%ad\|%s" --first-parent ${TDAQ_DB_BRANCH:-master} --name-only` | `oks-log.sh:81–91` |
| Commit | `git rev-parse --abbrev-ref HEAD`, `git checkout -b $temp`, `git pull --no-edit -r origin $branch` | `oks-commit.sh:172–179, :87–88` |

**Confidence: Confirmed.**

Two details worth carrying forward:

- **The log format is machine-parsed**: `%H|%an|%ad|%s` with `--name-only` populates
  `OksRepositoryVersion{m_commit_hash, m_user, m_date, m_comment, m_files}`
  (`oks/oks/kernel.h:516–531`; parsed at `oks/src/kernel.cpp:6395–6484`). So *"which files
  changed in which revision, by whom, when"* is available as structured data through
  `Configuration::get_versions()` — useful for an MCP that must explain provenance.
- **`--first-parent` on a configurable branch** means history is linearised along
  `${TDAQ_DB_BRANCH:-master}`; revisions on side branches are not listed.

### F4 — Is there an existing abstraction over Git providers?

**No provider abstraction. There is a *protocol* selection mechanism, which is a different
thing and must not be mistaken for one.**

> `oks/src/kernel.cpp:337–369`
> ```cpp
> if (const char * s = getenv("TDAQ_DB_REPOSITORY"))
>   {
>     std::string rep(s);
>     if (!std::all_of(rep.begin(), rep.end(), [](char c) { return std::isspace(c); }))
>       {
>         const char * p = getenv("OKS_GIT_PROTOCOL");
>         if (p && !*p) p = nullptr;
>         Oks::Tokenizer t(rep, "|");
>         std::string token;
>         while (t.next(token) && p_repository_root.empty())
>           {
>             if (p) { if (token.find(p) == 0) { p_repository_root = token; } }
>             else   { p_repository_root = token; }
>           }
>         if (p_repository_root.empty())
>           Oks::error_msg("OksKernel::OksKernel")
>             << "cannot find OKS_GIT_PROTOCOL=\"" << p << "\" in TDAQ_DB_REPOSITORY=\"" << rep << '"' << std::endl;
>       }
>   }
> ```

**What this proves.** `TDAQ_DB_REPOSITORY` is a `|`-separated list of repository URLs. If
`OKS_GIT_PROTOCOL` is set, the first URL whose text *starts with* that string is chosen;
otherwise the first URL wins. The selector is a **prefix match on the URL**, so it selects
`https://…` vs `ssh://…` vs `/local/path` — a transport choice. Nothing inspects the host or
adapts behaviour per provider.

A helper executable exposes the resolved value to the shell scripts:

> `oks/bin/oks_git_repository.cpp:26` — `std::cout << OksKernel::get_repository_root() << std::endl;`
> used as `git_repo=\`oks_git_repository\`` in `oks/scripts/oks-checkout.sh:16`.

There is also a **path-mapping** mechanism, `OKS_REPOSITORY_MAPPING_DIR`
(`oks/src/kernel.cpp:377–390`), used to turn absolute paths into repository-relative names
(`rn/src/lib.cpp:266–270`) — again, not a provider abstraction.

**Confidence: Confirmed.**

**Is a provider abstraction justified by repository evidence?** **No.** Building one would
add a layer the TDAQ code itself does not have. If the MCP needs Git, it needs
clone/checkout against a URL.

## 4. F5 — What would an MCP server actually need?

Derived from the evidence above and document `03`:

| Need | Why | Evidence |
|---|---|---|
| A **repository URL** for the OKS configuration repo | `TDAQ_DB_REPOSITORY` has no default | §3 F1 |
| **Read (clone) access** to it | `oks-checkout.sh` does a full `git clone` | `oks-checkout.sh:155` |
| A **`git` binary on `PATH`** | scripts invoke `git` directly | §3 F2 |
| The **`oks-*.sh` scripts on `PATH`** | `OksKernel` calls them by bare name via `system()` | `oks/src/kernel.cpp:5945` |
| **Writable temp space** | each kernel clones into a fresh user-repository dir | `oks/src/kernel.cpp:945–948` |
| `TDAQ_DB_VERSION` set **before** the kernel is constructed | the checkout happens in the constructor | `oks/src/kernel.cpp:930–958` |
| **No** provider credentials/tokens for reading | no provider API is used | §3 F2 |

**What it does *not* need:** a GitLab account, a GitLab API token, a provider SDK, or a
provider abstraction layer.

**Cost note, Confirmed from the code:** `oks-checkout.sh` performs a **full `git clone`**
(`:155`) into a **new temporary directory per kernel** (`oks/src/kernel.cpp:945`). A naive
MCP that constructs a `Configuration` per request would clone the entire configuration
repository per request. Caching checkouts per revision is an **engineering requirement**
this evidence implies — flagged as a proposal, not a repository fact.

## 5. Repository storage vs application-level configuration resolution

The prompt asks these be distinguished. They are genuinely different in this release:

| Layer | What it is | Identifier | Evidence |
|---|---|---|---|
| **Repository storage** | A Git repository of OKS XML files, at a URL | Git SHA / tag / date | `oks-checkout.sh`; `TDAQ_DB_REPOSITORY` |
| **Application-level resolution** | *Which* configuration inside that repository, and which revision, apply to a run | `CONFIGNAME` (file path) + `CONFIGVERSION` (SHA) + `PARTITIONNAME`, and tag `r<run>@<partition>` | `rn/src/lib.cpp:251–274, :100–107` |

Git answers *"give me the files as of revision X"*. It does **not** answer *"which revision
did run N use"* — that association is created by the run-number service and stored in a
database and a tag (document `03` §3). An MCP must implement the second layer; the first is
already implemented.

**Confidence: Confirmed.**

## 6. MCP implications

1. **Do not build a provider client.** Use Git, or better, let `OksKernel` use Git for you by
   setting `TDAQ_DB_VERSION` and letting `config`/`oksconfig` do the checkout (document `05`).
2. **Budget for clone cost.** Full clone per kernel; cache per revision.
3. **Historical answers can cite provenance.** `Configuration::get_versions()` yields SHA,
   author, date, comment and changed files — an MCP can explain *why* it selected a revision.
4. **Ensure the environment.** `git` and `oks-*.sh` on `PATH`, writable temp space,
   `TDAQ_DB_REPOSITORY` set — otherwise `OksKernel` fails at construction with
   `RepositoryOperationFailed`.
5. **Read-only is the default posture.** No push happens without an explicit
   `commit_repository()`; the MCP simply never calls it (document `04` §C4).

## 7. Unknowns

1. **The production repository URL and transport.** Not established (§3 F1). Expert question.
2. **Whether read access requires authentication** (Kerberos, SSH key, token). The scripts
   do not authenticate; they rely on the ambient Git configuration.
   **Not established from the new-release repository.**
3. **Repository size and clone time** — determines whether per-request clones are viable.
   Not established.
4. **Whether `r<run>@<partition>` tags are pruned or retained indefinitely** (document `03` §14).
5. **Whether a server-side hook enforces `oks_validate_repository`** on push
   (document `04` §D4).

## 8. Questions for ATLAS/TDAQ experts

- What is `TDAQ_DB_REPOSITORY` in production, and which `OKS_GIT_PROTOCOL` value should a
  read-only service use?
- How is read access authenticated, and can a service account be issued?
- How large is the configuration repository, and is a cached shared clone acceptable rather
  than a clone per request?
- Are `r<run>@<partition>` tags retained for all historical runs?

## 9. Evidence index

| File | Symbols / lines |
|---|---|
| `oks/src/kernel.cpp` | `get_repository_root` + `OKS_GIT_PROTOCOL` :337–369; `OKS_REPOSITORY_MAPPING_DIR` :377–390; temp user repo :945–948; ctor checkout :930–958; `oks-checkout.sh` cmd :5945, `system()` :5978–5980, stdout parse :5991–5997; `oks-copy.sh` :6021; `oks-update.sh` :6064; `oks-commit.sh` :6127; `oks-tag.sh` :6278; `oks-diff.sh` :6325; `oks-log.sh` :6397; log parsing :6395–6484 |
| `oks/oks/kernel.h` | `OksRepositoryVersion` :516–531; repository API :1586–1700 |
| `oks/CMakeLists.txt` | library link list :9–12; executables :14–17; `tdaq_add_scripts` :18 |
| `oks/bin/oks_git_repository.cpp` | prints repository root :26 |
| `oks/scripts/oks-checkout.sh` | `oks_git_repository` :16; branch default :30; `git clone` :155; `pull.rebase` :164; checkout/tag :172–174; `rev-list --before` :191; remote-head fallback :200–203; `rev-parse HEAD` :233 |
| `oks/scripts/oks-log.sh` | `git fetch --all` :81–82; `git log` format :90–91 |
| `oks/scripts/oks-update.sh` | checkout options :138–181; `rev-list --before` :157 |
| `oks/scripts/oks-commit.sh` | undo paths :43–75; `git pull -r` :87–88; branch/temp :172–179 |
| `rn/src/lib.cpp` | mapping-dir strip :266–270; `CONFIGVERSION`/`CONFIGNAME` :251–274; tag :100–107 |
| `CMakeLists.txt` (superproject) | `EXTERNALS ... git` :13–21 |
| `README.md` (superproject) | `gitlab.cern.ch/atlas-tdaq-software` — the *software* repo, not the configuration repo :8–11 |
