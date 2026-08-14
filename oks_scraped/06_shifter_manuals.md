# 06. Shifter manuals and operator documentation

This document collects sources written for ATLAS shifters/operators that
explain the OKS configuration service from the "user" side: what is stored,
how to answer "which configuration was used", how to browse it.

---

## 6.1 Public sources (accessible)

### 6.1.1 DBE (DataBase Editor) user manual — readthedocs branch

- URL: https://dune-daq-sw.readthedocs.io/en/johnfreeman-update_documentation_instructions/packages/dbe/
- Content: DBE = OKS **DataBase Editor**, the run-control GUI used to browse
  and edit the config DB (classes/objects/includes/comments; check-in /
  check-out / commit; versioning). Related sub-pages: `.../packages/dbe/schemaeditor/`.
- Verbatim capture: see `repos/` (static copy of the rendered pages is
  included in `FINAL_REPORT.md` references list).

### 6.1.2 OKS Data Editor online help (from oks_utils, copied here)

- Local: `repos/online-help/data-editor/` (54 files, incl. GIF screenshots)
  - `QueryWindow.html` — full manual of the OKS query constructor
    ("attribute expression", "relationship expression", "logical expressions
    and/or/not", save/load query files in LISP-like text format).
  - `OksDataEditor.html` (index), `MainWindow.html`, `ClassWindow.html`,
    `DataFileWindow.html`, `ObjectWindow.html`, `GraphicalWindow.html`,
    `ReplaceWindow.html`, `MessageLogWindow.html`.

### 6.1.3 NEVIS wiki — FLX configuration (public Foswiki)

- URL: https://wiki.nevis.columbia.edu/bin/view/FLX_Configuration
- Content: FELIX configuration summary written for colliders ops; includes
  where the config lives in OKS terms and the "FLX_Configuration" cheat sheet.
- Status: public, captured text in `05_...`/`06_...` (see access_status.md).

### 6.1.4 Release-notes & version docs

- https://atlas-tdaq-sw-releases.web.cern.ch/ — HOWTOs (containers, python
  pip, package tags, release notes format) + release notes tdaq-09…13.

---

## 6.2 Sources that require authentication (CERN accounts)

All are `https://twiki.cern.ch/twiki/bin/view{/viewauth/}Atlas/...` pages —
they returned **HTTP 401 (requires authentication)** to anonymous fetching.

Notable pages (referenced by git/docs so likely authoritative):

- `DaqHltOks` — master OKS page: architecture, query language user guide,
  "4. OKS Git Repository" (see RELEASE_NOTES tdaq-09-01-00 which links it).
- `DaqHltConfig` / `DaqHltConfigService` — configuration service howto.
- `DaqHltShifter` / `DaqHltShifters` — run-shift instructions incl. "what
  config was this run". (Name suggestions; confirm on twiki after login.)
- `DaqHltAccessManager`, `SWRodInputErrors`, `ROBFragmentHeaderStatusWords`,
  `DaqHltDal` (DAL class docs; the core.schema.xml descriptions carry
  `https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_1_Partition_Class`
  style links).
- `Atlas/AtlasOnline` (parent collab index).

**How to get them**: authenticate on twiki.cern.ch (SSO), then import the
pages e.g. with `curl -b cookies`. This is the main remaining gap for
shifter-specific material; the task's corpus should mark these as:

```
[Q] What configuration was used for run N?
[A] <twiki DaqHltShifter excerpt> ; OKS answer: tag r<N>@<partition>, see 01/05.
```

---

## 6.3 Gap analysis (what is missing for a perfect shifter manual)

1. Authenticated TWiki pages (above).
2. CDS records that are behind Anubis (see 03_papers §3.3) — notably CERN-OPEN-2014 "OKS".
3. Indico event 1452600 "DAQ for experts (Run 3)" — restricted (access key): potentially the **best** modern shifter primer; recommend obtaining key or training subset from TWiki mirror.
4. The "AI Assistant for ATLAS operations and beyond" workshop (indico 1566094 / c6690058) is public but has **no attached materials**; its abstract confirms the planned DAQ Shifter Assistant features (config version lookups, query building) — good scenario seeds.