# 03. Papers — OKS / configuration service literature

Local PDF/text copies live in `pdfs/`. Extracts (context views) are in
`pdfs/_p1_extract.md` and `pdfs/_p11_extract.md`.

---

## 3.1 main paper — the configuration service challenge

- **Title**: The ATLAS DAQ system online configurations database service challenge
- **Authors**: J. Almeida et al. (incl. I. Soloviev, ok.robert@cern.ch)
- **Source**: J. Phys. Conf. Ser. 119 022004 (2008), CHEP 2007.
- **URL**: https://iopscience.iop.org/article/10.1088/1742-6596/119/2/022004
- **Local copy**: `pdfs/p1_iopscience_119_022004.pdf` (957 655 B, 12 pages, 43 810 chars of text)

**What it explains (useful for the training corpus):**

1. The configuration service is a part of ATLAS DAQ/HLT + Detector Controls; it
   stores: which parts of ATLAS participate in a run, when/where processes are
   started, run-time environments, status checks & recovery, shutdown order,
   parameters for data-flow/trigger/detector modules (lines 66–70 of extract).
2. Access by thousands of processes concurrently at → run start; notify +
   reconfigure on mid-run changes; archives used configurations to be browsed
   by experts and accessed during event processing (lines 85–129).
3. OKS is an **object manager** — "the basic entity is an object with unique
   object identifier", classes/attributes/relationships, composite objects,
   integrity constraints; classes/objects created & modified dynamically;
   native API is **C++**; there is a **query language**; change notifications
   (lines 656–685).
4. Storage: human-readable **XML files** (schema files + data files, file
   includes); relational back-ends via CORAL (Oracle, MySQL, SQLite) oriented
   for **incremental archiving**; RDB CORBA servers for remote access
   (lines 689–753). Query results caching on RDB server.
5. Editors: UML-like **Schema Editor** and **Data Editor** with "graphical
   query constructor → query saved as file, reusable via editor or OKS API"
   (lines 766–776).
6. Archiving: at start of each run the used configuration is archived;
   archive browsable by time, release, user, host, partition (lines 823–829;
   and the `rn_ls` example in the release notes shows Version + Config Name).

**Verbatim DAL example (from the paper, also §2.2 in `02_dune_dal_code.md`)**

```
Configuration db("oksconfig:daq/partitions/test.xml");
const Partition * format = dal::core::get_partition(db, "test");
const Computer * h = p->get_DefaultHost();
std::cout << "Default host: " << h->UID() << std::endl;
const Computer * h2 = db.get<Computer>("pc-tdaq-onl-02");
p->set_DefaultHost(h2);
db.commit();
```

---

## 3.2 The L1Calo database user guide

- **Title**: DatabaseUserGuide — L1Calo (Trigger Calorimeter) configuration with OKS
- **Source**: Queen Mary, University of London (pprc):
  `https://pprc.qmul.ac.uk/l1calo/doc/out/DatabaseUserGuide.pdf`
- **Local copy**: `pdfs/p11_qmul_databaseuserguide.pdf` (159 523 B, 22 pages, 44 155 chars)
- **Extract**: `pdfs/_p11_extract.md`

**Content highlights:**
- The L1Calo DB is organized as CMT packages `dbFiles` (schema+data) — schema
  defines classes used by all L1Calo readout modules; data files hold concrete
  values such as thresholds, formats, dead-time, cable maps...
- OKS = generic storage layer; DAL = typed access layer generated from schema;
  the DB is stored as `.schema.xml`/`.data.xml` under a `TDAQ_DB_PATH` area.
- The document explains how DAL **subclasses** existing classes (e.g.
  `CaloPprModule` → `L1Calo...`) to add detector-specific attributes without
  touching the core schema — same pattern used in the deA standard schema.

---

## 3.3 Other papers attempted (availability status)

| Ref | Source | Title (if known) | Status |
|-----|--------|------------------|--------|
| p2 | EPJ Web Conf. (2025) — epj-conferences.org | bot-protected | **403** (Anubis bot wall) |
| p3 | EPJ Web Conf. (2021) — epj-conferences.org | bot-protected | **403** (Anubis) |
| p4 | IDIAP (idiap.ch) | link not existing | **404 Not Found** |
| p5 | Middle East Technical Univ. (open.metu.edu.tr) | OKS-related thesis | **timeout** — connection unreachable (WinError 10060) |
| p6–p10 | CERN CDS records 446327, 1457575, 2919574, 2649073, 2923938 | various OKS/talk slides | **blocked by Anubis anti-bot page** (record page also truncates at ~7.6 KB and would require the JS challenge) |

**Note on the CDS records**: the actual record numbers (446327 —
"OKS - the object kernel for DAQ applications", I. Soloviev, CERN-OPEN-2014, etc.)
are legitimate but the server requires a JS challenge; PDFs can be fetched
with a real browser afterwards (see `access_status.md`).