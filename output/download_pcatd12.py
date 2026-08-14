# -*- coding: utf-8 -*-
# Fetch archived ATLAS TDAQ OKS/config release-notes pages from the Wayback Machine.
# Source site pcatd12.cern.ch is dead (2026-07-08: transport error / proxy 590 UPSTREAM502).
import io, os, time, urllib.request

OUTDIR = r"output\extracts\pcatd12"
os.makedirs(OUTDIR, exist_ok=True)

PAGES = [
    # (pkg, version-marker, timestamp, url)
    *[(f"oks", v, ts,
       f"http://pcatd12.cern.ch/cmt/releases/nightly/oks/doc/RELEASE_NOTES.{v}.html")
      for v, ts in [
          ("tdaq-01-01-00", "20111107082403"),
          ("tdaq-01-02-00", "20111107082427"),
          ("tdaq-01-04-00", "20111107082448"),
          ("tdaq-01-06-00", "20111107082509"),
          ("tdaq-01-07-00", "20111107082520"),
          ("tdaq-01-08-00", "20111107082539"),
          ("tdaq-01-08-03", "20111107082556"),
          ("tdaq-01-08-04", "20111107082611"),
          ("tdaq-01-09-00", "20111107082613"),
          ("tdaq-02-00-00", "20111107082627"),
          ("tdaq-02-00-01", "20111107082647"),
          ("tdaq-02-01-00", "20111107082657"),
          ("tdaq-04-00-00", "20111107082709"),
      ]],
    ("config", "tdaq-01-01-00", "20111106134653",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-01-00.html"),
    ("config", "tdaq-01-02-00", "20111106134706",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-02-00.html"),
    ("config", "tdaq-01-04-00", "20111106134711",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-04-00.html"),
    ("config", "tdaq-01-06-00", "20111106134722",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-06-00.html"),
    ("config", "tdaq-01-06-02", "20111106134740",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-06-02.html"),
    ("config", "tdaq-01-07-00", "20111106134757",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-07-00.html"),
    ("config", "tdaq-01-08-00", "20111106134758",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-08-00.html"),
    ("config", "tdaq-01-08-03", "20111106134804",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-08-03.html"),
    ("config", "tdaq-01-08-04", "20111106134807",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-08-04.html"),
    ("config", "tdaq-01-09-00", "20111106134811",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-01-09-00.html"),
    ("config", "tdaq-02-00-00", "20111106134813",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-02-00-00.html"),
    ("config", "tdaq-03-00-00", "20111106134818",
     "http://pcatd12.cern.ch/cmt/releases/nightly/config/doc/RELEASE_NOTES.tdaq-03-00-00.html"),
    # doxygen ConfigPackages (DAL/C++ package overview)
    ("doxygen", "ConfigPackages-nightly", "20110326220841",
     "http://pcatd12.cern.ch/cmt/releases/doxygen/nightly/html/ConfigPackages.html"),
    ("doxygen", "ConfigPackages-tdaq-02-00-03", "20110327163333",
     "http://pcatd12.cern.ch/cmt/releases/doxygen/tdaq-02-00-03/html/ConfigPackages.html"),
    ("doxygen", "ConfigPackages-tdaq-03-00-01", "20110326094004",
     "http://pcatd12.cern.ch/cmt/releases/doxygen/tdaq-03-00-01/html/ConfigPackages.html"),
    ("doxygen", "ConfigPackages-tdaq-04-00-00", "20111027092808",
     "http://pcatd12.cern.ch/cmt/releases/doxygen/tdaq-04-00-00/html/ConfigPackages.html"),
    ("doxygen", "ConfigPackages-tdaq-04-00-01", "20120224154520",
     "http://pcatd12.cern.ch/cmt/releases/doxygen/tdaq-04-00-01/html/ConfigPackages.html"),
    # javadoc (config API)
    ("javadoc", "config-package-summary", "20110707223035",
     "http://pcatd12.cern.ch/cmt/releases/javadoc/nightly/config/package-summary.html"),
    ("javadoc", "config-Query", "20110322202710",
     "http://pcatd12.cern.ch/cmt/releases/javadoc/nightly/config/Query.html"),
    ("javadoc", "config-BadQueryException", "20110322185043",
     "http://pcatd12.cern.ch/cmt/releases/javadoc/nightly/config/BadQueryException.html"),
]

def fetch(page):
    pkg, name, ts, url = page
    wb = f"https://web.archive.org/web/{ts}id_/{url}"
    req = urllib.request.Request(wb, headers={"User-Agent": "Mozilla/5.0 research archive rescue"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

failed = []
for page in PAGES:
    pkg, name, ts, url = page
    fn = os.path.join(OUTDIR, f"{pkg}__{name}__{ts}.html")
    if os.path.exists(fn) and os.path.getsize(fn) > 500:
        print("skip", fn, os.path.getsize(fn))
        continue
    try:
        data = fetch(page)
        with io.open(fn, "wb") as f:
            f.write(data)
        print("ok", fn, len(data))
    except Exception as e:
        failed.append((fn, str(e)))
        print("FAIL", fn, e)
    time.sleep(1)

print("done; failures:", len(failed))
for fn, e in failed:
    print(" -", fn, e)