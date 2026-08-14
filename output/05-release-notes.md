# Source 5: ATLAS TDAQ release notes for the OKS and Config packages (archived via Wayback Machine)

> Rendered by `output/build_05.py`; all blocks are text-extracted from archived HTML pages (snapshot timestamps in each heading). The original site `pcatd12.cern.ch` is dead; the raw snapshot files are preserved in `output/extracts/pcatd12/`.

> Generated 2026-08-08 by automated extraction renderer (`output/build_05.py`).
> The original site `pcatd12.cern.ch` no longer responds: direct fetch fails with a transport error, and a real-browser attempt returns HTTP 500 ("proxy 590 UPSTREAM502: 0 bytes"). All pages below were therefore recovered from the Internet Archive Wayback Machine via the CDX API (`https://web.archive.org/cdx/search/cdx?url=pcatd12.cern.ch&matchType=domain&...`) and fetched as snapshots with the `id_` flag (raw archived content, no Wayback overlay).
>
> These are the original per-package release-notes pages of the CMT-era ATLAS TDAQ build (`nightly/oks/doc/`, `nightly/config/doc/`), preserved in the 2011-2012 nightly snapshots. They predate - and are complementary to - the modern `doc/RELEASE_NOTES.md` of the current `oks` GIT repository (already embedded in `03-cern-gitlab.md`, which covers the `oks-02-07-02` .. `oks-08-04-00` era). Together they form a continuous OKS 1.x/2.x timeline.

## 1. `oks` package release notes (13 pages, archived 2011-11-07)

### Snapshot `oks__tdaq-01-01-00__20111107082403.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-01-00__20111107082403.html`*

```text
RELEASE_NOTES

Database Consistency

 No more identical objects allowed. In the past a warning message was
 printed out and an anonymous object was created, when identical object was
 read. Now the error message is printed out, the reading of the database file
 containing duplicated object is stopped and the bad status of the file is
 returned. The error message contains the object identity and both
 names of the files containing such objects.

 Non-existent attributes and relationships of objects are reported as
 warnings. Before the data stored in extended format were converted without
 any message in case of schema evolution.

 To avoid possible confusion of users with variables converters provided by
 the dal package, the syntax of environment variables description used by
 oks in filenames is changed. Now the valid syntax is $(FOO). In previous releases it
 was ${FOO}. Note, it is not recommended to use environment variables in
 includes, since it makes database dependent on user's setup. The recommended
 way is to define includes either relative to a database repository, or to the
 parent file.

Queries Creation and Destruction

 To allow proper destruction of a query make all internal query-related
 objects allocated on heap. In the past  a query constructed from string
 was not properly released and memory leak took place. Now all sub-query
 objects are created on heap and are properly released, when the query object is
 destroyed. All code using queries (the oks kernel code, tutorial, examples)
 has been changed.

OKS Dump Application

 Add several command line options:

 |  --files-only 
 | prints out list names of database files

 |  --class 
 | dump given class (all objects of class or matching some query)

 |  --query 
 | print objects matching query (can only be used with class)

Bugs Fixes

 Avoid possible segmentation fault, when read an object without loaded
 class.

 When load a schema, do not set automatically default value for enumeration
 attribute, if it was empty. It caused such default value explicitly set,
 when the schema is saved from the editor and such behaviour was not expected
 by users.
```

### Snapshot `oks__tdaq-01-02-00__20111107082427.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-02-00__20111107082427.html`*

```text
New Page 1

OKS Relational Backend

An exercise to use a relational database to store oks schema and data
information instead of xml files has been done. New roks library appears.
It contains code to store oks classes and oks objects to a relational database
and to retrieve them back. It is based on the LCG POOL RAL package (see http://lcgapp.cern.ch/project/persist/
for more information). Four new example applications oks_put_schema,
oks_put_data, oks_get_schema and oks_get_data demonstrate
it's usage. The file oks/src/rlib/create_db.sql contains definition of
the relational tables to store oks information. The exercise has been tested
with Oracle on devdb.cern.ch server supported by the CERN IT.

The following sequence of steps to create relational tables, put/get schema
and put/get data should to work:

 sqlplus $user/$passwd@$server $TDAQ_INST_PATH/../oks/src/rlib/create_db.sql
oks_put_schema -c "oracle://$server" -u $user -p $passwd -f oks-file.xml -t "v1" "first" -s 1
oks_get_schema -c "oracle://$server" -u $user -p $passwd -s "/tmp/v1.schema.xml" -e
oks_put_data -c "oracle://$server" -u $user -p $passwd -f oks-file.xml -v -l -a -t "v1.1" "first"
oks_get_data -c "oracle://$server" -u $user -p $passwd -t "v1.1" -f /tmp/v1.1.data.xml

For more information contact the oks package developer.

Path Query

Add support for path queries. Such query returns path between two objects by
navigating via relationships in accordance with user-defined query pattern. The
result of such query is a list of oks objects forming the path. The use case is
to get a path in several trees of references between objects using the same
leave objects. Note, for composite objects and exclusive relationships, the
usage of reverse composite relationships is more effective. In such case there
is the only tree built on top of given leaves.

API
Add oks::QueryPath class to describe special type of query calculating
path between two given objects. The constructor uses query as a text. Syntax of
query path is shown below:

 query-path ::= '(path-to "destination-object" query-path-expression)'
query-path-expression ::= '(query-path-type "rel-name" [, "rel-name"*] [query-path-expression])'
query-path-type ::= 'direct | nested'

If the string cannot be parsed, the exception oks::bad_query_syntax is
thrown.

When an oks query path object is created, it can be used to search a path
from given source object using the following method:

 OksObject::List * OksObject::find_path(const oks::QueryPath& query) const;

If a path is found, non-empty list is returned.

Example of query string
The example of query is shown below:

 (path-to "my-id@my-class" (direct "A" "B" (nested "N" (direct "X" "Y" "Z"))))

The destination object is "my-id@my-class". The search can be
started from any object of any class. In our example the start object has to
have two relationships named "A" and "B". An object
referenced via "A" and "B" should have relationship
"N". In our example it is possible to lookup for path via nested
objects linked via relationship "N". Finally all objects referenced
via "N" should have relationships "X", "Y" and
"Z". If the destination object is referenced by them, the path is
found.

Generic Query Extensions

The oks query expression was extended to use object ID as part of query
expression. The
used syntax is '(object-id "an-object-id")'. The
use case is to identify an object used in a relationship expression, e.g. get
all objects of some class referencing this object. Note, this is more effective
than search by non-indexed attribute value and this is the only way to define an
object without non-key attributes.

The object ID expression is integrated to the oks data editor query
constructor (choose "Object ID" radio button in an attribute
expression form).

Example of query string
The example of query to search all objects of some class referencing via
relationship "my-relationship" an object with id equal to
"test". 

 (all ("my-relationship" some (object-id "test" =)))

 For example, find all applications including subclasses, which runs on
host with id lxplus001.cern.ch:

(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))

Dangling References

Add 'bool OksKernel::get_bind_objects_status() const' method, that
returns status of last OksKernel::bind_objects() method call. It can be
used to check lack of dangling references after loading of database files.

Oks improves reporting of the dangling references. In addition to the
dangling reference itself the oks reports an object where unresolved reference
was found:

 WARNING [OksObject::bind()]:
Cannot find object "lxplus053.cern.ch@Computer"
WARNING [OksObject::bind_objects()]:
There are unresolved references from object "lxplus-3x3-23 ctrl@RunControlApplication"

OKS Dump

The oks_dump binary returns non-null status, if the loaded files have
non-resolved references between objects.

It also supports path queries: use '--path "object"
"path-query"' command line parameters, e.g. to find path between
an application and partition objects:

bash$ oks_dump --path "onlsw_test_3x3_lxlpus@Partition" '(path-to "lxplus-3x3-21-ctrl@RunControlApplication" (direct "Segments" "OnlineInfrastructure" (nested "Segments" (direct "Applications" "IsControlledBy" "Resources"))))' daq/partitions/lxplus_tests.data.xml

Found 3 objects in the path "(path-to "lxplus-3x3-21-ctrl@RunControlApplication" (direct "Segments" "OnlineInfrastructure" (nested "Segments" (direct "Applications" "IsControlledBy" "Resources"))))" from object "onlsw_test_3x3_lxlpus@Partition":

Object "onlsw_test_3x3_lxlpus@Partition"
...

Object "lxplus-3x3-2@Segment"
...

Object "lxplus-3x3-21@Segment"
...
```

### Snapshot `oks__tdaq-01-04-00__20111107082448.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-04-00__20111107082448.html`*

```text
d>

New Page 1

There are several changes in the relational OKS backend:

 use bulk insert for values of oks attributes and relationships

 replace OksDataInt, OksDataNum, OksDataString and OksDataDate tables by
 single OksDataVal table with appropriate columns to store integer, number,
 string and date values

 environment variable OKS_RAL_ORDER_QUERY_RESULTS can be used as switch
 on/off "order by" statement of queries reading values of
 attributes and relationships for performance studies

 to improve performance do not read description of class methods and their
 implementations, when get oks data only

Change interpretation of s8 and u8 oks data types from symbol 
type to 8 bits integer type:

 u8 and s8 oks data types are interpreted as integers by any output 
 method; before printing out non-alphanumeric symbols as char resulted wrong 
 output

 oks_data_editor allows to edit u8 and s8 types as octal, decimal and 
 hexadecimal numbers

 oks_schema_editor allows to set format for s8 and u8 types

The OksData stream output operator uses 'format' field to prints out 
s8, u8, s16, u16, s32 and u32 types. It is used by the oks_dump program.

Fix bug appeared with few window managers, when under certain conditions oks 
gui applications do not react on mouse button clicks.
```

### Snapshot `oks__tdaq-01-06-00__20111107082509.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-06-00__20111107082509.html`*

```text
New Page 1

There are no any changes in OKS, that require a user to 
modify or to convert a consistent database file. However the OKS becomes more 
strict for saving and loading of inconsistent schema and data files (no required 
includes, dangling object references, wrong or missing attribute and 
relationship values). A user can be asked to modify data as it is required by 
schema before it will be possible to save them using OKS tools. The other 
changes in OKS are connected with extension of features using relational backend 
(new relational tables and utilities).

OKS library

Files Consistency

 to improve diagnostic report included files, where 'no files 
 inclusion path between referenced objects' problem takes place

 allow duplicated objects for archiving purposes (use 
 OKS_KERNEL_ALLOW_DUPLICATED_OBJECTS variable)

 report object id and attribute name when read data with wrong range

 check inclusion of required schema files before saving

 allow empty objects (i.e. without attribute and relationship values)

Schema Consistency

 report warning when attributes and relationships change between 
 single-value/multi-value in case of redefinition in derived class or there 
 are such conflicts in super-classes

 change exclusiveness scope of composite relations from object to 
 relationship

 e.g. a module can be exclusively inserted to crate and to detector, but it 
 cannot be inserted to several crates

XML Parser

 report correct line number and position for certain types of problems in 
 oks xml

 fix minor memory leak in OKS xml parser

 fix several bugs with xml comments and end of comment

 skip any attributes defined in the oks-schema or oks-data tag (they can 
 come from automatic xml generation tools)

 allow xml style-sheets and xmlns tags

 allow different encodings of xml

Relational Methods using RAL

 move from POOL RAL to CORAL and follow changes in CORAL API up to latest 
 used version (CORAL 1.3.0)

 add table to keep used configurations

 normalize schema as it was recommended by CERN Oracle DBA

 store oks date and time as string

 increase length of class name (now it is limited by 64 bytes)

 use xml authentication (see file authentication.xml pointed by the 
 CORAL_AUTH_PATH variable)

General Methods

 add method to get referenced objects

 path query: check goal at non-leave object in the path to allow paths 
 with optional branches

 fix bug when TDAQ_DB_PATH is not defined

 do not print warning in silent mode (before few ones left by mistake)

General OKS Utilities

New oks-generate-schema-docs.sh
The utility generates description of the schema files using xsl conversion of 
standard oks schema xml files. Such conversion is performed by user's Internet 
browser on fly. This should work with MS Internet Explorer 6.0, Mozilla 1.7.12 
and their higher versions.

 Usage: oks-generate-schema-docs.sh [--help] [--verbose] [--search-dir in-dir] [--search-pattern schema-file-pattern] --target-dir out-dir
Arguments/Options:
 -v | --verbose verbose output
 -h | --help print this message
 -d | --search-dir in-dir directory to search schema files; current value = [/afs/cern.ch/atlas/project/tdaq/cmt/nightly/installed/share/data]
 -p | --search-pattern p pattern for schema file names; current value = [*.xml]
 -t | --target-dir out-dir directory where to put out files
 -n | --page-name name provide name for generated index.html file; current value = [TDAQ Release Schema Files]

The example of generated schema description for DAQ/HLT-I nightly release is 
available on: 

http://pcatd12.cern.ch/releases/nightly/installed/share/doc/DAQRelease/html

The utility can be used by users of the DAQ/HLT-I release to generate 
descriptions of own schema files using --search-dir to point to area with own 
schema files.

New oks-test-duplicated-objects.sh
The utility tests duplicated objects (i.e. objects with equal class names and 
IDs) stored in oks data files referenced by the TDAQ_DB_PATH variable.

The utility has been created to find files, which are bad from 
archiving point of view. In ideal case it should find no duplications.

To filter out files which need to be ignored either put file name pattern(s) 
into -s command line option, or install into in any subdirectory of ${TDAQ_INST_PATH} 
file(s) with name remove-from-oks-archive.txt containing such patterns 
(one pattern per line), e.g. run "oks-test-duplicated-objects.sh 
-v -s '.*share/data/ExampleConfiguration.*' '.*share/data/training.*'" to 
skip all files installed by the ExampleConfiguration and training 
packages.

oks_merge

 merge data files (use -o option) and schema files (use 
 -s option)

oks_diff_data

 add options to compare objects of one class or single object

oks_diff_schema

 allow data files as input (i.e. compare schemes used by data files)

 change values returned by binary to be able to report number of found 
 differences:

 | 0
 |  - 
 | there are no 
 differences between two schema files

 | 253 
 |  - 
 | bad command line

 | 254 
 |  - 
 | cannot load database file(s)

 | 255 
 |  - 
 | loaded file has no any class

 | 1..252
 |  - 
 | number of differences (is limited by the max possible value)

oks_dump

 return different status in case of different problems:

 | 0
 |  - 
 | 
 no problems found

 | 1
 |  - 
 | 
 bad command line parameter

 | 2
 |  - 
 | 
 bad oks file(s)

 | 3
 |  - 
 | 
 bad query passed via -q or -p options

 | 4
 |  - 
 | 
 cannot find class passed via -c option

 | 5
 |  - 
 | 
 loaded objects have dangling references

 new option -i adds possibility to read files to be 
 printed from input-file instead of command line to help with very long list 
 of files (that may exceed maximum command line length)

 distinguish lists of schema and data files lists on 
 user choice:

 use option -f to print list of all oks xml files (is used as before)

 use new option -s to print list oks schema files

 use new option -d to print list oks data files

 add option -r to print out list of objects referenced 
 by found objects (can only be used with query)

Utilities for OKS Archiving

All utilities described below require two parameters:

 the database connection string

 the name of the relational database working schema

The values of above parameters are site specific. For development purposes at 
CERN they are:

 | the connection string:
 | oracle://devdb10/tdaq_dev_backup

 | the working schema:
 | onlcool

For other sites or different purposes different database servers and/or accounts 
should be used. To create new database (for new owner or different DB server) 
use oks/src/rlib/create_db.sql file, e.g. in case of Oracle:

 bash$ sqlplus ${user}/${password}@${host} @$TDAQ_INST_PATH/../oks/src/rlib/create_db.sql

where ${user}, ${password} and ${host} have 
site-specific values.

New oks-create-new-base-version.sh
The utility has to be used to create a new base version in the archive. It is 
necessary when the there are changes in the configuration schemes or there are 
significant changes in the configuration data. In particular a request to use 
this utility can be send by the oks2coral binary.

By default, the utility checks differences between head schema version 
from archive and schemes found under TDAQ_DB_PATH. If there are changes, the 
utility creates new head schema in the archive. Then the utility reads 
all data files pointed by the TDAQ_DB_PATH variable and stores them into 
archive. The command line parameters used by the utility are shown below:

 Usage: oks-create-new-base-version.sh -c connect_string -w schema_name [--help] [--verbose level] [--skip-files reg-exp*]
Arguments/Options:
 -c | --connect-string connect_str database connection string
 -w | --working-schema schema_name name of relational database working schema
 -v | --verbose level switch on verbose output
 -h | --help print this message
 -s | --skip-files r1 ... list of regular expressions to ignore files

New oks_tag_data
The utility is created to set a unique string tag on any existing data in OKS 
archive. A data can be accessed by such human meaningful tag instead of schema 
and data version numbers.

 usage: oks_tag_data -c | --connect-string connect_string
 -w | --working-schema schema_name
 -t | --tag data_tag
 [-e | --head-data-version]
 [-s | --schema-version schema_version]
 [-n | --data-version data_version]
 [-v | --verbose-level verbosity_level]
 [-h | --help]
Options/Arguments:
 -c connect_string database connection string
 -w schema_name name of working schema
 -t data_tag unique tag
 -e tag head data version (for head schema or defined by -s)
 -s schema_version use data for given schema version (extra -n or -e is required)
 -n data_version use given data version (extra -s is required)
 -v verbosity_level set verbose output level (0 - silent, 1 - normal, 2 - extended, 3 - debug, ...)
 -h print this message

New oks_ls_data
The utility is created to print out information about data in OKS archive.

 usage: oks_ls_data
 -c | --connect-string connect_string
 -w | --working-schema schema_name
 [-s | --schema-version schema_version]
 [-b | --base-data-only]
 [-z | --show-size]
 [-u | --show-usage]
 [-v | --verbose-level verbosity_level]
 [-h | --help]

Options/Arguments:
 -c connect_string database connection string
 -w schema_name name of working schema
 -s schema_version print out data of this particular version (0 = HEAD version)
 -b print out base data versions only
 -z print size of version (i.e. number of relational rows to store it)
 -u show who, when, where and how used given version
 -v verbosity_level set verbose output level (0 - silent, 1 - normal, 2 - extended, 3 - debug, ...)
 -h print this message

The version is shown as sv.dv[.bv], where:

 sv - schema version;

 dv - data version;

 bv - base version (optional, only appears for incremental data 
 versions).

 For example:

 1.12 - base version with schema-version = 1 and data-version = 12

 1.34.12 - incremental version with data-version = 34 built on top of 
 base version 1.12

The size is reported when -z option is used explicitly. To get the size it is 
necessary to execute additional queries and this may take some time for big 
number of versions. The size of a base version is defined as number of rows in 
relational tables (OksObject, OksDataVal and OksDataRel) to 
describe it's data. For an incremental version the size shows numbers of 
additional rows to show differences from it's base version, i.e. such rows can 
be used to mark an object as created, removed or updated, and to provide new 
values for attributes and relationships of objects. The size is presented in 
form obj-num:attr-num:rel-num, where:

 obj-num - number of objects rows;

 attr-num - number of attribute value rows;

 rel-num - number of relationship rows.

 For example:

 951:8271:1498 - the base version contains 951 objects; the objects have 
 8271 attribute values and 1498 relationships

 1:1:0 - the incremental version has one object updated comparing with 
 base version (an attribute of the object was modified)

The usage of archived versions is reported when -u option is used explicitly. 
It requires some additional queries and may take some time for big number of 
versions. The usage of archived data is shown in table below the information 
about version. The values in Version and Size columns remain 
empty. The Description column contains information about partition and 
run number.

oks_put_schema,  oks_put_data,  oks_get_schema and oks_get_data

 use xml authentication instead of explicit user name and password passed 
 via command line

 try to re-use the same options between binaries

 to know exact options per binary run it with --help option

GUI Editors

Schema Editor

 meaningless "Many" cardinality is not supported for relationships

 check classes and files consistency during save operation

Data Editor

 fix bug, when create new object providing ID of already existing object

 do not exit, if there is an error with file saving (i.e. allow user to 
 change file name or it's permissions)

 check objects and files consistency during save operation

 refresh correctly list of all files when reload a file that changed 
 includes

 warn user about bad files during loading them (e.g. with missing 
 includes); a user should to fix reported problem before any other 
 modifications!
```

### Snapshot `oks__tdaq-01-07-00__20111107082520.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-07-00__20111107082520.html`*

```text
New Page 1

API Changes

OKS library was starting to use exceptions to report 
problems. The methods dealing with input / output operations (i.e. load...(),
save...() and new...() methods of OksKernel and related 
methods of OksClass, OksObject, OksData, etc.) throw 
oks::exception instead of returning OksStatus. 

The old code testing return status:

 OksKernel kernel;
OksFile * fh1 = kernel.load_file("test.in.xml"); # (1) can return zero in case of error!
if(fh1 == 0) { std::cerr << "ERROR: Can not load file \"test.in.xml\"\n"; exit(1); }
OksFile * fh2 = kernel.new_data("test.out.xml"); # (2) can return zero in case of error!
if(fh2 == 0) { std::cerr << "ERROR: Can not create file \"test.out.xml\"\n"; exit(1); }
... # (3) some code modifying oks data
if(kernel.save_schema(fh2) != OksSuccess) { # (4) need to check OksStatus
 std::cerr << "ERROR: Can not save file \"test.out.xml\"\n"; exit(1);
}

has to be replaced with the following one:

 OksKernel kernel;
try {
 OksFile * fh1 = kernel.load_file("test.in.xml"); # (5) always returns non-zero!
 OksFile * fh2 = kernel.new_data("test.out.xml"); # (6) always returns non-zero!
 ... # (7) some code modifying oks data
 kernel.save_schema(fh2); # (8) is void
}
catch (oks::exception & ex) { std::cerr << "Caught OKS exception: " << ex << std::endl; exit(1); }

Using exceptions there is no more need to test return 
values:

 a returned pointer is always non-zero (compare lines 
 1, 2 with 5, 6)

 save...() methods become void instead 
 of returning OksStatus (compare line 4 with 8)

Improved Reporting of XML Problems

Another advantage of exception usage is consistent error 
reporting, that is especially important in case of multiple include files. In 
the past, any error has been reported to the standard error stream in the moment 
of it's detection and in some cases without enough diagnostics. For example the 
only possibility to get name of the file where a problem took place was to read
OKS info messages:

 lxplus055:db6$ oks_dump -f /tmp/daq/partitions/be_test.data.xml
Reading data file "/tmp/daq/partitions/be_test.data.xml" in extended format (3331 bytes)...
* reading data file "/tmp/daq/segments/segments.data.xml" in extended format (10503 bytes)...
* loading 53 classes from file "/tmp/dal/schema/core.schema.xml"...
* reading data file "/tmp/DAQRelease/sw/repository.data.xml" in extended format (88245 bytes)...
* reading data file "/tmp/DAQRelease/sw/external.data.xml" in extended format (15272 bytes)...
* reading data file "/tmp/DAQRelease/sw/tags.data.xml" in extended format (1928 bytes)...
ERROR [OksXmlInputStream::read_tag_start()]:
(line 67, char 1)
Unexpected end of file
ERROR [OksXmlInputStream::read_tag_start()]:
(line 67, char 1)
Unexpected end of file
ERROR [OksObject::read_header()]:
(line 67, char 1)
Failed read start-of-object 'obj' tag

When above problem took place using oksconfig plug-in, it 
was not possible to identify the exact place of problem at all (at least without 
setting OKS_KERNEL_SILENCE to no):

 bash$ config_dump -d oksconfig:daq/partitions/be_test.data.xml -c Partition
ERROR [OksXmlInputStream::read_tag_start()]:
(line 67, char 2)
Unexpected end of file
ERROR [OksXmlInputStream::read_tag_start()]:
(line 67, char 2)
Unexpected end of file

Now the resulted exception always contains exact reason of 
error and keeps full chain of files inclusion and oks entities dependencies, 
e.g.:

 bash$ export OKS_KERNEL_SILENCE=yes
bash$ oks_dump -f /tmpdaq/partitions/be_test.data.xml
Caught oks exception:
oks[10] ***: failed to load data file "/tmp/daq/partitions/be_test.data.xml" because:
oks[9] ***: failed to load include "daq/segments/segments.data.xml" because:
oks[8] ***: failed to load data file "/tmp/daq/segments/segments.data.xml" because:
oks[7] ***: failed to load include "DAQRelease/sw/repository.data.xml" because:
oks[6] ***: failed to load data file "/tmp/DAQRelease/sw/repository.data.xml" because:
oks[5] ***: failed to load include "DAQRelease/sw/external.data.xml" because:
oks[4] ***: failed to load data file "/tmp/DAQRelease/sw/external.data.xml" because:
oks[3] ***: failed to load include "DAQRelease/sw/tags.data.xml" because:
oks[2] ***: failed to load data file "/tmp/DAQRelease/sw/tags.data.xml" because:
oks[1] ***: failed to read 'object "i686-slc3-gcc344-dbg@Tag"'
oks[0] ***: Unexpected end of file while read tag start at (line 66, char 51)

The same exception will be passed to the ERS exception 
reported by oksconfig plug-in:

 config_dump -d oksconfig:/tmp/daq/partitions/be_test.data.xml -c Partition
ERROR 2007-Jan-17 11:20:12 [ConfigurationImpl* _oksconfig_creator_(...)
at oksconfig/src/OksConfiguration.cpp:29] oksconfig initialization error
 was caused by: ERROR 2007-Jan-17 11:20:12 [virtual void OksConfiguration::open_db(...) at
 oksconfig/src/OksConfiguration.cpp:57] cannot load file '/tmp/daq/partitions/be_test.data.xml':
oks[10] ***: failed to load data file "/tmp/daq/partitions/be_test.data.xml" because:
...
oks[2] ***: failed to load data file "/tmp/DAQRelease/sw/tags.data.xml" because:
oks[1] ***: failed to read 'object "i686-slc3-gcc344-dbg@Tag"'
oks[0] ***: Unexpected end of file while read tag start at (line 66, char 51)

OKS Archiving

Add Release column to OksSchema table to 
simplify choice of right schema by oks2coral and to allow user easier choice of 
archived configuration data. There is new OKS Archiving Web GUI, allowing:

 queries on archived configurations by time intervals, 
 release, user, host and partition patterns;

 sorting result by multiple columns;

 selection which columns to be shown.

The test Web GUI replaced previous one:

http://cern.ch/isolov/cgi-bin/oks-archive.pl

Provide bootstrap files for different RDBMS:

 create_db.mysql.sql

 create_db.oracle.sql (renamed old create_db.sql)

 create_db.sqlite.sql

Fix several run-time problem for MySQL CORAL plug-in.

API changes

 Add optional release parameter to several 
 functions. It is used to get HEAD schema and data version per TDAQ release. 
 By default the release parameter points to current release (i.e. to 
 "tdaq-01-07-00").

 Add function get_max_schema_version() to know 
 maximum schema version number to be used to choose free version number. 
 Note, the existing method get_head_schema_version() returns head 
 schema version per release.

 Add function get_time_host_user() to extract 
 time, host and user values from attribute list. It is used by roks 
 library and by oks_ls_data utility.

List Archives Utility
Add several new options to specify archives 
selection criteria:

 usage: oks_ls_data
 -c | --connect-string connect_string
 -w | --working-schema schema_name
 [-l | --list-releases]
 [-s | --schema-version schema_version]
 [-b | --base-data-only]
 [-z | --show-size]
 [-u | --show-usage]
 [-d | --show-description]
 [-t | --sorted-by parameters]
 [-r | --release release_name]
 [-e | --user user_name_pattern]
 [-o | --host hostname_pattern]
 [-p | --partition partition_name_pattern]
 [-S | --archived-since timestamp]
 [-T | --archived-till timestamp]
 [-v | --verbose-level verbosity_level]
 [-h | --help] 
 Options/Arguments:
 -c connect_string database connection string
 -w schema_name name of working schema
 -l list releases
 -s schema_version print out data of this particular version (0 = HEAD version)
 -b print out base data versions only
 -z print size of version (i.e. number of relational rows to store it)
 -u show who, when, where and how used given version
 -d show description
 -t parameters sort output by several columns; the parameters may contain the following
 items (where first symbol is for ascending and second for descending order):
 v | V - sort by versions;
 t | T - sort by time;
 u | U - sort by user names;
 h | H - sort by hostnames;
 p | P - sort by partition names (i.e. by descriptions);
 -r release_name show configuration for given release name
 -e user_name_pattern show configuration for user names satisfying pattern (see syntax description below)
 -o hostname_pattern show configuration for hostnames satisfying pattern (see syntax description below)
 -p partition_pattern show configuration for partition names satisfying pattern (see syntax description below)
 -S since_timestamp show configuration archived since given moment (see timestamp format description below)
 -T till_timestamp show configuration archived before given moment (see timestamp format description below)
 -v verbosity_level set verbose output level (0 - silent, 1 - normal, 2 - extended, 3 - debug, ...)
 -h print this message 
 Description:
 The utility prints out details of oks data versions archived in relational database.
 The Version is shown as sv.dv[.bv], where:
 * sv = schema version;
 * dv = data version;
 * bv = base version (optional, only appears for incremental data versions).
 The Size (numbers of relational rows) is reported in form x:y:z, where the:
 * x = number of new[/deleted/updated] objects;
 * y = number of new[/deleted/updated] attribute values;
 * z = number of new[/deleted/updated] relationship values.
 The timestamps to be provided in ISO 8601 format: "YYYY-MM-DD HH:MM:SS".
 The allowed wildcard characters used to select by user, host and partition names are:
 % (i.e. percent symbol) - any string of zero or more characters;
 _ (i.e. underscore symbol) - any single character.

Other Implementation Changes and Bug Fixes

 replace OksAlloc class used for the memory 
 usage optimisation by the Boost class boost/pool/pool_alloc.hpp; 
 header file oks/alloc.h has been removed; OKS is always 
 initialized in multi-thread safe mode;

 when save a data file, keep the file flags

 fix run-time bug appeared on 64-bits architecture (wrong calculation of 
 const string literal size); by chance it worked correctly on 32 bits;

OKS Schema Editor

 attach Range and Initial Value properties to the right 
 side of the attribute window to allow see long strings;

 do not show Non Null Value property for boolean attribute.

OKS Data Editor

 mark file updated, when swap objects inside relationship value;

 avoid bug when copy object to existing id;

 fix bug when load query with attribute comparator.
```

### Snapshot `oks__tdaq-01-08-00__20111107082539.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-08-00__20111107082539.html`*

```text
ï»¿

Untitled 1

OKS Archiving

Add newly appeared classes (e.g. after integration with new detector) into 
schema already existing in archive (before it was required to create new 
version):

 smaller number of versions

 reduce archive toolâs downtime (human intervention is only needed when 
 the database schema is modified, but not when it is extended)

Add newly appeared objects into base data version (before such objects were 
created in the incremental version, that takes more space):

 assume that any configuration object is referenced somehow (implicitly) 
 by the partition object

 agreed with TDAQ groups and detectors; required schema changes in areas 
 where string values were used for references instead of relations 

As result, the utility to create new base or schema version in archive 
becomes much more robust since it does not require to put all data from all OKS 
repositories into base version in one go.

OKS Data Editor: Graphical Window

 fix several bugs when work with icons of small size

 add possibility to arrange objects of a relationship by one object per 
 single line, that makes OKS graphical window look like more "standard"; to 
 use it, select "Arrange" -> "One child per line" item from graphical popup 
 menu (press right mouse button in a free area of a graphical window)

OKS Library

 most kernel functions throw exceptions instead of printing error 
 messages; this allows better integration with oksconfig plug-in

 improve performance of OKS methods reading and saving database by 
 caching names of tested files and directories
```

### Snapshot `oks__tdaq-01-08-03__20111107082556.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-08-03__20111107082556.html`*

```text
ï»¿

Untitled 1

General Changes

Max Length for OKS Names
By needs of OKS archiving, limit maximum string length for attributes of some 
OKS types, which are:

 OKS Type
 Attribute
 Maximum Length

 (bytes)

 | OksObject 
 | Object ID
 | 64

 | OksClass
 | Name
 | 64

 | Description
 | 2000

 | OksAttribute
 | Name
 | 128

 | Description
 | 2000

 | Range
 | 1024

 | OksRelationship
 | Name
 | 128

 | Description
 | 2000

 | OksMethod
 | Name
 | 128

 | Description
 | 2000

 | 
 OksMethodImplementation
 | 
 Language
 | 16

 | Prototype
 | 
 1024

 | Body
 | 2048

 | OksData
 | data.STRING
 | 4000

New Oks Data Types
Add new OKS Data types:

 s64_int_type - signed 64-bits integer ("s64"); for implementation uses 
 typed on the int64_t type

 u64_int_type - unsigned 64-bits integer ("u64"); for implementation uses 
 typed on the uint64_t type

 class_type - reference on class; is implemented as string with range of 
 allowed values equal to names of classes defined by the schema; it is 
 important to put an initial value pointing to a class; if it will remain 
 empty, then OKS will complain trying to create a new object.

Above types are fully supported by oks xml files, GUI editors and archiving.

If there are already existing and used OKS relational archives, check oks/src/rlib/create_db.[oracle|mysql|sqlite].sql 
bootstrap files for technology you are using and decide if schema of existing 
archive tables have to be changed.

Bug Fixes
Use maximum compiler-supported precision when store or print out values of 
OKS float and double 
numeric 
types. Before the precision was limited to the C++ std::ostream default value = 6 
digits. E.g. it was not possible to store in OKS a double value equal to 
1.23456789, which was rounded to 1.23457.

OKS GUI Changes

New Features
The Data and Schema editors store options of graphical windows in the 
~/.oks-data-editor-rc.xml and  ~/.oks-schema-editor-rc.xml files. To produce 
those files press <Set Default Values> button from a "Set Parameters" or 
"Properties" windows. The saved values will be used as default ones when the 
editor will be started next time.

Bug Fixes and Known Problems of OKS Data Editor
Fix bug in a graphical view, when several objects were over-drawn on the same 
place.

OKS Data Editor cannot display too many graphical objects in a graphical 
view. The maximum allowed number of objects is limited by capabilities of used 
Motif Drawing Area widget limiting size of area 35767x35767 pixels. When wrap to 
visible area or one object per row arrangement was used, the vertical limit was 
already reached for M4 combined partition and resource objects. Now in such case 
the editor will report error message and suggest the user to set different 
arrangement of objects.
```

### Snapshot `oks__tdaq-01-08-04__20111107082611.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-08-04__20111107082611.html`*

