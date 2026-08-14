# Access status of OKS/DAL source material

Compiled 2026-08-08 during scraping of DUNE-DAQ oks/dal + ATLAS TDAQ sources.

## Fully accessible and captured

| Material | Where captured | Notes |
|---|---|---|
| DUNE oks source (query.cpp, oks_dump, release info) | `01_dune_oks_code.md` | GitHub, public |
| DUNE dal + tutorial schema/data + tutorial.py | `02_dune_dal_code.md` + `repos/tutorial.schema.xml`, `repos/test.data.xml`, `repos/tutorial.py` | GitHub, public |
| Extra schemas (swrod, core, all_types, DAQ-Configuration, default-parameters, dal_testing) | `repos/*.schema.xml`, `repos/dal_testing.data.xml` | GitHub, public |
| CERN original oks gitlab + release notes + tags API | `05_cern_gitlab.md` | gitlab.cern.ch, public |
| OKS Data Editor online help (all windows incl. QueryWindow) | `repos/online-help/data-editor/*.html` | kept as captured copies |
| Papers: CHEP-2008 config-service & DAL ~ IOPS `119/022004`, QMUL L1Calo DB guide | `03_papers.md` + `pdfs/p1_*`, `pdfs/p11_*` | DOI/IOP public |
| Indico talks: DAQ-for-experts 1815, Bianchi EPS-2011 poster, ID training 2016, GM overview, talk 332 | `04_indico_tutorials.md` + `indico/*.pdf|.txt` | CERN indico public |
| Docs/README.md of oks (DUNE fork) | `01_dune_oks_code.md` | GitHub |

## Blocked / not retrievable

| Item | Reason | Workaround used |
|---|---|---|
| `https://epjs.web.cern.ch/EPJS/paper/403...` (EPJ paper 403) | 403/failed mirror | skipped, note in `03_papers.md`; content instead from DAL examples + guides |
| CDS/Anubis config service papers | records old, attachments blocked to bots | note in `03_papers.md` |
| ATLAS twiki (atlas-tdaq-info pages: ShifterDocs) | requires CERN SSO | excluded; DBE/online-help used instead (see `06_shifter_manuals.md`) |
| Some indico events (note files, slides for old CHEP talks) | ACL-restricted or missing PDF | only abstracts listed in `04_indico_tutorials.md` |
| `p1` CEPS/IOP `119, 022004` full text of *related* paper | pdf fetched | extracted to `pdfs/_p1_extract.md` |

## Not yet tried (worth a later pass)

- `https://atlasop.cern.ch/atlas-point1/tdaq/web_is/app/oks.html` (needs ATLAS P1 account).
- fresh-anubis `docs` for oks2coral & swrod provenance (add if ever needed for fine-tuning YAML).
- DUNE's `daq_config` (new name) repo — it is the successor of `oks`; not needed for OKS query fine-tuning.