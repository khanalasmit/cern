# Using an installed TDAQ configuration release

This project must build its schema context from the TDAQ configuration release
that will be queried.  Do **not** assume that a class, attribute,
relationship, enum value, or object ID found in the evaluation dataset exists
in another release.  In particular, the examples in
`eval_dataset/oks_eval_queries.jsonl` are query-language examples, not a
schema contract for `schema-12-00-00`.

The layout is normally release-independent: a selected release contains a
`daq` directory with `hw`, `schema`, `segments`, and `sw` below it.  The
release number is an input, not a value hard-coded into the application.

## Select and inspect a release

Set `TDAQ_RELEASE_ROOT` to either the directory that contains `daq`, or to a
directory that contains one or more `schema-<release>` directories.  This
works for `schema-12-00-00` and for other installed releases.

```bash
export TDAQ_RELEASE_ROOT=/path/to/schema-12-00-00

if [ -d "$TDAQ_RELEASE_ROOT/daq" ]; then
  export DAQ_ROOT="$TDAQ_RELEASE_ROOT/daq"
else
  release_dir=$(find "$TDAQ_RELEASE_ROOT" -maxdepth 1 -type d -name 'schema-*' -print -quit)
  test -n "$release_dir" || { echo 'No schema-* release directory found'; exit 1; }
  export DAQ_ROOT="$release_dir/daq"
fi

for area in hw schema segments sw; do
  test -d "$DAQ_ROOT/$area" || { echo "Missing $DAQ_ROOT/$area"; exit 1; }
done
printf 'Using release data under: %s\n' "$DAQ_ROOT"
find "$DAQ_ROOT" -type f \( -name '*.schema.xml' -o -name '*.data.xml' \) | sort | sed -n '1,40p'
```

Before writing a query, inspect the selected release rather than borrowing a
name from a different release.  The following command prints every class,
including inherited attributes and relationships, from the selected release.
It is deliberately release-agnostic.

```bash
python3 - "$DAQ_ROOT" <<'PY'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

daq = Path(sys.argv[1])
classes = {}
for path in daq.rglob('*.schema.xml'):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        print(f"Skipping malformed schema {path}: {exc}", file=sys.stderr)
        continue
    for node in root.findall('.//class'):
        name = node.get('name')
        if not name:
            continue
        entry = classes.setdefault(name, {'parents': [], 'attrs': {}, 'rels': {}})
        entry['parents'].extend(x.get('name') for x in node.findall('superclass') if x.get('name'))
        entry['attrs'].update({x.get('name'): x.get('type') for x in node.findall('attribute') if x.get('name')})
        entry['rels'].update({x.get('name'): x.get('class-type') for x in node.findall('relationship') if x.get('name')})

def members(name, seen=frozenset()):
    if name in seen or name not in classes:
        return {}, {}
    attrs, rels = {}, {}
    for parent in classes[name]['parents']:
        parent_attrs, parent_rels = members(parent, seen | {name})
        attrs.update(parent_attrs)
        rels.update(parent_rels)
    attrs.update(classes[name]['attrs'])
    rels.update(classes[name]['rels'])
    return attrs, rels

for name in sorted(classes):
    attrs, rels = members(name)
    print(f"{name}\n  attributes: " + ', '.join(f"{key}:{attrs[key]}" for key in sorted(attrs)))
    print("  relationships: " + ', '.join(f"{key}->{rels[key]}" for key in sorted(rels)))
PY
```

Use `rg -n 'name="<Class>"|name="<Attribute-or-relationship>"' "$DAQ_ROOT/schema"`
to locate the declaring schema file and inspect its declared type, enum range,
and relationship target.  Search `hw`, `segments`, and `sw` data files for an
actual object ID before using an `object-id` query.

## Form valid queries

An OKS query is used together with a target class.  `all` means that target
class and its subclasses; `this` means only the target class.  Values are
quoted, including numbers and boolean values.  `~=` is the regular-expression
operator: it is written as `~=` — not `\~=`.

```text
(all ("Attribute" "value" =))
(all ("NumericAttribute" "30" <=))
(all (and ("AttributeA" "value" =) ("AttributeB" "5" >)))
(all ("Relationship" some (object-id "known-id" =)))
(all (not ("Relationship" some (object-id "known-id" =))))
```

Only instantiate a pattern when the inspection output confirms the named
members in the chosen release.  For example, if the selected release reports
`BaseApplication` with `InitTimeout`, `IfExitsUnexpectedly`, and
`InitializationDependsFrom`, these are valid queries for that class:

| Natural-language request | Target class | Query |
| --- | --- | --- |
| Applications that initialise in 30 seconds or less | `BaseApplication` | `(all ("InitTimeout" "30" <=))` |
| Applications that restart or ignore an unexpected exit | `BaseApplication` | `(all (or ("IfExitsUnexpectedly" "Restart" =) ("IfExitsUnexpectedly" "Ignore" =)))` |
| Applications that depend on the verified object ID `ipc-server` | `BaseApplication` | `(all ("InitializationDependsFrom" some (object-id "ipc-server" =)))` |
| Applications with no dependency on that object ID | `BaseApplication` | `(all (not ("InitializationDependsFrom" some (object-id "ipc-server" =))))` |

Similarly, use the following only if `IPCServiceApplication.InterfaceName` is
present in the inspected release:

```text
Question: Which IPC service applications expose the is/repository interface?
Class:    IPCServiceApplication
Query:    (all ("InterfaceName" "is/repository" =))
```

Do not substitute a nearby class merely because it has a similarly named
field.  For example, a `BinaryName` attribute declared on `BinaryFile` must be
queried with `BinaryFile` (or an appropriate subclass) as the target class;
it is not automatically an attribute of `Binary`.

## Validate against the same release

Run the query with the matching class and data files from the selected release.
Start with the relevant file(s), then widen the input set only if the release's
include graph requires it.

```bash
oks_dump --class BaseApplication \
  --query '(all ("InitTimeout" "30" <=))' \
  "$DAQ_ROOT/segments/setup.data.xml"
```

For a release-specific object ID, discover it from the data first:

```bash
rg -n 'id="[^"]+"' "$DAQ_ROOT/hw" "$DAQ_ROOT/segments" "$DAQ_ROOT/sw" | sed -n '1,60p'
```

If `oks_dump` reports an unknown class, attribute, relationship, or data-file
include, treat that as a release-context error: return to the schema/data
inspection step and form a query from what this release actually contains.