```text
Untitled 1

GUI Changes

OKS Data Editor Force Save
The users have possibility to save partly-inconsistent data using
"Force Save" command. This is required to save partial work avoiding
it's possible lost because of exterior problems. For more info see
Savannah request: https://savannah.cern.ch/bugs/index.php?28879
OKS Editors Recovery Mode
The users have possibility to periodically save changes made with OKS
Schema and Data editors. Such changes automatically go to ${FILE}.saved
for any unsaved modifications. If user skips changes on exit or an
editor stops the work unexpectedly, those ".saved" files remain and can
be used for manual recovery. This option can be switched On/Off using
an editor Options menu. From the same menu it is possible to set the
period of such saving varying from 5" up to 1 hour. For more info see
Savannah request: https://savannah.cern.ch/bugs/index.php?28879

Comments
The users have possibility to add comments to files. The comments can
be
browsed and edited from File dialog of the OKS Schema and Data editors.
When file is saved, the editors can to ask user to provide comments, if
"Ask comment on file save" option is activated in the "Options" menu
(default option if user never saved GUI options). To add a comment user
has to provide non-empty text. If no comment should be added on file
save, press "Cancel" button in the Comment dialog.

XML Format Changes

The value of the "num-of-items" attribute of the oks schema info record
is ignored. This was a reason of several wrong schema files after
modifications made by users with text editors, when they forgot to set
the correct value of this attribute.

API Changes

Note: the changes are completely transparent to users of config and DAL
layers. Update your code only if
you are using OKS directly!

OksObject Class Changes
For consistent error reporting and simplification of code the following
methods have been changed.

 Old Method Spec

 New Method Spec

 | OksReturnStatus
GetAttributeValue(const std::string&, OksData **) const
 | OksData *
GetAttributeValue(const std::string&) const throw (oks::exception)

 | void
GetAttributeValue(const OksDataInfo *, OksData **) const
 | OksData * GetAttributeValue(const OksDataInfo *) const throw ()

 | OksReturnStatus
GetRelationshipValue(const std::string&, OksData **) const
 | OksData *
GetRelationshipValue(const std::string&) const throw (oks::exception)

 | void
GetRelationshipValue(const OksDataInfo *, OksData **)
 | OksData * GetRelationshipValue(const OksDataInfo *) const throw ()

 | OksReturnStatus
SetAttributeValue(const std::string&, OksData *)
 | void
SetAttributeValue(const std::string&, OksData *) throw (oks::exception)

 | OksReturnStatus
SetAttributeValue(const OksDataInfo *, OksData *)
 | void SetAttributeValue(const OksDataInfo *, OksData *) throw (oks::exception)

 | OksReturnStatus
SetRelationshipValue(const std::string&, OksData *)
 | void
SetRelationshipValue(const std::string&, OksData *) throw (oks::exception)

 | OksReturnStatus
SetRelationshipValue(const OksDataInfo *, OksData *)
 | void SetRelationshipValue(const OksDataInfo *, OksData *) throw(oks::exception)

 | OksReturnStatus
SetRelationshipValue(const std::string&, OksObject *)
 | void
SetRelationshipValue(const std::string&, OksObject *) throw (oks::exception)

 | OksReturnStatus
SetRelationshipValue(const OksDataInfo *, OksObject *)
 | void SetRelationshipValue(const OksDataInfo *, OksObject *) throw (oks::exception)

 | OksReturnStatus
SetRelationshipValue(const std::string&, const std::string&,
const std::string&)
 | void
SetRelationshipValue(const std::string&, const std::string&,
const std::string&) throw
(oks::exception)

 | OksReturnStatus
AddRelationshipValue(const std::string&, OksObject *)
 | void AddRelationshipValue(const std::string&, OksObject
*) throw (oks::exception)

 | OksReturnStatus
AddRelationshipValue(const OksDataInfo *, OksObject *)
 | void
AddRelationshipValue(const OksDataInfo *, OksObject *) throw (oks::exception)

 | OksReturnStatus
AddRelationshipValue(const std::string&, const std::string&,
const std::string&)
 | void AddRelationshipValue(const std::string&, const
std::string&, const std::string&) throw (oks::exception)

 | OksReturnStatus
RemoveRelationshipValue(const char *, OksObject *)
 | void
RemoveRelationshipValue(const std::string&, OksObject *) throw (oks::exception)

 | OksReturnStatus
RemoveRelationshipValue(const OksDataInfo *, OksObject *)
 | void RemoveRelationshipValue(const OksDataInfo *, OksObject
*) throw (oks::exception)

 | OksReturnStatus
RemoveRelationshipValue(const std::string&, const std::string&,
const std::string&)
 | void
RemoveRelationshipValue(const std::string&, const std::string&,
const std::string&) throw
(oks::exception)

Also by needs of config Python bindings one new method have been added:
std::list<OksObject *> * get_all_rels(const std::string& name = "*") const
The method returns list of objects which have a reference on given one.
If the relationship name is set to "*", then the method takes into
account  all relationships of all objects. The method performs
full scan of all OKS objects and it is not recommended at large scale
to build complete graph of relations between all database object; if
only composite parents are needed, them the reverse_composite_rels()
method has to be used.

By needs of tidb package there are two new methods to read OksObject
from and to it put into standard streams:

 static OksObject * get(std::istream&, OksKernel *) throw (oks::exception)

 void put(std::ostream&) const throw (oks::exception)

OksClass Class Changes

By needs of tidb package there are two new methods to read OksClass
from and to it put into standard streams:

 static OksClass * get(std::istream&, OksKernel *) throw (oks::exception)

 void put(std::ostream&) const throw (oks::exception)

OksFile Class Changes
To improve error reporting the following methods throw exception
instead of returning bad error code:

 Old Method Spec
 New Method Spec

 | Oks::ReturnStatus
lock(bool = false)
 | void
lock(bool force = false) throw (oks::exception)

 | Oks::ReturnStatus unlock()
 | void unlock() throw
(oks::exception)

 | Oks::ReturnStatus
set_logical_name(const std::string &)
 | void
set_logical_name(const std::string& name) throw (oks::exception)

 | Oks::ReturnStatus set_type(const
std::string &)
 | void set_type(const
std::string& type) throw (oks::exception)

OksKernel Class Changes
For consistent error reporting and consistent naming convention on
methods names the following
methods have been changed.

 Old Method Spec
 New Method Spec

 | OksReturnStatus
set_active_schema(OksFile *)
 | void
set_active_schema(OksFile *) throw (oks::exception)

 | OksReturnStatus
set_active_data(OksFile *)
 | void set_active_data(OksFile *)
throw (oks::exception)

 | bool
GetAllowDuplicatedObjectsMode() const
 | bool
get_allow_duplicated_objects_mode() const

 | void
SetAllowDuplicatedObjectsMode(const bool)
 | void
set_allow_duplicated_objects_mode(const bool)

 | bool
GetVerboseMode() const
 | bool
get_verbose_mode() const

 | void SetVerboseMode(const bool)
 | void set_verbose_mode(const bool)

 | bool
GetSilenceMode() const
 | bool
get_silence_mode() const

 | void SetSilenceMode(const bool)
 | void set_silence_mode(const bool)

 | bool
GetProfilingMode() const 
 | bool
get_profiling_mode() const 

 | void SetProfilingMode(const bool)
 | void set_profiling_mode(const
bool)

The OKS kernel provides new methods to check status and to change
various kernel modes:

 the status of mode checking maximum length of string attributes
of some OKS objects (see also 1.8.3
OKS release notes):

 static bool get_skip_max_length_check_mode()

 static void set_skip_max_length_check_mode(const bool)

it can also be set using
OKS_SKIP_MAX_LENGTH_CHECK environment variable.

 the status of the mode testing inherited duplicated objects:

 bool get_test_duplicated_objects_via_inheritance_mode() const

 void set_test_duplicated_objects_via_inheritance_mode(const bool)

There are new methods to backup schema and data files (the operation is
silent and ignores any consistency rules):

 void backup_data(OksFile * pf, const char * suffix = ".bak") throw (oks::exception)

 void backup_schema(OksFile * pf, const char * suffix = ".bak") throw (oks::exception)

There are new methods to create OksClass and OksObject objects from
standard streams:

 OksObject * create_object(std::istream& input) throw (oks::exception)

 OksClass * create_class(std::istream& input) throw (oks::exception)
```

### Snapshot `oks__tdaq-01-09-00__20111107082613.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-01-09-00__20111107082613.html`*

```text
Untitled 1

OKS Library

 reload any consistent data file (also including changes in the
included files)

 speed up OKS XML loading (about 25% faster comparing with release
1.8.4)

 when read XML schema file, throw exception if base class is not
loaded

 oks query supports regular expressions (add attribute comparator
'~=')

OKS Archiving Library

 use temporal tables to create "try" incremental data version (to
reduce unnecessary overhead on Oracle stream replication as requested
by ATLAS Oracle DBA)

OKS GUI Library

 add support for mouse wheel (can be used in most dialogs of OKS
schema and data editors)

OKS Data Editor

 improvements in the Find/Replace dialog:

 optionally find by Class and Attribute/Relationship names

 present result as table

 select visible classes by name and objects by
UID (Savannah request http://savannah.cern.ch/bugs/?34890)

 see search panel at bottom of main window and object dialogs

 the search panel supports simple string search (auto-select
when modify the selection pattern) and regular expressions (press
button appearing
when this option selected to apply regular expression)

 improve performance when build class dialog containing big number
of objects (can be seen in 1.8.4 when number of objects is greater than
10K)
```

### Snapshot `oks__tdaq-02-00-00__20111107082627.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-02-00-00__20111107082627.html`*

```text
Untitled 1

C++ API Changes

Use new integer types from <stdint.h> to support 64-bits platform
as shown in the following table:

 OKS
Type

 Old
C++ Type

 New
C++ Type

 |  s8 (8-bits signed integer)

 | unsigned
char

 | uint8_t

 |  u8 (8-bits unsigned integer)

 | signed
char

 | int8_t

 | s16 (16-bits signed integer)

 | unsigned
short

 | uint16_t

 | u16 (16-bits unsigned integer)

 | signed
short

 | int16_t

 | s32 (32-bits signed integer)

 | unsigned
long

 | uint32_t

 | u32 (32-bits unsigned integer)

 | signed
long

 | int32_t

OKS Server

On Point-1 access to database repository will be controoled by the OKS
Server. Read more about it on the TWiki
page.

OKS Data Editor Changes

 Add search by file name in the main window

 Add search by class and object ID in the Data File dialog

 Add group file operations from the File menu:

 Save all updated files (<Ctrl-S> shortcut)

 OKS server related operations:

 Release User Repository (<Ctrl-D> shortcut)

 Update User Repository (<Ctrl-U> shortcut)

 Commit User Repository (<Ctrl-C> shortcut)

 Add "Referenced By" function from Object dialog (available on
right mouse click from dialog's icon)
```

### Snapshot `oks__tdaq-02-00-01__20111107082647.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-02-00-01__20111107082647.html`*

```text
Untitled 1

OKS Server

 the oks-commit.sh supports directories in addition to files

 add oks-import.sh utility to simplify import of new directories
and files

 the repository locks remain from abnormally terminated oks
commits can be removed on Point-1 by DAQ experts using
/oks/admin/unlock-repository.sh script via sudo

 the "Replace" dialog of OKS Data editor proposes user to
check-out repository file containing modified objects

 file-related relative pathnames and absolute pathnames includes
are not allowed (in
particular to avoid inclusion of files stored outside current
repository and to simplify consistency check by oks-commit.sh)

Read more details on the TWiki
page.

OKS Performance Improvements

 the OKS library uses pool of threads to load OKS data files, i.e.
the data files can be read in parallel

 the number of threads by default is equal to number of the
computer's CPU cores

 it can be modified via OKS_KERNEL_THREADS_POOL_SIZE environment
variable

 the OKS library does not stop reading of files on first error,
but continues loading of files in parallel threads until their ends or
errors

 thus the final error report may contain several errors coming
from different files

 this error report may change between different runs of OKS
utilities even if the files were not updated

 for optimal performance it is recommended:

 to reduce number of schema files (at some point after a schema
file parsing OKS requires single active thread to update the database
schema)

 to avoid huge data files (processing of single data file is not
parallelized since XML files are non indexed)
```

### Snapshot `oks__tdaq-02-01-00__20111107082657.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-02-01-00__20111107082657.html`*

```text
Untitled 1

To simplify future release patching
procedure the oks package was split on two packages: oks and oks_utils.
The oks package only contains library. All utilities including editors,
relational oks and oks server were moved to oks_utils package.

The changes of OKS library since tdaq-02-00-03 initial build include:

 use Boost date and time format instead of OWL package classes
(patched in tdaq-02-00-03)

 performance improvements of XML files parsing (partly implemented
as tdaq-02-00-03 patch)

 substitute round brackets
variable name by value before error reporting (see tdaq-02-00-03

 patch https://savannah.cern.ch/patch/index.php?3619)

 checking of date and time
attribute initial values (see tdaq-02-00-03 patch https://savannah.cern.ch/patch/index.php?3656)

 provide a possibility for fast objects destruction required for
RDB server (see tdaq-02-00-03 patch https://savannah.cern.ch/patch/?3798)

 throw exception, if a schema file is modified on data files
reload (see tdaq-02-00-03 patch https://savannah.cern.ch/patch/?3798)

 add mode, when duplicated classes are not allowed
```

### Snapshot `oks__tdaq-04-00-00__20111107082709.html`
*Local file: `output/extracts/pcatd12/oks__tdaq-04-00-00__20111107082709.html`*

```text
RELEASE_NOTES

 OKS Library

 Fix bug with wrong
 objects list returned by referenced_by() method from config
 package. The patch fixes calculation of RCRs by
 OksObject::SetRelationshipValue(const OksDataInfo * odi, OksData * d)
 method (see bug
 82615).

 Fix problem when OKS
 file was created incorrectly by third-party tools: if creation date tag in the info
 section is missing (see bug 70563), after saving by OKS on
 reload it resulted "not-a-date-time" error.

 Fix several internal
 problems connected with execution of OKS code in several
 threads and several OKS kernels discovered during RDB writer server exploitation:

 bug 76158: the server may go into error state
 when several clients are updating OKS server repository;

 bug 78326: the server may crash, when several
 clients actively update database caused by fast boost
 allocator with null mutex;

 bug 82762: the server may crash under
 certain conditions during database reload.
```

## 2. `config` package release notes (12 pages, archived 2011-11-06)

The `config` package is the ATLAS 2011-2014 configuration program (and the config-data legacy library `Config` on which the DAL was layered); before OKS took over it held the configuration database APIs.

### Snapshot `config__tdaq-01-01-00__20111106134653.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-01-00__20111106134653.html`*

```text
RELEASE_NOTES

Change Mechanism to Modify Attribute Values

The mechanism used for user-defined modification of attributes values has
been changed.

Before a user-defined function was used, which was invoked when an attribute
of certain type was read from database. This was not flexible enough, since
parameters of the function were not defined by the user.

The substitution function was replaced by the substitution object. The user
defines a class as he likes and can define any parameters he needs. The only
rules he has to follow are:

 class must to inherit from template class ::Configuration::AttributeConverter<T>
 class, where template parameter T defines type of attributes which values
 need to be converted

 class must to implement virtual method convert(), which makes the
 real conversion of attribute values

To register a converter object the user needs to create an object of his
class dynamically and pass pointer to the ::Configuration::register_converter()
method. The configuration destructor will destroy all registered converter
objects itself, so user must not do it himself and be careful with registering
of the same object more than once.

Example
Below there is example, which demonstrates how to write a simple class, which
will add user-defined prefix to values of attributes of string type.

 class AddPrefix : public ::Configuration::AttributeConverter<std::string> {
 private:
 std::string my_prefix; // keep parameters, provided by user (a single string in our case, but can be everything also)
 public:
 AddPrefix (const std::string& s) : my_prefix(s) {;} // constructor to initialize user parameters
 virtual void convert(std::string& value, const ::Configuration&, const ::ConfigObject&, const std::string&) {
 if(...) value = my_prefix + value; // the code, which in some cases does the conversion
 }
};
 ...
 ::Configuration db(...);
db.register_converter(new AddPrefix("test-")); // registration of the conversion object

Get Objects Referencing Given Object

If there is a composite relationship between two classes (e.g. from class A
to B), then there is a fast way to get value of reverse relationship. E.g. if
class A has composite relationship X to class B, then from given object of class
B one can get information about objects of class A pointing to this object via
relationship X. In particular this can be useful to answer a question "Whom
this object belongs?", e.g. if a crate contains list of modules, then
the operation to get crate of this module is straightforward.

The list of objects referencing given one can be obtained using two methods:

 template<class T, class V> bool ::Configuration::referenced_by(const T& obj, const std::string& relationship_name, std::vector<const V*>&
 objects, bool init = false)

 bool referenced_by(const std::string& relationship_name, const std::string& class_name, std::vector<ConfigObject>& value)

The first method should be used for objects of classes generated by the
genconfig. Below there is example to get crates referencing given module via
relationship "Modules":

 ::Configuration db(...);
::daq::core::Module m = db.get<daq::core::Module>("my module"); // get a module by any mean, e.g. by ID
std::vector<const daq::core::Crate *> crates; // the output vector
db.referenced_by(m, "Modules", crates); // get crates referencing given module
std::cout << "Module " << m << " is referenced by " << crates.size() << " crates\n";
if(crates.size() > 0) { std::cout << "first crate is = " << crates[0] << std::endl; }

The second method should be used by developers, which use config abstract
database API directly.

Bug Fixes

 Fix bug with access of inexistent objects by ID. In the past first attempt
 to read inexistent object returned null, that is correct. However by
 mistake such null pointer was registered in the cache of read objects of
 that class. Under certain circumstances (e.g. next access with the same ID)
 it resulted an error.

 Allow ::ConfigObject point to null implementation object. It is
 required, when the ConfigObject is initialised by the ::Configuration::get(relationship,
 obj)

 method and the relationship's value is set to null. Before in such
 case the method returned false and there was no way to differentiate
 between an error and the null value of relationship. Now the method's
 behaviour was corrected: it returns false only if implementation
 method fails; if the relationship is not set in the database, the method
 returns true and the ConfigObject points to null.
```

### Snapshot `config__tdaq-01-02-00__20111106134706.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-02-00__20111106134706.html`*

```text
Statistics on template objects

Statistics on template objects

The mechanism to get statistics information on generated DAL's objects
created by user process has been implemented. When the ::Configuration object is
destroyed, it prints out information about read object's references, full
objects and numbers of client cache hits. This only works, if the user defines
environment variable TDAQ_DUMP_CONFIG_PROFILER_INFO.

Example
Below there is example, which demonstrates how to use and to interpreter the
profiling:

bash$ export TDAQ_DUMP_CONFIG_PROFILER_INFO=1
bash$ dal_dump_apps --oks -d daq/partitions/lxplus_tests.data.xml -p onlsw_test_3x3_lxlpus -a 'lxplus-3x3-33 ctrl
...
Configuration profiler report:
number of created template objects: 152
number of read template objects: 22
number of cache hits: 160

The number of created template objects shows how many references on
the database objects were created inside user process. Note, creation of
references does not mean the database object was read and this is relatively inexpensive
operation from performance point of view. By default the values of an object's
attributes and relationships are read, when they are accessed explicitly by
user's code.

The number of read template objects indicates how many objects were
actually read because user's code accessed value of an attribute or a
relationship. It is desirable to reduce such number as much is possible to gain
a performance.

The number of cache hits shows client cache effectiveness. This means
a requested object has been taken from user's application cache instead of
database.

Database loading

Add new environment variable TDAQ_DB_NAME, which has higher priority than
TDAQ_DB_DATA to define name of the database to be loaded. It is a temporal
solution to allow multiple RDB servers used inside single partition. If RDB
implementation is used, it is necessary to define TDAQ_DB_NAME environment
variable at the partition level and to set it's value to the "RDB"
since it is required by the TDAQ setup (e.g. see partition be_test from daq/partitions/be_test.data.xml
as example).

If parameter of the Configuration::load() method is empty, then it
uses one of above environment variables to load database. It is requested by the
Control WG to allow DSA supervisor to re-load a database without knowing it's
exact name.
```

### Snapshot `config__tdaq-01-04-00__20111106134711.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-04-00__20111106134711.html`*

```text
Statistics on template objects

Database Implementation Plug-ins

The plug-ins technique makes database applications truly independent from
available database implementations:

 there is no anymore implicit link between database application code and
 implementation's headers and libraries;

 if new implementation is available, or an existing one is modified, there
 is no need to re-link or to re-compile user's applications

The config database implementation (to be used by the application) is defined
by one and only one parameter, that is TDAQ_DB environment variable. It
contains name of the implementation and it's initialization parameter separated
by colon, e.g.:

 | TDAQ_DB="oksconfig:daq/partitions/be_test.data.xml"
 |   
 | 
 # use oks and file daq/partitions/be_test.data.xml

 | TDAQ_DB="rdbconfig:RDB"
 |   
 | # use rdb and server
 with name RDB

Previous environment variables such as TDAQ_DB_IMPLEMENTATION, TDAQ_DB_DATA,
TDAQ_DB_NAME are not used by the plug-ins technique.

The same TDAQ_DB variable format is used for both C++ in Java:

 in case of C++ the plug-in name is translated into shared library name,
 that is loaded dynamically and to be found in the LD_LIBRARY_PATH

 in case of Java the plug-in name is translated into names of Java package
 and class, that is searched in the CLASSPATH

C++ code changes
The creation of the configuration object requires to pass one string
parameter only.

To get such parameter from environment variable TDAQ_DB leave it empty as
shown below:

::Configuration db("");

If the parameter can optionally be set via command line or provided by a different
mean, the code shown below is recommended. Note the way, how error is reported,
since the user does not know exact parameter used for the configuration object
construction:

std::string db_spec;
if(...) db_spec = ...; // optionally set parameter, e.g. from command line
::Configuration db(db_spec);
if(!db.loaded()) {
 std::cerr << "ERROR: cannot load database \"" << db.get_impl_spec() << '\"' << std::endl;
}

Java code changes
The Java code to build configuration object is very similar to C++. Use
configuration object constructor with string parameter. If it is empty string,
then the value of the TDAQ_DB environment variable will be used. An example of
code is shown below:

String db_spec;
if(...) db_spec = ...;
try {
 config.Configuration db = new config.Configuration(db_spec);
}
catch (config.SystemException ex) {
 System.err.println( "ERROR: caught \'config.SystemException\':\n" + ex.getMessage());
}

C++ binary linkage
Only link your binary with config library, i.e. use -lconfig. Implementation plug-in will be loaded automatically at run-time.

Old Configuration Constructors

The user's code using old approach will be compiled and will work as before.
It is not necessary to modify it immediately. However this should be done by
next TDAQ release.

Config dump  binary
The new binary config_dump can be used to dump contents of any
database object using new implementation plug-in technology. Examples below show
how to print out partition objects stored in the oks data file be_test.data.xml
and defined on the RDB server running in the partition be_test:

 config_dump -d "oksconfig:daq/partitions/be_test.data.xml" -c Partition
config_dump -d "rdbconfig:be_test::RDB" -c Partition

Java Attribute Converters

Java config package supports attribute converters in the way similar to
existing C++ ones. This allows in particular to substitute variable parameters
in the strings attributes, that is widely used by the TDAQ configuration
databases. See dal package release notes for examples.

Bug Fixes

Fix problem with Configuration::cast() method. Now it checks, the target and 
source objects are physically the same. Before it was possible to cast source 
object to any target class, if it contained an object with ID of source object.
```

### Snapshot `config__tdaq-01-06-00__20111106134722.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-06-00__20111106134722.html`*

```text
New Page 1

Important Changes: no more obsolete configuration constructors!

Obsolete Configuration constructors and helper function are no more 
supported. See release notes from tdaq-01-04-00 release explaining details of 
new plug-in based constructors and required changes in user's code:

http://lnxatd01.cern.ch/cmt/releases/download/tdaq-01-04-00/RELEASE_NOTES.html#config

If your code does anything listed below, it has to be modified:

 is using Configuration(const std::string&, ConfigurationImpl *) 
 or Configuration(ConfigurationImpl *) constructor

 includes removed dal/implementation.h header or is using 
 daq::core::create_config_implementation() function

 includes rdbconfig/RdbConfiguration.h header, which is not 
 installing anymore (it is only used internally by the rdbconfig plug-in) or 
 uses RdbConfiguration class

 includes oksconfig/OksConfiguration.h header, which is not 
 installing anymore (it is only used internally by the oksconfig plug-in) or 
 uses OksConfiguration class

Caching of config implementation objects

Before only template objects were stored in the client's cache and the 
implementation objects were read from the database each time when 
Configuration::get(..., ConfigObject&) methods were used. If rdbconfig 
implementation was used, this caused new network operation per call. Now all 
implementation objects are also stored in the Configuration object's cache.

Local cast()

Before the Configuration::cast() method asked database implementation, 
if given object can be casted to an object of target class (i.e. if the target 
class is one of the database object's super-classes). Now the information about 
super-classes hierarchy is stored by the Configuration object and any cast() 
operation is local to client, i.e. no any network operations are required in 
case of rdbconfig usage.

Also fix bug when null pointer was passed to the cast() method: now Configuration::cast<T>(0) 
always returns 0.

Read several implementation objects at one call

An object may have several references to other objects. In general, our 
configuration is the directed graph built from interlinked objects, where the 
partition object is the entry point to navigate to any other object used in the 
configuration. By the other words any object used in the configuration can be 
accessed via references starting from the partition object.

Before each new implementation object was read in a separate call, that 
required in case of the rdbconfig implementation new network operation. This 
significantly slowed down performance of database service, when some type of 
applications tried to scan most of the objects in the database, e.g. to find an 
object with certain parameters going through hierarchy of all 
partition/segments/resources&applications objects. Partly this problem was 
solved using path-queries introduced in summer 2005.

Now, when an object is read from the database, it is possible to define, if 
the implementation objects referenced by it are also have to be read and stored 
in the client's cache by the same call. For the moment it is done via new 
[optional] parameter called "references-level", that can be defined for 
any sort of Configuration::get() methods dealing with ConfigObjects 
and template objects. This parameter defines how many levels of references 
between objects we want to follow starting from the object(s) returned by the 
method, e.g. for ConfigObject API:

 Configuration db;

 ConfigObject partition;

 db.get("Partition", "be_test", partition,
 0 /*rlevel*/);  
 // (1) read ONLY partition object

 db.get("Partition", "be_test", 
 partition, 1 /*rlevel*/);  
 // (2) read partition object and all objects directly 
 referenced by it (i.e. segments of first level)

 db.get("Partition", "be_test", partition,
 2 /*rlevel*/);  
 // (3) read partition object, all objects 
 referenced 
 by it and all objects directly referenced by them 
 (i.e. segments of first level & their applications and segments of second 
 level)

 db.get("Partition", "be_test", 
 partition, 10 /*rlevel*/); 
 // (4) very probably read ALL objects 
 used for given configuration

In a similar way, this can be used for template objects:

 Configuration db;

 daq::core::Partition * p;

 p = db.get<daq::core::Partition>("be_test", false, true, 0
 /*rlevel*/);  // (5) read
 ONLY partition object

 p = db.get<daq::core::Partition>("be_test", 
 false, true, 10 /*rlevel*/); 
 // (6) very probably read ALL objects 
 used for given configuration

In addition to above, a user may decide that he needs to read referenced 
objects belonging to certain classes only. To do this there is one extra 
optional parameter not shown in above examples, that is called "referenced-classes". 
It is a pointer to vector of string defined names of base classes. If it is not 
0, then only objects of such classes or derived from them will be cached. 
Example:

 Configuration db;
daq::core::Partition * p;

 std::vector<std::string> rc;

 rc.push_back("BaseApplication");

 rc.push_back("Computer");

 p = db.get<daq::core::Partition>("be_test", false, true, 
 10, &rc);  // (7) read applications 
 and computers used in partition

Also such parameters are available in the algorithm from dal package 
used to get partition object:

 const daq::core::Partition * daq::core::get_partition(
 ::Configuration& conf, const std::string& pname, unsigned long rlevel = 7, const std::vector<std::string> * rclasses = 0);

It is up to user to decide, if above parameter has to be set to values 
different from default ones. If the reference level is too small, there is a risk for too many 
additional network calls in case of rdbconfig implementation. If it is too big, 
there is a risk the user's application will read too much data, which it does 
not use (e.g. detector specific config objects, which can be quite big). In any 
case, avoid a setting of such parameter to big numbers if many Configuration::get() 
methods are used, since this will increase total amount of the same data read 
multiple times. Ideally one should to prepare right set of parameters once when 
top-level configuration object is accessed using get() method and read 
all other configuration objects via navigation from the top-level object.

Profiling config objects access

It is possible to get information about effectiveness of database service 
usage by setting TDAQ_DUMP_CONFIG_PROFILER_INFO variable. For example:

 export TDAQ_DUMP_CONFIG_PROFILER_INFO=1
ipc_server &
rdb_server -d be_test -D daq/partitions/be_test.data.xml &
dal_dump -d rdbconfig:be_test -c Segment
... skip several hundreds of lines of segments descriptions
Configuration profiler report:
number of created template objects: 54
number of read template objects: 13
number of cache hits: 57
Configuration implementation profiler report:
number of read objects: 49
number of cache hits: 46
RdbConfiguration profiler report:
number of xget_object() calls: 0
number of xget_all_objects() calls: 1
number of xget_objects_by_query() calls: 0
number of get_objects_by_path() calls: 0
number of get_object_values() calls: 0

From above one can see, that:

 54 template objects were created and attributes of 13 of them were read 
 (see Configuration profiler report)

 49 implementation objects (i.e. instances of ConfigObject) were read (see
 Configuration implementation 
 profiler report)

 all above required 1 (only one!) rdb operation (see xget_all_objects() 
 statistics from the RdbConfiguration profiler report)

 The same from tdaq-01-04-01 requires several tens of rdb network operations.

Access deleted template objects

 When a template object is deleted (e.g. via subscription mechanism or by 
 explicit user call), it is marked as deleted. When user accesses it, the 
 config::DeletedObject exception is thrown. Note, deletion of an object may 
 cause several deleted template objects, e.g. via inheritance (deletion an 
 object results deletion of all template objects built from it) or via 
 dependent composite references (deletion of parent may cause deletion of 
 it's dependent children). If user keeps pointers on template objects, which 
 can be deleted by any of above means, it is necessary to catch the 
 config::DeletedObject or more general exceptions, from which it is derived. 
 Below there is example:
 Crate * crate = db.create<Crate>("/tmp/data.xml", ""); // create crate
vector<Module*> modules(1, db.create<Module>(*crate, ""); // create array containg one module
crate->set_Modules(modules); // set modules of crate; the relationship Crate->Modules is DEPENDENT
std::cout << "1. The module's name is " << modules[0].get_Name() << std::endl; // OK, print the module's name
db.destroy(*crate); // destroy crate and all it's modules
try {
 std::cout << "2. The module's name is " << modules[0].get_Name() << std::endl; // ERROR, the module was removed !!!!
}
catch ( config::GenericException& e ) {
 std::cerr << "Caught config exception: \"" << e.what() << '\"' << std::endl;
}

Other Changes

Add method to get super-class hierarchy

 const std::map<std::string, std::set<std::string> >& Configuration::superclasses() const;

If a class has super-classes, it's name is stored as key that points to names 
of super-classes via value.

Add parameter to check if database exists
Set silent mode to true to check if database exists or not:

 bool Configuration::load(const std::string& db_name, bool silent = false);
```

### Snapshot `config__tdaq-01-06-02__20111106134740.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-06-02__20111106134740.html`*

```text
New Page 1

Performance Improvements

There is a performance improvement, that can be 
used by plug-ins (in particular it is used by the rdbconfig implementation). The 
config library now shares implementation config object for instantiations of all 
generated DAL parent classes.

Technically this becomes available due to new 
Configuration::subclasses() method, returning subclasses hierarchy of 
database classes.

Example
The class C is derived from class B, and the class B is 
derived from class A. User creates object c of class C, 
object b of class B and object a of class A using 
the same database object. All such objects a, b and c share 
the same config object (that will be read once via network in case of 
rdbconfig implementation).
```

### Snapshot `config__tdaq-01-07-00__20111106134757.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-07-00__20111106134757.html`*

```text
API Changes

Since last public TDAQ release there are important 
public API changes, which can require modifications of the user's code!

Public API Changes: Migration to ERS

The interfaces of configuration packages were implemented long time ago, when 
used compilers did not supported exceptions. By that reason most of the methods 
of configuration classes returned boolean status to indicate that a 
method was successful or had a problem.

During summer 2006 the DAQ/HLT-I coordination group took a decision the

ERS has to be used by all packages of TDAQ release to report problems 
starting from TDAQ release 01-07-00. Now the status reporting mechanism of 
methods of config classes has been changed: to report a problem they throw ERS 
exception and the return type of them is changed to void.

Each method of config classes and classes of data access libraries generated 
by genconfig has explicit exception specification. For complete information 
about particular method see generated Doxygen documentation or appropriate 
header files. The following config exceptions can be thrown:

 daq::config::Generic is used to report most of the problems (bad 
 database, wrong parameter, plug-in problems, etc.);

 daq::config::NotFound is thrown when a config object accessed by 
 ID is not found, or a class accessed by name is not found;

 daq::config::DeletedObject is thrown when accessing template 
 object that has been deleted (via notification mechanism or by the user's 
 code modifying database) - exists since previous release.

All above exceptions have common class daq::config::Exception, which 
in turn is derived from the ers::Issue. The catch of 
daq::config::Exception is recommending to be used, if exact reason of error 
is not important for the user's code.

If the method's exception specification is throw(), then such method 
does not throw any exception.

Below there are several examples of changes.

Example 1. Loading of database
In the past to check status of the database loading it was necessary to use 
special method loaded() as shown below: 

 std::string data("oksconfig:db.data.xml");
Configuration db(data);
if(!db.loaded()) {
 std::cerr << "ERROR: cannot load database " << data << std::endl;
 return;
}
... // code working with database

Now the call of the method loaded() is not needed any more. One can 
catch exception in a common try / catch block as shown below: 

 try {
 Configuration db("oksconfig:db.data.xml");
 ... // code working with database
}
catch (daq::config::Exception & ex) {
 std::cerr << "Caught exception " << ex << std::endl;
 return;
}

Example 2. Get object by id
There are two ways to get an object by id: using config layer defined by this 
package and using generated data access library layer (see genconfig and e.g. 
dal packages).

The correct old code to get an object using the config layer was: 

 // return true if object has been printed
bool print_obj(::Configuration& db, const std::string& class_name, const std::string& object_id) {
 ConfigObject obj;
 // try to get object
 // in case of an error, the plug-in reports the problem to standard error stream
 if(db.get(class_name, object_id, obj) == false) {
 std::cerr << "ERROR: cannot get object " << object_id << " of class " << class_name << std::endl;
 return false;
 }
 std::cout << obj;
 return true;
} 

Now it has to be replaced by: 

 // return true if object has been printed
bool print_obj(::Configuration& db, const std::string& class_name, const std::string& object_id) throw() {
 try {
 ConfigObject obj;
 db.get(class_name, object_id, obj);
 std::cout << obj;
 return true;
 }
 catch (daq::config::NotFound& ex) {
 std::cerr << "ERROR: cannot get object " << object_id << " of class " << class_name << std::endl;
 }
 catch (daq::config::Generic& ex) { // catch and report plug-in errors
 std::cerr << "Caught exception " << ex << std::endl;
 }
 return false;
}

In case when generated DAL layer is used to get a template object by ID, the
daq::config::NotFound exception is not thrown, but it is necessary to 
catch generic daq::config::Exception as shown below:

 // return true if object has been printed
bool print_application(::Configuration& db, const std::string& object_id) throw() {
 try {
 const daq::core::BaseApplication * a = db.get<daq::core::BaseApplication>(object_id);
 if(a) { std::cout << *a << std::endl; return true; }
 else { std::cerr << "ERROR: there is no application object with id " << object_id << std::endl; }
 }
 catch (daq::config::Exception& ex) { // catch and report plug-in errors, also can use here daq::config::Generic
 std::cerr << "Caught exception " << ex << std::endl;
 }
 return false;
}

Example 3. Access objects of class by query 
In a similar way to above, the config layer can throw daq:config::NotFound 
exception, if there is no class with given name, see:

 const char * class_name = "Segment";
try {
 Configuration db("rdbconfig:RDB");
 std::vector<ConfigObject> objects;
 db.get(class_name, objects); // get all objects of class "Segment"
 std::cout << "There are " << objects.size() << " objects of " << class_name << " class\n";
}
catch(daq::config::NotFound& ex) {
 std::cerr << "Wrong database schema, caught " << ex << ". Check the right database is used!\n";
}
catch(daq::config::Exception& ex) {
 std::cerr << "Caught exception " << ex << std::endl;
}

For corresponding generated data access library template method get() 
the daq::config::NotFound exception is not thrown. In case if a database 
with wrong schema is loaded, the problem is reported by daq::config::Generic 
exception:

 try {
 Configuration db("rdbconfig:RDB");
 std::vector<const daq::core::Segment*> objs;
 db.get(objs); // get all objects of class "Segment"
 std::cout << "There are " << objects.size() << " objects of Segment class\n";
}
catch(daq::config::Exception& ex) {
 std::cerr << "Caught exception " << ex << std::endl;
}

Example 4. Access object's attributes and relationships 
In the past it was necessary to check boolean status of generated DAL 
set method and get/set status of config layer methods dealing with 
attributes and relationships. Now all such methods are void and throw 
generic daq::config::Exception in case of problems, e.g.: 

 ::ConfigObject obj = ...;
std::string name;
if(obj.get("Name", name) == false) { std::cerr << "ERROR: cannot read Name attribute" << std::endl; }
ConfigObject item;
if(obj.get("Item", item) == false) { std::cerr << "ERROR: cannot read Item relationship" << std::endl; }
daq::core::Application * a = ...;
name = a->get_Name();
const daq::core::Item * i = a->get_Item();

Now such code needs to be changed to the following:

 try {
 ::ConfigObject obj = ...;
 std::string name; obj.get("Name", name);
 ConfigObject item; obj.get("Item", item);
 daq::core::Application * a = ...;
 name = a->get_Name();
 const daq::core::Item * i = a->get_Item();
}
catch (daq::config::Exception& ex) {
 std::cerr << "Caught exception " << ex << std::endl;
}

Modify Update-on-notification

When receive a notification, update objects of derived classes stored in the 
clients configuration cache (this problem has been found in the Run Control). 
Note, the update of direct and base classes in case of notification was 
implemented before.

Below there are several examples explaining different mechanisms of objects 
updates in client's cache depending on subscription:

 class B is derived from class A, class C is derived 
 from class B;

 there are objects a, b, and c created from 
 corresponding classes A, B and C;

 all objects a, b and c are read into client's 
 configuration cache, i.e.
 class A has objects a, b (class B is a 
 subclass of class A), c (class C is a subclass of 
 class A);

 class B has objects b, c (class C is a 
 subclass of class B);

 class C has object c;

 all objects a, b and c been updated;

 client subscribes on one notification of all objects of class 
 A, B or C (e.g. subscribe on all changes of objects in 
 class B).

Example of direct classes update (implemented in previous release)

 clients subscribes on changes in class A: objects a, b,
 c modification results their update in the client's cache (i.e. a,
 b, c objects for class A);

 clients subscribes on changes in class B: objects b, c 
 modification results their update in the client's cache (i.e. b, c 
 objects for class B);

 clients subscribes on changes in class C: object c 
 modification results it's update in the client's cache (i.e. c object 
 for class C).

Example of base classes update (implemented in previous release)

 clients subscribes on changes in class B: objects b, c 
 modification results their updates in the client's cache of the base class 
 (i.e. b, c objects for class A);

 clients subscribes on changes in class C: object c 
 modification results it's update in the client's cache (i.e. c object 
 for class A; c object for class B).

Example of derived classes update (new, was missing in previous releases)

 clients subscribes on changes in class A: objects b, c 
 modification results their updates in the client's cache (i.e. b, 
 c objects for class B; c object for class C);

 clients subscribes on changes in class B: object c 
 modification results it's update in the client's cache (i.e. c object 
 for class C).

Thus, subscription on:

 class A guaranties correct updates of a, b, c 
 objects in client's cache (a, b, c in class A;
 b, c in class B; c in class C);

 class B guaranties correct updates of b, c objects 
 in client's cache (b, c in class A; b, c 
 in class B; c in class C);

 class C guaranties correct updates of c objects in 
 client's cache (c in class A; c in class B; c 
 in class C).

Add Configuration unread_objects() Method

Add method Configuration::unread_objects() to unread unread objects of 
template classes in the client's configuration cache. This is required after 
reading parameters for substitution, since cache contains objects with 
non-substituted attributes.

Changes in the tdaq-01-06-02 Release

Also note

config changes in the LST release.
```

