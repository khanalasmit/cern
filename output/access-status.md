# Access-status log for the OKS/DAL documentation extraction

> Status as of 2026-08-08. Per-source result of each access attempt, with exact error messages where access was blocked.

## Sources accessed successfully

| Source | What was retrieved | Status |
|--------|--------------------|--------|
| https://github.com/DUNE-DAQ/oks (develop) | Full clone; schema/data + README + docs | OK (git clone) |
| https://github.com/DUNE-DAQ/dal (develop) | Full clone; code + docs + schemas; documented in 02 | OK (git clone) |
| https://gitlab.cern.ch/atlas-tdaq-software/oks | Full clone (HEAD 2026-07-09); all files embedded in 03 | OK (git clone) |
| https://gitlab.cern.ch/atlas-tdaq-software/oks_utils | Full clone (HEAD 2025-08-18); examples, tutorial, help pages | OK (git clone) |
| https://gitlab.cern.ch/atlas-tdaq-software/swrod | Full clone (HEAD 2026-08-04) | OK (git clone) |
| https://gitlab.cern.ch/atlas-tdaq-software/oks2coral | Full clone (HEAD 2021-03-02) | OK (git clone) |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/ | DBE main page, dbe_main, schemaeditor pages | OK |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/daqconf/ | daqconf package page | OK |
| https://web.archive.org/cdx/search/cdx (Wayback CDX API) | Full index of pcatd12.cern.ch; used to locate release notes | OK |
| https://web.archive.org/web/<ts>id_/<url> (Wayback snapshots) | 33 archived pages of pcatd12.cern.ch (oks/config release notes, doxygen, javadoc) | OK |

## Sources blocked or partially blocked

| Source | Attempted | Result |
|--------|-----------|--------|
| https://pcatd12.cern.ch/releases/ (live site) | direct fetch | Transport error (connection refused) |
| https://pcatd12.cern.ch/cmt/releases/download/tdaq-02-00-00/RELEASE_NOTES.html (and other tdaq-* versions) | Direct fetch | HTTP 500 "Detected a session error / proxy 590 UPSTREAM502: 0 bytes" (via Apify rag-web-browser; 1 item returned, no content). Site is dead. |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/ | Direct fetch | HTTP 404 - all `packages/dal/*` URLs (README, DalReader, DalWriter, ConfigVersion, DAL-schema, DAL-test-schema, RELEASE_NOTES) are gone; the dal package was removed from the docs project and links from the dal GitHub README are dead. |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/dbe/ (DbeRoo subtree) | Direct fetch | HTTP 404 for the deep subtree pages (dbe/dbe/... lower-level pages); only the top-level dbe pages are available. |

## Notes

- All WayBack fetches used the `id_` flag (raw content) and passed a Mozilla UA; CDX queries with `matchType=domain`, `fl=original,timestamp`, `collapse=urlkey`, `filter=statuscode:200` worked best.
- The oldest OKS release-notes pages available in the archive: `nightly/oks/doc/RELEASE_NOTES.tdaq-01-01-00.html` (snapshot 20111107082403) .. `tdaq-04-00-00` (20111107082709); config package notes `tdaq-01-01-00` .. `tdaq-03-00-00` (snapshots 20111106134653-20111106134818). No `tdaq-05-00-00` or later notes ever archived on this site (CDX prefix filter confirmed); that era is covered by the GIT-era release notes (see 03-cern-gitlab.md).
- Raw HTML snapshot files are preserved under `output/extracts/pcatd12/` bound to the timestamps listed in `output/05-release-notes.md`.