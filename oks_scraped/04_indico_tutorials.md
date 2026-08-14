# 04. Indico tutorials and talks on OKS configuration

Local PDFs are in `indico/`. Extracts in `indico/_*_extract.md`.

---

## 4.1 DAQ for Experts lecture — "config service" session (best shifter source)

- **Event**: indico.cern.ch/event/106368 (DAQ for Experts school/lecture series)
- **PDF**: `indico/indico_daq_for_experts.pdf` (3 966 147 B, 59 pages)
- **Extract**: `indico/_daq_for_experts_extract.md`

Key content (verified in extract):
- The **configuration database is called the "OKS" database** in everyday
  ATLAS jargon; the term comes from the OKS object kernel/manager product.
- Config is structured as **partitions / segments / applications**; each
  application object describes what to start, where (host/computer), with
  which environment/command line, and how to recover it.
- Runs are defined by a **partition**; `setup_daq <partition-file> <name>`
  starts a session bound to a config **version** (git hash) — see also §1.5.
- Pages include worked examples of "which version did this run use?" and
  "where is application X configured?" — good question/answer pairs for the
  training data.

## 4.2 OKS configuration service talk (IS, CHEP-era)

- **Event**: indico (CHEP 2007 conference) — `talk/332/...`
- **PDF**: `indico/indico_talk332.pdf` (1 195 401 B, 14 pages)
- **Extract**: `indico/_talk332_extract.md`
- Content: I. Soloviev et al., "ATLAS DAQ and configuration service"
  — introduces OKS, DAL, config service architecture; describes **archiving of
  used configurations at run start for every run**; retrieval by experts later.

## 4.3 Data editor / GUI training ("INFOST-2016")

- **Event**: indico.cern.ch/event/548007
- **PDF**: `indico/indico_id_training_2016.pdf` (22 603 975 B, 97 pages — mostly
  screenshots, scanned); text-layer extract `indico/_id_training_extract.md`
  (36 469 chars) contains the *step-by-step* layout of training on
  `oks_data_editor`.

## 4.4 Global Monitoring overview (explanation of run-dependent info)

- **Event**: indico.cern.ch/event/1380665 (or similar) — "Global monitoring"
- **PDF**: `indico/indico_gm_overview.pdf` (1 208 147 B, 42 pages)
- **Extract**: `indico/_gm_overview_extract.md`
- Content: explains run number, partitions, how COOL stores configuration per
  run offline; confirms the split "online → OKS (real-time config), offline →
  COOL (by run)". Not OKS-heavy, but gives vocabulary for shifter questions.

## 4.5 Poster — Bianchi, EPS 2011 (1 page)

- **PDF**: `indico/indico_bianchi_eps2011.pdf` (5 588 158 B, 1 page)
- **Extract**: `indico/_bianchi_eps2011_extract.md` (7 821 chars)
- **Content**: "The ATLAS configuration service" poster; states the 
  OKS/DAL/config layering and describes how run-relevant config data is
  archived; a good short description for citations.

---

## 4.6 Not available sessions

| Event | Content | Reason |
|-------|---------|--------|
| indico.cern.ch/event/1452600 | "DAQ for experts — Run 3" (modern) | page requires **access key** (private/restricted); headless-fetch returns "requires_authentication" |
| agenda.infn.it/event/.../TDAQ_BO_Ep_2.pdf | TDAQ bootcamp EP2 | **Anubis anti-bot** (v1.25.0) blocks; direct .pdf path returns HTML "not found" |
| indico.cern.ch/event/1566094 contribution 6690058 | "AI RCS Strategy Workshop: AI Assistant for ATLAS operations and beyond" (Sep 2025) | accessible page, but **no materials attached** (abstract only; mentions shifter-assistant use cases) — see `06_shifter_manuals.md` |

---

## 4.7 Source URLs

| Local file | Event URL |
|---|---|
| indico_daq_for_experts.pdf | https://indico.cern.ch/event/106368 |
| indico_talk332.pdf | https://indico.cern.ch/event/3580/contributions/332 (CHEP 2007) |
| indico_id_training_2016.pdf | https://indico.cern.ch/event/548007 |
| indico_gm_overview.pdf | https://indico.cern.ch/event/130675 |
| indico_bianchi_eps2011.pdf | indico.in2p3.fr (EPS 2011 poster)