### Snapshot `config__tdaq-01-08-00__20111106134758.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-08-00__20111106134758.html`*

```text
API Changes

The documentation for config and generated DAL package has been updated. Now it 
is generated by DoxyGen tool and available from the release installation, see

ConfigPackages page.C++ Changes

The utilization of attribute converters is moved on the level of config 
package from the dal packages. This reduces size of generated 
code, improves performance (only one conversion is performed per database object 
instead of multiple conversions for each generated DAL object instantiated from 
it) and allows to use converted values from the config layer without explicitly 
invoked converters (e.g. by test manager and RCD packages).

Add new method test_object() to the Configuration class. The 
method tests existence of object by class name and object ID, and returns true, 
if the object was found and false otherwise. This method duplicates 
functionality of similar get() method. The difference is the 
new method does not throw daq::config::NotFound exception if the object is not 
found, since the Python config interface has problems catching ERS exceptions.

Java Changes

Add new methods to get inheritance hierarchy:

 TreeMap<String, TreeSet<String>> superclasses() - get names of 
 superclasses for each database class

 TreeMap<String, TreeSet<String>> subclasses() - get names of subclasses 
 for database classes having them

New: Python Interfaces to Configuration and ConfigObject classes. These binding were 
made to be quite "pythonic", which means that their function calls were changed to cope with Python interafce.
```

### Snapshot `config__tdaq-01-08-03__20111106134804.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-08-03__20111106134804.html`*

```text
New Page 1

 Configuration::cast() should not init object; this avoids unexpected 
 exception, if the object is dangling [oksconfig] 

 ConfigObject: add support for 64-bits integers and OKS class reference 
 types:
 64 bits signed integer type: int64_t

 64 bits unsigned integer type: uint64_t

 class reference: std::string

 Split existing ERS macros on declaration and implementation parts: this 
 fixes implementation bugs linking C++ code with Java and Python
```

### Snapshot `config__tdaq-01-08-04__20111106134807.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-08-04__20111106134807.html`*

```text
New Page 1

C++ and Java Changes

API Changes
The referenced_by()
methods were changed. The code
using them need to be modified!

Now these methods allow to return objects referencing given object via
composite (old behavior) and weak (new) relationships.

Unfortunately there are some changes in API:

 the class_name argument was removed from config layer,
since
it was never used and can be efficiently replaced by config cast, if
really needed

 the check_composite_only argument was added to switch
between
composite relationships (efficient) and weak ones (use carefully, it is
non-scalable!)

The relationship name by default is set to "*" to allow return objects
referencing given one via any relationship. Set it to any explicit
name, if necessary. Leave check_composite_only parameter with default
value to keep old
behavior.

The exact methods declarations and descriptions of modified parameters
are:

1. Template method of Configuration
class:

*  \param
obj                  
object

   *  \param
objects              
returned value

   *  \param
relationship_name     name of the relationship, via
which the object is referenced

   *  \param
check_composite_only  only returned composite parent
objects

 template<class T, class V> void referenced_by(

  const T& obj,

  std::vector<const V*>& objects,

  const std::string& relationship_name = "*",

  bool check_composite_only = true,

  bool init = false,

  unsigned long rlevel = 0,

  const std::vector<std::string> * rclasses = 0) throw
(daq::config::Generic);

2. The method of ConfigObject
class:

*  \param
value                
returned objects

  *  \param
relationship_name     name of relationship (if "*",
then return objects referencing via ANY relationship)

  *  \param
check_composite_only  only returned composite parent
objects

void referenced_by(

 std::vector<ConfigObject>& value,

 const std::string& relationship_name = "*",

 bool check_composite_only = true,

 unsigned long rlevel = 0,

 const std::vector<std::string> * rclasses = 0 ) const
throw
(daq::config::Generic);

New C++ API to Get Schema Description
The new API to get database schema description is defined by the config/Schema.h
file. The complete list of classes defined by the schema can be
obtained using Configuration::superclasses() method. Once name of class
is known, it's properties can be queried using new Configuration method:

const daq::config::class_t& get_class_info(const std::string& class_name, bool direct_only = false) throw (daq::config::Generic, daq::config::NotFound)
The old get_class_info(const std::string& class_name, MetaDataType
type, bool ...)
method is supported in 1.8.4 and will be removed in longer term.
Bug fixes

 Fix wrong C++ code deleting an object pointed by set's iterator
(may
be a reason of rare crashes)

 Fix unload() C++ method bug, if it was called twice (uncleared
map
contains destroyed objects, which are destroyed second time; came from
LArg)

 Correct C++ DEBUG output in several cases (config template cast,
search of implementation objects in cache)

 Proper C++ reload of database in case of objects removing (fix
setup
crash)

Other Improvements:

 The C++ Configuration::superclasses() returns map of all classes
including those which have no base ones; for the moment this is the
only way to get list of all classes from config layer and this is
required for Partition Maker's dynamic Python bindings. See also Savannah request https://savannah.cern.ch/bugs/?30737

 Allow re-create removed C++ DAL objects (basically now user is
allowed to
reload database after any modifications [except of changes with include
files]).

 Put JNI implementation for Java oksconfig plug-in set methods
(before it was not possible to use Java config layer with oks plug-in
to modify database).

 Add method ConfigObject::contained_in() returning name of file
the object belongs to.
```

### Snapshot `config__tdaq-01-09-00__20111106134811.html`
*Local file: `output/extracts/pcatd12/config__tdaq-01-09-00__20111106134811.html`*

```text
Untitled 1

New ConfigActions Class

An action is called on database load/reload/unload operation or config
object modification.

As an example
it is used to implement DAL's Component::disabled() algorithm in a way
transparent to users (the disabled() algorithm holds static set, that
needs to be updated in case of database modification).

To add an action user has to:

 implement new class deriving from ConfigAction class (defined in the
config/ConfigAction.h for C++ and config/jsrc/config/ConfigAction.java
for Java)

 create new action object and register it using Configuration::add_config_action(ConfigAction * ac)
method in C++ or config.Configuration.add_config_action(config.ConfigAction
obj) in Java

Unread All Template Objects (C++)

Add method Configuration::unread_all_objects() to unread all template
objects.

As an example
it is used when attribute string converter reads many template objects
(partition, segments, resources, applications, sw repositories) while
builds conversion map. All such objects have to be unread after
conversion map has been built, since their attributes may have
variables also need to be converted.

Existing unread_objects() method was replaced by
_unread_objects(CacheBase*) to be effectively used by the new
unread_all_objects().

Thread Safe (C++)

As required by new RunControl accessing DAL objects simultaneously from
several threads, the config and generated code has been made
thread-safe.

Performance Improvements and API Changes (C++)

Improve performance of most DAL methods replacing STL set and map by
GNU hash_set and hash_map.

Above requires changes in code using Configuration superclasses() and subclasses() methods:

Old methods:

 const std::map<std::string, std::set<std::string>
>& superclasses() const throw ()

 const std::map<std::string, std::set<std::string>
>& subclasses() const 

New methods:

 const config::map<config::set>& superclasses()
const throw ()

 const config::map<config::set>& subclasses()
const

See config/map.h and config/set.h for more information about config::map and config::set classes.

Note, new methods return unordered data.
```

### Snapshot `config__tdaq-02-00-00__20111106134813.html`
*Local file: `output/extracts/pcatd12/config__tdaq-02-00-00__20111106134813.html`*

```text
Untitled 1

C++ API Changes

To support 64-bits platform the ConfiObject get() and set() methods use typedefs from
<stdint.h> instead of non-safe built-in C++ types. One has to
replace any occurrences of explicitly used in such methods signed and
unsigned char, short and long types as shown in the following table:

 OKS Type

 Old C++ Type

 New C++ Type

 |  s8 (8-bits signed integer)

 | unsigned char

 | uint8_t

 |  u8 (8-bits unsigned integer)

 | signed char

 | int8_t

 | s16 (16-bits signed integer)

 | unsigned short

 | uint16_t

 | u16 (16-bits unsigned integer)

 | signed
short

 | int16_t

 | s32 (32-bits signed integer)

 | unsigned
long

 | uint32_t

 | u32 (32-bits unsigned integer)

 | signed
long

 | int32_t

Java Changes

The methods of config.Configuration
class are synchronized for multi-thread safety.
```

### Snapshot `config__tdaq-03-00-00__20111106134818.html`
*Local file: `output/extracts/pcatd12/config__tdaq-03-00-00__20111106134818.html`*

```text
Untitled 1

API Changes

 Add method to unread all Java objects Configuration.unread_all_objects().

 Add log message to commit methods.

 Add method get_updated_dbs()
returning names of uncommitted database files.

 C++: remove obsolete enter_loop parameter from subscribe() and reset_subscription()
methods; remove check_notification() method.

 C++: add parameter to unread implementation objects by Configuration::unread_all_objects()
method.

 Add set_commit_credentials() method to pass them to OKS server.

Bug Fixes

Fix problem with parallel access to the config
actions.

Improvements

There is minor improvement allowing to get rid of one unnecessary
search operation when new template DAL object is created (see patch 4146).
```

## 3. Doxygen `ConfigPackages` pages (5 snapshots, 2011-2012)

`ConfigPackages` is the Doxygen "main page" of the Config package documentation; each snapshot corresponds to one TDAQ version, content extracted with navigation boilerplate intact. Versions: `nightly` (20110326220841), `tdaq-02-00-03` (20110327163333), `tdaq-03-00-01` (20110326094004), `tdaq-04-00-00` (20111027092808), `tdaq-04-00-01` (20110124154520).

### Snapshot `doxygen__ConfigPackages-nightly__20110326220841.html`
*Local file: `output/extracts/pcatd12/doxygen__ConfigPackages-nightly__20110326220841.html`*

```text
TDAQ release nightly: Config Packages

 Main Page

 Related Pages

 Modules

 Namespaces

 Data Structures

 Files

 Examples

Config Packages 

The goal of the config package is to provide user-friendly API to access data from the configuration database.

There are two layers of such API which can be seen by user:

abstract config layer working with arbitrary database schema and hiding details of DBMS implementation

data access library (DAL), that is generated for given database schema to map it on programming language data types

This page describes basics which a user should know to generate DAL from the database schema, to get data from database, to receive notification on their change, to create new data or to modify existing data using generated DAL.

1. Development of the configuration database schema 

2. Generation of the DAL 

2.1. Parameters of genconfig utility 

2.2. Integration with CMT 

3. DAL classes and methods 

3.1. Mapping Between OKS Attribute Types and Programming Languages Types 

4. Errors Handling 

5. How to get data 

5.1. Initialisation 

5.2. Read objects of class 

5.3. Reading Values of Attributes 

5.4. Reading Values of Relationships 

5.5. Cast Class Types 

5.6. Data Destruction 

6. How to create and to modify data 

6.1. Creation of new database file 

6.2. Database Includes 

6.3. Objects Manipulations 

6.4. Modification Values of Attributes 

6.5. Modification Values of Relationships 

7. Notification mechanism 

7.1. User Callback 

7.2. Subscription criteria 

7.3. Subscription 

8. Algorithms

Sections 1, 2 and 3 are needed for those, who develops own schema and wants to generate DAL. Section 4 explain basics of error handling to be known by any user of DAL. Section 5 explain how to get data using DAL. Section 6 explains how to create or to modify data using DAL. Section 7 explains how to receive notification in case of data changes. The possibility to plug-in user algorithms to the generated DAL is described in section 8.

1. Development of the configuration database schema

The user may to develop own schema in case he needs to describe own configuration data which can not be described by existing schemes. The development of the schema can be done using OKS Schema Editor. The user has the choice to extend the existing schemes or to develop his own schema from scratch. If user wants to extend existing schema, first he needs to run the editor with existing schemes (which he can not modify) and to create the schema he will be the owner of, e.g.:

oks_schema_editor dal/schema/core.schema.xml

The editor window with loaded schema will appear. Then the user can create his own schema and define his own classes. If user wants to create new schema from scratch, he just needs to run the editor without parameters and to create a new schema. For more information on the OKS schema editor, the OKS schema capabilities and exporting schema into different formats see OKS documentation [6]. After the user finish with his schema development, he needs to save the schema into xml file and add it to the sources of his package. Such schema file will be used for the database data access library generation described by next section.

2. Generation of the DAL

A DAL is generated by the genconfig utility. It uses OKS schema files as input and produces: 

C++ source files to build the library 

C++ header files to describe library interface 

C++ files to build binaries dumping content of the database 

Java files to build jar file 

genconfig.info file containing information about names of generated classes, the C++ code namespace, include prefix directory and java package name

2.1. Parameters of genconfig utility

The command line parameters of genconfig utility are listed below: 

genconfig [-d | --C++-dir-name directory-name]
 [-n | --C++-namespace namespace
 [-i | --C++-headers-dir directory-prefix]
 [-j | --java-dir-name directory-name]
 [-p | --java-package-name package-name]
 [-I | --include-dirs dirs*]
 [-c | --classes class*]
 [-D | --user-defined-classes [namespace::]user-class[@dir-pefix]*]
 [-f | --info-file-name file-name]
 [-v | --verbose]
 [-h | --help]
 -s | --schema-files file.schema.xml+

Options/Arguments:
 -d directory-name name of firectory for C++ header and implementation files
 -n namespace namespace for C++ classes
 -i directory-prefix name of directory prefix for C++ header files
 -j directory-name name of directory for java files
 -p package-name package name for java files
 -I dirs* directories where to search for already generated files
 -c class* explicit list of classes to be generated
 -D [x::]c[@d]* user-defined classes
 -f filename name of output file describing generated files
 -v switch on verbose output
 -h this message
 -s files+ the schema files (at least one is mandatory)

To generate a DAL user has to provide name of the schema file. By default the DAL is generated for all classes contained in the schema files, otherwise user should provide names of required classes via --classes parameter. It is recommended to use unique namespace for each generated DAL to avoid possible problems when several DALs are used by one application.

It is possible to reuse already generated DALs. In this case the user should to provide a list of directories containing information about already generated DALs via --include-dirs parameter, to provide list of his schema files and optionally to provide list of names of classes to be generated. It is expected such schema files use include statement for base schema files. The DAL is generated only for classes contained in the explicitly mentioned schema files, the classes from included files are ignored.

2.2. Integration with CMT

The genconfig package provides CMT fragment. To generate all classes from given schema file a user should write in his requirement file: 

use genconfig
document generate-config my-dal -s=.. \
 namespace="my-ns" \
 include="my-include" \
 packagename="my-java-package" \
 some-path/my.schema.xml

This will produce C++ files for user schema file, which will be placed in several directories (relative to the root of user package) in accordance with their types: 

C++ library source files are placed into "$(bin)my-dal.tmp" directory, 

C++ header files are placed into "$(bin)$(include-dir-name)" directory, 

the C++ source files for dump binaries are placed into "$(bin)my-dal.tmp/dump" directory, 

the java files are placed into "$(bin)my-dal.tmp/$(java-package-name)" directory.

For our example to build C++ library put into cmt/requirements file: 

library mydal $(lib_opts) $(bin)my-dal.tmp/*.cpp

To build java jar file put into cmt/requirements file: 

apply_pattern build_jar name=my-dal src_dir="$(bin)my-dal.tmp/my-java-package" sources=*.java

Finally, to build dump binaries from C++ generated files put into cmt/requirements file: 

use config
application my_dump -no_prototypes "$(bin)my-dal.tmp/dump/dump_my_ns.cpp"
macro my_dump_okslinkopts "-lmy-dal -lconfig"

Note, the order of generation of files, library and binary builds is important: 

put into your cmt/requirements file dependecy of application from generated library macro my_dump_dependencies my-dal

to allow parallel build using gmake -jN option modify your cmt/Makefile: include $(CMTROOT)/src/Makefile.header
$(bin)my-dal.make $(bin)my_dump.make:: $(bin)generate-dal.stamp
include $(CMTROOT)/src/constituents.make

To be used by other packages the library, the jar file and generated header files have to be installed. There is no need to install or even to add to the user package' sources generated C++ and Java files. The C++ and Java DAL to be installed as a normal library and jar file. To install C++ header files in platform-independent directory put into requirement file: 

ignore_pattern install_headers_bin_auto
apply_pattern install_headers src_dir="$(bin)my-dal" files=*.h

If it is necessary to produce the DAL for a subset of classes defined by the schema files, the user have to define macro generate-config-classes containing space-separated list of classes: 

macro generate-config-classes "MyClass1 MyClass2 MyClass3"

If the DAL uses other existing DALs, the user have to define macro generate-config-include-dirs containing space-separated list of directories with installed headers of such DALs, e.g.: 

macro generate-config-include-dirs "${HOME1}/share/data/dal1 \
 ${HOME2}/share/data/dal2"

It is possible to change default locations for generated C++ and Java files using generate-config document options: 

cppdir option changes default directory for generated C++ files (i.e. "my-dal.tmp" for above example); the result files will be in the "$(bin)$(cppdir)" 

javadir option changes default directory for generated Java files (i.e. "my-dal.tmp/my-java-package" for above example); the result files will be in the "$(bin)$(javadir)/$(package)"; if containes dots (e.g. package="daq.core"), they will be substituted by slashes (i.e. Java files will be genereted in /daq/core directory).

It is possible to use nested namespace for generated C++ classes. To separate namespaces use double colon signs in the namespace option of the generate-config document, e.g.: 

document generate-config my-dal -s=.. namespace="daq::core" ...

 will produce classes in nested namespaces daq and core, i.e.: 

namespace daq {
 namespace core {
 ...
 }
}

3. DAL classes and methods

For each OKS class appropriate DAL classes are generated: 

in case of C++ the generated class has the same name as OKS one and is declared inside namespace defined by the user; there is separate header file per each class; it has the same name as the database class and, to be included, it may have directory prefix, defined by user; if a class is derived from other classes, an appropriate C++ inheritance is used; 

in case of Java there is interface which has the same name as the database class declared inside package with name provided by the user; the interface implementation is in the class with suffix _Impl; the static methods to get existent or to create new objects of the class are in the class with suffix _Helper; an appropriate inheritance is used between interfaces.

For each direct attribute and relationship defined for OKS class the appropriate methods are generated. Such methods have the same names as the names of the attributes and the relationships in the database with get_ and set_ prefixes. The database attribute types are mapped to appropriate C++ and Java types. The multi-value attributes are mapped to std::vector of attribute type in C++ and to array of attribute type in Java. The database relationships are mapped to methods returning pointer or std::vector of pointers to objects of referenced class in C++ and similarly an object or array of objects in Java.

Additionally, for each class there are methods to get object's class name and object identity as they are defined in the database.

For C++ two std::ostream operators are generated for each class: 

the one with const reference to object prints out the full description of the object, and 

the other one with const pointer to object prints out the object's class name and identity.

In Java for each class there is generated method print() which prints out full description of the object.

When DAL is generated, any non-alphanumeric characters appeared in the names of classes, attributes, relationships and methods are replaced by underscore symbol, e.g. database attribute "# of c++ lines" will appear in DAL as "__of_c___lines".

3.1. Mapping Between OKS Attribute Types and Programming Languages Types

Below there is map between OKS attribute types and C++/Java types: 

 | OKS Type | C++ type | Java type 

 | bool | bool | boolean 

 | s8 (8-bits signed integer) | int8_t | char 

 | u8 (8-bits unsigned integer) | uint8_t | byte 

 | s16 (16-bits signed integer) | int16_t | short 

 | u16 (16-bits unsigned integer) | uint16_t | short 

 | s32 (32-bits signed integer) | int32_t | int 

 | u32 (32-bits unsigned integer) | uint32_t | int

 | s64 (64-bits signed integer) | int64_t | long 

 | u64 (64-bits unsigned integer) | uint64_t | long 

 | float | float | float 

 | double | double | double 

 | date | std::string | java.lang.String 

 | time | std::string | java.lang.String 

 | string | std::string | java.lang.String 

 | enum | std::string | java.lang.String 

 | class | std::string | java.lang.String 

In C++ the complex values (strings and vectors) are passed by const reference and not by value.s

4. Errors Handling

Methods of C++ and Java config classes throw exceptions in case of errors.

Each C++ method has explicit exception specification. The following exceptions can be thrown:

daq::config::Generic is used to report most of the problems (bad DB, wrong parameter, plug-in specific, etc.)

daq::config::NotFound the config object accessed by ID is not found, class accessed by name is not found

daq::config::DeletedObject accessing template object that has been deleted (via notification or by the user's code)

All above exceptions have common class daq::config::Exception, that can be used to catch all of them. 

try {
 // load database using oks file /tmp/mydb.data.xml
 Configuration db("oksconfig:/tmp/mydb.data.xml");

 ... // user's code working with db
}
catch (daq::config::Exception & ex) {
 // throw some user-defined exception in case of config exception
 throw ers::error(user::exception(ERS_HERE, "cannot read config", ex));
}

5. How to get data

The entry point to get data from database is the class Configuration defined in global namespace in C++ and in the config package in Java. Below it is described how to create an object of this class and how to use it to get the database information.

5.1. Initialisation

The Configuration constructors in both Java and C++ languages have single string parameter. If the parameter is an empty string, the constructor will use value of the TDAQ_DB environment variable. In case if both the constructor parameter and the environment variable are not set, or empty, then the configuration construcor throws daq::config::Generic in case of C++, or config.SystemException is thrown in case of Java.

The format of the parameter is "name-of-plugin:plugin-parameters". The plug-in's parameter is optional. If it is non-empty, it is passed to the implementation plug-in constructor.

In C++ the name of plug-in is converted into name of the shared library by adding prefix lib and suffix .so, e.g. "oksconfig" plug-in name is converted into "liboksconfig.so". The shared library must be in the path to shared libraries, e.g. in the LD_LIBRARY_PATH environment variable.

In Java the name of plug-in is converted into name of the class in package "plugin-name" with name created from "plugin-name", where 1-st and 4-th characters are converted to upper case and "uration" string is appended (it is so by historical reasons), e.g. "oksconfig" plug-in name is converted into "oksconfig.OksConfiguration". The CLASSPATH variable has to point to such class or jar file. For the moment two implementation plug-ins are available: 

the oksconfig using OKS implementation directly (i.e. reads XML files), and 

the rdbconfig accessing OKS with RDB server.

Details of initialization in C++ and examples

Below there are examples of the Configuration constructor explicit parameters: 

#include "config/Configuration.h"

try {
 // example (1): load daq/partitions/be_test.data.xml file using oks
 ::Configuration db1("oksconfig:daq/partitions/be_test.data.xml");

 // example (2): connect with server RDB using rdb implementation (in initial partition)
 ::Configuration db2("rdbconfig:RDB");

 // example (2a): connect with server RDB using rdb implementation (in test partition)
 ::Configuration db2a("rdbconfig:test::RDB");

 // example (2b): same as above using new style server-name@partition-name
 ::Configuration db2b("rdbconfig:RDB@test");

 // example (3): use oks implementation and create new database
 ::Configuration db3("oksconfig");
 db3.create("", "/tmp/my.data.xml", std::list<std::string>(1,"/tmp/my.sch.xml"));

 // example (4): use rdb implementation and create new database
 // on server RDB running in partition test
 ::Configuration db4("rdbconfig");
 db4.create("test::RDB", "/tmp/my.data.xml", std::list<std::string>());
}
catch(daq::config::Exception& ex) {
 std::cerr << "ERROR: " << ex << std::endl;
}

The recommended way is to get plug-in and it's parameter via environment variable. Most of the user's code for applications run by TDAQ's setup should to leave the parameter empty: 

#include "config/Configuration.h"

int main() {
 try {
 ::Configuration db("");
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

In case it the parameter can be also passed via command line, use it as shown below: 

#include "config/Configuration.h"

int main(int argc, char *argv[]) {
 try {
 ::Configuration db(argv[1]);
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

Note, to get proper plug-in name and parameter used for configuration initialization (e.g. obtained via TDAQ_DB), use get_impl_spec() method of Configuration class, which is used in above examples for debug reporting.

Initialization in Java

The Configuration constructor parameters are the same, as in case of C++. In case of problems the exception is thrown. An example is shown below: 

import config.Configuration;

try {
 config.Configuration db = new config.Configuration("rdbconfig:RDB");
}
catch (config.SystemException ex) {
 System.err.println( "ERROR caught \'config.SystemException\':");
 System.err.println( "*** " + ex.getMessage() + " ***" );
}

Note in case when rdb implementation is used, the partition name of the RDB server can be specified by several ways: 

using the same approach as for C++, i.e. via constructor parameter using double colon-separated partition and server names, e.g. "rdbconfig:partition-name::server-server" or "rdbconfig:server-server@partition-name"; 

via tdaq.ipc.partition.name java virtual machine property, e.g. run java application with "-Dtdaq.ipc.partition.name=partition-name".

5.2. Read objects of class

Once an object of the Configuration class is successfully created, it can be used to get configuration data (i.e. objects). Normally to get configuration objects only C++ template methods of the Configuration class and generated Java code should be used. The usage of config layer (i.e. direct usage of objects of ConfigObject class) only makes sense in few packages working with arbitrary database schemes.

For each generated class T two methods can be applied using configuration object: 

C++ template methods of the Configuration class: 

 const T * Configuration::get(const std::string&, bool, bool, unsigned long, const std::vector<std::string> *) - to read named object; 

 void Configuration::get(std::vector<const T*>&, bool, bool, const std::string&, unsigned long rlevel, const std::vector<std::string> *) - to read objects of class; 

Java methods generated in class T_Helper: 

static public T get(config.Configuration db, String id) to read named object 

static public T[] gets(config.Configuration db, Query query) to read objects of class 

The methods looking for single object by identity and methods looking for objects of class in case if the query string is empty are searching objects in the class and all it's subclasses, e.g. if class B is derived from class A, then the second method used for class A returns all objects of class A and all objects of class B, and the first method used for class A is looking for object with given identity in class A and then in class B. The same methods used for class B are only looking for objects of class B.

If the query is non-empty, the methods filling vectors of objects only return objects satisfying the query criteria. A query can be an OKS query string. It can be created by the OKS Data Editor or written by hand as described by the OKS documentation , e.g.: 

 (all ("Name" "my-object" =)) - search all objects of class T and it's subclasses which name is equal to "my-object"; 

 (this (and ("Address" 128 >=) ("Address" 256 <))) - search all objects of class T which address is equal or greater than 128 and less than 256; 

 (this ("Modules" all ("State" 0 =))) - search all objects of class T which has objects referenced via relationship "Modules" with attribute "State" set to 0.

C++ Example (using online dal package)

To read all applications via C++ dal provided by the online software one can write: 

#include <config/ConfigObject.h>
#include <config/Configuration.h>
#include <dal/Application.h>

try {
 ::Configuration db("");
 // 'objects' vector contains Applications and all objects from derived classes,
 // e.g. RunControlApplications, etc.
 std::vector<const dal::Application *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

To get only run control applications it is possible to use the following code: 

#include <dal/RunControlApplication.h>
try {
 ::Configuration db("");
 std::vector<const dal::RunControlApplication *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Note, to get a named object it is necessary to use template parameter explicitly and to write: 

const dal::Application * a = db.get<dal::Application>("my-application");

instead of 

const dal::Application * a = db.get("my-application"); // COMPILATION ERROR!

When the methods parameter init_children is set to true, all objects referenced by the retrieved objects are also read and initialized (i.e. values of their attributes are read from database and all referenced objects are also recursively read). Otherwise the referenced objects can only be pre-allocated (if they were not already read explicitly) and the actual reading will happen, when the user will apply a method to read values of their attributes or relationships.

When the methods parameter init_object is set to false, all retrieved objects are only pre-allocated without reading their attributes and relationships. The values of attributes and relationships will actually be read from database implementation, when the user will apply a method to read an attribute or relationship value.

The above two parameters can be used by the user to improve performance. For example, if the parameter init_children is set to false, the only objects which are really used by the user process will be read from the database. However in this case the database can not be closed (e.g. to free used resources) until the configuration data are used. Also, the actual read from database can happen at an unexpected moment, that can introduce undesired delays.

Java Example (online DAL)

To read all applications via Java dal provided by the online software one can write: 

import config.Configuration;
import dal.Application;
import dal.Application_Helper;
...
config.Configuration db = new config.Configuration(...);
try {
 dal.Application objs[] = dal.Application_Helper.get(db, new config.Query());
} catch ( config.NotFoundException ex ) {
 System.err.println("ERROR: bad query or no such class loaded");
} catch ( config.SystemException ex ) {
 System.err.println("ERROR: caught system exception");
}

To get only run control applications it is possible to write (try/catch statements are skipped): 

import dal.RunControlApplication;
import dal.RunControlApplication_Helper;
...
dal.RunControlApplication objs[] = dal.RunControlApplication_Helper.get(db, new config.Query());

Below there is an example of code to get an application by ID. Note, if object with such ID does not exist, config.NotFoundException exception is thrown. 

try {
 dal.Application obj = dal.Application_Helper.get(db, "RootController");
}
catch (config.NotFoundException e) {
 System.err.println( "ERROR: can not find application \'RootController\'" );
}

5.3. Reading Values of Attributes

Once the objects are retrieved, the user can get values of their attributes. A method to read attribute value is created for each attribute of each generated class. It has the following format: 

for C++: 

 type get_AttributeName() const - for single-value integer and float numbers; 

 const std::string& get_AttributeName() const - for single-value string-based attributes; 

 const std::vector<type>& get_AttributeName() const - for multi-value attributes; 

for Java: 

 type get_AttributeName() const - for single-value attributes; 

 type[] get_AttributeName() const - for multi-value attributes. 

Attribute Converters

The user can use one or several ways to convert values of all attributes of a C++ or Java type. To do this he/she needs to implement or to use already existing converter class, to create converter object of that class and to pass such object to the Configuration object using method Configuration::register_converter().

In case of C++ such class has to inherit from the template Configuration::AttributeConverter < T > class, where template parameter T defines type of attributes which values need to be converted and to implement virtual method Configuration::AttributeConverter::convert(), that performs the real conversion of attribute values.

Note:The C++ converter object is destroyed by the configuration destructor. User must not call delete on the attribute converter object.
In case of Java a converter class has to implement config.AttributeConverter interface defining two methods: the method convert() as in C++ and the method get_class(), which returns class of converted attributes.

Below there is C++ example of user functions converting string and integer attributes: 

#include <config/Configuration.h>

 // converter to replace by '_' a non-alpha-numeric symbol in db strings
class GoodString : public ::Configuration::AttributeConverter<std::string> {
public:
 static char cvt_symbol(char c) { return (isalnum(c) ? c : '_'); }
 void convert(std::string& s, const Configuration&, const ConfigObject&, const std::string&) {
 std::transform(s.begin(), s.end(), s.begin(), cvt_symbol);
 }
}
 // converter to make any long integer value positive
class PositiveInt : public ::Configuration::AttributeConverter<unsigned long> {
 void convert(unsigned long& i, const Configuration&, const ConfigObject&, const std::string&) {
 if(i < 0) i = -i;
 }
}
...
try {
 ::Configuration db("");
 db.register_converter(new GoodString());
 db.register_converter(new PositiveInt());
 ...
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In the Java an example of Java code is shown below: 

import config.Configuration;
import config.AttributeConverter;

 // converter removes leading and trailing whitespace from a string
public class TrimString implements config.AttributeConverter {
 public Object convert(Object s, config.Configuration db, config.ConfigObject obj, String attr_name) { return (Object)(s.trim()); }
 public Class get_class() { return String.class; }
}
...
config.Configuration db = new config.Configuration("");
db.register_converter(new TrimString());

Online DAL Converters

The core TDAQ C++ DAL (libdaq-core-dal.so) provides converter daq::core::SubstituteVariables class to substitute configuration parameters in values of string attributes. It's constructor requires Configuration object and Partition object, since they are used to calculate conversion map. In case, if configuration database is reloaded, such parameters have to be reset using reset() method. An example of the C++ code is shown below: 

#include <config/Configuration.h>
#include "dal/Partition.h"
#include <dal/util.h>

try {
 ::Configuration db("");
 if(const daq::core::Partition * p = daq::core::get_partition(db, "partition-X")) {
 db.register_converter(new daq::core::SubstituteVariables(db, *p));
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Similar Java dal.jar provides attribute converter in the same way. An example of it's usage is shown below: 

import config.Configuration;
import config.DalObject;
import dal.SubstituteVariables;
import dal.Partition;

config.Configuration db = new config.Configuration("");
dal.Partition p = dal.Algorithms.get_partition(db, "partition-X");
if(p != null) {
 db.register_converter(new dal.SubstituteVariables(db, p));
}

5.4. Reading Values of Relationships

Once an object is retrieved, the user can get objects referenced by it. A method is created for each relationship of each generated class. It has the following format: 

for C++: 

 const class-type * get_RelationshipName() const - for single-value relationships; 

 const std::vector<const class-type*>& get_RelationshipName() const - for multi-value relationships; 

for Java: 

 class-type get_RelationshipName() const - for single-value relationships; 

 class-type[] get_RelationshipName() const - for multi-value relationships. 

5.5. Cast Class Types

There are situations when user may need to cast an object from one class to a derived one. To make a down cast for an object of generated class the user should to use the methods of the configuration classes and never use cast supported by the programming languages.

C++ cast

There are situations when some set of objects can belong to different classes, e.g. objects can be of class A or B which is derived from class A. For a down cast the Configuration::cast() method must be used. As an example, the code to try and to cast from application to run-control application type is shown below: 

try {
 ::Configuration db;
 // some code to get the vector of applications
 const std::vector<const dal::Application*>& l = ...;
 std::vector<const dal::Application*>::const_iterator j = l.begin();
 for(; j != l.end(); ++j) {
 if(const dal::RunControlApplication * r = db.cast<dal::RunControlApplication>(*j)) {
 std::cout << "application " << r << " is run control application" << std::endl; 
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Java cast

To down cast an object of generated Java DAL use aproapriate cast() method in generated class. For example, some object of application class can be down casted to the run control application: 

config.Configuration db(...);
dal.Application a = ...; // some code to get application
dal.RunControlApplication rc_application = dal.RunControlApplication_Helper.cast(db, a);
if(rc_application != null) { ... }

5.6. Data Destruction

In C++ the object of the Configuration class should not be destroyed while the DAL is in use. All objects read via template methods are destroyed by the Configuration class destructor. The user must never try to modify or to destroy such objects himself.

6. How to create and to modify data

This section explains how to create a new database file, how to create or remove database data and how to modify existing data.

Any modifications described by this section becomes persistent and visible to others processes only after successful commit operation. If the modification should not be committed (e.g. a modification failed), it is necessary to execute abort operation, e.g. in C++: 

try {
 ::Configuration db();
 bool success = true;
 ... // some code which makes changes and sets the variable to false if failed
 if(success) {
 std::cout << "commit changes\n";
 db.commit(); // one also check return status, true means success
 }
 else {
 std::cerr << "ERROR: something was wrong, abort changes\n";
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Below there is the same example for Java: 

config.Configuration db = new config.Configuration(...);
... // some code to makes changes and sets the success variable to false if failed
if(success) {
 System.out.println("commit changes");
 db.commit();
}
else {
 System.err.println("ERROR: something was wrong, abort changes");
 db.abort();
}

To modify or to destroy an object using generated C++ DAL methods described below, it is necessary to have a non-const pointer or reference on the object. However all generated DAL methods return objects as const. To make a change it is necessary to use C++ const_cast to get non-const pointer or reference.

6.1. Creation of new database file

To create a new database file using C++ it is necessary to build an object of the Configuration class only providing name of implementation plug-in: 

::Configuration db("oksconfig");

Similar code for Java is below: 

config.Configuration db = new config.Configuration("rdbconfig"); // no db file

To create a new database data file it is necessary to decide which schema (at least one schema is always required) and optionally others database files will be used. Then it is necessary to provide an absolute name for newly created database file (the user should have write permission or the rdb server must be run in read-write mode under account which has such rights). If rdb implementation is used, it is also necessary to provide server and optionally partition name. After this it is necessary to use create method of the Configuration class and check it's return status.

Below there is example for C++ and oks implementation: 

try {
 ::Configuration db("oksconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 if(db.create("", db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For rdb implementation it is similar, but requires rdb server and optionally partition's names: 

try {
 ::Configuration db("rdbconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 const char * server_name = "foo::bar"; // server with name bar running in part. foo
 if(db.create(server_name, db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << " on " << server_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java an example with rdb implementation is shown below: 

try {
 config.Configuration db = new config.Configuration("rdbconfig");
 String[] includes = new String[2];
 includes[0] = "online/schema/online.schema.xml"; // common schema
 includes[1] = "online/segments/setup.data.xml"; // online infrastructure
 db.create("foo::bar", "/tmp/my-partition.data.xml", includes);
 db.commit();
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
}
catch(config.NotAllowedException ex) {
 System.err.println("ERROR: caught \'config.NotAllowed\' exception");
}
... // catch config.AlreadyExistsException in a similar way

The included files should exist in advance and be defined either as an absolute path or as a relative path to a token of the TDAQ_DB_PATH variable value.

6.2. Database Includes

There are methods in C++ class Configuration to add a new include, to remove an existing include or to get list of includes for given database. They are: 

 bool Configuration::add_include(const std::string& db_name, const std::string& include) - adds include to the database db_name and returns true in case of success or false if failed; 

 bool Configuration::remove_include(const std::string& db_name, const std::string& include) - removes an existing include from the database db_name and returns true in case of success or false if failed; 

 bool Configuration::get_includes(const std::string& db_name, std::list<std::string>& includes) const - fills list of includes by files which are included by the db_name and returns true in case of success or false if failed.

Similar methods in Java class config.Configuration are: 

 void add_include(String db_name, String include) - adds include to the database db_name or throws exception if failed; 

 void remove_include(String db_name, String include) - removes an existing include from the database db_name or throws exception if failed; 

 void get_includes(String db_name, String[] includes) - fills array of includes by files which are included by the db_name or throws exception if failed.

6.3. Objects Manipulations

This subsection explains how to create and how to destroy database objects.

Objects Creation

To create a new object using generated C++ DAL there are two Configuration template methods: 

 const T * Configuration::create(const std::string& at, const std::string& id, bool) - to create new object of class T with identity id at existing database file with name at; 

 const T * Configuration::create(const ::DalObject& at, const std::string& id, bool) - to create new object of class T with identity id at a database file where object at is stored.

The methods return non-null pointer in case of success or null if failed. The second method is faster since time to search the database file where to put new object is much smaller.

When the init_object parameter is set to false, then the values of attributes and relationships are not read from implementation (for a newly created object they are set to default values in accordance with the database schema).

An example how to create two new objects of the online dal::Computer class is shown below: 

try {
 ::Configuration db(...);
 const char * dbfile = "/tmp/my-db.data.xml";
 const dal::Computer * host = db.create<dal::Computer>(dbfile, "host-1");
 if(host == 0) {
 std::cerr << "ERROR: failed to create object \'host-1\' at \'" << dbfile << "\'\n";
 }
 else {
 if(db.create<dal::Computer>(*host, "host-2") == 0) {
 std::cerr << "ERROR: failed to create object \'host-2\' at file of " << host;
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

On Java similar methods are genereted in the helper classes. For class T two methods are available: 

 T create(config.Configuration db, String at, String id) - to create new object of class T with identity id at existing database file with name at; 

 T create(config.Configuration db, config.DalObject at, String id) - to create new object of class T with identity id at a database file where object at is stored.

The example to create online segment and it's application is shown below:: 

config.Configuration db = new ...
String db_file = "/tmp/my-db.data.xml";
try {
 dal.Segment s = dal.Segment_Helper.create(db, db_file, "my segment");
 dal.Application a = dal.Application_Helper.create(db, s, "my application");
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
} ... // also other exceptions to be caught

Objects Destruction

To destroy an existing object there is template method in the C++ Configuration class bool destroy(T& obj). It returns true in case of success and false if failed. See example: 

try {
 ::Configuration db(...);
 dal::Computer * host = ...; // some code to get pointer
 db.destroy(*host);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In Java the method void destroy(config.Configuration db) is generated in T.java, e.g.: 

config.Configuration db = new ...;
dal.Computer host = ...; // some code to get object
try {
 host.destroy(db);
}
catch(config.SystemException ex) {
 System.err.println("ERROR: failed to destroy " + host);
} ... // also other exceptions to be caught

6.4. Modification Values of Attributes

Once the objects are retrieved or created, the user can modify values of their attributes. A method to set attribute value is created for each attribute of each generated class. The mapping between C++/Java types and OKS types can be seen in the 3.1. Mapping Between OKS Attribute Types and Programming Languages Types section.

In C++ such method throws daq::config::Exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(const std::vector<type>& value) - for multi-value attribute.

In Java such method throws an exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(type[] value) - for multi-value attribute.

6.5. Modification Values of Relationships

Once the objects are retrieved or created, the user can modify values of their relationships. A method to set relationship value is created for each relationship of each generated class.

For C++ it has the following format and throws daq::config::Exception if failed: 

 void set_RelationshipName(const class-type * value) - for single-value relationships; 

 void set_RelationshipName(const std::vector<const class-type*>& value) - for multi-value relationships.

For Java it has the following format and throws an exception if failed: 

 void set_RelationshipName(class-type value) - for single-value relationships; 

 void set_RelationshipName(class-type[] value) - for multi-value relationships.

7. Notification mechanism

The user application can be notified on changes of the configuration data. To do this user should to implement one or many callback functions (C++) or classes (Java) which will be used when the database changes are committed and to choose which changes in classes and objects should be reported (i.e. to define the subscription criteria ).

The user receives description of information changes in one go via callbacks invoked after commit of database changes. This is more preferred way than individual callback per object or per class since user may want to see all changes at single point. Each callback receives own list of changes in accordance with it's subscription criteria.

The changes are reported as a collection of changes per DAL class. A change per class contains 4 parameters: the class name and the identities of created, modified and removed objects.

To make a subscription it is necessary to make three steps: 

implement callback, 

define subscription criteria, 

invoke subscribe method with above entities on the configuration object.

7.1. User Callback

To start with any subscription on database changes the user must to implement at least one Configuration::notify callback function in C++ or config.Callback interface on Java. Below there are details for C++ and Java subscriptions.

C++ callback function

The user has to implement Configuration::notify callback. It has the following parameters: 

 const std::vector<::ConfigurationChange *> & changes - description of changes 

 void * parameter - user parameter

The ConfigurationChange class is declared in the config/Change.h file and has 4 methods to get name of the class and vectors of created, modified and removed object identities. An example of callback functions is shown below: 

void callback(const std::vector< ConfigurationChange *> & changes, void *)
{
 std::cout << "The CALLBACK reports all changes:\n";

 // iterate changes sorted by classes
 for(std::vector<ConfigurationChange *>::const_iterator j = changes.begin(); j != changes.end(); ++j) {

 // print class name
 std::cout << "- there are changes in class \"" << (*j)->get_class_name() << "\"\n";

 std::vector<std::string>::const_iterator i;

 // print modified objects
 for(i = (*j)->get_modified_objs().begin(); i != (*j)->get_modified_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was modified\n";
 }

 // print removed objects
 for(i = (*j)->get_removed_objs().begin(); i != (*j)->get_removed_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was removed\n";
 }

 // print created objects
 for(i = (*j)->get_created_objs().begin(); i != (*j)->get_created_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was created\n";
 }
 }
}

Java callback interface

The user has to create a class implementing the config.Callback interface. It requires to implement method void process_changes(config.Change[] changes, java.lang.Object parameter). Example below illustrates how to implement notification callback: 

class TestCallback implements config.Callback {
 private config.Configuration db;

 public TestCallback(config.Configuration d) { db = d; }

 public void process_changes(config.Change[] changes, java.lang.Object parameter) {

 // the parameter can be any; as an example, the callback ID is passed as string
 String cb_id = (String)parameter;

 // print out changes description
 System.out.println("[TestCallback " + cb_id + "] got changes:");
 config.Change.print(changes, " ");

 // iterate changes by classes
 for(int i = 0; i < changes.length; i++) {
 config.Change change = changes[i];
 System.out.println("* there are changes in the \'" + change.get_class_name() + "\' class");

 // just as example, look for changed objects of the Application class
 if((change.get_class_name().equals("Application") == true) && (change.get_changed_objects() != null)) {
 System.out.println("* " + change.get_changed_objects().length + " updated objects of the Application class");

 // iterate by all changed objects and print them out
 for(int j = 0; j < change.get_changed_objects().length; ++j) {
 dal.Application a = dal.Application_Helper.get(db, change.get_changed_objects()[j]);

 // an example of correct down cast
 if(a.class_name().equals("RunControlApplication")) {
 dal.RunControlApplication_Helper.get(db, a.config_object()).print(" "); // print as RC application
 }
 else {
 a.print(" "); // print as an application
 }
 }
 }
 }
 }
}

7.2. Subscription criteria

The subscription criteria is an object of ConfigurationSubscriptionCriteria class in C++ or config.Subscription class in Java. It is used to define lists of classes and objects, which changes will be monitored and reposted to user. If user provides no any class or object, it means subscription on any change and a database modification is reported.

Subscription on any changes in class

The notification callback is invoked for any changes of class objects including creation of new objects, removing or modification of existing objects.

In C++ to subscribe on any changes in some class the user should to use ConfigurationSubscriptionCriteria::add(const std::string&) method. For a class generated by genconfig the s_class_name attribute can be used, e.g. to subscribe on changes in class dal::Application: 

::ConfigurationSubscriptionCriteria c;
c.add(dal::Application::s_class_name);

In Java method config.Subscription.add(String class_name) should be used, e.g. to subscribe on changes in class Application it is necessary to write the following code: 

config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add("Application");

Subscription on object changes

When subscription on object changes has done, the notification callback is invoked for any changes of the objects or it's removing.

In C++ to subscribe on object changes notification the user should to use ConfigurationSubscriptionCriteria::add(const ::DalObject&), e.g. to subscribe on changes of an object of the Application class: 

::ConfigurationSubscriptionCriteria c;
const dal::Application * app_obj;
c->add(*app_obj);

In Java config.add(DalObject obj) method to be used, e.g.: 

dal.Application app = ...; // some code to get application object
config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add(app);

7.3. Subscription

To make the actual subscription it is necessary to have a notification callback been implemented and a subscription criteria object. The the method subscribe() to be invoked on the configuration object. For C++ an example is shown below: 

 // user-defined callback
void cb(const std::vector<ConfigurationChange *> & changes, void * p) { ... }

try {
 // configuration object
 ::Configuration db(...);

 // subscription criteria object
 ::ConfigurationSubscriptionCriteria c;
 c.add(dal::Application::s_class_name);

 // subscription; if database is changed, the cb can be invoked after this line
 ::CallbackId id = db.subscribe(c, cb);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java above example looks like: 

 // user-defined callback
class MyCallback implements config.Callback { ... }

 // configuration object
config.Configuration db = new config.Configuration(...);

 // subscription criteria object
config.Subscription c = new config.Subscription(new MyCallback(db), null);
c.add("Application");

 // subscription; MyCallback::process_changes() can be invoked after this line
db.subscribe(c);

The method unsubscribe() can be used to remove subscription set above. In case of C++ it's parameter is a return value of the subscribe() method (i.e. CallbackId value). For Java it's parameter is the subscription object used as parameter of subscribe() method.

8. Algorithms

By default, the generated classes have one-to-one mapping to database schema and DAL objects directly correspond to the database objects. If user wants to add more algorithms on top of the generated DAL without modification of DAL code by hand, he has possibility to define algorithms on top of the OKS class methods.

When a class method is created, user can add it's implementation for different programming languages. To be taken into account by genconfig, user have to provide C++ and/or Java implementation. Then he has two possibilities: 

declare method prototype, write method implementation in the separate file and add such file when build DAL; 

declare method prototype and write it's implementation in OKS.

The first way is more flexible, but requires more steps when build library. The second way does not require any additional steps when build library, but will require schema modifications to any method's implementation modification.

The online DAL defines several algorithms (e.g. to find partition, get all applications, to calculate application environment, etc.) and uses first way to implement algorithms. More information can be found in the online dal package. 

 All Data Structures Namespaces Files Functions Variables Typedefs Enumerations Enumerator Friends Defines

Generated on Thu Mar 3 2011 18:28:30 for TDAQ release nightly by 

 1.7.2
```

