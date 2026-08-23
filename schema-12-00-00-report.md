# Plain-language guide to `schema-12-00-00`

## Short answer

`schema-12-00-00` is not one XML schema file and it is not only a database of
real machines.  It is normally a **snapshot of the TDAQ configuration
repository** for release 12.  The snapshot is a set of XML files that, when
loaded together, describe a possible ATLAS online system configuration.

It has two distinct kinds of file:

1. **Schema files** (`*.schema.xml`) define the allowed object types and
   fields.  They are like a database table/class definition.  They do not
   themselves describe a particular host, application, or run.
2. **Data files** (`*.data.xml`) create objects using those definitions.  A
   data file can describe a host, a software binary, an application, a segment,
   or a partition, and can link those objects together.

The repository is modular.  A top-level configuration file includes other
files, which include still more schema and data files.  The result is one
connected configuration graph.

## Important limitation of this report

The actual `schema-12-00-00` directory is not mounted in this repository.
Therefore this document explains the documented TDAQ 12 layout and gives
commands to inspect an installed copy.  It does **not** claim an exact file
list, object count, or that every example object ID exists in your copy.

The known TDAQ 12 release change in the local release notes is to OKS XML
editing: `update_data()` preserves the existing XML layout and user comments,
whereas `save_data()` rewrites the file in the standard layout.  This is a
file-editing behavior change, not a claim that all configuration data changed.

## Expected layout

The data root is usually similar to:

```text
schema-12-00-00/
└── daq/
    ├── schema/
    ├── hw/
    ├── sw/
    ├── segments/
    └── partitions/        # commonly present, even when not mentioned first
```

Some installations place the same tree under
`$TDAQ_INST_PATH/share/data/daq`; some use a checked-out OKS repository.  The
important part is the relative repository path beginning with `daq/`.

### `daq/schema/`: the vocabulary and rules

Files in this directory usually end in `.schema.xml`.  They declare:

- **classes** — object types, for example `Computer`, `BaseApplication`,
  `Binary`, `Segment`, or detector-specific types;
- **superclasses** — inheritance, so a child class has its parent class's
  attributes and relationships;
- **attributes** — values such as `Name`, `InitTimeout`, an enum, a boolean,
  or a number;
- **relationships** — named links to another object, such as an application
  pointing to the program it runs or to applications it depends on;
- **cardinality** — whether a relationship can have zero, one, or many target
  objects;
- **includes** — other schema files needed by this schema.

For example, a SW ROD schema declares that it includes the core and Data Flow
schemas before declaring its own classes.  That means its classes may use the
types defined in those files.

```xml
<include>
  <file path="daq/schema/core.schema.xml"/>
  <file path="daq/schema/df.schema.xml"/>
</include>

<class name="SwRodApplication">
  <superclass name="ROS"/>
  <attribute name="CPU" type="string"/>
</class>
```

This is a **definition**, not an instance of a running application.  It says a
`SwRodApplication` is a permitted kind of object, inherits from `ROS`, and may
have a `CPU` value.

### `daq/hw/`: hardware inventory and topology

Files here are normally `.data.xml` files holding hardware objects.  Depending
on the configuration, they can describe computers/hosts, racks, crates,
modules, interfaces, network or detector equipment, and the links between
them.

These are configuration records.  A host object may represent a real host name
and a rack object may represent a real physical rack, but the file is not a
live monitoring feed: it does not tell you current CPU load, whether the host
is switched on, or whether a cable is currently healthy.

### `daq/sw/`: software catalogue and reusable settings

Files here normally describe software configuration rather than program source
code.  Typical objects include software repositories, packages, binary or jar
programs, platform tags, environment parameters, and reusable resource or
template definitions.

The data may contain real deployment names and paths, but it is still intended
configuration: it identifies **what is meant to be installed or run**, not a
proof that the executable is currently running on a host.

The documented TDAQ workflow imports `daq/schema`, selected `daq/sw/*.data.xml`
files, and `daq/segments/common-environment.data.xml` from a release into an
OKS repository.  That is a useful indication that these are shareable baseline
configuration files, not an event-data store.

### `daq/segments/`: online-system assembly

A segment groups applications and resources into a logical part of the online
system.  Segment files commonly define application objects, their programs,
their host assignment, startup and shutdown dependencies, and shared
environment settings.

For example, `setup.data.xml`, `setup-initial.data.xml`, and
`common-environment.data.xml` are conventional names seen in TDAQ material.
They are configuration entry points or shared building blocks.  They are not
the data taken during a physics run.

### `daq/partitions/`: a runnable selection of the system

When present, a partition file normally selects the online infrastructure,
segments, resources, and run-control information used for one named
configuration.  It is often the most useful entry point when the question is
"what would this partition run?"

It should not be confused with a run database.  A partition is a configuration
definition; a run database records what happened during a particular run.

## What one data file looks like

An OKS data file normally has an `<oks-data>` root, optional `<include>`
entries, and `<obj>` entries:

```xml
<oks-data>
  <include>
    <file path="daq/schema/core.schema.xml"/>
    <file path="daq/hw/hosts.data.xml"/>
  </include>

  <obj class="Binary" id="my-program">
    <attr name="BinaryName" type="string" val="my-program"/>
    <rel name="BelongsTo" class="SW_Repository" id="Online"/>
  </obj>
</oks-data>
```

