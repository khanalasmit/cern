# Source 2: DUNE-DAQ/dal (GitHub, public, branch `develop`)

> Generated 2026-08-08 by an automated extraction renderer (`output/build_02.py`).
> Every code block below is the full byte-content of the named file, copied verbatim from the local clone.


## Provenance

- **Source URL:** https://github.com/DUNE-DAQ/dal (branch `develop`)
- **Local mirror:** `repo/dune-dal/` (git clone, depth 1)
- **HEAD commit:** `6b0ba51b9f093e14f9878edf0ff884279cc7a087` (2024-07-17 10:30:51 -0500, "JCF: fix ambiguous line in tutorial")
- **Caption:** The DUNE DAQ `dal` (Data Access Library) package: the DUNE DAQ release of the OKS configuration system. It provides generated DAL classes (off the ATLAS `core` schema), algorithms, command-line tools, and Python bindings on top of `conffwk`/`okssystem`. This is the package the ReadTheDocs page `dune-daq-sw.readthedocs.io/en/latest/packages/dal/` documents.
- **Relationship to the task topic (GIT/version/hash):** the OKS/GIT version of a running partition's configuration is published via the Information Service and read back by `dal_get_config_version`; `get_config_version()` reads the `TDAQ_DB_VERSION` environment variable (set by `Partition::get_DBVersion()`, the DB version attribute of the `Partition` OKS class); `ConfigVersion` (an ISInfo class) carries the "OKS GIT SHA key used for given partition".

## Documentation

### `docs/README.md — "An Introduction to OKS"`  
*Local path: `repo/dune-dal/docs/README.md`*

```markdown

# An Introduction to OKS

## Overview

OKS (Object Kernel Support) is a suite of packages [originally
written](https://gitlab.cern.ch/atlas-tdaq-software/oks) for the ATLAS
data acquisition effort. Its features include:
* The ability to define object types in XML (known as OKS "classes"), off of which C++ and Python classes can automatically be generated
* Support for class Attributes, Relationships, and Methods. Attributes and Relationships are automatically generated; Methods allow developers to add behavior to classes
* The ability to create instances of classes (known as OKS "objects"), modify them, read them into an XML file serving as a database and retrieve them from the database

This document provides a taste of what OKS has to offer.

## Getting Started

To get started working with the DUNE-repurposed OKS packages, you'll want to [set up a work area](https://dune-daq-sw.readthedocs.io/en/latest/packages/daq-buildtools/) and then clone and build this repo ("dal") in order to run the tutorial below. These packages include [dbe (the DataBase Editor GUI)](https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/), dal (Data Access Library, this repo), [oksutils](https://github.com/DUNE-DAQ/oksutils), [oksdalgen](https://github.com/DUNE-DAQ/oksdalgen) (contains code generation executable), [oks](https://github.com/DUNE-DAQ/oks) (core OKS functionality, not to be confused with the entire OKS suite), [conffwk](https://github.com/DUNE-DAQ/conffwk), [oksconflibs](https://github.com/DUNE-DAQ/oksconflibs) and [okssystem](https://github.com/DUNE-DAQ/okssystem). Some of these packages you may never need to worry about, others (such as the dbe GUI) may benefit from further development. 
  
With the work area set up, build dal. After building it, it's time to run some tests to make sure things are in working order. These include:
* `test_configuration.py`: A test script in the conffwk package. Tests that you can create objects, save them to a database, read them back, and remove them from a database.
* `test_dal.py`: Also from the conffwk package. Test that you can change the values of objects, and get expected errors if you assign out-of-range values. 
* `algorithm_tests.py`: A script from the dal package. Test that Python bindings to class Methods implemented in C++ work as expected. 

If anything goes wrong during the tests, it will be self-evident. 

## A Look at OKS Databases: XML-Represented Classes and Objects

While ATLAS has various database implementations (Oracle-based, etc.), for the DUNE DAQ we only need their basic database format, which is an XML file on disk. There are generally two types of database file: the kind that defines classes, which by convention have the `*.schema.xml` extension, and the kind that define instances of those classes (i.e. objects) and have `*.data.xml` extensions. The class files are known from ATLAS as "schema files" and the object files are known from ATLAS as "data files". A good way to get a feel for these files is to start with the tutorial schema, `./install/dal/share/schema/dal/tutorial.schema.xml` from the base of your work area.  

### Overview of `tutorial.schema.xml`

Let's start with a description of what `tutorial.schema.xml` contains before we even look at its contents. It describes via three classes needed for a (very) simple DAQ: `ReadoutApplication` for detector readout, `RCApplication` for the Run Control in charge of `ReadoutApplication` instances, and a third class, `Application`, of which they're both subclasses. Open the file, and *unless you're purely curious, scroll past the lengthy header which you'll never need to understand* until you see the following:
```
 <class name="Application" description="A software executable" is-abstract="yes">
  <attribute name="Name" description="Name of the executable, including full path" type="string" init-value="Unknown" is-not-null="yes"/>
 </class>
```
(_n.b. if you want to use `emacs` in this environment you may need to run `spack unload cairo`; this hasn't apparently had any negative effects on OKS functionality_). The `is-abstract` qualifier means that you can't have an object which is concretely of type `Application`, you can only have objects of subclasses of `Application`. However, any class which is a subclass of `Application` will automatically contain a `Name` attribute, which here is intended to be the fully-qualified path of the executable in a running DAQ system. 

Next, we see the class for readout:
```
<class name="ReadoutApplication" description="An executable which reads out subdetectors">
  <superclass name="Application"/>
  <attribute name="SubDetector" description="An enum to describe what type of subdetector it can read out" type="enum" range="PMT,WireChamber" init-value="WireChamber"/>
 </class>
```
...where you can see that there's an OKS enumerated type, where here there are only two options, basically a photon detector or a TPC. 

Then, there's the run control application:
```
<class name="RCApplication" description="An executable which allows users to control datataking">
  <superclass name="Application"/>
  <attribute name="Timeout" description="Seconds to wait before giving up on a transition" type="u16" range="1..3600" init-value="20" is-not-null="yes"/>
  <relationship name="ApplicationsControlled" description="Applications RC is in charge of" class-type="Application" low-cc="one" high-cc="many"/>
 </class>
```
And here, we have two items of interest: 
* A `Timeout` Attribute representing the max number of seconds before giving up on a transition. Represented by an unsigned 2-byte integer, the max timeout is one hour, and defaults to 20 seconds. 
* An `ApplicationsControlled` Relationship, which refers to anywhere from one object subclassed from `Application` to "many", which is OKS-speak for "basically unlimited". 

OKS also provides tools which parse the XML and provide summaries of the contents of the database (XML file). `config_dump`, part of the conffwk package, is quite useful in this regard. Pass it `-h` to get a description of its abilities; if you just run `config_dump -d oksconflibs:./install/dal/share/schema/dal/tutorial.schema.xml` you'll get a summary of the classes used to defined the objects in the file. Running `config_dump -d oksconflibs:./install/dal/share/schema/dal/tutorial.schema.xml -C` will give you much more detail. For a schema as simple as the one we're showing here, this tool isn't super-useful, but it can be powerful when schemas get bigger and more complex. 

### Overview of `tutorial.data.xml`

In this section, we're going to _make_ a data file using the classes from `tutorial.schema.xml`. It's extremely simple, just run this script:
```
tutorial.py 
```
...and it will produce `tutorial.data.xml`. We'll look at it in a moment, but two things to note first:
1. As you can see if you open up `tutorial.py`, a Python module is actually _generated_ off of `tutorial.schema.xml`. If we add Attributes, Relations, etc. to the classes, the Python code will automatically pick them up without any additional Python needing to be written. 
1. `config_dump -d oksconflibs:tutorial.data.xml --list-objects --print-referenced-by` provides a nice summary of `tutorial.data.xml`'s contents

We can also see what `tutorial.py` created by opening up `tutorial.data.xml`. Again, please scroll past the extensive header. What we see is two types of readout application, one ID'd as `PhotonReadout` and the other ID'd as `TPCReadout`; these names, of course, are chosen to reflect the choice of the `SubDetector` enum. Then we also see an instance of `RCApplication` where the `ApplicationsControlled` relationship establishes that run control is in charge of the two readout applications:
```
<obj class="RCApplication" id="DummyRC">
 <attr name="Name" type="string" val="/full/pathname/of/RC/executable"/>
 <attr name="Timeout" type="u16" val="20"/>
 <rel name="ApplicationsControlled">
  <ref class="ReadoutApplication" id="PhotonReadout"/>
  <ref class="ReadoutApplication" id="TPCReadout"/>
 </rel>
</obj>
```
The run control timeout is set to its default of 20 seconds. Say we want to change this, and save the result. For such a small data file it would be easy to manually edit, but if you think of a full-blown DAQ system you'll want to automate a lot of things. Fortunately we can alter the value via Python. Go into an interactive Python environment and do the following:
```
import conffwk
db = conffwk.Configuration('oksconflibs:tutorial.data.xml')
rc = db.get_dal("RCApplication", "DummyRC")  # i.e., first argument is name of the class, the second is the name of the object
print(rc.Timeout)
```
where in the last command, you see the timeout of 20 seconds.

For fun, let's try to set the timeout to an illegal value (i.e., a timeout greater than an hour):
```
rc.Timeout = 7200 # 2 hrs before run control gives up!
```
...you'll get a `ValueError`. 

Let's set it to a less-ridiculous 60 seconds, and save the result:
```
rc.Timeout = 60
db.update_dal(rc)
db.commit()
```
If we exit out of Python and look at `tutorial.data.xml`, we see the timeout is now 60 rather than 20. And if we read the data file back in, this update will be reflected. 

You're encouraged to experiment yourself with the objects, either interactively or via checking out the dal repo and editing `sourcecode/dal/scripts/tutorial.py`; make sure to run `dbt-build` in the case of the latter. 


## A Realistic Example

The `tutorial.schema.xml` file and `tutorial.data.xml` files are fairly easy to understand, and meant to be for educational purposes. To see the actual classes which are used on ATLAS, we can look at the following from the base of your work area: `./install/dal/share/schema/dal/core.schema.xml`. This file is quite large, and describes classes which actually model ATLAS's DAQ systems like `ComputerProgram` and `Rack` and `Crate`. If you look in [dal's `CMakeLists.txt` file](https://github.com/DUNE-DAQ/dal/blob/develop/CMakeLists.txt) you see the following:
```
daq_oks_codegen(core.schema.xml)
  
daq_add_library(algorithms.cpp disabled-components.cpp test_circular_dependency.cpp LINK_LIBRARIES conffwk::conffwk okssystem::okssystem logging::logging)
```
`core.schema.xml` gets fed into `daq_oks_codegen` which proceeds to generate code off of the classes defined in `core.schema.xml` that will subsequently be built into the package's main library. Details on `daq_oks_codegen` can be found [here](https://dune-daq-sw.readthedocs.io/en/latest/packages/daq-cmake/#daq_oks_codegen). 

You'll notice also that the classes in `core.schema.xml` contain not only Attributes and Relationships as in the tutorial example above, but also Methods. If you look at the `Partition` class (l. 415) and scroll down a bit, you'll see a `get_all_applications` Method declared, along with its accompanying C++ declaration (as well as Java declaration, but we ignore this). The implementation of `get_all_applications` needs to be done manually, however, and is accomplished on l. 1301 of `src/algorithms.cpp`. If you scroll to the top of that file you'll see a `#include "dal/Partition.hpp"` line. In the actual dal repo, there's no such include file. However, assuming you followed the build instructions at the top of this document, you'll find it in the `build/` area of your work area, as the header was in fact generated. 

To see the `get_all_applications` function in action, you can do the
following. 
```
dal_dump_app_config -d oksconflibs:./install/dal/bin/dal_testing.data.xml -p ToyPartition -s ToyOnlineSegment
```
...where `dal_testing.data.xml` is written specifically for testing dal's functionality. The output will look like the following:
```
Got 2 applications:
====================================================================================================================================================================
| num | Application Object                             | Host                      | Segment                        | Segment unique id | Application unique id    |
====================================================================================================================================================================
|   1 | ToyRunControlApplication@RunControlApplication | toyhost.fnal.gov@Computer | ToyOnlineSegment@OnlineSegment | ToyOnlineSegment  | ToyRunControlApplication |
|   2 | SomeApp@CustomLifetimeApplication              | toyhost.fnal.gov@Computer | ToyOnlineSegment@OnlineSegment | ToyOnlineSegment  | SomeApp                  |
====================================================================================================================================================================
```

Note that in the output, `Application Object`, `Host` and `Segment` are printed in the format `<object name>@<class name>` where the object is an instance of a class. Note also that `RunControlApplication` is an actual ATLAS class and not to be confused with the much simpler `RCApplication` from the tutorial above. 

Likewise, you can see a Python script which serves the same function,
but via calling Python bindings to C++ functions. We of course want
the output to be identical:
```
dal_dump_app_config.py -d oksconflibs:./install/dal/bin/dal_testing.data.xml -p ToyPartition -s ToyOnlineSegment
```
You can also play around with `dal_dump_apps` or `dal_dump_apps.py`, pass the
`-h` argument to either program to see your options. 

## Next Step

Now that we've learned a bit about OKS, let's take a look at the [GUI interfaces to OKS](https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/)
```

### `docs/RELEASE_NOTES.md`  
*Local path: `repo/dune-dal/docs/RELEASE_NOTES.md`*

```markdown

_JCF, Jan-23-2023: the following are the original ATLAS TDAQ release notes; they are not guaranteed to be applicable to the DUNE DAQ refactor of this repository_

# dal

## tdaq-09-01-00

### OKS git

When TDAQ_DB_REPOSITORY and TDAQ_DB_USER_REPOSTORY are defined, the DAL algorithm calculating environment sets TDAQ_DB_PATH=$TDAQ_DB_USER_REPOSTORY and usets TDAQ_DB_REPOSITORY and TDAQ_DB_USER_REPOSTORY process environment to allow standalone user tests.

### SW repository generation utility was removed

Remove dal_create_sw_repository. The create_repo.py has to be used instead. See [CMake TWiki](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltCMake#Software_Repository_Generation) for more information.

## tdaq-08-03-00

### New template-based segments and applications config
Jira: [ADTCC-177](https://its.cern.ch/jira/browse/ADTCC-177)

The generated DAL classes BaseApplication and Segment replaced old AppConfig and SegConfig ones.

Updated partition algorithms:
```
std::vector<const BaseApplication *> Partition::get_all_applications(std::set<std::string> * app_types = nullptr,
  std::set<std::string> * use_segments = nullptr, std::set<const Computer *> * use_hosts = nullptr) const;

const Segment * Partition::get_segment(const std::string& name) const;
```

The segment algorithms:
```
std::vector<const BaseApplication *> Segment::get_all_applications(std::set<std::string> * app_types = nullptr,
  std::set<std::string> * use_segments = nullptr, std::set<const Computer *> * use_hosts = nullptr) const;

const BaseApplication * Segment::get_controller() const;

const std::vector<const BaseApplication *>& Segment::get_infrastructure() const;

const std::vector<const BaseApplication *>& Segment::get_applications() const;

const std::vector<const Segment*>& Segment::get_nested_segments() const;

const std::vector<const Computer*>& Segment::get_hosts() const;

const Segment * Segment::get_base_segment() const;

bool Segment::is_disabled() const;

bool Segment::is_templated() const;

void Segment::get_timeouts(int & actionTimeout, int & shortActionTimeout) const;
``` 

The application algorithms:
```
const Computer * BaseApplication::get_host() const;

const daq::core::Segment * BaseApplication::get_segment() const;

std::vector<const daq::core::Computer *> BaseApplication::get_backup_hosts() const;

const daq::core::BaseApplication * BaseApplication::get_base_app() const;

std::vector<const daq::core::BaseApplication *>
BaseApplication::get_initialization_depends_from(const std::vector<const daq::core::BaseApplication *>& all_apps) const;

std::vector<const daq::core::BaseApplication *>
BaseApplication::get_shutdown_depends_from(const std::vector<const daq::core::BaseApplication *>& all_apps) const;
```

The algorithms on Segment and BaseApplication objects may only be called, if such objects in turn were instantiated by get_all_applications() or partition's get_segment() DAL algorithms.

### Algorithms changes
Jira: [ADTCC-209](https://its.cern.ch/jira/browse/ADTCC-209)

Several algorithms were never used and deleted or reorganized

#### Modified algorithms

* BaseApplication::get_output_error_directory() is renamed to Partition::get_log_directory() because the log directory does not depend on the application
* BaseApplication::get_info() remove partition, segment and host parameters
* Segment::get_timeouts() remove partition and database parameters
* SubstituteVariables remove database parameter in the constructor

#### Removed algorithms

Several algorithms were obsolete and deleted, or not used by user code and removed from public API:

* ComputerProgram::get_parameters()
* BaseApplication::get_application()
* BaseApplication::get_some_info()
* ResourceBase::get_applications()
* Variable::get_value(tag)
```

> The `docs/Twiki.txt` file below is the original ATLAS TDAQ Twiki on the DAL package (DUNE header comment: "the following is the original ATLAS TDAQ Twiki; it is not guaranteed to be applicable to the DUNE DAQ refactor of this repository"). Its Basic Concepts section describes Partition/Segment/Application DAL classes, and it lists the `dal_get_config_version`/`dal_set_config_version` tools in the context of the OKS GIT-based configuration versioning (see "Config versioning" within). Full byte-content is preserved below.
### `docs/Twiki.txt (51 KB, original ATLAS TDAQ Twiki)`  
*Local path: `repo/dune-dal/docs/Twiki.txt`*

```text
<!-- /ActionTrackerPlugin -->
<LINK href="/twiki/pub/TWiki/KupuContrib/kuputwiki.css" type=text/css
rel=stylesheet>
<!-- /ActionTrackerPlugin --><LINK
href="/twiki/pub/TWiki/KupuContrib/kuputwiki.css" type=text/css
rel=stylesheet>
<!-- By default the title is the WikiWord used to create this topic !-->
<!-- if you want to modify it to something more meaningful, just replace
%TOPIC% below with i.e "My Topic"!-->
<!---------------------------------------------------------  snip snip
----------------------------------------------------------------->
%CERTIFY% 
---+!! <nop>%TOPIC% 
%TOC% <!--optional-->%STARTINCLUDE% 

JCF, Jan-23-2023: the following is the original ATLAS TDAQ Twiki; it is not guaranteed to be applicable to the DUNE DAQ refactor of this repository


The DAL (Data Access Library) is a software package to simplify access to the
configuration data created on top of the *core* schema. It is automatically
generated by the *dal* package for C++, Java and Python programming languages.
To use the DAL package you need to read the
[[https://pcatd12.cern.ch/doxygen/tdaq-02-00-00/html/ConfigPackages.html
][config User's Guide]]. 

---+ 1. Responsible 

%ICON{person}% [[http://consult.cern.ch/xwho/people/432778][Igor Soloviev]]

---+ 2. Documentation 

Below there are several useful links pointing to release-specific
documentation.<!-- Add an introduction here, describing the purpose of this
topic. !--> 

---++ 2.1. Release tdaq-01-09-01

%Y% The release tdaq-01-09-01 is production release. 

Available documentation: 
   * <div class="TML">the core schema</div>
      * <div class="TML">the
      * [[http://pcatd12.cern.ch/releases/tdaq-01-09-01/installed/share/data/daq/schema/core.schema.xml][OKS
      * xml]] file</div>
      * <div class="TML">several
      * [[http://pcatd12.cern.ch/releases/tdaq-01-09-01/installed/share/doc/dal/views/][views
      * (eps, mif, xml)]]&nbsp;created using OKS Schema Editor for sub-sets of
      * the core schema classes</div>
      * <div class="TML">generated
      * [[http://pcatd12.cern.ch/releases/tdaq-01-09-01/installed/share/doc/DAQRelease/html/core.schema.xml][XSLT]]
      * description for all classes</div>
   * <div class="TML">the
   * [[http://pcatd12.cern.ch/doxygen/tdaq-01-09-01/html/namespacedaq_1_1core.html][C++
   * doxygen]] generated documentation</div>
   * <div class="TML">the
   * [[http://pcatd12.cern.ch/javadoc/tdaq-01-09-01/dal/package-summary.html][JavaDoc]]
   * generated documentation</div>

---++ 2.2. Release tdaq-02-00-00

%Y% The release tdaq-02-00-00 is new release. 

Available documentation: 
   * <div class="TML">the core schema</div>
      * <div class="TML">the
      * [[http://pcatd12.cern.ch/releases/tdaq-02-00-00/installed/share/data/daq/schema/core.schema.xml][OKS
      * xml]] file</div>
      * <div class="TML">several
      * [[http://pcatd12.cern.ch/releases/tdaq-02-00-00/installed/share/doc/dal/views/][views
      * (eps, mif, xml)]]&nbsp;created using OKS Schema Editor for sub-sets of
      * the core schema classes</div>
      * <div class="TML">generated
      * [[http://pcatd12.cern.ch/releases/tdaq-02-00-00/installed/share/doc/DAQRelease/html/core.schema.xml][XSLT]]
      * description for all classes</div>
   * <div class="TML">the
   * [[http://pcatd12.cern.ch/doxygen/tdaq-02-00-00/html/namespacedaq_1_1core.html][C++
   * doxygen]] generated documentation</div>
   * <div class="TML">the
   * [[http://pcatd12.cern.ch/javadoc/tdaq-02-00-00/dal/package-summary.html][JavaDoc]]
   * generated documentation</div>

---++ 2.3. Release nightly 

%X% The availability of documentation for nightly release depends on the
%[[http://pcatd12.cern.ch/cmt/releases/nightly.html][status]] of the nightly
%build. If the build fails, it may be unavailable. In such case contact the
%software librarian. 

Available documentation: 
   * <div class="TML">the core schema</div>
      * <div class="TML">the
      * [[http://pcatd12.cern.ch/releases/nightly/installed/share/data/daq/schema/core.schema.xml][OKS
      * xml]] file</div>
      * <div class="TML">several
      * [[http://pcatd12.cern.ch/releases/nightly/installed/share/doc/dal/views/][views
      * (eps, mif, xml)]]&nbsp;created using OKS Schema Editor for sub-sets of
      * the core schema classes</div>
      * <div class="TML">generated
      * [[http://pcatd12.cern.ch/releases/nightly/installed/share/doc/DAQRelease/html/core.schema.xml][XSLT]]
      * description for all classes</div>
   * <div class="TML">the
   * [[http://pcatd12.cern.ch/doxygen/nightly/html/namespacedaq_1_1core.html][C++
   * doxygen]] generated documentation</div>
   * <div class="TML">the
   * [[http://pcatd12.cern.ch/javadoc/nightly/dal/package-summary.html][JavaDoc]]
   * generated documentation</div>

---+ 3. Basic Concepts

Below there is description of several main classes, algorithms and utilities
provided by the DAL package. 

---++ 3.1. Partition Class

A partition is a sub-set of the ATLAS systems and detectors for the purpose of
data taking. In the configuration database it is described by an object of the
*Partition* class. The participating systems and detectors are described as
objects of the *Segment* class, linked with partition object.

<div style="text-align: center;"> %ATTACHURL%/Partition.gif </div>

---++ 3.2. Segment Classes

A segment is self-sufficient part of the system which can be configured and
controlled independently from the rest of the TDAQ system. A segment
represents a detector, a system or their part. A segment can include other
segments. For example: 
   * <div class="TML">the Tile detector segment includes tile EBA, EBC, LBA,
   * LBC and monitoring segments; the Tile segment or any it's sub-segments
   * can be included into partition individually</div>
   * <div class="TML">the partition includes ROS, EB, LVL2, EF TDAQ and
   * several detector segments</div>

A segment is controlled by associated RC controller application. 

In the configuration database a segment is described by an object of the
*Segment* class. To be used by the partition it has to be added to the
partition's _Segments_ relationship. To be temporary ignored or taken out
(e.g. for tests, fixing problems, etc.) a segment can be disabled, i.e. added
to the partition's _Disabled_ relationship. When a segment is disabled, the
DAL algorithms consider all nested segments also disabled. The nested segments
are linked with parent segment via _Segments_ relationship.

<div style="text-align: center;"> %ATTACHURL%/Segment1.gif </div>

In addition to nested segments, a segment can include applications and
resources. The resources are described by objects of classes derived from the
*ResourceBase* class and the applications are described by objects of classes
derived from the *BaseApplication* class. The resources are linked with
segment via _Resources_ relationship. There are several types of applications
and depending of it's type an application can be linked with segment via
different relationships (see next section). 

<div style="text-align: center;"> %ATTACHURL%/Segment2.gif </div>

---++ 3.3. Application Classes

An application object corresponds to a process or several processes to be
started under certain conditions. An application is described a class derived
from the *BaseApplication* class. There are two main sub-types of
applications: 
   * the _normal_ applications, which specify computer where to run the
   * process (the relationship is empty for _localhost_ partitions) and
   * correspond to one-and-only-one process to be started; such applications
   * are described by an object of the *Application* class or an object of
   * class derived from it; a normal application object belongs to
   * one-and-only-one segment;
   * the _template_ applications, which specify set of computers where similar
   * processes have to started; such applications are described by an object
   * of the *TemplateApplication* class or an object of class derived from it;
   * a template application object can be shared between several segments;
   * more information about template applications can be found in the
   * [[http://edms.cern.ch/document/684859][Template Applications Proposal]]
   * document.

<div style="text-align: center;"> %ATTACHURL%/Applications.gif </div>

The normal applications can be linked with Segment by one of the following
ways: 
   * via _Applications_ relationship (typical user application);
   * via _Resources_ relationship (when application is a resource, see
   * Resources section for more information)
   * via _Infrastructure_ relationship (vital segment's infrastructure
   * applications; to be run before any other applications in this segment;
   * have associated list of backup computes to be restarted on one of them in
   * case of problems with default one)

<div style="text-align: center;"> %ATTACHURL%/ApplicationsOfSegment.gif </div>

The template applications can be linked with special template segment (an
object of *HLTSegment* or derived class) via _TemplateApplications_
relationship. 

The segment's controller application is linked with it's segment via
_IsControlledBy_ relationship. The controller can be a normal application or
template application. In the latter case the segment's _DefaultHost_
relationship has to point to an object of the Computer class (except the
_localhost_ partitions). 

<img width="16" alt="" src="%PUBURL%/TWiki/TWikiDocGraphics/tip.gif"
height="16" classname="undefined">&nbsp;An application has to be linked with
segment only using one relationship. For example, a resource application
object (i.e. when it's class has two base classes: the !ResourceBase and the
Application) has to be linked with segment object only via _Resources_
relationship; it shall not be added to the _Applications_ relationship at the
same time. 

---+++ 3.3.1. Application Names

To be uniquely identified in the system, each process created from the
application object has unique name. Such names are used by applications to
publish information about themselves in
[[http://atlas-tdaq-monitoring.web.cern.ch/atlas-tdaq-monitoring/IS/Welcome.htm][IS]],
to create log or data files, etc. For normal applications the unique name is
equal to the application database object unique ID. For template applications
such name is calculated dynamically. It was made as short as possible without
losing useful information allowing identifying the application. The format of
template application names is the following:
   * the "appID:segmentID:short-hostID:instance" is used for most template
   * applications, e.g. "PT:EFarm10:pc-tdq-ef-22:3"
   * the "DcName-DcAppInstanceId" is used for Level-2 data-collection
   * applications, e.g. "L2PU-7654"
   * the "segmentID:short-hostID" is used for template controllers (one per
   * host and per segment), e.g. "EFarm10:pc-tdq-ef-22"

%X% Since usage of the message passing instance ID in the level-2 application
%name is the mandatory requirement of the level-2 community, the mapping
%between level-2 application name and corresponding configuration database
%object, a segment it belongs and a host where it is running is not trivial.
%The calculation of the data collection instance ID requires knowledge of the
%message passing node ID, that in turn requires iteration through all
%segments, resources and applications defined in the partition to find all
%level-2 template applications. That in addition makes such mapping an
%expensive operation from database point of view. One of the ways to know such
%mapping is the usage of the [[#DalDumpAppConfigUtility][dal_dump_app_config]]
%binary (see below for more info).

---++ 3.4. Resource Classes

A _simple resource_ is the smallest part of the ATLAS TDAQ system which can be
individually disabled (i.e. masked out of the ATLAS TDAQ), and possibly
enabled, without stopping the data taking process.

A _resource set_ consists of simple resources or another resource sets and it
is used to describe closely-coupled resources, where disabling/enabling of
single resource may affect a necessity to disable/enable others. Disabling of
the resource set means disabling of all resources belonging to it.

In the configuration database a simple resource is described by an object of
the *Resource* class and a resource set is described by the *ResourceSet*
class. To be used by the segment it has to be added to the segment's
_Resources_ relationship. Like in case with segments, to be temporary ignored
or taken out (e.g. for tests, fixing problems, etc.) a resource can be
disabled, i.e. added to the partition's _Disabled_ relationship. When a
resource set is disabled, the DAL algorithms consider all nested resources
also disabled. The nested resource objects are linked with parent resource set
via _Contains_ relationship. 

There are two special types of the resource set: the _resource-set-or_ and
_resource-set-and_, which are described by objects of the *ResourceSetOr* and
the *ResourceSetAnd* configuration database class. The DAL algorithms consider
objects of those classes automatically disabled, when respectively any or all
nested resources of that resource sets are disabled. For more information
about these classes see the [[http://edms.cern.ch/document/812273][Cabling
Description Schema Extension Proposal]] document and
[[TDAQConfigSchemaExtension][relevant discussion with detectors]].

<div style="text-align: center;"> %ATTACHURL%/Resources.gif </div>

---++ 3.5. Software Repository Classes and Utilities

An application configuration object is linked with _software-object_ (i.e.
_computer-program_ or _script_ object created from related *Binary* or
*Script* database class) belonging to a software repository. A software
repository object (i.e. an object of the *SW_Repository* class) describes
common properties for all software objects it contains. In particular such
properties are:
   * installation paths to the software objects it contains (i.e. binaries,
   * scripts, libraries and jar files)
   * common process environment to be set for above software objects
   * the IS-info files describing IS data created by above software objects
   * the IGUI panels dealing with information or status of above software
   * objects
   * other used software repositories

A software repository is considered to be _used_ in the scope of partition, if
there is an application using it and belonging to a segment of this partition.
The disabled segments and resource applications are also taken into account.

A software repository corresponds to the software releases built using CMT.
This allows assuming standard paths for installation of the computer programs,
scripts and libraries. There is special *SW_ExternalPackage* class which is
used for third-party software releases and packages, where mapping between
names of directories for installed libraries and standard CMT tags is required
(for more information see the [[http://edms.cern.ch/document/732735][Proposals
for Description of External Packages]] document).

<div style="text-align: center;"> %ATTACHURL%/SW_Repository.gif </div>

A software repository description can be created manually using OKS tools, or
can be generated by the DAL utility _dal_create_sw_repository_. The latter one
is integrated into TDAQ release build and also used some detectors. Below
there are more details about software repository properties and their
generation.

---+++ 3.5.1. Generation of Software Objects

To add computer programs and scripts into software repository one has to put
few macros into cmt/requirements file of package, which builds or installs
them. The syntax of the macros is the following:

<verbatim>
    macro sw.repository.binary.${NAME}:${property}     "value"
    macro sw.repository.script.${NAME}:${property}     "value"
    macro sw.repository.java.${NAME}.jar:${property}   "value"
</verbatim>

The ${NAME} defines the object ID of the generated software object. If the
binary.name property is not set explicitly, then it has to be equal to the
computer program or script name (e.g. ipc_server, rdb_server, igui_start,
etc.) or jar file name.

The allowed properties are:
| *Property* | *Value* |
| name  | Short description.  |
| binary.name  | Explicitly define script or binary name.  |
| description  | Explicitly provide software object name; if not defined, is
extracted from script or binary running with _--help_ command line option.  |
| help.url  | Set help URL describing software object.  |
| default.parameters  | Set default parameters for script or binary.  |
| needs.resource  | Set RM resources used by the script or binary. Can be
repeated several times to set multiple resources.  |
| needs.environment  | Set process environment required by the script or
binary. Can be repeated several times to set multiple environment variables.
|
| includes  | Include database files containing configuration objects required
for description of this software object. Can be repeated several times to
include several files.  |
| uses  | Set used software repositories and external packages. Can be
repeated several times to set usage of several objects.  |

To be generated, at least one above macro describing software object has to be
put into requirements file.

An example is shown below:

<pre>
      # <i>generate description of binary object loading IS info</i>
    macro <b>sw.repository.binary.</b>dal_load_is_info_files:<b>name</b>
"load IS info files on rdb server"

      # <i>generate description for dal.jar file</i>
    macro <b>sw.repository.java.</b>dal.jar:<b>name</b>           "core dal"
    macro <b>sw.repository.java.</b>dal.jar:<b>description</b>    "generated
dal for classes defined by the core.schema.xml"
    macro <b>sw.repository.java.</b>dal.jar:<b>help.url</b>
"https://twiki.cern.ch/twiki/bin/save/Atlas/DaqHltDal"
</pre>

---+++ 3.5.2. Generation of External Packages and Variables

To generate description of the external software packages one has to put
macros using the following syntax:

<verbatim>
    macro sw.external.package.${NAME}:${property}     "value"
</verbatim>

The ${NAME} defines the object ID of the generated package object. The allowed
properties and meaning of their values are:

| *Property* | *Value* |
| description  | Description of the external package.  |
| installation.path  | The package's top-level directory, i.e. the root
directory of all package' subdirectories.  |
| cmt.tag  | The CMT tag, for which current description is generated.  |
| lib.mapping  | Mapping of the path to installed libraries of this package
for given CMT tag. The patch is relative to the intallation path.  |
| bin.mapping  | Mapping of the path to installed binaries of this package for
given CMT tag. The patch is relative to the intallation path.  |
| uses  | Set used external packages. Can be repeated several times to set
usage of several objects.  |
| needs.environment  | Set process environment required by the script or
binary. Can be repeated several times to set multiple environment variables.
|

To be generated, at least the _installation.path_, the _cmt.tag_ and
_lib.mapping_ macros describing software package have to be put into
requirements file.

An example for package CORAL for i686-slc4-gcc34-opt CMT tag is shown below:
<pre>
    macro <b>sw.external.package</b>.CORAL:<b>installation.path</b>
'${CORAL_HOME}'
    macro <b>sw.external.package</b>.CORAL:<b>cmt.tag</b>
i686-slc4-gcc34-opt
    macro <b>sw.external.package</b>.CORAL:<b>lib.mapping</b>
slc4_ia32_gcc34/lib
    macro <b>sw.external.package</b>.CORAL:<b>bin.mapping</b>
slc4_ia32_gcc34/bin
</pre>

%ICON{note}% The above example uses a variable. The generation of
%package-specific variables normally should be done at the same moment as
%generation of the package, and the description of variables should be stored
%in the same xml file, as description of their packages.

To generate description of the external software packages one has to put
macros using the following syntax:

<verbatim>
    sw.environment.variable.${NAME}:${property}     "value"
</verbatim>

The ${NAME} defines the object ID of the generated package object, which is
equal to the variable name. The allowed properties and meaning of their values
are:

| *Property* | *Value* |
| value  | Value of the variable.  |
| description  | Description of the variable.  |

The _value_ macro is mandatory to generate description of a variable object.

An example of variables for package CORAL is shown below:

<pre>
    macro <b>sw.environment.variable</b>.LCG_INST_PATH:<b>value</b>
/afs/cern.ch/sw/lcg
    macro <b>sw.environment.variable</b>.CORAL_VERSION:<b>value</b>
CORAL_1_9_0
    macro <b>sw.environment.variable</b>.CORAL_HOME:<b>value</b>
${LCG_INST_PATH}/app/releases/CORAL/${CORAL_VERSION}
</pre>

%ICON{more}% The generation of the description of external packages and their
%variables should be done for each supported CMT tag. The
%_dal_create_sw_repository_ generation utility should be run for each
%supported tag using the xml file generated on previous step, e.g.:
<pre>
      # <i><b>create</b> description for i686-slc4-gcc34-opt</i>
    dal_create_sw_repository -r i686-slc4-gcc34-opt.external.macros -o
externals.data.xml -e SEAL CORAL ...
      # <i><b>add</b> description for i686-slc4-gcc34-dbg</i>
    dal_create_sw_repository -r i686-slc4-gcc34-dbg.external.macros -o
externals.data.xml -e SEAL CORAL ...
      # <i><b>add</b> description for i686-slc3-gcc323-opt</i>
    dal_create_sw_repository -r i686-slc3-gcc323-opt.external.macros -o
externals.data.xml -e SEAL CORAL ...
</pre>
Above example will generate description of SEAL, CORAL, etc. packages for 3
platforms. Each sw package may have own mapping of directories containing
libraries and binaries files and values of variables depending on platform.
The core schema and the generation utility support the multi-value environment
variables, which value depend on platform, e.g. environment variable
SEAL_PLUGINS has value dependent on CMT tag:
<pre>
    ${COOL_HOME}/<b>slc4_ia32_gcc34</b>/lib/modules:${SEAL_HOME}/<b>slc4_ia32_gcc34</b>/lib/modules:...
# <i>on i686-slc4-gcc34-xxx</i>
    ${COOL_HOME}/<b>slc3_ia32_gcc323</b>/lib/modules:${SEAL_HOME}/<b>slc3_ia32_gcc323</b>/lib/modules:...
# <i>on i686-slc3-gcc323-opt</i>
</pre>

---+++ 3.5.3. Generation and Calculation of Used IS Info Files

The IS info schema files contain description of data created by the binaries
belonging to the software repository. Such files have to be loaded in special
rdb_server to make such descriptions available online to some IS applications.
The software repository object stores names of such files in the
_ISInfoDescriptionFiles_ multi-string attribute (the names are relative to the
repository' installation path). The list of such files is calculated by the
_dal_load_is_info_files_ utility, reading the configuration database and
checking all software repositories using by given partition.

To be automatically generated by the dal_create_sw_repository utility, the IS
info files have to be described using the following macros put into
appropriate CMT requirements files:

The syntax:
<verbatim>
    macro sw.repository.is-info-file.${FILE}:name "description"
</verbatim>

Above the FILE value is the filename relative to the repository installation
path.

The example below shows how to add the file
${TDAQ_INST_PATH}/share/data/oks2coral/oks-archive-info.xml to the list of
used IS info files:

<pre>
    macro
<b>sw.repository.is-info-file.</b>share/data/oks2coral/oks-archive-info.xml:<b>name</b>
"OKS Archive Info"
</pre>

---+++ 3.5.4. Generation and Calculation of IGUI Properties and Required Java
Jar Files

When IGUI starts, it has to load user-defined panels or in more wide scope to
apply user-specific properties. The calculation of complete list of such
properties and associated java jar files is implemented via configuration
database. The user-defined properties and required jar files are associated
with the software repositories. They are taken into account for any software
repository used by given partition. The list of such properties is calculated
by the _dal_get_igui_setup_ utility, reading the configuration database and
checking all software repositories using by given partition. This utility is
internally used by IGUI start script. The properties are stored by the sw
repository _IGUIProperties_ multi-value string attribute.

To be automatically generated by the dal_create_sw_repository utility, the
IGUI properties have to be described in the CMT requirements files defined
using the following syntax:

<verbatim>
    sw.repository.igui-properties.${NAME}: "java property"
</verbatim>

The NAME value is an arbitrary property name. It is reserved for future usage,
for example:

<pre>
    macro <b>sw.repository.igui-properties</b>.logfile:
"-Digui.logfile=${TDAQ_LOGS_PATH}/igui.out"
    macro <b>sw.repository.igui-properties</b>.L1CaloPanel:
"-Digui.panel=l1calo.L1CaloPanel "
</pre>

The IGUI Java property value should have a format -D${property}=${value}. For
multiple entries of properties with the same name, the values are put into
colon-separated list. Such technique is used for IGUI panels. For example see
value of _IGUI_PROPERTIES_ variable from below example.
The Java CLASSPATH is concatenated from jar files of all used software
repositories. See example below for M4 combined partition:

<pre>
    bash$ dal_get_igui_setup -d
oksconflibs:combined/partitions/m4_combined.data.xml -p m4_combined -s sh
    export <b>__IGUI_PROPERTIES__</b>="  \
        -Digui.ed=TileCaledPanel -Digui.logfile=/logs/M4/m4_combined/igui.out
\
        -Digui.panel=TGCI_ParametersPanel:TGCI_StatusPanel:TileCalIguiPanel:igui.SctSupervisorPanel:l1calo.L1CaloPanel
\
        -Dl1calo.root=/det/l1calo/releases/pro/installed
-Donline.isServer.name=LargParams \
        -Donline.panel.name=LargOnlinePanel -Donline.root.segment=LArg"
    export
<b>__IGUI_CLASSPATH__</b>="/det/l1calo/releases/l1calo-00-05-15/installed/share/lib/l1calo.jar:\
        /det/l1calo/releases/l1calo-00-05-15/installed/share/lib/l1calo_dal.jar:\
        /det/l1calo/releases/l1calo-00-05-15/installed/share/lib/l1calo_ed.jar:\
        ...
        /det/muon/sw/installed//share/lib/TGCPanel.jar"
</pre>

---+++ 3.5.5. Installation Path Variables

In many cases it is usefull to have a
[[#4_1_3_Converter_for_substitution][substitution parameter]] pointing to the
software repository installation area and a process environment variable with
the same value. Such variables can be created automatically by DAL algorithms.
To do this the sw repository' _InstallationPathVariableName_ has to be filled
by a variable name. For all applications using such software repository the
relevant process environment variable will be created on fly. As well, the
similar substitution parameter will be created at scope of partition.

For example for M4 combined partition:
   * object "L1Calo@SW_Repository"
      * attribute
      * !InstallationPath="/det/l1calo/releases/l1calo-00-05-15/installed"
      * attribute !InstallationPathVariableName="L1CALO_INST_PATH"
      * %ICON{hand}% result automatic generation of
      * !L1CALO_INST_PATH="/det/l1calo/releases/l1calo-00-05-15/installed"
      * variable for all !L1Calo application
   * object "Online@SW_Repository"
      * attribute !InstallationPath="/sw/atlas/tdaq/tdaq-01-08-01/installed"
      * attribute !InstallationPathVariableName="TDAQ_INST_PATH"
      * %ICON{hand}% result automatic generation of
      * TDAQ_INST_PATH="/sw/atlas/tdaq/tdaq-01-08-01/installed" variable for
      * all applications (_all_ since any one is using TDAQ)

---+++ 3.5.6. Extendable Software Package Variables

The SW_PackageVariable class describes expendable environment variables
defined by the software packages (links the variables via new
!AddProcessEnvironment relationship). The class defines the variable name and
the suffix concatenated with the installation path of sw package it is linked
with. When the same package variable is linked with several packages, their
values are concatenated with colon (i.e. ':') separator. The values defined
via such mechanism are prefixed to a normal variable value, if it is defined.

---+++ 3.5.7. Generation of Segment-Wide Process Environment by Infrastructure
Applications

An infrastructure application server may provide service used by all
applications running inside this segment (e.g. rdb_server, is_server,
dbproxy). It is necessary to pass the name of the server to all it's clients.
This process can be automated using process environment variables generated by
DAL algorithm using values of attributes !SegmentProcEnvVarName,
!SegmentProcEnvVarParentName and !SegmentProcEnvVarValue of the
!InfrastructureApplication class.

If value of the !SegmentProcEnvVarName attribute is non-empty, the process
environment variable with name equal to value of this attribute is created for
any application of the segment the infrastructure application belongs to (use
case: pass name of server to all clients in the segment). The value of this
variable is calculated depending on the value of the !SegmentProcEnvVarValue
attribute: it either can be the application ID, or the name of the host the
infrastructure application runs on.

If value of the !SegmentProcEnvVarParentName attribute is not empty, the
process environment variable with name equal to the attribute's value is
generated for all applications of the segment. The value of the environment is
equal to value set for variable corresponding to the !SegmentProcEnvVarName
from a parent segment (use case: pass name of top-level server to the server
of this segment, e.g. from intermediate dbproxy to it's child).

---++++!! Example: segment rdb_server

   1. set rdb_server's !SegmentProcEnvVarName=TDAQ_DB_NAME and
!SegmentProcEnvVarValue=appId
   1. run rdb server with option "-a TDAQ_DB_NAME"; %BR%
   %H% the "-a" option says: take name from environment with name
   %TDAQ_DB_NAME; %BR%
   %X% do not use -d XYZ command line option and do not create any process
   %environment to pass name of rdb_server to segment's applications as it was
   %before!
   1. as result of above, the rdb_server will be run with unique application
ID and this ID will be passed via TDAQ_DB_NAME process environment variable to
all applications of this segment

---++ 3.6. Process Environment Calculation

The process environment of applications is calculated from the configuration
database. Each application may have own environment variables. The following
algorithm is used:
   * add setup and partition-specific variables: TDAQ_PARTITION,
   * TDAQ_IPC_INIT_REF and TDAQ_DB_PATH
   * add application's object environment (i.e. defined by
   * _ProcessEnvironment_ relationship for given object)
   * add environment of application's program object
   * for direct parent segment of application and parent segments of it's
   * segment (i.e. recursively from low level segment up to top level one
   * belonging to partition object):
      * add environment of segment object;
      * %N% add [[#3_5_7_Generation_of_Segment_Wide][segment-wide
      * environment]] defined by the infrastructure applications as defined by
      * the !SegmentProcEnvVar* variables);
   * add environment of partition object
   * for used software packages:
      * add software repositories
      * [[#3_5_5_Installation_Path_Variable][installation path variables]];
      * %N% extend environment variables via
      * [[#3_5_6_Extendable_Software_Packag][SW_PackageVariable objects]]
      * linked with the software package;
   * calculate TDAQ_DB value taking into account config plug-in technology
   * selected for partition object and running RDB infrastructure servers
   * calculate TDAQ_APPLICATION_OBJECT_ID (contains database object ID) and
   * TDAQ_APPLICATION_NAME (i.e. [[#3_3_1_Application_Names][unique
   * application name]]) variables

In above algorithm once a variable is defined on a high level, it's value will
be ignored from any lower levels. For example, TDAQ_PARTITION or
TDAQ_IPC_INIT_REF variables are defined automatically on the very top level
and cannot be changed by user even if are explicitly linked with application
object. Apart of this example, the environment defined for application has
higher priority, then defined for it's segment or partition. Similarly, the
environment variables defined by explicit parent segment have higher
priorities, than environment coming from top-level segments or partition.

The PATH and LD_LIBRARY_PATH variables are calculated for an application by
the [[DaqHltRunControl][RunControl]] taking into account the sw repositories
and external packages used by the application. It is not recommended to set
those values to an application by any mean.

The process environment of any application can be checked using dal_dump_apps
utility (to use it from command line it is necessary to define TDAQ_DB_DATA
variable often used by the partition object). Run this utility by passing OKS
xml file, partition name and optionally application ID, e.g. as shown below:
<verbatim>
  bash$ export TDAQ_DB_DATA=daq/partitions/be_test.data.xml
  bash$ dal_dump_apps -d oksconflibs:$TDAQ_DB_DATA -p be_test -s -a
RootController
</verbatim>

---+ 4. Recommendations for Developers 

Below there are several guidelines for developers using the generated DAL. 

---++ 4.1. From what to start 

To access any configuration data one has to get the *configuration* object,
then find the *partition* object (that is the _entry point_ to get any another
objects relevant for the configuration) and to register the *converter* for
configuration parameters. The user's binary has to be linked with config and
dal libraries. If user is developing a plug-in or an application on top of the
[[DaqHltRunControl][RunControl]], !DataCollection (ac package), RCD or other
C++ frameworks, or Java-based [[DaqHltIGUI][IGUI]], then all previous steps
already done and the configuration and partition objects can be accessed via
API of above frameworks (see their documentation for more information). If
above is not the case, then above steps need to be done by the code of user's
application and they are described below: 

---+++ 4.1.1. How to create the configuration object 

To create the configuration object one has to call the constructor of the
*Configuration* class. The constructor has string parameter that identifies
which implementation plug-in will be used and what are parameters for this
plug-in. If the parameter of the constructor is empty, then the constructor
will use value of *TDAQ_DB* environment variable for it. When an application
is running by _setup_daq_, the *TDAQ_DB* variable is always created and set
into right value, so the user may leave the parameter of the constuctor empty.
In case of errors the constructor throws an exception. 

---++++!! C++ Example 

Read configuration from file _"daq/partitions/be_test.data.xml"_ using oks
plug-in. 

<verbatim>
    #include "conffwk/Configuration.h"
    ...
    try {
      ::Configuration db("oksconflibs:daq/partitions/be_test.data.xml");
      ... // user's code accessing configuration data
    }
    catch(dunedaq::conffwk::Exception & ex) {
      std::cerr << "Caught config exception:\n" << ex << std::endl;
    }
</verbatim>

To use value of TDAQ_DB variable leave parameter of the constructor empty: 

<verbatim>
    ::Configuration db("");
</verbatim>

---++++!! Java Example 

Below there is an example reading data from rdb server with name _"RDB"_
running in the initial partition. 

<verbatim>
    import config.Configuration;
    ...
    try {
      config.Configuration db = new config.Configuration("rdbconfig:RDB");
    }
    catch (config.SystemException ex) {
      System.err.println( "Caught \'config.SystemException\':\n" +
ex.getMessage());
    }
</verbatim>

---+++ 4.1.2. Get partition object 

To get the partition object one has use DAL's algorithm *get_partition()*
defined for the *Partition* database class. The algorithm has string attribute
to find the partition object by ID. If it's value is empty, then value of
*TDAQ_PARTITION* variable is used. Similarly to the Configuration class, the
user may leave this parameter empty, if his application is running by
_setup_daq_ that always creates the variable with correct value. If the
partition object with such ID does not exist, then the _null_ is returned. 

---++++!! C++ Example 

Get partition object with ID _"be_test"_. 

<verbatim>
    #include "dal/Partition.h"
    #include <dal/util.h>
    ...
    ::Configuration db("oksconflibs:daq/partitions/be_test.data.xml");
    if(const daq::core::Partition * p = daq::core::get_partition(db,
"be_test")) {
      ... // work with object p
    }
</verbatim>

---++++!! Java Example 

Get partition object with ID _"be_test"_. 
<verbatim>
    import config.Configuration;
    import dal.Partition;
    ...
    try {
      config.Configuration db = new config.Configuration("");
      dal.Partition p = dal.Algorithms.get_partition(db, "be_test");
      if(p != null) {
        ... // work with object p
    }
    catch (config.SystemException ex) {
      System.err.println( "Caught \'config.SystemException\':\n" +
ex.getMessage());
    }
</verbatim>

---+++ 4.1.3. Converter for substitution of variables

In some cases attributes can or shall have equal values or parts of them. For
example they can contain name of directory where software is installed, where
data are stored, where log files have to be written, etc. To avoid a necessity
to update several attributes synchronously and to related problems because of
inconsistent update, the configuration service supports the parameterization
via so-called *parameter* variables. If the value of a string attribute has to
be paramertized, then: 
   * the name of the parameter to be put inside braces and prefixed by dollar
   * sign, e.g. _"${LOGS_DIR}/my.log"_, where the LOGS_DIR is a parameter to
   * define directory for log files; if the LOGS_DIR="/tmp", the file name is
   * "/tmp/my.log"
   * the parameter to be created as an object of the *Variable* class and
   * linked with either partition or used segment object, e.g. for above
   * example on can to create variable with Name="LOGS_DIR" and Values="/tmp"
   * and to link it with user's segment via _"Parameters"_ relationship.

The mechanism of above mentioned strings parameters substitution is
implemented as generic configuration service attribute converter. Such
converter is not registered automatically, when the configuration object is
build by two main reasons: 
   * there are cases, when the automatic substitution shall not be done, e.g.
   * for database editors;
   * the parameters are partition and segments specific, so the configuration
   * object has no any special knowledge about them and what has to be done,
   * when those objects are updated.

To register the converter for strings attributes substitution the user has to
create the converter object and to register it on the configuration object,
e.g. as it is shown below. 

---++++!! C++ Example 

<verbatim>
    #include "conffwk/Configuration.h"
    #include "dal/Partition.h"
    #include "dal/util.h"
    ...
    try {
      Configuration db;
      if(const daq::core::Partition * partition = daq::core::get_partition(db,
"be_test")) {
        db.register_converter(new daq::core::SubstituteVariables(db,
*partition));
      }
    }
    catch(dunedaq::conffwk::Exception & ex) {
      std::cerr << "Caught config exception:\n" << ex << std::endl;
    }
</verbatim>

---++++!! Java Example 

<verbatim>
    import config.Configuration;
    import dal.Algorithm;
    import dal.SubstituteVariables;
    import dal.Partition;
    ...
    try {
      config.Configuration db = new config.Configuration("");
      dal.Partition p = dal.Algorithms.get_partition(db, "be_test");
      if(p != null) {
        db.register_converter(new dal.SubstituteVariables(db, p));
      }
    }
    catch (config.SystemException ex) {
      System.err.println( "Caught \'config.SystemException\':\n" +
ex.getMessage());
    }
</verbatim>

---+++ 4.1.4. Linkage 

For C++ it is enough to link against generated DAL and config libraries: 
<verbatim>
    -ldaq-core-dal -lconfig
</verbatim>
%ICON{note}% The implementation plug-ins like liboksconflibs.so, librdbconfig.so
%and low level libraries used by them (e.g. liboks.so, librdb.so, etc.) are
%loaded dynamically and not needed to be linked with your binaries. It is
%enough, if they will be referenced by your LD_LIBRARY_PATH. 

For Java the dal.jar and config.jar files have to be in the CLASSPATH. The
implementation plug-ins like oksconflibs.jar or rdbconfig.jar have to be in the
CLASSPATH as well. 

---++ 4.2. Applications

---+++ 4.2.1. Iterate all applications

There are two ways to get list of applications defined for the partition:
   * %Y% use get_all_applications() algorithm; if necessary, user can filter
   * out applications by type, segment and computer masks.
   * %ICON{choice-no}% go through tree of segments and calculate applications
   * for each of them; it is not recommended, since user has to know about
   * rules for normal and template applications, resources, resource sets and
   * their disabling, segment's infrastructure applications and controllers,
   * etc.

---++++ The get_all_applications algorithm

To get all applications defined for given partition one has to use
*Partition::get_all_applications()* algorithm, which is available for C++ and
Java DAL.

The C++ propotype is:
<verbatim>
    void daq::core::Partition::get_all_applications(
        std::vector<daq::core::AppConfig>& out, Configuration& db,
        std::set<std::string> * app_types = 0,
        std::set<const Segment *> * use_segments = 0,
        std::set<const Computer *> * use_hosts = 0
    ) const;
</verbatim>

where:
   * the _out_ parameter is the result of the algorithm's work (see
   * [[http://isscvs.cern.ch/cgi-bin/viewcvs-all.cgi/DAQ/online/dal/dal/app-config.h?root=atlastdaq&view=markup][dal/app-config.h]]
   * file or
   * [[http://pcatd12.cern.ch/doxygen/tdaq-01-08-04/html/classdaq_1_1core_1_1AppConfig.html][DoxyGen]]
   * for more information about *AppConfig* class to get application
   * parameters such as: application id, data collection node id, pointers to
   * application, segment and host configuration database objects);
   * the optional _app_types_ parameter defines set of application class names
   * (also takes into account their subclasses), which objects have to be
   * taken into account (use all applications, if the parameter is 0); 
   * the optional _use_segments_ parameter defines set of segments, which
   * applications have to be taken into account (use all segments, if the
   * parameter = 0); 
   * the optional _use_hosts_ parameter defines set of hosts where the
   * applications have to run on (use all hosts, if the parameter = 0). 

Above optional parameters can be combined.

The similar algorithm is defined for Java DAL:

<verbatim>
    dal.AppConfig[] dal.Partition.get_all_applications(
        String[] app_types,
        dal.Segment[] use_segments,
        dal.Computer[] use_hosts
    );
</verbatim>

The details of the *dal.AppConfig* can be found in the
[[http://isscvs.cern.ch/cgi-bin/viewcvs-all.cgi/DAQ/online/dal/jsrc/dal/AppConfig.java?root=atlastdaq&view=markup][dal/jsrc/dal/AppConfig.java]]
file.

#DalDumpAppConfigUtility To test get_all_applications() algorithm work there
is dedicated binary dal_dump_app_config (see also it's
[[http://isscvs.cern.ch/cgi-bin/viewcvs-all.cgi/DAQ/online/dal/examples/dal_dump_app_config.cpp?root=atlastdaq&view=markup][source]]
as example of code):

<verbatim>
    Usage: dal_dump_app_config [-d database-name] -p partition [-t [types
...]] [-c [ids ...]] [-s [ids ...]] 
    Options/Arguments: 
      --data | -d  database-name         name of the database (ignore TDAQ_DB
variable) 
      --partition-name | -p partition    name of the partition object 
      --application-types | -t types     filter out all applications except
given classes (and their subclasses) 
      --hosts | -c ids                   filter out all applications except
those which run on given hosts 
      --segments | -s ids                filter out all applications except
those which belong to given segments 
</verbatim>

Example below shows how to get all template and run control applications on
computer lxplus002 for a test partition (the Computer column is filtered out):

<verbatim>
    bash$ dal_dump_app_config -d
oksconflibs:daq/partitions/lxplus_template_tests.data.xml \
      -p lxplus-test -c lxplus002.cern.ch -t TemplateApplication
RunControlApplication
    ===========================================================================================================
    | num | Application Object                      | Segment                |
MP:id | Application unique id  |
    ===========================================================================================================
    |   1 | test-L2@L2PUTemplateApplication         | lxplus01-19@HLTSegment |
32763 | L2PU-8187              |
    |   2 | test-L2@L2PUTemplateApplication         | lxplus01-19@HLTSegment |
32762 | L2PU-8186              |
    |   3 | test-L2@L2PUTemplateApplication         | lxplus01-19@HLTSegment |
32761 | L2PU-8185              |
    |   4 | test-L2@L2PUTemplateApplication         | lxplus01-19@HLTSegment |
32760 | L2PU-8184              |
    |   5 | rc@RunControlTemplateApplication        | lxplus01-19@HLTSegment |
0 | lxplus01-19:lxplus002  |
    |   6 | ExampleRC@RunControlTemplateApplication | ROSSegment-1@Segment   |
0 | ROSSegment-1:lxplus002 |
    |   7 | rc@RunControlTemplateApplication        | testSeg@Segment        |
0 | testSeg:lxplus002      |
    |   8 | RootController@RunControlApplication    | setup@OnlineSegment    |
0 | RootController         |
    |   9 | efd_controller@RunControlApplication    | efd_subfarm@EF_SubFarm |
0 | efd_controller         |
    |  10 | LVL2Segment-1@RunControlApplication     | LVL2Segment-1@Segment  |
0 | LVL2Segment-1          |
    ===========================================================================================================
</verbatim>

The *get_all_applications()* algorithm does not return applications which are
disabled in the scope of partition. However it returns applications for hosts,
which are off (i.e. the _State_ attribute has *false* value). This is done to
allow the !RunControl to inform user about error in case when host of a
critical application is off. If the user needs to skip the applications on
hosts switched off, then the code has to check state of the returned hosts,
e.g.:

<verbatim>
   Configuration db(...);
   daq::core::Partition * partition(...); 
   std::vector<daq::core::AppConfig> app_out;
   partition->get_all_applications(app_out, db);
   for(size_t i = 0; i < app_out.size(); ++i) {
     if (app_out[i].get_host().get_State() == false) {
       // do not take this application into account!
     }
     else {
       ...
     }
   }
</verbatim>

---++ 4.3. Segments and Resources 

---+++ 4.3.1. Build tree of segments and Graph of Resources

The simplest way to build tree of segments is to write recursive function
processing current segment and recursively invoking on nested segments. The
entry point of this function is the list of segments of the partition object.
The simplified fragment of such C++ code from
[[http://isscvs.cern.ch/cgi-bin/viewcvs-all.cgi/DAQ/online/dal/examples/dal_print_segments.cpp?root=atlastdaq&view=markup][dal_print_segments]]
example application is shown below:
<verbatim>
    static void print_segment(const daq::core::Segment& seg, unsigned int
recursion_level)
    {
      std::string s(recursion_level*4, ' ');
      std::cout << s << seg.UID() << std::endl;
      daq::core::SegmentIterator i = seg.get_Segments().begin();
      while(i != seg.get_Segments().end()) {
        print_segment(**i, recursion_level + 1); ++i;
      }
    }
    ...
    Configuration db;
    const daq::core::Partition * p = daq::core::get_partition(db, "");
    db.register_converter(new daq::core::SubstituteVariables(db, *p));
    daq::core::SegmentIterator i = p->get_Segments().begin();
    while(i != p->get_Segments().end()) {
      print_segment(**i, 0); ++i;
    }
</verbatim>

In a similar way for each segment it is possible to build graph of resources
using _Contains_ relationship defined for the !ResourceSet class and
_Resources_ relationship of the Segment class. %BR%
%X% Note, that a resource can belong to several segments or resource sets
%(e.g. a link resource belongs to ROS and ROD resource sets), so in general
%case the resources are linked into a graph and not to a single tree.

---+++ 4.3.2. Check disabled status

A segment or resource is disabled, when it or it's parent is added to the
partition's disabled relationship. In addition a resource can be implicitly
disabled when it is a resource set with _and_ or _or_ logic, or it's parent
belongs to such set.

To get disabled status of a resource or a segment the DAL algorithm
*disabled()* should be used. It is available for both C++ and Java DALs.

<!--***********************************************************--><!--Do NOT
remove the remaining lines, but add requested info as
appropriate--><!--***********************************************************-->

---
<!--For significant updates to the topic, consider adding your 'signature'
(beneath this editing box)--> *Major updates*:%BR% -- Main.isolov - 24 Aug
2007 

<!--Please add the name of someone who is responsible for this page so that
he/she can be contacted if changes are needed.
The creator's name will be added by default, but this can be replaced if
appropriate.
Put the name first, without dashes.-->%RESPONSIBLE% %REVINFO{"$wikiusername"
rev="1.1"}% %BR% <!--Once this page has been reviewed, please add the name and
the date e.g. Main.StephenHaywood - 31 Oct 2006 -->%REVIEW% *Never reviewed* 

%STOPINCLUDE% </img>
```


## Include headers

### `include/dal/ConfigVersion.hpp`  
*Local path: `repo/dune-dal/include/dal/ConfigVersion.hpp`*

```cpp
#ifndef CONFIGVERSION_H
#define CONFIGVERSION_H

#include <is/info.h>

#include <string>
#include <ostream>


// <<BeginUserCode>>

// <<EndUserCode>>
/**
 * The class is used to store GIT version of the OKS database used for given partition.
 * 
 * @author  produced by the IS generator
 */

class ConfigVersion : public ISInfo {
public:

    /**
     * OKS GIT SHA key used for given partition
     */
    std::string                   Version;


    static const ISType & type() {
	static const ISType type_ = ConfigVersion( ).ISInfo::type();
	return type_;
    }

    std::ostream & print( std::ostream & out ) const {
	ISInfo::print( out );
	out << std::endl;
	out << "Version: " << Version << "\t// OKS GIT SHA key used for given partition";
	return out;
    }

    ConfigVersion( )
      : ISInfo( "ConfigVersion" )
    {
	initialize();
    }

    ~ConfigVersion(){

// <<BeginUserCode>>

// <<EndUserCode>>
    }

protected:
    ConfigVersion( const std::string & type )
      : ISInfo( type )
    {
	initialize();
    }

    void publishGuts( ISostream & out ){
	out << Version;
    }

    void refreshGuts( ISistream & in ){
	in >> Version;
    }

private:
    void initialize()
    {

// <<BeginUserCode>>

// <<EndUserCode>>
    }


// <<BeginUserCode>>

// <<EndUserCode>>
};

// <<BeginUserCode>>

// <<EndUserCode>>
inline std::ostream & operator<<( std::ostream & out, const ConfigVersion & info ) {
    info.print( out );
    return out;
}

#endif // CONFIGVERSION_H
```

### `include/dal/util.hpp`  
*Local path: `repo/dune-dal/include/dal/util.hpp`*

```cpp
#ifndef _dal_util_H_
#define _dal_util_H_

#include <exception>

#include "conffwk/Configuration.hpp"
#include "conffwk/DalObject.hpp"


namespace dunedaq {

namespace dal {

    // forward declaration

  class BaseApplication;
  class Partition;
  class SW_Repository;
  class Tag;
  class Computer;


   /**
     *  \brief  Check if given tag can be used on given computer.
     *  
     *  The algorithm reads platforms compatibility description from partition's OnlineSegment.
     *  This allows to describe a host with real hw platform and installed operating system,
     *  and to run on it applications with compatible tags, e.g.:
     *  host with 64 bits SLC5 allows to run applications with x86_64-slc5, i686-slc5 and i686-slc4 tags.
     *
     *  \par Parameters and return value
     *
     *  \param tag             tested tag
     *  \param host            host where the tag is tested
     *  \param partition       partition defining online segment with compatibility info
     *  \return                true, if tag is compatible
     */

  bool is_compatible(const dunedaq::dal::Tag& tag, const dunedaq::dal::Computer& host, const dunedaq::dal::Partition& partition);



    /**
     *  \brief Substitute variables from conversion map or from process environment.
     *
     *  Substitute variables using special syntax like ${FOO}, $(BAR), etc.
     *  If substitution %is defined, then the variables are replaced by the corresponding
     *  substitution value. The substitution values are defined either by the
     *  substitution map, or by the process environment.
     *
     *  \par Parameters and return value
     *
     *  \param value            string containing variables to be substituted
     *  \param conversion_map   pointer to conversion map; if null, the process environment %is used
     *  \param beginning        definition of syntax symbols which delimit the beginning of the variable
     *  \param ending           definition of syntax symbols which delimit the ending of the variable
     *  \return                 Returns the result of substitution.
     *
     *  \par Example
     *
     *  If the conversion map has pair "FOO","BAR", then substitute_variables("/home/${FOO}", cmap, "${", "}") returns "/home/BAR".
     *  Otherwise it returns non-changed value "/home/${FOO}".
     *  <BR>
     *  If there %is environment variable "USER" with value "Online", then substitute_variables("/home/$(USER)", 0, "$()") returns "/home/Online".
     *  Otherwise it returns non-changed value "/home/$(USER)".
     */

  std::string substitute_variables(const std::string& value, const std::map<std::string, std::string> * conversion_map, const std::string& beginning, const std::string& end);

    /**
     *  \brief Implements string converter for database parameters.
     *
     *  The class implements dunedaq::conffwk::Configuration::AttributeConverter for string %type.
     *  It reads parameters defined for given partition object and uses them to
     *  substitute values of database string attributes.
     *
     *  The parameters are stored as a map of substitution keys and values.
     *  If database %is changed, the reset(dunedaq::conffwk::Configuration&, const Partition&) method needs to be used.
     *
     *  \par Example
     *
     *  The example shows how to use the converter:
     *
     *  <pre><i>
     *
     *  dunedaq::conffwk::Configuration db(...);  // some code to build configuration database object
     *
     *  const dunedaq::dal::Partition * partition = dunedaq::dal::get_partition(db, partition_name);
     *  if(partition) {
     *    db.register_converter(new dunedaq::dal::SubstituteVariables(db, *partition));
     *  }
     *
     *  </i></pre>
     *
     */

  class SubstituteVariables : public dunedaq::conffwk::Configuration::AttributeConverter<std::string> {

    public:


        /** Build converter object. **/

      SubstituteVariables(const Partition& p)
      {
        reset (p);
      }


        /** Method to reset substitution map in case of database changes. **/

      void reset(const Partition&);


        /** Implementation of convert method. **/

      virtual void convert(std::string& value, const dunedaq::conffwk::Configuration& conf, const dunedaq::conffwk::ConfigObject& obj, const std::string& attr_name);


        /** Destroy conversion map. **/

      virtual ~SubstituteVariables() {;}


        /** Return conversion map **/

      const std::map<std::string, std::string> * get_conversion_map() const {return &m_cvt_map;}


    private:

      std::map<std::string, std::string> m_cvt_map;
  };


    /**
     *  \brief Get partition object.
     *
     *  The algorithm %is searching the partition object by given name.
     *  If the name %is empty, then the algorithm takes the name from
     *  the TDAQ_PARTITION environment variable.<BR>
     *
     *  The last parameter of the algorithm can be used to optimise performance
     *  of the DAL in case if a database server config implementation %is used.
     *  The parameter defines how many layers of objects referenced by given 
     *  partition object should be read into client's config cache together with
     *  partition object during single network operation. For example:
     *  - if the parameter %is 0, then only partition object %is read;
     *  - if the parameter %is 1, then partition and first layer segment objects are read;
     *  - if the parameter %is 2, then partition, segments of first and second layers, and application/resources of first layer segments objects are read;
     *  - if the parameter %is 10, then mostly probable all objects referenced by given partition object are read.<BR>
     *
     *  The parameters of the algorithm are:
     *  \param conf      the configuration object with loaded database
     *  \param name      the name of the partition to be loaded (if empty, TDAQ_PARTITION variable %is used)
     *  \param rlevel    optional parameter to optimise performance ("the references level")
     *  \param rclasses  optional parameter to optimise performance ("names of classes which objects are cached")
     *
     *  \return Returns the pointer to the partition object if found, or 0.
     */

  const dunedaq::dal::Partition * get_partition(dunedaq::conffwk::Configuration& conf, const std::string& name, unsigned long rlevel = 10, const std::vector<std::string> * rclasses = nullptr);


    /**
     *  \brief Get used software repositories.
     *
     *  The algorithm %is searching the sw repositories used by given partition,
     *  checking all active segments and applications.
     *
     *  The method throws dunedaq::dal::AlgorithmError exception in case of logical problems found in database
     *  (such as circular dependencies between segments, resources or repositories).
     *
     *  The parameters of the algorithm are:
     *  \param p the partition object
     *
     *  \return The used repositories
     */

  std::set<const dunedaq::dal::SW_Repository *> get_used_repositories(const dunedaq::dal::Partition& p);


    /**
     *  \brief Add into CLASSPATH JARs defined by JarFile objects.
     *
     *  The function iterates all SW objects of given repository and tests found JarFile objects.
     *  For each JarFile it checks if corresponding JAR file exists in repository root, patch or installation areas.
     *  First readable jar file is added to the class path.
     *
     *  @param[in] rep               the repository with JarFile objects
     *  @param[in] repository_root   the partition's repository root
     *  @param[in,out] class_path    the value of class path
     *
     *  @throw dunedaq::dal::NoJarFile is thrown when the jar file is not found or not readable.
     */

  void add_classpath(const dunedaq::dal::SW_Repository& rep, const std::string& repository_root, std::string& class_path);


    /**
     * \brief Get OKS GIT version for running partition.
     *
     * The method extracts GIT version for running partition configuration reading value from the RunParams information server.
     * If not set, it tries to extract the value from the TDAQ_DB_VERSION process environment.
     *
     * \param partition the name of the partition
     * \return the configuration version
     *
     *  @throw dunedaq::conffwk::NotFound is thrown if case if partition or information repository does not exist
     *  @throw dunedaq::conffwk::Exception is thrown if case of problems
     */

  std::string
  get_config_version(const std::string& partition);


    /**
     * \brief Set new OKS GIT version for running partition.
     *
     * The method writes version on the RunParams information server and reloads with this version RDB and RDB_RW servers.
     * In initial partition only RDB_INITIAL server is reloaded.
     *
     * \param partition the name of the partition
     * \param version the configuration version
     * \param reload if true, send reload command to RDB and RDB_RW servers
     *
     *  @throw dunedaq::conffwk::NotFound is thrown if case if partition or information repository does not exist
     *  @throw dunedaq::conffwk::Exception is thrown if case of problems
     */

  void
  set_config_version(const std::string& partition, const std::string& version, bool reload);

} // namespace dal


  ERS_DECLARE_ISSUE(
    dal,
    AlgorithmError,
    ,
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadVariableUsage,
    AlgorithmError,
    message,
    ,
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadApplicationInfo,
    AlgorithmError,
    "Failed to retrieve information for Application \'" << app_id << "\' from the database: " << message,
    ,
    ((std::string)app_id)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadPartitionID,
    AlgorithmError,
    "There is no partition object with UID = \"" << name << '\"',
    ,
    ((std::string)name)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    SegmentDisabled,
    AlgorithmError,
    "Cannot get information about applications because the segment is disabled",
    ,
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadProgramInfo,
    AlgorithmError,
    "Failed to retrieve information for Program \'" << prog_id << "\' from the database: " << message,
    ,
    ((std::string)prog_id)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadHost,
    AlgorithmError,
    "Failed to retrieve application \'" << app_id << "\' from the database: " << message,
    ,
    ((std::string)app_id)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    NoDefaultHost,
    AlgorithmError,
    "Failed to find default host for segment \'" << seg_id << "\' " << message,
    ,
    ((std::string)seg_id)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    NoTemplateAppHost,
    AlgorithmError,
    "Both partition default and segment default hosts are not defined for template application \'" << app_id << "\' from segment \'" << seg_id << "\' (will use localhost, that may cause problems presenting info in IGUI for distributed partition).",
    ,
    ((std::string)app_id)
    ((std::string)seg_id)
  )


  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadTag,
    AlgorithmError,
    "Failed to use tag \'" << tag_id << "\' because: " << message,
    ,
    ((std::string)tag_id)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadSegment,
    AlgorithmError,
    "Invalid Segment \'" << seg_id << "\' because: " << message,
    ,
    ((std::string)seg_id)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    GetTemplateApplicationsOfSegmentError,
    AlgorithmError,
    "Failed to get template applications of \'" << name << "\' segment" << message,
    ,
    ((std::string)name)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    BadTemplateSegmentDescription,
    AlgorithmError,
    "Bad configuration description of template segment \'" << name << "\': " << message,
    ,
    ((std::string)name)
    ((std::string)message)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    CannotGetApplicationObject,
    AlgorithmError,
    "Failed to get application object from name: " << reason,
    ,
    ((std::string)reason)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    CannotFindSegmentByName,
    AlgorithmError,
    "Failed to find segment object \'" << name << "\': " << reason,
    ,
    ((std::string)name)
    ((std::string)reason)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    NotInitedObject,
    AlgorithmError,
    "The " << item << " object " << obj << " was not initialized",
    ,
    ((const char *)item)
    ((void *)obj)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    NotInitedByDalAlgorithm,
    AlgorithmError,
    "The " << obj_id << '@' << obj_class << " object " << address << " was not initialized by DAL algorithm " << algo,
    ,
    ((std::string)obj_id)
    ((std::string)obj_class)
    ((void*)address)
    ((const char *)algo)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    CannotCreateSegConfig,
    AlgorithmError,
    "Failed to create config for segment \'" << name << "\': " << reason,
    ,
    ((std::string)name)
    ((std::string)reason)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    CannotGetParents,
    AlgorithmError,
    "Failed to get parents of \'" << object << '\'',
    ,
    ((std::string)object)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    FoundCircularDependency,
    AlgorithmError,
    "Reach maximum allowed recursion (" << limit << ") during calculation of " << goal << "; possibly there is circular dependency between these objects: " << objects,
    ,
    ((unsigned int)limit)
    ((const char *)goal)
    ((std::string)objects)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    NoJarFile,
    AlgorithmError,
    "Cannot find jar file \'" << file << "\' described by \'" << obj_id << '@' << obj_class << "\' that is part of \'" << rep_id << '@' << rep_class << '\'',
    ,
    ((std::string)file)
    ((std::string)obj_id)
    ((std::string)obj_class)
    ((std::string)rep_id)
    ((std::string)rep_class)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    DuplicatedApplicationID,
    AlgorithmError,
    "Two applications have equal IDs:\n  1) " << first << "\n  2) " << second,
    ,
    ((std::string)first)
    ((std::string)second)
  )

  ERS_DECLARE_ISSUE_BASE(
    dal,
    SegmentIncludedMultipleTimes,
    AlgorithmError,
    "The segment \"" << segment << "\" is included by:\n  1) " << first << "\n  2) " << second,
    ,
    ((std::string)segment)
    ((std::string)first)
    ((std::string)second)
  )

} // namespace dunedaq

#endif
```

### `include/dal/app-config.hpp`  
*Local path: `repo/dune-dal/include/dal/app-config.hpp`*

```cpp
#ifndef _dal_app_config_H_
#define _dal_app_config_H_

#include <string>
#include <vector>

namespace dunedaq::dal {

      // forward declarations

    class BaseApplication;
    class Computer;
    class Segment;
    class Partition;
    class Tag;
    class BackupHostFactory;

    /**
     * \brief The class describes application configuration parameters
     *
     *  The class provides methods to get description an application.
     *
     *  It hides differences between normal (i.e. created from \b Application configuration class) and template
     *  (i.e. created from \b TemplateApplication configuration class) applications.
     *  In case of normal application a name (or ID) of application is equal to the unique ID of corresponding
     *  configuration object. For template application it is generated taking into account segment, host and
     *  instance ID, e.g.:
     *  - "segment-name:host-id" for template controller
     *  - "application-id:segment-name:host-id" for template application with instance number = 1
     *  - "application-id:segment-name:host-id:instance-id" for others
     *
     *  The main properties of an application are:
     *  - use method get_app_id() to get application id
     *  - use method get_base_app() to get configuration database object for this application
     *  - use method get_host() to get host where application is running
     *  - use method get_segment() to get configuration object describing segment this application belongs to
     *  - use method get_seg_id() to get segment id (is different from segment configuration object ID for template segments)
     *
     *  An object of AppConfig class may only be created by the SegConfig::get_all_applications() and
     *  the dunedaq::dal::Partition::get_all_applications() algorithms. A user should not create an object of AppConfig class
     *  (constructor remains public by efficiency reasons).
     **/

    class AppConfig
    {

      friend class AlgorithmUtils;
      friend class Partition;

    public:

      /**
       *  The constructor may only used by the SegConfig::get_all_applications() algorithm to create normal application.
       *  It cannot be made truly private by efficiency reasons.
       **/
      AppConfig(const BaseApplication * app, const Computer * host, const dunedaq::dal::Segment * seg);

      /**
       *  The constructor may only used by the SegConfig::get_all_applications() algorithm to create templated application.
       *  It cannot be made truly private by efficiency reasons.
       **/
      AppConfig(const BaseApplication * app, const Computer * host, const dunedaq::dal::Segment * seg, BackupHostFactory& factory);

      /**
       * Get base application object used to configure the application.
       * \throw Throw dunedaq::dal::NotInitedObject if the object was not initialized and cannot be used.
       */
      const BaseApplication *
      get_base_app() const
      {
        return m_base_app;
      }

      /**
       * Get the host where the application runs on.
       * \throw Throw dunedaq::dal::NotInitedObject if the object was not initialized and cannot be used.
       */
      const Computer *
      get_host() const
      {
        return m_host;
      }

      /**
       * Get segment that the application belongs.
       * \throw Throw dunedaq::dal::NotInitedObject if the object was not initialized and cannot be used.
       */
      const Segment *
      get_segment() const
      {
        return m_segment;
      }

      /**
       *  Get backup hosts for this application.
       *
       *  The method returns vector of computers where the application can be restarted in case of problems.
       *
       *  For normal applications the backup hosts are defined via "BackupHosts" relationship.
       *  For template applications with "RunsOn" attribute set to "FirstHostWithBackup" the backup hosts are
       *  randomly chosen from list of segment hosts; there are no backup hosts for other types of template "RunsOn".
       *
       *  \throw Throw dunedaq::conffwk::Exception in case of problems
       */

      std::vector<const Computer *>
      get_backup_hosts() const;

      bool
      get_is_templated() const
      {
        return m_is_templated;
      }

    private:

      const BaseApplication * m_base_app;
      const Computer * m_host;
      const Segment * m_segment;
      bool m_is_templated;
      std::vector<const dunedaq::dal::Computer *> m_template_backup_hosts;

      void
      clear()
      {
        m_base_app = nullptr;
        m_host = nullptr;
        m_segment = nullptr;
        m_is_templated = false;
        m_template_backup_hosts.clear();
      }

      AppConfig()
      {
        clear();
      }

    };
} // namespace dunedaq::dal

#endif
```

### `include/dal/seg-config.hpp`  
*Local path: `repo/dune-dal/include/dal/seg-config.hpp`*

```cpp
#ifndef _dal_seg_config_H_
#define _dal_seg_config_H_

#include <string>
#include <vector>

#include "dal/Segment.hpp"
#include "dal/app-config.hpp"


namespace dunedaq::dal {

    // forward declarations

    class Computer;
    class Partition;
    class Segment;

    /**
     * \brief The class describes segment configuration parameters
     *
     *  The class provides methods to get description of nested segments and applications.
     *  An object of SegConfig class should be created by dunedaq::dal::Partition::get_segment() algorithm.
     *  Above algorithm allows to limit depth of nested segments description (e.g. for efficiency reasons)
     *  using optional \e depth parameter. If depth parameter is set to 0, then get description of this
     *  segment only (no description of nested segments is provided even if there are such segments in database).
     *  The Run Control may set depth parameter equal to 1 to get information about controller and infrastructure
     *  of nested segments to set them up. If depth parameter is used with default value, the algorithm returns
     *  description of all nested segments.
     *
     *  There are four main use cases:
     *  - to get tree of segments (all disabled and enabled segments are returned)
     *  - to get description of enabled applications of a segment
     *  - to get description of all enabled applications belonging to this and nested segments
     *  - to get description of segment hosts
     *
     *  \par Descriptions of Segment and Nested Segments
     *
     *  Each segment has configuration object, describing the segment in database. The object is returned by the get_segment() method.
     *  Each segment has name (usually is equal to unique ID of configuration object). If the segment is created from template segment object,
     *  then the name is different from UID and it is equal to colon-separated IDs of templated segment and rack configuration objects.
     *  The nested segments can be accessed using get_nested_segments().
     *  The enabled / disabled status of segment can be checked using is_disabled() method.
     *
     *  \par Descriptions of Segment Applications
     *
     *  Each segment has 3 types of applications:
     *  - the segment controller (is described by IsControlledBy relationship); use get_controller() method to access it
     *  - the segment infrastructure applications (are described by the Infrastructure relationship); use get_infrastructure() method to access them
     *  - the segment applications (are described by the Applications and Resources relationships); use get_applications() method to access them
     *
     *  Only enabled application are put into SegConfig description.
     *
     *  \par Descriptions of All Applications
     *
     *  Use get_all_applications() method to get description of applications in given and chosen nested segments (as defined by depth parameter).
     *  It is possible to provide precise selection criteria by application class types, names of nested segments and hosts.
     *  The get_all_applications() method invoked on online segment is used to get all applications of partition (see
     *  dunedaq::dal::Partition::get_all_applications() algorithm).
     *
     *  \par Segment Hosts
     *
     *  The segment hosts are described by the Hosts relationship. For templated segments the Hosts are defined by the hosts of corresponding rack object.
     *  Only enabled (i.e. switched "On") hosts are described.
     *  The first enabled host is considered as "infrastructure" or "default" host.
     *  It is used to run applications without explicitly defined "runs on" relationship.
     **/

    class SegConfig
    {

      friend class Partition;
      friend class AlgorithmUtils;

    public:

      /**
       *  The constructor should only used by the Partition::get_segment() algorithm.
       *  It cannot be made truly private by efficiency reasons.
       */

      SegConfig(const Partition * p) :
          m_partition(p), m_base_segment(nullptr), m_controller(nullptr), m_is_disabled(true), m_is_templated(false)
      {
        ;
      }


      /**
       * Get partition object.
       */

      const Partition *
      get_partition() const
      {
        return m_partition;
      }

      /**
       * Get segment database object.
       */

      const Segment *
      get_base_segment() const
      {
        return m_base_segment;
      }

      /**
       * Get segment controller.
       */

      const BaseApplication *
      get_controller() const
      {
        return m_controller;
      }

      /**
       *  Get infrastructure applications of this segment.
       *  Include applications created from the \e Infrastructure relationship.
       */

      const std::vector<const BaseApplication *>&
      get_infrastructure() const
      {
        return m_infrastructure;
      }

      /**
       *  Get segment applications.
       *  Include applications created from \e Resources and \e Applications relationships.
       */

      const std::vector<const BaseApplication *>&
      get_applications() const
      {
        return m_applications;
      }

      /**
       *  Get nested segments.
       *  Include generated template segments.
       */

      const std::vector<const Segment *>&
      get_nested_segments() const
      {
        return m_nested_segments;
      }

      /**
       *  Get hosts of the segment.
       *  Such hosts are used to run applications without explicitly defined host via "RunsOn" relationship
       */

      const std::vector<const Computer *>&
      get_hosts() const
      {
        return m_hosts;
      }

      /**
       *  Get disabled status.
       *  \return \b true if the segment is disabled and \b false if it is not
       */

      bool
      is_disabled() const
      {
        return m_is_disabled;
      }

      /**
       *  Get disabled status.
       *  \return \b true if the segment is templated and \b false if it is not
       */

      bool
      is_templated() const
      {
        return m_is_templated;
      }


    private:

      const dunedaq::dal::Partition * m_partition;
      const dunedaq::dal::Segment * m_base_segment;
      const BaseApplication * m_controller;
      std::vector<const BaseApplication *> m_infrastructure;
      std::vector<const BaseApplication *> m_applications;
      std::vector<const Segment *> m_nested_segments;
      std::vector<const dunedaq::dal::Computer *> m_hosts;
      bool m_is_disabled;
      bool m_is_templated;

      void
      clear(const Partition * p)
      {
        m_partition = p;
        m_base_segment = nullptr;
        m_controller = nullptr;
        m_infrastructure.clear();
        m_applications.clear();
        m_nested_segments.clear();
        m_hosts.clear();
        m_is_disabled = false;
        m_is_templated = false;
      }

    };
} // namespace dunedaq::dal

#endif
```

### `include/dal/disabled-components.hpp`  
*Local path: `repo/dune-dal/include/dal/disabled-components.hpp`*

```cpp
#ifndef _dal_disabled_components_H_
#define _dal_disabled_components_H_

#include <string>
#include <vector>

#include "conffwk/Configuration.hpp"
#include "conffwk/ConfigAction.hpp"

#include "dal/Component.hpp"

namespace dunedaq::dal {

    class Partition;
    class ResourceSet;
    class Segment;

    class DisabledComponents : public dunedaq::conffwk::ConfigAction
    {

      friend class Partition;
      friend class Component;

    private:

      struct SortStringPtr
      {
        bool
        operator()(const std::string * s1, const std::string * s2) const
        {
          return (*s1 < *s2);
        }
      };

      dunedaq::conffwk::Configuration& m_db;

      unsigned long m_num_of_slr_enabled_resources;
      unsigned long m_num_of_slr_disabled_resources;

      std::set<const std::string *, SortStringPtr> m_disabled;
      std::set<const dunedaq::dal::Component *> m_user_disabled;
      std::set<const dunedaq::dal::Component *> m_user_enabled;

      void
      __clear() noexcept
      {
        m_disabled.clear();
        m_user_disabled.clear();
        m_user_enabled.clear();
        m_num_of_slr_enabled_resources = 0;
        m_num_of_slr_disabled_resources = 0;
      }

    public:

      DisabledComponents(dunedaq::conffwk::Configuration& db);

      virtual
      ~DisabledComponents();

      void
      notify(std::vector<dunedaq::conffwk::ConfigurationChange *>& /*changes*/) noexcept;

      void
      load() noexcept;

      void
      unload() noexcept;

      void
      update(const dunedaq::conffwk::ConfigObject& obj, const std::string& name) noexcept;

      void
      reset() noexcept;

      size_t
      size() noexcept
      {
        return m_disabled.size();
      }

      void
      disable(const dunedaq::dal::Component& c)
      {
        m_disabled.insert(&c.UID());
      }

      bool
      is_enabled(const dunedaq::dal::Component* c);

      bool
      is_enabled_short(const dunedaq::dal::Component* c)
      {
        return (m_disabled.find(&c->UID()) == m_disabled.end());
      }

      void
      disable_children(const dunedaq::dal::ResourceSet&);

      void
      disable_children(const dunedaq::dal::Segment&);

      static unsigned long
      get_num_of_slr_resources(const dunedaq::dal::Partition& p);

    };
} // namespace dunedaq::daq

#endif
```

### `include/dal/application-config.hpp`  
*Local path: `repo/dune-dal/include/dal/application-config.hpp`*

```cpp
#ifndef _dal_application_config_H_
#define _dal_application_config_H_

#include <atomic>
#include <mutex>

#include "conffwk/ConfigAction.hpp"

namespace dunedaq {
  namespace conffwk {
    class Configuration;
  }
}

namespace dunedaq::dal {

    class Segment;
    class Partition;

    class ApplicationConfig : public dunedaq::conffwk::ConfigAction
    {
      friend class Partition;

    private:

      dunedaq::conffwk::Configuration& m_db;
      mutable std::atomic<const dunedaq::dal::Segment*> m_root_segment;
      mutable std::mutex m_root_segment_mutex;

      void
      __clear() noexcept
      {
        std::lock_guard<std::mutex> scoped_lock(m_root_segment_mutex);
        m_root_segment.store(nullptr);
      }

    public:

      ApplicationConfig(dunedaq::conffwk::Configuration& db);

      virtual
      ~ApplicationConfig();

      void
      notify(std::vector<dunedaq::conffwk::ConfigurationChange *>& /*changes*/) noexcept
      {
        __clear();
      }

      void
      load() noexcept
      {
        __clear();
      }

      void
      unload() noexcept
      {
        __clear();
      }

      void
      update(const dunedaq::conffwk::ConfigObject& /*obj*/, const std::string& /*name*/) noexcept
      {
        __clear();
      }

    };
} // namespace dunedaq::dal

#endif
```


## Command-line tools (apps)

### `apps/dal_get_config_version.cxx`  
*Local path: `repo/dune-dal/apps/dal_get_config_version.cxx`*

```cpp
#include <boost/program_options.hpp>

#include "dal/util.hpp"
#include "exit_status.hpp"

int
main(int argc, char **argv)
{

  std::string partition;

  boost::program_options::options_description desc(
      "Get configuration version. The partition infrastructure has to be running. The program reads version from information service.\n\n"
      "Available options are:");

  try
    {
      desc.add_options()
        ("partition,p", boost::program_options::value<std::string>(&partition)->required(), "name of partition")
        ("help,h", "Print help message");

      boost::program_options::variables_map vm;
      boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);

      if (vm.count("help"))
        {
          std::cout << desc << std::endl;
          return __SuccessExitStatus__;
        }

      boost::program_options::notify(vm);
    }
  catch (std::exception& ex)
    {
      std::cerr << "Command line parsing errors occurred:\n" << ex.what() << std::endl;
      return __CommandLineErrorExitStatus__;
    }

  try
    {
      std::string version = ::dunedaq::dal::get_config_version(partition);
      std::cout << version << std::endl;
    }
  catch (const dunedaq::conffwk::NotFound & ex)
    {
      std::cerr << ex << std::endl;
      auto params = ex.parameters();
      return (params["type"] == "is value" ? __InfoNotFoundExitStatus__ : __RepositoryNotFoundExitStatus__);
    }
  catch (const dunedaq::conffwk::Exception & ex)
    {
      std::cerr << "ERROR: " << ex << std::endl;
      return __FailureExitStatus__;
    }

  return __SuccessExitStatus__;
}
```

### `apps/dal_set_config_version.cxx`  
*Local path: `repo/dune-dal/apps/dal_set_config_version.cxx`*

```cpp
#include <boost/program_options.hpp>

#include "dal/util.hpp"
#include "exit_status.hpp"

int
main(int argc, char **argv)
{

  std::string partition;
  std::string version;
  bool reload;

  boost::program_options::options_description desc(
      "Set configuration version. The partition infrastructure has to be running. The program publishes new version in information service and reloads remote database service.\n\n"
      "Available options are:");

  try
    {
      desc.add_options()
        ("version,v", boost::program_options::value<std::string>(&version)->required(), "set configuration version or erase if empty")
        ("partition,p", boost::program_options::value<std::string>(&partition)->required(), "name of partition")
        ("reload,r", "reload database service")
        ("help,h", "Print help message");

      boost::program_options::variables_map vm;
      boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);

      if (vm.count("help"))
        {
          std::cout << desc << std::endl;
          return __SuccessExitStatus__;
        }

      reload = vm.count("reload");

      boost::program_options::notify(vm);
    }
  catch (std::exception& ex)
    {
      std::cerr << "Command line parsing errors occurred:\n" << ex.what() << std::endl;
      return __CommandLineErrorExitStatus__;
    }

  try
    {
      ::dunedaq::dal::set_config_version(partition, version, reload);
    }
  catch (const dunedaq::conffwk::NotFound & ex)
    {
      std::cerr << ex << std::endl;
      return __RepositoryNotFoundExitStatus__;
    }
  catch (const dunedaq::conffwk::Exception & ex)
    {
      std::cerr << "ERROR: " << ex << std::endl;
      return __FailureExitStatus__;
    }

  return __SuccessExitStatus__;
}
```

### `src/exit_status.hpp`  
*Local path: `repo/dune-dal/src/exit_status.hpp`*

```cpp
#ifndef _daq_core_exit_status_H_
#define _daq_core_exit_status_H_

 /// used for get and set config versions exit status

enum __ExitStatus__
{
  __SuccessExitStatus__ = 0,
  __CommandLineErrorExitStatus__ = 1,
  __RepositoryNotFoundExitStatus__ = 2,
  __InfoNotFoundExitStatus__ = 3,
  __FailureExitStatus__ = 4
};

#endif
```

> Other apps in the repo (`dal_dump_apps.cxx`, `dal_dump_app_config.cxx`, `dal_dump_app_depends.cxx`, `dal_get_app_env.cxx`, `dal_print_hosts.cxx`, `dal_print_segments.cxx`, `dal_test_disabled.cxx`, `dal_test_get_config.cxx`, `dal_test_rw.cxx`, `dal_test_timeouts.cxx`, `dal_dump_apps_mt.cxx`) share the same style: Boost program_options parsing of `-p <partition>`, then calls into the `dunedaq::dal` algorithms. They are registered in `CMakeLists.txt` (below). `dal_test_rw.cxx` also exercises the OKS GIT interface: it clones/pulls the configuration git repository and reads the version with `dal::get_config_version` (`TDAQ_DB_VERSION` env var / `Partition::get_DBVersion()`). Their sources are preserved in the local clone (`repo/dune-dal/apps/`) and are available on GitHub; the two config-version tools plus `exit_status.hpp` are reproduced in full above because they are the topic-relevant ones.

## Schemas (XML, DTD + classes)

### `schema/dal/tutorial.schema.xml`  
*Local path: `repo/dune-dal/schema/dal/tutorial.schema.xml`*

```xml
<?xml version="1.0" encoding="ASCII"?>

<!-- oks-schema version 2.2 -->


<!DOCTYPE oks-schema [
  <!ELEMENT oks-schema (info, (include)?, (comments)?, (class)+)>
  <!ELEMENT info EMPTY>
  <!ATTLIST info
      name CDATA #IMPLIED
      type CDATA #IMPLIED
      num-of-items CDATA #REQUIRED
      oks-format CDATA #FIXED "schema"
      oks-version CDATA #REQUIRED
      created-by CDATA #IMPLIED
      created-on CDATA #IMPLIED
      creation-time CDATA #IMPLIED
      last-modified-by CDATA #IMPLIED
      last-modified-on CDATA #IMPLIED
      last-modification-time CDATA #IMPLIED
  >
  <!ELEMENT include (file)+>
  <!ELEMENT file EMPTY>
  <!ATTLIST file
      path CDATA #REQUIRED
  >
  <!ELEMENT comments (comment)+>
  <!ELEMENT comment EMPTY>
  <!ATTLIST comment
      creation-time CDATA #REQUIRED
      created-by CDATA #REQUIRED
      created-on CDATA #REQUIRED
      author CDATA #REQUIRED
      text CDATA #REQUIRED
  >
  <!ELEMENT class (superclass | attribute | relationship | method)*>
  <!ATTLIST class
      name CDATA #REQUIRED
      description CDATA ""
      is-abstract (yes|no) "no"
  >
  <!ELEMENT superclass EMPTY>
  <!ATTLIST superclass name CDATA #REQUIRED>
  <!ELEMENT attribute EMPTY>
  <!ATTLIST attribute
      name CDATA #REQUIRED
      description CDATA ""
      type (bool|s8|u8|s16|u16|s32|u32|s64|u64|float|double|date|time|string|uid|enum|class) #REQUIRED
      range CDATA ""
      format (dec|hex|oct) "dec"
      is-multi-value (yes|no) "no"
      init-value CDATA ""
      is-not-null (yes|no) "no"
      ordered (yes|no) "no"
  >
  <!ELEMENT relationship EMPTY>
  <!ATTLIST relationship
      name CDATA #REQUIRED
      description CDATA ""
      class-type CDATA #REQUIRED
      low-cc (zero|one) #REQUIRED
      high-cc (one|many) #REQUIRED
      is-composite (yes|no) #REQUIRED
      is-exclusive (yes|no) #REQUIRED
      is-dependent (yes|no) #REQUIRED
      ordered (yes|no) "no"
  >
  <!ELEMENT method (method-implementation*)>
  <!ATTLIST method
      name CDATA #REQUIRED
      description CDATA ""
  >
  <!ELEMENT method-implementation EMPTY>
  <!ATTLIST method-implementation
      language CDATA #REQUIRED
      prototype CDATA #REQUIRED
      body CDATA ""
  >
]>

<oks-schema>

<info name="" type="" num-of-items="3" oks-format="schema" oks-version="862f2957270" created-by="jcfree" created-on="mu2edaq13.fnal.gov" creation-time="20230123T223700" last-modified-by="jcfree" last-modified-on="mu2edaq13.fnal.gov" last-modification-time="20230123T223700"/> 

 <class name="Application" description="A software executable" is-abstract="yes">
  <attribute name="Name" description="Name of the executable, including full path" type="string" init-value="Unknown" is-not-null="yes"/>
 </class>

 <class name="ReadoutApplication" description="An executable which reads out subdetectors">
  <superclass name="Application"/>
  <attribute name="SubDetector" description="An enum to describe what type of subdetector it can read out" type="enum" range="PMT,WireChamber" init-value="WireChamber"/>
 </class>

 <class name="RCApplication" description="An executable which allows users to control datataking">
  <superclass name="Application"/>
  <attribute name="Timeout" description="Seconds to wait before giving up on a transition" type="u16" range="1..3600" init-value="20" is-not-null="yes"/> 
  <relationship name="ApplicationsControlled" description="Applications RC is in charge of" class-type="Application" low-cc="one" high-cc="many"/> 
 </class>

</oks-schema>
```

> `core.schema.xml` is the DUNE copy of the ATLAS `core` schema — the full class hierarchy (83 KB). It is reproduced in full below (the renderer embeds its byte content); its header DTD is identical to the one in `tutorial.schema.xml` above. It declares classes such as `Partition`, `Segment`, `OnlineSegment`, `Computer`, `Application`, `RunControlApplication`, `Binary`, `SW_Repository`, `Tag`, `Variable` with Attributes, Relationships, and Methods (e.g. the `get_all_applications` Method on `Partition`, implemented in `src/algorithms.cpp`).
### `schema/dal/core.schema.xml`  
*Local path: `repo/dune-dal/schema/dal/core.schema.xml`*

```xml
<?xml version="1.0" encoding="ASCII"?>

<!-- oks-schema version 2.2 -->


<!DOCTYPE oks-schema [
  <!ELEMENT oks-schema (info, (include)?, (comments)?, (class)+)>
  <!ELEMENT info EMPTY>
  <!ATTLIST info
      name CDATA #IMPLIED
      type CDATA #IMPLIED
      num-of-items CDATA #REQUIRED
      oks-format CDATA #FIXED "schema"
      oks-version CDATA #REQUIRED
      created-by CDATA #IMPLIED
      created-on CDATA #IMPLIED
      creation-time CDATA #IMPLIED
      last-modified-by CDATA #IMPLIED
      last-modified-on CDATA #IMPLIED
      last-modification-time CDATA #IMPLIED
  >
  <!ELEMENT include (file)+>
  <!ELEMENT file EMPTY>
  <!ATTLIST file
      path CDATA #REQUIRED
  >
  <!ELEMENT comments (comment)+>
  <!ELEMENT comment EMPTY>
  <!ATTLIST comment
      creation-time CDATA #REQUIRED
      created-by CDATA #REQUIRED
      created-on CDATA #REQUIRED
      author CDATA #REQUIRED
      text CDATA #REQUIRED
  >
  <!ELEMENT class (superclass | attribute | relationship | method)*>
  <!ATTLIST class
      name CDATA #REQUIRED
      description CDATA ""
      is-abstract (yes|no) "no"
  >
  <!ELEMENT superclass EMPTY>
  <!ATTLIST superclass name CDATA #REQUIRED>
  <!ELEMENT attribute EMPTY>
  <!ATTLIST attribute
      name CDATA #REQUIRED
      description CDATA ""
      type (bool|s8|u8|s16|u16|s32|u32|s64|u64|float|double|date|time|string|uid|enum|class) #REQUIRED
      range CDATA ""
      format (dec|hex|oct) "dec"
      is-multi-value (yes|no) "no"
      init-value CDATA ""
      is-not-null (yes|no) "no"
      ordered (yes|no) "no"
  >
  <!ELEMENT relationship EMPTY>
  <!ATTLIST relationship
      name CDATA #REQUIRED
      description CDATA ""
      class-type CDATA #REQUIRED
      low-cc (zero|one) #REQUIRED
      high-cc (one|many) #REQUIRED
      is-composite (yes|no) #REQUIRED
      is-exclusive (yes|no) #REQUIRED
      is-dependent (yes|no) #REQUIRED
      ordered (yes|no) "no"
  >
  <!ELEMENT method (method-implementation*)>
  <!ATTLIST method
      name CDATA #REQUIRED
      description CDATA ""
  >
  <!ELEMENT method-implementation EMPTY>
  <!ATTLIST method-implementation
      language CDATA #REQUIRED
      prototype CDATA #REQUIRED
      body CDATA ""
  >
]>

<oks-schema>

<info name="" type="" num-of-items="83" oks-format="schema" oks-version="oks-08-03-03 built &quot;Apr 30 2021&quot;" created-by="isolov" created-on="lxplus015" creation-time="20030411T150215" last-modified-by="isolov" last-modified-on="pc-tbed-pub-21.cern.ch" last-modification-time="20210430T142105"/>

 <class name="Application" description="This abstract class is used to describe base properties of a simple process.&#xA;For more information read https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_3_Application_Classes" is-abstract="yes">
  <superclass name="BaseApplication"/>
  <relationship name="RunsOn" description="Defines computer device where to start the process." class-type="Computer" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="BackupHosts" class-type="ComputerBase" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="BaseApplication" description="This class is used to describe processes which can be started at certain moment and order. To describe a new process it is necessary to create an instance of a concrete class derived from this one and put references to the software object (i.e. ComputerProgram class) to describe what to start and the ComputerBase to describe where to start. The &apos;Initialization&apos; and &apos;Shutdown&apos; dependencies are used in case if we want to start a process synchronously and we know which one we must start or kill first. For more information read https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_3_Application_Classes" is-abstract="yes">
  <superclass name="TestableObject"/>
  <attribute name="Parameters" description="Command line parameters." type="string"/>
  <attribute name="RestartParameters" description="Command line parameters to restart application in case of application failure." type="string"/>
  <attribute name="Logging" description="Indicates whether the stdout of this application shall be piped to /dev/null or stored in a log file.." type="bool" init-value="true" is-not-null="yes"/>
  <attribute name="InputDevice" description="If defined, it will be used as standard input." type="string"/>
  <attribute name="InitTimeout" description="Initialization timeout, i.e. maximum time for a process to go to state&#xA;&quot;ready-to-communicate&quot; with others, e.g. a server start up time." type="u32" init-value="0"/>
  <attribute name="ExitTimeout" description="Time to wait for the application to exit cleanly before sending it a SIGKILL." type="u32" range="1..60" init-value="5" is-not-null="yes"/>
  <attribute name="StartIn" description="Directory where to start the process." type="string"/>
  <attribute name="RestartableDuringRun" description="This flag indicates whether an application can or cannot be restarted while a Run is ongoing." type="bool" init-value="false"/>
  <attribute name="IfExitsUnexpectedly" description="Describes an action if the application exits at unexpected moment.&#xA;" type="enum" range="Error,Ignore,Restart,Handle" init-value="Error"/>
  <attribute name="IfFailsToStart" description="Describes action if the application cannot be started." type="enum" range="Error,Ignore,Restart,Handle" init-value="Error"/>
  <relationship name="InitializationDependsFrom" description="Defines processes to be started before this one." class-type="BaseApplication" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ShutdownDependsFrom" description="Defines shutdown order." class-type="BaseApplication" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Program" description="Defines computer program to be used for this process." class-type="ComputerProgram" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ExplicitTag" description="If defined it points to the exact tag of computer program." class-type="Tag" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Uses" description="Define sw packages which are used by given application in addition to ones defined by the program.&#xA;" class-type="SW_Package" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ProcessEnvironment" description="Define application specific process environment." class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <method name="get_host" description="">
   <method-implementation language="c++" prototype="const dunedaq::dal::Computer * get_host() const" body="ADD_ALGO_1"/>
   <method-implementation language="java" prototype="dal.Computer get_host() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_app_config(false).get_host();"/>
  </method>
  <method name="get_segment" description="Get generated segment object this application belongs to.">
   <method-implementation language="c++" prototype="const dunedaq::dal::Segment * get_segment() const" body="ADD_ALGO_1"/>
   <method-implementation language="java" prototype="dal.Segment get_segment() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_app_config(false).get_segment();"/>
  </method>
  <method name="get_backup_hosts" description="Get backup hosts for this application.&#xA;&#xA;The method returns vector of computers where the application can be restarted in case of problems.&#xA;&#xA;For normal applications the backup hosts are defined via &quot;BackupHosts&quot; relationship.&#xA;For template applications with &quot;RunsOn&quot; attribute set to &quot;FirstHostWithBackup&quot; the backup hosts are randomly chosen from list of segment hosts; there are no backup hosts for other types of template &quot;RunsOn&quot;.&#xA;&#xA;\throw daq::conffwk::Exception in case of problems">
   <method-implementation language="c++" prototype="std::vector&lt;const dunedaq::dal::Computer *&gt; get_backup_hosts() const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="dal.Computer[] get_backup_hosts() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_app_config(false).get_backup_hosts();"/>
  </method>
  <method name="get_base_app" description="Return original base application object, i.e. not created by DAL algorithms">
   <method-implementation language="c++" prototype="const dunedaq::dal::BaseApplication * get_base_app() const" body=""/>
   <method-implementation language="java" prototype="dal.BaseApplication get_base_app() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_app_config(false).get_base_app();"/>
  </method>
  <method name="get_initialization_depends_from" description="Get applications initialization depends from.&#xA;&#xA;If this application is normal (i.e. non-templated), the algorithm returns all dependent normal applications and templated applications which belong to the segment of the application.&#xA;If this application is templated, then the algorithm returns all dependent applications belonging to the same segment and running on the same host.&#xA;&#xA;By performance efficiency reasons the algorithm needs to know all applications running in this segment.&#xA;The all_apps input parameter should contain result returned by get_all_applications() algorithm running for the segment of this application (preferable) or it&apos;s partition.&#xA;&#xA;\param all_apps  all applications in this segment or whole partition&#xA;\return result containing initialization dependent applications&#xA;\throw Throw dunedaq::dal::NotInitedObject if the object was not initialized and cannot be used">
   <method-implementation language="c++" prototype="std::vector&lt;const dunedaq::dal::BaseApplication *&gt; get_initialization_depends_from(const std::vector&lt;const dunedaq::dal::BaseApplication *&gt;&amp; all_apps) const" body=""/>
  </method>
  <method name="get_shutdown_depends_from" description="Get applications shutdown depends from.&#xA;&#xA;The behavior is similar to the get_initialization_depends_from() method.&#xA; &#xA;\param all_apps  all applications in this segment or whole partition&#xA;\return result containing shutdown dependent applications&#xA;\throw dunedaq::dal::NotInitedObject if the object was not initialized and cannot be used">
   <method-implementation language="c++" prototype="std::vector&lt;const dunedaq::dal::BaseApplication *&gt; get_shutdown_depends_from(const std::vector&lt;const dunedaq::dal::BaseApplication *&gt;&amp; all_apps) const" body=""/>
  </method>
  <method name="get_info" description="Get full information about application.&#xA;&#xA;The method returns vector of allowed tags, process environment, possible program names and command line arguments.&#xA;The root_segment has to be a reference on online segment returned by the partition&apos;s get_segment() invoked on the online segment.&#xA;\param environment   output map of process environment name:value pairs&#xA;\param program_names output vector of possible program names&#xA;\param partition     reference on partition&#xA;\param root_segment  reference on online segment (as returned by dunedaq::dal::Partition::get_segment() invoked on the online segment)&#xA;\param host          reference on host where to run application (may override host set in AppConfig)&#xA;\param startArgs     output string with command line arguments to start application&#xA;\param restartArgs   output string with command line arguments to re-start application&#xA;\return tag for this application&#xA;\throw  dunedaq::dal::AlgorithmError in case of problems">
   <method-implementation language="c++" prototype="const dunedaq::dal::Tag * get_info(std::map&lt;std::string, std::string&gt;&amp; environment, std::vector&lt;std::string&gt;&amp; program_names, std::string &amp; startArgs, std::string &amp; restartArgs) const" body=""/>
   <method-implementation language="java" prototype="dal.Tag get_info(java.util.Map&lt;String, String&gt; environment, java.util.List&lt;String&gt; program_names, StringBuilder startArgs, StringBuilder restartArgs) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return dal.AppConfig.get_info(this, environment,program_names, startArgs, restartArgs);"/>
  </method>
  <method name="is_templated" description="Return true if application is templated">
   <method-implementation language="c++" prototype="bool is_templated() const" body=""/>
   <method-implementation language="java" prototype="boolean get_is_templated() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_app_config(false).get_is_templated();"/>
  </method>
  <method name="get_app_config" description="">
   <method-implementation language="c++" prototype="const AppConfig * get_app_config(bool no_except = false) const" body="BEGIN_HEADER_PROLOGUE&#xA;#include &lt;atomic&gt;&#xA;#include &lt;dal/app-config.hpp&gt;&#xA;namespace dunedaq { namespace dal { class AlgorithmUtils; } }&#xA;END_HEADER_PROLOGUE&#xA;&#xA;BEGIN_PRIVATE_SECTION&#xA;std::unique_ptr&lt;AppConfig&gt; p_app_config;&#xA;mutable std::atomic&lt;const BaseApplication *&gt; p_gen_obj;&#xA;friend class dunedaq::dal::AlgorithmUtils;&#xA;END_PRIVATE_SECTION&#xA;&#xA;BEGIN_MEMBER_INITIALIZER_LIST&#xA;p_gen_obj(nullptr)&#xA;END_MEMBER_INITIALIZER_LIST&#xA;"/>
   <method-implementation language="java" prototype="dal.AppConfig get_app_config(boolean no_except) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="BEGIN_PRIVATE_SECTION&#xA;dal.AppConfig p_app_config;&#xA;dal.BaseApplication p_gen_obj;&#xA;END_PRIVATE_SECTION&#xA;&#xA;return dal.ApplicationConfig.get_app_config(this, no_except);&#xA;"/>
  </method>
 </class>

 <class name="Binary" description="This class is used to describe binary program. By default binaries should exist for each tag defined for the software repository this binary belongs to (see ExactImplementations relationship for more details).">
  <superclass name="ComputerProgram"/>
  <relationship name="ExactImplementations" description="Is used to describe implementations different from default, e.g. having different binary name, command line parameters, environment, etc.&#xA;If a program object is defined, there are no default implementations." class-type="BinaryFile" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="yes"/>
 </class>

 <class name="BinaryFile">
  <attribute name="BinaryName" type="string" is-not-null="yes"/>
  <relationship name="Tag" class-type="Tag" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Cable" description="Describe generic directional connector between two connectable objects (source and destination).">
  <superclass name="HW_Object"/>
  <superclass name="Resource"/>
  <relationship name="Destination" description="Points on destination object connected by this cable." class-type="HW_ConnectableObject" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Source" description="Points on source object connected by this cable." class-type="HW_ConnectableObject" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Component" description="Abstract base class for Segment and Resource classes. It is only used to allow objects of derived classes to be put into list of disabled items. For more information read https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_4_Resource_Classes" is-abstract="yes">
  <method name="get_parents" description="The algorithm calculates a vector of segments which are parents of given segment.&#xA;If the segment has parents referenced by the partition object, then:&#xA;- in case of C++ it fills parents parameter&#xA;- in case of Java it returns parents; otherwise it throws {@link NotFoundException} exception">
   <method-implementation language="c++" prototype="void get_parents(const dunedaq::dal::Partition&amp; partition, std::list&lt; std::vector&lt;const dunedaq::dal::Component *&gt; &gt;&amp; parents) const" body=""/>
   <method-implementation language="java" prototype="Component[][] get_parents(Partition partition) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return dal.Algorithms.get_parents(this, partition);"/>
  </method>
  <method name="disabled" description="The algorithm checks if the segment / resource is disabled in the partition that uses it.&#xA;@param partition      partition object containing this resource or segment&#xA;">
   <method-implementation language="c++" prototype="bool disabled(const dunedaq::dal::Partition&amp; partition, bool skip_check = false) const" body=""/>
   <method-implementation language="java" prototype="boolean disabled(Partition partition) throws config.GenericException, config.SystemException, config.NotFoundException, config.NotValidException" body="return partition.resources().get_disabled(this, partition, false);"/>
  </method>
  <method name="why_disabled" description="">
   <method-implementation language="java" prototype="String why_disabled(Partition partition, String prefix, boolean full_report) throws config.GenericException, config.SystemException, config.NotFoundException, config.NotValidException" body="return partition.resources().why_disabled(this, prefix, full_report);"/>
  </method>
 </class>

 <class name="Computer" description="Describes a computer.">
  <superclass name="ComputerBase"/>
  <superclass name="Platform"/>
  <superclass name="HW_Object"/>
  <attribute name="Memory" description="Memory in MB" type="u32" init-value="16384" is-not-null="yes"/>
  <attribute name="CPU" description="Computer performance. Now in MHz frequency. To be discussed." type="u16" init-value="2048" is-not-null="yes"/>
  <attribute name="NumberOfCores" description="Number of cores." type="u16" init-value="8"/>
  <attribute name="RLogin" description="Defines command used for computer remote login. Examples: rsh, ash, ssh." type="string" init-value="ssh" is-not-null="yes"/>
  <relationship name="Interfaces" description="A computer can have several interfaces (e.g. NIC) connecting it with other hw." class-type="Interface" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="yes"/>
 </class>

 <class name="ComputerBase" description="Describes an abstract computer power. Can be a computer or set of computers." is-abstract="yes">
 </class>

 <class name="ComputerProgram" description="Describes programs which can be running of generic computer." is-abstract="yes">
  <superclass name="SW_Object"/>
  <attribute name="DefaultParameters" description="Define default command line parameters." type="string"/>
  <relationship name="ProcessEnvironment" class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <method name="get_info" description="Calculates computer program parameters:&#xA;- list of possible program files&#xA;- process environment&#xA; &#xA;Requires:&#xA;- partition reference&#xA;- tag reference&#xA;- computer reference&#xA;- optional partition pointer&#xA;">
   <method-implementation language="c++" prototype="void get_info(std::map&lt;std::string, std::string&gt;&amp; environment, std::vector&lt;std::string&gt;&amp; program_names, const dunedaq::dal::Partition&amp; partition, const dunedaq::dal::Tag&amp; tag, const dunedaq::dal::Computer&amp; host) const" body=""/>
   <method-implementation language="java" prototype="void get_info(java.util.Map&lt;String, String&gt; environment, java.util.List&lt;String&gt; program_names, dal.Partition partition, dal.Tag tag, dal.Computer host) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="dal.Algorithms.get_info(this, environment, program_names, partition, tag, host);"/>
  </method>
 </class>

 <class name="ComputerSet" description="Describes set of computers.">
  <superclass name="ComputerBase"/>
  <relationship name="Contains" description="Link to computers composing this set object." class-type="ComputerBase" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="ConnectorCable" description="Extension of the cable class to provide more properties required for bundle cable description.">
  <superclass name="Cable"/>
  <attribute name="SrcConnectionType" description="Type of source connector port." type="string"/>
  <attribute name="DstConnectionType" description="Type of destination connector port." type="string"/>
  <attribute name="SrcConnectionNumber" description="Number of source connector port." type="u16"/>
  <attribute name="DstConnectionNumber" description="Number of destination connector port." type="u16"/>
 </class>

 <class name="Crate" description="A crate is a physical container of modules.">
  <superclass name="HW_Object"/>
  <attribute name="NumberOfSlots" description="Number of slots for modules." type="u16"/>
  <attribute name="Position" description="Position of crate inside rack." type="u16" init-value="0"/>
  <attribute name="LogicalId" description="Logical ID of crate." type="u32" init-value="0"/>
  <relationship name="Modules" description="Modules inserted into crate." class-type="Module" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
  <relationship name="ControlHost" description="Points to a Computer where programs, communicating with crate modules (e.g. via VME) should/can be launched. Typically this is a zero Module in the Crate, but can also be a PC, connecting to a Crate by other interface." class-type="Computer" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="CustomLifetimeApplication">
  <superclass name="CustomLifetimeApplicationBase"/>
  <superclass name="Application"/>
 </class>

 <class name="CustomLifetimeApplicationBase">
  <attribute name="Lifetime" description="Defines the transitions at which the application shall be started/stopped." type="enum" range="Boot_Shutdown,Configure_Unconfigure,SOR_EOR,EOR_SOR,UserDefined_Shutdown" init-value="Boot_Shutdown"/>
  <attribute name="AllowSpontaneousExit" description="Allow the application to exit when it has finished its task.&#xA;The exit code will be checked and if it is !=0 then the system will behave as specified by the IfExitsUnexpectedly attribute." type="bool" init-value="false"/>
 </class>

 <class name="CustomLifetimeTemplateApplication">
  <superclass name="CustomLifetimeApplicationBase"/>
  <superclass name="TemplateApplication"/>
 </class>

 <class name="DBConnection" description="Describes the database connection to be used to obtain configuration parameters">
  <attribute name="Server" description="Database server name" type="string"/>
  <attribute name="Port" description="Port to be used to contact DB server." type="string"/>
  <attribute name="Name" description="Schema name for oracle, database name for MySQL" type="string"/>
  <attribute name="Alias" description="Logical name of the DB which is normally stored in dblookup files." type="string"/>
  <attribute name="User" description="User name for database connection" type="string"/>
  <attribute name="Password" description="Password for database connection" type="string"/>
  <attribute name="Type" description="Technology used by the DB accessor, value ignored if db lookup mechanism is used." type="enum" range="MySQL,Oracle,SQLite,Coral" is-not-null="yes"/>
 </class>

 <class name="DataFlowParameters" description="Abstract class to be extended by the dataflow." is-abstract="yes">
  <attribute name="Name" description="Name of the parameters set." type="string"/>
 </class>

 <class name="Detector" description="There are two types of usage:&#xA; * detector is a generic container for hw systems and objects;&#xA; * sub-detector as defined by event format and referenced by ROS or RCD">
  <superclass name="HW_System"/>
  <attribute name="LogicalId" description="Event format sub-detector source identifier." type="u8" init-value="0"/>
 </class>

 <class name="FpgaProgram">
  <superclass name="SW_Object"/>
  <attribute name="VersionID" description="Version number reported by this FPGA program when loaded." type="u32" format="hex" init-value="0x0" is-not-null="yes"/>
  <attribute name="CadProject" description="Name of the CAD project used to create the FPGA program (can be checked in the binary file)." type="string" is-not-null="yes"/>
  <attribute name="CheckString" description="Some other string which can (optionally) be checked in the binary file." type="string"/>
  <attribute name="Checksum" description="Expected checksum of the binary file." type="u32" init-value="0x0" is-not-null="yes"/>
  <attribute name="ChipType" description="Type of FPGA chip into which this program may be loaded." type="string" is-not-null="yes"/>
  <attribute name="FlashRamBlock" description="Block within flash RAM to download this FPGA program." type="u32" format="hex" init-value="0x0" is-not-null="yes"/>
  <attribute name="SourceURL" description="URL for downloading new versions of the binary file." type="string"/>
  <attribute name="ProgramType" description="Function of this FPGA program." type="string" range="Invalid" init-value="Invalid" is-not-null="yes"/>
  <attribute name="DeviceName" description="Name of FPGA device on the module for which this FPGA program is intended." type="string" range="Invalid" init-value="Invalid" is-not-null="yes"/>
 </class>

 <class name="HLTImplementation" description="The HLT implementation object contains a pointer to the specific implementation of the application that will run on the HLT trigger processor" is-abstract="yes">
  <attribute name="libraries" description="Libraries that implement the functionality to be loaded inside the trigger processor" type="string" is-multi-value="yes"/>
 </class>

 <class name="HW_ConnectableObject">
  <superclass name="HW_Object"/>
 </class>

 <class name="HW_Object" description="Generic hardware object.">
  <superclass name="TestableObject"/>
  <attribute name="Type" description="Hardware manufacture type." type="string"/>
  <attribute name="Location" description="Physical location of hw object." type="string"/>
  <attribute name="Description" type="string" is-not-null="yes"/>
  <attribute name="HelpLink" description="URL containing description." type="string"/>
  <attribute name="InstallationRef" description="Reference to object from installation DB." type="string"/>
  <attribute name="State" description="If the state is &apos;true&apos;, the hw device is On." type="bool" init-value="true"/>
 </class>

 <class name="HW_System">
  <attribute name="Description" type="string"/>
  <attribute name="HelpLink" type="string"/>
  <attribute name="State" type="bool"/>
  <relationship name="HW_Systems" class-type="HW_System" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="yes" is-dependent="yes"/>
  <relationship name="HW_Objects" class-type="HW_Object" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="IPCServiceApplication" description="Describes infrastructure application having CORBA test">
  <superclass name="IPCServiceApplicationBase"/>
  <superclass name="InfrastructureApplication"/>
 </class>

 <class name="IPCServiceApplicationBase" description="Describes base properties of applications having IPC test interface" is-abstract="yes">
  <attribute name="InterfaceName" description="Name of CORBA IDL interface" type="string" range=".+" init-value="ipc/servant" is-not-null="yes"/>
  <attribute name="IPCName" description="Name of this application (CORBA service) as published in IPC. It may differ from dal AppId for the application, so the synchronisation of command line parameters is needed." type="string"/>
 </class>

 <class name="IPCServiceTemplateApplication" description="Describes template infrastructure application having CORBA test">
  <superclass name="IPCServiceApplicationBase"/>
  <superclass name="InfrastructureTemplateApplication"/>
 </class>

 <class name="IS_EventsAndRates" description="A class which describes IS variables to use as event counters and rate indicators.">
  <attribute name="EventCounter" description="Indicates from which IS variable to read the event counter from." type="string"/>
  <attribute name="Rate" description="Indicates from which IS variable to read the rate from." type="string"/>
  <attribute name="Description" description="Describes the type of IS information." type="string"/>
 </class>

 <class name="IS_InformationSources">
  <relationship name="LVL1" description="Where to pick the IS information for L1 accepts." class-type="IS_EventsAndRates" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="HLT" description="Where to pick the IS information for events processed by the HLT." class-type="IS_EventsAndRates" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Recording" description="Where to pick the IS information for recorded events." class-type="IS_EventsAndRates" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Others" description="Indicates other IS information to take. Place holder for reduced DF panel." class-type="IS_EventsAndRates" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="InfrastructureApplication">
  <superclass name="Application"/>
  <superclass name="InfrastructureBase"/>
 </class>

 <class name="InfrastructureBase" description="Infrastructure applications are essential for data taking, so they have a set of backup hosts where these applications can be restarted if their default host is going down or become unavailable. This class represents the common features of all infrastructure apps." is-abstract="yes">
  <attribute name="SegmentProcEnvVarName" description="When value is non-empty, the infrastructure application defines process environment for each application of given and nested segments. The name of the environment is equal to the value of this attribute. The value of the variable is calculated in accordance with value of the SegmentProcEnvVarValue attribute." type="string"/>
  <attribute name="SegmentProcEnvVarParentName" description="Propagate parent&apos;s segment value of environment variable generated from the SegmentProcEnvVarName attribute." type="string"/>
  <attribute name="SegmentProcEnvVarValue" description="appId           - set value to the application ID&#xA;runsOn          - set value to the host name, where application runs on&#xA;runsOnAndBackup - set value to the comma separated list of host and backup hosts names, where application can be runs on" type="enum" range="appId,runsOn,runsOnAndBackup"/>
 </class>

 <class name="InfrastructureTemplateApplication">
  <superclass name="TemplateApplication"/>
  <superclass name="InfrastructureBase"/>
 </class>

 <class name="Interface">
  <superclass name="HW_Object"/>
  <attribute name="Label" type="string"/>
 </class>

 <class name="JarFile">
  <superclass name="SW_Object"/>
 </class>

 <class name="L1TriggerConfiguration" description="Trigger-configuration parameters specific for LVL1">
  <attribute name="CtpPartitionNumber" description="Describes which partition of the CTP is used. 0=full ATLAS partition, 1/2/3=multi-partition running where only partition 1 has full readout and partition 2/3 are obliged to use TTC2LAN." type="u32" range="0..3" init-value="0" is-not-null="yes"/>
  <attribute name="Lvl1PrescaleKey" description="Configuration key for LVL1 prescales" type="u32" init-value="0" is-not-null="yes"/>
  <attribute name="Lvl1BunchGroupKey" description="Configuration key for LVL1 bunch groups" type="u32" init-value="0" is-not-null="yes"/>
  <attribute name="ConfigureLvl1MenuFrom" description="Configuration source for LVL1" type="enum" range="DB,XML,OKS" init-value="DB" is-not-null="yes"/>
 </class>

 <class name="LinkInterface">
  <superclass name="Interface"/>
  <attribute name="Type" type="enum" range="source,destination" init-value="source"/>
 </class>

 <class name="MasterTrigger" description="Container for application controlling the master trigger and the master trigger module.">
  <relationship name="Controller" description="Relation to Application controlling the master trigger.&#xA;The Root Controller will send luminosity block updates to it." class-type="RunControlApplicationBase" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="TriggerModule" description="Relation to the Module acting as master trigger in the partition." class-type="ResourceBase" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Module" description="Class Module describes a generic module.&#xA;It has a lot of subclasses.">
  <superclass name="HW_ConnectableObject"/>
  <attribute name="PhysAddress" type="u32" format="hex" init-value="0"/>
  <attribute name="CommAddress" type="u32" format="hex"/>
  <attribute name="Position" type="u16" range="0..31" init-value="0"/>
  <attribute name="Width" type="u16" init-value="1"/>
  <attribute name="LogicalId" type="u32" init-value="0"/>
  <relationship name="CPUs" class-type="Computer" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="yes" is-dependent="no"/>
 </class>

 <class name="MonApplication" description="This class should be used by any monitoring application that is not state aware.&#xA;It allows to define at what transition the application should start/stop and whether it should be restarted at warm start/stop.">
  <superclass name="CustomLifetimeApplication"/>
  <superclass name="WarmStartStopReactor"/>
 </class>

 <class name="MonTemplateApplication" description="This class should be used by any monitoring application that is not state aware.&#xA;It allows to define at what transition the application should start/stop and whether it should be restarted at warm start/stop.">
  <superclass name="CustomLifetimeTemplateApplication"/>
  <superclass name="WarmStartStopReactor"/>
 </class>

 <class name="MonitoringApplication" description="DEPRECATED!">
  <superclass name="Application"/>
 </class>

 <class name="Network">
  <attribute name="Name" type="string"/>
  <attribute name="IPMask" type="string" init-value="225.225.0.0"/>
  <relationship name="EndPoints" class-type="NetworkInterface" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="NetworkInterface">
  <superclass name="Interface"/>
  <attribute name="IPAddress" description="The hostname or dotted IP address for this interface." type="string"/>
  <attribute name="Label" description="TDAQ network label. CTRL, DC* and EF to be used on Point-1. The DATA to be used on external testbeds." type="enum" range="NONE,CTRL,DC1,DC2,EF,DATA"/>
  <attribute name="InterfaceName" description="Value returned by /sbin/config for this NIC." type="string" is-not-null="yes"/>
 </class>

 <class name="OnlineSegment">
  <superclass name="Segment"/>
  <attribute name="T0_ProjectTag" description="Set T0 project tag for production partition" type="string" is-multi-value="yes" init-value="obsolete" is-not-null="yes"/>
  <relationship name="CompatibilityInfo" description="Reference on platform compatibilities" class-type="PlatformCompatibility" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="PmgAgent" description="Points to the software object describing process-manager-agent program." class-type="SW_Object" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="InitialPartition" description="Links the Online segment of a Partition to the initial Partition which provides the basic infrastructure." class-type="Partition" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="TestHosts" description="set of hosts randomly used by Test Manager to launch tests on (in case no explicit host is given to TM)" class-type="ComputerSet" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Parameter" description="This abstract class is used to describe a single variable (name:value pair) or s set of variables." is-abstract="yes">
  <attribute name="Description" description="Describes the purpose of the parameter." type="string"/>
 </class>

 <class name="Partition" description="The class describes TDAQ configuration including top-level segments, disabled components, various TDAQ base and user specific parameters. For more information read https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_1_Partition_Class">
  <attribute name="RepositoryRoot" description="Specifies temporary sw installation area having highest priority over any other installation areas, e.g. to take shared libraries, binaries, etc. Usually it is used for testing patches." type="string"/>
  <attribute name="IPCRef" description="Defines IPC init reference. By default, it is copied from the variable TDAQ_IPC_INIT_REF defined in the process environment and passed to environment of all applications of such partition." type="string" init-value="$(TDAQ_IPC_INIT_REF)"/>
  <attribute name="DBPath" description="Defines locations of database repositories (i.e. OKS_DB_ROOT). By default, it is copied from the variable TDAQ_DB_PATH defined in the process environment and passed to environment of all applications of such partition." type="string" init-value="$(TDAQ_DB_PATH)"/>
  <attribute name="DBName" description="Defines database name, e.g. name of the OKS data file. By default, it is copied from the variable TDAQ_DB_DATA defined in the process environment and passed to environment of all applications of such partition." type="string" init-value="$(TDAQ_DB_DATA)"/>
  <attribute name="DBVersion" description="Defines database version (SHA key) if GIT repository is used . By default, it is copied from the variable TDAQ_DB_VERSION defined in the process environment and passed to environment of all applications of such partition." type="string" init-value="$(TDAQ_DB_VERSION)"/>
  <attribute name="DBTechnology" description="Defines config database technology implementation to be used by all processes running in given partition. Defines TDAQ_DB variable to be passed to all applications of the partition." type="enum" range="rdbconfig,oksconflibs" init-value="rdbconfig"/>
  <attribute name="LogRoot" description="Defines root directory for log files." type="string" init-value="/tmp"/>
  <attribute name="WorkingDirectory" description="Defines directory, where a new process run by pmg will be started." type="string" init-value="/tmp"/>
  <attribute name="RunTypes" type="string" is-multi-value="yes"/>
  <relationship name="Segments" description="References on top-level segments composing given partition. If a segment needs to be temporary disactivated in the partition, do not remove it from this list, but add it to the Disabled list." class-type="Segment" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
  <relationship name="OnlineInfrastructure" description="Defines online infrastructure segment." class-type="OnlineSegment" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Disabled" description="Lists segments and resources, which are temporary disabled." class-type="Component" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no" ordered="yes"/>
  <relationship name="DefaultHost" description="The default host defines a host to run all applications with empty value of &apos;RunsOn&apos; relationship." class-type="Computer" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="DefaultTags" description="If an application has no explicit tag, first suitable tag from this list will be used to select binary for that application." class-type="Tag" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ProcessEnvironment" description="Define process environment for any application ran in given partition." class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Parameters" description="Define list of parameters used for database string substitution. Another source of parameters are segments linked with partition." class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="DataFlowParameters" description="A partition may have one data-flow parameters set." class-type="DataFlowParameters" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="IS_InformationSource" description="Links the Partition to a set of IS variables used to display global performance monitoring." class-type="IS_InformationSources" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="RunTagList" description="Links the partition to a set of user defined run tags" class-type="RunTagList" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="MasterTrigger" description="Link to the master trigger of the partition." class-type="MasterTrigger" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="TestRepositories" description="Links the partition object with the Tests that are performed on it." class-type="TestRepository" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="TriggerConfiguration" description="Points to object describing Level-1 and HLT trigger configuration." class-type="TriggerConfiguration" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ResourcesInfoConfiguration" description="Defines configuration for ResourcesInfo service.&#xA;The service is only active, if this configuration is correctly defined.&#xA;Do not activate the service for test partitions!&#xA;Do not disable the service without a reason for combined partition!" class-type="ResourcesInfoConfig" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="OnlineInfrastructureApplications" description="Extension of OnlineSegment applications" class-type="Application" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <method name="get_all_applications" description="Returns all templated and non-templated applications defined in the partition with their parameters to be used by the data collection and message passing configurations.">
   <method-implementation language="c++" prototype="std::vector&lt;const dunedaq::dal::BaseApplication *&gt; get_all_applications(std::set&lt;std::string&gt; * app_types = nullptr, std::set&lt;std::string&gt; * use_segments = nullptr, std::set&lt;const Computer *&gt; * use_hosts = nullptr) const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="dal.BaseApplication[] get_all_applications(String[] app_types, String[] use_segments, dal.Computer[] use_hosts) throws config.GenericException, config.SystemException, config.NotFoundException, config.NotValidException" body="return get_segment(get_OnlineInfrastructure().UID()).get_all_applications(app_types, use_segments, use_hosts);"/>
  </method>
  <method name="set_disabled" description="In addition to persistently disabled components, dynamically disable these components. It will be taken into account by disabled() algorithm of Component class. This information is not committed to the database and will be overwritten by next set_disabled() call or erased by any config action (DB load, unload, reload).">
   <method-implementation language="c++" prototype="void set_disabled(const std::set&lt;const dunedaq::dal::Component *&gt;&amp; objs) const" body="BEGIN_PRIVATE_SECTION&#xA;friend class DisabledComponents;&#xA;friend class Component;&#xA;mutable dunedaq::dal::DisabledComponents m_disabled_components; &#xA;END_PRIVATE_SECTION&#xA;BEGIN_MEMBER_INITIALIZER_LIST&#xA;m_disabled_components(p_db)&#xA;END_MEMBER_INITIALIZER_LIST&#xA;BEGIN_HEADER_PROLOGUE&#xA;#include &quot;dal/disabled-components.hpp&quot;&#xA;END_HEADER_PROLOGUE"/>
   <method-implementation language="java" prototype="void set_disabled(Component objs[]) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="BEGIN_PUBLIC_SECTION&#xA;Resources resources() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException;&#xA;END_PUBLIC_SECTION&#xA;BEGIN_PRIVATE_SECTION&#xA;private Resources p_resources;&#xA;&#xA;public Resources resources() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException {&#xA;  if(p_was_read == false) {init();}&#xA;  return p_resources;&#xA;}&#xA;END_PRIVATE_SECTION&#xA;BEGIN_MEMBER_INITIALIZER_LIST&#xA;if(p_resources == null) p_resources = new Resources(p_db);&#xA;END_MEMBER_INITIALIZER_LIST&#xA;resources().set_disabled(objs);"/>
  </method>
  <method name="set_enabled" description="Dynamically enable these persistently disabled components. It will be taken into account by disabled() algorithm of the Component class. This information is not committed to the database and will be overwritten by next set_enabled() call or erased by any config action (DB load, unload, reload).">
   <method-implementation language="c++" prototype="void set_enabled(const std::set&lt;const dunedaq::dal::Component *&gt;&amp; objs) const" body=""/>
   <method-implementation language="java" prototype="void set_enabled(Component objs[]) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="resources().set_enabled(objs);"/>
  </method>
  <method name="get_segment" description="The DAL algorithm to access segment by name. It generates templated segments and applications objects dynamically">
   <method-implementation language="c++" prototype="const dunedaq::dal::Segment * get_segment(const std::string&amp; name) const" body="BEGIN_PRIVATE_SECTION&#xA;mutable dunedaq::dal::ApplicationConfig m_app_config; &#xA;END_PRIVATE_SECTION&#xA;&#xA;BEGIN_MEMBER_INITIALIZER_LIST&#xA;m_app_config(p_db)&#xA;END_MEMBER_INITIALIZER_LIST&#xA;&#xA;BEGIN_HEADER_PROLOGUE&#xA;#include &quot;dal/application-config.hpp&quot;&#xA;END_HEADER_PROLOGUE"/>
   <method-implementation language="java" prototype="dal.Segment get_segment(String id) throws config.GenericException, config.SystemException, config.NotFoundException, config.NotValidException" body="return p_application_config.get_segment(this, id);&#xA;&#xA;BEGIN_PRIVATE_SECTION&#xA;private ApplicationConfig p_application_config;&#xA;END_PRIVATE_SECTION&#xA;&#xA;BEGIN_MEMBER_INITIALIZER_LIST&#xA;if(p_application_config == null) p_application_config = new ApplicationConfig(p_db);&#xA;END_MEMBER_INITIALIZER_LIST&#xA;"/>
  </method>
  <method name="get_log_directory" description="returns the directory in which to write log files. ">
   <method-implementation language="c++" prototype="std::string get_log_directory() const" body=""/>
  </method>
  <method name="set_config_version" description="Set configuration version, i.e. OKS GIT repository SHA. The partition infrastructure has to be running.">
   <method-implementation language="c++" prototype="void set_config_version(const std::string&amp; name, bool reload)" body=""/>
   <method-implementation language="java" prototype="void set_config_version(final String version, boolean reload) throws config.GenericException, config.SystemException, config.NotFoundException, config.NotValidException" body="dal.Algorithms.set_config_version(UID(), version, reload);"/>
  </method>
  <method name="get_config_version" description="Return configuration version used by given partition, i.e. OKS GIT repository SHA. The partition infrastructure has to be running.">
   <method-implementation language="c++" prototype="std::string get_config_version()" body=""/>
   <method-implementation language="java" prototype="String get_config_version() throws config.GenericException, config.SystemException, config.NotFoundException, config.NotValidException" body="return dal.Algorithms.get_config_version(UID());"/>
  </method>
 </class>

 <class name="Platform" description="This abstract class is used to define base hw tags used in TDAQ." is-abstract="yes">
  <attribute name="HW_Tag" description="Set of all available hardware tags in the format: &quot;hardware platform&quot;-&quot;operating system&quot;" type="enum" range="i686-slc6,x86_64-slc6,x86_64-mac108,x86_64-cc7,x86_64-centos7,x86_64-centos8,x86_64-centos9,aarch64-centos7,aarch64-centos8,aarch64-centos9,armv7-centos7,armv7-centos8" init-value="x86_64-centos7" is-not-null="yes"/>
 </class>

 <class name="PlatformCompatibility" description="The class describes compatibility of HW platforms">
  <superclass name="Platform"/>
  <relationship name="CompatibleWith" description="List of platforms compatible with given one" class-type="PlatformCompatibility" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="RM_HW_Resource">
  <superclass name="RM_Resource"/>
  <attribute name="HardwareClass" type="string"/>
 </class>

 <class name="RM_Resource" description="The Resource class is used to describe shared and exclusive resources used by the processes: the name of the resource, the maximum numbers of copies per partition and per system (i.e. total), and documentation (help URL and comments). The dynamic part of a resource includes the list of processes that allocated this resource.&#xA;An example of a resource could be a run-time license (for example we can start limited number of processes with GUI that use some commercial widget). A resource can describe some hardware resources (for example we can not have two concurrent processes that write on the same type recorder device). The use of resources can be connected with the architecture of the process (for example, we do not want to allow start simultaneously several GUI editors for the same data, if there is no concurrent update of graphical view or the creator of software objects knows that it must be started only once per system or per partition, etc.)." is-abstract="yes">
  <attribute name="Description" type="string"/>
  <attribute name="MaxCopyPerPartition" type="s32" init-value="1"/>
  <attribute name="MaxCopyTotal" type="s32" init-value="1"/>
  <attribute name="HelpLink" type="string" init-value="http://"/>
 </class>

 <class name="RM_SW_Resource">
  <superclass name="RM_Resource"/>
 </class>

 <class name="Rack">
  <superclass name="HW_Object"/>
  <superclass name="Component"/>
  <relationship name="Nodes" class-type="ComputerBase" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="yes"/>
  <relationship name="Crates" class-type="Crate" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="yes" is-dependent="no"/>
  <relationship name="LFS" description="Local File Servers of the rack (can be more than one)." class-type="Computer" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Resource">
  <superclass name="ResourceBase"/>
 </class>

 <class name="ResourceApplication" description="The class describes an application, that can be enabled or disabled in the scope of partition.">
  <superclass name="CustomLifetimeApplication"/>
  <superclass name="Resource"/>
 </class>

 <class name="ResourceBase">
  <superclass name="Component"/>
  <method name="get_resources" description="Returns list of resources including defined by the nested sets. If partition parameter is provided (i.e. it is not &lt;b&gt;null&lt;/b&gt;), only enabled resources are added.">
   <method-implementation language="c++" prototype="void get_resources(conffwk::Configuration&amp; db, std::list&lt;const Resource *&gt;&amp; out, const Partition * p = 0) const" body=""/>
  </method>
 </class>

 <class name="ResourceSet">
  <superclass name="ResourceBase"/>
  <relationship name="Contains" description="A resource set is a container of resources to easily implement group operations (add/remove, enable/disable)." class-type="ResourceBase" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="ResourceSetAND" description="This resource set is considered disabled when ALL nested resources are disabled.">
  <superclass name="ResourceSet"/>
 </class>

 <class name="ResourceSetOR" description="This resource set is considered disabled when ANY nested resource is disabled.">
  <superclass name="ResourceSet"/>
 </class>

 <class name="ResourcesInfoConfig" description="Describes full configuration of ResourceInfo service. An instance of that class to be linked with Partition object to enable the service.">
  <attribute name="ArchiveInCOOL" description="If true, the resources info is stored on COOL. Otherwise the resources info is only published in IS." type="bool" init-value="false"/>
  <relationship name="DetectorFolders" description="Defines detectors folders." class-type="ResourcesInfoDetectorConfig" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="GlobalFolder" description="Mandatory relationship on folder collecting resources shared by several detectors. The mix and max ID values are ignored, but sub-folders config is used." class-type="ResourcesInfoDetectorConfig" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="DefaultDetectorSubFolders" description="Defines sub-folders for all detectors" class-type="ResourcesInfoDetectorFolderConfig" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="ResourcesInfoDetectorConfig">
  <attribute name="FolderName" description="Defines name of detector folder." type="string" is-not-null="yes"/>
  <attribute name="SubDetectorIDs" description="Defines sub-detector identifiers for given detector group (see ranges in eformat/SourceIdentifier.hpp of tdaq-common release)." type="u8" format="hex" is-multi-value="yes"/>
  <relationship name="SubFolders" description="Defines structure of detector sub-folders.&#xA;The order of sub-folders in this list defines selection priority:&#xA;if resource&apos;s class matches to a name of OKS base class,&#xA;the resource goes into given sub-folder." class-type="ResourcesInfoDetectorFolderConfig" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="ResourcesInfoDetectorFolderConfig" description="Describes configuration of detector sub-folder used by the ResourceInfo service.">
  <attribute name="FolderName" description="Defines name of detector sub-folder." type="string" is-not-null="yes"/>
  <attribute name="BaseClasses" description="Defines names of detector resource base classes. If resource class is derived from any such class, it is archived in given detector sub-folder." type="string" is-multi-value="yes" is-not-null="yes"/>
 </class>

 <class name="RunControlApplication">
  <superclass name="RunControlApplicationBase"/>
  <superclass name="Application"/>
 </class>

 <class name="RunControlApplicationBase" is-abstract="yes">
  <superclass name="IPCServiceApplicationBase"/>
  <attribute name="ActionTimeout" description="Maximum time (unit is seconds!) allowed to change a state, before a timeout warning shall be raised.." type="s32" init-value="10" is-not-null="yes"/>
  <attribute name="ProbeInterval" description="Defines at what interval (in seconds) a controller shall probe its children." type="s32" init-value="25" is-not-null="yes"/>
  <attribute name="FullStatisticsInterval" description="Defines at what time interval (in seconds) the controller shall request complete operational statistics to its children." type="s32" init-value="63" is-not-null="yes"/>
  <attribute name="IfError" description="This attribute is used by the parent controller to know how to react in case that this controlled application goes in Error state or sends a FATAL error." type="enum" range="Error,Ignore,Restart,Handle"/>
  <attribute name="ControlsTTCPartitions" description="Flag that indicates whether on this controller the dynamic restart during a run can by applied." type="bool" init-value="false"/>
 </class>

 <class name="RunControlTemplateApplication">
  <superclass name="RunControlApplicationBase"/>
  <superclass name="TemplateApplication"/>
 </class>

 <class name="RunTagList">
  <attribute name="RunTags" description="Array of user defined tags which will be added to the run description.&#xA;Format is: tag_name={predefined_value_1, predefined_value_2...}} or tag_name if there are no predefined values." type="string" is-multi-value="yes"/>
 </class>

 <class name="SW_ExternalPackage">
  <superclass name="SW_Package"/>
  <relationship name="Binaries" description="Maps package specific dir with binaries to CMT one" class-type="TagMapping" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="SharedLibraries" description="Maps package specific dir with shared libraries to CMT one" class-type="TagMapping" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SW_Object" description="This class is used to describe platform independent part of DAQ software component from logical point of view.&#xA;The platform dependent part is described by &apos;Program&apos; class.&#xA;To start DAQ software component it is necessary to create an instance of &apos;SW_Module&apos; class." is-abstract="yes">
  <superclass name="TestableObject"/>
  <attribute name="BinaryName" description="Name of executable file." type="string" is-not-null="yes"/>
  <attribute name="Description" description="Description of executable file. Often it is a result of --help command line option." type="string"/>
  <attribute name="Authors" description="Lists developers of given binary." type="string" is-multi-value="yes"/>
  <attribute name="HelpURL" description="URL to provide more information about binary." type="string" init-value="http://"/>
  <relationship name="Needs" description="Point to RM resources required by given binary. If defined, such resources are allocated by PMG before starting this binary." class-type="RM_Resource" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="BelongsTo" description="A software object has to belong to some repository, that defines various paths and environment required to run such binary." class-type="SW_Repository" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Uses" description="A software object can use zero or many software repositories&#xA;(here &quot;uses&quot; means that at least it needs shared libraries from them)." class-type="SW_Package" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SW_Package" description="Describe common properties of SW repository and ExternalPackage classes" is-abstract="yes">
  <attribute name="Name" description="The string defines name of the software repository." type="string" init-value="Unknown SW" is-not-null="yes"/>
  <attribute name="InstallationPath" description="The string defines the software repository installation path." type="string" init-value="/usr/local" is-not-null="yes"/>
  <attribute name="PatchArea" description="If patch area is non-empty, it is added to:&#xA;* the PATH and the LD_LIBRARY_PATH process environment variables of sw objects using it;&#xA;* the possible binary file names (i.e. if exists, binary will be taken from the patch area)." type="string"/>
  <relationship name="Uses" description="Define others sw repositories which are used by given one.&#xA;This adds paths to bin and lib directories of the repository&apos; programs." class-type="SW_Package" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ProcessEnvironment" description="A software package defines environment variables to be set for any application using such sw package." class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="AddProcessEnvironment" class-type="SW_PackageVariable" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SW_PackageVariable" description="This class is used to extend process environment defined by a sw package. The value of suffix is added to the sw package installation path and appended to the variable using colon separator.">
  <attribute name="Description" type="string"/>
  <attribute name="Name" description="Name of environment variable." type="string" is-not-null="yes"/>
  <attribute name="Suffix" description="The suffix is appended to the SW_Package installation path and the resulted value is appended to the variable value separated by colon sign." type="string"/>
 </class>

 <class name="SW_Repository" description="The sw repository describes an installation area of sw release built on top of CMT.">
  <superclass name="SW_Package"/>
  <attribute name="ISInfoDescriptionFiles" description="List of files describing IS information produced by the computer programs of given repository." type="string" is-multi-value="yes"/>
  <attribute name="IGUIProperties" description="List of properties to be passed to IGUI, when this sw repository is used by partition." type="string" is-multi-value="yes"/>
  <attribute name="InstallationPathVariableName" description="The value defines variable to be created by DAL algorithm, if an application belongs or uses this sw repository. It is ignored, if empty." type="string"/>
  <relationship name="Tags" description="List tags available in given sw repository. Any binary belonging to the repository should have implementations for each tag." class-type="Tag" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="SW_Objects" description="A software repository contains at least one software object.  A referenced software object shall point to the same software repository (i.e. a software object can&apos;t be shared by several repositories)." class-type="SW_Object" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Script" description="This class is used to describe a script program. The scripts are usually installed on share/bin directory.">
  <superclass name="ComputerProgram"/>
  <attribute name="Shell" description="Specify shell script interpreter." type="string"/>
 </class>

 <class name="Segment" description="A segment is self-sufficient part of the system which can be configured and controlled independently from the rest of the TDAQ system. A segment represents a detector, a system or their part. A segment can include other segments. A segment is controlled by associated RC controller application.&#xA;To be used by the partition it has to be added to the partition&apos;s Segments relationship. To be temporary ignored a segment can be disabled, i.e. added to the partition&apos;s Disabled relationship. When a segment is disabled, all nested segments are also disabled.&#xA;A segment can include applications and resources.&#xA;For more information read https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_2_Segment_Classes">
  <superclass name="Component"/>
  <relationship name="Segments" description="Nested segments of given segment." class-type="Segment" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
  <relationship name="UsesObjects" description="A segment state depends on state of hw objects it uses." class-type="HW_Object" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="UsesSystems" description="A segment state depends on state of hw systems it uses." class-type="HW_System" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Resources" class-type="ResourceBase" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
  <relationship name="Infrastructure" description="Infrastructure applications are started before any other applications from given and all included segments." class-type="InfrastructureBase" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Applications" description="Normal applications of segment." class-type="BaseApplication" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="no"/>
  <relationship name="ProcessEnvironment" description="Process environment defined for all applications of given and nested segments." class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="IsControlledBy" description="RunControl application controlling the segment." class-type="RunControlApplicationBase" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="DefaultTags" description="If an application has no explicit tag, first suitable tag from this list will be used to select binary for that application for given and nested segments (if not overwritten by them)." class-type="Tag" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="JarFiles" class-type="JarFile" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Parameters" description="Parameters which are used by database objects belonging to this segment." class-type="Parameter" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Hosts" description="Defines host where to run segment&apos;s applications without explicitly defined host.&#xA;The first host is state &quot;On&quot; is used to run normal applications and template applications with &quot;RunsOn&quot; = &quot;FirstHost&quot;.&#xA;The other hosts are used for template applications with &quot;RunsOn&quot; = &quot;All*Hosts&quot;." class-type="ComputerBase" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="TestRepositories" description="Links the Segment with the specific Tests which can be performed on it." class-type="TestRepository" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="SubTransitions" description="The list of sub-transitions this segment&apos;s controller will dispatch to its children" class-type="SubTransition" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <method name="get_timeouts" description="calculates the timeouts for long and short execution of run control commands: shortTimeout and actionTimeout.&#xA;throws dunedaq::dal::BadSegment&#xA;Requires:&#xA;- reference to Configuration&#xA;- reference to Partition">
   <method-implementation language="c++" prototype="void get_timeouts(int &amp; actionTimeout, int &amp; shortActionTimeout) const" body=""/>
  </method>
  <method name="find_is_server_by_mask" description="The method searches nearest IS server between this segment and partition with name including given mask.">
   <method-implementation language="c++" prototype="std::string find_is_server_by_mask(const std::string&amp; mask, const dunedaq::dal::Partition&amp; partition) const" body=""/>
  </method>
  <method name="get_all_applications" description="Get all application of this and nested segments.&#xA;In the parameters one can precise types of applications, names of segments and hosts the applications run on. The method is used to implement partition&apos;s get_all_applications() algorithm returning description of all applications running in the partition; in this case it is run on partition&apos;s online segment.">
   <method-implementation language="c++" prototype="std::vector&lt;const dunedaq::dal::BaseApplication *&gt; get_all_applications(std::set&lt;std::string&gt; * app_types = nullptr, std::set&lt;std::string&gt; * use_segments = nullptr, std::set&lt;const Computer *&gt; * use_hosts = nullptr) const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="dal.BaseApplication[] get_all_applications(String[] app_types, String[] use_segments, dal.Computer[] use_hosts) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return dal.SegConfig.get_all_applications(this, app_types, use_segments, use_hosts);"/>
  </method>
  <method name="get_controller" description="">
   <method-implementation language="c++" prototype="const dunedaq::dal::BaseApplication * get_controller() const" body="ADD_ALGO_1"/>
   <method-implementation language="java" prototype="dal.BaseApplication get_controller() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).get_controller();"/>
  </method>
  <method name="get_infrastructure" description="">
   <method-implementation language="c++" prototype="const std::vector&lt;const dunedaq::dal::BaseApplication *&gt;&amp; get_infrastructure() const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="dal.BaseApplication[] get_infrastructure() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).get_infrastructure();"/>
  </method>
  <method name="get_applications" description="">
   <method-implementation language="c++" prototype="const std::vector&lt;const dunedaq::dal::BaseApplication *&gt;&amp; get_applications() const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="dal.BaseApplication[] get_applications() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).get_applications();"/>
  </method>
  <method name="get_nested_segments" description="The algorithm calculates a vector of nested segments including templated ones.&#xA;">
   <method-implementation language="c++" prototype="const std::vector&lt;const dunedaq::dal::Segment*&gt;&amp; get_nested_segments() const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="dal.Segment[] get_nested_segments() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).get_nested_segments();"/>
  </method>
  <method name="get_hosts" description="">
   <method-implementation language="c++" prototype="const std::vector&lt;const dunedaq::dal::Computer*&gt;&amp; get_hosts() const" body="ADD_ALGO_N"/>
   <method-implementation language="java" prototype="Computer[] get_hosts() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).get_hosts();"/>
  </method>
  <method name="get_base_segment" description="">
   <method-implementation language="c++" prototype="const Segment * get_base_segment() const" body="ADD_ALGO_1"/>
   <method-implementation language="java" prototype="dal.Segment get_base_segment() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).get_base_segment();"/>
  </method>
  <method name="is_disabled" description="">
   <method-implementation language="c++" prototype="bool is_disabled() const" body=""/>
   <method-implementation language="java" prototype="boolean is_disabled() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).is_disabled();"/>
  </method>
  <method name="is_templated" description="">
   <method-implementation language="c++" prototype="bool is_templated() const" body=""/>
   <method-implementation language="java" prototype="boolean is_templated() throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return get_seg_config(false,false).is_templated();"/>
  </method>
  <method name="get_seg_config" description="">
   <method-implementation language="c++" prototype="SegConfig * get_seg_config(bool check_disabled, bool no_except = false) const" body="BEGIN_HEADER_PROLOGUE&#xA;#include &lt;atomic&gt;&#xA;#include &lt;dal/seg-config.hpp&gt;&#xA;END_HEADER_PROLOGUE&#xA;&#xA;BEGIN_PRIVATE_SECTION&#xA;std::unique_ptr&lt;SegConfig&gt; p_seg_config;&#xA;mutable std::atomic&lt;const Segment *&gt; p_gen_obj;&#xA;friend class Partition;&#xA;friend class AlgorithmUtils;&#xA;END_PRIVATE_SECTION&#xA;&#xA;BEGIN_MEMBER_INITIALIZER_LIST&#xA;p_gen_obj(nullptr)&#xA;END_MEMBER_INITIALIZER_LIST"/>
   <method-implementation language="java" prototype="dal.SegConfig get_seg_config(boolean check_disabled, boolean no_except) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="BEGIN_PRIVATE_SECTION&#xA;dal.SegConfig p_seg_config;&#xA;dal.Segment p_gen_obj;&#xA;END_PRIVATE_SECTION&#xA;&#xA;return dal.ApplicationConfig.get_seg_config(this, check_disabled, no_except);"/>
  </method>
 </class>

 <class name="SubTransition">
  <attribute name="MainTransition" description="The main transition the sub-transition refers to" type="enum" range="CONFIGURE,CONNECT,START,STOPROIB,STOPDC,STOPHLT,STOPRECORDING,STOPGATHERING,STOPARCHIVING,DISCONNECT,UNCONFIGURE" init-value="CONFIGURE" is-not-null="yes"/>
  <attribute name="Substeps" description="Sub-steps for one of the main transitions" type="string" is-multi-value="yes" is-not-null="yes"/>
 </class>

 <class name="Tag" description="Defines available CMT tags.">
  <superclass name="Platform"/>
  <attribute name="SW_Tag" description="Available compilers and their instrumentations." type="enum" range="gcc49-opt,gcc49-dbg,gcc62-opt,gcc62-dbg,gcc7-opt,gcc7-dbg,gcc8-opt,gcc8-dbg,gcc9-opt,gcc9-dbg,clang80-opt,clang80-dbg,clang39-opt,clang39-dbg,clang8-opt,clang8-dbg,clang9-opt,clang9-dbg,clang12-opt,clang12-dbg,clang13-opt,clang13-dbg,clang14-opt,clang14-dbg,gcc10-opt,gcc10-dbg,gcc11-opt,gcc11-dbg,gcc12-opt,gcc12-dbg" init-value="gcc8-opt" is-not-null="yes"/>
 </class>

 <class name="TagMapping" description="Is used to map CMT tag installation on model used by external package, e.g.: i686-slc4-gcc34-opt/bin is mapped on slc4_ia32_gcc34/bin">
  <superclass name="Tag"/>
  <attribute name="Value" description="Defines mapping of value depending from tag." type="string"/>
 </class>

 <class name="TemplateApplication" description="This class is used to describe many process to be started.&#xA;A template application is referenced by segment objects, which keep lists of template application hosts.&#xA;For more information about template applications read https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltDal#3_3_Application_Classes" is-abstract="yes">
  <superclass name="BaseApplication"/>
  <attribute name="Instances" description="Defines number of instances per template host. If number is set to 0, then the number of instances on a host is equal to the number of it&apos;s CPU cores." type="u16" init-value="1"/>
  <attribute name="RunsOn" description="Describe where to run template application.&#xA;For a segment the list of hosts is defined by &quot;Hosts&quot; relationship.&#xA;For template segment the list of hosts is defined by rack&apos;s hosts.&#xA;The &quot;FirstHost&quot; is first host in the list in state &quot;On&quot; without a possibility to restart application on a backup host.&#xA;The &quot;FirstHostWithBackup&quot; is similar to above and allows to restart application on one of enabled hosts.&#xA;Error is raised if:&#xA;1) &quot;FirstHost&quot; or &quot;AllHosts&quot; is set, but there are no segment hosts in state &quot;On&quot;&#xA;2) &quot;AllButFirstHost&quot; is set, but there is only one segment host in state &quot;On&quot;" type="enum" range="FirstHost,FirstHostWithBackup,AllButFirstHost,AllHosts" init-value="AllButFirstHost" is-not-null="yes"/>
 </class>

 <class name="TemplateSegment" description="The HLTSegment has to be used to describe a segment with template applications.">
  <superclass name="Segment"/>
  <relationship name="Racks" class-type="Rack" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="TestRepository" description="Abstract class to allow set of tests to be linked to the Partition or Segment objects (implementation of it in testdal)." is-abstract="yes">
 </class>

 <class name="TestableObject" description="An object that may have test (test4Object) associated and therefore be testable with test manager.&#xA;This is an abstract class, real testable classes must be inherited (e.g. Computer, Module)." is-abstract="yes">
 </class>

 <class name="TriggerConfiguration" description="Object for the trigger-configuration settings for LVL1 and HLT">
  <attribute name="LatencyValue" description="LVL1 trigger latency offset value (e.g., 0 refers to the standard Physics configuration)" type="s32" init-value="0"/>
  <attribute name="TriggerCoolConnection" description="Database to write HLT prescale changes to.&#xA;This is used by the CTP or the HLTSV in pre-loaded mode." type="string"/>
  <relationship name="l1" description="The L1 configuration parameters" class-type="L1TriggerConfiguration" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="hlt" description="The L2 implementation to be loaded in Level-2 processors" class-type="HLTImplementation" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="TriggerDBConnection" description="Object containing the database connection parameters for the TriggerDB." class-type="TriggerDBConnection" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="DBConnections" description="Links the description of DB connections needed to configure the Trigger to the TriggerConfiguration object.&#xA;This relationship excludes the TriggerDB connection which is linked via the TriggerDBConnections relationship. " class-type="DBConnection" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="TriggerDBConnection" description="Describes the database connection to be used to obtain trigger-configuration parameters">
  <superclass name="DBConnection"/>
  <attribute name="SuperMasterKey" description="The super-master key for the configuration in the database" type="u32" init-value="0"/>
 </class>

 <class name="Variable" description="Variable allows to associate a value with string name. It is used for process environment and database strings substitution. In some cases the value of application process environment depends on context of variable usage (when TagValues relationship is set).">
  <superclass name="Parameter"/>
  <attribute name="Name" description="Name of the variable." type="string"/>
  <attribute name="Value" description="Default value of the variable. If TagValues is not empty, the value can be re-defined by corresponding tag in the context of the application&apos;s process environment." type="string"/>
  <relationship name="TagValues" description="Defines value of variable for given tag." class-type="TagMapping" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <method name="get_value" description="The method returns value of variable depending on the application context (if tag is provided).">
   <method-implementation language="c++" prototype="const std::string&amp; get_value(const Tag * = 0) const" body=""/>
   <method-implementation language="java" prototype="String get_value(Tag tag) throws config.GenericException, config.NotFoundException, config.NotValidException, config.SystemException" body="return dal.Algorithms.get_value(this, tag);"/>
  </method>
 </class>

 <class name="VariableSet" description="Set of variables or variable sets. Names and values of all nested variables are added to value of relationship using resource set.">
  <superclass name="Parameter"/>
  <relationship name="Contains" description="List of included variables or variable sets." class-type="Parameter" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="WarmStartStopReactor" description="This class has two attributes to flag to the run control what should be done with an application at warm start/stop." is-abstract="yes">
  <attribute name="RestartAtWarmStart" description="Set to true if you want your application to be restarted at warm start." type="bool" init-value="true"/>
  <attribute name="RestartAtWarmStop" description="Set to true if you want your application to be restarted at warm stop" type="bool" init-value="false"/>
 </class>

</oks-schema>
```


## Scripts and data

### `scripts/tutorial.py`  
*Local path: `repo/dune-dal/scripts/tutorial.py`*

```python
#!/bin/env python3

import conffwk
import os

schemafile=f'{os.environ["DAL_SHARE"]}/schema/dal/tutorial.schema.xml'
datafile="tutorial.data.xml"

# binds a new dal into the module named "tutorial"               
tutorial = conffwk.dal.module('tutorial', schemafile)

db = conffwk.Configuration("oksconflibs")
db.create_db(datafile, [schemafile])

readout_app1 = tutorial.ReadoutApplication("PhotonReadout", 
                                          Name="/full/pathname/of/readout/executable",
                                          SubDetector="PMT")

readout_app2 = tutorial.ReadoutApplication("TPCReadout", 
                                          Name="/full/pathname/of/readout/executable",
                                          SubDetector="WireChamber")

runcontrol_app = tutorial.RCApplication("DummyRC",
                                                Name="/full/pathname/of/RC/executable",
                                                ApplicationsControlled=[readout_app1, readout_app2])

db.update_dal(readout_app1)
db.update_dal(readout_app2)
db.update_dal(runcontrol_app)
db.commit()

print(f"""
Please take a look at {datafile} for the data file this script 
created using OKS classes from {schemafile}
""")
```

### `scripts/dal_testing.data.xml`  
*Local path: `repo/dune-dal/scripts/dal_testing.data.xml`*

```xml
<?xml version="1.0" encoding="ASCII"?>

<!-- oks-data version 2.2 -->


<!DOCTYPE oks-data [
  <!ELEMENT oks-data (info, (include)?, (comments)?, (obj)+)>
  <!ELEMENT info EMPTY>
  <!ATTLIST info
      name CDATA #IMPLIED
      type CDATA #IMPLIED
      num-of-items CDATA #REQUIRED
      oks-format CDATA #FIXED "data"
      oks-version CDATA #REQUIRED
      created-by CDATA #IMPLIED
      created-on CDATA #IMPLIED
      creation-time CDATA #IMPLIED
      last-modified-by CDATA #IMPLIED
      last-modified-on CDATA #IMPLIED
      last-modification-time CDATA #IMPLIED
  >
  <!ELEMENT include (file)*>
  <!ELEMENT file EMPTY>
  <!ATTLIST file
      path CDATA #REQUIRED
  >
  <!ELEMENT comments (comment)*>
  <!ELEMENT comment EMPTY>
  <!ATTLIST comment
      creation-time CDATA #REQUIRED
      created-by CDATA #REQUIRED
      created-on CDATA #REQUIRED
      author CDATA #REQUIRED
      text CDATA #REQUIRED
  >
  <!ELEMENT obj (attr | rel)*>
  <!ATTLIST obj
      class CDATA #REQUIRED
      id CDATA #REQUIRED
  >
  <!ELEMENT attr (data)*>
  <!ATTLIST attr
      name CDATA #REQUIRED
      type (bool|s8|u8|s16|u16|s32|u32|s64|u64|float|double|date|time|string|uid|enum|class|-) "-"
      val CDATA ""
  >
  <!ELEMENT data EMPTY>
  <!ATTLIST data
      val CDATA #REQUIRED
  >
  <!ELEMENT rel (ref)*>
  <!ATTLIST rel
      name CDATA #REQUIRED
      class CDATA ""
      id CDATA ""
  >
  <!ELEMENT ref EMPTY>
  <!ATTLIST ref
      class CDATA #REQUIRED
      id CDATA #REQUIRED
  >
]>

<oks-data>

<!-- JCF, Jan-18-2023: the entire point of this file is that it defines objects which can be used for the dal repo's algorithm_tests.py script. The values of the attributes, etc., have no useful meaning. -->

<info name="" type="" num-of-items="2" oks-format="data" oks-version="N/A" created-by="jcfree" created-on="mu2edaq13.fnal.gov" creation-time="20230105T194746" last-modified-by="jcfree" last-modified-on="mu2edaq13.fnal.gov" last-modification-time="20230105T194746"/>

<include>
 <file path="../share/schema/dal/core.schema.xml"/>
</include>

<obj class="Partition" id="ToyPartition">

  <rel name="OnlineInfrastructure" class="OnlineSegment" id="ToyOnlineSegment"/>
  <rel name="DefaultHost" class="Computer" id="toyhost.fnal.gov"/>
  
  <rel name="Disabled">
    <ref class="ResourceBase" id="AProblematicResource">
  </rel>
</obj>

<obj class="ResourceBase" id="AProblematicResource">
</obj>


<obj class="RunControlApplication" id="ToyRunControlApplication">
 <attr name="InterfaceName" type="string" val="rc/commander"/>
 <attr name="ActionTimeout" type="s32" val="10"/>
 <attr name="ProbeInterval" type="s32" val="5"/>
 <attr name="FullStatisticsInterval" type="s32" val="60"/>
 <attr name="ControlsTTCPartitions" type="bool" val="0"/>
 <attr name="Logging" type="bool" val="1"/>
 <attr name="InitTimeout" type="u32" val="60"/>
 <attr name="ExitTimeout" type="u32" val="5"/>
 <attr name="RestartableDuringRun" type="bool" val="0"/>
 <attr name="IfExitsUnexpectedly" type="enum" val="Error"/>
 <attr name="IfFailsToStart" type="enum" val="Error"/>
 <rel name="Program" class="Binary" id="rc_controller"/> 
 <rel name="ExplicitTag" class="Tag" id="ToyTag"/>
</obj>

<obj class="SW_Repository" id="ToyRepository">
  <rel name="Tags">
   <ref class="Tag" id="ToyTag"/>
  </rel>
</obj>

<obj class="Binary" id="rc_controller">
 <attr name="BinaryName" type="string" val="rc_controller"/>
 <attr name="Description" type="string" val="A Controller implementing all the default actions"/>
 <attr name="HelpURL" type="string" val=""/>
 <attr name="DefaultParameters" type="string" val="foo bar"/>
 <rel name="BelongsTo" class="SW_Repository" id="ToyRepository"/> 
</obj>

<obj class="Binary" id="coolapp">
 <attr name="BinaryName" type="string" val="coolapp"/>
 <attr name="Description" type="string" val="Just a straight-up amazing application"/>
 <attr name="HelpURL" type="string" val=""/>
 <attr name="DefaultParameters" type="string" val="arg1 arg2 arg3"/>
 <rel name="BelongsTo" class="SW_Repository" id="ToyRepository"/> 
</obj>


<obj class="CustomLifetimeApplication" id="SomeApp">
 <attr name="Lifetime" type="enum" val="UserDefined_Shutdown"/>
 <attr name="AllowSpontaneousExit" type="bool" val="0"/>
 <rel name="Program" class="Binary" id="coolapp"/> 
 <rel name="ExplicitTag" class="Tag" id="ToyTag"/>
</obj>


<obj class="OnlineSegment" id="ToyOnlineSegment">
 <attr name="T0_ProjectTag" type="string" val="data_test"/> 
 <rel name="IsControlledBy" class="RunControlApplication" id="ToyRunControlApplication"/>
 <rel name="InitialPartition" class="Partition" id="ToyPartition">
 <rel name="Applications">
   <ref class="CustomLifetimeApplication" id="SomeApp"/>
 </rel>
  <rel name="Segments">
    <ref class="Segment" id="ToyChildSegment"/>
  </rel>
</obj>

<obj class="Segment" id="ToyChildSegment"/>
 <rel name="IsControlledBy" class="RunControlApplication" id="ToyRunControlApplication"/>
</obj>

<obj class="Tag" id="ToyTag">
 <attr name="HW_Tag" type="enum" val="x86_64-centos7"/>
 <attr name="SW_Tag" type="enum" val="gcc49-opt"/>
</obj>

<obj class="Computer" id="toyhost.fnal.gov">
 <attr name="HW_Tag" type="enum" val="x86_64-centos7"/>
 <attr name="SW_Tag" type="enum" val="gcc49-opt"/>
 <attr name="Type" type="string" val="Intel(R) Xeon(TM) CPU 3.40GHz"/>
 <attr name="Location" type="string" val=""/>
 <attr name="Description" type="string" val=""/>
 <attr name="HelpLink" type="string" val=""/>
 <attr name="InstallationRef" type="string" val=""/>
 <attr name="State" type="bool" val="1"/>
 <attr name="Memory" type="u16" val="514"/>
 <attr name="CPU" type="u16" val="3400"/>
 <attr name="NumberOfCores" type="s16" val="2"/>
 <attr name="RLogin" type="string" val="ssh"/>
</obj>

<!-- JCF, Jan-17-2023: this snippet is derived from /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-09-05-00/TM/data/part_hlt.data.xml as an example of a Variable -->
<obj class="Variable" id="PYTHONPATH">
 <attr name="Description" type="string" val=""/>
 <attr name="Name" type="string" val="PYTHONPATH"/>
 <attr name="Value" type="string" val="${LCG_INST_PATH}/LCG_95/Python/2.7.15"/>
 <rel name="TagValues">                                                                  
  <ref class="TagMapping" id="ToyTagMapping"/>
 </rel>
</obj>

<obj class="TagMapping" id="ToyTagMapping">
 <attr name="HW_Tag" type="enum" val="x86_64-centos7"/>
 <attr name="SW_Tag" type="enum" val="gcc49-opt"/>
 <attr name="Value" type="string" val="12345"/>
</obj>


</oks-data>
```

### `scripts/algorithm_tests.py`  
*Local path: `repo/dune-dal/scripts/algorithm_tests.py`*

```python
#!/bin/env python

from __future__ import print_function
import dal
import sys
import conffwk
import os
import subprocess
import filecmp

test_output_verbose = True

def print_output(res1, res2):
    if test_output_verbose:
        print("")
        print("=====================Output When Python Bindings to C++ Used======================")
        print("")
        print(res1)
        print("")
        print("===========================Output When Original C++ Used==========================")
        print("")
        print(res2)
        print("")
        print("==================================================================================")

def check (result, test_name) :
    if result == True:
        print("")
        print(test_name + ": PASS")
    else :
        print("")
        print(test_name + ": FAIL")
        raise RuntimeError("")  

def print_app(app):
    return app.get_app_id() + "@" + app.get_base_app().class_name + " on " + app.get_host().id + "@" + app.get_host().class_name

def print_segment(seg):
    res = "segment: " + seg.get_seg_id() + '\n'

    res += "controller: " + print_app(seg.get_controller()) + '\n'

    infr= seg.get_infrastructure()
    if ( (infr is not None) and (not (len(infr) == 0)) ):
        res += "infrastructure:\n"
        for i in range (0,len(infr)) :
            res += print_app(infr[i]) + '\n'
    else:
        res += "no infrastructure\n"

    apps= seg.get_applications()
    if ( (apps is not None) and (not (len(apps) == 0)) ):
        res += "applications:\n"
        for i in range (0,len(apps)) :
            res += print_app(apps[i]) + '\n'
    else:
        res += "no applications\n"

    hosts= seg.get_hosts()
    if ( (hosts is not None) and (not (len(hosts) == 0)) ):
        res += "hosts:\n"
        for i in range (0,len(hosts)) :
            res += hosts[i].id + "@" + hosts[i].class_name + '\n'
    else:
        res += "no hosts\n"

    nested_segs=seg.get_nested_segments()
    if ( (nested_segs is not None) and (not (len(nested_segs) == 0)) ):
        res += "nested segments:\n"
        for i in range (0,len(nested_segs)) :
            res += print_segment(nested_segs[i])
    else:
        res += "no nested segments\n"

    return res

def print_segment_timeout(seg):
    res = "segment " + seg.get_seg_id() + " actionTimeout: " + str(seg.get_timeouts()['actionTimeout']) + ", shortActionTimeout" + str(seg.get_timeouts()['shortActionTimeout'] ) + '\n'

    nested_segs=seg.get_nested_segments()
    if ( (nested_segs is not None) and (not (len(nested_segs) == 0)) ):
        for i in range (0,len(nested_segs)) :
            res += print_segment_timeout(nested_segs[i])

    return res

def get_timeouts_test_case () :
    root_seg = partition.get_segment(db, partition.OnlineInfrastructure.id)

    res1 = print_segment_timeout(root_seg)
    res2 = dal.get_timeouts_test(db._obj, partition.id, root_seg.get_seg_id())

    res1 = res1.replace(",","").replace("[","").replace("]","").replace(" ","").replace("\n","")
    res2 = res2.replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","").replace("\n","")

    print_output(res1, res2)

    return (res1 == res2) 


def get_parents_test_case () :
    
    res1 = ""
    components =  db.get_dals('Component')

    for i in range (0,len(components)) :
        res1 += str(components[i].get_parents(db, partition)) 
        res1 +='\n'
    
    res2 = ""
    for i in range (0,len(components)) : 

        res2+='['
        res2+=str(dal.get_parents_test(db._obj, partition.id, components[i].id)) 
        res2+= ']'  

    res1 = res1.replace(",","").replace("[","").replace("]","").replace(" ","").replace("\n","")
    res2 = res2.replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","").replace("\n","")

    print_output(res1, res2)

    return (res1 == res2) 


def get_log_directory_test_case () :

    res1 = ""
    parts =  db.get_dals('Partition')
    print("Number of partitions to be tested : " + str(len(parts)))
    for i in range (0,len(parts)) : 
        res1 += str(parts[i].get_log_directory(db)) 
        res1 +='\n'
    
    res2 = ""
    for i in range (0,len(parts)) : 
        res2+=str(dal.get_log_directory_test(db._obj, parts[i].id)) 

    res1 = res1.replace(",","").replace("[","").replace("]","").replace(" ","").replace("\n","")
    res2 = res2.replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","").replace("\n","")

    print_output(res1, res2)

    return (res1 == res2) 


def get_segment_test_case () :
    segs =  partition.Segments   
    print("Number of Segments to be tested : " + str(len(segs)+1))

    root_seg = partition.get_segment(db, partition.OnlineInfrastructure.id)

    res1 = print_segment(root_seg)
    for i in range (0,len(segs)) :
        res1 += print_segment(partition.get_segment(db, segs[i].id))
        res1 +='\n'

    res2 = dal.get_segment_test(db._obj, partition.id, root_seg.get_seg_id())
    for i in range (0,len(segs)) :
        res2+=str(dal.get_segment_test(db._obj, partition.id, segs[i].id))

    res1 = res1.replace(",","").replace("[","").replace("]","").replace(" ","").replace("\n","")
    res2 = res2.replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","").replace("\n","")

    print_output(res1, res2)

    return (res1 == res2) 

def get_disabled_test_case():

    res1 = ""
    components = db.get_dals('Component')    
    print("Number of components to be tested : " + str(len(components)))
    for i in range (0,len(components)) : 
        res1 += str(components[i].disabled(db, partition.id)) 
        res1 +='\n'

    res2 = ""
    for i in range (0,len(components)) : 
        res2+=str(dal.disabled_test(db._obj, partition.id, components[i].id)) 
    
    res1 = res1.replace(",","").replace("[","").replace("]","").replace(" ","").replace("\n","")
    res2 = res2.replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","").replace("\n","")

    print_output(res1, res2)
    return (res1 == res2) 

def get_value_test_case():
 
    res1 = ""
    variables =  db.get_dals('Variable')    
    print("Number of Variables to be tested : " + str(len(variables)))
     
    for i in range (0,len(variables)) :
        if len(variables[i].TagValues) != 0:
           tag = variables[i].TagValues[0] 
           res1 += str(variables[i].get_value(db, tag)) 
           res1 +='\n'
 
    res2 = ""
    for i in range (0,len(variables)) : 
        if len(variables[i].TagValues) != 0:
           tag = variables[i].TagValues[0]
           
           res2+=str(dal.get_value_test(db._obj, variables[i].id, tag.id) )

    res1 = res1.replace(",","").replace("[","").replace("]","").replace(" ","").replace("\n","")
    res2 = res2.replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","").replace("\n","")

    print_output(res1, res2)

    return (res1 == res2) 



if __name__ == '__main__':
    global db
    global partition

    if "TDAQ_DB_PATH" not in os.environ:
        os.environ["TDAQ_DB_PATH"] = os.environ["DUNEDAQ_SHARE_PATH"]

    scriptsdir=os.path.dirname(os.path.realpath(__file__))

    db_file=f"{scriptsdir}/dal_testing.data.xml"
    assert os.path.exists(db_file)
    db = conffwk.Configuration(f"oksconflibs:{db_file}")

    partition=db.get_dal("Partition", "ToyPartition")

    print(f"\n\nRUNNING TEST \"get_log_directory_test_case\"")
    check( get_log_directory_test_case(), "get_log_directory_test_case")

    print(f"\n\nRUNNING TEST \"get_segment_test_case\"")
    check( get_segment_test_case(), "get_segment_test_case")

    print(f"\n\nRUNNING TEST \"get_value_test_case\"")
    check( get_value_test_case(), "get_value_test_case")

    print(f"\n\nRUNNING TEST \"get_parents_test_case\"")
    check( get_parents_test_case(), "get_parents_test_case")

    print(f"\n\nRUNNING TEST \"get_disabled_test_case\"")
    check( get_disabled_test_case(), "get_disabled_test_case")

    print(f"\n\nRUNNING TEST \"get_timeouts_test_case\"")
    check( get_timeouts_test_case(), "get_timeouts_test_case")

    print("""
n.b. newlines have been removed from the test output above; the important 
thing is that the output agrees between calls to the C++ function and their
Python bindings
""")
```

### `scripts/dal_dump_apps.py`  
*Local path: `repo/dune-dal/scripts/dal_dump_apps.py`*

```python
#!/usr/bin/env python
import argparse
import sys
import conffwk
import dal    
import os
from argparse import RawTextHelpFormatter

def print_info(file_names,environment):
    print(" - possible program file names:")
    if file_names is None :
       print("no")
    else:
        for file in file_names:
           print("    * " + file)

    print(" - environment variables:")
    if environment is None :
       print("no")
    else:
        for key in sorted(environment):
            
           print("    * " + key + "=\"" + environment[key] + "\"")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Example of dunedaq::dal::Application::get_info() algorithm usage. The database name is defined either\n
       the -d command line parameter, or by the TDAQ_DB environment variable in format \"impl:parameter\",\n
       e.g. \"oksconflibs:/tmp/my-db.xml\". By default the algorithms are applied to all applications used by\n
       the partition are their results are printed out.\n\n
       usage: dal_dump_apps.py [-d | --data database-name]\n
                         [-p | --partition-id partition-id]\n
                         [-a | --application-id app-id]\n
                         [-n | --application-name app-name]\n
                         [-g | --application-segment-id seg-id]\n
        \n""", formatter_class=RawTextHelpFormatter)
    parser.add_argument("-d", "--data", help = "name of the database (ignore TDAQ_DB variable)" )
    parser.add_argument("-p", "--partition_id", help = "name of the partition object")
    parser.add_argument("-a", "--application_id", help = "identity of the application object (if not provided, dump all applications")
    parser.add_argument("-n", "--application_name", help = "name of the application object (if not provided, dump all applications)")
    parser.add_argument("-g", "--application_segment_id", help = "identity of the application's segment object (if defined,print apps of this segment")  
 
    args = parser.parse_args()

    for required_env_variable in ["TDAQ_IPC_INIT_REF", "TDAQ_DB_PATH", "TDAQ_DB_DATA"]:
        if required_env_variable not in os.environ:
            os.environ[required_env_variable] = "DUMMY_TDAQ_ENV_VALUE"

    # Open database
    db = conffwk.Configuration(args.data)
    #Get the application object
    app = 0
    if args.application_id : 
        app = db.get_dal('BaseApplication', args.application_id)
    if args.application_name :
        app = db.get_dal('BaseApplication', args.application_name.split(':')[0])  
        args.application_id = args.application_name
    # get Partition object
    partition = db.get_dal('Partition', args.partition_id)
    app_config_list = partition.get_all_applications(db, None, args.application_segment_id, None)  

    count = 0

    for i in app_config_list :
        if app and type(app) != int and (i.get_base_app().id != app.id): # recall app is initialized to the integer 0
            continue           
        if  i.is_templated() :
            if ((args.application_id is not None) ) and ( not (   args.application_name == i.app_id) ): #watch out for these 
                continue
        else :
            if (args.application_id is not None)  and ( not (   app.id == i.get_app_id()) ):
                continue

        count += 1
        if (':' in str(i.get_app_id()) ) or ('Template' in str(i.get_base_app().class_name) ) : # if it is type template app
           print("### (" + str(count) + ") template application " + i.get_app_id() + " ###")
        else: # if templated
           print("### (" + str(count) + ") application \'" + i.get_app_id() + '@' +i.get_base_app().class_name + "\' ###")

        info = i.get_info() 

        print(" - command line start args:\n    " +  info['startArgs'])
        print(" - command line restart args:\n    " +  info['restartArgs'])
        print_info(info['programNames'], info['environment'])

    if count == 0 :
        if app is not None and type(app) != int:  # recall app is initialized to the integer 0
           print("the application " + app.id + " is not running in the partition; it is disabled or not included into partition")
        elif args.application_name is not None:
           print("the application with name \'" + args.application_name + "\' is not running in the partition; it is disabled or not included into partition")
        elif args.application_segment_id is not None :
           print("the applications of segment " + args.application_segment_id + " are not running in the partition; the segment or it\'s applications are disabled or the segment is not included into partition")
```

### `scripts/dal_dump_app_config.py`  
*Local path: `repo/dune-dal/scripts/dal_dump_app_config.py`*

```python
#!/usr/bin/env python

class TableRow :
    def __init__(self, fill, separator, s1, s2, s3, s4, s5, s6):
        self.fill = fill
        self.separator = separator
        self.items = []
        if s1 is not None :
            self.items.append(s1)
            self.items.append(s2)
            self.items.append(s3)
            self.items.append(s4)
            self.items.append(s5)         
            self.items.append(s6)  
        else :
            self.items.append("=")
            self.items.append("=") 
            self.items.append("=") 
            self.items.append("=") 
            self.items.append("=") 
            self.items.append("=") 
                         
    @classmethod
    def fromhost(cls, fill, separator, host ):
        return cls(fill, separator, "", "", host.id + "@" + host.class_name , "", "", "")
    @classmethod
    def fromobjects(cls, fill, separator, num, app, host, seg, seg_id, app_id):
        return cls(fill, separator, num, app.id + "@" + app.class_name, host.id + "@" + host.class_name, seg.id + "@" + seg.class_name, seg_id, app_id )
    @classmethod
    def fromchar(cls, fill, separator):
        return cls(fill, separator, None,None,None,None,None,None)

  
if __name__ == '__main__':

    import argparse
    import sys    
     
    import conffwk

    import dal

        
    parser = argparse.ArgumentParser(description='''This program prints out applications and their configuration parameters using Partition::get_all_applications() algorithm.
        Usage: dal_dump_app_config.py [-d database-name] -p name-of-partition [-t [types ...]] [-c [ids ...]] [-s [ids ...]]''')
    parser.add_argument("-d", "--database_name", 
                        help="name of the database (ignore TDAQ_DB variable)")
    parser.add_argument("-p", "--partition_name", required = True,
                        help="name of the partition object")
    parser.add_argument("-t", "--application_types",   nargs = '*',
                        help="filter out all applications except given classes (and their subclasses)")
    parser.add_argument("-c", "--hosts",   nargs = '*',
                        help="filter out all applications except those which run on given hosts")
    parser.add_argument("-s", "--segments", nargs = '*',
                        help="filter out all applications except those which belong to given segments")  
    parser.add_argument("-b", "--show_backup_hosts", action='count',
                        help="print backup hosts")                       

    args = parser.parse_args()

      # Open test database
    db = conffwk.Configuration(args.database_name)

    # get Partition object
    partition = db.get_dal('Partition', args.partition_name)

    app_config_list = partition.get_all_applications(db, args.application_types , args.segments, args.hosts)

    print ('Got ' + str(len(app_config_list)) + ' applications:')

    rows = []
    rows.append(TableRow.fromchar('=', '='))
    rows.append(TableRow(' ', '|', "num","Application Object","Host","Segment","Segment unique id","Application unique id"))    
    rows.append(TableRow.fromchar('=', '='))    

    count = 1

    for i in app_config_list :
#         init = i.get_initialization_depends_from(app_config_list)
#         print "initialisation of",i.get_app_id(),"depends from",len(init)
#         shut = i.get_shutdown_depends_from(app_config_list)
#         for x in init:
#             print '   ',x.get_app_id(),'on',x.get_host().id
#         print "shutdown of",i.get_app_id(),"depends from",len(shut)
#         for x in shut:
#             print '   ',x.get_app_id(),'on',x.get_host().id
        rows.append(TableRow.fromobjects(' ', '|', str(count), i.get_base_app(), i.get_host(), i.get_base_seg(), i.get_seg_id(), i.get_app_id()))         
        count+=1
        if args.show_backup_hosts is not None:
            backup_hosts = i.get_backup_hosts()
            for j in backup_hosts :
                rows.append(TableRow.fromhost(' ', '|', j))  

    rows.append(TableRow.fromchar('=', '=')) 

    cw = [1,1,1,1,1,1]

    for row in rows:
        #print row.items
        for idx in range(0,6) : 
            length = len(str(row.items[idx]))
            if length > cw[idx]:
                cw[idx] = length
        #print cw

    align_left = [False, True, True, True, True, True]

    for row in rows :
        line =[]
        for idx in range(0,6):
            line.append(row.separator)
            line.append(row.fill)
            if align_left[idx]:
                line.append(row.items[idx])
                line.append(row.fill*(cw[idx]-len(row.items[idx]))) 
                line.append(row.fill)
            else :
                line.append(row.fill*(cw[idx]-len(row.items[idx])))        
                line.append(row.items[idx])        
                line.append(row.fill)

        line.append(row.separator)     
        line = ''.join(str(e) for e in line)  
        print(line)
                               
```


## Python bindings

### `python/dal/__init__.py`  
*Local path: `repo/dune-dal/python/dal/__init__.py`*

```python
import conffwk
import os
from ._daq_dal_py import * 


scriptsdir=os.path.dirname(os.path.realpath(__file__))

core_schema_name = f'{scriptsdir}/../../../share/schema/dal/core.schema.xml'
assert os.path.exists(core_schema_name), f"Couldn't find schema file {core_schema_name}"
dal_classes = conffwk.dal.module('dal_classes', core_schema_name)

Partition = dal_classes.Partition
Component = dal_classes.Component
Variable = dal_classes.Variable

def setify(arg):
    if arg is None:
        return set()
    elif type(arg) is str:
        return set( {arg} )
    else:
        return set(arg)

def _partition_get_all_applications_wrapper(self, db, app_types, use_segments, use_hosts):
    return partition_get_all_applications(db._obj, self.id, setify(app_types), setify(use_segments), setify(use_hosts))

def _partition_get_log_directory_wrapper(self, db):
    return partition_get_log_directory(db._obj, self.id)

def _partition_get_segment_wrapper(self, db, segname):
    return partition_get_segment(db._obj, self.id, segname)

def _component_get_parents_wrapper(self, db, partition):

    parents = []
    parents = component_get_parents(db._obj, partition.id, self.id)
    parent_list = []
    for p in parents:
        component_list = []
        for c in p:
            component_list.append(db.get_dal(c.class_name, c.id))
        parent_list.append(component_list)
    return parent_list

def _component_disabled_wrapper(self, db, partition):
    return component_disabled(db._obj, partition, self.id)

def _variable_get_value_wrapper(self, db, tag):
    return variable_get_value(db._obj, self.id, tag.id)

Partition.get_all_applications = _partition_get_all_applications_wrapper
Partition.get_log_directory = _partition_get_log_directory_wrapper
Partition.get_segment = _partition_get_segment_wrapper

Component.get_parents = _component_get_parents_wrapper
Component.disabled = _component_disabled_wrapper

Variable.get_value = _variable_get_value_wrapper
```

### `pybindsrc/module.cpp`  
*Local path: `repo/dune-dal/pybindsrc/module.cpp`*

```cpp
/**
 * @file module.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq::dal::python {

extern void
register_dal_classes(py::module&);

extern void
register_algorithm_test_bindings(py::module&);

PYBIND11_MODULE(_daq_dal_py, m)
{

  m.doc() = "Python interface to the dal package"; 

  register_dal_classes(m);
  register_algorithm_test_bindings(m);
}

} // namespace dunedaq::dal::python
```

### `pybindsrc/dal_classes.cpp`  
*Local path: `repo/dune-dal/pybindsrc/dal_classes.cpp`*

```cpp
/**
 * @file dal_classes.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "dal_pybind_utils.hpp"

#include "dal/BaseApplication.hpp"
#include "dal/Partition.hpp"
#include "dal/ComputerProgram.hpp"
#include "dal/Tag.hpp"
#include "dal/Computer.hpp"
#include "dal/OnlineSegment.hpp"
#include "dal/TemplateSegment.hpp"
#include "dal/TemplateApplication.hpp"
#include "dal/ResourceBase.hpp"
#include "dal/Resource.hpp"
#include "dal/Variable.hpp"
#include "dal/util.hpp"

#include "conffwk/Configuration.hpp"

#include "ers/Issue.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <iostream>
#include <map>
#include <string>
#include <variant>
#include <vector>

namespace py = pybind11;
using namespace dunedaq::conffwk;


namespace dunedaq::dal::python {

  using AppInfo_t = std::variant<std::string, std::vector<std::string>, std::map<std::string, std::string>>;
  using ComputerProgramInfo_t = std::variant<std::vector<std::string>, std::map<std::string, std::string>>;

  struct ObjectLocator {
    
    ObjectLocator(const std::string& id_arg, const std::string& class_name_arg) :
      id(id_arg), class_name(class_name_arg) 
    {}

    const std::string id;
    const std::string class_name;
  };

  class AppConfigHelper {

  public:
    AppConfigHelper(const dunedaq::dal::BaseApplication* app):
      m_app(app)
    {
      check_ptrs( {m_app});
    }

    const std::string& get_app_id() const {
      check_ptrs( { m_app } );
      return m_app->UID();
    }

    ObjectLocator* get_base_app() const {
      check_ptrs( {m_app});
      check_ptrs( {m_app->get_base_app()} );
      return new ObjectLocator(m_app->get_base_app()->UID(), m_app->get_base_app()->class_name());
    }

    ObjectLocator* get_host() const {
      check_ptrs( {m_app});
      check_ptrs( {m_app->get_host()} );
      return new ObjectLocator(m_app->get_host()->UID(), m_app->get_host()->class_name());
    }

    ObjectLocator* get_base_seg() const {
      check_ptrs( {m_app});
      check_ptrs( {m_app->get_segment() });
      check_ptrs( {m_app->get_segment()->get_base_segment() } );
      return new ObjectLocator(m_app->get_segment()->get_base_segment()->UID(), m_app->get_segment()->get_base_segment()->class_name());
    }

    const std::string& get_seg_id() const {
      check_ptrs( {m_app});
      check_ptrs( {m_app->get_segment() });
      return m_app->get_segment()->UID();
    }

    std::vector<ObjectLocator> get_backup_hosts() const {
      std::vector<ObjectLocator> backup_hosts;
      for (const auto& host : m_app->get_backup_hosts()) {
	check_ptrs({host});
	backup_hosts.push_back(ObjectLocator(host->UID(), host->class_name()));
      }
      return backup_hosts;
    }

    bool is_templated() const {
      check_ptrs( {m_app});
      return m_app->is_templated();
    }

    std::unordered_map<std::string, AppInfo_t> get_info() {
      std::unordered_map<std::string, AppInfo_t> app_info_collection;
    
      std::map<std::string, std::string> environment;
      std::vector<std::string> program_names;
      std::string start_args, restart_args;
    
      const dunedaq::dal::Tag * tag = m_app->get_info(environment, program_names, start_args, restart_args);
      check_ptrs({tag});

      app_info_collection["tag"] = tag->UID();
      app_info_collection["environment"] = environment;
      app_info_collection["programNames"] = program_names;
      app_info_collection["startArgs"] = start_args;
      app_info_collection["restartArgs"] = restart_args;
    
      return app_info_collection;
    }

  private:

    const dunedaq::dal::BaseApplication* m_app;
  };

  class SegConfigHelper {

  public:
    SegConfigHelper(const dunedaq::dal::Segment* seg) :
      m_segment(seg) {
    }

    std::string get_seg_id() const { 
      check_ptrs({m_segment});
      return m_segment->UID();
    }

    std::vector<AppConfigHelper> get_all_applications(std::set<std::string>* app_types = nullptr, 
						      std::set<std::string>* use_segments = nullptr, 
						      std::set<const dunedaq::dal::Computer *>* use_hosts = nullptr) const {
      check_ptrs({m_segment});
      return app_translator(m_segment->get_all_applications(app_types, use_segments, use_hosts));
    }

    AppConfigHelper* get_controller() const {
      check_ptrs({m_segment});
      return new AppConfigHelper(m_segment->get_controller());
    }

    std::vector<AppConfigHelper> get_infrastructure() const {
      check_ptrs({m_segment});
      return app_translator(m_segment->get_infrastructure());
    }

    std::vector<AppConfigHelper> get_applications() const {
      check_ptrs({m_segment});
      return app_translator(m_segment->get_applications());
    }

    std::vector<SegConfigHelper> get_nested_segments() const {
      std::vector<SegConfigHelper> nested_segments;

      check_ptrs({m_segment});
      for (const auto& seg : m_segment->get_nested_segments()) {
	nested_segments.emplace_back(SegConfigHelper(seg));
      }
      
      return nested_segments;
    }

    std::vector<ObjectLocator> get_hosts() const {
      std::vector<ObjectLocator> hosts;

      check_ptrs({m_segment});
      for (const auto& host : m_segment->get_hosts()) {
	check_ptrs({host});
	hosts.emplace_back(ObjectLocator(host->UID(), host->class_name()));
      }

      return hosts;
    }

    ObjectLocator* get_base_seg() const {
      check_ptrs({m_segment});
      check_ptrs({m_segment->get_base_segment()});

      return new ObjectLocator(m_segment->get_base_segment()->UID(), m_segment->get_base_segment()->class_name());
    }

    bool is_disabled() const {
      check_ptrs({m_segment});
      return m_segment->is_disabled();
    }

    bool is_templated() const {
      check_ptrs({m_segment});
      return m_segment->is_templated();
    }

    std::unordered_map<std::string, int> get_timeouts() const {
      int action_timeout = -999;
      int shortaction_timeout = -999;
      
      check_ptrs({m_segment});
      m_segment->get_timeouts(action_timeout, shortaction_timeout);

      std::unordered_map<std::string, int> timeouts;
      timeouts["actionTimeout"] = action_timeout;
      timeouts["shortActionTimeout"] = shortaction_timeout;

      return timeouts;
    }

  private:

    static std::vector<AppConfigHelper> app_translator(const std::vector<const dunedaq::dal::BaseApplication *>& apps_in) {
      std::vector<AppConfigHelper> apps_out;

      for (const auto& app : apps_in) {
	apps_out.emplace_back(AppConfigHelper(app));
      }

      return apps_out;
    }
    
    const dunedaq::dal::Segment* m_segment;
  };

    std::vector<AppConfigHelper> 
    partition_get_all_applications(const Configuration& db, 
				   const std::string& partition_name,
				   std::set<std::string> app_types,
				   std::set<std::string> use_segments,
				   std::set<std::string> use_hosts) {
      const dunedaq::dal::Partition* partition = dunedaq::dal::get_partition(const_cast<Configuration&>(db), partition_name);

      check_ptrs({partition});

      std::set<const dunedaq::dal::Computer *> use_hosts_concrete;
      for (const auto& hostname : use_hosts) {
	auto computer_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Computer>(hostname);
	check_ptrs({computer_ptr});
	use_hosts_concrete.insert(computer_ptr);
      }

      std::vector<AppConfigHelper> apps;
      for (const auto& app : partition->get_all_applications(&app_types, &use_segments, &use_hosts_concrete)) {
	apps.emplace_back(AppConfigHelper(app));
      }

      return apps;
    }

  std::vector<std::vector<ObjectLocator>> component_get_parents(const Configuration& db, const std::string& partition_id, const std::string& component_id) {
    const dunedaq::dal::Component* component_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Component>(component_id);
    const dunedaq::dal::Partition* partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id);
    check_ptrs( {component_ptr, partition_ptr});

    std::list<std::vector<const dunedaq::dal::Component*>> parents;
    std::vector<std::vector<ObjectLocator>> parent_ids;

    component_ptr->get_parents(*partition_ptr, parents);

    for (const auto& parent : parents) { 
      std::vector<ObjectLocator> parents_components;
      
      for (const auto& ancestor_component_ptr : parent) { 
	check_ptrs( {ancestor_component_ptr} );
	parents_components.emplace_back( ObjectLocator(ancestor_component_ptr->UID(), 
						       ancestor_component_ptr->class_name()) );
      }
      parent_ids.emplace_back(parents_components);
    }
    
    return parent_ids;
  }

  bool component_disabled(const Configuration& db, const std::string& partition_id, const std::string& component_id) {
    const dunedaq::dal::Component* component_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Component>(component_id);
    const dunedaq::dal::Partition* partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id);

    check_ptrs({component_ptr});
    check_ptrs({partition_ptr});

    return component_ptr->disabled(*partition_ptr);
  }

  std::string partition_get_log_directory(const Configuration& db, const std::string& partition_id) {
    const dunedaq::dal::Partition* partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id);
    check_ptrs( {partition_ptr} );
    return partition_ptr->get_log_directory();
  }

  SegConfigHelper* partition_get_segment(const Configuration& db, const std::string& partition_id, const std::string& seg_name) {
    auto partition_ptr = dunedaq::dal::get_partition(const_cast<Configuration&>(db), partition_id);
    check_ptrs( {partition_ptr} );
    auto segptr = partition_ptr->get_segment(seg_name);
    check_ptrs( {segptr} );
    return new SegConfigHelper(segptr);
  }

  std::string variable_get_value(const Configuration& db, const std::string& variable_id, const std::string& tag_id) {
    const dunedaq::dal::Variable* variable_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Variable>(variable_id);
    check_ptrs( {variable_ptr} );
    const dunedaq::dal::Tag* tag_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Tag>(tag_id);
    check_ptrs( {tag_ptr} );
    return variable_ptr->get_value(tag_ptr);
  }

  std::vector<ComputerProgramInfo_t> computer_program_get_info(const Configuration& db, const std::string& partition_id, const std::string& prog_id, const std::string& tag_id, const std::string& host_id) {

    std::vector<ComputerProgramInfo_t> proginfo_collection;

    std::map<std::string, std::string> environment;
    std::vector<std::string> program_names;

    auto partition_ptr = dunedaq::dal::get_partition(const_cast<Configuration&>(db), partition_id);
    auto prog_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::ComputerProgram>(prog_id);
    auto tag_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Tag>(tag_id);
    auto host_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Computer>(host_id);
    check_ptrs( {partition_ptr, prog_ptr, tag_ptr, host_ptr } );

    prog_ptr->get_info(environment, program_names, *partition_ptr, *tag_ptr, *host_ptr);
		       
    proginfo_collection.emplace_back(environment);
    proginfo_collection.emplace_back(program_names);
    
    return proginfo_collection;
  }


void
register_dal_classes(py::module& m)
{
  py::class_<ObjectLocator>(m, "ObjectLocator")
    .def(py::init<const std::string&, const std::string&>())
    .def_readonly("id", &ObjectLocator::id)
    .def_readonly("class_name", &ObjectLocator::class_name)
    ;

  py::class_<AppConfigHelper>(m, "AppConfigHelper")
    .def(py::init<const dunedaq::dal::BaseApplication*>())
    .def("get_app_id", &AppConfigHelper::get_app_id, "Wrapper for BaseApplication::UID()")
    .def("get_base_app", &AppConfigHelper::get_base_app, "Return identifying info on the BaseApplication")
    .def("get_host", &AppConfigHelper::get_host, "Return identifying info on the host")
    .def("get_base_seg", &AppConfigHelper::get_base_seg, "Return identifying info on the base segment")
    .def("get_seg_id", &AppConfigHelper::get_seg_id, "Return the ID of the segment")
    .def("get_backup_hosts", &AppConfigHelper::get_backup_hosts, "Computers where the application can be restarted in case of problems")
    .def("is_templated", &AppConfigHelper::is_templated, "Is the application templated")
    .def("get_info", &AppConfigHelper::get_info, "Get information required to run the application")
    ;

  py::class_<SegConfigHelper>(m, "SegConfigHelper")
    .def(py::init<const dunedaq::dal::Segment*>())
    .def("get_seg_id", &SegConfigHelper::get_seg_id, "get segment id")
    .def("get_all_applications", &SegConfigHelper::get_all_applications, "Get all applications in the segment")
    .def("get_controller", &SegConfigHelper::get_controller, "Get segment controller")
    .def("get_infrastructure", &SegConfigHelper::get_infrastructure, "Get segment infrastructure applications")
    .def("get_applications", &SegConfigHelper::get_applications, "Get segment applications")
    .def("get_nested_segments", &SegConfigHelper::get_nested_segments, "Get nested segments")
    .def("get_hosts", &SegConfigHelper::get_hosts, "Get hosts for given segment")
    .def("get_base_seg", &SegConfigHelper::get_base_seg, "Get base segment object (i.e. used to create template segment)")
    .def("is_templated", &SegConfigHelper::is_templated, "Return true if this segment is a template segment")
    .def("is_disabled", &SegConfigHelper::is_disabled, "Return true if this segment is disabled")
    .def("get_timeouts", &SegConfigHelper::get_timeouts, "Return run control action timeouts")
    ;

  m.def("partition_get_all_applications", &partition_get_all_applications, "Get list of applications in the requested partition");
  m.def("partition_get_log_directory", partition_get_log_directory);
  m.def("partition_get_segment", partition_get_segment);

  m.def("component_get_parents", &component_get_parents, "Get the Component-derived class instances of the parent(s) of the Component-derived object in question");
  m.def("component_disabled", &component_disabled, "Determine if a Component-derived object (e.g. a Segment) has been disabled");

  m.def("variable_get_value", &variable_get_value, "Get the value stored in an object of class Variable");

  m.def("computer_program_get_info", &computer_program_get_info, "Get details about a computer program");
}


} // namespace dunedaq::dal::python
```

### `pybindsrc/dal_pybind_utils.hpp`  
*Local path: `repo/dune-dal/pybindsrc/dal_pybind_utils.hpp`*

```cpp
#ifndef DAL_PYBINDSRC_DAL_PYBIND_UTILS_HPP_
#define DAL_PYBINDSRC_DAL_PYBIND_UTILS_HPP_

#include "ers/Issue.hpp"

namespace dunedaq {

  ERS_DECLARE_ISSUE(dal, NullPointerReturned, "A null pointer was returned",)

} // namespace dunedaq

namespace {

  void check_ptrs(const std::vector<const void*> ptrs) {
    for (const auto& ptr : ptrs) {
      if (!ptr) {
	throw dunedaq::dal::NullPointerReturned(ERS_HERE);
      }
    }
  }
} // namespace


#endif
```

### `pybindsrc/algorithm_test_bindings.cpp`  
*Local path: `repo/dune-dal/pybindsrc/algorithm_test_bindings.cpp`*

```cpp
/**
 * @file algorithm_test_bindings.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "dal_pybind_utils.hpp"

#include "dal/BaseApplication.hpp"
#include "dal/Partition.hpp"
#include "dal/ComputerProgram.hpp"
#include "dal/Tag.hpp"
#include "dal/Computer.hpp"
#include "dal/OnlineSegment.hpp"
#include "dal/TemplateSegment.hpp"
#include "dal/TemplateApplication.hpp"
#include "dal/ResourceBase.hpp"
#include "dal/Resource.hpp"
#include "dal/Variable.hpp"
#include "dal/util.hpp"

#include "conffwk/Configuration.hpp"

#include "ers/Issue.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <iostream>

namespace py = pybind11;

using namespace dunedaq::conffwk;

namespace {

  std::string print_app(const dunedaq::dal::BaseApplication* app) {
    check_ptrs({app});
    return app->UID() + "@" + app->class_name() + " on " + app->get_host()->UID() + "@" + app->get_host()->class_name();
  }

  std::string print_segment(const dunedaq::dal::Segment* seg)
  {
    check_ptrs({seg});

    std::string out;

    out += std::string("segment: ") + seg->UID() + '\n';

    out += std::string("controller: ") + print_app(seg->get_controller()) + '\n';

    if(!seg->get_infrastructure().empty()) {
      out.append("infrastructure:\n");
      for(const auto& x : seg->get_infrastructure()) {
	out += print_app(x) + '\n';
      }
    } else {
      out.append("no infrastructure\n");
    }

    if(!seg->get_applications().empty()) {
      out.append("applications:\n");
      for(const auto& x : seg->get_applications()) {
	out += print_app(x) + '\n';
      }
    } else {
      out.append("no applications\n");
    }

    if(!seg->get_hosts().empty()) {
      out.append("hosts:\n");
      for(const auto& x : seg->get_hosts()) {
	out += x->UID() + "@" + x->class_name();
      }
    } else {
      out.append("no hosts\n");
    }

    if(!seg->get_nested_segments().empty()) {
      out.append("nested segments:\n");
      for(const auto& x : seg->get_nested_segments()) {
	out += print_segment(x);
      }
    } else {
      out.append("no nested segments\n");
    }

    return out;
  }
  
  std::string print_segment_timeout(const dunedaq::dal::Segment* seg) {
    check_ptrs({seg});

    int action_timeout, shortaction_timeout;

    seg->get_timeouts(action_timeout, shortaction_timeout);

    std::string out = std::string("segment ") + seg->UID() + " actionTimeout: " + std::to_string(action_timeout) + ", shortActionTimeout" + std::to_string(shortaction_timeout) + '\n';

    for(const auto& x : seg->get_nested_segments()) {
        out += print_segment_timeout(x);
    }

    return out;
  }

} // namespace ""

namespace dunedaq::dal::python {

  std::string get_parents_test(const Configuration& db, const::std::string partition_id, const std::string& component_id ) {
    
    const dunedaq::dal::Component* component_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Component>(component_id);
    const dunedaq::dal::Partition* partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id.c_str());

    check_ptrs( {component_ptr, partition_ptr});

    std::list< std::vector<const dunedaq::dal::Component*>> parents;
    component_ptr->get_parents(*partition_ptr, parents);

    std::string line;

    for (const auto& parent: parents) {
      line += "[";
      for (const auto& ancestor_component_ptr : parent) {
	check_ptrs( {ancestor_component_ptr});
	line += "<" + std::string(ancestor_component_ptr->UID()) + "@" + std::string(ancestor_component_ptr->class_name()) + ">";
      }
    }
    
    return line;
  }

  std::string get_log_directory_test(const Configuration& db, const::std::string partition_id) {
    return const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id)->get_log_directory();
  }

  std::string get_segment_test(const Configuration& db, const::std::string partition_id, const std::string& seg_name) {
    auto partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id);
    check_ptrs({partition_ptr});
    
    return print_segment(partition_ptr->get_segment(seg_name));
  }

  std::string get_value_test(const Configuration& db, const std::string& variable_id, const std::string& tag_id) {

    const dunedaq::dal::Variable *variable_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Variable>(variable_id);
    const dunedaq::dal::Tag * tag_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Tag>(tag_id);

    check_ptrs({variable_ptr, tag_ptr});

    return variable_ptr->get_value(tag_ptr);
  }

  bool disabled_test(const Configuration& db, const::std::string partition_id, const std::string& component_id) {
    const dunedaq::dal::Component* component_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Component>(component_id);
    const dunedaq::dal::Partition* partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id);

    check_ptrs({component_ptr});
    check_ptrs({partition_ptr});

    return component_ptr->disabled(*partition_ptr);
  }

  std::string get_timeouts_test(const Configuration& db, const::std::string partition_id, const std::string& segment_id) {
    const dunedaq::dal::Partition* partition_ptr = const_cast<Configuration&>(db).get<dunedaq::dal::Partition>(partition_id);
    check_ptrs({partition_ptr});

    const dunedaq::dal::Segment* segment_ptr = partition_ptr->get_segment(segment_id);
    check_ptrs({segment_ptr});

    return print_segment_timeout(segment_ptr);
  }
  
  
  void
  register_algorithm_test_bindings(py::module& m)
  {
    m.def("get_parents_test", &get_parents_test, "To test against the component_get_parents binding");
    m.def("get_log_directory_test", &get_log_directory_test, "To test against the partition_get_log_directory binding");
    m.def("get_segment_test", &get_segment_test, "To test against the partition_get_segment binding");
    m.def("get_value_test", &get_value_test, "To test against the variable_get_value binding");
    m.def("disabled_test", &disabled_test, "To test against the component_disabled binding");
    m.def("get_timeouts_test", &get_timeouts_test, "To test the SegConfigHelper get_timeouts binding");
  }

} // namespace dunedaq::dal::python
```


## Core algorithms (generated DAL class algorithms)

> `src/algorithms.cpp` contains implementations of the algorithms for the generated DAL classes (attribute `Partition`/`Segment`/`Application`/... methods declared as Methods in `core.schema.xml`), including `is_compatible`, `get_partition`, `get_used_repositories`, `substitute_variables`, `SubstituteVariables::convert`, and the topic-relevant `get_config_version` (reads `TDAQ_DB_VERSION` process environment; see lines 3211-3232) plus `Partition::get_config_version()` and the environment variable `TDAQ_DB_VERSION` propagation (line 82, 802-803, where `Partition::get_DBVersion()` is injected into the application environment). Reproduced in full byte content below.
### `src/algorithms.cpp`  
*Local path: `repo/dune-dal/src/algorithms.cpp`*

```cpp
//
//  FILE: dal/src/algorithms.cpp
//
//  Contains implementations of algorithms for generated DAL classes.
//
//
//  Implementation:
//	<Igor.Soloviev@cern.ch> - May 2003
//

#include <strings.h>
#include <sys/stat.h>

#include <list>
#include <set>
#include <iostream>
#include <sstream>
#include <algorithm>

#include "ers/ers.hpp"
#include "okssystem/Host.hpp"
#include "logging/Logging.hpp"

#include <boost/spirit/include/karma.hpp>

#include "conffwk/ConfigObject.hpp"
#include "conffwk/ConfigAction.hpp"
#include "conffwk/Configuration.hpp"
#include "conffwk/map.hpp"

#include "dal/util.hpp"

#include "dal/BinaryFile.hpp"
#include "dal/Binary.hpp"
#include "dal/Computer.hpp"
#include "dal/ComputerSet.hpp"
#include "dal/InfrastructureApplication.hpp"
#include "dal/InfrastructureTemplateApplication.hpp"
#include "dal/JarFile.hpp"
#include "dal/OnlineSegment.hpp"
#include "dal/Partition.hpp"
#include "dal/PlatformCompatibility.hpp"
#include "dal/Rack.hpp"
#include "dal/Resource.hpp"
#include "dal/ResourceSetAND.hpp"
#include "dal/ResourceSetOR.hpp"
#include "dal/RunControlTemplateApplication.hpp"
#include "dal/RunControlApplication.hpp"
#include "dal/Segment.hpp"
#include "dal/Script.hpp"
#include "dal/SW_ExternalPackage.hpp"
#include "dal/SW_PackageVariable.hpp"
#include "dal/SW_Repository.hpp"
#include "dal/Tag.hpp"
#include "dal/TagMapping.hpp"
#include "dal/TemplateApplication.hpp"
#include "dal/TemplateSegment.hpp"
#include "dal/Variable.hpp"
#include "dal/VariableSet.hpp"

#include "test_circular_dependency.hpp"

using namespace dunedaq::conffwk;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // the strings below are used in various make_path algorithms

const std::string s_share_bin_str("share/bin");
const std::string s_share_lib("share/lib");
const std::string s_bin_str("bin");
const std::string s_lib_str("lib");

const std::string s_rdbconfig_str("rdbconfig");
const std::string s_rdbconfig_colon_str("rdbconfig:");

const std::string s_classpath_str("CLASSPATH");
const std::string s_tdaq_db_str("TDAQ_DB");
const std::string s_tdaq_db_name_str("TDAQ_DB_NAME");
const std::string s_tdaq_db_path_str("TDAQ_DB_PATH");
const std::string s_tdaq_db_data_str("TDAQ_DB_DATA");
const std::string s_tdaq_db_version_str("TDAQ_DB_VERSION");
const std::string s_tdaq_db_repository_str("TDAQ_DB_REPOSITORY");
const std::string s_tdaq_db_user_repository_str("TDAQ_DB_USER_REPOSITORY");
const std::string s_oks_repository_mapping_dir_str("OKS_REPOSITORY_MAPPING_DIR");
const std::string s_tdaq_partition_str("TDAQ_PARTITION");
const std::string s_tdaq_ipc_init_ref_str("TDAQ_IPC_INIT_REF");

const std::string s_tdaq_application_object_id_str("TDAQ_APPLICATION_OBJECT_ID");
const std::string s_tdaq_application_name_str("TDAQ_APPLICATION_NAME");

const std::string s_path_str("PATH");
const std::string s_ld_library_path_str("LD_LIBRARY_PATH");

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

const int search_path_default_size(64);
const int paths_to_shared_libraries_default_size(32);

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

typedef std::map<std::string, std::string> Emap;
typedef std::vector<const dunedaq::dal::Parameter *> EnvironmentVars;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // spirit::karma::generate is faster than sprintf() or std::ostringstream

inline void append2str(std::string& s, unsigned short i)
{
  char buf[8];
  char * ptr(buf);
  boost::spirit::karma::generate(ptr, boost::spirit::ushort_, i);
  s.append(buf, ptr - buf);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // The functions to recursively find first enabled host

static const dunedaq::dal::Computer *
find_enabled(const std::vector<const dunedaq::dal::ComputerBase *>& hosts);

static const dunedaq::dal::Computer *
find_enabled(const dunedaq::dal::ComputerBase * cb)
{
  if (const dunedaq::dal::Computer * c = cb->cast<dunedaq::dal::Computer>())
    {
      if (c->get_State())
        return c;
    }
  else if (const dunedaq::dal::ComputerSet * cs = cb->cast<dunedaq::dal::ComputerSet>())
    {
      for (const auto & i : cs->get_Contains())
        {
          if (const dunedaq::dal::Computer * c = find_enabled(i))
            return c;
        }
    }

  return nullptr;
}

static const dunedaq::dal::Computer *
find_enabled(const std::vector<const dunedaq::dal::ComputerBase *>& hosts)
{
  for (const auto & i : hosts)
    if(const dunedaq::dal::Computer * c = find_enabled(i))
      return c;

  return nullptr;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // The functions to recursively build vector of computers from computer base object(s)

static void
add_computers(std::vector<const dunedaq::dal::Computer *>& v, const dunedaq::dal::ComputerBase * cb)
{
  if (const dunedaq::dal::Computer * cp = cb->cast<dunedaq::dal::Computer>())
    {
      v.push_back(cp);
    }
  else if (const dunedaq::dal::ComputerSet * cs = cb->cast<dunedaq::dal::ComputerSet>())
    {
      for (const auto & i : cs->get_Contains())
        add_computers(v, i);
    }
}

static void
add_computers(std::vector<const dunedaq::dal::Computer *>& v, const std::vector<const dunedaq::dal::ComputerBase *>& hosts)
{
  for (const auto & i : hosts)
    add_computers(v, i);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

const std::string&
dunedaq::dal::Variable::get_value(const Tag * tag) const
{
  if (tag == nullptr)
    {
      if (get_TagValues().size())
        {
          std::ostringstream text;
          text << "the algorithm was invoked on multi-value " << this << " object (file \'" << p_obj.contained_in() << "\') without explicit Tag object";
          throw dunedaq::dal::BadVariableUsage(ERS_HERE, text.str());
        }
    }
  else
    {
      for (const auto& i : get_TagValues())
        if (i->get_HW_Tag() == tag->get_HW_Tag() && i->get_SW_Tag() == tag->get_SW_Tag())
          return i->get_Value();
    }

  return get_Value();
}


  /**
   *  Static function to add single variable to the map.
   *  The variable is added only if it is not in the map.
   */

static void
add_env_var(Emap& dict, const dunedaq::dal::Variable * var, const dunedaq::dal::Tag * tag)
{
  dict.emplace(var->get_Name(), var->get_value(tag));
}


  /**
   *  Static function to add a parameter (variable or set) to the map.
   */

static void
add_env_vars(Emap& dict, const EnvironmentVars& envs, const dunedaq::dal::Tag * tag)
{
  for (const auto & i : envs)
    if (const dunedaq::dal::Variable * var = i->cast<dunedaq::dal::Variable>())
      add_env_var(dict, var, tag);
    else if (const dunedaq::dal::VariableSet * vars = i->cast<dunedaq::dal::VariableSet>())
      add_env_vars(dict, vars->get_Contains(), tag);
}


  /**
   *  Static function to add special variable to the map.
   */

static void
add_env_var(Emap& dict, const std::string& name, const std::string& value)
{
  static const std::string beg_str("$(");
  static const std::string end_str(")");

  std::string s = dunedaq::dal::substitute_variables(value, 0, beg_str, end_str);
  if( s.length() < 2 || s[0] != '$' || s[1] != '(' ) {
    dict[name] = std::move(s);
  }
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  /**
   *  Static functions to combine 2, 3 and 4 strings into a path.
   */

static std::string
make_path(const std::string& s1, const std::string& s2)
{
  std::string s;
  s.reserve(s1.size() + s2.size() + 1);
  s.append(s1);
  s.push_back('/');
  s.append(s2);
  return s;
}

static std::string
make_path(const std::string& s1, const std::string& s2, const std::string& s3)
{
  std::string s;
  s.reserve(s1.size() + s2.size() + s3.size() + 2);
  s.append(s1);
  s.push_back('/');
  s.append(s2);
  s.push_back('/');
  s.append(s3);
  return s;
}

static void
add_search_path(std::vector<std::string>& paths, std::string&& path)
{
  for (const auto& i : paths)
    if (path == i)
      return;

  paths.emplace_back(std::move(path));
}

//
// Static function to recursively go down the SW_Package tree and add to paths
//

struct BinaryInfo
{
  BinaryInfo(const dunedaq::dal::Tag& tag) : m_hw_tag(tag.get_HW_Tag()), m_sw_tag(tag.get_SW_Tag())
  {
    m_bin_path.reserve(32);
    m_lib_path.reserve(32);

    m_bin_path = m_hw_tag;
    m_bin_path.push_back('-');
    m_bin_path.append(m_sw_tag);
    m_bin_path.push_back('/');

    m_lib_path = m_bin_path;

    m_bin_path.append(s_bin_str);
    m_lib_path.append(s_lib_str);
  }

  bool
  is_compatible(const dunedaq::dal::TagMapping* mapping) const
  {
    return (m_hw_tag == mapping->get_HW_Tag() && m_sw_tag == mapping->get_SW_Tag());
  }

  const std::string& m_hw_tag;
  const std::string& m_sw_tag;

  std::string m_bin_path;   // ${hw_tag}-${sw_tag}/bin; assume max len 32
  std::string m_lib_path;   // ${hw_tag}-${sw_tag}/lib; assume max len 32
};

static void
get_paths(
    const dunedaq::dal::SW_Package* package,
    std::vector<std::string>& search_paths,
    std::vector<std::string>& paths_to_shared_libraries,
    const BinaryInfo& binary_info,
    dunedaq::dal::TestCircularDependency& cd_fuse)
{
  if (const dunedaq::dal::SW_Repository * repository = package->cast<dunedaq::dal::SW_Repository>())
    {
      const std::string& patch_area(repository->get_PatchArea());
      const std::string& installation_path(repository->get_InstallationPath());

      if (patch_area.empty())
        {
          TLOG_DEBUG(2) <<  "skip empty \"PatchArea\" of " << repository ;
        }
      else
        {
          add_search_path(search_paths,make_path(patch_area, s_share_bin_str));
          add_search_path(search_paths,make_path(patch_area, binary_info.m_bin_path));
          add_search_path(paths_to_shared_libraries,make_path(patch_area, binary_info.m_lib_path));
        }

      if (installation_path.empty())
        {
          TLOG_DEBUG( 2 ) <<  "skip " << repository << " with empty \"InstallationPath\" attribute" ;
        }
      else
        {
          add_search_path(search_paths, make_path(installation_path, s_share_bin_str));
          add_search_path(search_paths, make_path(installation_path, binary_info.m_bin_path));
          add_search_path(paths_to_shared_libraries, make_path(installation_path, binary_info.m_lib_path));
        }
    }
  else if (const dunedaq::dal::SW_ExternalPackage * epkg = package->cast<dunedaq::dal::SW_ExternalPackage>())
    {
      const std::string& package_patch_area(epkg->get_PatchArea());
      const std::string& package_installation_path(epkg->get_InstallationPath());

      for (const auto& i : epkg->get_Binaries())
        {
          if (binary_info.is_compatible(i))
            {
              if (!package_patch_area.empty())
                add_search_path(search_paths, make_path(package_patch_area, i->get_Value()));

              add_search_path(search_paths, make_path(package_installation_path, i->get_Value()));

              break;
            }
        }

      for (const auto& i : epkg->get_SharedLibraries())
        {
          if (binary_info.is_compatible(i))
            {
              if (!package_patch_area.empty())
                add_search_path(paths_to_shared_libraries, make_path(package_patch_area, i->get_Value()));

              add_search_path(paths_to_shared_libraries, make_path(package_installation_path, i->get_Value()));

              break;
            }
        }
    }
  else
    {
      std::ostringstream text;
      text << "failed to cast " << package << " to " << dunedaq::dal::SW_Repository::s_class_name << " or " << dunedaq::dal::SW_ExternalPackage::s_class_name << " class";
      throw (dunedaq::dal::AlgorithmError(ERS_HERE, text.str()));
    }

  // Loop over all Uses SW_Package and call get_paths on those
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, package);
      for (const auto & i : package->get_Uses())
        get_paths(i, search_paths, paths_to_shared_libraries, binary_info, cd_fuse);
    }
}


//
// Static function to recursively go down the SW_Package tree and check tag
// is available in all the tree
//

static void
check_tag(const dunedaq::dal::SW_Package* package, const dunedaq::dal::Tag& tag, dunedaq::dal::TestCircularDependency& cd_fuse)
// throws (dunedaq::dal::BadTag)
{
  if (const dunedaq::dal::SW_Repository * repository = package->cast<dunedaq::dal::SW_Repository>())
    {
      // Check through the tags to see if there is a match
      for (const auto& i : repository->get_Tags())
        if (i == &tag)
          goto test_used_sw_packages;
    }
  else if (const dunedaq::dal::SW_ExternalPackage * epkg = package->cast<dunedaq::dal::SW_ExternalPackage>())
    {
      // Check through the shared library tag mappings to see if there is a match
      for (const auto& i : epkg->get_SharedLibraries())
        if (i->get_HW_Tag() == tag.get_HW_Tag() && i->get_SW_Tag() == tag.get_SW_Tag())
          goto test_used_sw_packages;

      // Check through the binaries tag mappings to see if there is a match
      for (const auto& i : epkg->get_Binaries())
        if (i->get_HW_Tag() == tag.get_HW_Tag() && i->get_SW_Tag() == tag.get_SW_Tag())
          goto test_used_sw_packages;
    }
  else
    {
      std::ostringstream text;
      text << "failed to cast " << package << " to SW_Repository or SW_ExternalPackage class";
      throw(dunedaq::dal::AlgorithmError(ERS_HERE, text.str()));
    }

  {
    std::ostringstream text;
    text << "the " << package << " does not support this tag";
    throw(dunedaq::dal::BadTag(ERS_HERE, tag.UID(), text.str()));
  }

  // Test tags of used packages
  test_used_sw_packages:
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, package);

      for (const auto& i : package->get_Uses())
        check_tag(i, tag, cd_fuse);
    }
}


/******************************************************************************
************************** ALGORITHM get_parents() ****************************
******************************************************************************/

  /**
   *  Copy a path 'p' to list of paths 'out'.
   */

inline void
add_path(const std::vector<const dunedaq::dal::Component *> & p, std::list<std::vector<const dunedaq::dal::Component *> >& out)
{
  out.push_back(p);
}


  /**
   *  Static function to calculate list of components
   *  from the root segment to the lowest component which
   *  the child object (a segment or a resource) belongs.
   */

static void
make_parents_list(
    const ConfigObjectImpl * child,
    const dunedaq::dal::ResourceSet * resource_set,
    std::vector<const dunedaq::dal::Component *> & p_list,
    std::list< std::vector<const dunedaq::dal::Component *> >& out,
    dunedaq::dal::TestCircularDependency& cd_fuse)
{
  dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, resource_set);

  // add the resource set to the path
  p_list.push_back(resource_set);

  // check if the application is in the resource relationship, i.e. is a resource or belongs to resource set(s)
  for (const auto& i : resource_set->get_Contains())
    {
      if (i->config_object().implementation() == child)
        {
          add_path(p_list, out);
        }
      else if (const dunedaq::dal::ResourceSet * rs = i->cast<dunedaq::dal::ResourceSet>())
        {
          make_parents_list(child, rs, p_list, out, cd_fuse);
        }
    }

  // remove the resource set from the path
  p_list.pop_back();
}


static void
make_parents_list(
    const ConfigObjectImpl * child,
    const dunedaq::dal::Segment * segment,
    std::vector<const dunedaq::dal::Component *> & p_list,
    std::list<std::vector<const dunedaq::dal::Component *> >& out,
    bool is_segment,
    dunedaq::dal::TestCircularDependency& cd_fuse)
{
  dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, segment);

  // add the segment to the path
  p_list.push_back(segment);

  // check if the application is in the nested segment
  for (const auto& i : segment->get_Segments())
    if (i->config_object().implementation() == child)
      add_path(p_list, out);
    else
      make_parents_list(child, i, p_list, out, is_segment, cd_fuse);

  // check if the application is in the resource relationship, i.e. is a resource or belongs to resource set(s)
  if (!is_segment)
    {
      for (const auto& i : segment->get_Resources())
        if (i->config_object().implementation() == child)
          add_path(p_list, out);
        else if (const dunedaq::dal::ResourceSet * resource_set = i->cast<dunedaq::dal::ResourceSet>())
          make_parents_list(child, resource_set, p_list, out, cd_fuse);
    }

  // remove the segment from the path

  p_list.pop_back();
}


static void
check_segment(
    std::list< std::vector<const dunedaq::dal::Component *> >& out,
    const dunedaq::dal::Segment * segment,
    const ConfigObjectImpl * child,
    bool is_segment,
    dunedaq::dal::TestCircularDependency& cd_fuse)
{
  dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, segment);

  std::vector<const dunedaq::dal::Component *> s_list;

  if (segment->config_object().implementation() == child)
    add_path(s_list,out);

  make_parents_list(child, segment, s_list, out, is_segment, cd_fuse);
}


void
dunedaq::dal::Component::get_parents(const dunedaq::dal::Partition& partition, std::list<std::vector<const dunedaq::dal::Component *>>& parents) const
{
  const ConfigObjectImpl * obj_impl = config_object().implementation();

  const bool is_segment = castable(dunedaq::dal::Segment::s_class_name);

  try
    {
      dunedaq::dal::TestCircularDependency cd_fuse("component parents", &partition);

      // check partition's segments
      for (const auto& i : partition.get_Segments())
        check_segment(parents, i, obj_impl, is_segment, cd_fuse);

      // check online-infrastructure segment
      const dunedaq::dal::Segment * s = partition.get_OnlineInfrastructure();
      check_segment(parents, s, obj_impl, is_segment, cd_fuse);

      // check partition's online-infrastructure
      for (const auto &a : partition.get_OnlineInfrastructureApplications())
        if (a->config_object().implementation() == obj_impl)
          {
            parents.emplace_back(1, s);
            break;
          }

      if (parents.empty())
        TLOG_DEBUG(1) <<  "cannot find segment/resource path(s) between Component " << this << " and partition " << &partition << " objects (check this object is linked with the partition as a segment or a resource)" ;
    }
  catch (ers::Issue & ex)
    {
      ers::error(dunedaq::dal::CannotGetParents(ERS_HERE, full_name(), ex));
    }
}


bool
dunedaq::dal::is_compatible(const dunedaq::dal::Tag& tag, const dunedaq::dal::Computer& host, const dunedaq::dal::Partition& partition)
{
  if (tag.get_HW_Tag() == host.get_HW_Tag())
    return true;

  for (const auto& info_obj : partition.get_OnlineInfrastructure()->get_CompatibilityInfo())
    {
      if (host.get_HW_Tag() == info_obj->get_HW_Tag())
        {
          for (const auto& j : info_obj->get_CompatibleWith())
            if (tag.get_HW_Tag() == j->get_HW_Tag())
              return true;

          return false;
        }
    }

  return false;
}


static void
set_path(std::map<std::string, std::string>& environment, const std::string& var, std::vector<std::string>& value)
{
  // create colon-separated string from tokens

  std::string s;

  std::string::size_type len = value.size();

  for (const auto& i : value)
    len += i.size();

  s.reserve(len);

  for (const auto& i : value)
    {
      if (s.empty() == false)
        s.push_back(':');

      s.append(i);
    }

  // concatenate above string and a value in map if exists

  std::string& result(environment[var]);

  if (result.empty())
    {
      result = std::move(s);
    }
  else
    {
      std::string old_val = std::move(result);
      result = std::move(s);
      result.push_back(':');
      result.append(old_val);
    }
}


/***************************************************************************/

// helper functions to recursively get all used sw packages

struct UsedPackages
{
  std::set<const dunedaq::dal::SW_Package*> m_packages_set;
  std::vector<const dunedaq::dal::SW_Package*> m_packages;

  UsedPackages()
  {
    m_packages.reserve(24);
  }

  void
  add(const dunedaq::dal::SW_Package* p)
  {
    if (m_packages_set.insert(p).second == true)
      {
        m_packages.push_back(p);
        add(p->get_Uses());
      }
  }

  void
  add(const std::vector<const dunedaq::dal::SW_Package*>& in)
  {
    for (const auto & i : in)
      add(i);
  }
};

/***************************************************************************/

static const char *
get_env(const char * name)
{
  const char * val = ::getenv(name);
  if (val && !*val)
    return nullptr;
  return val;
}


  // helper functions to get partition environment
  // note, they cannot be combined together since there is an order of environment build
  // and some code is executed between add_front... and add_end_partition_environment()

static const char * s_repository(get_env(s_tdaq_db_repository_str.c_str()));

static void
add_front_partition_environment(std::map<std::string, std::string>& environment, const dunedaq::dal::Partition& partition)
{
  if (s_repository)
    {
      if (const char * s_user_repository = get_env(s_tdaq_db_user_repository_str.c_str()))
        {
          add_env_var(environment, s_tdaq_db_path_str, s_user_repository);
          TLOG_DEBUG(2) <<  "Set " << s_tdaq_db_path_str << "=" << s_user_repository << " and unset " << s_tdaq_db_user_repository_str << " and " << s_tdaq_db_repository_str ;
        }
      else
        {
          static const char * s_mapping_dir(get_env(s_oks_repository_mapping_dir_str.c_str()));

          add_env_var(environment, s_tdaq_db_repository_str, s_repository);
          add_env_var(environment, s_tdaq_db_path_str, "");
          TLOG_DEBUG(2) <<  "Set " << s_tdaq_db_repository_str << '=' << s_repository << " and unset " << s_tdaq_db_path_str ;

          if (s_mapping_dir)
            {
              add_env_var(environment, s_oks_repository_mapping_dir_str, s_mapping_dir);
              TLOG_DEBUG(2) <<  "Set " << s_oks_repository_mapping_dir_str << '=' << s_mapping_dir ;
            }
        }
    }

  add_env_var(environment, s_tdaq_partition_str, partition.UID());

  try
    {
      const std::string& IPCRef = partition.get_IPCRef();
      if (!IPCRef.empty())
        add_env_var(environment, s_tdaq_ipc_init_ref_str, IPCRef);

      if (!s_repository)
        { // is taken only is TDAQ_DB_REPOSITORY is not set
          const std::string& DBPath = partition.get_DBPath();
          if (!DBPath.empty())
            add_env_var(environment, s_tdaq_db_path_str, DBPath);
        }

      const std::string& DBName = partition.get_DBName();
      if (!DBName.empty())
        add_env_var(environment, s_tdaq_db_data_str, DBName);
    }
  catch (dunedaq::conffwk::Generic& ex)
    {
      std::ostringstream text;
      text << "failed to read object " << &partition;
      throw dunedaq::conffwk::Generic(ERS_HERE, text.str().c_str(), ex);
    }
}


static void
extend_env_var(std::map<std::string, std::string>& environment,
               const dunedaq::dal::SW_PackageVariable* var,
               const dunedaq::dal::SW_Package * package,
               std::string&& value)
{
  std::string& val = environment[var->get_Name()];

  if(val.empty())
    {
      val = std::move(value);
    }
  else
    {
      const std::string old_value(std::move(val));
      val = std::move(value);
      val.push_back(':');
      val.append(old_value);
    }

  TLOG_DEBUG(4) <<  "extend environment variable " << var->get_Name() << "=\'" << environment[var->get_Name()] << "\' as defined by object " << var << " linked with " << package ;
}


static void
add_end_partition_environment(std::map<std::string, std::string>& environment,
                              const dunedaq::dal::Partition& partition,
			      const dunedaq::dal::BaseApplication * base_application,
			      const dunedaq::dal::ComputerProgram * computer_program,
                              const dunedaq::dal::Tag * tag)
{
  // Partition needs Environment
  add_env_vars(environment, partition.get_ProcessEnvironment(), tag);

  if (s_repository && environment.find(s_tdaq_db_version_str) == environment.end())
    add_env_var(environment, s_tdaq_db_version_str, partition.get_DBVersion());

  // Add environment defined by the sw packages used by application (if != 0) and the computer program
  {
    UsedPackages used_sw;

    if (base_application)
      used_sw.add(base_application->get_Uses());

    used_sw.add(computer_program->get_BelongsTo()->cast<dunedaq::dal::SW_Package>());
    used_sw.add(computer_program->get_Uses());

    for (const auto &i : used_sw.m_packages)
      add_env_vars(environment, i->get_ProcessEnvironment(), tag);

    for (const auto &j : used_sw.m_packages)
      if (const dunedaq::dal::SW_Repository *sr = j->cast<dunedaq::dal::SW_Repository>())
        {
          const std::string &rn = sr->get_InstallationPathVariableName();
          if (!rn.empty())
            {
              if (environment.emplace(rn, sr->get_InstallationPath()).second == true)
                {
                  TLOG_DEBUG(4) <<  "add environment variable " << rn << "=\'" << sr->get_InstallationPath() << "\' defined by object " << sr ;
                }
              else
                {
                  std::ostringstream text;
                  text << "environment variable " << rn << "=\'" << sr->get_InstallationPath() << "\' defined by object " << sr
                      << " was already defined for it; check configuration database";
                  ers::warning(dunedaq::dal::BadVariableUsage(ERS_HERE, text.str()));
                }
            }
        }

    for (std::vector<const dunedaq::dal::SW_Package*>::const_reverse_iterator j = used_sw.m_packages.rbegin(); j != used_sw.m_packages.rend(); ++j)
      for (const auto &v : (*j)->get_AddProcessEnvironment())
        {
          extend_env_var(environment, v, (*j), make_path((*j)->get_InstallationPath(), v->get_Suffix()));

          // note, new value is prepended, so patch area will have priority
          if (const dunedaq::dal::SW_Repository *r = (*j)->cast<dunedaq::dal::SW_Repository>())
            {
              if (!r->get_PatchArea().empty())
                extend_env_var(environment, v, (*j), make_path(r->get_PatchArea(), v->get_Suffix()));
            }
        }


    // if the program is Java script, generate Java's CLASSPATH
    if (const dunedaq::dal::Script *script = computer_program->cast<dunedaq::dal::Script>())
      if (!strcasecmp("java", script->get_Shell().c_str()))
        {
          TLOG_DEBUG(5) <<  "application " << base_application << " is Java script" ;

          std::string class_path;
          std::map<std::string, std::string>::const_iterator x = environment.find(s_classpath_str);
          if (x != environment.end())
            {
              class_path = x->second;
              TLOG_DEBUG(5) <<  "CLASSPATH defined via environment: " << class_path ;
            }

          const std::string &user_dir(partition.get_RepositoryRoot());

          for (const auto &j : used_sw.m_packages)
            {
              if (const dunedaq::dal::SW_Repository *rep = j->cast<dunedaq::dal::SW_Repository>())
                {
                  add_classpath(*rep, user_dir, class_path);
                }
            }

          TLOG_DEBUG(5) <<  "set final CLASSPATH: " << class_path ;
          environment[s_classpath_str] = class_path;
        }
  }


      // Set TDAQ_DB and TDAQ_DB_NAME if necessary:
      //  - if not defined, set TDAQ_DB variable
      //  - check db technology
      //    set TDAQ_DB_NAME="RDB", if it is not set and the technology is rdbconfig

  auto tdaq_db_var_it = environment.find(s_tdaq_db_str);

  if(partition.get_DBTechnology() == s_rdbconfig_str) {
    auto it = environment.find(s_tdaq_db_name_str);
    if(it != environment.end()) {
      if(tdaq_db_var_it == environment.end()) {
	add_env_var(environment, s_tdaq_db_str, std::string(s_rdbconfig_colon_str) + it->second);
      }
    }
    else {
      add_env_var(environment, s_tdaq_db_name_str, "RDB");
      if(tdaq_db_var_it == environment.end()) {
	add_env_var(environment, s_tdaq_db_str, "rdbconfig:RDB");
      }
    }
  }
  else {
    if(tdaq_db_var_it == environment.end()) {
      add_env_var(environment, s_tdaq_db_str, std::string("oksconflibs:") + partition.get_DBName());
      environment.erase(s_tdaq_db_name_str);
    }
  }
}


#ifndef ERS_NO_DEBUG
static std::string
mk_app_env_string(std::map<std::string, std::string>& environment)
{
  std::string s;
  for(const auto& i : environment) {
    s += i.first + "=\'" + i.second + "\'\n";
  }
  return s;
}
#endif


/******************************************************************************
***************** ALGORITHM ComputerProgram::get_parameters() *****************
******************************************************************************/

static void get_parameters(
  const dunedaq::dal::ComputerProgram * this_cp,
  std::vector<std::string>& program_names,
  std::vector<std::string>& search_paths,
  std::vector<std::string>& paths_to_shared_libraries,
  const dunedaq::dal::Tag& tag,
  const dunedaq::dal::Computer& host,
  const dunedaq::dal::Partition& partition
)
// throw ( BadProgramInfo BadTag)
{
  TLOG_DEBUG(4) << " CALL get_parameters()"
            << "\n  program   = " << this_cp
            << "\n  tag       = " << &tag
            << "\n  host      = " << &host
            << "\n  partition = " << &partition ;

  const dunedaq::dal::SW_Repository * belongs_to = nullptr;
  const bool is_script = (this_cp->class_name() == dunedaq::dal::Script::s_class_name);
  const std::string& repository_root(partition.get_RepositoryRoot());

  // Check ComputerProgram belong to SW_Package
  try
    {
      belongs_to = this_cp->get_BelongsTo();
    }
  catch (dunedaq::conffwk::Exception& ex)
    {
      throw dunedaq::dal::BadProgramInfo(ERS_HERE, this_cp->UID(), "Failed to read SW_Package object", ex);
    }

  // Check the tag is supported by the hardware
  if (!dunedaq::dal::is_compatible(tag, host, partition))
    {
      std::ostringstream text;
      text << "this tag is not applicable on host " << host.UID() << " with hw tag \"" << host.get_HW_Tag() << '\"';
      throw dunedaq::dal::BadTag(ERS_HERE, tag.UID(), text.str());
    }

  // Check that the software repositories support the tag
  // i.e. the BelongsTo and its subtree and the Uses and their subtree
  try
    {
      dunedaq::dal::TestCircularDependency cd_fuse("program tags", this_cp);

      // Check the BelongsTo repository (and its subtree) supports the tag
      check_tag(belongs_to, tag, cd_fuse);

      // Check that the Uses repositories (and their uses subtree) support the tag
      for (const auto& i : this_cp->get_Uses())
        check_tag(i, tag, cd_fuse);
    }
  catch (ers::Issue & ex)
    {
      std::ostringstream text;
      text << this_cp << " is not compatible (running on on host " << &host << ')';
      throw dunedaq::dal::BadTag(ERS_HERE, tag.UID(), text.str(), ex );
    }

  // Find program name (either a script, a binary with no exact implementation or a binary with exact implementation)
  std::string program_name;

  if (is_script)
    {
      // Script
      program_name = this_cp->get_BinaryName();
      TLOG_DEBUG(6) <<  "the Program name is \"" << program_name << "\" (name of script)" ;
      if (program_name.empty())
        throw dunedaq::dal::BadProgramInfo(ERS_HERE, this_cp->UID(), "program has no BinaryName defined (name of script)" );
      }
    else
      {
        const dunedaq::dal::Binary * binary_program = this_cp->cast<dunedaq::dal::Binary>();

        if (binary_program == nullptr)
          throw dunedaq::dal::BadProgramInfo(ERS_HERE, this_cp->UID(), "program is not a ComputerProgram");

        if (binary_program->get_ExactImplementations().empty())
          {
            // Binary with no exact implementation
            program_name = this_cp->get_BinaryName();
            TLOG_DEBUG(6) <<  "the program name is \"" << program_name << "\" (name of binary without exact implementations)" ;
            if (program_name.empty())
              throw dunedaq::dal::BadProgramInfo(ERS_HERE, this_cp->UID(), "program has no BinaryName defined (no exact implementation)" );
          }
        else
          {
            // Binary with exact implementation
            for (const auto& j : binary_program->get_ExactImplementations())
              {
                // Check the Tag matches
                if (j->get_Tag() == &tag)
                  {
                    program_name = j->get_BinaryName();
                    TLOG_DEBUG(6) <<  "the program name is \"" << program_name << "\" name of exact implementation binary file " << j  ;
                    break;
                  }
              }

            if (program_name.empty())
              {
                std::ostringstream text;
                text << "the program " << this_cp << " has no exact implementation for it";
                throw dunedaq::dal::BadTag(ERS_HERE, tag.UID(), text.str() );
              }
          }
      }

  // Make binary tag strings
  BinaryInfo binary_info(tag);

  // Create possible paths to computer program
  if (program_name[0] == '/')
    {
      // Fully qualified path and name
      program_names.emplace_back(program_name);
    }
  else
    {
      const std::string& patch_area(belongs_to->get_PatchArea());
      const std::string& installation_path(belongs_to->get_InstallationPath());

      const std::string& path_suffix(is_script ? s_share_bin_str : binary_info.m_bin_path);

      // Add paths to user-defined repository (Partition RepositoryRoot)
      if (!repository_root.empty())
        program_names.emplace_back(std::move(make_path(repository_root, path_suffix, program_name)));

      // Add paths to PathArea if it is non-empty
      if (!patch_area.empty())
        program_names.emplace_back(std::move(make_path(patch_area, path_suffix, program_name)));

      // Add paths to BelongsTo repository
      program_names.emplace_back(std::move(make_path(installation_path, path_suffix, program_name)));
    }


  // Add search paths and paths to shared libraries to user-defined repository if it is used (i.e. Partition RepositoryRoot)
  // Rotate the vectors to make the Repository Root paths first
  if (!repository_root.empty())
    {
      search_paths.emplace_back(std::move(make_path(repository_root, s_share_bin_str)));
      search_paths.emplace_back(std::move(make_path(repository_root, binary_info.m_bin_path)));
      paths_to_shared_libraries.emplace_back(std::move(make_path(repository_root, binary_info.m_lib_path)));

      if (search_paths.size() > 2)
        std::rotate(search_paths.begin(), search_paths.end() - 2, search_paths.end());

      if (paths_to_shared_libraries.size() > 1)
        std::rotate(paths_to_shared_libraries.begin(), paths_to_shared_libraries.end() - 1, paths_to_shared_libraries.end());
    }

  // Add search paths and paths to shared libraries to used repository
  // and any repositories which they use (recursively)
  try
    {
      dunedaq::dal::TestCircularDependency cd_fuse("program binary and library paths", this_cp);

      for (const auto& i : this_cp->get_Uses())
        get_paths(i, search_paths, paths_to_shared_libraries, binary_info, cd_fuse);

      // Add search paths and paths to shared libraries to repository the program belongs to
      // and any repositories which it uses (recursively)
      get_paths(belongs_to, search_paths, paths_to_shared_libraries, binary_info, cd_fuse);
    }
  catch (ers::Issue & ex)
    {
      throw dunedaq::dal::BadProgramInfo(ERS_HERE, this_cp->UID(), "Failed to get binary and library paths.", ex);
    }
}

/******************************************************************************
 ******************* ALGORITHM ComputerProgram::get_info() ********************
 ******************************************************************************/

void dunedaq::dal::ComputerProgram::get_info(
  std::map<std::string, std::string>& environment,
  std::vector<std::string>& program_names,
  const dunedaq::dal::Partition& partition,
  const dunedaq::dal::Tag& tag,
  const dunedaq::dal::Computer& host
) const
{
  TLOG_DEBUG(4) << " CALL dunedaq::dal::ComputerProgram::get_info()" 
	    << "  \n this      = " << this  
	    << "  \n tag       = " << &tag 
	    << "  \n host      = " << &host
	    << "  \n partition = " << &partition ;


    // Get the program names and the search paths

  std::vector<std::string> search_paths;
  std::vector<std::string> paths_to_shared_libraries;

  search_paths.reserve(search_path_default_size);
  paths_to_shared_libraries.reserve(paths_to_shared_libraries_default_size);

  get_parameters(this, program_names, search_paths, paths_to_shared_libraries, tag, host, partition);


    // Get the environment:
    //  - add environment defined by the partition's attributes (Name, IPCRef, DBPath, DBName, ...)
    //  - add environment defined for the computer program
    //  - add rest of environment defined for the partition

  try {
    add_front_partition_environment(environment, partition); // throw no_subst_parameter

    add_env_vars(environment, get_ProcessEnvironment(), nullptr);

    add_end_partition_environment(environment, partition, nullptr, this, &tag);
  }
  catch ( dunedaq::conffwk::Generic & ex ) {
     throw dunedaq::dal::BadProgramInfo( ERS_HERE, UID(), "failed to build Program environment", ex ) ;
  }

    // add "PATH" and "LD_LIBRARY_PATH" variables

  set_path(environment, s_path_str, search_paths);
  set_path(environment, s_ld_library_path_str, paths_to_shared_libraries);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

static void
get_resourse_apps(
  const dunedaq::dal::ResourceBase * obj,
  std::vector<const dunedaq::dal::BaseApplication *>& out,
  const dunedaq::dal::Partition * p,
  dunedaq::dal::TestCircularDependency& cd_fuse)
{
  if (p == nullptr || obj->disabled(*p, true) == false)
    {
      // test if the resource base can be casted to the application
      if (const dunedaq::dal::BaseApplication * r = obj->cast<dunedaq::dal::BaseApplication>())
        {
          out.push_back(r);
        }

      // test if the resource base can contain nested resources
      if (const dunedaq::dal::ResourceSet * s = obj->cast<dunedaq::dal::ResourceSet>())
        {
          for (const auto& i : s->get_Contains())
            {
              dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
              get_resourse_apps(i, out, p, cd_fuse);
            }
        }
    }
}

static std::vector<const dunedaq::dal::BaseApplication *>
get_resource_applications(const dunedaq::dal::ResourceBase * obj, const dunedaq::dal::Partition * p = nullptr)
{
  dunedaq::dal::TestCircularDependency cd_fuse("resource applications", obj);
  std::vector<const dunedaq::dal::BaseApplication *> out;
  get_resourse_apps(obj, out, p, cd_fuse);
  return out;
}

/******************************************************************************
******************* ALGORITHM Segment::get_timeouts() ***********
******************************************************************************/

void
dunedaq::dal::Segment::get_timeouts(int& actionTimeout, int& shortActionTimeout) const
  //throws (dunedaq::dal::BadSegment)
{
  const dunedaq::dal::Partition * partition = get_seg_config(false)->get_partition();

  actionTimeout = shortActionTimeout = 0;

  for (const auto& a : get_infrastructure())
    if (static_cast<int>(a->get_ExitTimeout()) > shortActionTimeout)
      shortActionTimeout = a->get_ExitTimeout();

  for(const auto& i : get_nested_segments())
    {
      if (i->disabled(*partition) == false)
        {
          for (const auto& it : get_infrastructure())
            {
              if (static_cast<int>(it->get_ExitTimeout()) > shortActionTimeout)
                {
                  shortActionTimeout = it->get_ExitTimeout();
                }
            }

          int tmpLongTime, tmpShortTime;
          i->get_timeouts(tmpLongTime, tmpShortTime);

          if (tmpLongTime > actionTimeout)
            actionTimeout = tmpLongTime;
          if (tmpShortTime > shortActionTimeout)
            shortActionTimeout = tmpShortTime;
        }
    }

  for (const auto& a : get_applications())
    {
      if (const dunedaq::dal::RunControlApplicationBase* rcApp = a->cast<dunedaq::dal::RunControlApplicationBase>())
        {
          if (rcApp->get_ActionTimeout() > actionTimeout)
            actionTimeout = rcApp->get_ActionTimeout();
        }

      if (const dunedaq::dal::BaseApplication* slApp = a->cast<dunedaq::dal::BaseApplication>())
        {
          if (static_cast<int>(slApp->get_ExitTimeout()) > shortActionTimeout)
            shortActionTimeout = slApp->get_ExitTimeout();
        }

    }

  actionTimeout += get_IsControlledBy()->get_ActionTimeout();
  shortActionTimeout += get_IsControlledBy()->cast<dunedaq::dal::BaseApplication>()->get_ExitTimeout();

  TLOG_DEBUG(4) <<  "Segment: " << UID() << ": Action Timeout --> " << actionTimeout << "; Exit Timeout --> " << shortActionTimeout ;

  return;
}

namespace dunedaq::dal {

    class BackupHostFactory
    {
    public:
      BackupHostFactory(const dunedaq::dal::Segment& seg) :
          m_seg(seg), m_num_of_hosts(seg.get_Hosts().size()), m_count(0)
      {
      }

      const dunedaq::dal::Computer *
      get_next()
      {
        size_t idx = m_count++ % m_num_of_hosts;

        if (idx == 0)
          {
            m_count++;
            return m_seg.get_Hosts()[1]->cast<dunedaq::dal::Computer>();
          }

        return m_seg.get_Hosts()[idx]->cast<dunedaq::dal::Computer>();
      }

      size_t
      get_size() const
      {
        return m_num_of_hosts;
      }

    private:
      const dunedaq::dal::Segment& m_seg;
      const size_t m_num_of_hosts;
      size_t m_count;
    };
} // namespace dunedaq::dal




/******************************************************************************
********************** ALGORITHM get_all_applications() ***********************
******************************************************************************/


std::vector<const dunedaq::dal::BaseApplication *>
dunedaq::dal::Partition::get_all_applications(std::set<std::string> * app_types, std::set<std::string> * use_segments, std::set<const dunedaq::dal::Computer *> * use_hosts) const
{
  return get_segment(get_OnlineInfrastructure()->UID())->get_all_applications(app_types, use_segments, use_hosts);
}


void
get_generic_resources(const dunedaq::dal::ResourceBase * obj, ::Configuration& db, std::list<const dunedaq::dal::Resource *>& out, const dunedaq::dal::Partition * p, dunedaq::dal::TestCircularDependency& cd_fuse)
{
  if (p == nullptr || obj->disabled(*p) == false)
    {
      if (const dunedaq::dal::Resource * r = db.cast<dunedaq::dal::Resource>(obj))
        {
          out.push_back(r);
        }
      else if (const dunedaq::dal::ResourceSet * s = db.cast<dunedaq::dal::ResourceSet>(obj))
        {
          for (const auto& i : s->get_Contains())
            {
              dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
              get_generic_resources(i, db, out, p, cd_fuse);
            }
        }
    }
}

void
dunedaq::dal::ResourceBase::get_resources(::Configuration& db, std::list<const Resource *>& out, const dunedaq::dal::Partition * p) const
{
  dunedaq::dal::TestCircularDependency cd_fuse("generic resources", this);
  get_generic_resources(this, db, out, p, cd_fuse);
}


static std::vector<const dunedaq::dal::BaseApplication *>
get_all_referenced(const dunedaq::dal::AppConfig * app, const std::vector<const dunedaq::dal::BaseApplication*>& refs, const std::vector<const dunedaq::dal::BaseApplication *>& all_apps)
{
  std::vector<const dunedaq::dal::BaseApplication *> out;

  for (const auto& x : all_apps)
    {
      const ConfigObjectImpl * app_impl(x->get_base_app()->config_object().implementation());

      for (const auto& a : refs)
        {
          if (a->config_object().implementation() == app_impl)
            {
              if (x->is_templated())
                {
                  if (app->get_segment() == x->get_segment())
                    {
                      if (app->get_is_templated())
                        {
                          if (app->get_host() == x->get_host())
                            {
                              out.push_back(x); // both applications are templated; depend only when hosts and segments are equal
                            }
                        }
                      else
                        {
                          out.push_back(x); // the application is not templated, depend on referenced templated applications from the same segment
                        }
                    }
                }
              else
                {
                  out.push_back(x); // referenced application is normal; depend on it in any case
                }
            }
        }
    }

  return out;
}


namespace dunedaq::dal {
    // This class is a friend of AppConfig and SegConfig
    class AlgorithmUtils
    {

      friend class Partition;

    public:

      static void
      add_applications(dunedaq::dal::Segment& seg, const dunedaq::dal::Rack * rack, const dunedaq::dal::Partition& p, const dunedaq::dal::Computer * default_host);

      static void
      add_segments(dunedaq::dal::Segment& seg, const dunedaq::dal::Partition& p, const std::vector<const dunedaq::dal::Segment*>& objs, const dunedaq::dal::Rack * rack, const dunedaq::dal::Computer * default_host, dunedaq::conffwk::map<std::string>& fuse);

      static void
      get_applications(std::vector<const dunedaq::dal::BaseApplication *>& out, const dunedaq::dal::Segment& seg, std::set<std::string> * app_types, std::set<std::string> * segments, std::set<const dunedaq::dal::Computer *> * hosts);

      static AppConfig *
      reset_app_config(dunedaq::dal::BaseApplication& app);

      static SegConfig *
      reset_seg_config(dunedaq::dal::Segment& seg, const dunedaq::dal::Partition* p);

      static const dunedaq::dal::Partition*
      get_partition(const dunedaq::dal::BaseApplication * app);


    private:

      static void
      add_template_application(const dunedaq::dal::TemplateApplication * a, const char * type, dunedaq::dal::Segment& seg, std::vector<const dunedaq::dal::BaseApplication *>& apps, BackupHostFactory& factory);

      static void
      add_normal_application(const dunedaq::dal::Application * a, dunedaq::dal::Segment& seg, std::vector<const dunedaq::dal::BaseApplication *>& apps);

      static const dunedaq::dal::Computer *
      get_host(const dunedaq::dal::Segment& seg, const dunedaq::dal::BaseApplication * base_app, const dunedaq::dal::Application * app = nullptr);

      static bool
      check_app(const dunedaq::dal::BaseApplication * app, std::set<std::string> * app_types, std::set<std::string> * use_segments, std::set<const dunedaq::dal::Computer *> * use_hosts);

      static void
      check_non_template_segment(const dunedaq::dal::Segment& seg, const dunedaq::dal::BaseApplication * base_app);

      static void
      set_backup_hosts(const std::string& runs_on, std::vector<const dunedaq::dal::Computer *>& template_backup_hosts, BackupHostFactory& factory);

    };
} // namespace dunedaq::dal

const dunedaq::dal::Computer *
dunedaq::dal::AlgorithmUtils::get_host(const dunedaq::dal::Segment& seg, const dunedaq::dal::BaseApplication * base_app, const dunedaq::dal::Application * app)
{
  if (app)
    {
      if (const dunedaq::dal::Computer * h = app->get_RunsOn())
        return h;
    }

  if (!seg.get_hosts().empty())
    return seg.get_hosts().front()->cast<dunedaq::dal::Computer>();

  std::ostringstream text;
  text << "to run " << base_app << " (there is no any defined enabled default host for segment, partition or localhost)";
  throw (dunedaq::dal::NoDefaultHost(ERS_HERE, seg.UID(), text.str()));
}

void
dunedaq::dal::AlgorithmUtils::add_normal_application(const dunedaq::dal::Application * a, dunedaq::dal::Segment& seg, std::vector<const dunedaq::dal::BaseApplication *>& apps)
{
  check_non_template_segment(seg, a);
  dunedaq::dal::BaseApplication * app_obj = const_cast<dunedaq::dal::BaseApplication *>(seg.configuration().get<dunedaq::dal::BaseApplication>(const_cast<ConfigObject&>(a->config_object()), a->UID()));
  dunedaq::dal::AppConfig * app_config = dunedaq::dal::AlgorithmUtils::reset_app_config(*app_obj);
  app_config->m_host = get_host(seg, a, a);
  app_config->m_segment = &seg;
  app_config->m_base_app = a;
  apps.emplace_back(app_obj);
}

void
dunedaq::dal::AlgorithmUtils::add_template_application(const dunedaq::dal::TemplateApplication * a, const char * type, dunedaq::dal::Segment& seg, std::vector<const dunedaq::dal::BaseApplication *>& apps, BackupHostFactory& factory)
{
  const std::vector<const dunedaq::dal::Computer*>& hosts(seg.get_hosts());
  int start_idx(0), end_idx(hosts.size());

  const std::string& runs_on(a->get_RunsOn());
  const bool runs_on_first_host(runs_on == dunedaq::dal::TemplateApplication::RunsOn::FirstHost || runs_on == dunedaq::dal::TemplateApplication::RunsOn::FirstHostWithBackup);

  if (hosts.empty())
    {
      std::ostringstream text;
      text << type << " template application " << a << " may not be run, since segment has no enabled hosts";
      throw dunedaq::dal::CannotCreateSegConfig(ERS_HERE, seg.UID(), text.str());
    }

  if (runs_on == dunedaq::dal::TemplateApplication::RunsOn::AllButFirstHost)
    {
      if (hosts.size() < 2)
        {
          std::ostringstream text;
          text << type << " template application " << a << " may not be run on \"" << dunedaq::dal::TemplateApplication::RunsOn::AllButFirstHost << "\" since segment has " << hosts.size() << " enabled hosts only";
          throw dunedaq::dal::CannotCreateSegConfig(ERS_HERE, seg.UID(), text.str());
        }

      start_idx = 1;
    }
  else if(runs_on_first_host)
    {
      end_idx = 1;
    }

  const uint16_t default_num_of_tapps(a->get_Instances());

  std::string app_id(a->UID());
  app_id.push_back(':');
  app_id.append(seg.UID());
  const std::string::size_type app_id_seg_idx = app_id.length();

  for (int i = start_idx; i < end_idx; ++i)
    {
      const dunedaq::dal::Computer * h = hosts[i];
      const uint16_t num_of_tapps(default_num_of_tapps ? default_num_of_tapps : h->get_NumberOfCores());

      if(!runs_on_first_host)
        {
          app_id.erase(app_id_seg_idx);
          app_id.push_back(':');
          const std::string& host_uid(h->UID());
          app_id.append(host_uid, 0, host_uid.find('.'));
        }

      const std::string::size_type app_id_host_idx = app_id.length();

      for (unsigned short j = 1; j <= num_of_tapps; ++j)
        {
          if(num_of_tapps > 1)
            {
              app_id.erase(app_id_host_idx);
              app_id.push_back(':');
              append2str(app_id, j);
            }

          dunedaq::dal::BaseApplication * app_obj = const_cast<dunedaq::dal::BaseApplication *>(seg.configuration().get<dunedaq::dal::BaseApplication>(const_cast<ConfigObject&>(a->config_object()), app_id));
          dunedaq::dal::AppConfig * app_config = dunedaq::dal::AlgorithmUtils::reset_app_config(*app_obj);
          app_config->m_is_templated = true;
          app_config->m_host = h;
          set_backup_hosts(runs_on, app_config->m_template_backup_hosts, factory);
          app_config->m_segment = &seg;
          app_config->m_base_app = a;
          apps.emplace_back(app_obj);
        }
    }
}

void
dunedaq::dal::AlgorithmUtils::check_non_template_segment(const dunedaq::dal::Segment& seg, const dunedaq::dal::BaseApplication * base_app)
{
  if(seg.p_seg_config->m_is_templated)
    {
      std::ostringstream text;
      text << "the segment contains non-template application " << base_app;
      throw dunedaq::dal::BadTemplateSegmentDescription(ERS_HERE, seg.UID(), text.str());
    }
}

void
dunedaq::dal::AlgorithmUtils::set_backup_hosts(const std::string& runs_on, std::vector<const dunedaq::dal::Computer *>& template_backup_hosts, BackupHostFactory& factory)
{
  if (runs_on == dunedaq::dal::TemplateApplication::RunsOn::FirstHostWithBackup)
    {
      if (factory.get_size() > 1)
        {
          template_backup_hosts.push_back(factory.get_next());

          if (factory.get_size() > 2)
            {
              template_backup_hosts.push_back(factory.get_next());
            }
        }
    }
}


static void
add_enabled_hosts(std::vector<const dunedaq::dal::Computer *>& to, const std::vector<const dunedaq::dal::ComputerBase*>& from, unsigned int default_capacity)
{
  std::vector<const dunedaq::dal::Computer *> hosts;
  hosts.reserve(default_capacity);
  add_computers(hosts, from);

  for (const auto & h : hosts)
    if (h->get_State())
      to.push_back(h);
}

void
dunedaq::dal::AlgorithmUtils::add_applications(dunedaq::dal::Segment& seg, const dunedaq::dal::Rack * rack, const dunedaq::dal::Partition& p, const dunedaq::dal::Computer * default_host)
{
  dunedaq::dal::SegConfig * seg_config = seg.get_seg_config(false);

  // fill hosts of segment

  if(rack == nullptr)
    {
      add_enabled_hosts(seg_config->m_hosts, seg.get_Hosts(), 4);
    }
  else
    {
      add_enabled_hosts(seg_config->m_hosts, rack->get_Nodes(), 40);

      if(seg_config->m_hosts.size() < 2)
        {
          std::ostringstream text;
          text << "number of enabled computers in \'" << rack << "\' is " << seg_config->m_hosts.size() << " (at least two required)";
          throw dunedaq::dal::CannotCreateSegConfig(ERS_HERE, seg.UID(), text.str());
        }
    }

  // if there are no hosts, try to use partition and closest parent segment default host
  if(seg_config->m_hosts.empty() && default_host)
    {
      seg_config->m_hosts.push_back(default_host);
    }

  // check local-host, if there are no hosts
  if(seg_config->m_hosts.empty())
    {
      static std::string local_hostname = OksSystem::LocalHost::full_local_name();

      if (const dunedaq::dal::Computer * host = seg.configuration().get<dunedaq::dal::Computer>(local_hostname))
        {
          if (host->get_State() == true)
            {
              seg_config->m_hosts.push_back(host);
            }
        }
    }


  // backup ....
  BackupHostFactory factory(seg);

  // add controller
    {
      const dunedaq::dal::RunControlApplicationBase * ctrl_obj = seg.get_IsControlledBy();
      dunedaq::dal::BaseApplication * app_obj = nullptr;
      dunedaq::dal::AppConfig * app_config = nullptr;

      if (const dunedaq::dal::RunControlApplication * a = ctrl_obj->cast<dunedaq::dal::RunControlApplication>())
        {
          check_non_template_segment(seg, a);
          app_obj = const_cast<dunedaq::dal::BaseApplication *>(seg.configuration().get<dunedaq::dal::BaseApplication>(const_cast<ConfigObject&>(a->config_object()), a->UID()));
          app_config = dunedaq::dal::AlgorithmUtils::reset_app_config(*app_obj);
          app_config->m_host = get_host(seg, a, a);
        }
      else if (const dunedaq::dal::TemplateApplication * t = ctrl_obj->cast<dunedaq::dal::TemplateApplication>())
        {
          const std::string& t_runs_on(t->get_RunsOn());
          if(t_runs_on != dunedaq::dal::TemplateApplication::RunsOn::FirstHost && t_runs_on != dunedaq::dal::TemplateApplication::RunsOn::FirstHostWithBackup)
            {
              std::ostringstream text;
              text << "controller template application " << t << " may only be run on first host (\"" << t_runs_on << "\" is set instead)";
              throw dunedaq::dal::CannotCreateSegConfig(ERS_HERE, seg.UID(), text.str());
            }

          app_obj = const_cast<dunedaq::dal::BaseApplication *>(seg.configuration().get<dunedaq::dal::BaseApplication>(const_cast<ConfigObject&>(t->config_object()), seg.UID()));
          app_config = dunedaq::dal::AlgorithmUtils::reset_app_config(*app_obj);
          app_config->m_is_templated = true;
          app_config->m_host = get_host(seg, t);
          set_backup_hosts(t_runs_on, app_config->m_template_backup_hosts, factory);
        }

      app_config->m_segment = &seg;
      app_config->m_base_app = ctrl_obj->cast<dunedaq::dal::BaseApplication>();
      seg_config->m_controller = app_obj;
    }

  // add infrastructure
  for (const auto& x : seg.get_Infrastructure())
    {
      if (seg.configuration().cast<dunedaq::dal::Resource>(x) == nullptr)
        {
          if (const dunedaq::dal::InfrastructureApplication * a = x->cast<dunedaq::dal::InfrastructureApplication>())
            {
              add_normal_application(a, seg, seg_config->m_infrastructure);
            }
          else if (const dunedaq::dal::TemplateApplication * t = x->cast<dunedaq::dal::TemplateApplication>())
            {
              add_template_application(t, "infrastructure", seg, seg_config->m_infrastructure, factory);
            }
        }
    }

  // add resources
  for (const auto& x : seg.get_Resources())
    {
      // get enabled resources
      for (const auto& j : get_resource_applications(x, &p))
        {
          if (const dunedaq::dal::Application * a = j->cast<dunedaq::dal::Application>())
            {
              add_normal_application(a, seg, seg_config->m_applications);
            }
          else if (const dunedaq::dal::TemplateApplication * t = j->cast<dunedaq::dal::TemplateApplication>())
            {
              add_template_application(t, "resource", seg, seg_config->m_applications, factory);
            }
        }
    }

  // add applications
  for (const auto& x : seg.get_Applications())
    {
      if (seg.configuration().cast<dunedaq::dal::Resource>(x) == nullptr)
        {
          if (const dunedaq::dal::Application * a = x->cast<dunedaq::dal::Application>())
            {
              add_normal_application(a, seg, seg_config->m_applications);
            }
          else if (const dunedaq::dal::TemplateApplication * t = x->cast<dunedaq::dal::TemplateApplication>())
            {
              add_template_application(t, "normal", seg, seg_config->m_applications, factory);
            }
        }
    }
}


static std::string
seg_config_to_name(const std::string& s)
{
  if (s.empty() == true)
    return std::string("partition");
  else
    return std::string("segment \"") + s + "\"";
}

static void
check_mulpiple_inclusion(dunedaq::conffwk::map<std::string>& fuse, const std::string& id, const std::string& parent)
{
  auto ret = fuse.emplace(id,parent);
  if(ret.second == false)
    {
      throw dunedaq::dal::SegmentIncludedMultipleTimes( ERS_HERE, id, seg_config_to_name((*ret.first).second), seg_config_to_name(parent) );
    }
}

void
dunedaq::dal::AlgorithmUtils::add_segments(
    dunedaq::dal::Segment& seg,
    const dunedaq::dal::Partition& p,
    const std::vector<const dunedaq::dal::Segment*>& objs,
    const dunedaq::dal::Rack * rack,
    const dunedaq::dal::Computer * default_host,
    dunedaq::conffwk::map<std::string>& fuse)
{
  dunedaq::dal::SegConfig * seg_config = seg.get_seg_config(false);

  if(const dunedaq::dal::Computer * c = find_enabled(seg.get_Hosts()))
    default_host = c;

  seg_config->m_is_disabled = seg.disabled(p, true);

  if(seg_config->m_is_disabled == false)
    {
      dunedaq::dal::AlgorithmUtils::add_applications(seg, rack, p, default_host);
    }

  for(const auto& x : objs)
    {
      if(const dunedaq::dal::TemplateSegment * ts = x->cast<TemplateSegment>())
        {
          bool ts_is_disabled = ts->disabled(p, true);

          for(const auto& y : ts->get_Racks())
            {
              std::string id(x->UID());
              id.push_back(':');
              id.append(y->UID());

              bool is_disabled = ts_is_disabled || y->disabled(p, true);

              check_mulpiple_inclusion(fuse, id, seg.p_UID);

              dunedaq::dal::Segment * s = const_cast<dunedaq::dal::Segment *>(p.configuration().get<dunedaq::dal::Segment>(const_cast<ConfigObject&>(ts->config_object()), id));
              dunedaq::dal::SegConfig * nested_seg_config = dunedaq::dal::AlgorithmUtils::reset_seg_config(*s, &p);
              nested_seg_config->m_is_disabled = is_disabled;
              nested_seg_config->m_is_templated = true;
              nested_seg_config->m_base_segment = x;

              seg_config->m_nested_segments.emplace_back(s);

              if(is_disabled == false)
                {
                  add_applications(*s, y, p, default_host);
                }
            }
        }
      else
        {
          check_mulpiple_inclusion(fuse, x->UID(), seg.p_UID);

          dunedaq::dal::Segment * s = const_cast<dunedaq::dal::Segment *>(p.configuration().get<dunedaq::dal::Segment>(const_cast<ConfigObject&>(x->config_object()), x->UID()));
          dunedaq::dal::SegConfig * nested_seg_config = dunedaq::dal::AlgorithmUtils::reset_seg_config(*s, &p);
          nested_seg_config->m_is_templated = false;
          nested_seg_config->m_base_segment = x;

          seg_config->m_nested_segments.emplace_back(s);

          add_segments(*s, p, x->get_Segments(), nullptr, default_host, fuse);
        }
    }
}



/**
 *  Function returns true if application's type is listed by the app_types,
 *  the segment is listed in the use_segments and
 *  the host is listed in use_hosts (if containers are defined)
 */

bool
dunedaq::dal::AlgorithmUtils::check_app(const dunedaq::dal::BaseApplication * app, std::set<std::string> * app_types, std::set<std::string> * use_segments, std::set<const dunedaq::dal::Computer *> * use_hosts)
{
  TLOG_DEBUG( 5) <<
    "check_app(app=" << app->UID() << ", seg=" << app->get_segment() << ", host=" << app->get_host() << "):"
    " app_types=" << (app_types && app_types->find(app->class_name()) == app_types->end()) <<
    " use_segments=" << (use_segments && use_segments->find(app->get_segment()->UID()) == use_segments->end()) <<
    " use_hosts=" << (use_hosts && use_hosts->find(app->get_host()) == use_hosts->end());

  return (
    (
      (app_types && app_types->find(app->class_name()) == app_types->end()) ||
      (use_segments && use_segments->find(app->get_segment()->UID()) == use_segments->end()) ||
      (use_hosts && use_hosts->find(app->get_host()) == use_hosts->end())
    ) ? false : true
  );
}

void
dunedaq::dal::AlgorithmUtils::get_applications(std::vector<const dunedaq::dal::BaseApplication *>& out, const dunedaq::dal::Segment& seg, std::set<std::string> * app_types, std::set<std::string> * segments, std::set<const dunedaq::dal::Computer *> * hosts)
{
  SegConfig * seg_config = seg.get_seg_config(false);

  // return, if segment is disabled
  if (seg_config->is_disabled() == true)
    {
      TLOG_DEBUG( 3) <<  "segment " << seg.UID() << " is disabled"  ;
      return;
    }

  // check controller
    {
      if (check_app(seg_config->m_controller, app_types, segments, hosts))
        {
          out.push_back(seg_config->m_controller);
        }
    }

  // check infrastructure
  for (const auto& x : seg_config->m_infrastructure)
    if (check_app(x, app_types, segments, hosts))
      out.push_back(x);

  // check applications
  for (const auto& x : seg_config->m_applications)
    if (check_app(x, app_types, segments, hosts))
      out.push_back(x);

  // check nested segments
  for (const auto& x : seg_config->m_nested_segments)
    get_applications(out, *x, app_types, segments, hosts);
}

dunedaq::dal::AppConfig *
dunedaq::dal::AlgorithmUtils::reset_app_config(dunedaq::dal::BaseApplication& app)
{
  if (app.p_app_config)
    app.p_app_config->clear();
  else
    app.p_app_config.reset(new AppConfig());

  return app.p_app_config.get();
}

dunedaq::dal::SegConfig *
dunedaq::dal::AlgorithmUtils::reset_seg_config(dunedaq::dal::Segment& seg, const dunedaq::dal::Partition* p)
{
  if (seg.p_seg_config)
    seg.p_seg_config->clear(p);
  else
    seg.p_seg_config.reset(new SegConfig(p));

  return seg.p_seg_config.get();
}

const dunedaq::dal::Partition*
dunedaq::dal::AlgorithmUtils::get_partition(const dunedaq::dal::BaseApplication * app)
{
  return app->get_segment()->get_seg_config(false)->get_partition();
}

const dunedaq::dal::Segment *
dunedaq::dal::Partition::get_segment(const std::string& name) const
{
  if (m_app_config.m_root_segment == nullptr)
    {
      std::lock_guard<std::mutex> scoped_lock(m_app_config.m_root_segment_mutex);

      if (m_app_config.m_root_segment == nullptr)
        {
          const dunedaq::dal::OnlineSegment * onlseg = get_OnlineInfrastructure();

          dunedaq::dal::Segment * root_segment = const_cast<dunedaq::dal::Segment *>(const_cast<Configuration&>(p_db).get<dunedaq::dal::Segment>(const_cast<ConfigObject&>(onlseg->config_object()), onlseg->UID()));

          // reinitialize seg config
          dunedaq::dal::AlgorithmUtils::reset_seg_config(*root_segment, this);

          root_segment->p_seg_config->m_base_segment = root_segment;

          const dunedaq::dal::Computer * default_host = get_DefaultHost();

          if (default_host && default_host->get_State() == false)
            {
              default_host = nullptr;
            }

          dunedaq::conffwk::map<std::string> fuse;
          fuse[root_segment->UID()] = "";

          dunedaq::dal::AlgorithmUtils::add_segments(*root_segment, *this, get_Segments(), nullptr, default_host, fuse);

          for (const auto& a : get_OnlineInfrastructureApplications())
            {
              if (const dunedaq::dal::ResourceBase * r = a->cast<dunedaq::dal::ResourceBase>())
                {
                  if (r->disabled(*this, true) == true)
                    continue;
                }

              std::vector<const dunedaq::dal::BaseApplication *>& apps(a->cast<dunedaq::dal::InfrastructureBase>() ? root_segment->get_seg_config(false)->m_infrastructure : root_segment->get_seg_config(false)->m_applications);
              dunedaq::dal::AlgorithmUtils::add_normal_application(a, *root_segment, apps);
            }

          // check duplicated application IDs

          // FIXME 2022-06-02:
          //   move check to get_all_applications() in next release tdaq-09-05-00
          //   do it once per load/reload modifying ApplicationConfig

          struct Compare {
              bool operator()(const dunedaq::dal::BaseApplication *lhs, const dunedaq::dal::BaseApplication *rhs) const
              { return (lhs->UID() < rhs->UID()); };
          };

          struct ValidateAppID
          {
            std::map<const dunedaq::dal::BaseApplication *, const dunedaq::dal::Segment *, Compare> m_map;

            static std::string
            str(const dunedaq::dal::BaseApplication * x, const dunedaq::dal::Segment * y)
            {
              std::ostringstream s;
              s << '\"' << x << "\" in segment \"" << y->UID() << '\"';
              return s.str();
            }

            void
            check_duplicated(const dunedaq::dal::BaseApplication * a, const dunedaq::dal::Segment * s)
            {
              auto ret = m_map.emplace(a, s);

              if (ret.second == false)
                throw dunedaq::dal::DuplicatedApplicationID( ERS_HERE, ValidateAppID::str(a, s), ValidateAppID::str(ret.first->first, ret.first->second) );
            }

            void
            check_duplicated(const dunedaq::dal::Segment *s)
            {
              SegConfig * seg_config = s->get_seg_config(false);

              if (seg_config->is_disabled() == false)
                {
                  check_duplicated(seg_config->get_controller(), s);

                  // check infrastructure
                  for (const auto &x : seg_config->get_infrastructure())
                    check_duplicated(x, s);

                  // check applications
                  for (const auto &x : seg_config->get_applications())
                    check_duplicated(x, s);

                  // check nested segments
                  for (const auto &x : seg_config->get_nested_segments())
                    check_duplicated(x);
                }
            }
          };

          ValidateAppID test;
          test.check_duplicated(root_segment);

          m_app_config.m_root_segment.store(root_segment);
        }
    }

  const dunedaq::dal::Segment * seg = p_db.find<dunedaq::dal::Segment>(name);

  if(seg == nullptr)
    {
      std::string::size_type idx = name.find(':');

      if (idx != std::string::npos)
        {
          std::string seg_id = name.substr(0, idx);

          seg = p_db.get<Segment>(seg_id);

          if (seg == nullptr)
            {
              std::ostringstream text;
              text << "cannot find template segment object \'" << seg_id << '\'';
              throw dunedaq::dal::CannotFindSegmentByName(ERS_HERE, name, text.str());
            }

          if (const dunedaq::dal::TemplateSegment * ts = seg->cast<TemplateSegment>())
            {
              std::ostringstream text;
              text << "template segment " << ts << " does not have rack \'" << name.substr(idx + 1) << '\'';
              throw dunedaq::dal::CannotFindSegmentByName(ERS_HERE, name, text.str());
            }
          else
            {
              std::ostringstream text;
              text << "object \'" << seg_id << "\' is not template segment";
              throw dunedaq::dal::CannotFindSegmentByName(ERS_HERE, name, text.str());
            }
        }
      else
        {
          throw dunedaq::dal::CannotFindSegmentByName(ERS_HERE, name, "no such non-template segment object");
        }
    }

  return seg;
}

const dunedaq::dal::AppConfig *
dunedaq::dal::BaseApplication::get_app_config(bool no_except) const
{
  const BaseApplication * ptr;

  if(typeid(*this) != typeid(BaseApplication))
    {
      if(p_gen_obj)
        {
          ptr = p_gen_obj;
        }
      else
        {
          ptr = p_db.find<dunedaq::dal::BaseApplication>(UID());

          if(ptr)
            {
              p_gen_obj.store(ptr);
            }
          else
            {
              if (no_except)
                return nullptr;
              else
                throw dunedaq::dal::NotInitedByDalAlgorithm(ERS_HERE, UID(), class_name(), (void*)this, "BaseApplication::get_app_config()");
            }
        }
    }
  else
    {
      ptr = this;
    }

  if(!ptr->p_app_config)
    {
      if (no_except)
        return nullptr;
      else
        throw dunedaq::dal::NotInitedByDalAlgorithm(ERS_HERE, UID(), class_name(), (void*)this, "BaseApplication::get_app_config()");
    }

  return ptr->p_app_config.get();

}

dunedaq::dal::SegConfig *
dunedaq::dal::Segment::get_seg_config(bool check_disabled, bool no_except) const
{
  const Segment * ptr;

  if (typeid(*this) != typeid(Segment))
    {
      if (p_gen_obj)
        {
          ptr = p_gen_obj;
        }
      else
        {
          ptr = p_db.find<dunedaq::dal::Segment>(UID());

          if (ptr)
            {
              p_gen_obj.store(ptr);
            }
          else
            {
              if (no_except)
                return nullptr;
              else
                throw dunedaq::dal::NotInitedByDalAlgorithm(ERS_HERE, UID(), class_name(), (void*)this, "Segment::get_seg_config()");
            }
        }
    }
  else
    {
      ptr = this;
    }

  if (!ptr->p_seg_config)
    {
      if (no_except)
        return nullptr;
      else
        throw dunedaq::dal::NotInitedByDalAlgorithm(ERS_HERE, UID(), class_name(), (void*)this, "Segment::get_seg_config()");
    }

  if (check_disabled && ptr->p_seg_config->is_disabled() && no_except == false)
    {
      throw(dunedaq::dal::SegmentDisabled(ERS_HERE));
    }

  return ptr->p_seg_config.get();

}

const dunedaq::dal::Computer *
dunedaq::dal::BaseApplication::get_host() const
{
  return get_app_config()->get_host();
}

const dunedaq::dal::Segment *
dunedaq::dal::BaseApplication::get_segment() const
{
  return get_app_config()->get_segment();
}

const dunedaq::dal::BaseApplication *
dunedaq::dal::BaseApplication::get_base_app() const
{
  return get_app_config()->get_base_app();
}

bool
dunedaq::dal::BaseApplication::is_templated() const
{
  return get_app_config()->get_is_templated();
}

bool
dunedaq::dal::Segment::is_disabled() const
{
  return get_seg_config(false)->is_disabled();
}

bool
dunedaq::dal::Segment::is_templated() const
{
  return get_seg_config(false)->is_templated();
}

const dunedaq::dal::Segment *
dunedaq::dal::Segment::get_base_segment() const
{
  return get_seg_config(false)->get_base_segment();
}

const dunedaq::dal::BaseApplication *
dunedaq::dal::Segment::get_controller() const
{
  return get_seg_config(true)->get_controller();
}

const std::vector<const dunedaq::dal::BaseApplication *>&
dunedaq::dal::Segment::get_infrastructure() const
{
  return get_seg_config(true)->get_infrastructure();
}

const std::vector<const dunedaq::dal::BaseApplication *>&
dunedaq::dal::Segment::get_applications() const
{
  return get_seg_config(true)->get_applications();
}

const std::vector<const dunedaq::dal::Segment*>&
dunedaq::dal::Segment::get_nested_segments() const
{
  return get_seg_config(false)->get_nested_segments();
}

const std::vector<const dunedaq::dal::Computer*>&
dunedaq::dal::Segment::get_hosts() const
{
  return get_seg_config(false)->get_hosts();
}


std::vector<const dunedaq::dal::BaseApplication *>
dunedaq::dal::BaseApplication::get_initialization_depends_from(const std::vector<const dunedaq::dal::BaseApplication *>& all_apps) const
{
  return get_all_referenced(get_app_config(), get_base_app()->get_InitializationDependsFrom(), all_apps);
}

std::vector<const dunedaq::dal::BaseApplication *>
dunedaq::dal::BaseApplication::get_shutdown_depends_from(const std::vector<const dunedaq::dal::BaseApplication *>& all_apps) const
{
  return get_all_referenced(get_app_config(), get_base_app()->get_ShutdownDependsFrom(), all_apps);
}


std::vector<const dunedaq::dal::BaseApplication *>
dunedaq::dal::Segment::get_all_applications(std::set<std::string> * app_types, std::set<std::string> * segments, std::set<const dunedaq::dal::Computer *> * hosts) const
{
  // get all sub-types
  std::set<std::string> all_app_types;

  if (app_types)
    {
      if (app_types->empty())
        {
          app_types = nullptr;
        }
      else
        {
          const dunedaq::conffwk::fmap<dunedaq::conffwk::fset>& all_scs(configuration().superclasses());

          for (const auto& i : *app_types)
            {
              all_app_types.insert(i);

              for (const auto& j : all_scs)
                {
                  if (j.second.find(&DalFactory::instance().get_known_class_name_ref(i)) != j.second.end())
                    {
                      all_app_types.insert(*j.first);
                    }
                }
            }

          app_types = &all_app_types;
        }
    }

  if (segments && segments->empty())
    segments = nullptr;

  if (hosts && hosts->empty())
    hosts = nullptr;

  std::vector<const dunedaq::dal::BaseApplication *> out;
  dunedaq::dal::AlgorithmUtils::get_applications(out, *this, app_types, segments, hosts);
  return out;
}

static std::vector<const dunedaq::dal::Tag*>
get_some_info(const dunedaq::dal::BaseApplication * this_app, std::list<const dunedaq::dal::Segment *>& s_list)
{
  std::vector<const dunedaq::dal::Tag*> tags;

  const dunedaq::dal::Partition& partition(*dunedaq::dal::AlgorithmUtils::get_partition(this_app));
  const dunedaq::dal::Segment * root_segment(partition.get_OnlineInfrastructure()->cast<dunedaq::dal::Segment>());
  const dunedaq::dal::Computer& host(*this_app->get_host());

  const dunedaq::dal::BaseApplication * base_app = this_app->get_base_app();
  const dunedaq::dal::Segment * segment = this_app->get_segment();

  TLOG_DEBUG( 4) << "  this           = " << this_app->UID() << "\n"
                "  partition      = " << &partition << "\n"
                "  parent segment = " << segment << "\n"
                "  host           = " << &host ;

    {
      TLOG_DEBUG( 4) <<  "Building partition-segment[s] path to the application"  ;

      std::list<std::vector<const dunedaq::dal::Component *>> paths;
      segment->get_parents(partition, paths);

      for (auto& i : paths)
        i.push_back(segment);

      // If still not found then there is a problem
      if (paths.empty())
        {
          throw dunedaq::dal::BadApplicationInfo( ERS_HERE, this_app->UID(), "the application is not in the partition control tree" );
        }
      else if (paths.size() > 1)
        {
          std::ostringstream text;
          text << "there are " << paths.size() << " paths from the partition object " << &partition << ":\n";
          for (const auto& i : paths)
            {
              text << " * path including " << i.size() << " components:\n";
              for (const auto& j : i)
              text << "   - " << j << std::endl;
            }
          throw dunedaq::dal::BadApplicationInfo( ERS_HERE, this_app->UID(), text.str() );
        }

      std::vector<const dunedaq::dal::Component *>& path = paths.front();

      TLOG_DEBUG( 5) <<  "add " << root_segment << " as root segment for application " << this_app->UID() ;
      s_list.push_back(root_segment);

      if (path.size() != 1 || path[0]->UID() != root_segment->UID())
        {
          const std::vector<const dunedaq::dal::Segment*> * segs = &root_segment->get_nested_segments();

          for (const auto& i : path)
            {
              const dunedaq::dal::TemplateSegment * tseg = i->cast<dunedaq::dal::TemplateSegment>();

              if (const dunedaq::dal::Segment * seg = i->cast<dunedaq::dal::Segment>())
                {
                  const ConfigObjectImpl * seg_config_obj_implementation(seg->config_object().implementation());

                  for (const auto & j : *segs)
                    {
                      if (j->get_base_segment()->config_object().implementation() == seg_config_obj_implementation)
                        {
                          if (tseg != nullptr)
                            {
                              if (segment->UID() != j->UID())
                                {
                                  continue;
                                }
                            }

                          s_list.push_back(j);
                          segs = &j->get_nested_segments();
                          break;
                        }

                      if (&j == &segs->back())
                        {
                          std::ostringstream text;
                          text << "cannot find segment " << seg << " as nested child of " << &partition;
                          throw dunedaq::dal::BadApplicationInfo( ERS_HERE, this_app->UID(), text.str() );
                        }
                    }
                }
              else
                {
                  break;
                }
            }
        }
    }

  // If necessary, print out the segment path to application
  if (ers::debug_level() >= 4)
    {
      std::ostringstream text;
      for (std::list<const dunedaq::dal::Segment *>::reverse_iterator i = s_list.rbegin(); i != s_list.rend(); ++i)
        {
          text << " * segment " << (*i)->UID() << std::endl;
        }
      text << " * partition: " << &partition << std::endl;
      TLOG_DEBUG(4) <<  "PATH to application " << this_app->UID() << " is:\n" << text.str() ;
    }

  // Check Application has a Program linked to it and that program is linked to a sw repository
  try
    {
      base_app->get_Program()->get_BelongsTo(); // throw an exception if "Program" or "BelongsTo" is not set
    }
  catch (dunedaq::conffwk::Exception& ex)
    {
      throw dunedaq::dal::BadApplicationInfo( ERS_HERE, this_app->UID(), "failed to read application's Program object", ex );
    }


  // Get the Tags
  //   - get the tag or possible tags (Application ExplicitTag, DefaultTags
  //     from the segment list, Partition DefaultTags)
  //   - eliminate those which are not supported by the hw

  std::vector<const dunedaq::dal::Tag*> tempTags;

  // Get possible tags
  if (base_app->get_ExplicitTag()) {
    // Application ExplicitTag
    tempTags.push_back(base_app->get_ExplicitTag());
  } else {
    // DefaultTags from the segment list
    for (std::list<const dunedaq::dal::Segment *>::reverse_iterator i = s_list.rbegin(); i != s_list.rend(); ++i) {
      if(s_list.size() > 1 && *i == root_segment)
        {
          TLOG_DEBUG(4) <<  "skip default tags of " << root_segment << " for application " << this_app->UID() ;
          continue;
        }

      const auto& default_tags((*i)->get_DefaultTags());
      if (!default_tags.empty()) {
        tempTags.insert(tempTags.end(), default_tags.begin(), default_tags.end());
        TLOG_DEBUG(4) <<  "use default tags of " << *i << " for application " << this_app->UID() ;
        break;
      }
    }

    // Partition DefaultTags
    const auto& default_tags(partition.get_DefaultTags());
    if (!default_tags.empty() && tempTags.empty()) {
      tempTags.insert(tempTags.end(), default_tags.begin(), default_tags.end());
      TLOG_DEBUG(4) <<  "use default tags of " << &partition << " for application " << this_app->UID() ;
    }
  }

  // Report error if there are no possible tags
  if (tempTags.empty())
    throw dunedaq::dal::BadApplicationInfo( ERS_HERE, this_app->UID(), "there are no Tags defined for the application" ) ;

  // Remove tags which are not supported by the hardware
  {
    // Go through all tags and remove tags if not for this hardware
    for (const auto& i : tempTags)
      if (dunedaq::dal::is_compatible(*i, host, partition))
        tags.push_back(i);
      else
        TLOG_DEBUG(6) <<  "* remove tag " << i << " which is incompatible with the HW tag " << host.get_HW_Tag() ;

    // No Tags found to support this hardware
    if (tags.empty())
      {
        std::ostringstream text ;
        text << "application's and/or default tags (";
        for (const auto& i : tempTags)
          {
            if(i != *tempTags.begin()) text << ", ";
            text << i;
          }
        text << ") are not supported by the host " << &host << " (HW tag: \'" << host.get_HW_Tag() << "\')";
        throw dunedaq::dal::BadApplicationInfo( ERS_HERE, this_app->UID(), text.str() ) ;
      }


    // Print list of possible Tags
    if(ers::debug_level() >= 6)
      {
        std::ostringstream text;
        text <<" application's tags for " << this_app->UID() << " are:\n";
        for (const auto& i : tags)
          text << " * tag " << i << "\n";
        TLOG_DEBUG(6) << text.str() ;
      }
  }

  return tags;
}

static std::string
get_host_and_backup_list(const dunedaq::dal::BaseApplication * app)
{
  std::string s(app->get_host()->UID());

  std::vector<const dunedaq::dal::Computer *> backup_hosts = app->get_backup_hosts();

  for (const auto& x : backup_hosts)
    {
      s.push_back(',');
      s.append(x->UID());
    }

  return s;
}

const dunedaq::dal::Tag *
dunedaq::dal::BaseApplication::get_info(std::map<std::string, std::string>& environment, std::vector<std::string>& program_names, std::string & startArgs, std::string & restartArgs) const
{
  const dunedaq::dal::Tag * tag = nullptr;
  const dunedaq::dal::BaseApplication * base_app = get_base_app();
  const dunedaq::dal::ComputerProgram * program = base_app->get_Program();

  const dunedaq::dal::Partition& partition(*dunedaq::dal::AlgorithmUtils::get_partition(this));
  const dunedaq::dal::Computer& host(*get_host());

  std::list<const dunedaq::dal::Segment *> s_list;
  std::vector<const dunedaq::dal::Tag *> tags = get_some_info(this, s_list) ; // throw BadApplicationInfo

  std::vector<std::string> tmp_paths_to_shared_libraries;
  std::vector<std::string> tmp_search_paths;

  tmp_paths_to_shared_libraries.reserve(search_path_default_size);
  tmp_search_paths.reserve(paths_to_shared_libraries_default_size);

  for (unsigned int i = 0 ; i < tags.size(); i++) {
    try {
      get_parameters(program, program_names, tmp_search_paths, tmp_paths_to_shared_libraries, *(tags[i]), host, partition); // throw BadProgramInfo
      tag = tags[i];
      break;
    }
    catch(const dunedaq::dal::BadTag &ex) {
      const int debug_level = 3;
      if(ers::debug_level() >= debug_level) {
        std::ostringstream text;
        text << "cannot use tag " << tags[i];
        ers::debug( dunedaq::dal::BadApplicationInfo(ERS_HERE, UID(), text.str(), ex), debug_level);
      }

      if (i == tags.size()-1) {
        throw dunedaq::dal::BadApplicationInfo(ERS_HERE, UID(), "No program suited for the possible Tags found.", ex);
      }
    }
    catch(dunedaq::dal::BadProgramInfo &ex) {
      throw dunedaq::dal::BadApplicationInfo(ERS_HERE, UID(), "No program suited for the possible Tags found.", ex);
    }
    catch(dunedaq::conffwk::Exception& ex) {
      throw dunedaq::dal::BadApplicationInfo(ERS_HERE, UID(), "Failed to read application's parameters to get possible Tags." , ex);
    }

  }

  std::vector<std::string> search_paths;
  std::vector<std::string> paths_to_shared_libraries;

  search_paths.reserve(search_path_default_size);
  paths_to_shared_libraries.reserve(paths_to_shared_libraries_default_size);

  // Insert in front paths to shared libraries and search paths for the Uses relationship
  // of the Application object (recursively)
  {
    // Make binary tag strings
    BinaryInfo binary_info(*tag);

    // Check if the partition has RepositoryRoot (in this case copy first item from local copy of paths to libs)
    unsigned int idx = (partition.get_RepositoryRoot().empty() ? 0 : 1);
    unsigned int idx2 = idx * 2;
    if(idx == 1) {
      paths_to_shared_libraries.emplace_back(std::move(tmp_paths_to_shared_libraries[0]));
      search_paths.emplace_back(std::move(tmp_search_paths[0]));
      search_paths.emplace_back(std::move(tmp_search_paths[1]));
    }

    // Append paths to shared libraries from application's repositories
    try {
      dunedaq::dal::TestCircularDependency cd_fuse("application binary and library paths", this);
      for (const auto& i : get_Uses()) {
        get_paths(i, search_paths, paths_to_shared_libraries, binary_info, cd_fuse);
      }
    }
    catch(dunedaq::dal::FoundCircularDependency &ex) {
      throw dunedaq::dal::BadApplicationInfo(ERS_HERE, UID(), "Failed to get binary and library paths.", ex);
    }


    // Copy rest of paths to shared libraries from application's repositories
    while(idx < tmp_paths_to_shared_libraries.size()) {
      if(std::find(paths_to_shared_libraries.begin(), paths_to_shared_libraries.end(), tmp_paths_to_shared_libraries[idx]) == paths_to_shared_libraries.end()) {
        paths_to_shared_libraries.emplace_back(std::move(tmp_paths_to_shared_libraries[idx]));
      }
      idx++;
    }

    // Copy rest of search paths from application's repositories
    while(idx2 < tmp_search_paths.size()) {
      if(std::find(search_paths.begin(), search_paths.end(), tmp_search_paths[idx2]) == search_paths.end()) {
        search_paths.emplace_back(std::move(tmp_search_paths[idx2]));
      }
      idx2++;
    }
  }


    // set application's process environment

  environment.clear();

  try
  {
    add_front_partition_environment(environment, partition); // throw
    TLOG_DEBUG( 5) << "calculate " << this << " process environment:\n"
                  "add front " << &partition << " object environment\n"
                  << mk_app_env_string(environment) ;

    // Application needs Environment
    add_env_vars(environment, get_ProcessEnvironment(), tag);
    TLOG_DEBUG( 5) << "calculate " << this << " process environment:\n"
                  "add " << this << " object environment\n"
                  << mk_app_env_string(environment) ;

    // Application's ComputerProgram needs Environment
    add_env_vars(environment, program->get_ProcessEnvironment(), tag);
    TLOG_DEBUG( 5) << "calculate " << this << " process environment:\n"
                  "add " << program << " object environment\n"
                  << mk_app_env_string(environment) ;

    // Segment list NeedsEnvironment
    std::map<std::string,std::string> parent_var_names;
    for (std::list<const dunedaq::dal::Segment *>::reverse_iterator i = s_list.rbegin(); i != s_list.rend(); ++i) {
      add_env_vars(environment, (*i)->get_ProcessEnvironment(), tag);

      for(const auto& j : (*i)->get_infrastructure()) {
        const dunedaq::dal::InfrastructureBase * ia = j->get_base_app()->cast<dunedaq::dal::InfrastructureBase>();
        const std::string& swv_name(ia->get_SegmentProcEnvVarName());
        if(!swv_name.empty()) {
          try {
              // add value of this segment-wide process environment variable
            const std::string value = (
              ia->get_SegmentProcEnvVarValue() == dunedaq::dal::InfrastructureBase::SegmentProcEnvVarValue::AppId ? j->UID() :
              ia->get_SegmentProcEnvVarValue() == dunedaq::dal::InfrastructureBase::SegmentProcEnvVarValue::RunsOn ? j->get_host()->UID() :
              get_host_and_backup_list(j)
            );

            TLOG_DEBUG(6) <<  j->get_base_app() << " adds segment-wide process environment " << swv_name << " => " << value ;
            environment.emplace(swv_name, value);

              // check if one is looking for parent with this name; add and mark if found
            std::map<std::string,std::string>::iterator x = parent_var_names.find(swv_name);
            if(x != parent_var_names.end() && !x->second.empty()) {
              environment.emplace(x->second, value);
              TLOG_DEBUG(6) <<  j->get_base_app() << " adds parent segment-wide process environment " << x->second << " => " << value ;
              x->second = "";
            }

              // add to parent search list
            const std::string& swv_parent_name(ia->get_SegmentProcEnvVarParentName());
            if(!swv_parent_name.empty()) {
              if(parent_var_names.emplace(swv_name,swv_parent_name).second == true) {
                TLOG_DEBUG(6) <<  j->get_base_app() << " requires to add parent segment-wide process environment " << swv_parent_name << " (set for " << swv_name << ')' ;
              }
            }
          }
          catch(ers::Issue& ex) {
            throw dunedaq::dal::BadApplicationInfo( ERS_HERE, UID(), "failed to build Application environment", ex ) ;
          }
        }
      }

      TLOG_DEBUG( 5) << "calculate " << this << " process environment:\n"
                    "add " << *i << " object environment\n"
                    << mk_app_env_string(environment) ;
    }

    add_end_partition_environment(environment, partition, base_app, program, tag);
    TLOG_DEBUG( 5) << "calculate " << base_app << " process environment:\n"
                  "add end " << &partition << " object environment\n"
                  << mk_app_env_string(environment) ;

    // Set Application ID and name variables
    add_env_var(environment, s_tdaq_application_object_id_str, base_app->UID());
    add_env_var(environment, s_tdaq_application_name_str, UID());

    TLOG_DEBUG( 5) << "final " << base_app << " process environment:\n"
                  "add TDAQ_APPLICATION_OBJECT_ID and TDAQ_APPLICATION_NAME variables to environment\n"
               << mk_app_env_string(environment)  ;
  }
  catch  ( dunedaq::conffwk::Generic & ex ) {
    throw dunedaq::dal::BadApplicationInfo( ERS_HERE, UID(), "failed to build Application environment", ex ) ;
  }

    // Add "PATH" and "LD_LIBRARY_PATH" variables

  set_path(environment, s_path_str, search_paths);
  set_path(environment, s_ld_library_path_str, paths_to_shared_libraries);

  // Resolve the command line options
  static const std::string beg_env_str("env(");
  static const std::string end_env_str(")");
  std::string sa = program->get_DefaultParameters();
  sa.push_back(' ');
  std::string rsa = sa;
  sa.append(base_app->get_Parameters());
  rsa.append(base_app->get_RestartParameters());
  startArgs = dunedaq::dal::substitute_variables(sa, &environment, beg_env_str, end_env_str);
  restartArgs = dunedaq::dal::substitute_variables(rsa, &environment, beg_env_str, end_env_str);

  return tag;
}


std::vector<const dunedaq::dal::Computer *>
dunedaq::dal::AppConfig::get_backup_hosts() const
{
  if(const dunedaq::dal::Application * a = m_base_app->cast<dunedaq::dal::Application>())
    {
      std::vector<const dunedaq::dal::Computer *> result;
      add_computers(result, a->get_BackupHosts());
      return result;
    }
  else
    {
      return m_template_backup_hosts;
    }
}

std::vector<const dunedaq::dal::Computer *>
dunedaq::dal::BaseApplication::get_backup_hosts() const
{
  return get_app_config()->get_backup_hosts();
}

dunedaq::dal::ApplicationConfig::ApplicationConfig(::Configuration& db) :
    m_db(db), m_root_segment(nullptr)
{
  TLOG_DEBUG(2) <<  "construct the object " << (void *)this ;
  m_db.add_action(this);
}

dunedaq::dal::ApplicationConfig::~ApplicationConfig()
{
  TLOG_DEBUG(2) <<  "destroy the object " << (void *)this ;
  m_db.remove_action(this);
}

/******************************************************************************
 ******************* ALGORITHM BaseApplication::get_output_error_directory() **
 ******************************************************************************/

std::string
dunedaq::dal::Partition::get_log_directory() const
{
  TLOG_DEBUG(4) <<  " CALL " << this << "::get_log_directory()" ;

  std::string log_path = get_LogRoot();

  if (log_path.empty() == true)
    {
      log_path = "/tmp/logs";
    }

  // Add to this base path the partition name
  log_path += "/" + UID();

  return log_path;
}


// adds Parameters used in segment to the vector
static void
add_parameters( std::vector<const dunedaq::dal::Parameter*>& params, const dunedaq::dal::Segment& segment, dunedaq::dal::TestCircularDependency& cd_fuse )
{
  const std::vector<const dunedaq::dal::Parameter*>& seg_params(segment.get_Parameters());
  params.insert(params.end(), seg_params.begin(), seg_params.end() ) ;

  for(const auto& i : segment.get_Segments())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      add_parameters(params, *i, cd_fuse) ;
    }
}

static void
add_vars(std::map<std::string, std::string>& cvt_map, const std::vector<const dunedaq::dal::Parameter*>& params, dunedaq::dal::TestCircularDependency& cd_fuse)
{
  for (const auto& i : params)
    {
      if (const dunedaq::dal::Variable * var = i->cast<dunedaq::dal::Variable>())
        {
          const std::string& v = var->get_value(); // note, algorithm is used here; it returns empty value for multi-value variable
          cvt_map[var->get_Name()] = v;
          if (v.find('$') != std::string::npos || var->get_Name().find('$') != std::string::npos)
            {
              const_cast<dunedaq::dal::Variable *>(var)->DalObject::unread();
            }
        }
      else if (const dunedaq::dal::VariableSet * vars = i->cast<dunedaq::dal::VariableSet>())
        {
          dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, vars);
          add_vars(cvt_map, vars->get_Contains(), cd_fuse);
        }
    }
}

void
dunedaq::dal::SubstituteVariables::reset(const Partition& p)
{
  m_cvt_map.clear();

  m_cvt_map[s_tdaq_partition_str] = p.UID();                      // insert name-of-partition parameter
  m_cvt_map["TDAQ_LOGS_ROOT"] = p.get_LogRoot();                  // insert partition log root
  m_cvt_map["TDAQ_LOGS_PATH"] = p.get_LogRoot() + "/" + p.UID() ; // insert TDAQ logs path

  try
    {
      dunedaq::dal::TestCircularDependency cd_fuse("segments substitution parameters", &p);
      std::vector<const dunedaq::dal::Parameter*> params = p.get_Parameters();

      if (const dunedaq::dal::Segment* oseg = p.get_OnlineInfrastructure())
        {
          dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, oseg);
          add_parameters(params, *oseg, cd_fuse);
        }

      for (const auto& i : p.get_Segments())
        {
          dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
          add_parameters(params, *i, cd_fuse);
        }

      add_vars(m_cvt_map, params, cd_fuse);

      // get list of used sw repositories and add parameters, referencing their installation
      for (const auto& i : get_used_repositories(p))
        {
          const std::string& rn = i->get_InstallationPathVariableName();
          if (!rn.empty())
            {
              if(m_cvt_map.emplace(rn, i->get_InstallationPath()).second == true)
                {
                  TLOG_DEBUG(4) <<  "add substitute variables conversion map parameter " << rn << "=\'" << i->get_InstallationPath() << "\' defined by object " << *i ;
                }
              else
                {
                  std::ostringstream text;
                  text << "substitute variables conversion map parameter " << rn << "=\'" << i->get_InstallationPath() << "\' defined by object " << *i << " was already defined; check configuration database";
                  ers::warning(dunedaq::dal::BadVariableUsage(ERS_HERE, text.str()));
                }
            }
        }
    }
  catch(ers::Issue& ex)
    {
      throw dunedaq::conffwk::Generic(ERS_HERE, "Failed to substitute parameters from the database", ex);
    }

  // Recursive substitution of the variables before they are used
  static const std::string beg_str("${");
  static const std::string end_str("}");
  std::string subst_s;
  std::map<std::string, std::string>::const_iterator map_iter = m_cvt_map.begin();
  while (map_iter != m_cvt_map.end())
    {
      try
        {
          subst_s = substitute_variables(map_iter->second, &m_cvt_map, beg_str, end_str);
        }
      catch (dunedaq::conffwk::Exception& ex)
        {
          std::ostringstream text;
          text << "Failed to calculate variable \'" << map_iter->first << '\'';
          throw dunedaq::conffwk::Generic(ERS_HERE, text.str().c_str(), ex);
        }

      if (subst_s != map_iter->second)
        {
          m_cvt_map[map_iter->first] = std::move(subst_s);
        }
      map_iter++;
    }

  if (ers::debug_level() >= 3)
    {
      std::ostringstream text;
      text << "Variables substitution map contains " << m_cvt_map.size() << " entries:\n";
      map_iter = m_cvt_map.begin();
      while (map_iter != m_cvt_map.end())
        {
          text << " [" << map_iter->first << "] => " << map_iter->second << std::endl;
          map_iter++;
        }

      TLOG_DEBUG(3) <<  text.str() ;
    }

  // unread all objects, which may appear in template cache

  p.configuration().unread_template_objects();
}

void
dunedaq::dal::SubstituteVariables::convert(std::string& s, const Configuration&, const ConfigObject& o, const std::string& a)
{
  TLOG_DEBUG(5) <<  "convert attribute \'" << a << "\' value \'" << s << "\' of object " << &o ;

  static const std::string beg_str("${");
  static const std::string end_str("}");

  s = substitute_variables(s, &m_cvt_map, beg_str, end_str);

  TLOG_DEBUG(5) <<  "return value \'" << s << '\'' ;
}

std::string
dunedaq::dal::substitute_variables(const std::string& str_from, const std::map<std::string, std::string> * cvs_map, const std::string& beg, const std::string& end)
{
  std::string s(str_from);

  std::string::size_type pos = 0;       // position of tested string index
  std::string::size_type p_start = 0;   // beginning of variable
  std::string::size_type p_end = 0;     // beginning of variable

  int subst_count(1);
  const int max_subst(128);             // max allowed number of substitutions

  while(
   ((p_start = s.find(beg, pos)) != std::string::npos) &&
   ((p_end = s.find(end, p_start + beg.size())) != std::string::npos)
  ) {
    std::string var(s, p_start + beg.size(), p_end - p_start - beg.size());

    if(++subst_count > max_subst) {
      std::ostringstream text;
      text << "Value \'" << str_from << "\' has exceeded the maximum number of substitutions allowed (" << max_subst << "). "
              "It might have a circular dependency with substitution variables. "
              "After " << max_subst << " substitutions it is \'" << s << '\'';
      throw dunedaq::conffwk::Generic(ERS_HERE, text.str().c_str());
    }

    if(cvs_map) {
      std::map<std::string, std::string>::const_iterator j = cvs_map->find(var);
      if(j != cvs_map->end()) {
        s.replace(p_start, p_end - p_start + end.size(), j->second);
      }
    }
    else {
      if(char * env = getenv(var.c_str())) {
        s.replace(p_start, p_end - p_start + end.size(), env);
      }
      else {
        std::ostringstream text;
        text << "substitution failed for parameter \'" << std::string(s, p_start, p_end - p_start + end.size()) << '\'';
        throw dunedaq::conffwk::Generic(ERS_HERE, text.str().c_str());
      }
    }

    pos = p_start + 1;
  }

  return s;
}

////////////////////////////////////////////////////////////////////////////////////

  // class Tokenizer is used for easy parsing of string containing several tokens

namespace dunedaq::dal {
class Tokenizer {

  public:

    Tokenizer(const std::string&, const char *);
    std::string next();

  private:

    std::string p_string;
    const char * p_delimeters;
    std::string::size_type p_idx;

};

Tokenizer::Tokenizer(const std::string& s, const char * d) :
  p_string(s),
  p_delimeters(d),
  p_idx(p_string.find_first_not_of(p_delimeters))
{
}

std::string
Tokenizer::next()
{
  if(p_idx == std::string::npos) return "";
  std::string::size_type end_idx = p_string.find_first_of(p_delimeters, p_idx);
  if(end_idx == std::string::npos) end_idx=p_string.length();
  std::string token = p_string.substr(p_idx, end_idx - p_idx);
  p_idx = p_string.find_first_not_of(p_delimeters, end_idx);
  return token;
}
} // namespace dunedaq::dal

////////////////////////////////////////////////////////////////////////////////////

const dunedaq::dal::Partition *
dunedaq::dal::get_partition(::Configuration& conf, const std::string& pname, unsigned long rlevel, const std::vector<std::string> * rclasses)
{
  static std::set<std::string> s_already_processed_partitions; // keep list of already processed partitions
  static std::mutex s_mutex;

  std::string name = pname;

  if (name.empty())
    {
      s_already_processed_partitions.clear(); // re-set the already processed partitions list to allow re-read referenced objects, when it is needed

      if (const char * s = getenv("TDAQ_PARTITION"))
        {
          name = s;
        }
      else
        {
          ers::error(dunedaq::dal::BadPartitionID(ERS_HERE, name, std::runtime_error("No partition UID provided. What is the UID of the partition you are looking for?")));
          return nullptr;
        }
    }

  // code below can be used for performance measurements

  if (const char * rl = get_env("DAL_GET_PARTITION_REF_LEVEL"))
    {
      rlevel = atoi(rl);
      TLOG_DEBUG(3) <<  " set ref-level parameter = " << rlevel << " (was read from non-empty environment variable \"DAL_GET_PARTITION_REF_LEVEL\")" ;
    }

  // reset reference parameter if the method was called for this partition

  std::ostringstream cname_ss;
  cname_ss << name << '@' << (void *)&conf;
  const std::string cname(cname_ss.str());

  std::lock_guard<std::mutex> scoped_lock(s_mutex);

  if (s_already_processed_partitions.find(cname) != s_already_processed_partitions.end())
    {
      rlevel = 0;
      TLOG_DEBUG(3) <<  " set ref-level parameter = 0 (the method get_partition() has been called already for partition@configuration \'" << cname << "\')" ;
    }
  else
    {
      s_already_processed_partitions.insert(cname);
    }

  std::vector<std::string> dummu;

  if (rlevel)
    {
      if (const char * rn = get_env("DAL_GET_PARTITION_REF_CLASS_NAMES"))
        {
          rclasses = &dummu;
	  dunedaq::dal::Tokenizer t(rn, ",");
          std::string token;
          std::string names;
          while (!(token = t.next()).empty())
            {
              dummu.push_back(token);
              names += token + '\n';
            }
          TLOG_DEBUG(3) <<  " set ref-class-names parameter = " << names << " (was read from non-empty environment variable \"DAL_GET_PARTITION_REF_CLASS_NAMES\")" ;
        }
      else if (getenv("DAL_GET_PARTITION_AVOID_DEF_REF_CLASS_NAMES") == nullptr)
        {
          rclasses = &dummu;
          dummu =
            {
              dunedaq::dal::Partition::s_class_name,        // the partition object
              dunedaq::dal::Tag::s_class_name,              // tags, tags mappings (always needed)
              dunedaq::dal::Segment::s_class_name,          // segments
              dunedaq::dal::ResourceSet::s_class_name,      // resource sets
              dunedaq::dal::Rack::s_class_name,             // racks
              dunedaq::dal::BaseApplication::s_class_name,  // applications
              dunedaq::dal::ComputerBase::s_class_name,     // computers and computer sets
              dunedaq::dal::SW_Package::s_class_name,       // sw repositories, packages
              dunedaq::dal::SW_Object::s_class_name,        // sw objects
              dunedaq::dal::BinaryFile::s_class_name,       // sw object extensions
              dunedaq::dal::Parameter::s_class_name         // parameters for substitution
            };
          TLOG_DEBUG(3) <<  " set default ref-class-names parameter (to get info about applications)" ;
        }
    }

  const dunedaq::dal::Partition * p = conf.get<dunedaq::dal::Partition>(name, false, true, rlevel, rclasses);

  if (!p)
    {
      ers::error(dunedaq::dal::BadPartitionID(ERS_HERE, name));
    }

  return p;
}


////////////////////////////////////////////////////////////////////////////////////


  // add vector of repository objects to the set of repositories

static void
add_repositories(std::set<const dunedaq::dal::SW_Repository *>& repositories, const std::vector<const dunedaq::dal::SW_Package*>& reps, dunedaq::dal::TestCircularDependency& cd_fuse)
{
  for (const auto& i : reps)
    {
      if (const dunedaq::dal::SW_Repository * r = i->cast<dunedaq::dal::SW_Repository>())
        repositories.insert(r);

      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      add_repositories(repositories, i->get_Uses(), cd_fuse);
    }
}


  // process repositories linked with application

static void
process_application(std::set<const dunedaq::dal::SW_Repository *>& repositories, const dunedaq::dal::BaseApplication * a)
{
  if (a)
    {
      try
        {
          dunedaq::dal::TestCircularDependency cd_fuse("used repositories", a);

          // add repositories used by application
          add_repositories(repositories, a->get_Uses(), cd_fuse);

          // add repositories linked with the application's program
          if (const dunedaq::dal::ComputerProgram * p = a->get_Program())
            {
              if (const dunedaq::dal::SW_Repository * r = p->get_BelongsTo())
                repositories.insert(r);

              dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, p);
              add_repositories(repositories, p->get_Uses(), cd_fuse);
            }

        }
      catch (ers::Issue& ex)
        {
          ers::error(dunedaq::dal::BadApplicationInfo(ERS_HERE,a->UID(),"db problem",ex));
        }
    }
}


  // process applications of segment

static void
process_segment(std::set<const dunedaq::dal::SW_Repository *>& repositories, const dunedaq::dal::Segment& s, dunedaq::dal::TestCircularDependency& cd_fuse)
{
  // check segment's controller
  process_application(repositories, s.get_IsControlledBy()->cast<dunedaq::dal::BaseApplication>());

  // check segment's applications, which are not resources
  for (const auto & i : s.get_Applications())
    process_application(repositories, i);

  // check segment's infrastructure applications
  for (const auto& i : s.get_Infrastructure())
    process_application(repositories, i->cast<dunedaq::dal::BaseApplication>());

  // add segment's resource applications
  for (const auto& i : s.get_Resources())
    for (const auto& j : get_resource_applications(i))
      process_application(repositories, j);

  // process applications from nested segments
  for (const auto& i : s.get_Segments())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      process_segment(repositories, *i, cd_fuse);
    }
}

std::set<const dunedaq::dal::SW_Repository *>
dunedaq::dal::get_used_repositories(const dunedaq::dal::Partition& p)
{
  std::set<const dunedaq::dal::SW_Repository *> repositories;

  dunedaq::dal::TestCircularDependency cd_fuse("used segments and repositories", &p);

  if (const dunedaq::dal::OnlineSegment * online_segment = p.get_OnlineInfrastructure())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, online_segment);
      process_segment(repositories, *online_segment, cd_fuse);

      for (const auto &a : p.get_OnlineInfrastructureApplications())
        process_application(repositories, a);
    }

  for (const auto& i : p.get_Segments())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      process_segment(repositories, *i, cd_fuse);
    }

  return repositories;
}

static void
check_file_exists(const std::string& path, std::string & file)
{
  TLOG_DEBUG(6) <<  "try path \'" << path << '\'' ;

  struct stat buffer;
  if (stat(path.c_str(), &buffer) == 0)
    file = path;
}


void
dunedaq::dal::add_classpath(const dunedaq::dal::SW_Repository& rep, const std::string& user_dir, std::string& class_path)
{
  for (const auto& j : rep.get_SW_Objects())
    {
      if (const dunedaq::dal::JarFile *jf = j->cast<dunedaq::dal::JarFile>())
        {
          std::string file;

          const std::string& bn = jf->get_BinaryName();

          // check file name is an absolute path
          if (bn[0] == '/')
            check_file_exists(bn, file);

          // check user dir (Repository Root)
          if (file.empty() && !user_dir.empty())
            check_file_exists(make_path(user_dir, s_share_lib, bn), file);

          // check patch area
          if (file.empty() && !rep.get_PatchArea().empty())
            check_file_exists(make_path(rep.get_PatchArea(), s_share_lib, bn), file);

          if (file.empty())
            check_file_exists(make_path(rep.get_InstallationPath(), s_share_lib, bn), file);

          if (file.empty())
            {
              ers::error(dunedaq::dal::NoJarFile(ERS_HERE, bn, j->UID(), j->class_name(), rep.UID(), rep.class_name()));
            }
          else
            {
              if (!class_path.empty())
                class_path.push_back(':');
              class_path.append(file);
            }
        }
    }
}

/******************************************************************************
********** ALGORITHMS get_config_version() and get_config_version() ***********
******************************************************************************/

static std::string cv_info_name("RunParams.ConfigVersion");


std::string
dunedaq::dal::get_config_version(const std::string& /*partition*/)
{
  
  if(const char * env = getenv(s_tdaq_db_version_str.c_str()))
    return env;

  throw dunedaq::conffwk::Generic(ERS_HERE, ("The environment variable \"" + s_tdaq_db_version_str + "\" needs to be defined").c_str());
}

std::string
dunedaq::dal::Partition::get_config_version()
{
  return ::dunedaq::dal::get_config_version(UID());
}
```

### `src/disabled-components.cpp`  
*Local path: `repo/dune-dal/src/disabled-components.cpp`*

```cpp
#include "dal/Application.hpp"
#include "dal/Partition.hpp"
#include "dal/ResourceSet.hpp"
#include "dal/ResourceSetAND.hpp"
#include "dal/ResourceSetOR.hpp"
#include "dal/Segment.hpp"
#include "dal/TemplateApplication.hpp"
#include "dal/OnlineSegment.hpp"
#include "dal/util.hpp"
#include "dal/disabled-components.hpp"

#include "logging/Logging.hpp"

#include "test_circular_dependency.hpp"

using namespace dunedaq::conffwk;

dunedaq::dal::DisabledComponents::DisabledComponents(Configuration& db) :
  m_db(db),
  m_num_of_slr_enabled_resources(0),
  m_num_of_slr_disabled_resources(0)
{
  TLOG_DEBUG(2) <<  "construct the object " << (void *)this  ;
  m_db.add_action(this);
}

dunedaq::dal::DisabledComponents::~DisabledComponents()
{
  TLOG_DEBUG(2) <<  "destroy the object " << (void *)this ;
  m_db.remove_action(this);
}

void
dunedaq::dal::DisabledComponents::notify(std::vector<ConfigurationChange *>& /*changes*/) noexcept
{
  TLOG_DEBUG(2) <<  "reset partition components because of notification callback on object " << (void *)this ;
  __clear();
}

void
dunedaq::dal::DisabledComponents::load() noexcept
{
  TLOG_DEBUG(2) <<  "reset partition components because of configuration load on object " << (void *)this ;
  __clear();
}

void
dunedaq::dal::DisabledComponents::unload() noexcept
{
  TLOG_DEBUG(2) <<  "reset partition components because of configuration unload on object " << (void *)this ;
  __clear();
}

void
dunedaq::dal::DisabledComponents::update(const ConfigObject& obj, const std::string& name) noexcept
{
  TLOG_DEBUG(2) <<  "reset partition components because of configuration update (obj = " << obj << ", name = \'" << name << "\') on object " << (void *)this ;
  __clear();
}

void
dunedaq::dal::DisabledComponents::reset() noexcept
{
  TLOG_DEBUG(2) <<  "reset disabled by explicit user call" ;
  m_disabled.clear(); // do not clear s_user_disabled && s_user_enabled !!!
}

bool
dunedaq::dal::DisabledComponents::is_enabled(const dunedaq::dal::Component * c)
{
  if (const dunedaq::dal::Segment * seg = c->cast<dunedaq::dal::Segment>())
    {
      if (dunedaq::dal::SegConfig * conf = seg->get_seg_config(false, true))
        {
          return !conf->is_disabled();
        }
    }
  else if (const dunedaq::dal::BaseApplication * app = c->cast<dunedaq::dal::BaseApplication>())
    {
      if (const dunedaq::dal::AppConfig * conf = app->get_app_config(true))
        {
          const dunedaq::dal::BaseApplication * base = conf->get_base_app();
          if (base != app && is_enabled_short(base->cast<dunedaq::dal::Component>()) == false)
            return false;
        }
    }

  return is_enabled_short(c);
}


void
dunedaq::dal::Partition::set_disabled(const std::set<const dunedaq::dal::Component *>& objs) const
{
  m_disabled_components.m_user_disabled.clear();

  for (const auto& i : objs)
      m_disabled_components.m_user_disabled.insert(i);

  m_disabled_components.m_num_of_slr_disabled_resources = m_disabled_components.m_user_disabled.size();

  m_disabled_components.reset();

  m_app_config.__clear();
}

void
dunedaq::dal::Partition::set_enabled(const std::set<const dunedaq::dal::Component *>& objs) const
{
  m_disabled_components.m_user_enabled.clear();

  for (const auto& i : objs)
    m_disabled_components.m_user_enabled.insert(i);

  m_disabled_components.m_num_of_slr_enabled_resources = m_disabled_components.m_user_enabled.size();

  m_disabled_components.reset();

  m_app_config.__clear();
}

void
dunedaq::dal::DisabledComponents::disable_children(const dunedaq::dal::ResourceSet& rs)
{
  for (auto & i : rs.get_Contains())
    {
      // FIXME 2022-04-22: implement efficient castable() method working with pointers
      //if (i->castable(&dunedaq::dal::TemplateApplication::s_class_name) == false)
      if (i->cast<dunedaq::dal::TemplateApplication>() == nullptr)
        {
          TLOG_DEBUG(6) <<  "disable resource " << i << " because it's parent resource-set " << &rs << " is disabled" ;
          disable(*i);
        }
      else
        {
          TLOG_DEBUG(6) <<  "do not disable template resource application " << i << " (it's parent resource-set " << &rs << " is disabled)" ;
        }

      if (const dunedaq::dal::ResourceSet * rs2 = i->cast<dunedaq::dal::ResourceSet>())
        {
          disable_children(*rs2);
        }
    }
}

void
dunedaq::dal::DisabledComponents::disable_children(const dunedaq::dal::Segment& s)
{
  for (auto & i : s.get_Resources())
    {
      // FIXME 2022-04-22: implement efficient castable() method working with pointers
      //if (i->castable(&dunedaq::dal::TemplateApplication::s_class_name) == false)
      if (i->cast<dunedaq::dal::TemplateApplication>() == nullptr)
        {
          TLOG_DEBUG(6) <<  "disable resource " << i << " because it's parent segment " << &s << " is disabled" ;
          disable(*i);
        }
      else
        {
          TLOG_DEBUG(6) <<  "do not disable template resource application " << i << " (it's parent segment " << &s << " is disabled)" ;
        }

      if (const dunedaq::dal::ResourceSet * rs = i->cast<dunedaq::dal::ResourceSet>())
        {
          disable_children(*rs);
        }
    }

  for (auto & j : s.get_Segments())
    {
      TLOG_DEBUG(6) <<  "disable segment " << j << " because it's parent segment " << &s << " is disabled" ;
      disable(*j);
      disable_children(*j);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace dunedaq {
  ERS_DECLARE_ISSUE_BASE(
    dal,
    ReadMaxAllowedIterations,
    AlgorithmError,
    "Has exceeded the maximum of iterations allowed (" << limit << ") during calculation of disabled objects",
    ,
    ((unsigned int)limit)
  )
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // fill data from resource sets

static void fill(
  const dunedaq::dal::ResourceSet& rs,
  std::vector<const dunedaq::dal::ResourceSetOR *>& rs_or,
  std::vector<const dunedaq::dal::ResourceSetAND *>& rs_and,
  dunedaq::dal::TestCircularDependency& cd_fuse
)
{
  if (const dunedaq::dal::ResourceSetAND * r1 = rs.cast<dunedaq::dal::ResourceSetAND>())
    {
      rs_and.push_back(r1);
    }
  else if (const dunedaq::dal::ResourceSetOR * r2 = rs.cast<dunedaq::dal::ResourceSetOR>())
    {
      rs_or.push_back(r2);
    }

  for (auto & i : rs.get_Contains())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      if (const dunedaq::dal::ResourceSet * rs2 = i->cast<dunedaq::dal::ResourceSet>())
        {
          fill(*rs2, rs_or, rs_and, cd_fuse);
        }
    }
}


  // fill data from segments

static void fill(
  const dunedaq::dal::Segment& s,
  std::vector<const dunedaq::dal::ResourceSetOR *>& rs_or,
  std::vector<const dunedaq::dal::ResourceSetAND *>& rs_and,
  dunedaq::dal::TestCircularDependency& cd_fuse
)
{
  for (auto & i : s.get_Resources())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      if (const dunedaq::dal::ResourceSet * rs = i->cast<dunedaq::dal::ResourceSet>())
        {
          fill(*rs, rs_or, rs_and, cd_fuse);
        }
    }

  for (auto & j : s.get_Segments())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, j);
      fill(*j, rs_or, rs_and, cd_fuse);
    }
}


  // fill data from partition

static void fill(
  const dunedaq::dal::Partition& p,
  std::vector<const dunedaq::dal::ResourceSetOR *>& rs_or,
  std::vector<const dunedaq::dal::ResourceSetAND *>& rs_and,
  dunedaq::dal::TestCircularDependency& cd_fuse
)
{
  if (const dunedaq::dal::OnlineSegment * onlseg = p.get_OnlineInfrastructure())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, onlseg);
      fill(*onlseg, rs_or, rs_and, cd_fuse);

      // NOTE: normally application may not be ResourceSet, but for some "exotic" cases put this code
      for (auto &a : p.get_OnlineInfrastructureApplications())
        {
          if (const dunedaq::dal::ResourceSet * rs = a->cast<dunedaq::dal::ResourceSet>())
            {
              fill(*rs, rs_or, rs_and, cd_fuse);
            }
        }
    }

  for (auto & i : p.get_Segments())
    {
      dunedaq::dal::AddTestOnCircularDependency add_fuse_test(cd_fuse, i);
      fill(*i, rs_or, rs_and, cd_fuse);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

bool
dunedaq::dal::Component::disabled(const dunedaq::dal::Partition& partition, bool skip_check) const
{
  // fill disabled (e.g. after partition changes)

  if (partition.m_disabled_components.size() == 0)
    {
      if (partition.get_Disabled().empty() && partition.m_disabled_components.m_user_disabled.empty())
        {
          return false;  // the partition has no disabled components
        }
      else
        {
          // get two lists of all partition's resource-set-or and resource-set-and
          // also test any circular dependencies between segments and resource sets
          dunedaq::dal::TestCircularDependency cd_fuse("component \'is-disabled\' status", &partition);
          std::vector<const dunedaq::dal::ResourceSetOR *> rs_or;
          std::vector<const dunedaq::dal::ResourceSetAND *> rs_and;
          fill(partition, rs_or, rs_and, cd_fuse);

          // calculate explicitly and implicitly (nested) disabled components
            {
              std::vector<const dunedaq::dal::Component *> vector_of_disabled;
              vector_of_disabled.reserve(partition.get_Disabled().size() + partition.m_disabled_components.m_user_disabled.size());

              // add user disabled components, if any
              for (auto & i : partition.m_disabled_components.m_user_disabled)
                {
                  vector_of_disabled.push_back(i);
                  TLOG_DEBUG(6) <<  "disable component " << i << " because it is explicitly disabled by user" ;
                }

              // add partition-disabled components ignoring explicitly enabled by user
              for (auto & i : partition.get_Disabled())
                {
                  TLOG_DEBUG(6) <<  "check component " << i << " explicitly disabled in partition" ;

                  if (partition.m_disabled_components.m_user_enabled.find(i) == partition.m_disabled_components.m_user_enabled.end())
                    {
                      vector_of_disabled.push_back(i);
                      TLOG_DEBUG(6) <<  "disable component " << i << " because it is explicitly disabled in partition" ;
                    }
                  else
                    {
                      TLOG_DEBUG(6) <<  "skip component " << i << " because it is enabled by user" ;
                    }
                }

              // fill set of explicitly and implicitly (segment/resource-set containers) disabled components
              for (auto & i : vector_of_disabled)
                {
                  partition.m_disabled_components.disable(*i);

                  if (const dunedaq::dal::ResourceSet * rs = i->cast<dunedaq::dal::ResourceSet>())
                    {
                      partition.m_disabled_components.disable_children(*rs);
                    }
                  else if (const dunedaq::dal::Segment * seg = i->cast<dunedaq::dal::Segment>())
                    {
                      partition.m_disabled_components.disable_children(*seg);
                    }
                }
            }

          for (unsigned long count = 1; true; ++count)
            {
              const unsigned long num(partition.m_disabled_components.size());

              TLOG_DEBUG(6) <<  "before auto-disabling iteration " << count << " the number of disabled components is " << num ;

              for (const auto& i : rs_or)
                {
                  if (partition.m_disabled_components.is_enabled_short(i))
                    {
                      // check ANY child is disabled
                      for (auto & i2 : i->get_Contains())
                        {
                          if (!partition.m_disabled_components.is_enabled_short(i2))
                            {
                              TLOG_DEBUG(6) <<  "disable resource-set-OR " << i << " because it's child " << i2 << " is disabled" ;
                              partition.m_disabled_components.disable(*i);
                              partition.m_disabled_components.disable_children(*i);
                              break;
                            }
                        }
                    }
                }

              for (const auto& j : rs_and)
                {
                  if (partition.m_disabled_components.is_enabled_short(j))
                    {
                      const std::vector<const dunedaq::dal::ResourceBase*> &resources = j->get_Contains();

                      if (!resources.empty())
                        {
                          // check ANY child is enabled
                          bool found_enabled = false;
                          for (auto & j2 : resources)
                            {
                              if (partition.m_disabled_components.is_enabled_short(j2))
                                {
                                  found_enabled = true;
                                  break;
                                }
                            }
                          if (found_enabled == false)
                            {
                              TLOG_DEBUG(6) <<  "disable resource-set-AND " << j << " because all it's children are disabled" ;
                              partition.m_disabled_components.disable(*j);
                              partition.m_disabled_components.disable_children(*j);
                            }
                        }
                    }
                }

              if (partition.m_disabled_components.size() == num)
                {
                  TLOG_DEBUG(6) <<  "after " << count << " iteration(s) auto-disabling algorithm found no newly disabled sets, exiting loop ..." ;
                  break;
                }

              unsigned int iLimit(1000);

              if (count > iLimit)
                {
                  ers::error(dunedaq::dal::ReadMaxAllowedIterations(ERS_HERE, iLimit));
                  break;
                }
            }
        }
    }

  bool result(skip_check ? !partition.m_disabled_components.is_enabled_short(this) : !partition.m_disabled_components.is_enabled(this));
  TLOG_DEBUG( 6) <<  "disabled(" << this << ") returns " << std::boolalpha << result  ;
  return result;
}

unsigned long
dunedaq::dal::DisabledComponents::get_num_of_slr_resources(const dunedaq::dal::Partition& p)
{
  return (p.m_disabled_components.m_num_of_slr_enabled_resources + p.m_disabled_components.m_num_of_slr_disabled_resources);
}
```

### `src/test_circular_dependency.cpp`  
*Local path: `repo/dune-dal/src/test_circular_dependency.cpp`*

```cpp
#include "conffwk/DalObject.hpp"

#include "test_circular_dependency.hpp"

void
dunedaq::dal::TestCircularDependency::push(const dunedaq::conffwk::DalObject * object)
{
  if(p_index < p_limit) {
    p_objects[p_index++] = object;
  }
  else {
    std::ostringstream s;
    for(unsigned int i = 0; i < p_index; ++i) {
      if(i != 0) s << ", ";
      s << p_objects[i];
    }

    throw dunedaq::dal::FoundCircularDependency(ERS_HERE, p_limit, p_goal, s.str());
  }
}
```

### `src/test_circular_dependency.hpp`  
*Local path: `repo/dune-dal/src/test_circular_dependency.hpp`*

```cpp
#ifndef _daq_core_test_circular_dependency_H_
#define _daq_core_test_circular_dependency_H_


#include "dal/util.hpp"

namespace dunedaq {
  namespace conffwk {
    class DalObject;
  }
}

namespace dunedaq::dal {

    class TestCircularDependency {

      friend class AddTestOnCircularDependency;

      public:

        TestCircularDependency(const char * goal, const dunedaq::conffwk::DalObject * first_object) :
            p_goal(goal), p_index(0)
        {
          p_objects[p_index++] = first_object;
        }


      private:

        /// \throw dunedaq::dal::FoundCircularDependency
        void push(const dunedaq::conffwk::DalObject * object);

        void
        pop()
        {
          p_index--;
        }

          /// maximum recursion level
        enum {
	  p_limit = 64
	};

        const char * p_goal;
        unsigned int p_index;
        const dunedaq::conffwk::DalObject * p_objects[p_limit];

    };

    class AddTestOnCircularDependency {

      public:

        AddTestOnCircularDependency(TestCircularDependency& fuse, const dunedaq::conffwk::DalObject * obj) : p_fuse(fuse) { p_fuse.push(obj); }
        ~AddTestOnCircularDependency() { p_fuse.pop(); }


      private:

        TestCircularDependency& p_fuse;
    };
} // dunedaq::dal


#endif
```


## Build configuration

### `CMakeLists.txt`  
*Local path: `repo/dune-dal/CMakeLists.txt`*

```cmake
cmake_minimum_required(VERSION 3.12)
project(dal VERSION 1.0.0)

find_package(daq-cmake REQUIRED)

daq_setup_environment()

find_package(okssystem REQUIRED)
find_package(oksdalgen REQUIRED)
find_package(ers REQUIRED)
find_package(logging REQUIRED)
find_package(conffwk REQUIRED)


daq_oks_codegen(core.schema.xml)

daq_add_library(algorithms.cpp disabled-components.cpp test_circular_dependency.cpp LINK_LIBRARIES conffwk::conffwk okssystem::okssystem logging::logging)

daq_add_python_bindings(*.cpp LINK_LIBRARIES dal)

daq_add_application(dal_print_hosts dal_print_hosts.cxx                               LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_test_rw dal_test_rw.cxx                                  LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_test_timeouts dal_test_timeouts.cxx                      LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_dump_apps dal_dump_apps.cxx                              LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_dump_apps_mt dal_dump_apps_mt.cxx                        LINK_LIBRARIES dal conffwk::conffwk Boost::program_options pthread)
daq_add_application(dal_dump_app_config dal_dump_app_config.cxx                 LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_dump_app_depends dal_dump_app_depends.cxx                LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_print_segments dal_print_segments.cxx                    LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_get_app_env dal_get_app_env.cxx                               LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_test_disabled dal_test_disabled.cxx                      LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)
daq_add_application(dal_test_get_config dal_test_get_config.cxx                  LINK_LIBRARIES dal conffwk::conffwk Boost::program_options)

daq_install()
```

### `cmake/dalConfig.cmake.in`  
*Local path: `repo/dune-dal/cmake/dalConfig.cmake.in`*

```cmake

@PACKAGE_INIT@

include(CMakeFindDependencyMacro)


find_dependency(okssystem)
find_dependency(ers)
find_dependency(logging)
find_dependency(conffwk)

# Figure out whether or not this dependency is an installed package or
# in repo form

if (EXISTS ${CMAKE_SOURCE_DIR}/@PROJECT_NAME@)

message(STATUS "Project \"@PROJECT_NAME@\" will be treated as repo (found in ${CMAKE_SOURCE_DIR}/@PROJECT_NAME@)")
add_library(@PROJECT_NAME@::@PROJECT_NAME@ ALIAS @PROJECT_NAME@)

get_filename_component(@PROJECT_NAME@_DAQSHARE "${CMAKE_CURRENT_LIST_FILE}" DIRECTORY)

else()

message(STATUS "Project \"@PROJECT_NAME@\" will be treated as installed package (found in ${CMAKE_CURRENT_LIST_DIR})")
set_and_check(targets_file ${CMAKE_CURRENT_LIST_DIR}/@PROJECT_NAME@Targets.cmake)
include(${targets_file})

set(@PROJECT_NAME@_DAQSHARE "${CMAKE_CURRENT_LIST_DIR}/../../../share")

endif()

check_required_components(@PROJECT_NAME@)
```

### `LICENSE`  
*Local path: `repo/dune-dal/LICENSE`*

```text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

### `NOTICE`  
*Local path: `repo/dune-dal/NOTICE`*

```text

This repo's code has been copied from the ATLAS TDAQ package of the
same name (under the tdaq-9-05-00 release) and been refactored for the
DUNE DAQ. Original ATLAS TDAQ licensing info (Apache License 2.0) can
be found below this line. Note that while this license does not
necessarily apply to the refactored parts of the code, it does apply
to the unmodified parts.

======================================================================

Copyright (C) 2001-2020 CERN for the benefit of the ATLAS collaboration.
Licensed under the Apache License, version 2.0.

Contributors
============
 Igor Soloviev <Igor.Soloviev@cern.ch>
 Giovanna Lehmann Miotto <Giovanna.Lehmann@cern.ch>
 Marc Dobson <Marc.Dobson@cern.ch>
 Andrei Kazarov <Andrei.Kazarov@cern.ch>
 Giuseppe Avolio <Giuseppe.Avolio@cern.ch>
 Bahar Aydemir <bahar.aydemir@cern.ch>
 Andy Salnikov <salnikov@slac.stanford.edu>
 Andre Dos Anjos <andre.dos.anjos@gmail.com>
```