### Snapshot `doxygen__ConfigPackages-tdaq-02-00-03__20110327163333.html`
*Local file: `output/extracts/pcatd12/doxygen__ConfigPackages-tdaq-02-00-03__20110327163333.html`*

```text
TDAQ release tdaq-02-00-03: Config Packages

 Main Page

 Related Pages

 Modules

 Namespaces

 Data Structures

 Files

 Examples

Config Packages 

The goal of the config package is to provide user-friendly API to access data from the configuration database.

There are two layers of such API which can be seen by user:

abstract config layer working with arbitrary database schema and hiding details of DBMS implementation

data access library (DAL), that is generated for given database schema to map it on programming language data types

This page describes basics which a user should know to generate DAL from the database schema, to get data from database, to receive notification on their change, to create new data or to modify existing data using generated DAL.

1. Development of the configuration database schema 

2. Generation of the DAL 

2.1. Parameters of genconfig utility 

2.2. Integration with CMT 

3. DAL classes and methods 

3.1. Mapping Between OKS Attribute Types and Programming Languages Types 

4. Errors Handling 

5. How to get data 

5.1. Initialisation 

5.2. Read objects of class 

5.3. Reading Values of Attributes 

5.4. Reading Values of Relationships 

5.5. Cast Class Types 

5.6. Data Destruction 

6. How to create and to modify data 

6.1. Creation of new database file 

6.2. Database Includes 

6.3. Objects Manipulations 

6.4. Modification Values of Attributes 

6.5. Modification Values of Relationships 

7. Notification mechanism 

7.1. User Callback 

7.2. Subscription criteria 

7.3. Subscription 

8. Algorithms

Sections 1, 2 and 3 are needed for those, who develops own schema and wants to generate DAL. Section 4 explain basics of error handling to be known by any user of DAL. Section 5 explain how to get data using DAL. Section 6 explains how to create or to modify data using DAL. Section 7 explains how to receive notification in case of data changes. The possibility to plug-in user algorithms to the generated DAL is described in section 8.

1. Development of the configuration database schema

The user may to develop own schema in case he needs to describe own configuration data which can not be described by existing schemes. The development of the schema can be done using OKS Schema Editor. The user has the choice to extend the existing schemes or to develop his own schema from scratch. If user wants to extend existing schema, first he needs to run the editor with existing schemes (which he can not modify) and to create the schema he will be the owner of, e.g.:

oks_schema_editor dal/schema/core.schema.xml

The editor window with loaded schema will appear. Then the user can create his own schema and define his own classes. If user wants to create new schema from scratch, he just needs to run the editor without parameters and to create a new schema. For more information on the OKS schema editor, the OKS schema capabilities and exporting schema into different formats see OKS documentation [6]. After the user finish with his schema development, he needs to save the schema into xml file and add it to the sources of his package. Such schema file will be used for the database data access library generation described by next section.

2. Generation of the DAL

A DAL is generated by the genconfig utility. It uses OKS schema files as input and produces: 

C++ source files to build the library 

C++ header files to describe library interface 

C++ files to build binaries dumping content of the database 

Java files to build jar file 

genconfig.info file containing information about names of generated classes, the C++ code namespace, include prefix directory and java package name

2.1. Parameters of genconfig utility

The command line parameters of genconfig utility are listed below: 

genconfig [-d | --C++-dir-name directory-name]
 [-n | --C++-namespace namespace
 [-i | --C++-headers-dir directory-prefix]
 [-j | --java-dir-name directory-name]
 [-p | --java-package-name package-name]
 [-I | --include-dirs dirs*]
 [-c | --classes class*]
 [-D | --user-defined-classes [namespace::]user-class[@dir-pefix]*]
 [-f | --info-file-name file-name]
 [-v | --verbose]
 [-h | --help]
 -s | --schema-files file.schema.xml+

Options/Arguments:
 -d directory-name name of firectory for C++ header and implementation files
 -n namespace namespace for C++ classes
 -i directory-prefix name of directory prefix for C++ header files
 -j directory-name name of directory for java files
 -p package-name package name for java files
 -I dirs* directories where to search for already generated files
 -c class* explicit list of classes to be generated
 -D [x::]c[@d]* user-defined classes
 -f filename name of output file describing generated files
 -v switch on verbose output
 -h this message
 -s files+ the schema files (at least one is mandatory)

To generate a DAL user has to provide name of the schema file. By default the DAL is generated for all classes contained in the schema files, otherwise user should provide names of required classes via --classes parameter. It is recommended to use unique namespace for each generated DAL to avoid possible problems when several DALs are used by one application.

It is possible to reuse already generated DALs. In this case the user should to provide a list of directories containing information about already generated DALs via --include-dirs parameter, to provide list of his schema files and optionally to provide list of names of classes to be generated. It is expected such schema files use include statement for base schema files. The DAL is generated only for classes contained in the explicitly mentioned schema files, the classes from included files are ignored.

2.2. Integration with CMT

The genconfig package provides CMT fragment. To generate all classes from given schema file a user should write in his requirement file: 

use genconfig
document generate-config my-dal -s=.. \
 namespace="my-ns" \
 include="my-include" \
 packagename="my-java-package" \
 some-path/my.schema.xml

This will produce C++ files for user schema file, which will be placed in several directories (relative to the root of user package) in accordance with their types: 

C++ library source files are placed into "$(bin)my-dal.tmp" directory, 

C++ header files are placed into "$(bin)$(include-dir-name)" directory, 

the C++ source files for dump binaries are placed into "$(bin)my-dal.tmp/dump" directory, 

the java files are placed into "$(bin)my-dal.tmp/$(java-package-name)" directory.

For our example to build C++ library put into cmt/requirements file: 

library mydal $(lib_opts) $(bin)my-dal.tmp/*.cpp

To build java jar file put into cmt/requirements file: 

apply_pattern build_jar name=my-dal src_dir="$(bin)my-dal.tmp/my-java-package" sources=*.java

Finally, to build dump binaries from C++ generated files put into cmt/requirements file: 

use config
application my_dump -no_prototypes "$(bin)my-dal.tmp/dump/dump_my_ns.cpp"
macro my_dump_okslinkopts "-lmy-dal -lconfig"

Note, the order of generation of files, library and binary builds is important: 

put into your cmt/requirements file dependecy of application from generated library macro my_dump_dependencies my-dal

to allow parallel build using gmake -jN option modify your cmt/Makefile: include $(CMTROOT)/src/Makefile.header
$(bin)my-dal.make $(bin)my_dump.make:: $(bin)generate-dal.stamp
include $(CMTROOT)/src/constituents.make

To be used by other packages the library, the jar file and generated header files have to be installed. There is no need to install or even to add to the user package' sources generated C++ and Java files. The C++ and Java DAL to be installed as a normal library and jar file. To install C++ header files in platform-independent directory put into requirement file: 

ignore_pattern install_headers_bin_auto
apply_pattern install_headers src_dir="$(bin)my-dal" files=*.h

If it is necessary to produce the DAL for a subset of classes defined by the schema files, the user have to define macro generate-config-classes containing space-separated list of classes: 

macro generate-config-classes "MyClass1 MyClass2 MyClass3"

If the DAL uses other existing DALs, the user have to define macro generate-config-include-dirs containing space-separated list of directories with installed headers of such DALs, e.g.: 

macro generate-config-include-dirs "${HOME1}/share/data/dal1 \
 ${HOME2}/share/data/dal2"

It is possible to change default locations for generated C++ and Java files using generate-config document options: 

cppdir option changes default directory for generated C++ files (i.e. "my-dal.tmp" for above example); the result files will be in the "$(bin)$(cppdir)" 

javadir option changes default directory for generated Java files (i.e. "my-dal.tmp/my-java-package" for above example); the result files will be in the "$(bin)$(javadir)/$(package)"; if containes dots (e.g. package="daq.core"), they will be substituted by slashes (i.e. Java files will be genereted in /daq/core directory).

It is possible to use nested namespace for generated C++ classes. To separate namespaces use double colon signs in the namespace option of the generate-config document, e.g.: 

document generate-config my-dal -s=.. namespace="daq::core" ...

 will produce classes in nested namespaces daq and core, i.e.: 

namespace daq {
 namespace core {
 ...
 }
}

3. DAL classes and methods

For each OKS class appropriate DAL classes are generated: 

in case of C++ the generated class has the same name as OKS one and is declared inside namespace defined by the user; there is separate header file per each class; it has the same name as the database class and, to be included, it may have directory prefix, defined by user; if a class is derived from other classes, an appropriate C++ inheritance is used; 

in case of Java there is interface which has the same name as the database class declared inside package with name provided by the user; the interface implementation is in the class with suffix _Impl; the static methods to get existent or to create new objects of the class are in the class with suffix _Helper; an appropriate inheritance is used between interfaces.

For each direct attribute and relationship defined for OKS class the appropriate methods are generated. Such methods have the same names as the names of the attributes and the relationships in the database with get_ and set_ prefixes. The database attribute types are mapped to appropriate C++ and Java types. The multi-value attributes are mapped to std::vector of attribute type in C++ and to array of attribute type in Java. The database relationships are mapped to methods returning pointer or std::vector of pointers to objects of referenced class in C++ and similarly an object or array of objects in Java.

Additionally, for each class there are methods to get object's class name and object identity as they are defined in the database.

For C++ two std::ostream operators are generated for each class: 

the one with const reference to object prints out the full description of the object, and 

the other one with const pointer to object prints out the object's class name and identity.

In Java for each class there is generated method print() which prints out full description of the object.

When DAL is generated, any non-alphanumeric characters appeared in the names of classes, attributes, relationships and methods are replaced by underscore symbol, e.g. database attribute "# of c++ lines" will appear in DAL as "__of_c___lines".

3.1. Mapping Between OKS Attribute Types and Programming Languages Types

Below there is map between OKS attribute types and C++/Java types: 

 | OKS Type | C++ type | Java type 

 | bool | bool | boolean 

 | s8 (8-bits signed integer) | int8_t | char 

 | u8 (8-bits unsigned integer) | uint8_t | byte 

 | s16 (16-bits signed integer) | int16_t | short 

 | u16 (16-bits unsigned integer) | uint16_t | short 

 | s32 (32-bits signed integer) | int32_t | int 

 | u32 (32-bits unsigned integer) | uint32_t | int

 | s64 (64-bits signed integer) | int64_t | long 

 | u64 (64-bits unsigned integer) | uint64_t | long 

 | float | float | float 

 | double | double | double 

 | date | std::string | java.lang.String 

 | time | std::string | java.lang.String 

 | string | std::string | java.lang.String 

 | enum | std::string | java.lang.String 

 | class | std::string | java.lang.String 

In C++ the complex values (strings and vectors) are passed by const reference and not by value.s

4. Errors Handling

Methods of C++ and Java config classes throw exceptions in case of errors.

Each C++ method has explicit exception specification. The following exceptions can be thrown:

daq::config::Generic is used to report most of the problems (bad DB, wrong parameter, plug-in specific, etc.)

daq::config::NotFound the config object accessed by ID is not found, class accessed by name is not found

daq::config::DeletedObject accessing template object that has been deleted (via notification or by the user's code)

All above exceptions have common class daq::config::Exception, that can be used to catch all of them. 

try {
 // load database using oks file /tmp/mydb.data.xml
 Configuration db("oksconfig:/tmp/mydb.data.xml");

 ... // user's code working with db
}
catch (daq::config::Exception & ex) {
 // throw some user-defined exception in case of config exception
 throw ers::error(user::exception(ERS_HERE, "cannot read config", ex));
}

5. How to get data

The entry point to get data from database is the class Configuration defined in global namespace in C++ and in the config package in Java. Below it is described how to create an object of this class and how to use it to get the database information.

5.1. Initialisation

The Configuration constructors in both Java and C++ languages have single string parameter. If the parameter is an empty string, the constructor will use value of the TDAQ_DB environment variable. In case if both the constructor parameter and the environment variable are not set, or empty, then the configuration construcor throws daq::config::Generic in case of C++, or config.SystemException is thrown in case of Java.

The format of the parameter is "name-of-plugin:plugin-parameters". The plug-in's parameter is optional. If it is non-empty, it is passed to the implementation plug-in constructor.

In C++ the name of plug-in is converted into name of the shared library by adding prefix lib and suffix .so, e.g. "oksconfig" plug-in name is converted into "liboksconfig.so". The shared library must be in the path to shared libraries, e.g. in the LD_LIBRARY_PATH environment variable.

In Java the name of plug-in is converted into name of the class in package "plugin-name" with name created from "plugin-name", where 1-st and 4-th characters are converted to upper case and "uration" string is appended (it is so by historical reasons), e.g. "oksconfig" plug-in name is converted into "oksconfig.OksConfiguration". The CLASSPATH variable has to point to such class or jar file. For the moment two implementation plug-ins are available: 

the oksconfig using OKS implementation directly (i.e. reads XML files), and 

the rdbconfig accessing OKS with RDB server.

Details of initialization in C++ and examples

Below there are examples of the Configuration constructor explicit parameters: 

#include "config/Configuration.h"

try {
 // example (1): load daq/partitions/be_test.data.xml file using oks
 ::Configuration db1("oksconfig:daq/partitions/be_test.data.xml");

 // example (2): connect with server RDB using rdb implementation (in initial partition)
 ::Configuration db2("rdbconfig:RDB");

 // example (2a): connect with server RDB using rdb implementation (in test partition)
 ::Configuration db2a("rdbconfig:test::RDB");

 // example (2b): same as above using new style server-name@partition-name
 ::Configuration db2b("rdbconfig:RDB@test");

 // example (3): use oks implementation and create new database
 ::Configuration db3("oksconfig");
 db3.create("", "/tmp/my.data.xml", std::list<std::string>(1,"/tmp/my.sch.xml"));

 // example (4): use rdb implementation and create new database
 // on server RDB running in partition test
 ::Configuration db4("rdbconfig");
 db4.create("test::RDB", "/tmp/my.data.xml", std::list<std::string>());
}
catch(daq::config::Exception& ex) {
 std::cerr << "ERROR: " << ex << std::endl;
}

The recommended way is to get plug-in and it's parameter via environment variable. Most of the user's code for applications run by TDAQ's setup should to leave the parameter empty: 

#include "config/Configuration.h"

int main() {
 try {
 ::Configuration db("");
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

In case it the parameter can be also passed via command line, use it as shown below: 

#include "config/Configuration.h"

int main(int argc, char *argv[]) {
 try {
 ::Configuration db(argv[1]);
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

Note, to get proper plug-in name and parameter used for configuration initialization (e.g. obtained via TDAQ_DB), use get_impl_spec() method of Configuration class, which is used in above examples for debug reporting.

Initialization in Java

The Configuration constructor parameters are the same, as in case of C++. In case of problems the exception is thrown. An example is shown below: 

import config.Configuration;

try {
 config.Configuration db = new config.Configuration("rdbconfig:RDB");
}
catch (config.SystemException ex) {
 System.err.println( "ERROR caught \'config.SystemException\':");
 System.err.println( "*** " + ex.getMessage() + " ***" );
}

Note in case when rdb implementation is used, the partition name of the RDB server can be specified by several ways: 

using the same approach as for C++, i.e. via constructor parameter using double colon-separated partition and server names, e.g. "rdbconfig:partition-name::server-server" or "rdbconfig:server-server@partition-name"; 

via tdaq.ipc.partition.name java virtual machine property, e.g. run java application with "-Dtdaq.ipc.partition.name=partition-name".

5.2. Read objects of class

Once an object of the Configuration class is successfully created, it can be used to get configuration data (i.e. objects). Normally to get configuration objects only C++ template methods of the Configuration class and generated Java code should be used. The usage of config layer (i.e. direct usage of objects of ConfigObject class) only makes sense in few packages working with arbitrary database schemes.

For each generated class T two methods can be applied using configuration object: 

C++ template methods of the Configuration class: 

 const T * Configuration::get(const std::string&, bool, bool, unsigned long, const std::vector<std::string> *) - to read named object; 

 void Configuration::get(std::vector<const T*>&, bool, bool, const std::string&, unsigned long rlevel, const std::vector<std::string> *) - to read objects of class; 

Java methods generated in class T_Helper: 

static public T get(config.Configuration db, String id) to read named object 

static public T[] gets(config.Configuration db, Query query) to read objects of class 

The methods looking for single object by identity and methods looking for objects of class in case if the query string is empty are searching objects in the class and all it's subclasses, e.g. if class B is derived from class A, then the second method used for class A returns all objects of class A and all objects of class B, and the first method used for class A is looking for object with given identity in class A and then in class B. The same methods used for class B are only looking for objects of class B.

If the query is non-empty, the methods filling vectors of objects only return objects satisfying the query criteria. A query can be an OKS query string. It can be created by the OKS Data Editor or written by hand as described by the OKS documentation , e.g.: 

 (all ("Name" "my-object" =)) - search all objects of class T and it's subclasses which name is equal to "my-object"; 

 (this (and ("Address" 128 >=) ("Address" 256 <))) - search all objects of class T which address is equal or greater than 128 and less than 256; 

 (this ("Modules" all ("State" 0 =))) - search all objects of class T which has objects referenced via relationship "Modules" with attribute "State" set to 0.

C++ Example (using online dal package)

To read all applications via C++ dal provided by the online software one can write: 

#include <config/ConfigObject.h>
#include <config/Configuration.h>
#include <dal/Application.h>

try {
 ::Configuration db("");
 // 'objects' vector contains Applications and all objects from derived classes,
 // e.g. RunControlApplications, etc.
 std::vector<const dal::Application *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

To get only run control applications it is possible to use the following code: 

#include <dal/RunControlApplication.h>
try {
 ::Configuration db("");
 std::vector<const dal::RunControlApplication *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Note, to get a named object it is necessary to use template parameter explicitly and to write: 

const dal::Application * a = db.get<dal::Application>("my-application");

instead of 

const dal::Application * a = db.get("my-application"); // COMPILATION ERROR!

When the methods parameter init_children is set to true, all objects referenced by the retrieved objects are also read and initialized (i.e. values of their attributes are read from database and all referenced objects are also recursively read). Otherwise the referenced objects can only be pre-allocated (if they were not already read explicitly) and the actual reading will happen, when the user will apply a method to read values of their attributes or relationships.

When the methods parameter init_object is set to false, all retrieved objects are only pre-allocated without reading their attributes and relationships. The values of attributes and relationships will actually be read from database implementation, when the user will apply a method to read an attribute or relationship value.

The above two parameters can be used by the user to improve performance. For example, if the parameter init_children is set to false, the only objects which are really used by the user process will be read from the database. However in this case the database can not be closed (e.g. to free used resources) until the configuration data are used. Also, the actual read from database can happen at an unexpected moment, that can introduce undesired delays.

Java Example (online DAL)

To read all applications via Java dal provided by the online software one can write: 

import config.Configuration;
import dal.Application;
import dal.Application_Helper;
...
config.Configuration db = new config.Configuration(...);
try {
 dal.Application objs[] = dal.Application_Helper.get(db, new config.Query());
} catch ( config.NotFoundException ex ) {
 System.err.println("ERROR: bad query or no such class loaded");
} catch ( config.SystemException ex ) {
 System.err.println("ERROR: caught system exception");
}

To get only run control applications it is possible to write (try/catch statements are skipped): 

import dal.RunControlApplication;
import dal.RunControlApplication_Helper;
...
dal.RunControlApplication objs[] = dal.RunControlApplication_Helper.get(db, new config.Query());

Below there is an example of code to get an application by ID. Note, if object with such ID does not exist, config.NotFoundException exception is thrown. 

try {
 dal.Application obj = dal.Application_Helper.get(db, "RootController");
}
catch (config.NotFoundException e) {
 System.err.println( "ERROR: can not find application \'RootController\'" );
}

5.3. Reading Values of Attributes

Once the objects are retrieved, the user can get values of their attributes. A method to read attribute value is created for each attribute of each generated class. It has the following format: 

for C++: 

 type get_AttributeName() const - for single-value integer and float numbers; 

 const std::string& get_AttributeName() const - for single-value string-based attributes; 

 const std::vector<type>& get_AttributeName() const - for multi-value attributes; 

for Java: 

 type get_AttributeName() const - for single-value attributes; 

 type[] get_AttributeName() const - for multi-value attributes. 

Attribute Converters

The user can use one or several ways to convert values of all attributes of a C++ or Java type. To do this he/she needs to implement or to use already existing converter class, to create converter object of that class and to pass such object to the Configuration object using method Configuration::register_converter().

In case of C++ such class has to inherit from the template Configuration::AttributeConverter < T > class, where template parameter T defines type of attributes which values need to be converted and to implement virtual method Configuration::AttributeConverter::convert(), that performs the real conversion of attribute values.

Note:The C++ converter object is destroyed by the configuration destructor. User must not call delete on the attribute converter object.
In case of Java a converter class has to implement config.AttributeConverter interface defining two methods: the method convert() as in C++ and the method get_class(), which returns class of converted attributes.

Below there is C++ example of user functions converting string and integer attributes: 

#include <config/Configuration.h>

 // converter to replace by '_' a non-alpha-numeric symbol in db strings
class GoodString : public ::Configuration::AttributeConverter<std::string> {
public:
 static char cvt_symbol(char c) { return (isalnum(c) ? c : '_'); }
 void convert(std::string& s, const Configuration&, const ConfigObject&, const std::string&) {
 std::transform(s.begin(), s.end(), s.begin(), cvt_symbol);
 }
}
 // converter to make any long integer value positive
class PositiveInt : public ::Configuration::AttributeConverter<unsigned long> {
 void convert(unsigned long& i, const Configuration&, const ConfigObject&, const std::string&) {
 if(i < 0) i = -i;
 }
}
...
try {
 ::Configuration db("");
 db.register_converter(new GoodString());
 db.register_converter(new PositiveInt());
 ...
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In the Java an example of Java code is shown below: 

import config.Configuration;
import config.AttributeConverter;

 // converter removes leading and trailing whitespace from a string
public class TrimString implements config.AttributeConverter {
 public Object convert(Object s, config.Configuration db, config.ConfigObject obj, String attr_name) { return (Object)(s.trim()); }
 public Class get_class() { return String.class; }
}
...
config.Configuration db = new config.Configuration("");
db.register_converter(new TrimString());

Online DAL Converters

The core TDAQ C++ DAL (libdaq-core-dal.so) provides converter daq::core::SubstituteVariables class to substitute configuration parameters in values of string attributes. It's constructor requires Configuration object and Partition object, since they are used to calculate conversion map. In case, if configuration database is reloaded, such parameters have to be reset using reset() method. An example of the C++ code is shown below: 

#include <config/Configuration.h>
#include "dal/Partition.h"
#include <dal/util.h>

try {
 ::Configuration db("");
 if(const daq::core::Partition * p = daq::core::get_partition(db, "partition-X")) {
 db.register_converter(new daq::core::SubstituteVariables(db, *p));
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Similar Java dal.jar provides attribute converter in the same way. An example of it's usage is shown below: 

import config.Configuration;
import config.DalObject;
import dal.SubstituteVariables;
import dal.Partition;

config.Configuration db = new config.Configuration("");
dal.Partition p = dal.Algorithms.get_partition(db, "partition-X");
if(p != null) {
 db.register_converter(new dal.SubstituteVariables(db, p));
}

5.4. Reading Values of Relationships

Once an object is retrieved, the user can get objects referenced by it. A method is created for each relationship of each generated class. It has the following format: 

for C++: 

 const class-type * get_RelationshipName() const - for single-value relationships; 

 const std::vector<const class-type*>& get_RelationshipName() const - for multi-value relationships; 

for Java: 

 class-type get_RelationshipName() const - for single-value relationships; 

 class-type[] get_RelationshipName() const - for multi-value relationships. 

5.5. Cast Class Types

There are situations when user may need to cast an object from one class to a derived one. To make a down cast for an object of generated class the user should to use the methods of the configuration classes and never use cast supported by the programming languages.

C++ cast

There are situations when some set of objects can belong to different classes, e.g. objects can be of class A or B which is derived from class A. For a down cast the Configuration::cast() method must be used. As an example, the code to try and to cast from application to run-control application type is shown below: 

try {
 ::Configuration db;
 // some code to get the vector of applications
 const std::vector<const dal::Application*>& l = ...;
 std::vector<const dal::Application*>::const_iterator j = l.begin();
 for(; j != l.end(); ++j) {
 if(const dal::RunControlApplication * r = db.cast<dal::RunControlApplication>(*j)) {
 std::cout << "application " << r << " is run control application" << std::endl; 
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Java cast

To down cast an object of generated Java DAL use aproapriate cast() method in generated class. For example, some object of application class can be down casted to the run control application: 

config.Configuration db(...);
dal.Application a = ...; // some code to get application
dal.RunControlApplication rc_application = dal.RunControlApplication_Helper.cast(db, a);
if(rc_application != null) { ... }

5.6. Data Destruction

In C++ the object of the Configuration class should not be destroyed while the DAL is in use. All objects read via template methods are destroyed by the Configuration class destructor. The user must never try to modify or to destroy such objects himself.

6. How to create and to modify data

This section explains how to create a new database file, how to create or remove database data and how to modify existing data.

Any modifications described by this section becomes persistent and visible to others processes only after successful commit operation. If the modification should not be committed (e.g. a modification failed), it is necessary to execute abort operation, e.g. in C++: 

try {
 ::Configuration db();
 bool success = true;
 ... // some code which makes changes and sets the variable to false if failed
 if(success) {
 std::cout << "commit changes\n";
 db.commit(); // one also check return status, true means success
 }
 else {
 std::cerr << "ERROR: something was wrong, abort changes\n";
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Below there is the same example for Java: 

config.Configuration db = new config.Configuration(...);
... // some code to makes changes and sets the success variable to false if failed
if(success) {
 System.out.println("commit changes");
 db.commit();
}
else {
 System.err.println("ERROR: something was wrong, abort changes");
 db.abort();
}

To modify or to destroy an object using generated C++ DAL methods described below, it is necessary to have a non-const pointer or reference on the object. However all generated DAL methods return objects as const. To make a change it is necessary to use C++ const_cast to get non-const pointer or reference.

6.1. Creation of new database file

To create a new database file using C++ it is necessary to build an object of the Configuration class only providing name of implementation plug-in: 

::Configuration db("oksconfig");

Similar code for Java is below: 

config.Configuration db = new config.Configuration("rdbconfig"); // no db file

To create a new database data file it is necessary to decide which schema (at least one schema is always required) and optionally others database files will be used. Then it is necessary to provide an absolute name for newly created database file (the user should have write permission or the rdb server must be run in read-write mode under account which has such rights). If rdb implementation is used, it is also necessary to provide server and optionally partition name. After this it is necessary to use create method of the Configuration class and check it's return status.

Below there is example for C++ and oks implementation: 

try {
 ::Configuration db("oksconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 if(db.create("", db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For rdb implementation it is similar, but requires rdb server and optionally partition's names: 

try {
 ::Configuration db("rdbconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 const char * server_name = "foo::bar"; // server with name bar running in part. foo
 if(db.create(server_name, db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << " on " << server_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java an example with rdb implementation is shown below: 

try {
 config.Configuration db = new config.Configuration("rdbconfig");
 String[] includes = new String[2];
 includes[0] = "online/schema/online.schema.xml"; // common schema
 includes[1] = "online/segments/setup.data.xml"; // online infrastructure
 db.create("foo::bar", "/tmp/my-partition.data.xml", includes);
 db.commit();
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
}
catch(config.NotAllowedException ex) {
 System.err.println("ERROR: caught \'config.NotAllowed\' exception");
}
... // catch config.AlreadyExistsException in a similar way

The included files should exist in advance and be defined either as an absolute path or as a relative path to a token of the TDAQ_DB_PATH variable value.

6.2. Database Includes

There are methods in C++ class Configuration to add a new include, to remove an existing include or to get list of includes for given database. They are: 

 bool Configuration::add_include(const std::string& db_name, const std::string& include) - adds include to the database db_name and returns true in case of success or false if failed; 

 bool Configuration::remove_include(const std::string& db_name, const std::string& include) - removes an existing include from the database db_name and returns true in case of success or false if failed; 

 bool Configuration::get_includes(const std::string& db_name, std::list<std::string>& includes) const - fills list of includes by files which are included by the db_name and returns true in case of success or false if failed.

Similar methods in Java class config.Configuration are: 

 void add_include(String db_name, String include) - adds include to the database db_name or throws exception if failed; 

 void remove_include(String db_name, String include) - removes an existing include from the database db_name or throws exception if failed; 

 void get_includes(String db_name, String[] includes) - fills array of includes by files which are included by the db_name or throws exception if failed.

6.3. Objects Manipulations

This subsection explains how to create and how to destroy database objects.

Objects Creation

To create a new object using generated C++ DAL there are two Configuration template methods: 

 const T * Configuration::create(const std::string& at, const std::string& id, bool) - to create new object of class T with identity id at existing database file with name at; 

 const T * Configuration::create(const ::DalObject& at, const std::string& id, bool) - to create new object of class T with identity id at a database file where object at is stored.

The methods return non-null pointer in case of success or null if failed. The second method is faster since time to search the database file where to put new object is much smaller.

When the init_object parameter is set to false, then the values of attributes and relationships are not read from implementation (for a newly created object they are set to default values in accordance with the database schema).

An example how to create two new objects of the online dal::Computer class is shown below: 

try {
 ::Configuration db(...);
 const char * dbfile = "/tmp/my-db.data.xml";
 const dal::Computer * host = db.create<dal::Computer>(dbfile, "host-1");
 if(host == 0) {
 std::cerr << "ERROR: failed to create object \'host-1\' at \'" << dbfile << "\'\n";
 }
 else {
 if(db.create<dal::Computer>(*host, "host-2") == 0) {
 std::cerr << "ERROR: failed to create object \'host-2\' at file of " << host;
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

On Java similar methods are genereted in the helper classes. For class T two methods are available: 

 T create(config.Configuration db, String at, String id) - to create new object of class T with identity id at existing database file with name at; 

 T create(config.Configuration db, config.DalObject at, String id) - to create new object of class T with identity id at a database file where object at is stored.

The example to create online segment and it's application is shown below:: 

config.Configuration db = new ...
String db_file = "/tmp/my-db.data.xml";
try {
 dal.Segment s = dal.Segment_Helper.create(db, db_file, "my segment");
 dal.Application a = dal.Application_Helper.create(db, s, "my application");
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
} ... // also other exceptions to be caught

Objects Destruction

To destroy an existing object there is template method in the C++ Configuration class bool destroy(T& obj). It returns true in case of success and false if failed. See example: 

try {
 ::Configuration db(...);
 dal::Computer * host = ...; // some code to get pointer
 db.destroy(*host);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In Java the method void destroy(config.Configuration db) is generated in T.java, e.g.: 

config.Configuration db = new ...;
dal.Computer host = ...; // some code to get object
try {
 host.destroy(db);
}
catch(config.SystemException ex) {
 System.err.println("ERROR: failed to destroy " + host);
} ... // also other exceptions to be caught

6.4. Modification Values of Attributes

Once the objects are retrieved or created, the user can modify values of their attributes. A method to set attribute value is created for each attribute of each generated class. The mapping between C++/Java types and OKS types can be seen in the 3.1. Mapping Between OKS Attribute Types and Programming Languages Types section.

In C++ such method throws daq::config::Exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(const std::vector<type>& value) - for multi-value attribute.

In Java such method throws an exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(type[] value) - for multi-value attribute.

6.5. Modification Values of Relationships

Once the objects are retrieved or created, the user can modify values of their relationships. A method to set relationship value is created for each relationship of each generated class.

For C++ it has the following format and throws daq::config::Exception if failed: 

 void set_RelationshipName(const class-type * value) - for single-value relationships; 

 void set_RelationshipName(const std::vector<const class-type*>& value) - for multi-value relationships.

For Java it has the following format and throws an exception if failed: 

 void set_RelationshipName(class-type value) - for single-value relationships; 

 void set_RelationshipName(class-type[] value) - for multi-value relationships.

7. Notification mechanism

The user application can be notified on changes of the configuration data. To do this user should to implement one or many callback functions (C++) or classes (Java) which will be used when the database changes are committed and to choose which changes in classes and objects should be reported (i.e. to define the subscription criteria ).

The user receives description of information changes in one go via callbacks invoked after commit of database changes. This is more preferred way than individual callback per object or per class since user may want to see all changes at single point. Each callback receives own list of changes in accordance with it's subscription criteria.

The changes are reported as a collection of changes per DAL class. A change per class contains 4 parameters: the class name and the identities of created, modified and removed objects.

To make a subscription it is necessary to make three steps: 

implement callback, 

define subscription criteria, 

invoke subscribe method with above entities on the configuration object.

7.1. User Callback

To start with any subscription on database changes the user must to implement at least one Configuration::notify callback function in C++ or config.Callback interface on Java. Below there are details for C++ and Java subscriptions.

C++ callback function

The user has to implement Configuration::notify callback. It has the following parameters: 

 const std::vector<::ConfigurationChange *> & changes - description of changes 

 void * parameter - user parameter

The ConfigurationChange class is declared in the config/Change.h file and has 4 methods to get name of the class and vectors of created, modified and removed object identities. An example of callback functions is shown below: 

void callback(const std::vector< ConfigurationChange *> & changes, void *)
{
 std::cout << "The CALLBACK reports all changes:\n";

 // iterate changes sorted by classes
 for(std::vector<ConfigurationChange *>::const_iterator j = changes.begin(); j != changes.end(); ++j) {

 // print class name
 std::cout << "- there are changes in class \"" << (*j)->get_class_name() << "\"\n";

 std::vector<std::string>::const_iterator i;

 // print modified objects
 for(i = (*j)->get_modified_objs().begin(); i != (*j)->get_modified_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was modified\n";
 }

 // print removed objects
 for(i = (*j)->get_removed_objs().begin(); i != (*j)->get_removed_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was removed\n";
 }

 // print created objects
 for(i = (*j)->get_created_objs().begin(); i != (*j)->get_created_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was created\n";
 }
 }
}

Java callback interface

The user has to create a class implementing the config.Callback interface. It requires to implement method void process_changes(config.Change[] changes, java.lang.Object parameter). Example below illustrates how to implement notification callback: 

class TestCallback implements config.Callback {
 private config.Configuration db;

 public TestCallback(config.Configuration d) { db = d; }

 public void process_changes(config.Change[] changes, java.lang.Object parameter) {

 // the parameter can be any; as an example, the callback ID is passed as string
 String cb_id = (String)parameter;

 // print out changes description
 System.out.println("[TestCallback " + cb_id + "] got changes:");
 config.Change.print(changes, " ");

 // iterate changes by classes
 for(int i = 0; i < changes.length; i++) {
 config.Change change = changes[i];
 System.out.println("* there are changes in the \'" + change.get_class_name() + "\' class");

 // just as example, look for changed objects of the Application class
 if((change.get_class_name().equals("Application") == true) && (change.get_changed_objects() != null)) {
 System.out.println("* " + change.get_changed_objects().length + " updated objects of the Application class");

 // iterate by all changed objects and print them out
 for(int j = 0; j < change.get_changed_objects().length; ++j) {
 dal.Application a = dal.Application_Helper.get(db, change.get_changed_objects()[j]);

 // an example of correct down cast
 if(a.class_name().equals("RunControlApplication")) {
 dal.RunControlApplication_Helper.get(db, a.config_object()).print(" "); // print as RC application
 }
 else {
 a.print(" "); // print as an application
 }
 }
 }
 }
 }
}

7.2. Subscription criteria

The subscription criteria is an object of ConfigurationSubscriptionCriteria class in C++ or config.Subscription class in Java. It is used to define lists of classes and objects, which changes will be monitored and reposted to user. If user provides no any class or object, it means subscription on any change and a database modification is reported.

Subscription on any changes in class

The notification callback is invoked for any changes of class objects including creation of new objects, removing or modification of existing objects.

In C++ to subscribe on any changes in some class the user should to use ConfigurationSubscriptionCriteria::add(const std::string&) method. For a class generated by genconfig the s_class_name attribute can be used, e.g. to subscribe on changes in class dal::Application: 

::ConfigurationSubscriptionCriteria c;
c.add(dal::Application::s_class_name);

In Java method config.Subscription.add(String class_name) should be used, e.g. to subscribe on changes in class Application it is necessary to write the following code: 

config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add("Application");

Subscription on object changes

When subscription on object changes has done, the notification callback is invoked for any changes of the objects or it's removing.

In C++ to subscribe on object changes notification the user should to use ConfigurationSubscriptionCriteria::add(const ::DalObject&), e.g. to subscribe on changes of an object of the Application class: 

::ConfigurationSubscriptionCriteria c;
const dal::Application * app_obj;
c->add(*app_obj);

In Java config.add(DalObject obj) method to be used, e.g.: 

dal.Application app = ...; // some code to get application object
config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add(app);

7.3. Subscription

To make the actual subscription it is necessary to have a notification callback been implemented and a subscription criteria object. The the method subscribe() to be invoked on the configuration object. For C++ an example is shown below: 

 // user-defined callback
void cb(const std::vector<ConfigurationChange *> & changes, void * p) { ... }

try {
 // configuration object
 ::Configuration db(...);

 // subscription criteria object
 ::ConfigurationSubscriptionCriteria c;
 c.add(dal::Application::s_class_name);

 // subscription; if database is changed, the cb can be invoked after this line
 ::CallbackId id = db.subscribe(c, cb);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java above example looks like: 

 // user-defined callback
class MyCallback implements config.Callback { ... }

 // configuration object
config.Configuration db = new config.Configuration(...);

 // subscription criteria object
config.Subscription c = new config.Subscription(new MyCallback(db), null);
c.add("Application");

 // subscription; MyCallback::process_changes() can be invoked after this line
db.subscribe(c);

The method unsubscribe() can be used to remove subscription set above. In case of C++ it's parameter is a return value of the subscribe() method (i.e. CallbackId value). For Java it's parameter is the subscription object used as parameter of subscribe() method.

C++ specific

In C++ the method Configuration::subscribe() has optional boolean enter_loop parameter by default set to false. The parameter can be used to explicitly either enter or do not enter to the event loop. When it is set to true, the subscribe() method has no return and blocks current thread.

The event loop is database implementation specific. For OKS it is implemented as the following: 

while(true) {check_for_changes(); sleep(1);}

 and in single-threaded application user code will continue only after some changes will happen (i.e. when user callback will be called). By this reason for OKS implementation it can be desired do not set the enter_loop parameter to true and to get possible changes of the database periodically call Configuration::check_notification() method from event loop used by user application (e.g. X11 or CORBA).

For RDB implementation the subscribe() (if enter_loop parameter is true) and check_notification() methods call IPCServer::run() method.

8. Algorithms

By default, the generated classes have one-to-one mapping to database schema and DAL objects directly correspond to the database objects. If user wants to add more algorithms on top of the generated DAL without modification of DAL code by hand, he has possibility to define algorithms on top of the OKS class methods.

When a class method is created, user can add it's implementation for different programming languages. To be taken into account by genconfig, user have to provide C++ and/or Java implementation. Then he has two possibilities: 

declare method prototype, write method implementation in the separate file and add such file when build DAL; 

declare method prototype and write it's implementation in OKS.

The first way is more flexible, but requires more steps when build library. The second way does not require any additional steps when build library, but will require schema modifications to any method's implementation modification.

The online DAL defines several algorithms (e.g. to find partition, get all applications, to calculate application environment, etc.) and uses first way to implement algorithms. More information can be found in the online dal package. 

 All Data Structures Namespaces Files Functions Variables Typedefs Enumerations Enumerator Friends Defines

Generated on Tue Oct 12 2010 17:56:31 for TDAQ release tdaq-02-00-03 by 

 1.7.0
```

