# -*- coding: utf-8 -*-
# Renderer for 05-release-notes.md: ATLAS TDAQ OKS/config release notes rescued from the Wayback Machine
# (site pcatd12.cern.ch is dead as of 2026-08-08: direct fetch -> transport error; browser -> HTTP 500 "proxy 590 UPSTREAM502").
import glob, io, os, re

SRC = r"output\extracts\pcatd12"
OUT = r"output\05-release-notes.md"

def text_of(path):
    with io.open(path, "r", encoding="latin-1") as f:
        raw = f.read()
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

def block(path):
    fn = os.path.basename(path)
    return (f"### Snapshot `{fn}`\n"
            f"*Local file: `output/extracts/pcatd12/{fn}`*\n\n"
            f"```text\n{text_of(path)}\n```\n\n")

oks_files = sorted(glob.glob(os.path.join(SRC, "oks__*.html")))
cfg_files = sorted(glob.glob(os.path.join(SRC, "config__*.html")))
doc_files = sorted(glob.glob(os.path.join(SRC, "doxygen__*.html")))
jav_files = sorted(glob.glob(os.path.join(SRC, "javadoc__*.html")))

parts = []
parts.append("""> Generated 2026-08-08 by automated extraction renderer (`output/build_05.py`).
> The original site `pcatd12.cern.ch` no longer responds: direct fetch fails with a transport error, and a real-browser attempt returns HTTP 500 ("proxy 590 UPSTREAM502: 0 bytes"). All pages below were therefore recovered from the Internet Archive Wayback Machine via the CDX API (`https://web.archive.org/cdx/search/cdx?url=pcatd12.cern.ch&matchType=domain&...`) and fetched as snapshots with the `id_` flag (raw archived content, no Wayback overlay).
>
> These are the original per-package release-notes pages of the CMT-era ATLAS TDAQ build (`nightly/oks/doc/`, `nightly/config/doc/`), preserved in the 2011-2012 nightly snapshots. They predate - and are complementary to - the modern `doc/RELEASE_NOTES.md` of the current `oks` GIT repository (already embedded in `03-cern-gitlab.md`, which covers the `oks-02-07-02` .. `oks-08-04-00` era). Together they form a continuous OKS 1.x/2.x timeline.

## 1. `oks` package release notes (13 pages, archived 2011-11-07)

""")

def group(files):
    return "".join(block(f) for f in files)

parts.append(group(oks_files))
parts.append("""## 2. `config` package release notes (12 pages, archived 2011-11-06)

The `config` package is the ATLAS 2011-2014 configuration program (and the config-data legacy library `Config` on which the DAL was layered); before OKS took over it held the configuration database APIs.

""")
parts.append(group(cfg_files))
parts.append("""## 3. Doxygen `ConfigPackages` pages (5 snapshots, 2011-2012)

`ConfigPackages` is the Doxygen "main page" of the Config package documentation; each snapshot corresponds to one TDAQ version, content extracted with navigation boilerplate intact. Versions: `nightly` (20110326220841), `tdaq-02-00-03` (20110327163333), `tdaq-03-00-01` (20110326094004), `tdaq-04-00-00` (20111027092808), `tdaq-04-00-01` (20110124154520).

""")
parts.append(group(doc_files))
parts.append("""## 4. Javadoc of the `config` API (3 pages)

The Java `config` API documentation (subset most relevant to OKS/DAL usage and the query machinery): `package-summary.html` (20110707223035), `Query.html` (20110322202710), `BadQueryException.html` (20110322185043).

""")
parts.append(group(jav_files))
parts.append("""## 5. Observations

- The oldest OKS release note preserved here is `tdaq-01-01-00` (2011): it documents the `$(FOO)` environment-variable syntax change for filenames (`${FOO}` -> `$(FOO)`), the query heap-allocation fix, and new `oks_dump` options `--files-only`, `--class`, `--query`.
- `config` release notes cover `tdaq-01-01-00` .. `tdaq-03-00-00`; the last archived OKS note is `tdaq-04-00-00`. Later notes (05-00-00+) were never archived on this site (verified via CDX with prefix filters); coverage continues in the GIT-era `ooks` repo release notes (see 03-cern-gitlab.md).
- Together the archived pages and the GIT-repo notes document: `tdaq-01-01-00` .. `tdaq-04-00-00` (archived, 2011-2012) => git-era `oks-02-07-02` (2018) .. `oks-08-04-00` (2024).
- The `config` release notes show the pre-OKS era: the `Configuration`/`ConfigObject` APIs were the DB abstracted config data interface that OKS replaced/absorbed; the DAL (see 02-dune-dal.md) was introduced on top of it.
""")

doc = f"""# Source 5: ATLAS TDAQ release notes for the OKS and Config packages (archived via Wayback Machine)

> Rendered by `output/build_05.py`; all blocks are text-extracted from archived HTML pages (snapshot timestamps in each heading). The original site `pcatd12.cern.ch` is dead; the raw snapshot files are preserved in `output/extracts/pcatd12/`.

{''.join(parts)}"""
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("wrote", OUT, os.path.getsize(OUT), "bytes")