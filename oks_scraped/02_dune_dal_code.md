# 02. The DAL package — DUNE-DAQ fork (`DUNE-DAQ/dal`)

Source repository (public, default branch `develop`):
- https://github.com/DUNE-DAQ/dal
- Clone: `git clone https://github.com/DUNE-DAQ/dal`
- The DAL ("Data Access Library") is the typed C++/Python layer over OKS:
  classes in the OKS schema are mapped to C++ classes; objects are read and
  modified through `ConfigObject`/`Config` interfaces. The original ATLAS
  implementation and its docs live in the same repos (see `05_cern_gitlab.md`).

Files kept locally in this corpus: `repos/core.schema.xml`,
`repos/tutorial.schema.xml`, `repos/dal_testing.data.xml`, `repos/tutorial.py`.

---

## 2.1 Repository layout (relevant files)

| Path                          | Content |
|-------------------------------|---------|
| `docs/README.md`              | "An Introduction to OKS" — the canonical user-level documentation |
| `docs/TWiki.txt`              | 924-line copy of the old ATLAS TWiki OKS pages (DaqHltOks) |
| `docs/RELEASE_NOTES.md`       | DAL release notes (migrated from ATLAS tdaq) |
| `include/dal/ConfigVersion.hpp` | `ISInfo` w/ `Version` field — publish used config version to IS |
| `apps/dal_get_config_version.cxx` | CLI: publish config version into IS (`-p partition`) |
| `apps/dal_set_config_version.cxx` | CLI: set config version in IS (`-v`, `-p`, `-r`) |
| `apps/dal_dump_apps.cxx` (+ friend dump tools) | Dump running applications from config |
| `schema/dal/core.schema.xml`  | 83 540 B, 660 lines — the classic TDAQ core schema (Partition, Application, Computer, Segments, ...) |
| `schema/dal/tutorial.schema.xml` | Minimal 3-class schema used by the tutorial |
| `scripts/dal_testing.data.xml` | Data file matching tutorial schema |
| `scripts/dal_testing.py` / `tutorial.py` | Python tutorial |
| `CMakeLists.txt`              | Build (C++17, pybind11, cmake) |

---

## 2.2 The three-tier example (from DAL docs/tutorial)

Tutorial schema (`repos/tutorial.schema.xml`, 3 classes):

```xml
<class name="Application" description="A software executable" is-abstract="yes">
  <attribute name="Name" type="string" init-value="Unknown" is-not-null="yes"/>
</class>

<class name="ReadoutApplication" description="An executable which reads out subdetectors">
  <superclass name="Application"/>
  <attribute name="SubDetector" type="enum" range="PMT,WireChamber" init-value="WireChamber"/>
</class>

<class name="RCApplication" description="An executable which allows users to control datataking">
  <superclass name="Application"/>
  <attribute name="Timeout" type="u16" range="1..3600" init-value="20" is-not-null="yes"/>
  <relationship name="ApplicationsControlled" description="Applications RC is in charge of"
                class-type="Application" low-cc="one" high-cc="many"/>
</class>
```

Matching data (`repos/dal_testing.data.xml`, excerpt):

```xml
<oks-data>
  <include><file path="tutorial.schema.xml"/></include>
  <obj class="RCApplication" id="rc_negative">
    <attr name="Name" type="string" val="NegativeRC"/>
  </obj>
  ...
  <obj class="ReadoutApplication" id="0x1" >
    <attr name="Name" type="string" val="Collab"/>
    <attr name="SubDetector" type="enum" val="PMT"/>
  </obj>
</oks-data>
```

Python usage (`scripts/tutorial.py`, verbatim, 1 274 B — see repos/tutorial.py):

```python
import dal.tutorial as tut   # DAL classes generated from tutorial.schema.xml
import dal.core as core

# open the configuration database
f = tut.Config("file:filename=dal_testing.data.xml")
obj = f.get('ReadoutApplication')
print(f"ReadoutApplication: {obj}")     # prints id, attributes, relationships
...
f.set('Timeout', 20)                    # modify an attribute
f.commit()                              # save all changes back to XML files
```

---

## 2.3 The `ConfigVersion` pattern (shifter-relevant)

`include/dal/ConfigVersion.hpp`:

```cpp
class ConfigVersion : public ISInfo {
  // in the OKS schema: class ConfigVersion, attribute "Version" (string)
  // published to the Information Service under /<partition>/ConfigInfos/...
  // Version encodes the OKS git SHA-1 of the used configuration, e.g.
  //   hash:6800fe3b63a18859ef688612b44e051e4f36e345
};
```

CLI apps:
- `dal_get_config_version.cxx` — prints the currently published config version
  for a partition (`-p <partition>`), i.e. "which configuration am I running?".
- `dal_set_config_version.cxx` — sets it (`-v <version+sha1> -p <partition> -r`).

---

## 2.4 Core schema classes (excerpts from `core.schema.xml`, repo copy)

The full ATLAS(TDAQ) class hierarchy (~ hundreds of classes) starts with:
`Partition` (top), `Segment`/`OnlineSegment`, `Application` /
`InfrastructureApplication` / `CustomLifetimeApplication`,
`ComputerBase` > `Computer`/`ComputerSet` (Platform, HW_Object),
`Resource`, `Parameter`, `SW_Object`, `HW_Object`, `Detector`, ...

Key code snippet from the DUNE docs (also present in the CHEP 2008 paper,
see `03_papers.md`):

```cpp
#include <dal/Partition.h>
dal::Partition * p = db.getPartition("test");
std::string default_host = p->getDefaultHost();
```

---

## 2.5 Documentation pointers

- `docs/README.md` gives an "Introduction to OKS" (concepts: schema/classes,
  objects, attributes, relationships; multi-value, composite, exclusive;
  data + schema files; init values; ranges; archiving).
- DUNE readthedocs (public): 
  - https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/RELEASE_NOTES.html
  - https://dune-daq-sw.readthedocs.io/en/v4.1.0/packages/dal/RELEASE_NOTES/ — confirmed accessible and mirroring
    the ATLAS release notes (tdaq-09-01-00, tdaq-08-03-00 ...).
- DBE (DataBase Editor) user pages (public readthedocs branch):
  https://dune-daq-sw.readthedocs.io/en/johnfreeman-update_documentation_instructions/packages/dbe/

All license headers: © CERN, ATLAS collaboration; BSD-3-Clause.