### Snapshot `doxygen__ConfigPackages-tdaq-03-00-01__20110326094004.html`
*Local file: `output/extracts/pcatd12/doxygen__ConfigPackages-tdaq-03-00-01__20110326094004.html`*

```text
TDAQ release tdaq-03-00-01: Config Packages

 Main Page

 Related Pages

 Modules

 Namespaces

 Data Structures

 Files

 Examples

Config Packages 

The goal of the config package is to provide user-friendly API to access data from the configuration database.

There are two layers of such API which can be seen by user:

abstract config layer working with arbitrary database schema and hiding details of DBMS implementation

data access library (DAL), that is generated for given database schema to map it on programming language data types

This page describes basics which a user should know to generate DAL from the database schema, to get data from database, to receive notification on their change, to create new data or to modify existing data using generated DAL.

1. Development of the configuration database schema 

2. Generation of the DAL 

2.1. Parameters of genconfig utility 

2.2. Integration with CMT 

3. DAL classes and methods 

3.1. Mapping Between OKS Attribute Types and Programming Languages Types 

4. Errors Handling 

5. How to get data 

5.1. Initialisation 

5.2. Read objects of class 

5.3. Reading Values of Attributes 

5.4. Reading Values of Relationships 

5.5. Cast Class Types 

5.6. Data Destruction 

6. How to create and to modify data 

6.1. Creation of new database file 

6.2. Database Includes 

6.3. Objects Manipulations 

6.4. Modification Values of Attributes 

6.5. Modification Values of Relationships 

7. Notification mechanism 

7.1. User Callback 

7.2. Subscription criteria 

7.3. Subscription 

8. Algorithms

Sections 1, 2 and 3 are needed for those, who develops own schema and wants to generate DAL. Section 4 explain basics of error handling to be known by any user of DAL. Section 5 explain how to get data using DAL. Section 6 explains how to create or to modify data using DAL. Section 7 explains how to receive notification in case of data changes. The possibility to plug-in user algorithms to the generated DAL is described in section 8.

1. Development of the configuration database schema

The user may to develop own schema in case he needs to describe own configuration data which can not be described by existing schemes. The development of the schema can be done using OKS Schema Editor. The user has the choice to extend the existing schemes or to develop his own schema from scratch. If user wants to extend existing schema, first he needs to run the editor with existing schemes (which he can not modify) and to create the schema he will be the owner of, e.g.:

oks_schema_editor dal/schema/core.schema.xml

The editor window with loaded schema will appear. Then the user can create his own schema and define his own classes. If user wants to create new schema from scratch, he just needs to run the editor without parameters and to create a new schema. For more information on the OKS schema editor, the OKS schema capabilities and exporting schema into different formats see OKS documentation [6]. After the user finish with his schema development, he needs to save the schema into xml file and add it to the sources of his package. Such schema file will be used for the database data access library generation described by next section.

2. Generation of the DAL

A DAL is generated by the genconfig utility. It uses OKS schema files as input and produces: 

C++ source files to build the library 

C++ header files to describe library interface 

C++ files to build binaries dumping content of the database 

Java files to build jar file 

genconfig.info file containing information about names of generated classes, the C++ code namespace, include prefix directory and java package name

2.1. Parameters of genconfig utility

The command line parameters of genconfig utility are listed below: 

genconfig [-d | --C++-dir-name directory-name]
 [-n | --C++-namespace namespace
 [-i | --C++-headers-dir directory-prefix]
 [-j | --java-dir-name directory-name]
 [-p | --java-package-name package-name]
 [-I | --include-dirs dirs*]
 [-c | --classes class*]
 [-D | --user-defined-classes [namespace::]user-class[@dir-pefix]*]
 [-f | --info-file-name file-name]
 [-v | --verbose]
 [-h | --help]
 -s | --schema-files file.schema.xml+

Options/Arguments:
 -d directory-name name of firectory for C++ header and implementation files
 -n namespace namespace for C++ classes
 -i directory-prefix name of directory prefix for C++ header files
 -j directory-name name of directory for java files
 -p package-name package name for java files
 -I dirs* directories where to search for already generated files
 -c class* explicit list of classes to be generated
 -D [x::]c[@d]* user-defined classes
 -f filename name of output file describing generated files
 -v switch on verbose output
 -h this message
 -s files+ the schema files (at least one is mandatory)

To generate a DAL user has to provide name of the schema file. By default the DAL is generated for all classes contained in the schema files, otherwise user should provide names of required classes via --classes parameter. It is recommended to use unique namespace for each generated DAL to avoid possible problems when several DALs are used by one application.

It is possible to reuse already generated DALs. In this case the user should to provide a list of directories containing information about already generated DALs via --include-dirs parameter, to provide list of his schema files and optionally to provide list of names of classes to be generated. It is expected such schema files use include statement for base schema files. The DAL is generated only for classes contained in the explicitly mentioned schema files, the classes from included files are ignored.

2.2. Integration with CMT

The genconfig package provides CMT fragment. To generate all classes from given schema file a user should write in his requirement file: 

use genconfig
document generate-config my-dal -s=.. \
 namespace="my-ns" \
 include="my-include" \
 packagename="my-java-package" \
 some-path/my.schema.xml

This will produce C++ files for user schema file, which will be placed in several directories (relative to the root of user package) in accordance with their types: 

C++ library source files are placed into "$(bin)my-dal.tmp" directory, 

C++ header files are placed into "$(bin)$(include-dir-name)" directory, 

the C++ source files for dump binaries are placed into "$(bin)my-dal.tmp/dump" directory, 

the java files are placed into "$(bin)my-dal.tmp/$(java-package-name)" directory.

For our example to build C++ library put into cmt/requirements file: 

library mydal $(lib_opts) $(bin)my-dal.tmp/*.cpp

To build java jar file put into cmt/requirements file: 

apply_pattern build_jar name=my-dal src_dir="$(bin)my-dal.tmp/my-java-package" sources=*.java

Finally, to build dump binaries from C++ generated files put into cmt/requirements file: 

use config
application my_dump -no_prototypes "$(bin)my-dal.tmp/dump/dump_my_ns.cpp"
macro my_dump_okslinkopts "-lmy-dal -lconfig"

Note, the order of generation of files, library and binary builds is important: 

put into your cmt/requirements file dependecy of application from generated library macro my_dump_dependencies my-dal

to allow parallel build using gmake -jN option modify your cmt/Makefile: include $(CMTROOT)/src/Makefile.header
$(bin)my-dal.make $(bin)my_dump.make:: $(bin)generate-dal.stamp
include $(CMTROOT)/src/constituents.make

To be used by other packages the library, the jar file and generated header files have to be installed. There is no need to install or even to add to the user package' sources generated C++ and Java files. The C++ and Java DAL to be installed as a normal library and jar file. To install C++ header files in platform-independent directory put into requirement file: 

ignore_pattern install_headers_bin_auto
apply_pattern install_headers src_dir="$(bin)my-dal" files=*.h

If it is necessary to produce the DAL for a subset of classes defined by the schema files, the user have to define macro generate-config-classes containing space-separated list of classes: 

macro generate-config-classes "MyClass1 MyClass2 MyClass3"

If the DAL uses other existing DALs, the user have to define macro generate-config-include-dirs containing space-separated list of directories with installed headers of such DALs, e.g.: 

macro generate-config-include-dirs "${HOME1}/share/data/dal1 \
 ${HOME2}/share/data/dal2"

It is possible to change default locations for generated C++ and Java files using generate-config document options: 

cppdir option changes default directory for generated C++ files (i.e. "my-dal.tmp" for above example); the result files will be in the "$(bin)$(cppdir)" 

javadir option changes default directory for generated Java files (i.e. "my-dal.tmp/my-java-package" for above example); the result files will be in the "$(bin)$(javadir)/$(package)"; if containes dots (e.g. package="daq.core"), they will be substituted by slashes (i.e. Java files will be genereted in /daq/core directory).

It is possible to use nested namespace for generated C++ classes. To separate namespaces use double colon signs in the namespace option of the generate-config document, e.g.: 

document generate-config my-dal -s=.. namespace="daq::core" ...

 will produce classes in nested namespaces daq and core, i.e.: 

namespace daq {
 namespace core {
 ...
 }
}

3. DAL classes and methods

For each OKS class appropriate DAL classes are generated: 

in case of C++ the generated class has the same name as OKS one and is declared inside namespace defined by the user; there is separate header file per each class; it has the same name as the database class and, to be included, it may have directory prefix, defined by user; if a class is derived from other classes, an appropriate C++ inheritance is used; 

in case of Java there is interface which has the same name as the database class declared inside package with name provided by the user; the interface implementation is in the class with suffix _Impl; the static methods to get existent or to create new objects of the class are in the class with suffix _Helper; an appropriate inheritance is used between interfaces.

For each direct attribute and relationship defined for OKS class the appropriate methods are generated. Such methods have the same names as the names of the attributes and the relationships in the database with get_ and set_ prefixes. The database attribute types are mapped to appropriate C++ and Java types. The multi-value attributes are mapped to std::vector of attribute type in C++ and to array of attribute type in Java. The database relationships are mapped to methods returning pointer or std::vector of pointers to objects of referenced class in C++ and similarly an object or array of objects in Java.

Additionally, for each class there are methods to get object's class name and object identity as they are defined in the database.

For C++ two std::ostream operators are generated for each class: 

the one with const reference to object prints out the full description of the object, and 

the other one with const pointer to object prints out the object's class name and identity.

In Java for each class there is generated method print() which prints out full description of the object.

When DAL is generated, any non-alphanumeric characters appeared in the names of classes, attributes, relationships and methods are replaced by underscore symbol, e.g. database attribute "# of c++ lines" will appear in DAL as "__of_c___lines".

3.1. Mapping Between OKS Attribute Types and Programming Languages Types

Below there is map between OKS attribute types and C++/Java types: 

 | OKS Type | C++ type | Java type 

 | bool | bool | boolean 

 | s8 (8-bits signed integer) | int8_t | char 

 | u8 (8-bits unsigned integer) | uint8_t | byte 

 | s16 (16-bits signed integer) | int16_t | short 

 | u16 (16-bits unsigned integer) | uint16_t | short 

 | s32 (32-bits signed integer) | int32_t | int 

 | u32 (32-bits unsigned integer) | uint32_t | int

 | s64 (64-bits signed integer) | int64_t | long 

 | u64 (64-bits unsigned integer) | uint64_t | long 

 | float | float | float 

 | double | double | double 

 | date | std::string | java.lang.String 

 | time | std::string | java.lang.String 

 | string | std::string | java.lang.String 

 | enum | std::string | java.lang.String 

 | class | std::string | java.lang.String 

In C++ the complex values (strings and vectors) are passed by const reference and not by value.s

4. Errors Handling

Methods of C++ and Java config classes throw exceptions in case of errors.

Each C++ method has explicit exception specification. The following exceptions can be thrown:

daq::config::Generic is used to report most of the problems (bad DB, wrong parameter, plug-in specific, etc.)

daq::config::NotFound the config object accessed by ID is not found, class accessed by name is not found

daq::config::DeletedObject accessing template object that has been deleted (via notification or by the user's code)

All above exceptions have common class daq::config::Exception, that can be used to catch all of them. 

try {
 // load database using oks file /tmp/mydb.data.xml
 Configuration db("oksconfig:/tmp/mydb.data.xml");

 ... // user's code working with db
}
catch (daq::config::Exception & ex) {
 // throw some user-defined exception in case of config exception
 throw ers::error(user::exception(ERS_HERE, "cannot read config", ex));
}

5. How to get data

The entry point to get data from database is the class Configuration defined in global namespace in C++ and in the config package in Java. Below it is described how to create an object of this class and how to use it to get the database information.

5.1. Initialisation

The Configuration constructors in both Java and C++ languages have single string parameter. If the parameter is an empty string, the constructor will use value of the TDAQ_DB environment variable. In case if both the constructor parameter and the environment variable are not set, or empty, then the configuration construcor throws daq::config::Generic in case of C++, or config.SystemException is thrown in case of Java.

The format of the parameter is "name-of-plugin:plugin-parameters". The plug-in's parameter is optional. If it is non-empty, it is passed to the implementation plug-in constructor.

In C++ the name of plug-in is converted into name of the shared library by adding prefix lib and suffix .so, e.g. "oksconfig" plug-in name is converted into "liboksconfig.so". The shared library must be in the path to shared libraries, e.g. in the LD_LIBRARY_PATH environment variable.

In Java the name of plug-in is converted into name of the class in package "plugin-name" with name created from "plugin-name", where 1-st and 4-th characters are converted to upper case and "uration" string is appended (it is so by historical reasons), e.g. "oksconfig" plug-in name is converted into "oksconfig.OksConfiguration". The CLASSPATH variable has to point to such class or jar file. For the moment two implementation plug-ins are available: 

the oksconfig using OKS implementation directly (i.e. reads XML files), and 

the rdbconfig accessing OKS with RDB server.

Details of initialization in C++ and examples

Below there are examples of the Configuration constructor explicit parameters: 

#include "config/Configuration.h"

try {
 // example (1): load daq/partitions/be_test.data.xml file using oks
 ::Configuration db1("oksconfig:daq/partitions/be_test.data.xml");

 // example (2): connect with server RDB using rdb implementation (in initial partition)
 ::Configuration db2("rdbconfig:RDB");

 // example (2a): connect with server RDB using rdb implementation (in test partition)
 ::Configuration db2a("rdbconfig:test::RDB");

 // example (2b): same as above using new style server-name@partition-name
 ::Configuration db2b("rdbconfig:RDB@test");

 // example (3): use oks implementation and create new database
 ::Configuration db3("oksconfig");
 db3.create("", "/tmp/my.data.xml", std::list<std::string>(1,"/tmp/my.sch.xml"));

 // example (4): use rdb implementation and create new database
 // on server RDB running in partition test
 ::Configuration db4("rdbconfig");
 db4.create("test::RDB", "/tmp/my.data.xml", std::list<std::string>());
}
catch(daq::config::Exception& ex) {
 std::cerr << "ERROR: " << ex << std::endl;
}

The recommended way is to get plug-in and it's parameter via environment variable. Most of the user's code for applications run by TDAQ's setup should to leave the parameter empty: 

#include "config/Configuration.h"

int main() {
 try {
 ::Configuration db("");
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

In case it the parameter can be also passed via command line, use it as shown below: 

#include "config/Configuration.h"

int main(int argc, char *argv[]) {
 try {
 ::Configuration db(argv[1]);
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

Note, to get proper plug-in name and parameter used for configuration initialization (e.g. obtained via TDAQ_DB), use get_impl_spec() method of Configuration class, which is used in above examples for debug reporting.

Initialization in Java

The Configuration constructor parameters are the same, as in case of C++. In case of problems the exception is thrown. An example is shown below: 

import config.Configuration;

try {
 config.Configuration db = new config.Configuration("rdbconfig:RDB");
}
catch (config.SystemException ex) {
 System.err.println( "ERROR caught \'config.SystemException\':");
 System.err.println( "*** " + ex.getMessage() + " ***" );
}

Note in case when rdb implementation is used, the partition name of the RDB server can be specified by several ways: 

using the same approach as for C++, i.e. via constructor parameter using double colon-separated partition and server names, e.g. "rdbconfig:partition-name::server-server" or "rdbconfig:server-server@partition-name"; 

via tdaq.ipc.partition.name java virtual machine property, e.g. run java application with "-Dtdaq.ipc.partition.name=partition-name".

5.2. Read objects of class

Once an object of the Configuration class is successfully created, it can be used to get configuration data (i.e. objects). Normally to get configuration objects only C++ template methods of the Configuration class and generated Java code should be used. The usage of config layer (i.e. direct usage of objects of ConfigObject class) only makes sense in few packages working with arbitrary database schemes.

For each generated class T two methods can be applied using configuration object: 

C++ template methods of the Configuration class: 

 const T * Configuration::get(const std::string&, bool, bool, unsigned long, const std::vector<std::string> *) - to read named object; 

 void Configuration::get(std::vector<const T*>&, bool, bool, const std::string&, unsigned long rlevel, const std::vector<std::string> *) - to read objects of class; 

Java methods generated in class T_Helper: 

static public T get(config.Configuration db, String id) to read named object 

static public T[] gets(config.Configuration db, Query query) to read objects of class 

The methods looking for single object by identity and methods looking for objects of class in case if the query string is empty are searching objects in the class and all it's subclasses, e.g. if class B is derived from class A, then the second method used for class A returns all objects of class A and all objects of class B, and the first method used for class A is looking for object with given identity in class A and then in class B. The same methods used for class B are only looking for objects of class B.

If the query is non-empty, the methods filling vectors of objects only return objects satisfying the query criteria. A query can be an OKS query string. It can be created by the OKS Data Editor or written by hand as described by the OKS documentation , e.g.: 

 (all ("Name" "my-object" =)) - search all objects of class T and it's subclasses which name is equal to "my-object"; 

 (this (and ("Address" 128 >=) ("Address" 256 <))) - search all objects of class T which address is equal or greater than 128 and less than 256; 

 (this ("Modules" all ("State" 0 =))) - search all objects of class T which has objects referenced via relationship "Modules" with attribute "State" set to 0.

C++ Example (using online dal package)

To read all applications via C++ dal provided by the online software one can write: 

#include <config/ConfigObject.h>
#include <config/Configuration.h>
#include <dal/Application.h>

try {
 ::Configuration db("");
 // 'objects' vector contains Applications and all objects from derived classes,
 // e.g. RunControlApplications, etc.
 std::vector<const dal::Application *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

To get only run control applications it is possible to use the following code: 

#include <dal/RunControlApplication.h>
try {
 ::Configuration db("");
 std::vector<const dal::RunControlApplication *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Note, to get a named object it is necessary to use template parameter explicitly and to write: 

const dal::Application * a = db.get<dal::Application>("my-application");

instead of 

const dal::Application * a = db.get("my-application"); // COMPILATION ERROR!

When the methods parameter init_children is set to true, all objects referenced by the retrieved objects are also read and initialized (i.e. values of their attributes are read from database and all referenced objects are also recursively read). Otherwise the referenced objects can only be pre-allocated (if they were not already read explicitly) and the actual reading will happen, when the user will apply a method to read values of their attributes or relationships.

When the methods parameter init_object is set to false, all retrieved objects are only pre-allocated without reading their attributes and relationships. The values of attributes and relationships will actually be read from database implementation, when the user will apply a method to read an attribute or relationship value.

The above two parameters can be used by the user to improve performance. For example, if the parameter init_children is set to false, the only objects which are really used by the user process will be read from the database. However in this case the database can not be closed (e.g. to free used resources) until the configuration data are used. Also, the actual read from database can happen at an unexpected moment, that can introduce undesired delays.

Java Example (online DAL)

To read all applications via Java dal provided by the online software one can write: 

import config.Configuration;
import dal.Application;
import dal.Application_Helper;
...
config.Configuration db = new config.Configuration(...);
try {
 dal.Application objs[] = dal.Application_Helper.get(db, new config.Query());
} catch ( config.NotFoundException ex ) {
 System.err.println("ERROR: bad query or no such class loaded");
} catch ( config.SystemException ex ) {
 System.err.println("ERROR: caught system exception");
}

To get only run control applications it is possible to write (try/catch statements are skipped): 

import dal.RunControlApplication;
import dal.RunControlApplication_Helper;
...
dal.RunControlApplication objs[] = dal.RunControlApplication_Helper.get(db, new config.Query());

Below there is an example of code to get an application by ID. Note, if object with such ID does not exist, config.NotFoundException exception is thrown. 

try {
 dal.Application obj = dal.Application_Helper.get(db, "RootController");
}
catch (config.NotFoundException e) {
 System.err.println( "ERROR: can not find application \'RootController\'" );
}

5.3. Reading Values of Attributes

Once the objects are retrieved, the user can get values of their attributes. A method to read attribute value is created for each attribute of each generated class. It has the following format: 

for C++: 

 type get_AttributeName() const - for single-value integer and float numbers; 

 const std::string& get_AttributeName() const - for single-value string-based attributes; 

 const std::vector<type>& get_AttributeName() const - for multi-value attributes; 

for Java: 

 type get_AttributeName() const - for single-value attributes; 

 type[] get_AttributeName() const - for multi-value attributes. 

Attribute Converters

The user can use one or several ways to convert values of all attributes of a C++ or Java type. To do this he/she needs to implement or to use already existing converter class, to create converter object of that class and to pass such object to the Configuration object using method Configuration::register_converter().

In case of C++ such class has to inherit from the template Configuration::AttributeConverter < T > class, where template parameter T defines type of attributes which values need to be converted and to implement virtual method Configuration::AttributeConverter::convert(), that performs the real conversion of attribute values.

Note:The C++ converter object is destroyed by the configuration destructor. User must not call delete on the attribute converter object.
In case of Java a converter class has to implement config.AttributeConverter interface defining two methods: the method convert() as in C++ and the method get_class(), which returns class of converted attributes.

Below there is C++ example of user functions converting string and integer attributes: 

#include <config/Configuration.h>

 // converter to replace by '_' a non-alpha-numeric symbol in db strings
class GoodString : public ::Configuration::AttributeConverter<std::string> {
public:
 static char cvt_symbol(char c) { return (isalnum(c) ? c : '_'); }
 void convert(std::string& s, const Configuration&, const ConfigObject&, const std::string&) {
 std::transform(s.begin(), s.end(), s.begin(), cvt_symbol);
 }
}
 // converter to make any long integer value positive
class PositiveInt : public ::Configuration::AttributeConverter<unsigned long> {
 void convert(unsigned long& i, const Configuration&, const ConfigObject&, const std::string&) {
 if(i < 0) i = -i;
 }
}
...
try {
 ::Configuration db("");
 db.register_converter(new GoodString());
 db.register_converter(new PositiveInt());
 ...
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In the Java an example of Java code is shown below: 

import config.Configuration;
import config.AttributeConverter;

 // converter removes leading and trailing whitespace from a string
public class TrimString implements config.AttributeConverter {
 public Object convert(Object s, config.Configuration db, config.ConfigObject obj, String attr_name) { return (Object)(s.trim()); }
 public Class get_class() { return String.class; }
}
...
config.Configuration db = new config.Configuration("");
db.register_converter(new TrimString());

Online DAL Converters

The core TDAQ C++ DAL (libdaq-core-dal.so) provides converter daq::core::SubstituteVariables class to substitute configuration parameters in values of string attributes. It's constructor requires Configuration object and Partition object, since they are used to calculate conversion map. In case, if configuration database is reloaded, such parameters have to be reset using reset() method. An example of the C++ code is shown below: 

#include <config/Configuration.h>
#include "dal/Partition.h"
#include <dal/util.h>

try {
 ::Configuration db("");
 if(const daq::core::Partition * p = daq::core::get_partition(db, "partition-X")) {
 db.register_converter(new daq::core::SubstituteVariables(db, *p));
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Similar Java dal.jar provides attribute converter in the same way. An example of it's usage is shown below: 

import config.Configuration;
import config.DalObject;
import dal.SubstituteVariables;
import dal.Partition;

config.Configuration db = new config.Configuration("");
dal.Partition p = dal.Algorithms.get_partition(db, "partition-X");
if(p != null) {
 db.register_converter(new dal.SubstituteVariables(db, p));
}

5.4. Reading Values of Relationships

Once an object is retrieved, the user can get objects referenced by it. A method is created for each relationship of each generated class. It has the following format: 

for C++: 

 const class-type * get_RelationshipName() const - for single-value relationships; 

 const std::vector<const class-type*>& get_RelationshipName() const - for multi-value relationships; 

for Java: 

 class-type get_RelationshipName() const - for single-value relationships; 

 class-type[] get_RelationshipName() const - for multi-value relationships. 

5.5. Cast Class Types

There are situations when user may need to cast an object from one class to a derived one. To make a down cast for an object of generated class the user should to use the methods of the configuration classes and never use cast supported by the programming languages.

C++ cast

There are situations when some set of objects can belong to different classes, e.g. objects can be of class A or B which is derived from class A. For a down cast the Configuration::cast() method must be used. As an example, the code to try and to cast from application to run-control application type is shown below: 

try {
 ::Configuration db;
 // some code to get the vector of applications
 const std::vector<const dal::Application*>& l = ...;
 std::vector<const dal::Application*>::const_iterator j = l.begin();
 for(; j != l.end(); ++j) {
 if(const dal::RunControlApplication * r = db.cast<dal::RunControlApplication>(*j)) {
 std::cout << "application " << r << " is run control application" << std::endl; 
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Java cast

To down cast an object of generated Java DAL use aproapriate cast() method in generated class. For example, some object of application class can be down casted to the run control application: 

config.Configuration db(...);
dal.Application a = ...; // some code to get application
dal.RunControlApplication rc_application = dal.RunControlApplication_Helper.cast(db, a);
if(rc_application != null) { ... }

5.6. Data Destruction

In C++ the object of the Configuration class should not be destroyed while the DAL is in use. All objects read via template methods are destroyed by the Configuration class destructor. The user must never try to modify or to destroy such objects himself.

6. How to create and to modify data

This section explains how to create a new database file, how to create or remove database data and how to modify existing data.

Any modifications described by this section becomes persistent and visible to others processes only after successful commit operation. If the modification should not be committed (e.g. a modification failed), it is necessary to execute abort operation, e.g. in C++: 

try {
 ::Configuration db();
 bool success = true;
 ... // some code which makes changes and sets the variable to false if failed
 if(success) {
 std::cout << "commit changes\n";
 db.commit(); // one also check return status, true means success
 }
 else {
 std::cerr << "ERROR: something was wrong, abort changes\n";
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Below there is the same example for Java: 

config.Configuration db = new config.Configuration(...);
... // some code to makes changes and sets the success variable to false if failed
if(success) {
 System.out.println("commit changes");
 db.commit();
}
else {
 System.err.println("ERROR: something was wrong, abort changes");
 db.abort();
}

To modify or to destroy an object using generated C++ DAL methods described below, it is necessary to have a non-const pointer or reference on the object. However all generated DAL methods return objects as const. To make a change it is necessary to use C++ const_cast to get non-const pointer or reference.

6.1. Creation of new database file

To create a new database file using C++ it is necessary to build an object of the Configuration class only providing name of implementation plug-in: 

::Configuration db("oksconfig");

Similar code for Java is below: 

config.Configuration db = new config.Configuration("rdbconfig"); // no db file

To create a new database data file it is necessary to decide which schema (at least one schema is always required) and optionally others database files will be used. Then it is necessary to provide an absolute name for newly created database file (the user should have write permission or the rdb server must be run in read-write mode under account which has such rights). If rdb implementation is used, it is also necessary to provide server and optionally partition name. After this it is necessary to use create method of the Configuration class and check it's return status.

Below there is example for C++ and oks implementation: 

try {
 ::Configuration db("oksconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 if(db.create("", db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For rdb implementation it is similar, but requires rdb server and optionally partition's names: 

try {
 ::Configuration db("rdbconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 const char * server_name = "foo::bar"; // server with name bar running in part. foo
 if(db.create(server_name, db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << " on " << server_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java an example with rdb implementation is shown below: 

try {
 config.Configuration db = new config.Configuration("rdbconfig");
 String[] includes = new String[2];
 includes[0] = "online/schema/online.schema.xml"; // common schema
 includes[1] = "online/segments/setup.data.xml"; // online infrastructure
 db.create("foo::bar", "/tmp/my-partition.data.xml", includes);
 db.commit();
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
}
catch(config.NotAllowedException ex) {
 System.err.println("ERROR: caught \'config.NotAllowed\' exception");
}
... // catch config.AlreadyExistsException in a similar way

The included files should exist in advance and be defined either as an absolute path or as a relative path to a token of the TDAQ_DB_PATH variable value.

6.2. Database Includes

There are methods in C++ class Configuration to add a new include, to remove an existing include or to get list of includes for given database. They are: 

 bool Configuration::add_include(const std::string& db_name, const std::string& include) - adds include to the database db_name and returns true in case of success or false if failed; 

 bool Configuration::remove_include(const std::string& db_name, const std::string& include) - removes an existing include from the database db_name and returns true in case of success or false if failed; 

 bool Configuration::get_includes(const std::string& db_name, std::list<std::string>& includes) const - fills list of includes by files which are included by the db_name and returns true in case of success or false if failed.

Similar methods in Java class config.Configuration are: 

 void add_include(String db_name, String include) - adds include to the database db_name or throws exception if failed; 

 void remove_include(String db_name, String include) - removes an existing include from the database db_name or throws exception if failed; 

 void get_includes(String db_name, String[] includes) - fills array of includes by files which are included by the db_name or throws exception if failed.

6.3. Objects Manipulations

This subsection explains how to create and how to destroy database objects.

Objects Creation

To create a new object using generated C++ DAL there are two Configuration template methods: 

 const T * Configuration::create(const std::string& at, const std::string& id, bool) - to create new object of class T with identity id at existing database file with name at; 

 const T * Configuration::create(const ::DalObject& at, const std::string& id, bool) - to create new object of class T with identity id at a database file where object at is stored.

The methods return non-null pointer in case of success or null if failed. The second method is faster since time to search the database file where to put new object is much smaller.

When the init_object parameter is set to false, then the values of attributes and relationships are not read from implementation (for a newly created object they are set to default values in accordance with the database schema).

An example how to create two new objects of the online dal::Computer class is shown below: 

try {
 ::Configuration db(...);
 const char * dbfile = "/tmp/my-db.data.xml";
 const dal::Computer * host = db.create<dal::Computer>(dbfile, "host-1");
 if(host == 0) {
 std::cerr << "ERROR: failed to create object \'host-1\' at \'" << dbfile << "\'\n";
 }
 else {
 if(db.create<dal::Computer>(*host, "host-2") == 0) {
 std::cerr << "ERROR: failed to create object \'host-2\' at file of " << host;
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

On Java similar methods are genereted in the helper classes. For class T two methods are available: 

 T create(config.Configuration db, String at, String id) - to create new object of class T with identity id at existing database file with name at; 

 T create(config.Configuration db, config.DalObject at, String id) - to create new object of class T with identity id at a database file where object at is stored.

The example to create online segment and it's application is shown below:: 

config.Configuration db = new ...
String db_file = "/tmp/my-db.data.xml";
try {
 dal.Segment s = dal.Segment_Helper.create(db, db_file, "my segment");
 dal.Application a = dal.Application_Helper.create(db, s, "my application");
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
} ... // also other exceptions to be caught

Objects Destruction

To destroy an existing object there is template method in the C++ Configuration class bool destroy(T& obj). It returns true in case of success and false if failed. See example: 

try {
 ::Configuration db(...);
 dal::Computer * host = ...; // some code to get pointer
 db.destroy(*host);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In Java the method void destroy(config.Configuration db) is generated in T.java, e.g.: 

config.Configuration db = new ...;
dal.Computer host = ...; // some code to get object
try {
 host.destroy(db);
}
catch(config.SystemException ex) {
 System.err.println("ERROR: failed to destroy " + host);
} ... // also other exceptions to be caught

6.4. Modification Values of Attributes

Once the objects are retrieved or created, the user can modify values of their attributes. A method to set attribute value is created for each attribute of each generated class. The mapping between C++/Java types and OKS types can be seen in the 3.1. Mapping Between OKS Attribute Types and Programming Languages Types section.

In C++ such method throws daq::config::Exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(const std::vector<type>& value) - for multi-value attribute.

In Java such method throws an exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(type[] value) - for multi-value attribute.

6.5. Modification Values of Relationships

Once the objects are retrieved or created, the user can modify values of their relationships. A method to set relationship value is created for each relationship of each generated class.

For C++ it has the following format and throws daq::config::Exception if failed: 

 void set_RelationshipName(const class-type * value) - for single-value relationships; 

 void set_RelationshipName(const std::vector<const class-type*>& value) - for multi-value relationships.

For Java it has the following format and throws an exception if failed: 

 void set_RelationshipName(class-type value) - for single-value relationships; 

 void set_RelationshipName(class-type[] value) - for multi-value relationships.

7. Notification mechanism

The user application can be notified on changes of the configuration data. To do this user should to implement one or many callback functions (C++) or classes (Java) which will be used when the database changes are committed and to choose which changes in classes and objects should be reported (i.e. to define the subscription criteria ).

The user receives description of information changes in one go via callbacks invoked after commit of database changes. This is more preferred way than individual callback per object or per class since user may want to see all changes at single point. Each callback receives own list of changes in accordance with it's subscription criteria.

The changes are reported as a collection of changes per DAL class. A change per class contains 4 parameters: the class name and the identities of created, modified and removed objects.

To make a subscription it is necessary to make three steps: 

implement callback, 

define subscription criteria, 

invoke subscribe method with above entities on the configuration object.

7.1. User Callback

To start with any subscription on database changes the user must to implement at least one Configuration::notify callback function in C++ or config.Callback interface on Java. Below there are details for C++ and Java subscriptions.

C++ callback function

The user has to implement Configuration::notify callback. It has the following parameters: 

 const std::vector<::ConfigurationChange *> & changes - description of changes 

 void * parameter - user parameter

The ConfigurationChange class is declared in the config/Change.h file and has 4 methods to get name of the class and vectors of created, modified and removed object identities. An example of callback functions is shown below: 

void callback(const std::vector< ConfigurationChange *> & changes, void *)
{
 std::cout << "The CALLBACK reports all changes:\n";

 // iterate changes sorted by classes
 for(std::vector<ConfigurationChange *>::const_iterator j = changes.begin(); j != changes.end(); ++j) {

 // print class name
 std::cout << "- there are changes in class \"" << (*j)->get_class_name() << "\"\n";

 std::vector<std::string>::const_iterator i;

 // print modified objects
 for(i = (*j)->get_modified_objs().begin(); i != (*j)->get_modified_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was modified\n";
 }

 // print removed objects
 for(i = (*j)->get_removed_objs().begin(); i != (*j)->get_removed_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was removed\n";
 }

 // print created objects
 for(i = (*j)->get_created_objs().begin(); i != (*j)->get_created_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was created\n";
 }
 }
}

Java callback interface

The user has to create a class implementing the config.Callback interface. It requires to implement method void process_changes(config.Change[] changes, java.lang.Object parameter). Example below illustrates how to implement notification callback: 

class TestCallback implements config.Callback {
 private config.Configuration db;

 public TestCallback(config.Configuration d) { db = d; }

 public void process_changes(config.Change[] changes, java.lang.Object parameter) {

 // the parameter can be any; as an example, the callback ID is passed as string
 String cb_id = (String)parameter;

 // print out changes description
 System.out.println("[TestCallback " + cb_id + "] got changes:");
 config.Change.print(changes, " ");

 // iterate changes by classes
 for(int i = 0; i < changes.length; i++) {
 config.Change change = changes[i];
 System.out.println("* there are changes in the \'" + change.get_class_name() + "\' class");

 // just as example, look for changed objects of the Application class
 if((change.get_class_name().equals("Application") == true) && (change.get_changed_objects() != null)) {
 System.out.println("* " + change.get_changed_objects().length + " updated objects of the Application class");

 // iterate by all changed objects and print them out
 for(int j = 0; j < change.get_changed_objects().length; ++j) {
 dal.Application a = dal.Application_Helper.get(db, change.get_changed_objects()[j]);

 // an example of correct down cast
 if(a.class_name().equals("RunControlApplication")) {
 dal.RunControlApplication_Helper.get(db, a.config_object()).print(" "); // print as RC application
 }
 else {
 a.print(" "); // print as an application
 }
 }
 }
 }
 }
}

7.2. Subscription criteria

The subscription criteria is an object of ConfigurationSubscriptionCriteria class in C++ or config.Subscription class in Java. It is used to define lists of classes and objects, which changes will be monitored and reposted to user. If user provides no any class or object, it means subscription on any change and a database modification is reported.

Subscription on any changes in class

The notification callback is invoked for any changes of class objects including creation of new objects, removing or modification of existing objects.

In C++ to subscribe on any changes in some class the user should to use ConfigurationSubscriptionCriteria::add(const std::string&) method. For a class generated by genconfig the s_class_name attribute can be used, e.g. to subscribe on changes in class dal::Application: 

::ConfigurationSubscriptionCriteria c;
c.add(dal::Application::s_class_name);

In Java method config.Subscription.add(String class_name) should be used, e.g. to subscribe on changes in class Application it is necessary to write the following code: 

config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add("Application");

Subscription on object changes

When subscription on object changes has done, the notification callback is invoked for any changes of the objects or it's removing.

In C++ to subscribe on object changes notification the user should to use ConfigurationSubscriptionCriteria::add(const ::DalObject&), e.g. to subscribe on changes of an object of the Application class: 

::ConfigurationSubscriptionCriteria c;
const dal::Application * app_obj;
c->add(*app_obj);

In Java config.add(DalObject obj) method to be used, e.g.: 

dal.Application app = ...; // some code to get application object
config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add(app);

7.3. Subscription

To make the actual subscription it is necessary to have a notification callback been implemented and a subscription criteria object. The the method subscribe() to be invoked on the configuration object. For C++ an example is shown below: 

 // user-defined callback
void cb(const std::vector<ConfigurationChange *> & changes, void * p) { ... }

try {
 // configuration object
 ::Configuration db(...);

 // subscription criteria object
 ::ConfigurationSubscriptionCriteria c;
 c.add(dal::Application::s_class_name);

 // subscription; if database is changed, the cb can be invoked after this line
 ::CallbackId id = db.subscribe(c, cb);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java above example looks like: 

 // user-defined callback
class MyCallback implements config.Callback { ... }

 // configuration object
config.Configuration db = new config.Configuration(...);

 // subscription criteria object
config.Subscription c = new config.Subscription(new MyCallback(db), null);
c.add("Application");

 // subscription; MyCallback::process_changes() can be invoked after this line
db.subscribe(c);

The method unsubscribe() can be used to remove subscription set above. In case of C++ it's parameter is a return value of the subscribe() method (i.e. CallbackId value). For Java it's parameter is the subscription object used as parameter of subscribe() method.

8. Algorithms

By default, the generated classes have one-to-one mapping to database schema and DAL objects directly correspond to the database objects. If user wants to add more algorithms on top of the generated DAL without modification of DAL code by hand, he has possibility to define algorithms on top of the OKS class methods.

When a class method is created, user can add it's implementation for different programming languages. To be taken into account by genconfig, user have to provide C++ and/or Java implementation. Then he has two possibilities: 

declare method prototype, write method implementation in the separate file and add such file when build DAL; 

declare method prototype and write it's implementation in OKS.

The first way is more flexible, but requires more steps when build library. The second way does not require any additional steps when build library, but will require schema modifications to any method's implementation modification.

The online DAL defines several algorithms (e.g. to find partition, get all applications, to calculate application environment, etc.) and uses first way to implement algorithms. More information can be found in the online dal package. 

 All Data Structures Namespaces Files Functions Variables Typedefs Enumerations Enumerator Friends Defines

Generated on Fri Feb 18 2011 11:55:08 for TDAQ release tdaq-03-00-01 by 

 1.7.2
```

