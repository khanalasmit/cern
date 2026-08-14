# FINAL REPORT — OKS query-language documentation harvest

Goal: produce a comprehensive corpus about the OKS (Object Kernel Support)
configuration database and its query language, to be used as reference for
writing a DUNE-DAQ OKS-query fine-tuning dataset (English question ->
OKS query string).

Date of harvest: 2026-08-08. Working dir: `D:\document\projects\minor\oks_scraped\`

## 1. Deliverables (files written)

| File | Content |
|---|---|
| `01_dune_oks_code.md` | DUNE-DAQ/oks fork: query grammar (this/all, and/or/not, some/all, = != < <= > >= ~=, object-id), query classes (`oks_query`, list + *descendant classes*), `oks_dump` options/exit codes, git-versioning API (`get_repository_versions`, tags), Python bindings, README `oks lls/lns/lkm` commands. |
| `02_dune_dal_code.md` | DUNE-DAQ/dal: directory layout, `oks` schema (schema classes, attributes, relationships, child classes), tutorial schema/data + `tutorial.py`, `dalconverter`, `dalcli`, ConfigVersion & IS pattern docs. |
| `03_papers.md` | CHEP-2008 config-service (DAL) paper: query-string examples IR, DB design (xor/vector, comments, history, versioning); L1Calo DB guide extracted as `pdfs/p11_*`; status of EPJ-403 / CDS queries (blocked). |
| `04_indico_tutorials.md` | Five captured indico PDFs (DAQ-for-experts 1815, Bianchi EPS-2011 poster, ID training 2016, GM overview, talk 332) with page maps; restricted events listed. |
| `05_cern_gitlab.md` | Public CERN GitLab: oks, oks_utils, swrod, oks2coral; release-notes facts (tdaq-01-02-00 path query, tdaq-01-09-00 `~=` regex, repos versions); release-notes site; GitLab tags API sample output. |
| `06_shifter_manuals.md` | Shifter-facing corpus: DBE page, OKS Data Editor online help (all windows, incl. QueryWindow save/load semantics), Nevis wiki notes; twiki gap flagged. |
| `oks_schema_examples.xml` | Copy-ready XML: schema example (fleet/car tutorial + DUNE core/DAQ-Configuration snippets) + data example with provenance captions. |
| `oks_query_examples.md` | Grammar BNF, English->query table (attrs, rels, object-id, path queries), git-version queries, comparators C++ enum, GUI semantics, errors/exit codes, provenance map. |
| `access_status.md` | What was captured vs blocked vs not yet tried. |

## 2. Raw captures retained

- `pdfs/` p1 IOPS paper + extract, p11 QMUL L1Calo guide + extract
- `indico/` five PDFs + text extracts
- `repos/` original github/cern files: schemas (tutorial, test.data, swrod,
  core, all_types, DAQ-Configuration, default-parameters, dal_testing),
  tutorial.py, online-help/data-editor/* (full Data Editor help tree)

## 3. Facts pinned down (worth gold-labeling in the fine-tuning set)

- Query file format = plain text, Lisp-like; GUI can save/load query files
  (QueryWindow.html: "The format of the query file is simple... edit
  manually by any text editor").
- `(this ...)` = class-only vs `(all ...)` = class + subclasses.
- `some` = at least one diagram object referenced, `all` = every referenced.
- Only `=` allowed for `object-id` when comparing.
- `~=` gained in oks tdaq-01-09-00 (regex compare).
- Values are always *quoted strings*; type interpretation is weak (numeric vs
  string only matters at runtime).
- Exit codes of `oks_dump`: 0 ok, 1 CLI, 2 file, 3 query, 4 class, 5 dangling.
- Git versioning selectors: `tag:r380689@all_hosts`, `hash:`, `date:...` in
  `oks_clone_repository`; `get_repository_versions()`.
- Path-query syntax `(path-to ... (direct ... nested ...))` verified both from
  OK sources and from RELEASE_NOTES tdaq-01-02-00.

## 4. Gaps / risks

- Authoritative spec is prose (README, QueryWindow.html, RELEASE_NOTES);
  no formal grammar file exists. Grammar in `oks_query_examples.md` is
  reconstructed — keep it labeled as such.
- twiki + atlasop pages require SSO; not harvested.
- One attempted paper (EPJ 403) is not retrievable; if needed, use L1Calo
  guide + DBAL chapter as substitute grounding.

## 5. Suggested next step

1. ~~From `oks_query_examples.md` build a gold set of 100-300 (question, query)
   pairs covering: attribute ops, rel some/all, object-id, nested, path,
   version.~~ -> DONE: `gold_pairs.jsonl` (50 rows, JSONL schema
   `{question, query_oks, note, source_file}`), covering '='/'!='/'~='/'<'/'<='
   '/'>'/'>=', this/all scopes, and/or/not, rel some/all, object-id, nested
   rels, path-to queries, version selectors tag:/hash:/date:, oks_dump CLI and
   exit codes, GUI/weak-typing facts. Grounded in `repos/tutorial.schema.xml`,
   `repos/test.data.xml`, QueryWindow.html and CERN RELEASE_NOTES; rows marked
   "illustrative" are syntax-correct but use invented attribute names.
2. Use `oks_dump -f <file> -c <cls> -q '<query>'` on copied `repos/*.data.xml`
   to validate each pair end-to-end.
3. Optionally ship a final fine-tuning JSONL with schema `{question, query_oks,
   note, source_file}`.