Read this as: “create an object with type `Binary` and ID `my-program`; give
it a `BinaryName`; link it through `BelongsTo` to the `Online` repository.”

The class and fields must be legal according to the schema loaded through the
include graph.  A data file may include other data files, so an object can
reference a host or repository that is declared somewhere else.

## Are these real data?

It depends on what “real” means.

| Question | Answer |
| --- | --- |
| Are schema files real database content? | They are real type definitions, but they are not instances of equipment or applications. |
| Can data files contain real ATLAS host names, software paths, application IDs, and hardware topology? | Yes. Production configuration repositories commonly contain those identifiers. |
| Does every object necessarily correspond to hardware or software live right now? | No. A release can contain defaults, templates, examples, test objects, disabled components, and configuration intended for future use. |
| Is this detector/event/monitoring data? | No. It is configuration metadata, not event payloads or live status. |
| Does it reveal current runtime state? | Normally no. Runtime state comes from run-control, monitoring, IS, logs, or a run database. |

Treat the release as a source of **intended configuration**, not an operational
truth source.  To determine what was used in a particular run, use the run's
recorded configuration version and partition, then load that exact repository
revision.

## Includes: why there are so many files

The files are split to avoid copying shared definitions and objects.

```text
partition file
  ├── segment file
  │   ├── common environment
  │   ├── application/program definitions from sw
  │   └── host definitions from hw
  └── schema files
      ├── core schema
      └── specialized schemas
```

This means opening a single `.data.xml` file does not show the whole
configuration.  Follow its `<include>` elements recursively.  In documented
examples, a SW ROD data file includes core schema plus shared environment,
setup, hosts, and additional segment files before defining its own objects.

## How queries relate to these files

An OKS query filters objects after the relevant schema and data include graph
has been loaded.

```bash
oks_dump --class BaseApplication \
  --query '(all ("InitTimeout" "30" <=))' \
  daq/segments/setup.data.xml
```

The class is supplied by `--class`.  The query itself says how to filter that
class:

- `all` searches the target class and its subclasses;
- `this` searches only the target class;
- `("InitTimeout" "30" <=)` is an attribute comparison;
- `("Relationship" some (object-id "an-id" =))` follows a relationship;
- `and`, `or`, and `not` combine expressions.

The query is valid only when `BaseApplication`, `InitTimeout`, and the relevant
data file exist in the release being queried.  Likewise, an object ID is valid
only when the selected data graph actually contains that ID.

## Inspect an installed release yourself

Set the path to the release copy you want to understand:

```bash
export RELEASE_ROOT=/path/to/schema-12-00-00
export DAQ_ROOT="$RELEASE_ROOT/daq"

find "$DAQ_ROOT" -maxdepth 2 -type f \( -name '*.schema.xml' -o -name '*.data.xml' \) | sort
```

Count definitions and data files by area:

```bash
for area in schema hw sw segments partitions; do
  printf '%-12s ' "$area"
  find "$DAQ_ROOT/$area" -type f \( -name '*.schema.xml' -o -name '*.data.xml' \) 2>/dev/null | wc -l
done
```

List classes declared in schema files:

```bash
rg -n '<class name="' "$DAQ_ROOT/schema"
```

List actual objects declared in data files:

```bash
rg -n '<obj class="' "$DAQ_ROOT/hw" "$DAQ_ROOT/sw" "$DAQ_ROOT/segments" "$DAQ_ROOT/partitions"
```

List every include, which is the first step in reconstructing the graph:

```bash
rg -n '<file path="' "$DAQ_ROOT"
```

Find potentially production-looking records, while remembering that names alone
do not prove they are active:

```bash
rg -n '<obj class=|<attr name="(Name|BinaryName|InstallationPath)"|<rel name=' \
  "$DAQ_ROOT/hw" "$DAQ_ROOT/sw" "$DAQ_ROOT/segments" "$DAQ_ROOT/partitions"
```

## Where to find the information you need

| Need | Best source |
| --- | --- |
| What attributes/relationships are allowed? | The matching `.schema.xml` file, including its parent classes. |
| Which configured objects exist? | The loaded `.data.xml` files and all their recursive includes. |
| What host/program would an application use? | Segment/partition data plus the linked `hw` and `sw` objects. |
| Which configuration was used for a specific run? | The run database/configuration version, then that exact repository revision. |
| Current state, health, or event data | Monitoring, IS, logs, or the run-control/runtime systems—not these XML files. |

## Release-12-specific facts confirmed by local reference material

- TDAQ 12 added `update_data()`, which preserves XML layout and user comments;
  the older save operation rewrites the XML file.
- In the TDAQ 12 SW ROD configuration, `MemoryPool` became active: a
  `SwRodApplication` provides a default pool and a `SwRodRob` can override it.
  Its documented attributes are `PageSize` and `NumberOfPages`.
- The legacy `SwRodNetioInput` and `SwRodNetioNextInput` classes were removed
  from the SW ROD schema in that release.

Those facts apply to the documented release material.  Use the inspection
commands above before making a query or migration decision against a particular
installed `schema-12-00-00` snapshot.