### Snapshot `doxygen__ConfigPackages-tdaq-04-00-00__20111027092808.html`
*Local file: `output/extracts/pcatd12/doxygen__ConfigPackages-tdaq-04-00-00__20111027092808.html`*

```text
TDAQ release tdaq-04-00-00: Config Packages

 Main Page

 Related Pages

 Modules

 Namespaces

 Data Structures

 Files

 Examples

Config Packages 

The goal of the config package is to provide user-friendly API to access data from the configuration database.

There are two layers of such API which can be seen by user:

abstract config layer working with arbitrary database schema and hiding details of DBMS implementation

data access library (DAL), that is generated for given database schema to map it on programming language data types

This page describes basics which a user should know to generate DAL from the database schema, to get data from database, to receive notification on their change, to create new data or to modify existing data using generated DAL.

1. Development of the configuration database schema 

2. Generation of the DAL 

2.1. Parameters of genconfig utility 

2.2. Integration with CMT 

3. DAL classes and methods 

3.1. Mapping Between OKS Attribute Types and Programming Languages Types 

4. Errors Handling 

5. How to get data 

5.1. Initialisation 

5.2. Read objects of class 

5.3. Reading Values of Attributes 

5.4. Reading Values of Relationships 

5.5. Cast Class Types 

5.6. Data Destruction 

6. How to create and to modify data 

6.1. Creation of new database file 

6.2. Database Includes 

6.3. Objects Manipulations 

6.4. Modification Values of Attributes 

6.5. Modification Values of Relationships 

7. Notification mechanism 

7.1. User Callback 

7.2. Subscription criteria 

7.3. Subscription 

8. Algorithms

Sections 1, 2 and 3 are needed for those, who develops own schema and wants to generate DAL. Section 4 explain basics of error handling to be known by any user of DAL. Section 5 explain how to get data using DAL. Section 6 explains how to create or to modify data using DAL. Section 7 explains how to receive notification in case of data changes. The possibility to plug-in user algorithms to the generated DAL is described in section 8.

1. Development of the configuration database schema

The user may to develop own schema in case he needs to describe own configuration data which can not be described by existing schemes. The development of the schema can be done using OKS Schema Editor. The user has the choice to extend the existing schemes or to develop his own schema from scratch. If user wants to extend existing schema, first he needs to run the editor with existing schemes (which he can not modify) and to create the schema he will be the owner of, e.g.:

oks_schema_editor dal/schema/core.schema.xml

The editor window with loaded schema will appear. Then the user can create his own schema and define his own classes. If user wants to create new schema from scratch, he just needs to run the editor without parameters and to create a new schema. For more information on the OKS schema editor, the OKS schema capabilities and exporting schema into different formats see OKS documentation [6]. After the user finish with his schema development, he needs to save the schema into xml file and add it to the sources of his package. Such schema file will be used for the database data access library generation described by next section.

2. Generation of the DAL

A DAL is generated by the genconfig utility. It uses OKS schema files as input and produces: 

C++ source files to build the library 

C++ header files to describe library interface 

C++ files to build binaries dumping content of the database 

Java files to build jar file 

genconfig.info file containing information about names of generated classes, the C++ code namespace, include prefix directory and java package name

2.1. Parameters of genconfig utility

The command line parameters of genconfig utility are listed below: 

genconfig [-d | --C++-dir-name directory-name]
 [-n | --C++-namespace namespace
 [-i | --C++-headers-dir directory-prefix]
 [-j | --java-dir-name directory-name]
 [-p | --java-package-name package-name]
 [-I | --include-dirs dirs*]
 [-c | --classes class*]
 [-D | --user-defined-classes [namespace::]user-class[@dir-pefix]*]
 [-f | --info-file-name file-name]
 [-v | --verbose]
 [-h | --help]
 -s | --schema-files file.schema.xml+

Options/Arguments:
 -d directory-name name of firectory for C++ header and implementation files
 -n namespace namespace for C++ classes
 -i directory-prefix name of directory prefix for C++ header files
 -j directory-name name of directory for java files
 -p package-name package name for java files
 -I dirs* directories where to search for already generated files
 -c class* explicit list of classes to be generated
 -D [x::]c[@d]* user-defined classes
 -f filename name of output file describing generated files
 -v switch on verbose output
 -h this message
 -s files+ the schema files (at least one is mandatory)

To generate a DAL user has to provide name of the schema file. By default the DAL is generated for all classes contained in the schema files, otherwise user should provide names of required classes via --classes parameter. It is recommended to use unique namespace for each generated DAL to avoid possible problems when several DALs are used by one application.

It is possible to reuse already generated DALs. In this case the user should to provide a list of directories containing information about already generated DALs via --include-dirs parameter, to provide list of his schema files and optionally to provide list of names of classes to be generated. It is expected such schema files use include statement for base schema files. The DAL is generated only for classes contained in the explicitly mentioned schema files, the classes from included files are ignored.

2.2. Integration with CMT

The genconfig package provides CMT fragment. To generate all classes from given schema file a user should write in his requirement file: 

use genconfig
document generate-config my-dal -s=.. \
 namespace="my-ns" \
 include="my-include" \
 packagename="my-java-package" \
 some-path/my.schema.xml

This will produce C++ files for user schema file, which will be placed in several directories (relative to the root of user package) in accordance with their types: 

C++ library source files are placed into "$(bin)my-dal.tmp" directory, 

C++ header files are placed into "$(bin)$(include-dir-name)" directory, 

the C++ source files for dump binaries are placed into "$(bin)my-dal.tmp/dump" directory, 

the java files are placed into "$(bin)my-dal.tmp/$(java-package-name)" directory.

For our example to build C++ library put into cmt/requirements file: 

library mydal $(lib_opts) $(bin)my-dal.tmp/*.cpp

To build java jar file put into cmt/requirements file: 

apply_pattern build_jar name=my-dal src_dir="$(bin)my-dal.tmp/my-java-package" sources=*.java

Finally, to build dump binaries from C++ generated files put into cmt/requirements file: 

use config
application my_dump -no_prototypes "$(bin)my-dal.tmp/dump/dump_my_ns.cpp"
macro my_dump_okslinkopts "-lmy-dal -lconfig"

Note, the order of generation of files, library and binary builds is important: 

put into your cmt/requirements file dependecy of application from generated library macro my_dump_dependencies my-dal

to allow parallel build using gmake -jN option modify your cmt/Makefile: include $(CMTROOT)/src/Makefile.header
$(bin)my-dal.make $(bin)my_dump.make:: $(bin)generate-dal.stamp
include $(CMTROOT)/src/constituents.make

To be used by other packages the library, the jar file and generated header files have to be installed. There is no need to install or even to add to the user package' sources generated C++ and Java files. The C++ and Java DAL to be installed as a normal library and jar file. To install C++ header files in platform-independent directory put into requirement file: 

ignore_pattern install_headers_bin_auto
apply_pattern install_headers src_dir="$(bin)my-dal" files=*.h

If it is necessary to produce the DAL for a subset of classes defined by the schema files, the user have to define macro generate-config-classes containing space-separated list of classes: 

macro generate-config-classes "MyClass1 MyClass2 MyClass3"

If the DAL uses other existing DALs, the user have to define macro generate-config-include-dirs containing space-separated list of directories with installed headers of such DALs, e.g.: 

macro generate-config-include-dirs "${HOME1}/share/data/dal1 \
 ${HOME2}/share/data/dal2"

It is possible to change default locations for generated C++ and Java files using generate-config document options: 

cppdir option changes default directory for generated C++ files (i.e. "my-dal.tmp" for above example); the result files will be in the "$(bin)$(cppdir)" 

javadir option changes default directory for generated Java files (i.e. "my-dal.tmp/my-java-package" for above example); the result files will be in the "$(bin)$(javadir)/$(package)"; if containes dots (e.g. package="daq.core"), they will be substituted by slashes (i.e. Java files will be generated in /daq/core directory).

It is possible to use nested namespace for generated C++ classes. To separate namespaces use double colon signs in the namespace option of the generate-config document, e.g.: 

document generate-config my-dal -s=.. namespace="daq::core" ...

 will produce classes in nested namespaces daq and core, i.e.: 

namespace daq {
 namespace core {
 ...
 }
}

3. DAL classes and methods

For each OKS class appropriate DAL classes are generated: 

in case of C++ the generated class has the same name as OKS one and is declared inside namespace defined by the user; there is separate header file per each class; it has the same name as the database class and, to be included, it may have directory prefix, defined by user; if a class is derived from other classes, an appropriate C++ inheritance is used; 

in case of Java there is interface which has the same name as the database class declared inside package with name provided by the user; the interface implementation is in the class with suffix _Impl; the static methods to get existent or to create new objects of the class are in the class with suffix _Helper; an appropriate inheritance is used between interfaces.

For each direct attribute and relationship defined for OKS class the appropriate methods are generated. Such methods have the same names as the names of the attributes and the relationships in the database with get_ and set_ prefixes. The database attribute types are mapped to appropriate C++ and Java types. The multi-value attributes are mapped to std::vector of attribute type in C++ and to array of attribute type in Java. The database relationships are mapped to methods returning pointer or std::vector of pointers to objects of referenced class in C++ and similarly an object or array of objects in Java.

Additionally, for each class there are methods to get object's class name and object identity as they are defined in the database.

For C++ two std::ostream operators are generated for each class: 

the one with const reference to object prints out the full description of the object, and 

the other one with const pointer to object prints out the object's class name and identity.

In Java for each class there is generated method print() which prints out full description of the object.

When DAL is generated, any non-alphanumeric characters appeared in the names of classes, attributes, relationships and methods are replaced by underscore symbol, e.g. database attribute "# of c++ lines" will appear in DAL as "__of_c___lines".

3.1. Mapping Between OKS Attribute Types and Programming Languages Types

Below there is map between OKS attribute types and C++/Java types: 

 | OKS Type | C++ type | Java type 

 | bool | bool | boolean 

 | s8 (8-bits signed integer) | int8_t | char 

 | u8 (8-bits unsigned integer) | uint8_t | byte 

 | s16 (16-bits signed integer) | int16_t | short 

 | u16 (16-bits unsigned integer) | uint16_t | short 

 | s32 (32-bits signed integer) | int32_t | int 

 | u32 (32-bits unsigned integer) | uint32_t | int

 | s64 (64-bits signed integer) | int64_t | long 

 | u64 (64-bits unsigned integer) | uint64_t | long 

 | float | float | float 

 | double | double | double 

 | date | std::string | java.lang.String 

 | time | std::string | java.lang.String 

 | string | std::string | java.lang.String 

 | enum | std::string | java.lang.String 

 | class | std::string | java.lang.String 

In C++ the complex values (strings and vectors) are passed by const reference and not by value.s

4. Errors Handling

Methods of C++ and Java config classes throw exceptions in case of errors.

Each C++ method has explicit exception specification. The following exceptions can be thrown:

daq::config::Generic is used to report most of the problems (bad DB, wrong parameter, plug-in specific, etc.)

daq::config::NotFound the config object accessed by ID is not found, class accessed by name is not found

daq::config::DeletedObject accessing template object that has been deleted (via notification or by the user's code)

All above exceptions have common class daq::config::Exception, that can be used to catch all of them. 

try {
 // load database using oks file /tmp/mydb.data.xml
 Configuration db("oksconfig:/tmp/mydb.data.xml");

 ... // user's code working with db
}
catch (daq::config::Exception & ex) {
 // throw some user-defined exception in case of config exception
 throw ers::error(user::exception(ERS_HERE, "cannot read config", ex));
}

5. How to get data

The entry point to get data from database is the class Configuration defined in global namespace in C++ and in the config package in Java. Below it is described how to create an object of this class and how to use it to get the database information.

5.1. Initialisation

The Configuration constructors in both Java and C++ languages have single string parameter. If the parameter is an empty string, the constructor will use value of the TDAQ_DB environment variable. In case if both the constructor parameter and the environment variable are not set, or empty, then the configuration constructor throws daq::config::Generic in case of C++, or config.SystemException is thrown in case of Java.

The format of the parameter is "name-of-plugin:plugin-parameters". The plug-in's parameter is optional. If it is non-empty, it is passed to the implementation plug-in constructor.

In C++ the name of plug-in is converted into name of the shared library by adding prefix lib and suffix .so, e.g. "oksconfig" plug-in name is converted into "liboksconfig.so". The shared library must be in the path to shared libraries, e.g. in the LD_LIBRARY_PATH environment variable.

In Java the name of plug-in is converted into name of the class in package "plugin-name" with name created from "plugin-name", where 1-st and 4-th characters are converted to upper case and "uration" string is appended (it is so by historical reasons), e.g. "oksconfig" plug-in name is converted into "oksconfig.OksConfiguration". The CLASSPATH variable has to point to such class or jar file. For the moment two implementation plug-ins are available: 

the oksconfig using OKS implementation directly (i.e. reads XML files), and 

the rdbconfig accessing OKS with RDB server.

Details of initialization in C++ and examples

Below there are examples of the Configuration constructor explicit parameters: 

#include "config/Configuration.h"

try {
 // example (1): load daq/partitions/be_test.data.xml file using oks
 ::Configuration db1("oksconfig:daq/partitions/be_test.data.xml");

 // example (2): connect with server RDB using rdb implementation (in initial partition)
 ::Configuration db2("rdbconfig:RDB");

 // example (2a): connect with server RDB using rdb implementation (in test partition)
 ::Configuration db2a("rdbconfig:test::RDB");

 // example (2b): same as above using new style server-name@partition-name
 ::Configuration db2b("rdbconfig:RDB@test");

 // example (3): use oks implementation and create new database
 ::Configuration db3("oksconfig");
 db3.create("", "/tmp/my.data.xml", std::list<std::string>(1,"/tmp/my.sch.xml"));

 // example (4): use rdb implementation and create new database
 // on server RDB running in partition test
 ::Configuration db4("rdbconfig");
 db4.create("test::RDB", "/tmp/my.data.xml", std::list<std::string>());
}
catch(daq::config::Exception& ex) {
 std::cerr << "ERROR: " << ex << std::endl;
}

The recommended way is to get plug-in and it's parameter via environment variable. Most of the user's code for applications run by TDAQ's setup should to leave the parameter empty: 

#include "config/Configuration.h"

int main() {
 try {
 ::Configuration db("");
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

In case it the parameter can be also passed via command line, use it as shown below: 

#include "config/Configuration.h"

int main(int argc, char *argv[]) {
 try {
 ::Configuration db(argv[1]);
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

Note, to get proper plug-in name and parameter used for configuration initialization (e.g. obtained via TDAQ_DB), use get_impl_spec() method of Configuration class, which is used in above examples for debug reporting.

Initialization in Java

The Configuration constructor parameters are the same, as in case of C++. In case of problems the exception is thrown. An example is shown below: 

import config.Configuration;

try {
 config.Configuration db = new config.Configuration("rdbconfig:RDB");
}
catch (config.SystemException ex) {
 System.err.println( "ERROR caught \'config.SystemException\':");
 System.err.println( "*** " + ex.getMessage() + " ***" );
}

Note in case when rdb implementation is used, the partition name of the RDB server can be specified by several ways: 

using the same approach as for C++, i.e. via constructor parameter using double colon-separated partition and server names, e.g. "rdbconfig:partition-name::server-server" or "rdbconfig:server-server@partition-name"; 

via tdaq.ipc.partition.name java virtual machine property, e.g. run java application with "-Dtdaq.ipc.partition.name=partition-name".

5.2. Read objects of class

Once an object of the Configuration class is successfully created, it can be used to get configuration data (i.e. objects). Normally to get configuration objects only C++ template methods of the Configuration class and generated Java code should be used. The usage of config layer (i.e. direct usage of objects of ConfigObject class) only makes sense in few packages working with arbitrary database schemes.

For each generated class T two methods can be applied using configuration object: 

C++ template methods of the Configuration class: 

 const T * Configuration::get(const std::string&, bool, bool, unsigned long, const std::vector<std::string> *) - to read named object; 

 void Configuration::get(std::vector<const T*>&, bool, bool, const std::string&, unsigned long rlevel, const std::vector<std::string> *) - to read objects of class; 

Java methods generated in class T_Helper: 

static public T get(config.Configuration db, String id) to read named object 

static public T[] gets(config.Configuration db, Query query) to read objects of class 

The methods looking for single object by identity and methods looking for objects of class in case if the query string is empty are searching objects in the class and all it's subclasses, e.g. if class B is derived from class A, then the second method used for class A returns all objects of class A and all objects of class B, and the first method used for class A is looking for object with given identity in class A and then in class B. The same methods used for class B are only looking for objects of class B.

If the query is non-empty, the methods filling vectors of objects only return objects satisfying the query criteria. A query can be an OKS query string. It can be created by the OKS Data Editor or written by hand as described by the OKS documentation , e.g.: 

 (all ("Name" "my-object" =)) - search all objects of class T and it's subclasses which name is equal to "my-object"; 

 (this (and ("Address" 128 >=) ("Address" 256 <))) - search all objects of class T which address is equal or greater than 128 and less than 256; 

 (this ("Modules" all ("State" 0 =))) - search all objects of class T which has objects referenced via relationship "Modules" with attribute "State" set to 0.

C++ Example (using online dal package)

To read all applications via C++ dal provided by the online software one can write: 

#include <config/ConfigObject.h>
#include <config/Configuration.h>
#include <dal/Application.h>

try {
 ::Configuration db("");
 // 'objects' vector contains Applications and all objects from derived classes,
 // e.g. RunControlApplications, etc.
 std::vector<const dal::Application *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

To get only run control applications it is possible to use the following code: 

#include <dal/RunControlApplication.h>
try {
 ::Configuration db("");
 std::vector<const dal::RunControlApplication *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Note, to get a named object it is necessary to use template parameter explicitly and to write: 

const dal::Application * a = db.get<dal::Application>("my-application");

instead of 

const dal::Application * a = db.get("my-application"); // COMPILATION ERROR!

When the methods parameter init_children is set to true, all objects referenced by the retrieved objects are also read and initialized (i.e. values of their attributes are read from database and all referenced objects are also recursively read). Otherwise the referenced objects can only be pre-allocated (if they were not already read explicitly) and the actual reading will happen, when the user will apply a method to read values of their attributes or relationships.

When the methods parameter init_object is set to false, all retrieved objects are only pre-allocated without reading their attributes and relationships. The values of attributes and relationships will actually be read from database implementation, when the user will apply a method to read an attribute or relationship value.

The above two parameters can be used by the user to improve performance. For example, if the parameter init_children is set to false, the only objects which are really used by the user process will be read from the database. However in this case the database can not be closed (e.g. to free used resources) until the configuration data are used. Also, the actual read from database can happen at an unexpected moment, that can introduce undesired delays.

Java Example (online DAL)

To read all applications via Java dal provided by the online software one can write: 

import config.Configuration;
import dal.Application;
import dal.Application_Helper;
...
config.Configuration db = new config.Configuration(...);
try {
 dal.Application objs[] = dal.Application_Helper.get(db, new config.Query());
} catch ( config.NotFoundException ex ) {
 System.err.println("ERROR: bad query or no such class loaded");
} catch ( config.SystemException ex ) {
 System.err.println("ERROR: caught system exception");
}

To get only run control applications it is possible to write (try/catch statements are skipped): 

import dal.RunControlApplication;
import dal.RunControlApplication_Helper;
...
dal.RunControlApplication objs[] = dal.RunControlApplication_Helper.get(db, new config.Query());

Below there is an example of code to get an application by ID. Note, if object with such ID does not exist, config.NotFoundException exception is thrown. 

try {
 dal.Application obj = dal.Application_Helper.get(db, "RootController");
}
catch (config.NotFoundException e) {
 System.err.println( "ERROR: can not find application \'RootController\'" );
}

5.3. Reading Values of Attributes

Once the objects are retrieved, the user can get values of their attributes. A method to read attribute value is created for each attribute of each generated class. It has the following format: 

for C++: 

 type get_AttributeName() const - for single-value integer and float numbers; 

 const std::string& get_AttributeName() const - for single-value string-based attributes; 

 const std::vector<type>& get_AttributeName() const - for multi-value attributes; 

for Java: 

 type get_AttributeName() const - for single-value attributes; 

 type[] get_AttributeName() const - for multi-value attributes. 

Attribute Converters

The user can use one or several ways to convert values of all attributes of a C++ or Java type. To do this he/she needs to implement or to use already existing converter class, to create converter object of that class and to pass such object to the Configuration object using method Configuration::register_converter().

In case of C++ such class has to inherit from the template Configuration::AttributeConverter < T > class, where template parameter T defines type of attributes which values need to be converted and to implement virtual method Configuration::AttributeConverter::convert(), that performs the real conversion of attribute values.

Note:The C++ converter object is destroyed by the configuration destructor. User must not call delete on the attribute converter object.
In case of Java a converter class has to implement config.AttributeConverter interface defining two methods: the method convert() as in C++ and the method get_class(), which returns class of converted attributes.

Below there is C++ example of user functions converting string and integer attributes: 

#include <config/Configuration.h>

 // converter to replace by '_' a non-alpha-numeric symbol in db strings
class GoodString : public ::Configuration::AttributeConverter<std::string> {
public:
 static char cvt_symbol(char c) { return (isalnum(c) ? c : '_'); }
 void convert(std::string& s, const Configuration&, const ConfigObject&, const std::string&) {
 std::transform(s.begin(), s.end(), s.begin(), cvt_symbol);
 }
}
 // converter to make any long integer value positive
class PositiveInt : public ::Configuration::AttributeConverter<unsigned long> {
 void convert(unsigned long& i, const Configuration&, const ConfigObject&, const std::string&) {
 if(i < 0) i = -i;
 }
}
...
try {
 ::Configuration db("");
 db.register_converter(new GoodString());
 db.register_converter(new PositiveInt());
 ...
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In the Java an example of Java code is shown below: 

import config.Configuration;
import config.AttributeConverter;

 // converter removes leading and trailing whitespace from a string
public class TrimString implements config.AttributeConverter {
 public Object convert(Object s, config.Configuration db, config.ConfigObject obj, String attr_name) { return (Object)(s.trim()); }
 public Class get_class() { return String.class; }
}
...
config.Configuration db = new config.Configuration("");
db.register_converter(new TrimString());

Online DAL Converters

The core TDAQ C++ DAL (libdaq-core-dal.so) provides converter daq::core::SubstituteVariables class to substitute configuration parameters in values of string attributes. It's constructor requires Configuration object and Partition object, since they are used to calculate conversion map. In case, if configuration database is reloaded, such parameters have to be reset using reset() method. An example of the C++ code is shown below: 

#include <config/Configuration.h>
#include "dal/Partition.h"
#include <dal/util.h>

try {
 ::Configuration db("");
 if(const daq::core::Partition * p = daq::core::get_partition(db, "partition-X")) {
 db.register_converter(new daq::core::SubstituteVariables(db, *p));
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Similar Java dal.jar provides attribute converter in the same way. An example of it's usage is shown below: 

import config.Configuration;
import config.DalObject;
import dal.SubstituteVariables;
import dal.Partition;

config.Configuration db = new config.Configuration("");
dal.Partition p = dal.Algorithms.get_partition(db, "partition-X");
if(p != null) {
 db.register_converter(new dal.SubstituteVariables(db, p));
}

5.4. Reading Values of Relationships

Once an object is retrieved, the user can get objects referenced by it. A method is created for each relationship of each generated class. It has the following format: 

for C++: 

 const class-type * get_RelationshipName() const - for single-value relationships; 

 const std::vector<const class-type*>& get_RelationshipName() const - for multi-value relationships; 

for Java: 

 class-type get_RelationshipName() const - for single-value relationships; 

 class-type[] get_RelationshipName() const - for multi-value relationships. 

5.5. Cast Class Types

There are situations when user may need to cast an object from one class to a derived one. To make a down cast for an object of generated class the user should to use the methods of the configuration classes and never use cast supported by the programming languages.

C++ cast

There are situations when some set of objects can belong to different classes, e.g. objects can be of class A or B which is derived from class A. For a down cast the Configuration::cast() method must be used. As an example, the code to try and to cast from application to run-control application type is shown below: 

try {
 ::Configuration db;
 // some code to get the vector of applications
 const std::vector<const dal::Application*>& l = ...;
 std::vector<const dal::Application*>::const_iterator j = l.begin();
 for(; j != l.end(); ++j) {
 if(const dal::RunControlApplication * r = db.cast<dal::RunControlApplication>(*j)) {
 std::cout << "application " << r << " is run control application" << std::endl; 
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Java cast

To down cast an object of generated Java DAL use aproapriate cast() method in generated class. For example, some object of application class can be down casted to the run control application: 

config.Configuration db(...);
dal.Application a = ...; // some code to get application
dal.RunControlApplication rc_application = dal.RunControlApplication_Helper.cast(db, a);
if(rc_application != null) { ... }

5.6. Data Destruction

In C++ the object of the Configuration class should not be destroyed while the DAL is in use. All objects read via template methods are destroyed by the Configuration class destructor. The user must never try to modify or to destroy such objects himself.

6. How to create and to modify data

This section explains how to create a new database file, how to create or remove database data and how to modify existing data.

Any modifications described by this section becomes persistent and visible to others processes only after successful commit operation. If the modification should not be committed (e.g. a modification failed), it is necessary to execute abort operation, e.g. in C++: 

try {
 ::Configuration db();
 bool success = true;
 ... // some code which makes changes and sets the variable to false if failed
 if(success) {
 std::cout << "commit changes\n";
 db.commit(); // one also check return status, true means success
 }
 else {
 std::cerr << "ERROR: something was wrong, abort changes\n";
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Below there is the same example for Java: 

config.Configuration db = new config.Configuration(...);
... // some code to makes changes and sets the success variable to false if failed
if(success) {
 System.out.println("commit changes");
 db.commit();
}
else {
 System.err.println("ERROR: something was wrong, abort changes");
 db.abort();
}

To modify or to destroy an object using generated C++ DAL methods described below, it is necessary to have a non-const pointer or reference on the object. However all generated DAL methods return objects as const. To make a change it is necessary to use C++ const_cast to get non-const pointer or reference.

6.1. Creation of new database file

To create a new database file using C++ it is necessary to build an object of the Configuration class only providing name of implementation plug-in: 

::Configuration db("oksconfig");

Similar code for Java is below: 

config.Configuration db = new config.Configuration("rdbconfig"); // no db file

To create a new database data file it is necessary to decide which schema (at least one schema is always required) and optionally others database files will be used. Then it is necessary to provide an absolute name for newly created database file (the user should have write permission or the rdb server must be run in read-write mode under account which has such rights). If rdb implementation is used, it is also necessary to provide server and optionally partition name. After this it is necessary to use create method of the Configuration class and check it's return status.

Below there is example for C++ and oks implementation: 

try {
 ::Configuration db("oksconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 if(db.create("", db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For rdb implementation it is similar, but requires rdb server and optionally partition's names: 

try {
 ::Configuration db("rdbconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 const char * server_name = "foo::bar"; // server with name bar running in part. foo
 if(db.create(server_name, db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << " on " << server_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java an example with rdb implementation is shown below: 

try {
 config.Configuration db = new config.Configuration("rdbconfig");
 String[] includes = new String[2];
 includes[0] = "online/schema/online.schema.xml"; // common schema
 includes[1] = "online/segments/setup.data.xml"; // online infrastructure
 db.create("foo::bar", "/tmp/my-partition.data.xml", includes);
 db.commit();
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
}
catch(config.NotAllowedException ex) {
 System.err.println("ERROR: caught \'config.NotAllowed\' exception");
}
... // catch config.AlreadyExistsException in a similar way

The included files should exist in advance and be defined either as an absolute path or as a relative path to a token of the TDAQ_DB_PATH variable value.

6.2. Database Includes

There are methods in C++ class Configuration to add a new include, to remove an existing include or to get list of includes for given database. They are: 

 bool Configuration::add_include(const std::string& db_name, const std::string& include) - adds include to the database db_name and returns true in case of success or false if failed; 

 bool Configuration::remove_include(const std::string& db_name, const std::string& include) - removes an existing include from the database db_name and returns true in case of success or false if failed; 

 bool Configuration::get_includes(const std::string& db_name, std::list<std::string>& includes) const - fills list of includes by files which are included by the db_name and returns true in case of success or false if failed.

Similar methods in Java class config.Configuration are: 

 void add_include(String db_name, String include) - adds include to the database db_name or throws exception if failed; 

 void remove_include(String db_name, String include) - removes an existing include from the database db_name or throws exception if failed; 

 void get_includes(String db_name, String[] includes) - fills array of includes by files which are included by the db_name or throws exception if failed.

6.3. Objects Manipulations

This subsection explains how to create and how to destroy database objects.

Objects Creation

To create a new object using generated C++ DAL there are two Configuration template methods: 

 const T * Configuration::create(const std::string& at, const std::string& id, bool) - to create new object of class T with identity id at existing database file with name at; 

 const T * Configuration::create(const ::DalObject& at, const std::string& id, bool) - to create new object of class T with identity id at a database file where object at is stored.

The methods return non-null pointer in case of success or null if failed. The second method is faster since time to search the database file where to put new object is much smaller.

When the init_object parameter is set to false, then the values of attributes and relationships are not read from implementation (for a newly created object they are set to default values in accordance with the database schema).

An example how to create two new objects of the online dal::Computer class is shown below: 

try {
 ::Configuration db(...);
 const char * dbfile = "/tmp/my-db.data.xml";
 const dal::Computer * host = db.create<dal::Computer>(dbfile, "host-1");
 if(host == 0) {
 std::cerr << "ERROR: failed to create object \'host-1\' at \'" << dbfile << "\'\n";
 }
 else {
 if(db.create<dal::Computer>(*host, "host-2") == 0) {
 std::cerr << "ERROR: failed to create object \'host-2\' at file of " << host;
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

On Java similar methods are genereted in the helper classes. For class T two methods are available: 

 T create(config.Configuration db, String at, String id) - to create new object of class T with identity id at existing database file with name at; 

 T create(config.Configuration db, config.DalObject at, String id) - to create new object of class T with identity id at a database file where object at is stored.

The example to create online segment and it's application is shown below:: 

config.Configuration db = new ...
String db_file = "/tmp/my-db.data.xml";
try {
 dal.Segment s = dal.Segment_Helper.create(db, db_file, "my segment");
 dal.Application a = dal.Application_Helper.create(db, s, "my application");
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
} ... // also other exceptions to be caught

Objects Destruction

To destroy an existing object there is template method in the C++ Configuration class bool destroy(T& obj). It returns true in case of success and false if failed. See example: 

try {
 ::Configuration db(...);
 dal::Computer * host = ...; // some code to get pointer
 db.destroy(*host);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In Java the method void destroy(config.Configuration db) is generated in T.java, e.g.: 

config.Configuration db = new ...;
dal.Computer host = ...; // some code to get object
try {
 host.destroy(db);
}
catch(config.SystemException ex) {
 System.err.println("ERROR: failed to destroy " + host);
} ... // also other exceptions to be caught

6.4. Modification Values of Attributes

Once the objects are retrieved or created, the user can modify values of their attributes. A method to set attribute value is created for each attribute of each generated class. The mapping between C++/Java types and OKS types can be seen in the 3.1. Mapping Between OKS Attribute Types and Programming Languages Types section.

In C++ such method throws daq::config::Exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(const std::vector<type>& value) - for multi-value attribute.

In Java such method throws an exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(type[] value) - for multi-value attribute.

6.5. Modification Values of Relationships

Once the objects are retrieved or created, the user can modify values of their relationships. A method to set relationship value is created for each relationship of each generated class.

For C++ it has the following format and throws daq::config::Exception if failed: 

 void set_RelationshipName(const class-type * value) - for single-value relationships; 

 void set_RelationshipName(const std::vector<const class-type*>& value) - for multi-value relationships.

For Java it has the following format and throws an exception if failed: 

 void set_RelationshipName(class-type value) - for single-value relationships; 

 void set_RelationshipName(class-type[] value) - for multi-value relationships.

7. Notification mechanism

The user application can be notified on changes of the configuration data. To do this user should to implement one or many callback functions (C++) or classes (Java) which will be used when the database changes are committed and to choose which changes in classes and objects should be reported (i.e. to define the subscription criteria ).

The user receives description of information changes in one go via callbacks invoked after commit of database changes. This is more preferred way than individual callback per object or per class since user may want to see all changes at single point. Each callback receives own list of changes in accordance with it's subscription criteria.

The changes are reported as a collection of changes per DAL class. A change per class contains 4 parameters: the class name and the identities of created, modified and removed objects.

To make a subscription it is necessary to make three steps: 

implement callback, 

define subscription criteria, 

invoke subscribe method with above entities on the configuration object.

7.1. User Callback

To start with any subscription on database changes the user must to implement at least one Configuration::notify callback function in C++ or config.Callback interface on Java. Below there are details for C++ and Java subscriptions.

C++ callback function

The user has to implement Configuration::notify callback. It has the following parameters: 

 const std::vector<::ConfigurationChange *> & changes - description of changes 

 void * parameter - user parameter

The ConfigurationChange class is declared in the config/Change.h file and has 4 methods to get name of the class and vectors of created, modified and removed object identities. An example of callback functions is shown below: 

void callback(const std::vector< ConfigurationChange *> & changes, void *)
{
 std::cout << "The CALLBACK reports all changes:\n";

 // iterate changes sorted by classes
 for(std::vector<ConfigurationChange *>::const_iterator j = changes.begin(); j != changes.end(); ++j) {

 // print class name
 std::cout << "- there are changes in class \"" << (*j)->get_class_name() << "\"\n";

 std::vector<std::string>::const_iterator i;

 // print modified objects
 for(i = (*j)->get_modified_objs().begin(); i != (*j)->get_modified_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was modified\n";
 }

 // print removed objects
 for(i = (*j)->get_removed_objs().begin(); i != (*j)->get_removed_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was removed\n";
 }

 // print created objects
 for(i = (*j)->get_created_objs().begin(); i != (*j)->get_created_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was created\n";
 }
 }
}

Java callback interface

The user has to create a class implementing the config.Callback interface. It requires to implement method void process_changes(config.Change[] changes, java.lang.Object parameter). Example below illustrates how to implement notification callback: 

class TestCallback implements config.Callback {
 private config.Configuration db;

 public TestCallback(config.Configuration d) { db = d; }

 public void process_changes(config.Change[] changes, java.lang.Object parameter) {

 // the parameter can be any; as an example, the callback ID is passed as string
 String cb_id = (String)parameter;

 // print out changes description
 System.out.println("[TestCallback " + cb_id + "] got changes:");
 config.Change.print(changes, " ");

 // iterate changes by classes
 for(int i = 0; i < changes.length; i++) {
 config.Change change = changes[i];
 System.out.println("* there are changes in the \'" + change.get_class_name() + "\' class");

 // just as example, look for changed objects of the Application class
 if((change.get_class_name().equals("Application") == true) && (change.get_changed_objects() != null)) {
 System.out.println("* " + change.get_changed_objects().length + " updated objects of the Application class");

 // iterate by all changed objects and print them out
 for(int j = 0; j < change.get_changed_objects().length; ++j) {
 dal.Application a = dal.Application_Helper.get(db, change.get_changed_objects()[j]);

 // an example of correct down cast
 if(a.class_name().equals("RunControlApplication")) {
 dal.RunControlApplication_Helper.get(db, a.config_object()).print(" "); // print as RC application
 }
 else {
 a.print(" "); // print as an application
 }
 }
 }
 }
 }
}

7.2. Subscription criteria

The subscription criteria is an object of ConfigurationSubscriptionCriteria class in C++ or config.Subscription class in Java. It is used to define lists of classes and objects, which changes will be monitored and reposted to user. If user provides no any class or object, it means subscription on any change and a database modification is reported.

Subscription on any changes in class

The notification callback is invoked for any changes of class objects including creation of new objects, removing or modification of existing objects.

In C++ to subscribe on any changes in some class the user should to use ConfigurationSubscriptionCriteria::add(const std::string&) method. For a class generated by genconfig the s_class_name attribute can be used, e.g. to subscribe on changes in class dal::Application: 

::ConfigurationSubscriptionCriteria c;
c.add(dal::Application::s_class_name);

In Java method config.Subscription.add(String class_name) should be used, e.g. to subscribe on changes in class Application it is necessary to write the following code: 

config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add("Application");

Subscription on object changes

When subscription on object changes has done, the notification callback is invoked for any changes of the objects or it's removing.

In C++ to subscribe on object changes notification the user should to use ConfigurationSubscriptionCriteria::add(const ::DalObject&), e.g. to subscribe on changes of an object of the Application class: 

::ConfigurationSubscriptionCriteria c;
const dal::Application * app_obj;
c->add(*app_obj);

In Java config.add(DalObject obj) method to be used, e.g.: 

dal.Application app = ...; // some code to get application object
config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add(app);

7.3. Subscription

To make the actual subscription it is necessary to have a notification callback been implemented and a subscription criteria object. The the method subscribe() to be invoked on the configuration object. For C++ an example is shown below: 

 // user-defined callback
void cb(const std::vector<ConfigurationChange *> & changes, void * p) { ... }

try {
 // configuration object
 ::Configuration db(...);

 // subscription criteria object
 ::ConfigurationSubscriptionCriteria c;
 c.add(dal::Application::s_class_name);

 // subscription; if database is changed, the cb can be invoked after this line
 ::CallbackId id = db.subscribe(c, cb);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java above example looks like: 

 // user-defined callback
class MyCallback implements config.Callback { ... }

 // configuration object
config.Configuration db = new config.Configuration(...);

 // subscription criteria object
config.Subscription c = new config.Subscription(new MyCallback(db), null);
c.add("Application");

 // subscription; MyCallback::process_changes() can be invoked after this line
db.subscribe(c);

The method unsubscribe() can be used to remove subscription set above. In case of C++ it's parameter is a return value of the subscribe() method (i.e. CallbackId value). For Java it's parameter is the subscription object used as parameter of subscribe() method.

8. Algorithms

By default, the generated classes have one-to-one mapping to database schema and DAL objects directly correspond to the database objects. If user wants to add more algorithms on top of the generated DAL without modification of DAL code by hand, he has possibility to define algorithms on top of the OKS class methods.

When a class method is created, user can add it's implementation for different programming languages. To be taken into account by genconfig, user have to provide C++ and/or Java implementation. Then he has two possibilities: 

declare method prototype, write method implementation in the separate file and add such file when build DAL; 

declare method prototype and write it's implementation in OKS.

The first way is more flexible, but requires more steps when build library. The second way does not require any additional steps when build library, but will require schema modifications to any method's implementation modification.

The online DAL defines several algorithms (e.g. to find partition, get all applications, to calculate application environment, etc.) and uses first way to implement algorithms. More information can be found in the online dal package. 

 All Data Structures Namespaces Files Functions Variables Typedefs Enumerations Enumerator Friends Defines

Generated on Fri Nov 18 2011 10:10:26 for TDAQ release tdaq-04-00-00 by 

 1.7.2
```

### Snapshot `doxygen__ConfigPackages-tdaq-04-00-01__20120224154520.html`
*Local file: `output/extracts/pcatd12/doxygen__ConfigPackages-tdaq-04-00-01__20120224154520.html`*

```text
TDAQ release tdaq-04-00-01: Config Packages

 Main Page

 Related Pages

 Modules

 Namespaces

 Data Structures

 Files

 Examples

Config Packages 

The goal of the config package is to provide user-friendly API to access data from the configuration database.

There are two layers of such API which can be seen by user:

abstract config layer working with arbitrary database schema and hiding details of DBMS implementation

data access library (DAL), that is generated for given database schema to map it on programming language data types

This page describes basics which a user should know to generate DAL from the database schema, to get data from database, to receive notification on their change, to create new data or to modify existing data using generated DAL.

1. Development of the configuration database schema 

2. Generation of the DAL 

2.1. Parameters of genconfig utility 

2.2. Integration with CMT 

3. DAL classes and methods 

3.1. Mapping Between OKS Attribute Types and Programming Languages Types 

4. Errors Handling 

5. How to get data 

5.1. Initialisation 

5.2. Read objects of class 

5.3. Reading Values of Attributes 

5.4. Reading Values of Relationships 

5.5. Cast Class Types 

5.6. Data Destruction 

6. How to create and to modify data 

6.1. Creation of new database file 

6.2. Database Includes 

6.3. Objects Manipulations 

6.4. Modification Values of Attributes 

6.5. Modification Values of Relationships 

6.6. Modification of Database and Invalid Objects 

7. Notification mechanism 

7.1. User Callback 

7.2. Subscription criteria 

7.3. Subscription 

8. Algorithms

Sections 1, 2 and 3 are needed for those, who develops own schema and wants to generate DAL. Section 4 explain basics of error handling to be known by any user of DAL. Section 5 explain how to get data using DAL. Section 6 explains how to create or to modify data using DAL. Section 7 explains how to receive notification in case of data changes. The possibility to plug-in user algorithms to the generated DAL is described in section 8.

1. Development of the configuration database schema

The user may to develop own schema in case he needs to describe own configuration data which can not be described by existing schemes. The development of the schema can be done using OKS Schema Editor. The user has the choice to extend the existing schemes or to develop his own schema from scratch. If user wants to extend existing schema, first he needs to run the editor with existing schemes (which he can not modify) and to create the schema he will be the owner of, e.g.:

oks_schema_editor dal/schema/core.schema.xml

The editor window with loaded schema will appear. Then the user can create his own schema and define his own classes. If user wants to create new schema from scratch, he just needs to run the editor without parameters and to create a new schema. For more information on the OKS schema editor, the OKS schema capabilities and exporting schema into different formats see OKS documentation [6]. After the user finish with his schema development, he needs to save the schema into xml file and add it to the sources of his package. Such schema file will be used for the database data access library generation described by next section.

2. Generation of the DAL

A DAL is generated by the genconfig utility. It uses OKS schema files as input and produces: 

C++ source files to build the library 

C++ header files to describe library interface 

C++ files to build binaries dumping content of the database 

Java files to build jar file 

genconfig.info file containing information about names of generated classes, the C++ code namespace, include prefix directory and java package name

2.1. Parameters of genconfig utility

The command line parameters of genconfig utility are listed below: 

genconfig [-d | --C++-dir-name directory-name]
 [-n | --C++-namespace namespace
 [-i | --C++-headers-dir directory-prefix]
 [-j | --java-dir-name directory-name]
 [-p | --java-package-name package-name]
 [-I | --include-dirs dirs*]
 [-c | --classes class*]
 [-D | --user-defined-classes [namespace::]user-class[@dir-pefix]*]
 [-f | --info-file-name file-name]
 [-v | --verbose]
 [-h | --help]
 -s | --schema-files file.schema.xml+

Options/Arguments:
 -d directory-name name of firectory for C++ header and implementation files
 -n namespace namespace for C++ classes
 -i directory-prefix name of directory prefix for C++ header files
 -j directory-name name of directory for java files
 -p package-name package name for java files
 -I dirs* directories where to search for already generated files
 -c class* explicit list of classes to be generated
 -D [x::]c[@d]* user-defined classes
 -f filename name of output file describing generated files
 -v switch on verbose output
 -h this message
 -s files+ the schema files (at least one is mandatory)

To generate a DAL user has to provide name of the schema file. By default the DAL is generated for all classes contained in the schema files, otherwise user should provide names of required classes via --classes parameter. It is recommended to use unique namespace for each generated DAL to avoid possible problems when several DALs are used by one application.

It is possible to reuse already generated DALs. In this case the user should to provide a list of directories containing information about already generated DALs via --include-dirs parameter, to provide list of his schema files and optionally to provide list of names of classes to be generated. It is expected such schema files use include statement for base schema files. The DAL is generated only for classes contained in the explicitly mentioned schema files, the classes from included files are ignored.

2.2. Integration with CMT

The genconfig package provides CMT fragment. To generate all classes from given schema file a user should write in the requirement file: 

use genconfig
document generate-config my-dal -s=.. \
 namespace="my-ns" \
 include="my-include" \
 packagename="my-java-package" \
 some-path/my.schema.xml

This will produce C++ files for user schema file, which will be placed in several directories (relative to the root of user package) in accordance with their types: 

C++ library source files are placed into "$(bin)my-dal.tmp" directory, 

C++ header files are placed into "$(bin)$(include-dir-name)" directory, 

the C++ source files for dump binaries are placed into "$(bin)my-dal.tmp/dump" directory, 

the java files are placed into "$(bin)my-dal.tmp/$(java-package-name)" directory.

For our example to build C++ library put into cmt/requirements file: 

library mydal $(lib_opts) $(bin)my-dal.tmp/*.cpp

To build java jar file put into cmt/requirements file: 

apply_pattern build_jar name=my-dal src_dir="$(bin)my-dal.tmp/my-java-package" sources=*.java

Finally, to build dump binaries from C++ generated files put into cmt/requirements file: 

use config
application my_dump -no_prototypes "$(bin)my-dal.tmp/dump/dump_my_ns.cpp"
macro my_dump_okslinkopts "-lmy-dal -lconfig"

Note, the order of generation of files, library and binary builds is important: 

put into cmt/requirements file dependecy of application from generated library macro my_dump_dependencies my-dal

to allow parallel build using gmake -jN option modify your cmt/Makefile: include $(CMTROOT)/src/Makefile.header
$(bin)my-dal.make $(bin)my_dump.make:: $(bin)generate-dal.stamp
include $(CMTROOT)/src/constituents.make

To be used by other packages the library, the jar file and generated header files have to be installed. There is no need to install or even to add to the user package' sources generated C++ and Java files. The C++ and Java DAL to be installed as a normal library and jar file. To install C++ header files in platform-independent directory put into requirement file: 

ignore_pattern install_headers_bin_auto
apply_pattern install_headers src_dir="$(bin)my-dal" files=*.h

If it is necessary to produce the DAL for a subset of classes defined by the schema files, the user have to define macro generate-config-classes containing space-separated list of classes: 

macro generate-config-classes "MyClass1 MyClass2 MyClass3"

If the DAL uses other existing DALs, the user have to define macro generate-config-include-dirs containing space-separated list of directories with installed headers of such DALs, e.g.: 

macro generate-config-include-dirs "${HOME1}/share/data/dal1 \
 ${HOME2}/share/data/dal2"

It is possible to change default locations for generated C++ and Java files using generate-config document options: 

cppdir option changes default directory for generated C++ files (i.e. "my-dal.tmp" for above example); the result files will be in the "$(bin)$(cppdir)" 

javadir option changes default directory for generated Java files (i.e. "my-dal.tmp/my-java-package" for above example); the result files will be in the "$(bin)$(javadir)/$(package)"; if containes dots (e.g. package="daq.core"), they will be substituted by slashes (i.e. Java files will be generated in /daq/core directory).

It is possible to use nested namespace for generated C++ classes. To separate namespaces use double colon signs in the namespace option of the generate-config document, e.g.: 

document generate-config my-dal -s=.. namespace="daq::core" ...

 will produce classes in nested namespaces daq and core, i.e.: 

namespace daq {
 namespace core {
 ...
 }
}

3. DAL classes and methods

For each OKS class appropriate DAL classes are generated: 

in case of C++ the generated class has the same name as OKS one and is declared inside namespace defined by the user; there is separate header file per each class; it has the same name as the database class and, to be included, it may have directory prefix, defined by user; if a class is derived from other classes, an appropriate C++ inheritance is used; 

in case of Java there is interface which has the same name as the database class declared inside package with name provided by the user; the interface implementation is in the class with suffix _Impl; the static methods to get existent or to create new objects of the class are in the class with suffix _Helper; an appropriate inheritance is used between interfaces.

For each direct attribute and relationship defined for OKS class the appropriate methods are generated. Such methods have the same names as the names of the attributes and the relationships in the database with get_ and set_ prefixes. The database attribute types are mapped to appropriate C++ and Java types. The multi-value attributes are mapped to std::vector of attribute type in C++ and to array of attribute type in Java. The database relationships are mapped to methods returning pointer or std::vector of pointers to objects of referenced class in C++ and similarly an object or array of objects in Java.

Additionally, for each class there are methods to get object's class name and object identity as they are defined in the database.

For C++ two std::ostream operators are generated for each class: 

the one with const reference to object prints out the full description of the object, and 

the other one with const pointer to object prints out the object's class name and identity.

In Java for each class there is generated method print() which prints out full description of the object.

When DAL is generated, any non-alphanumeric characters appeared in the names of classes, attributes, relationships and methods are replaced by underscore symbol, e.g. database attribute "# of c++ lines" will appear in DAL as "__of_c___lines".

3.1. Mapping Between OKS Attribute Types and Programming Languages Types

Below there is map between OKS attribute types and C++/Java types: 

 | OKS Type | C++ type | Java type 

 | bool | bool | boolean 

 | s8 (8-bits signed integer) | int8_t | char 

 | u8 (8-bits unsigned integer) | uint8_t | byte 

 | s16 (16-bits signed integer) | int16_t | short 

 | u16 (16-bits unsigned integer) | uint16_t | short 

 | s32 (32-bits signed integer) | int32_t | int 

 | u32 (32-bits unsigned integer) | uint32_t | int

 | s64 (64-bits signed integer) | int64_t | long 

 | u64 (64-bits unsigned integer) | uint64_t | long 

 | float | float | float 

 | double | double | double 

 | date | std::string | java.lang.String 

 | time | std::string | java.lang.String 

 | string | std::string | java.lang.String 

 | enum | std::string | java.lang.String 

 | class | std::string | java.lang.String 

In C++ the complex values (strings and vectors) are passed by const reference and not by value.s

4. Errors Handling

Methods of C++ and Java config classes throw exceptions in case of errors.

Each C++ method has explicit exception specification. The following exceptions can be thrown:

daq::config::Generic is used to report most of the problems (bad DB, wrong parameter, plug-in specific, etc.)

daq::config::NotFound the config object accessed by ID is not found, class accessed by name is not found

daq::config::DeletedObject accessing template object that has been deleted (via notification or by the user's code)

All above exceptions have common class daq::config::Exception, that can be used to catch all of them. 

try {
 // load database using oks file /tmp/mydb.data.xml
 Configuration db("oksconfig:/tmp/mydb.data.xml");

 ... // user's code working with db
}
catch (daq::config::Exception & ex) {
 // throw some user-defined exception in case of config exception
 throw ers::error(user::exception(ERS_HERE, "cannot read config", ex));
}

5. How to get data

The entry point to get data from database is the class Configuration defined in global namespace in C++ and in the config package in Java. Below it is described how to create an object of this class and how to use it to get the database information.

5.1. Initialisation

The Configuration constructors in both Java and C++ languages have single string parameter. If the parameter is an empty string, the constructor will use value of the TDAQ_DB environment variable. In case if both the constructor parameter and the environment variable are not set, or empty, then the configuration constructor throws daq::config::Generic in case of C++, or config.SystemException is thrown in case of Java.

The format of the parameter is "name-of-plugin:plugin-parameters". The plug-in's parameter is optional. If it is non-empty, it is passed to the implementation plug-in constructor.

In C++ the name of plug-in is converted into name of the shared library by adding prefix lib and suffix .so, e.g. "oksconfig" plug-in name is converted into "liboksconfig.so". The shared library must be in the path to shared libraries, e.g. in the LD_LIBRARY_PATH environment variable.

In Java the name of plug-in is converted into name of the class in package "plugin-name" with name created from "plugin-name", where 1-st and 4-th characters are converted to upper case and "uration" string is appended (it is so by historical reasons), e.g. "oksconfig" plug-in name is converted into "oksconfig.OksConfiguration". The CLASSPATH variable has to point to such class or jar file. For the moment two implementation plug-ins are available: 

the oksconfig using OKS implementation directly (i.e. reads XML files), and 

the rdbconfig accessing OKS with RDB server.

Details of initialization in C++ and examples

Below there are examples of the Configuration constructor explicit parameters: 

#include "config/Configuration.h"

try {
 // example (1): load daq/partitions/be_test.data.xml file using oks
 ::Configuration db1("oksconfig:daq/partitions/be_test.data.xml");

 // example (2): connect with server RDB using rdb implementation (in initial partition)
 ::Configuration db2("rdbconfig:RDB");

 // example (2a): connect with server RDB using rdb implementation (in test partition)
 ::Configuration db2a("rdbconfig:test::RDB");

 // example (2b): same as above using new style server-name@partition-name
 ::Configuration db2b("rdbconfig:RDB@test");

 // example (3): use oks implementation and create new database
 ::Configuration db3("oksconfig");
 db3.create("", "/tmp/my.data.xml", std::list<std::string>(1,"/tmp/my.sch.xml"));

 // example (4): use rdb implementation and create new database
 // on server RDB running in partition test
 ::Configuration db4("rdbconfig");
 db4.create("test::RDB", "/tmp/my.data.xml", std::list<std::string>());
}
catch(daq::config::Exception& ex) {
 std::cerr << "ERROR: " << ex << std::endl;
}

The recommended way is to get plug-in and it's parameter via environment variable. Most of the user's code for applications run by TDAQ's setup should to leave the parameter empty: 

#include "config/Configuration.h"

int main() {
 try {
 ::Configuration db("");
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

In case it the parameter can be also passed via command line, use it as shown below: 

#include "config/Configuration.h"

int main(int argc, char *argv[]) {
 try {
 ::Configuration db(argv[1]);
 ERS_DEBUG( 1 , "Read database " << db.get_impl_spec())
 db.get(...) // any user's code working with Configuration object
 }
 catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
 }
}

Note, to get proper plug-in name and parameter used for configuration initialization (e.g. obtained via TDAQ_DB), use get_impl_spec() method of Configuration class, which is used in above examples for debug reporting.

Initialization in Java

The Configuration constructor parameters are the same, as in case of C++. In case of problems the exception is thrown. An example is shown below: 

import config.Configuration;

try {
 config.Configuration db = new config.Configuration("rdbconfig:RDB");
}
catch (config.SystemException ex) {
 System.err.println( "ERROR caught \'config.SystemException\':");
 System.err.println( "*** " + ex.getMessage() + " ***" );
}

Note in case when rdb implementation is used, the partition name of the RDB server can be specified by several ways: 

using the same approach as for C++, i.e. via constructor parameter using double colon-separated partition and server names, e.g. "rdbconfig:partition-name::server-server" or "rdbconfig:server-server@partition-name"; 

via tdaq.ipc.partition.name java virtual machine property, e.g. run java application with "-Dtdaq.ipc.partition.name=partition-name".

5.2. Read objects of class

Once an object of the Configuration class is successfully created, it can be used to get configuration data (i.e. objects). Normally to get configuration objects only C++ template methods of the Configuration class and generated Java code should be used. The usage of config layer (i.e. direct usage of objects of ConfigObject class) only makes sense in few packages working with arbitrary database schemes.

For each generated class T two methods can be applied using configuration object: 

C++ template methods of the Configuration class: 

 const T * Configuration::get(const std::string&, bool, bool, unsigned long, const std::vector<std::string> *) - to read named object; 

 void Configuration::get(std::vector<const T*>&, bool, bool, const std::string&, unsigned long rlevel, const std::vector<std::string> *) - to read objects of class; 

Java methods generated in class T_Helper: 

static public T get(config.Configuration db, String id) to read named object 

static public T[] gets(config.Configuration db, Query query) to read objects of class 

The methods looking for single object by identity and methods looking for objects of class in case if the query string is empty are searching objects in the class and all it's subclasses, e.g. if class B is derived from class A, then the second method used for class A returns all objects of class A and all objects of class B, and the first method used for class A is looking for object with given identity in class A and then in class B. The same methods used for class B are only looking for objects of class B.

If the query is non-empty, the methods filling vectors of objects only return objects satisfying the query criteria. A query can be an OKS query string. It can be created by the OKS Data Editor or written by hand as described by the OKS documentation , e.g.: 

 (all ("Name" "my-object" =)) - search all objects of class T and it's subclasses which name is equal to "my-object"; 

 (this (and ("Address" 128 >=) ("Address" 256 <))) - search all objects of class T which address is equal or greater than 128 and less than 256; 

 (this ("Modules" all ("State" 0 =))) - search all objects of class T which has objects referenced via relationship "Modules" with attribute "State" set to 0.

C++ Example (using online dal package)

To read all applications via C++ dal provided by the online software one can write: 

#include <config/ConfigObject.h>
#include <config/Configuration.h>
#include <dal/Application.h>

try {
 ::Configuration db("");
 // 'objects' vector contains Applications and all objects from derived classes,
 // e.g. RunControlApplications, etc.
 std::vector<const dal::Application *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

To get only run control applications it is possible to use the following code: 

#include <dal/RunControlApplication.h>
try {
 ::Configuration db("");
 std::vector<const dal::RunControlApplication *> objects;
 db.get(objects);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Note, to get a named object it is necessary to use template parameter explicitly and to write: 

const dal::Application * a = db.get<dal::Application>("my-application");

instead of 

const dal::Application * a = db.get("my-application"); // COMPILATION ERROR!

When the methods parameter init_children is set to true, all objects referenced by the retrieved objects are also read and initialized (i.e. values of their attributes are read from database and all referenced objects are also recursively read). Otherwise the referenced objects can only be pre-allocated (if they were not already read explicitly) and the actual reading will happen, when the user will apply a method to read values of their attributes or relationships.

When the methods parameter init_object is set to false, all retrieved objects are only pre-allocated without reading their attributes and relationships. The values of attributes and relationships will actually be read from database implementation, when the user will apply a method to read an attribute or relationship value.

The above two parameters can be used by the user to improve performance. For example, if the parameter init_children is set to false, the only objects which are really used by the user process will be read from the database. However in this case the database can not be closed (e.g. to free used resources) until the configuration data are used. Also, the actual read from database can happen at an unexpected moment, that can introduce undesired delays.

Java Example (online DAL)

To read all applications via Java dal provided by the online software one can write: 

import config.Configuration;
import dal.Application;
import dal.Application_Helper;
...
config.Configuration db = new config.Configuration(...);
try {
 dal.Application objs[] = dal.Application_Helper.get(db, new config.Query());
} catch ( config.NotFoundException ex ) {
 System.err.println("ERROR: bad query or no such class loaded");
} catch ( config.SystemException ex ) {
 System.err.println("ERROR: caught system exception");
}

To get only run control applications it is possible to write (try/catch statements are skipped): 

import dal.RunControlApplication;
import dal.RunControlApplication_Helper;
...
dal.RunControlApplication objs[] = dal.RunControlApplication_Helper.get(db, new config.Query());

Below there is an example of code to get an application by ID. Note, if object with such ID does not exist, config.NotFoundException exception is thrown. 

try {
 dal.Application obj = dal.Application_Helper.get(db, "RootController");
}
catch (config.NotFoundException e) {
 System.err.println( "ERROR: can not find application \'RootController\'" );
}

5.3. Reading Values of Attributes

Once the objects are retrieved, the user can get values of their attributes. A method to read attribute value is created for each attribute of each generated class. It has the following format: 

for C++: 

 type get_AttributeName() const - for single-value integer and float numbers; 

 const std::string& get_AttributeName() const - for single-value string-based attributes; 

 const std::vector<type>& get_AttributeName() const - for multi-value attributes; 

for Java: 

 type get_AttributeName() const - for single-value attributes; 

 type[] get_AttributeName() const - for multi-value attributes. 

Attribute Converters

The user can use one or several ways to convert values of all attributes of a C++ or Java type. To do this he/she needs to implement or to use already existing converter class, to create converter object of that class and to pass such object to the Configuration object using method Configuration::register_converter().

In case of C++ such class has to inherit from the template Configuration::AttributeConverter < T > class, where template parameter T defines type of attributes which values need to be converted and to implement virtual method Configuration::AttributeConverter::convert(), that performs the real conversion of attribute values.

Note:The C++ converter object is destroyed by the configuration destructor. User must not call delete on the attribute converter object.
In case of Java a converter class has to implement config.AttributeConverter interface defining two methods: the method convert() as in C++ and the method get_class(), which returns class of converted attributes.

Below there is C++ example of user functions converting string and integer attributes: 

#include <config/Configuration.h>

 // converter to replace by '_' a non-alpha-numeric symbol in db strings
class GoodString : public ::Configuration::AttributeConverter<std::string> {
public:
 static char cvt_symbol(char c) { return (isalnum(c) ? c : '_'); }
 void convert(std::string& s, const Configuration&, const ConfigObject&, const std::string&) {
 std::transform(s.begin(), s.end(), s.begin(), cvt_symbol);
 }
}
 // converter to make any long integer value positive
class PositiveInt : public ::Configuration::AttributeConverter<unsigned long> {
 void convert(unsigned long& i, const Configuration&, const ConfigObject&, const std::string&) {
 if(i < 0) i = -i;
 }
}
...
try {
 ::Configuration db("");
 db.register_converter(new GoodString());
 db.register_converter(new PositiveInt());
 ...
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In the Java an example of Java code is shown below: 

import config.Configuration;
import config.AttributeConverter;

 // converter removes leading and trailing whitespace from a string
public class TrimString implements config.AttributeConverter {
 public Object convert(Object s, config.Configuration db, config.ConfigObject obj, String attr_name) { return (Object)(s.trim()); }
 public Class get_class() { return String.class; }
}
...
config.Configuration db = new config.Configuration("");
db.register_converter(new TrimString());

Online DAL Converters

The core TDAQ C++ DAL (libdaq-core-dal.so) provides converter daq::core::SubstituteVariables class to substitute configuration parameters in values of string attributes. It's constructor requires Configuration object and Partition object, since they are used to calculate conversion map. In case, if configuration database is reloaded, such parameters have to be reset using reset() method. An example of the C++ code is shown below: 

#include <config/Configuration.h>
#include "dal/Partition.h"
#include <dal/util.h>

try {
 ::Configuration db("");
 if(const daq::core::Partition * p = daq::core::get_partition(db, "partition-X")) {
 db.register_converter(new daq::core::SubstituteVariables(db, *p));
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Similar Java dal.jar provides attribute converter in the same way. An example of it's usage is shown below: 

import config.Configuration;
import config.DalObject;
import dal.SubstituteVariables;
import dal.Partition;

config.Configuration db = new config.Configuration("");
dal.Partition p = dal.Algorithms.get_partition(db, "partition-X");
if(p != null) {
 db.register_converter(new dal.SubstituteVariables(db, p));
}

5.4. Reading Values of Relationships

Once an object is retrieved, the user can get objects referenced by it. A method is created for each relationship of each generated class. It has the following format: 

for C++: 

 const class-type * get_RelationshipName() const - for single-value relationships; 

 const std::vector<const class-type*>& get_RelationshipName() const - for multi-value relationships; 

for Java: 

 class-type get_RelationshipName() const - for single-value relationships; 

 class-type[] get_RelationshipName() const - for multi-value relationships. 

5.5. Cast Class Types

There are situations when user may need to cast an object from one class to a derived one. To make a down cast for an object of generated class the user should to use the methods of the configuration classes and never use cast supported by the programming languages.

C++ cast

There are situations when some set of objects can belong to different classes, e.g. objects can be of class A or B which is derived from class A. For a down cast the Configuration::cast() method must be used. As an example, the code to try and to cast from application to run-control application type is shown below: 

try {
 ::Configuration db;
 // some code to get the vector of applications
 const std::vector<const dal::Application*>& l = ...;
 std::vector<const dal::Application*>::const_iterator j = l.begin();
 for(; j != l.end(); ++j) {
 if(const dal::RunControlApplication * r = db.cast<dal::RunControlApplication>(*j)) {
 std::cout << "application " << r << " is run control application" << std::endl; 
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Java cast

To down cast an object of generated Java DAL use aproapriate cast() method in generated class. For example, some object of application class can be down casted to the run control application: 

config.Configuration db(...);
dal.Application a = ...; // some code to get application
dal.RunControlApplication rc_application = dal.RunControlApplication_Helper.cast(db, a);
if(rc_application != null) { ... }

5.6. Data Destruction

In C++ the object of the Configuration class should not be destroyed while the DAL is in use. All objects read via template methods are destroyed by the Configuration class destructor. The user must never try to modify or to destroy such objects himself.

6. How to create and to modify data

This section explains how to create a new database file, how to create or remove database data and how to modify existing data.

Any modifications described by this section becomes persistent and visible to others processes only after successful commit operation. If the modification should not be committed (e.g. a modification failed), it is necessary to execute abort operation, e.g. in C++: 

try {
 ::Configuration db();
 bool success = true;
 ... // some code which makes changes and sets the variable to false if failed
 if(success) {
 std::cout << "commit changes\n";
 db.commit(); // one also check return status, true means success
 }
 else {
 std::cerr << "ERROR: something was wrong, abort changes\n";
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

Below there is the same example for Java: 

config.Configuration db = new config.Configuration(...);
... // some code to makes changes and sets the success variable to false if failed
if(success) {
 System.out.println("commit changes");
 db.commit();
}
else {
 System.err.println("ERROR: something was wrong, abort changes");
 db.abort();
}

To modify or to destroy an object using generated C++ DAL methods described below, it is necessary to have a non-const pointer or reference on the object. However all generated DAL methods return objects as const. To make a change it is necessary to use C++ const_cast to get non-const pointer or reference.

6.1. Creation of new database file

To create a new database file using C++ it is necessary to build an object of the Configuration class only providing name of implementation plug-in: 

::Configuration db("oksconfig");

Similar code for Java is below: 

config.Configuration db = new config.Configuration("rdbconfig"); // no db file

To create a new database data file it is necessary to decide which schema (at least one schema is always required) and optionally others database files will be used. Then it is necessary to provide an absolute name for newly created database file (the user should have write permission or the rdb server must be run in read-write mode under account which has such rights). If rdb implementation is used, it is also necessary to provide server and optionally partition name. After this it is necessary to use create method of the Configuration class and check it's return status.

Below there is example for C++ and oks implementation: 

try {
 ::Configuration db("oksconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 if(db.create("", db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For rdb implementation it is similar, but requires rdb server and optionally partition's names: 

try {
 ::Configuration db("rdbconfig");
 std::list<std::string> includes;
 includes.push_back("online/schema/online.schema.xml"); // common schema
 includes.push_back("online/segments/setup.data.xml"); // online infrastructure
 const char * db_name = "/tmp/my-partition.data.xml"; // new database file name
 const char * server_name = "foo::bar"; // server with name bar running in part. foo
 if(db.create(server_name, db_name, includes) == false) {
 std::cerr << "ERROR: failed to create file " << db_name << " on " << server_name << std::endl;
 db.abort();
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java an example with rdb implementation is shown below: 

try {
 config.Configuration db = new config.Configuration("rdbconfig");
 String[] includes = new String[2];
 includes[0] = "online/schema/online.schema.xml"; // common schema
 includes[1] = "online/segments/setup.data.xml"; // online infrastructure
 db.create("foo::bar", "/tmp/my-partition.data.xml", includes);
 db.commit();
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
}
catch(config.NotAllowedException ex) {
 System.err.println("ERROR: caught \'config.NotAllowed\' exception");
}
... // catch config.AlreadyExistsException in a similar way

The included files should exist in advance and be defined either as an absolute path or as a relative path to a token of the TDAQ_DB_PATH variable value.

6.2. Database Includes

There are methods in C++ class Configuration to add a new include, to remove an existing include or to get list of includes for given database. They are: 

 bool Configuration::add_include(const std::string& db_name, const std::string& include) - adds include to the database db_name and returns true in case of success or false if failed; 

 bool Configuration::remove_include(const std::string& db_name, const std::string& include) - removes an existing include from the database db_name and returns true in case of success or false if failed; 

 bool Configuration::get_includes(const std::string& db_name, std::list<std::string>& includes) const - fills list of includes by files which are included by the db_name and returns true in case of success or false if failed.

Similar methods in Java class config.Configuration are: 

 void add_include(String db_name, String include) - adds include to the database db_name or throws exception if failed; 

 void remove_include(String db_name, String include) - removes an existing include from the database db_name or throws exception if failed; 

 void get_includes(String db_name, String[] includes) - fills array of includes by files which are included by the db_name or throws exception if failed.

6.3. Objects Manipulations

This subsection explains how to create and how to destroy database objects.

Objects Creation

To create a new object using generated C++ DAL there are two Configuration template methods: 

 const T * Configuration::create(const std::string& at, const std::string& id, bool) - to create new object of class T with identity id at existing database file with name at; 

 const T * Configuration::create(const ::DalObject& at, const std::string& id, bool) - to create new object of class T with identity id at a database file where object at is stored.

The methods return non-null pointer in case of success or null if failed. The second method is faster since time to search the database file where to put new object is much smaller.

When the init_object parameter is set to false, then the values of attributes and relationships are not read from implementation (for a newly created object they are set to default values in accordance with the database schema).

An example how to create two new objects of the online dal::Computer class is shown below: 

try {
 ::Configuration db(...);
 const char * dbfile = "/tmp/my-db.data.xml";
 const dal::Computer * host = db.create<dal::Computer>(dbfile, "host-1");
 if(host == 0) {
 std::cerr << "ERROR: failed to create object \'host-1\' at \'" << dbfile << "\'\n";
 }
 else {
 if(db.create<dal::Computer>(*host, "host-2") == 0) {
 std::cerr << "ERROR: failed to create object \'host-2\' at file of " << host;
 }
 }
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

On Java similar methods are genereted in the helper classes. For class T two methods are available: 

 T create(config.Configuration db, String at, String id) - to create new object of class T with identity id at existing database file with name at; 

 T create(config.Configuration db, config.DalObject at, String id) - to create new object of class T with identity id at a database file where object at is stored.

The example to create online segment and it's application is shown below:: 

config.Configuration db = new ...
String db_file = "/tmp/my-db.data.xml";
try {
 dal.Segment s = dal.Segment_Helper.create(db, db_file, "my segment");
 dal.Application a = dal.Application_Helper.create(db, s, "my application");
}
catch(config.SystemException ex) {
 System.err.println("ERROR: caught \'config.System\' exception");
} ... // also other exceptions to be caught

Objects Destruction

To destroy an existing object there is template method in the C++ Configuration class bool destroy(T& obj). It returns true in case of success and false if failed. See example: 

try {
 ::Configuration db(...);
 dal::Computer * host = ...; // some code to get pointer
 db.destroy(*host);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

In Java the method void destroy(config.Configuration db) is generated in T.java, e.g.: 

config.Configuration db = new ...;
dal.Computer host = ...; // some code to get object
try {
 host.destroy(db);
}
catch(config.SystemException ex) {
 System.err.println("ERROR: failed to destroy " + host);
} ... // also other exceptions to be caught

6.4. Modification Values of Attributes

Once the objects are retrieved or created, the user can modify values of their attributes. A method to set attribute value is created for each attribute of each generated class. The mapping between C++/Java types and OKS types can be seen in the 3.1. Mapping Between OKS Attribute Types and Programming Languages Types section.

In C++ such method throws daq::config::Exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(const std::vector<type>& value) - for multi-value attribute.

In Java such method throws an exception if failed: 

 void set_AttributeName(type value) - for single-value attribute; 

 void set_AttributeName(type[] value) - for multi-value attribute.

6.5. Modification Values of Relationships

Once the objects are retrieved or created, the user can modify values of their relationships. A method to set relationship value is created for each relationship of each generated class.

For C++ it has the following format and throws daq::config::Exception if failed: 

 void set_RelationshipName(const class-type * value) - for single-value relationships; 

 void set_RelationshipName(const std::vector<const class-type*>& value) - for multi-value relationships.

For Java it has the following format and throws an exception if failed: 

 void set_RelationshipName(class-type value) - for single-value relationships; 

 void set_RelationshipName(class-type[] value) - for multi-value relationships.

6.6. Modification of Database and Invalid Objects

There are several methods which may make instances of ConfigObject and generated DAL classes be invalid: 

Configuration::remove_include(const std::string&, const std::string&) - this method destroys objects belonging to files closed in result of include removal; 

Configuration::destroy_obj(ConfigObject&) and template Configuration::destroy(T&) - those methods destroy given object and may destroy other objects linked via composite dependent relationships.

In case of ConfigObject there is no simple way to know if an object is valid after above remove_include() or destroy_obj() method call, since by efficiency reasons all methods are redirected to implementation object without checking of it's validity. It is recommended to reinitialize all instances of ConfigObject after above calls.

With objects of generated DAL classes the situation is different. After implementation object destruction a method invoked on corresponding DAL objects will throw daq::config::DeletedObject exception, that can be caught by user code. Also, validity of object can be tested with DalObject::was_removed() method.

An example is shown below for include file removal and exception mechanism for generated DAL objects: 

Configuration db;

...

std::vector<const daq::core::Computer*> nodes;
db.get(nodes);

 // remove include "bar" from file "foo",
 // that may result some files to be closed
 // and several template objects to be invalidated

db.remove_include("foo", "bar");

for(std::vector<const daq::core::Computer*>::const_iterator i = nodes.begin(); i != nodes.end(); ++i) {
 try {
 (*i)->get_State(); // cause exception if object was destroyed
 std::cout << "object " << *i << " was not destroyed" << std::endl;
 }
 catch(daq::config::DeletedObject& ex) {
 std::cout << "Oops, object " << (void *)(*i) << " => " << *i << " was destroyed" << std::endl;
 }
}

7. Notification mechanism

The user application can be notified on changes of the configuration data. To do this user should to implement one or many callback functions (C++) or classes (Java) which will be used when the database changes are committed and to choose which changes in classes and objects should be reported (i.e. to define the subscription criteria ).

The user receives description of information changes in one go via callbacks invoked after commit of database changes. This is more preferred way than individual callback per object or per class since user may want to see all changes at single point. Each callback receives own list of changes in accordance with it's subscription criteria.

The changes are reported as a collection of changes per DAL class. A change per class contains 4 parameters: the class name and the identities of created, modified and removed objects.

To make a subscription it is necessary to make three steps: 

implement callback, 

define subscription criteria, 

invoke subscribe method with above entities on the configuration object.

7.1. User Callback

To start with any subscription on database changes the user must to implement at least one Configuration::notify callback function in C++ or config.Callback interface on Java. Below there are details for C++ and Java subscriptions.

C++ callback function

The user has to implement Configuration::notify callback. It has the following parameters: 

 const std::vector<::ConfigurationChange *> & changes - description of changes 

 void * parameter - user parameter

The ConfigurationChange class is declared in the config/Change.h file and has 4 methods to get name of the class and vectors of created, modified and removed object identities. An example of callback functions is shown below: 

void callback(const std::vector< ConfigurationChange *> & changes, void *)
{
 std::cout << "The CALLBACK reports all changes:\n";

 // iterate changes sorted by classes
 for(std::vector<ConfigurationChange *>::const_iterator j = changes.begin(); j != changes.end(); ++j) {

 // print class name
 std::cout << "- there are changes in class \"" << (*j)->get_class_name() << "\"\n";

 std::vector<std::string>::const_iterator i;

 // print modified objects
 for(i = (*j)->get_modified_objs().begin(); i != (*j)->get_modified_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was modified\n";
 }

 // print removed objects
 for(i = (*j)->get_removed_objs().begin(); i != (*j)->get_removed_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was removed\n";
 }

 // print created objects
 for(i = (*j)->get_created_objs().begin(); i != (*j)->get_created_objs().end(); ++i) {
 std::cout << " * object \"" << *i << "\" was created\n";
 }
 }
}

Java callback interface

The user has to create a class implementing the config.Callback interface. It requires to implement method void process_changes(config.Change[] changes, java.lang.Object parameter). Example below illustrates how to implement notification callback: 

class TestCallback implements config.Callback {
 private config.Configuration db;

 public TestCallback(config.Configuration d) { db = d; }

 public void process_changes(config.Change[] changes, java.lang.Object parameter) {

 // the parameter can be any; as an example, the callback ID is passed as string
 String cb_id = (String)parameter;

 // print out changes description
 System.out.println("[TestCallback " + cb_id + "] got changes:");
 config.Change.print(changes, " ");

 // iterate changes by classes
 for(int i = 0; i < changes.length; i++) {
 config.Change change = changes[i];
 System.out.println("* there are changes in the \'" + change.get_class_name() + "\' class");

 // just as example, look for changed objects of the Application class
 if((change.get_class_name().equals("Application") == true) && (change.get_changed_objects() != null)) {
 System.out.println("* " + change.get_changed_objects().length + " updated objects of the Application class");

 // iterate by all changed objects and print them out
 for(int j = 0; j < change.get_changed_objects().length; ++j) {
 dal.Application a = dal.Application_Helper.get(db, change.get_changed_objects()[j]);

 // an example of correct down cast
 if(a.class_name().equals("RunControlApplication")) {
 dal.RunControlApplication_Helper.get(db, a.config_object()).print(" "); // print as RC application
 }
 else {
 a.print(" "); // print as an application
 }
 }
 }
 }
 }
}

7.2. Subscription criteria

The subscription criteria is an object of ConfigurationSubscriptionCriteria class in C++ or config.Subscription class in Java. It is used to define lists of classes and objects, which changes will be monitored and reposted to user. If user provides no any class or object, it means subscription on any change and a database modification is reported.

Subscription on any changes in class

The notification callback is invoked for any changes of class objects including creation of new objects, removing or modification of existing objects.

In C++ to subscribe on any changes in some class the user should to use ConfigurationSubscriptionCriteria::add(const std::string&) method. For a class generated by genconfig the s_class_name attribute can be used, e.g. to subscribe on changes in class dal::Application: 

::ConfigurationSubscriptionCriteria c;
c.add(dal::Application::s_class_name);

In Java method config.Subscription.add(String class_name) should be used, e.g. to subscribe on changes in class Application it is necessary to write the following code: 

config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add("Application");

Subscription on object changes

When subscription on object changes has done, the notification callback is invoked for any changes of the objects or it's removing.

In C++ to subscribe on object changes notification the user should to use ConfigurationSubscriptionCriteria::add(const ::DalObject&), e.g. to subscribe on changes of an object of the Application class: 

::ConfigurationSubscriptionCriteria c;
const dal::Application * app_obj;
c->add(*app_obj);

In Java config.add(DalObject obj) method to be used, e.g.: 

dal.Application app = ...; // some code to get application object
config.Subscription s = new config.Subscription(new TestCallback(db), null);
s.add(app);

7.3. Subscription

To make the actual subscription it is necessary to have a notification callback been implemented and a subscription criteria object. The the method subscribe() to be invoked on the configuration object. For C++ an example is shown below: 

 // user-defined callback
void cb(const std::vector<ConfigurationChange *> & changes, void * p) { ... }

try {
 // configuration object
 ::Configuration db(...);

 // subscription criteria object
 ::ConfigurationSubscriptionCriteria c;
 c.add(dal::Application::s_class_name);

 // subscription; if database is changed, the cb can be invoked after this line
 ::CallbackId id = db.subscribe(c, cb);
}
catch(daq::config::Exception & ex) {
 std::cerr << "ERROR: " << ex << std::endl; return 1;
}

For Java above example looks like: 

 // user-defined callback
class MyCallback implements config.Callback { ... }

 // configuration object
config.Configuration db = new config.Configuration(...);

 // subscription criteria object
config.Subscription c = new config.Subscription(new MyCallback(db), null);
c.add("Application");

 // subscription; MyCallback::process_changes() can be invoked after this line
db.subscribe(c);

The method unsubscribe() can be used to remove subscription set above. In case of C++ it's parameter is a return value of the subscribe() method (i.e. CallbackId value). For Java it's parameter is the subscription object used as parameter of subscribe() method.

8. Algorithms

By default, the generated classes have one-to-one mapping to database schema and DAL objects directly correspond to the database objects. If user wants to add more algorithms on top of the generated DAL without modification of DAL code by hand, he has possibility to define algorithms on top of the OKS class methods.

When a class method is created, user can add it's implementation for different programming languages. To be taken into account by genconfig, user have to provide C++ and/or Java implementation. Then he has two possibilities: 

declare method prototype, write method implementation in the separate file and add such file when build DAL; 

declare method prototype and write it's implementation in OKS.

The first way is more flexible, but requires more steps when build library. The second way does not require any additional steps when build library, but will require schema modifications to any method's implementation modification.

The online DAL defines several algorithms (e.g. to find partition, get all applications, to calculate application environment, etc.) and uses first way to implement algorithms. More information can be found in the online dal package. 

 All Data Structures Namespaces Files Functions Variables Typedefs Enumerations Enumerator Friends Defines

Generated on Tue Jan 24 2012 16:04:15 for TDAQ release tdaq-04-00-01 by 

 1.7.2
```

## 4. Javadoc of the `config` API (3 pages)

The Java `config` API documentation (subset most relevant to OKS/DAL usage and the query machinery): `package-summary.html` (20110707223035), `Query.html` (20110322202710), `BadQueryException.html` (20110322185043).

### Snapshot `javadoc__config-BadQueryException__20110322185043.html`
*Local file: `output/extracts/pcatd12/javadoc__config-BadQueryException__20110322185043.html`*

```text
BadQueryException

 | 

 | Overview 
 | Package 
 |  Class 
 | Tree 
 | Deprecated 
 | Index 
 | Help 

 | 

 | 
 PREV CLASS 
 NEXT CLASS
 | 
 FRAMES  
 NO FRAMES  

 All Classes

 | 
 SUMMARY: NESTED | FIELD | CONSTR | METHOD
 | 
DETAIL: FIELD | CONSTR | METHOD

config

Class BadQueryException

java.lang.Object
 java.lang.Throwable
 java.lang.Exception
 java.lang.RuntimeException
 config.BadQueryException

All Implemented Interfaces: java.io.Serializable

public class BadQueryExceptionextends java.lang.RuntimeException

Thrown to indicate that the query syntax is bad.

Since:
 online release 00-21-02
See Also:Serialized Form

Constructor Summary

 | BadQueryException()

          Constructs a BadQueryException with no detail message.

 | BadQueryException(java.lang.String message)

          Constructs a BadQueryException with the specified detail message.

Method Summary

Methods inherited from class java.lang.Throwable

 | fillInStackTrace, getCause, getLocalizedMessage, getMessage, getStackTrace, initCause, printStackTrace, printStackTrace, printStackTrace, setStackTrace, toString

Methods inherited from class java.lang.Object

 | clone, equals, finalize, getClass, hashCode, notify, notifyAll, wait, wait, wait

Constructor Detail

BadQueryException

public BadQueryException()

Constructs a BadQueryException with no detail message.

BadQueryException

public BadQueryException(java.lang.String message)

Constructs a BadQueryException with the specified detail message.

Parameters:message - the detail message

 | 

 | Overview 
 | Package 
 |  Class 
 | Tree 
 | Deprecated 
 | Index 
 | Help 

 | 

 | 
 PREV CLASS 
 NEXT CLASS
 | 
 FRAMES  
 NO FRAMES  

 All Classes

 | 
 SUMMARY: NESTED | FIELD | CONSTR | METHOD
 | 
DETAIL: FIELD | CONSTR | METHOD
```

### Snapshot `javadoc__config-Query__20110322202710.html`
*Local file: `output/extracts/pcatd12/javadoc__config-Query__20110322202710.html`*

```text
Query

 | 

 | Overview 
 | Package 
 |  Class 
 | Tree 
 | Deprecated 
 | Index 
 | Help 

 | 

 | 
 PREV CLASS 
 NEXT CLASS
 | 
 FRAMES  
 NO FRAMES  

 All Classes

 | 
 SUMMARY: NESTED | FIELD | CONSTR | METHOD
 | 
DETAIL: FIELD | CONSTR | METHOD

config

Class Query

java.lang.Object
 config.Query

public class Queryextends java.lang.Object

The Query class is used to create query expression.
 For the moment a query is the OKS query string. In future the class
 will be extended to allow dynamic query creating which will potentially
 allow to work with others database implementations.

Since:
 online release 00-21-02

Constructor Summary

 | Query()

          Constructor to build an empty query.

 | Query(java.lang.String query)

          Constructor to build query from string.

Method Summary

 | 
 java.lang.String
 | get_query_string()

          Returns query string.

Methods inherited from class java.lang.Object

 | clone, equals, finalize, getClass, hashCode, notify, notifyAll, toString, wait, wait, wait

Constructor Detail

Query

public Query()

Constructor to build an empty query.

Query

public Query(java.lang.String query)
 throws BadQueryException

Constructor to build query from string.

Parameters:query - query string
Throws:
BadQueryException

Method Detail

get_query_string

public java.lang.String get_query_string()

Returns query string.

 | 

 | Overview 
 | Package 
 |  Class 
 | Tree 
 | Deprecated 
 | Index 
 | Help 

 | 

 | 
 PREV CLASS 
 NEXT CLASS
 | 
 FRAMES  
 NO FRAMES  

 All Classes

 | 
 SUMMARY: NESTED | FIELD | CONSTR | METHOD
 | 
DETAIL: FIELD | CONSTR | METHOD
```

### Snapshot `javadoc__config-package-summary__20110707223035.html`
*Local file: `output/extracts/pcatd12/javadoc__config-package-summary__20110707223035.html`*

```text
config

 | 

 | Overview 
 |  Package 
 | Class 
 | Tree 
 | Deprecated 
 | Index 
 | Help 

 | 

 | 
 PREV PACKAGE 
 NEXT PACKAGE
 | 
 FRAMES  
 NO FRAMES  

 All Classes

Package config

Interface Summary

 | AttributeConverter
 | The interface defines methods for an attribute converter object.

 | Callback
 | The Callback interface is used for receiving "interesting" information describing
 database changes.

 | ConfigAction
 | The ConfigAction interface is used to describe base methods of callback on configuration change.

 | ConfigObjectImpl
 | The ConfigObjectImpl interface is used to declare abstract interface to access
 the values of an object attributes & relationships and the object's identity.

 | ConfigurationImpl
 | The interface defines based methods to be supported by a database implementation.

 | DalObject
 | The DalObject interface is used to describe base methods of any class generated by genconfig.

Class Summary

 | Change
 | The Change class is used to describe subset of the database changes happen
 after a database modification which satisfies to the subscription criteria.

 | ConfigObject
 | The ConfigObject class is used to provide an abstract interface to
 the values of an object attributes & relationships and the object's identity.

 | Configuration
 | The Configuration class provides interfaces to database data which are independent
 from the used database implementations.

 | NotifyThread
 | The NotifyThread class provides interfaces for notification about changes.

 | Query
 | The Query class is used to create query expression.

 | Subscription
 | The class is used to provide the subscription criteria.

Exception Summary

 | AlreadyExistsException
 | Thrown to indicate that the an created item (an object, a file) already exists.

 | BadQueryException
 | Thrown to indicate that the query syntax is bad.

 | NotAllowedException
 | Thrown to indicate that the requested action is not allowed to given user.

 | NotFoundException
 | Thrown to indicate that the requested item (class, object, attribute, etc.) does not exist.

 | NotValidException
 | Thrown to indicate that the object is not valid.

 | SystemException
 | Thrown to indicate that there is a system exception (communication failure, file access problem, etc).

 | 

 | Overview 
 |  Package 
 | Class 
 | Tree 
 | Deprecated 
 | Index 
 | Help 

 | 

 | 
 PREV PACKAGE 
 NEXT PACKAGE
 | 
 FRAMES  
 NO FRAMES  

 All Classes
```

## 5. Observations

- The oldest OKS release note preserved here is `tdaq-01-01-00` (2011): it documents the `$(FOO)` environment-variable syntax change for filenames (`${FOO}` -> `$(FOO)`), the query heap-allocation fix, and new `oks_dump` options `--files-only`, `--class`, `--query`.
- `config` release notes cover `tdaq-01-01-00` .. `tdaq-03-00-00`; the last archived OKS note is `tdaq-04-00-00`. Later notes (05-00-00+) were never archived on this site (verified via CDX with prefix filters); coverage continues in the GIT-era `ooks` repo release notes (see 03-cern-gitlab.md).
- Together the archived pages and the GIT-repo notes document: `tdaq-01-01-00` .. `tdaq-04-00-00` (archived, 2011-2012) => git-era `oks-02-07-02` (2018) .. `oks-08-04-00` (2024).
- The `config` release notes show the pre-OKS era: the `Configuration`/`ConfigObject` APIs were the DB abstracted config data interface that OKS replaced/absorbed; the DAL (see 02-dune-dal.md) was introduced on top of it.
