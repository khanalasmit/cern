# Source 3: CERN GitLab OKS repositories (oks, oks_utils, swrod, oks2coral)

> Generated 2026-08-08 by automated extraction renderer (`output/build_03.py`).
> All code blocks are full byte-content of the named files from the local clones (or HTML-to-text conversion where noted).


## Provenance

The four repositories are the canonical ATLAS TDAQ OKS sources at CERN, cloned 2026-08-08 (git, depth 1):

| Repo | GitLab URL | Branch | HEAD commit | HEAD date |
|------|------------|--------|-------------|-----------|
| oks | https://gitlab.cern.ch/atlas-tdaq-software/oks | master | `bba5d25a6f4626b3a2bce4888cbc5bbff32da48c` | 2026-07-09 |
| oks_utils | https://gitlab.cern.ch/atlas-tdaq-software/oks_utils | master | `1761b535afc894f3f72c1595a53bdc7514b5ddbe` | 2025-08-18 |
| swrod | https://gitlab.cern.ch/atlas-tdaq-software/swrod | master | `f8a52efac6abd594209b2090eff807b11eb34574` | 2026-08-04 |
| oks2coral | https://gitlab.cern.ch/atlas-tdaq-software/oks2coral | master | `be046277b4fa16db855d14b463bce028905fd06f` | 2021-03-02 |

**Release-tag timeline of the `oks` repo (full list, 267 tags, extracted from `git ls-remote --tags`):**
- Oldest OKS-era tags: `oks-02-07-02`, `oks-02-07-03`, `oks-02-08-04`, `oks-02-08-05`, then `oks-03-00-00` ... `oks-08-04-00` (the series documented in `doc/RELEASE_NOTES.md`; DUNE forked from `oks-08-03-04`, 2022-04-14).
- TDAQ-era tags: `tdaq-01-04-00_patch_02` ... `tdaq-01-09-01_patches_02`, `online-00-18-00`.
- The complete sorted list is preserved in `output/extracts/cern-oks-tags.txt`.

## 1. `oks` — core OKS library (GitLab)

This is the current ATLAS TDAQ `oks` package (the DUNE fork is based on its `oks-08-03-04` tag). Files below are embedded in full: README, the complete release notes (documenting the GIT-integration history relevant to section G), the query grammar implementation (`oks/query.h` + `src/query.cpp`), the GIT repository utilities in `bin/` (built as `oks_clone_repository`, `oks_dump`, `oks_git_repository`, `oks_validate_repository`), the git-wrapper shell scripts `scripts/oks-*.sh`, and the test files.
### `README.md`  
*Local path: `repo/oks/README.md`*

```markdown
The OKS (Object Kernel Support) is a library to support a simple active persistent in-memory object manager. It is suitable for applications which need to create persistent structured information with fast access but do not require full database functionality. 

OKS is based on an object model that supports objects, classes, associations, methods, data abstraction, inheritance, polymorphism, object identifiers, composite objects, integrity constraints, schema evolution, data migration and active notification. OKS stores the class definitions and their instances in XML files (which can be used across different platforms). It provides query facilities. The OKS has C++ API and includes Motif based GUI applications to design class schema and to manipulate objects.

### Authors

Igor Soloviev

### Origin

The OKS was designed at the Information Technology (IT) Department of Petersburg Nuclear Physics Institute (PNPI) Russian Academy of Science in 1996.

### More information

[Release Notes](https://gitlab.cern.ch/atlas-tdaq-software/oks/-/blob/master/doc/RELEASE_NOTES.md)

[TWiki](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltOks)
```

### `doc/RELEASE_NOTES.md`  
*Local path: `repo/oks/doc/RELEASE_NOTES.md`*

```markdown
# OKS

## tdaq-13-01-00

### Improve get repository versions

* add support for Git date formats like concrete date "2026-06-15", or a relative date such as "2 years 1 day 3 minutes ago"
* add support for Git branches

### Improve creation of new files

* if TDAQ_DB_REPOSITORY is defined, new files are created in Git repository working area, otherwise in current working directory
* create sub-directories for new files if they do not exist
* add `OksKernel::import_file(to, from)` method to add external file into working area, where `to` should be a repository filename, e.g. `test/my.schema.xml`

## tdaq-12-00-00

### Add update data function

* new function keeps xml document layout and user comments unchanged only updating what has been changed
* contrary, the save-data function rewrites xml data file completely removing user comments and saves data using standard layout
* the update-data is integrated into OKS data editor in addition to previous save-data

## tdaq-11-02-00

* use `tbb::scalable_allocator` allocator instead of `boost::fast_pool_allocator`
* add debug info (`.git/oks_proc_info`) when clone oks repository
* use `flock` on `/var/tmp` before entering `oks-commit.sh` pull/push section to avoid issue when a user runs multiple commits on the same node
* add `ordered` flag into oks relationship constructor to be used by rdb's `oks copy`

## tdaq-10-00-00

* set `pull.rebase=true` when clone oks repository to avoid misleading merge commits by users

## tdaq-09-03-00

### Show hidden oks data xml attributes for text editors

Use new oks_refresh utility with -x option to enforce all attributes to be shown.

### Deprecated OWL date/time format

The OWL date/time formats are deprecated and will be removed in next public release. ERS warning is reported by oks library, when a file containing data stored in deprecated format is loaded.
Such file can be refreshed using oks editors or new **oks_refresh** utility. For example:
```
$ git clone <url> .
$ TDAQ_DB_PATH=`pwd`:$TDAQ_DB_PATH oks_refresh -f ./<file>
$ git commit -m "refresh <file> to update date/time format" ./<file>
$ git push origin master
```

### Ordering of multi-value attributes and relationships

Use new **ordered** attribute for multi-value attribute or relationship to sort its data on save. The default value is **no**.
Implement sort of multi-value attributes and relationships in OKS data editor.


## tdaq-09-02-01

### Postponed changes

The postponed changes are stored into a git branch and should not be applied immediately in the ongoing data taking session. If needed, they can be shared with other experts and tested using DAQ control and configuration tools. At an appropriate moment the branch will be merged with master branch and deleted.

When branch is created, the gitea pull request (also known as [merge request](https://docs.gitlab.com/ee/user/project/merge_requests/) in gitlab) can be created. All gitea pull requests can be accessed from a single point and applied using gitea web interface. In future, the pull requests will be integrated with DAQ Shifter Assistant.

A git branch can be created and updated using git, oks and gitea web interfaces.

#### Create and update branch

Create or checkout a branch into temporary private area:
```
$ cd `oks_clone_repository -b <branch-name>`
```

A branch can also be created using git command line and gitea web interfaces.

#### Modify oks files

Edit changes using config tools, a text editor or gitea web interface, for example:
```
$ export TDAQ_DB_USER_REPOSITORY=`pwd`
$ oks_data_editor x/y/z
$ vim x/y/z
```

#### Commit and push modifications

Use oks commit:
```
$ oks-commit.sh -m 'put here your commit message' -u `pwd`
```
or git command line interface:
```
$ git commit -m 'put here your commit message' x/y/z
$ git push origin <branch-name>
```

#### Edit branch script

The oks edit branch utility allows to create new or checkout existing git branch, modify and commit changes into it. It performs steps similar to described in three above sections.
Run:
```
oks-edit-branch.sh -h
```
to get more information about command line parameters and required process environment settings.

#### Create gitea pull request (recommended)

Create a new pull request for your branch using gitea Web interface (you need to be authorised first) using URL:
```
<gitea-release-url>/compare/master...<branch-name>
```

#### Merge postponed changes
When the changes have to be merged with the master branch, use git command line interface:
```
$ git checkout master
$ git merge <branch-name>
$ git push origin master
$ git push origin --delete <branch-name>
$ git branch -D <branch-name>
```
or, if the gitea pull request was created, use gitea web interface. Browse all pull requests:
```
<gitea-release-url>/pulls
```
Select your pull request, merge changes and delete branch.

#### How to run partition or use config-based tools

In case, if the postponed changes need to be validated running DAQ partition, a shared file system has to be used to checkout a branch. For example create it in NFS area:
```
$ export SHARED=<some-path> # e.g. "/tbed/scratch/`whoami`/$CMTRELEASE" on TestBed or "$HOME/oks/$CMTRELEASE" on Point-1
$ mkdir -p $SHARED
$ cd $SHARED
$ oks_clone_repository -b <branch-name> -o .
$ chgrp -R zp .
$ chmod -R g+w .
$ export TDAQ_DB_USER_REPOSITORY=`pwd`
```
Then edit and commit changes to branch and run setup:
```
$ setup_daq <path-to-partition-file> <partition-name>
```

### Undo commit

If there is a need to undo already committed and pushed changes, the [git revert](https://git-scm.com/docs/git-revert) command has to be used.

To undo first commit, one has to:
1. clone git repository
2. find hash of the wrong commit
3. run the revert git command with this hash
4. push changes to git

For example:

* clone repository and run [git log](https://git-scm.com/docs/git-log) to see details of recent commits:
```
$ cd `oks_clone_repository`
$ git log -5
```

* find wrong commit in above log, run git revert command and push changes:
```
$ git revert --no-edit ab12... # use real commit hash
$ git push origin master
```

At this point the wrong commit is undone. The repository is fixed and its contains information about both, the wrong commit and its reverting.


## tdaq-09-01-00

Jira: [ADTCC-214](https://its.cern.ch/jira/browse/ADTCC-214), [ADTCC-226](https://its.cern.ch/jira/browse/ADTCC-226) and [ADTCC-227](https://its.cern.ch/jira/browse/ADTCC-227) 

[TWiki page](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltOks#4_OKS_Git_Repository).


***Replace cvs repository by git repository.***

The oks repository is stored on a git server. To access oks configuration the git repository is cloned into a temporal area. When changes are committed, the git server validates them verifying consistency of all repository files and checking user permissions as defined by the Access Manager policy. If commit is successful, the git server updates latest version of oks files on the filesystem (git repository mapping). Contrary to cvs implementation, the repository mapping is not required to access oks data using git repository. It is only implemented for convenience of users (fast browse of files) or filesystem-based access.

This is the main difference between oks git and cvs repository implementations:
* the oks git implementation uses git database to store and access oks files (like DBMS) and ignores the files on the filesystem;
* the oks cvs implementation used filesystem to store and access oks files.

The ignorance of files on the filesystem by oks git is done on purpose to preserve used configurations, and to implement configuration archiving on top of git database.

If user needs to access configuration from files stored on filesystem, it is necessary to disable oks git as explained in next section.

### User git repository permissions

The permissions to update files in oks git repository are defined by the [Access Manager](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltAccessManager) policy rules and enabled user roles.

### Environment Variables

The TDAQ_DB_REPOSITORY is the only setting that enables or disables use of the oks git repository. If it is set, the oks git repository is used. If not set, the filesystem repositories are used.

There are 3 shell functions available after release setup on TestBed and Point-1 to enable, disable and get status of the oks git repository:
* oks-git-on - to enable use of the oks git repository
* oks-git-off - to disable use of the oks git repository
* oks-git-status - to give status of the oks git repository use

The variable TDAQ_DB_REPOSITORY contains one or several git URLs (it does not point to a filesystem anymore). If there are several URLs, the used one depends on the OKS_GIT_PROTOCOL variable. If it is not set, the first URL is used. To get URL use oks_git_repository utility, e.g. to clone repository:
```
$ git clone `oks_git_repository`
```

The TDAQ_DB_USER_REPOSITORY can point to user git area. If it is set, oks-based tools will not clone git repository, but will use that area instead. It is responsibility of user to create that area and remove when not needed.

The TDAQ_DB_VERSION can be used to access particular revision of oks git repository. It is used internally by setup_daq to preserve concrete revision to be used by data taking session. In case of configuration reload this variable is set into a new value and distributed to all processes accessing oks configuration. The variable can be used in two formats:
* hash:$value - select revision by explicit hash
* date:$value - select latest revision before given date or timestamp
If the variable is not defined, the latest revision will be checked out.

The variable OKS_REPOSITORY_MAPPING_DIR points to the repository mapping.

As before, the TDAQ_DB_PATH can be used for a filesystem-based access and can contain several colon-separated filesystem repositories. With filesystem based access, the oks data from git repository can be included using the repository mapping variable, for example:
```
$ unset TDAQ_DB_REPOSITORY
$ export TDAQ_DB_PATH=$OKS_REPOSITORY_MAPPING_DIR:/det/a/b/c:/home/x/y/z
```

### Filepaths

To access an oks file from git repository one has to use its repository filename, for example:
```
$ oks_data_editor daq/segments/setup.data.xml
```

One should not use any filesystem relative or absolute paths referencing oks git repository files. There are two exceptions.

#### Filepaths relative to repository mapping

If the filepaths are relative to the OKS_REPOSITORY_MAPPING_DIR. That is done to help users with shell path-completion (hitting _TAB_ key), for example the following commands will correctly checkout the files from git repository and run appropriate tools:
```
$ export OKS_REPOSITORY_MAPPING_DIR=/tbed/git/oks/tdaq-99-00-00
$ oks_data_editor /tbed/git/oks/tdaq-99-00-00/daq/partitions/part_hlt.data.xml
$ setup_daq /tbed/git/oks/tdaq-99-00-00/daq/partitions/part_hlt.data.xml part_hlt
```

However, the preferable way is to use the repository filenames, e.g.:
```
$ oks_data_editor daq/partitions/part_hlt.data.xml
$ setup_daq daq/partitions/part_hlt.data.xml part_hlt
```

#### Filepaths relative to user repository

If the files are checked out by user, one should set TDAQ_DB_USER_REPOSITORY to access them.

The following example will result an error, since user provides path relative to current working directory:
```
$ cd `oks_clone_repository`
$ oks_dump -f oks_dump -f daq/segments/setup.data.xml
```

To make it working it is necessary to set the above variable:
```
$ cd `oks_clone_repository`
$ export TDAQ_DB_USER_REPOSITORY=`pwd`
$ oks_dump -f oks_dump -f daq/segments/setup.data.xml
```

### OKS tools

The tools from previous implementation can be used with oks git repository.

#### oks_dump

As in the previous implementation, the oks_dump can be used for fast check of oks configuration. Now it shows details of git operations, if the git repository is used, e.g.:
```
$ oks_dump -f daq/segments/setup-initial.data.xml
2020-Aug-11 11:01:24.524 [OKS checkout] => oks-checkout.sh -u /tmp/oks.ou9Qxy
git clone -q -n ssh://gitea@pc-tdq-git.cern.ch/oks/tdaq-09-01-00.git .
git checkout -q 
checkout oks version eb175611bc85f3061541cc20c62be8a00b4b26e1
2020-Aug-11 11:01:26.377 [OKS checkout] => done in 46.548 ms
Reading data file "/tmp/oks.ou9Qxy/daq/segments/setup-initial.data.xml" in normal format (51591 bytes)...
...
```

#### oks-import.sh

As before, this tool allows to import or to update user files from previous repositories or release installation areas. Change current working directory to a repository root and import required files and directories.

For example, to import some files from TDAQ release:
```
bash$ cd ${TDAQ_INST_PATH}/share/data
bash$ oks-import.sh -m "import release files" daq/schema daq/sw/*.data.xml daq/segments/common-environment.data.xml
```

To import some sub-detector folders from previous release:
```
bash$ cd /atlas/oks/tdaq-09-00-00
bash$ oks-import.sh -m "commit message" tile/hw tile/sw
```

#### OKS data editor

New functionality:
* commit updated files into git repository
* show notification about new commits in the git repository and merge local changes with master branch
* browse archived versions in the git repository and switch to an archived version

There is no need to create a temporal user repository, it is done automatically.

#### Direct use of GIT interface

The git interface is exposed to user. It is possible to clone git repository, copy, delete files, use any editors to update them and commit changes back to the git repository, e.g.:
```
$ cd `mktemp -d`
$ git clone `oks_git_repository` .
$ modify, copy, remove any files
$ git commit -m 'describe changes' x y z ...
$ git push origin
```

Above, first two lines normally can be replaced by:
```
$ cd `oks_clone_repository`
```

There are web interfaces to see historical changes and perform minimal modifications using web text editors on [Point-1](http://pc-atlas-www.cern.ch/gitea) and [TestBed](http://pc-tbed-git.cern.ch/gitea).
The CERN gitlab [atlas-tdaq-oks](https://gitlab.cern.ch/atlas-tdaq-oks) project is a read-only mirror of Point-1 and TestBed repositories. It can be accessed world-wide by authenticated ATLAS users.

All changes have to be stored into _master_ branch. The other branches are not yet supported (for the moment they will be rejected by git server). In future they are planned to be used for merge requests, when the committed changes have to be ignored during few next runs.

#### Undo commits

To undo changes use git revert. Avoid use commands causing losing commit history such as git reset.

Clone git repository. Then get the hash code of last commit, revert that commit and push changes:
```
$ git log -1
$ git revert <hash_code_from_git_log>
$ git push
```

### Archiving

The oks2coral archiving in Oracle is disabled. If files are stored in git repository, they are automatically archived into git database.

The run number database stores a reference to the used config version and repository filename.
```
$ rn_ls -c "oracle://atonr_adg/rn_r" -w ATLAS_RUN_NUMBER -s '2020-07-31T12:00:00' -t '2020-08-02T12:00:00' -a '%xml'
====================================================================================================================================================================================================================
|    Name |    Num | Start At (UTC)           |    Duration |   User |                  Host | Partition |                                       Version | Config Name                         | Comment           |
====================================================================================================================================================================================================================
| point-1 | 380689 | 2020-Jul-31 16:33:59.818 | 0:00:12.248 | isolov | pc-tdq-onl-05.cern.ch | all_hosts | hash:6800fe3b63a18859ef688612b44e051e4f36e345 | daq/partitions/all_hosts.data.xml   | Clean stop of run |
| point-1 | 380688 | 2020-Jul-31 14:52:26.896 |             | tdaqsw | pc-tdq-onl-01.cern.ch |   initial | hash:2c39688d965cbac84832e77342c316ee9d96adb3 | daq/segments/setup-initial.data.xml |                   |
====================================================================================================================================================================================================================
```

In turn, the git repository is tagged by run number and partition name.

To clone git repository use *oks_clone_repository* utility. The user can specify output directory and particular version by commit hash, date or tag. For example checkout by tag configuration used for run 380689 and partition *all_hosts*:
```
$ oks_clone_repository --version tag:r380689@all_hosts
```
or by hash (one can provide first few characters of the hash, as long as that partial hash is at least four characters long and unambiguous), e.g.:
```
oks_clone_repository --version hash:6800fe3b
```

## tdaq-08-03-01

### OKS data file format
Jira: [ADTCC-185](https://its.cern.ch/jira/browse/ADTCC-185) 

#### Store values inside tags

Store attribute and relationship data inside values of tags

Format for single value attributes
```
<attr name="xxx" type="yyy" val="zzz"/>
```
Format for multi value attributes
```
<attr name="xxx" type="yyy">
 <data val="zzz1"/>
 <data val="zzz2"/>
</attr>
```
Format for 0..1 and 1..1 relationships
```
<rel name="xxx" class="yyy" id="zzz"/>
```
Format for 0..N and 1..N relationships
```
<rel name="xxx">
  <ref class="yyy1" id="zzz1">
  <ref class="yyy2" id="zzz2">
</rel>
```

#### Skip empty data

Do not store attributes with values equal to empty initial and empty relationships

#### Compatibility and data conversion

The changes are backward compatible. New OKS library is able to read old "extended" and "compact" data formats.
For conversion open data file stored in old format using OKS Data Editor or DBE and save it.
Do not mixture old and new formats in the same file, when update file in a text editor.

## tdaq-06-00-00

Change a meaning of the OKS attribute range for string data type. Before the tokens of range were used for lexical comparison of the string. Now regular expression is used instead.

To enforce a value of string attribute be non empty one can use ".+" regular expression for range.

If attribute range for string type is defined, initial value of that attribute may be required to validate schema, for example non-empty string may not have default value set to empty string.

If an OKS schema had range defined for a string attribute for previous release used for configuration databases it has to be converted to enumeration type. No other changes are needed for a programming code using config and generated DAL packages.

For IS schema the range is not needed, since IS does not validate values of IS objects, so irrespectively to any range defined for IS attribute, the IS will allow to put any value. It is up to user decide to remove range in this case, or to convert attribute type from string to enumeration. However in the latter case the programming code using such schema may need be changed.

## tdaq-04-00-00

* Fix bug with wrong objects list returned by *referenced_by()* method from config package. The patch fixes calculation of RCRs by _OksObject::SetRelationshipValue(const OksDataInfo * odi, OksData * d)_ method (see bug [82615](https://savannah.cern.ch/bugs/?82615)).
* Fix problem when OKS file was created incorrectly by third-party tools: if creation date tag in the info section is missing (see bug [70563](https://savannah.cern.ch/bugs/?70563)), after saving by OKS on reload it resulted "not-a-date-time" error.  
* Fix several internal problems connected with execution of OKS code in several threads and several OKS kernels discovered during RDB writer server exploitation:  
    * bug [76158](https://savannah.cern.ch/bugs/?76158): the server may go into error state when several clients are updating OKS server repository;
    * bug [78326](https://savannah.cern.ch/bugs/?78326): the server may crash, when several clients actively update database caused by fast boost allocator with null mutex;
    * bug [82762](https://savannah.cern.ch/bugs/?82762): the server may crash under certain conditions during database reload.
  
## tdaq-02-01-00
  
To simplify future release patching procedure the oks package was split on two packages: oks and oks_utils. The oks package only contains library. All utilities including editors, relational oks and oks server were moved to oks_utils package.

## tdaq-02-00-03

* use Boost date and time format instead of OWL package classes (patched in tdaq-02-00-03)  
* performance improvements of XML files parsing (partly implemented as tdaq-02-00-03 patch)  
* substitute round brackets variable name by value before error reporting (patch [3619](https://savannah.cern.ch/patch/index.php?3619))
* checking date and time attribute initial values (patch [3656](https://savannah.cern.ch/patch/index.php?3656))
* provide a possibility for fast objects destruction required for RDB server (patch [3798](https://savannah.cern.ch/patch/?3798) and [62853](https://savannah.cern.ch/bugs/index.php?62853))
* throw exception, if a schema file is modified on data files reload (patch [3798](https://savannah.cern.ch/patch/?3798))
* add mode, when duplicated classes are not allowed

## tdaq-02-00-01

### OKS Server

* the oks-commit.sh supports directories in addition to files
* add oks-import.sh utility to simplify import of new directories and files  

* the repository locks remain from abnormally terminated oks commits can be removed on Point-1 by DAQ experts using /oks/admin/unlock-repository.sh script via sudo
* the "Replace" dialog of OKS Data editor proposes user to check-out repository file containing modified objects
* file-related relative pathnames and absolute pathnames includes are not allowed (in particular to avoid inclusion of files stored outside current repository and to simplify consistency check by oks-commit.sh)  

Read more details on the [TWiki page](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltOks#3_OKS_Server).

### OKS Performance Improvements

* the OKS library uses pool of threads to load OKS data files, i.e. the data files can be read in parallel  
* the number of threads by default is equal to number of the computer's CPU cores
* it can be modified via OKS_KERNEL_THREADS_POOL_SIZE environment variable
* the OKS library does not stop reading of files on first error, but continues loading of files in parallel threads until their ends or errors
    * thus the final error report may contain several errors coming from different files
    * this error report may change between different runs of OKS utilities even if the files were not updated
* for optimal performance it is recommended:
    1. to reduce number of schema files (at some point after a schema file parsing OKS requires single active thread to update the database schema)
    2. to avoid huge data files (processing of single data file is not parallelized since XML files are non indexed)

## tdaq-02-00-00

### C++ API Changes

Use new integer types from <stdint.h> to support 64-bits platform as shown in the following table:  

| OKS Type | Old C++ Type | New C++ Type |
|----------|--------------:|--------------:|
| s8 (8-bits signed integer) | unsigned char | uint8_t |  
| u8 (8-bits unsigned integer) | signed char  | int8_t |
| s16 (16-bits signed integer) | unsigned short | uint16_t |
| u16 (16-bits unsigned integer) | signed short | int16_t |
| s32 (32-bits signed integer) | unsigned long | uint32_t |
| u32 (32-bits unsigned integer) | signed long | int32_t |

### OKS Server

On Point-1 access to database repository will be controlled by the OKS Server. Read more about it on the [TWiki page](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltOks#3_OKS_Server).  

#### OKS Data Editor Changes

* Add search by file name in the main window
* Add search by class and object ID in the Data File dialog
* Add group file operations from the File menu:
    * Save all updated files (<Ctrl-S> shortcut)
    * OKS server related operations:  
    * Release User Repository (<Ctrl-D> shortcut)
    * Update User Repository (<Ctrl-U> shortcut)
    * Commit User Repository (<Ctrl-C> shortcut)
* Add "Referenced By" function from Object dialog (available on right mouse click from dialog's icon)


## tdaq-01-09-00

### OKS Library

* reload any consistent data file (also including changes in the included files)
* speed up OKS XML loading (about 25% faster comparing with release 1.8.4)  
* when read XML schema file, throw exception if base class is not loaded
* oks query supports regular expressions (add attribute comparator '~=')

### OKS Archiving Library  

* use temporal tables to create "try" incremental data version (to reduce unnecessary overhead on Oracle stream replication as requested by ATLAS Oracle DBA)

### OKS GUI Library  

* add support for mouse wheel (can be used in most dialogs of OKS schema and data editors)  

### OKS Data Editor

* improvements in the Find/Replace dialog:
* optionally find by Class and Attribute/Relationship names  
* present result as table
* select visible classes by name and objects by UID (request [34890](http://savannah.cern.ch/bugs/?34890))  
* see search panel at bottom of main window and object dialogs
* the search panel supports simple string search (auto-select when modify the selection pattern) and regular expressions (press button appearing when this option selected to apply regular expression)
* improve performance when build class dialog containing big number of objects (can be seen in 1.8.4 when number of objects is greater than 10K)


## tdaq-01-08-04

### GUI Changes

#### OKS Data Editor Force Save

The users have possibility to save partly-inconsistent data using "Force Save" command. This is required to save partial work avoiding it's possible lost because of exterior problems. For more info see request [28879](https://savannah.cern.ch/bugs/index.php?28879)

#### OKS Editors Recovery Mode

The users have possibility to periodically save changes made with OKS Schema and Data editors. Such changes automatically go to ${FILE}.saved for any unsaved modifications. If user skips changes on exit or an editor stops the work unexpectedly, those ".saved" files remain and can be used for manual recovery. This option can be switched On/Off using an editor Options menu. From the same menu it is possible to set the period of such saving varying from 5" up to 1 hour. For more info see request [28879](https://savannah.cern.ch/bugs/index.php?28879)  

#### Comments

The users have possibility to add comments to files. The comments can be browsed and edited from File dialog of the OKS Schema and Data editors. When file is saved, the editors can to ask user to provide comments, if "Ask comment on file save" option is activated in the "Options" menu (default option if user never saved GUI options). To add a comment user has to provide non-empty text. If no comment should be added on file save, press "Cancel" button in the Comment dialog.  

### XML Format Changes

The value of the "num-of-items" attribute of the oks schema info record is ignored. This was a reason of several wrong schema files after modifications made by users with text editors, when they forgot to set the correct value of this attribute.  

### API Changes

Note: the changes are completely transparent to users of config and DAL layers. Update your code only if you are using OKS directly!  

#### OksObject Class Changes

For consistent error reporting and simplification of code the following methods have been changed.

| Old Method Spec  | New Method Spec  |
|------------------|------------------|
| OksReturnStatus GetAttributeValue(const std::string&, OksData **) const | OksData * GetAttributeValue(const std::string&) const throw (oks::exception) |
| void GetAttributeValue(const OksDataInfo *, OksData **) const | OksData * GetAttributeValue(const OksDataInfo *) const throw () |
| OksReturnStatus GetRelationshipValue(const std::string&, OksData **) const | OksData * GetRelationshipValue(const std::string&) const throw (oks::exception) |
| void GetRelationshipValue(const OksDataInfo *, OksData **) | OksData * GetRelationshipValue(const OksDataInfo *) const throw () |
| OksReturnStatus SetAttributeValue(const std::string&, OksData *) | void SetAttributeValue(const std::string&, OksData *) throw (oks::exception) |
| OksReturnStatus SetAttributeValue(const OksDataInfo *, OksData *) | void SetAttributeValue(const OksDataInfo *, OksData *) throw (oks::exception) |
| OksReturnStatus SetRelationshipValue(const std::string&, OksData *) | void SetRelationshipValue(const std::string&, OksData *) throw (oks::exception) |
| OksReturnStatus SetRelationshipValue(const OksDataInfo *, OksData *) | void SetRelationshipValue(const OksDataInfo *, OksData *) throw(oks::exception)
| OksReturnStatus SetRelationshipValue(const std::string&, OksObject *) | void SetRelationshipValue(const std::string&, OksObject *) throw (oks::exception) |
| OksReturnStatus SetRelationshipValue(const OksDataInfo *, OksObject *) | void SetRelationshipValue(const OksDataInfo *, OksObject *) throw (oks::exception) |
| OksReturnStatus SetRelationshipValue(const std::string&, const std::string&, const std::string&) | void SetRelationshipValue(const std::string&, const std::string&, const std::string&) throw (oks::exception) |
| OksReturnStatus AddRelationshipValue(const std::string&, OksObject *) | void AddRelationshipValue(const std::string&, OksObject *) throw (oks::exception) |
| OksReturnStatus AddRelationshipValue(const OksDataInfo *, OksObject *) | void AddRelationshipValue(const OksDataInfo *, OksObject *) throw (oks::exception) |
| OksReturnStatus AddRelationshipValue(const std::string&, const std::string&, const std::string&) | void AddRelationshipValue(const std::string&, const std::string&, const std::string&) throw (oks::exception) |
| OksReturnStatus RemoveRelationshipValue(const char *, OksObject *) | void RemoveRelationshipValue(const std::string&, OksObject *) throw (oks::exception) |
| OksReturnStatus RemoveRelationshipValue(const OksDataInfo *, OksObject *) | void RemoveRelationshipValue(const OksDataInfo *, OksObject *) throw (oks::exception) |
| OksReturnStatus RemoveRelationshipValue(const std::string&, const std::string&, const std::string&) | void RemoveRelationshipValue(const std::string&, const std::string&, const std::string&) throw (oks::exception) |

Also by needs of config Python bindings one new method have been added:
```
std::list<OksObject *> * get_all_rels(const std::string& name = "*") const
```

The method returns list of objects which have a reference on given one. If the relationship name is set to "*", then the method takes into account  all relationships of all objects. The method performs full scan of all OKS objects and it is not recommended at large scale to build complete graph of relations between all database object; if only composite parents are needed, them the reverse_composite_rels() method has to be used.  

By needs of tidb package there are two new methods to read OksObject from and to it put into standard streams:  
```
static OksObject * get(std::istream&, OksKernel *) throw (oks::exception)
void put(std::ostream&) const throw (oks::exception)
```

#### OksClass Class Changes  

By needs of tidb package there are two new methods to read OksClass from and to it put into standard streams:  
```
static OksClass * get(std::istream&, OksKernel *) throw (oks::exception)
void put(std::ostream&) const throw (oks::exception)
```

#### OksFile Class Changes

To improve error reporting the following methods throw exception instead of returning bad error code:  

| Old Method Spec | New Method Spec |
|-----------------|-----------------|
| Oks::ReturnStatus lock(bool = false) | void lock(bool force = false) throw (oks::exception) |
| Oks::ReturnStatus unlock() | void unlock() throw (oks::exception) |
| Oks::ReturnStatus set_logical_name(const std::string &) | void set_logical_name(const std::string& name) throw (oks::exception) |
| Oks::ReturnStatus set_type(const std::string &) | void set_type(const std::string& type) throw (oks::exception) |

#### OksKernel Class Changes

| Old Method Spec | New Method Spec |
|-----------------|-----------------|
| OksReturnStatus set_active_schema(OksFile *) | void set_active_schema(OksFile *) throw (oks::exception) |
| OksReturnStatus set_active_data(OksFile *) | void set_active_data(OksFile *) throw (oks::exception) |
| bool GetAllowDuplicatedObjectsMode() const | bool get_allow_duplicated_objects_mode() const |
| void SetAllowDuplicatedObjectsMode(const bool) | void set_allow_duplicated_objects_mode(const bool) |
| bool GetVerboseMode() cons | bool get_verbose_mode() const |
| void SetVerboseMode(const bool) | void set_verbose_mode(const bool) |
| bool GetSilenceMode() const | bool get_silence_mode() const |
| void SetSilenceMode(const bool) | void set_silence_mode(const bool) |
| bool GetProfilingMode() const | ool get_profiling_mode() const |
| void SetProfilingMode(const bool) | void set_profiling_mode(const bool) |

The OKS kernel provides new methods to check status and to change various kernel modes:
* the status of mode checking maximum length of string attributes of some OKS objects (see also 1.8.3 OKS release notes)
  ```
  static bool get_skip_max_length_check_mode()
  static void set_skip_max_length_check_mode(const bool)
  ```
  it can also be set using OKS_SKIP_MAX_LENGTH_CHECK environment variable.  
* the status of the mode testing inherited duplicated objects:
  ```
  bool get_test_duplicated_objects_via_inheritance_mode() const
  void set_test_duplicated_objects_via_inheritance_mode(const bool)
  ```

There are new methods to backup schema and data files (the operation is silent and ignores any consistency rules):
```
void backup_data(OksFile * pf, const char * suffix = ".bak") throw (oks::exception)
void backup_schema(OksFile * pf, const char * suffix = ".bak") throw (oks::exception)
```

There are new methods to create OksClass and OksObject objects from standard streams:  
```
OksObject * create_object(std::istream& input) throw (oks::exception)
OksClass * create_class(std::istream& input) throw (oks::exception)
```

## tdaq-01-08-03

### General Changes

#### Max Length for OKS Names

By needs of OKS archiving, limit maximum string length for attributes of some OKS types, which are:

| OKS Type        | Attribute   | Maximum Length |
|-----------------|-------------|----------------|
| OksObject       | Object ID   | 64             |
| OksClass        | Name        | 64             |
| ^^              | Description | 2000           |
| OksAttribute    | Name        | 128            |
| ^^              | Description | 2000           |
| ^^              | Range       | 1024           |
| OksRelationship | Name        | 128            |
| ^^              | Description | 2000           |
| OksMethod       | Name        | 128            |
| ^^              | Description | 2000           |


#### New Oks Data Types

Add new OKS Data types:

* **s64_int_type** - signed 64-bits integer ("s64"); for implementation uses typed on the **int64_t** type
* **u64_int_type** - unsigned 64-bits integer ("u64"); for implementation uses typed on the **uint64_t** type
* **class_type** - reference on class; is implemented as string with range of allowed values equal to names of classes defined by the schema; it is important to put an initial value pointing to a class; if it will remain empty, then OKS will complain trying to create a new object.

Above types are fully supported by oks xml files, GUI editors and archiving.

If there are already existing and used OKS relational archives, check oks/src/rlib/create_db.[oracle|mysql|sqlite].sql bootstrap files for technology you are using and decide if schema of existing archive tables have to be changed.

#### Bug Fixes

Use maximum compiler-supported precision when store or print out values of OKS **float** and **double** numeric types. Before the precision was limited to the C++ std::ostream default value = 6 digits. E.g. it was not possible to store in OKS a double value equal to 1.23456789, which was rounded to 1.23457.

### OKS GUI Changes

#### New Features

The Data and Schema editors store options of graphical windows in the ~/.oks-data-editor-rc.xml and  ~/.oks-schema-editor-rc.xml files. To produce those files press <Set Default Values> button from a "Set Parameters" or "Properties" windows. The saved values will be used as default ones when the editor will be started next time.

#### Bug Fixes and Known Problems of OKS Data Editor

Fix bug in a graphical view, when several objects were over-drawn on the same place.

OKS Data Editor cannot display too many graphical objects in a graphical view. The maximum allowed number of objects is limited by capabilities of used Motif Drawing Area widget limiting size of area 35767x35767 pixels. When wrap to visible area or one object per row arrangement was used, the vertical limit was already reached for M4 combined partition and resource objects. Now in such case the editor will report error message and suggest the user to set different arrangement of objects.

## tdaq-01-08-00

### OKS Archiving

Add newly appeared classes (e.g. after integration with new detector) into schema already existing in archive (before it was required to create new version):
* smaller number of versions
* reduce archive tool’s downtime (human intervention is only needed when the database schema is modified, but not when it is extended)

Add newly appeared objects into base data version (before such objects were created in the incremental version, that takes more space):
* assume that any configuration object is referenced somehow (implicitly) by the partition object
* agreed with TDAQ groups and detectors; required schema changes in areas where string values were used for references instead of relations

As result, the utility to create new base or schema version in archive becomes much more robust since it does not require to put all data from all OKS repositories into base version in one go.

### OKS Data Editor: Graphical Window

* fix several bugs when work with icons of small size
* add possibility to arrange objects of a relationship by one object per single line, that makes OKS graphical window look like more "standard"; to use it, select "Arrange" -> "One child per line" item from graphical popup menu (press right mouse button in a free area of a graphical window)

### OKS Library

* most kernel functions throw exceptions instead of printing error messages; this allows better integration with oksconfig plug-in
* improve performance of OKS methods reading and saving database by caching names of tested files and directories


## tdaq-01-07-00

### API Changes

OKS library was starting to use exceptions to report problems. The methods dealing with input / output operations (i.e. _load...()_, _save...()_ and _new...()_ methods of _OksKernel_ and related methods of _OksClass_, _OksObject_, _OksData_, etc.) throw _oks::exception_ instead of returning _OksStatus_.

The old code testing return status:
```
OksKernel kernel;
OksFile * fh1 = kernel.**load_file**("_test.in.xml_");  // (1) can return zero in case of error!
if(fh1 == 0) { std::cerr << "_ERROR: Can not load file \"test.in.xml\"\n_"; exit(1); }
OksFile * fh2 = kernel.**new_data**("_test.out.xml_");  // (2) can return zero in case of error!
if(fh2 == 0) { std::cerr << "_ERROR: Can not create file \"test.out.xml\"\n_"; exit(1); }
...                                                     // (3) some code modifying oks data
if(kernel.save_schema(fh2) != OksSuccess) {             // (4) need to check OksStatus
  std::cerr << "_ERROR: Can not save file \"test.out.xml\"\n_"; exit(1);
}
```
has to be replaced with the following one:
```
OksKernel kernel;
try {
  OksFile * fh1 = kernel.**load_file**("_test.in.xml_"); // (5) always returns non-zero!
  OksFile * fh2 = kernel.**new_data**("_test.out.xml_"); // (6) always returns non-zero!
  ...                                                    // (7) some code modifying oks data
  kernel.save_schema(fh2);                               // (8) is void
}
catch (oks::exception & ex) { std::cerr << "Caught OKS exception: " << ex << std::endl; exit(1); }
```

Using exceptions there is no more need to test return values:

* a returned pointer is always non-zero (compare lines 1, 2 with 5, 6)
* _save...()_ methods become _void_ instead of returning _OksStatus_ (compare line 4 with 8)

### Improved Reporting of XML Problems

Another advantage of exception usage is consistent error reporting, that is especially important in case of multiple include files. In the past, any error has been reported to the standard error stream in the moment of it's detection and in some cases without enough diagnostics. For example the only possibility to get name of the file where a problem took place was to read _OKS info messages_:
```
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
```

When above problem took place using oksconfig plug-in, it was not possible to identify the exact place of problem at all (at least without setting _OKS_KERNEL_SILENCE_ to _no_):
```
bash$ config_dump -d oksconfig:daq/partitions/be_test.data.xml -c Partition
ERROR [OksXmlInputStream::read_tag_start()]:
(line 67, char 2)
Unexpected end of file
ERROR [OksXmlInputStream::read_tag_start()]:
(line 67, char 2)
Unexpected end of file
```

Now the resulted exception always contains exact reason of error and keeps full chain of files inclusion and oks entities dependencies, e.g.:
```
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
```
The same exception will be passed to the ERS exception reported by oksconfig plug-in:
```
bash$ config_dump -d oksconfig:/tmp/daq/partitions/be_test.data.xml -c Partition
ERROR 2007-Jan-17 11:20:12 [ConfigurationImpl* _oksconfig_creator_(...)
at oksconfig/src/OksConfiguration.cpp:29] oksconfig initialization error
        was caused by: ERROR 2007-Jan-17 11:20:12 [virtual void OksConfiguration::open_db(...) at
        oksconfig/src/OksConfiguration.cpp:57] cannot load file '/tmp/daq/partitions/be_test.data.xml':
oks[10] ***: failed to load data file "/tmp/daq/partitions/be_test.data.xml" because:
...
oks[2] ***: failed to load data file "/tmp/DAQRelease/sw/tags.data.xml" because:
oks[1] ***: failed to read 'object "i686-slc3-gcc344-dbg@Tag"'
oks[0] ***: Unexpected end of file while read tag start at (line 66, char 51)
```

### OKS Archiving

Add _Release_ column to _OksSchema_ table to simplify choice of right schema by oks2coral and to allow user easier choice of archived configuration data. There is new OKS Archiving Web GUI, allowing:
* queries on archived configurations by time intervals, release, user, host and partition patterns;
* sorting result by multiple columns;
* selection which columns to be shown.

The test Web GUI replaced previous one: [http://cern.ch/isolov/cgi-bin/oks-archive.pl](http://cern.ch/isolov/cgi-bin/oks-archive.pl)
Provide bootstrap files for different RDBMS:
* create_db.mysql.sql
* create_db.oracle.sql (renamed old create_db.sql)
* create_db.sqlite.sql

Fix several run-time problem for MySQL CORAL plug-in.

#### API changes

* Add optional _release_ parameter to several functions. It is used to get HEAD schema and data version per TDAQ release. By default the release parameter points to current release (i.e. to "tdaq-01-07-00").
* Add function _get_max_schema_version()_ to know maximum schema version number to be used to choose free version number. Note, the existing method _get_head_schema_version()_ returns head schema version per release.
* Add function _get_time_host_user()_ to extract time, host and user values from attribute list. It is used by _roks_ library and by _oks_ls_data_ utility.

#### List Archives Utility

Add several _new options_ to specify archives selection criteria:
```
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
  -c connect_string    database connection string
  -w schema_name       name of working schema
  -l                   list releases
  -s schema_version    print out data of this particular version (0 = HEAD version)
  -b                   print out base data versions only
  -z                   print size of version (i.e. number of relational rows to store it)
  -u                   show who, when, where and how used given version
  -d                   show description
  -t parameters        sort output by several columns; the parameters may contain the following
                       items (where first symbol is for ascending and second for descending order):
                         v | V - sort by versions;
                         t | T - sort by time;
                         u | U - sort by user names;
                         h | H - sort by hostnames;
                         p | P - sort by partition names (i.e. by descriptions);
  -r release_name      show configuration for given release name
  -e user_name_pattern show configuration for user names satisfying pattern (see syntax description below)
  -o hostname_pattern  show configuration for hostnames satisfying pattern (see syntax description below)
  -p partition_pattern show configuration for partition names satisfying pattern (see syntax description below)
  -S since_timestamp   show configuration archived since given moment (see timestamp format description below)
  -T till_timestamp    show configuration archived before given moment (see timestamp format description below)
  -v verbosity_level   set verbose output level (0 - silent, 1 - normal, 2 - extended, 3 - debug, ...)
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
    % (i.e. percent symbol)    - any string of zero or more characters;
    _ (i.e. underscore symbol) - any single character.
```

#### Other Implementation Changes and Bug Fixes

* replace _OksAlloc_ class used for the memory usage optimisation by the Boost class _boost/pool/pool_alloc.hpp_; header file _oks/alloc.h_ has been removed; OKS is always initialized in multi-thread safe mode;
* when save a data file, keep the file flags
* fix run-time bug appeared on 64-bits architecture (wrong calculation of const string literal size); by chance it worked correctly on 32 bits;

##### OKS Schema Editor

* attach _Range_ and _Initial Value_ properties to the right side of the attribute window to allow see long strings;
* do not show _Non Null Value_ property for _boolean_ attribute.

##### OKS Data Editor

* mark file updated, when swap objects inside relationship value;
* avoid bug when copy object to existing id;
* fix bug when load query with attribute comparator.


## tdaq-01-06-00

There are no any changes in OKS, that require a user to modify or to convert a consistent database file. However the OKS becomes more strict for saving and loading of inconsistent schema and data files (no required includes, dangling object references, wrong or missing attribute and relationship values). A user can be asked to modify data as it is required by schema before it will be possible to save them using OKS tools. The other changes in OKS are connected with extension of features using relational backend (new relational tables and utilities).

### OKS library

#### Files Consistency

* to improve diagnostic report included files, where '_no files inclusion path between referenced objects_' problem takes place
* allow duplicated objects for archiving purposes (use OKS_KERNEL_ALLOW_DUPLICATED_OBJECTS variable)
* report object id and attribute name when read data with wrong range
* check inclusion of required schema files before saving
* allow empty objects (i.e. without attribute and relationship values)

#### Schema Consistency

* report warning when attributes and relationships change between single-value/multi-value in case of redefinition in derived class or there are such conflicts in super-classes
* change exclusiveness scope of composite relations from object to relationship  
  e.g. a module can be exclusively inserted to crate and to detector, but it cannot be inserted to several crates

#### XML Parser

* report correct line number and position for certain types of problems in oks xml
* fix minor memory leak in OKS xml parser
* fix several bugs with xml comments and end of comment
* skip any attributes defined in the oks-schema or oks-data tag (they can come from automatic xml generation tools)
* allow xml style-sheets and xmlns tags
* allow different encodings of xml

#### Relational Methods using RAL

* move from POOL RAL to CORAL and follow changes in CORAL API up to latest used version (CORAL 1.3.0)
* add table to keep used configurations
* normalize schema as it was recommended by CERN Oracle DBA
* store oks date and time as string
* increase length of class name (now it is limited by 64 bytes)
* use xml authentication (see file authentication.xml pointed by the CORAL_AUTH_PATH variable)

#### General Methods

* add method to get referenced objects
* path query: check goal at non-leave object in the path to allow paths with optional branches
* fix bug when TDAQ_DB_PATH is not defined
* do not print warning in silent mode (before few ones left by mistake)

### General OKS Utilities

#### New oks-generate-schema-docs.sh

The utility generates description of the schema files using xsl conversion of standard oks schema xml files. Such conversion is performed by user's Internet browser on fly. This should work with MS Internet Explorer 6.0, Mozilla 1.7.12 and their higher versions.
```
Usage: oks-generate-schema-docs.sh [--help] [--verbose] [--search-dir in-dir] [--search-pattern schema-file-pattern] --target-dir out-dir
Arguments/Options:
  -v | --verbose verbose output
  -h | --help print this message
  -d | --search-dir in-dir directory to search schema files; current value = [/afs/cern.ch/atlas/project/tdaq/cmt/nightly/installed/share/data]
  -p | --search-pattern p pattern for schema file names; current value = [*.xml]
  -t | --target-dir out-dir directory where to put out files
  -n | --page-name name provide name for generated index.html file; current value = [TDAQ Release Schema Files]
```

The example of generated schema description for DAQ/HLT-I nightly release is available on: [http://pcatd12.cern.ch/releases/nightly/installed/share/doc/DAQRelease/html](http://pcatd12.cern.ch/releases/nightly/installed/share/doc/DAQRelease/html/)

The utility can be used by users of the DAQ/HLT-I release to generate descriptions of own schema files using --search-dir to point to area with own schema files.

#### New oks-test-duplicated-objects.sh

The utility tests duplicated objects (i.e. objects with equal class names and IDs) stored in oks data files referenced by the TDAQ_DB_PATH variable.

The utility has been created to find files, which are _bad_ from archiving point of view. In ideal case it should find no duplications.

To filter out files which need to be ignored either put file name pattern(s) into _-s_ command line option, or install into in any subdirectory of ${TDAQ_INST_PATH} file(s) with name _remove-from-oks-archive.txt_ containing such patterns (one pattern per line), e.g. run "oks-test-duplicated-objects.sh -v -s '.*share/data/ExampleConfiguration.*' '.*share/data/training.*'" to skip all files installed by the _ExampleConfiguration_ and _training_ packages.

#### oks_merge

* merge data files (use _-o_ option) and schema files (use _-s_ option)

#### oks_diff_data

* add options to compare objects of one class or single object

#### oks_diff_schema

* allow data files as input (i.e. compare schemes used by data files)
* change values returned by binary to be able to report number of found differences:
    * 0 - there are no differences between two schema files
    * 253 - bad command line
    * 254 - cannot load database file(s)
    * 255 - loaded file has no any class
    * 1..252 - number of differences (is limited by the max possible value)


#### oks_dump

* return different status in case of different problems:
    * 0 - no problems found
    * 1 - ad command line parameter
    * 2 - bad oks file(s)
    * 3 - bad query passed via -q or -p options
    * 4 - cannot find class passed via -c option
    * 5 - loaded objects have dangling references
* new option _-i_ adds possibility to read files to be printed from input-file instead of command line to help with very long list of files (that may exceed maximum command line length)
* distinguish lists of schema and data files lists on user choice:
    * use option _-f_ to print list of all oks xml files (is used as before)
    * use new option _-s_ to print list oks schema files
   * use new option _-d_ to print list oks data files
* add option _-r_ to print out list of objects referenced by found objects (can only be used with query)

### Utilities for OKS Archiving

All utilities described below require two parameters:

* the database connection string
* the name of the relational database working schema

The values of above parameters are site specific. For development purposes at CERN they are:

| the connection string: | oracle://devdb10/tdaq_dev_backup |
| the working schema: | onlcool |

For other sites or different purposes different database servers and/or accounts should be used. To create new database (for new owner or different DB server) use _oks/src/rlib/create_db.sql_ file, e.g. in case of Oracle:
```
bash$ sqlplus ${user}/${password}@${host} @$TDAQ_INST_PATH/../oks/src/rlib/create_db.sql
```
where _${user}_, _${password}_ and _${host}_ have site-specific values.

#### New oks-create-new-base-version.sh

The utility has to be used to create a new base version in the archive. It is necessary when the there are changes in the configuration schemes or there are significant changes in the configuration data. In particular a request to use this utility can be send by the oks2coral binary.

By default, the utility checks differences between _head_ schema version from archive and schemes found under TDAQ_DB_PATH. If there are changes, the utility creates new _head_ schema in the archive. Then the utility reads all data files pointed by the TDAQ_DB_PATH variable and stores them into archive. The command line parameters used by the utility are shown below:
```
Usage: oks-create-new-base-version.sh -c connect_string -w schema_name [--help] [--verbose level] [--skip-files reg-exp*]
Arguments/Options:
  -c | --connect-string connect_str    database connection string
  -w | --working-schema schema_name    name of relational database working schema
  -v | --verbose level                 switch on verbose output
  -h | --help                          print this message
  -s | --skip-files r1 ...             list of regular expressions to ignore files
```

#### New oks_tag_data

The utility is created to set a unique string tag on any existing data in OKS archive. A data can be accessed by such human meaningful tag instead of schema and data version numbers.
```
usage: oks_tag_data -c | --connect-string connect_string
                    -w | --working-schema schema_name
                    -t | --tag data_tag
                    [-e | --head-data-version]
                    [-s | --schema-version schema_version]
                    [-n | --data-version data_version]
                    [-v | --verbose-level verbosity_level]
                    [-h | --help]
Options/Arguments:
  -c connect_string   database connection string
  -w schema_name      name of working schema
  -t data_tag         unique tag
  -e                  tag head data version (for head schema or defined by -s)
  -s schema_version   use data for given schema version (extra -n or -e is required)
  -n data_version     use given data version (extra -s is required)
  -v verbosity_level  set verbose output level (0 - silent, 1 - normal, 2 - extended, 3 - debug, ...)
  -h                  print this message
```

#### New oks_ls_data

The utility is created to print out information about data in OKS archive.
```
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
```

The version is shown as sv.dv[.bv], where:
* **sv** - schema version;
* **dv** - data version;
* **bv** - base version (optional, only appears for incremental data versions).

For example:
* 1.12 - base version with schema-version = 1 and data-version = 12
* 1.34.12 - incremental version with data-version = 34 built on top of base version 1.12

The size is reported when -z option is used explicitly. To get the size it is necessary to execute additional queries and this may take some time for big number of versions. The size of a base version is defined as number of rows in relational tables (_OksObject_, _OksDataVal_ and _OksDataRel_) to describe it's data. For an incremental version the size shows numbers of additional rows to show differences from it's base version, i.e. such rows can be used to mark an object as created, removed or updated, and to provide new values for attributes and relationships of objects. The size is presented in form obj-num:attr-num:rel-num, where:
* **obj-num** - number of objects rows;
* **attr-num** - number of attribute value rows;
* **rel-num** - number of relationship rows.

For example:
* 951:8271:1498 - the base version contains 951 objects; the objects have 8271 attribute values and 1498 relationships
* 1:1:0 - the incremental version has one object updated comparing with base version (an attribute of the object was modified)

The usage of archived versions is reported when -u option is used explicitly. It requires some additional queries and may take some time for big number of versions. The usage of archived data is shown in table below the information about version. The values in _Version_ and _Size_ columns remain empty. The _Description_ column contains information about partition and run number.

#### oks_put_schema,  oks_put_data,  oks_get_schema and oks_get_data

* use xml authentication instead of explicit user name and password passed via command line
* try to re-use the same options between binaries
* to know exact options per binary run it with _--help_ option

### GUI Editors

#### Schema Editor

* meaningless "Many" cardinality is not supported for relationships
*  heck classes and files consistency during save operation

#### Data Editor

* fix bug, when create new object providing ID of already existing object
* do not exit, if there is an error with file saving (i.e. allow user to change file name or it's permissions)
* check objects and files consistency during save operation
* refresh correctly list of all files when reload a file that changed includes
* warn user about bad files during loading them (e.g. with missing includes); a user should to fix reported problem before any other modifications!


## tdaq-01-04-00

There are several changes in the relational OKS back-end:
* use bulk insert for values of oks attributes and relationships
* replace OksDataInt, OksDataNum, OksDataString and OksDataDate tables by single OksDataVal table with appropriate columns to store integer, number, string and date values
* environment variable OKS_RAL_ORDER_QUERY_RESULTS can be used as switch on/off "order by" statement of queries reading values of attributes and relationships for performance studies
* to improve performance do not read description of class methods and their implementations, when get oks data only

Change interpretation of **s8** and **u8** oks data types from symbol type to 8 bits integer type:
* u8 and s8 oks data types are interpreted as integers by any output method; before printing out non-alphanumeric symbols as char resulted wrong output
* oks_data_editor allows to edit u8 and s8 types as octal, decimal and hexadecimal numbers
* oks_schema_editor allows to set format for s8 and u8 types

The OksData stream output operator uses '_format_' field to prints out s8, u8, s16, u16, s32 and u32 types. It is used by the oks_dump program.

Fix bug appeared with few window managers, when under certain conditions oks gui applications do not react on mouse button clicks.

## tdaq-01-02-00

### OKS Relational Backend

An exercise to use a relational database to store oks schema and data information instead of xml files has been done. New _roks_ library appears. It contains code to store oks classes and oks objects to a relational database and to retrieve them back. It is based on the LCG POOL RAL package (see [http://lcgapp.cern.ch/project/persist/](http://lcgapp.cern.ch/project/persist/) for more information). Four new example applications _oks_put_schema_, _oks_put_data_, _oks_get_schema_ and _oks_get_data_ demonstrate it's usage. The file _oks/src/rlib/create_db.sql_ contains definition of the relational tables to store oks information. The exercise has been tested with Oracle on devdb.cern.ch server supported by the CERN IT.

The following sequence of steps to create relational tables, put/get schema and put/get data should to work:
```
sqlplus $[user/$passwd@$server](mailto:user/password@server) $TDAQ_INST_PATH/../oks/src/rlib/create_db.sql
oks_put_schema -c "oracle://$server" -u $user -p $passwd -f oks-file.xml -t "v1" "first" -s 1
oks_get_schema -c "oracle://$server" -u $user -p $passwd -s "/tmp/v1.schema.xml" -e
oks_put_data -c "oracle://$server" -u $user -p $passwd -f oks-file.xml -v -l -a -t "v1.1" "first"
oks_get_data -c "oracle://$server" -u $user -p $passwd -t "v1.1" -f /tmp/v1.1.data.xml
```

For more information contact the oks package developer.

### Path Query

Add support for path queries. Such query returns path between two objects by navigating via relationships in accordance with user-defined query pattern. The result of such query is a list of oks objects forming the path. The use case is to get a path in several trees of references between objects using the same leave objects. Note, for composite objects and exclusive relationships, the usage of reverse composite relationships is more effective. In such case there is the only tree built on top of given leaves.

#### API

Add _oks::QueryPath_ class to describe special type of query calculating path between two given objects. The constructor uses query as a text. Syntax of query path is shown below:
```
query-path ::= '(**path-to** "destination-object" _query-path-expression_)'
query-path-expression ::= '(_query-path-type_ "rel-name" [, "rel-name"*] [_query-path-expression_])'
query-path-type ::= '**direct** | **nested'**
```

If the string cannot be parsed, the exception _oks::bad_query_syntax_ is thrown.

When an oks query path object is created, it can be used to search a path from given source object using the following method:
```
OksObject::List * OksObject::find_path(const oks::QueryPath& query) const;
```

If a path is found, non-empty list is returned.

#### Example of query string

The example of query is shown below:
```
(path-to "my-id@my-class" (direct "A" "B" (nested "N" (direct "X" "Y" "Z"))))
```

The destination object is "my-id@my-class". The search can be started from any object of any class. In our example the start object has to have two relationships named "A" and "B". An object referenced via "A" and "B" should have relationship "N". In our example it is possible to lookup for path via nested objects linked via relationship "N". Finally all objects referenced via "N" should have relationships "X", "Y" and "Z". If the destination object is referenced by them, the path is found.

#### Generic query extensions

The oks query expression was extended to use object ID as part of query expression. The used syntax is '(**object-id** "an-object-id")'. The use case is to identify an object used in a relationship expression, e.g. get all objects of some class referencing this object. Note, this is more effective than search by non-indexed attribute value and this is the only way to define an object without non-key attributes.

The object ID expression is integrated to the oks data editor query constructor (choose "_Object ID_" radio button in an attribute expression form).

#### Example of query string

The example of query to search all objects of some class referencing via relationship "my-relationship" an object with id equal to "test".
```
(all ("my-relationship" some (object-id "test" =)))
```

For example, find all applications including subclasses, which runs on host with id lxplus001.cern.ch:
```
(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))
```

### Dangling references

Add '_bool OksKernel::get_bind_objects_status() const_' method, that returns status of last _OksKernel::bind_objects()_ method call. It can be used to check lack of dangling references after loading of database files.

OKS improves reporting of the dangling references. In addition to the dangling reference itself the oks reports an object where unresolved reference was found:
```
WARNING [OksObject::bind()]:
Cannot find object "[lxplus053.cern.ch@Computer](mailto:lxplus053.cern.ch@Computer)"
WARNING [OksObject::bind_objects()]:
There are unresolved references from object "lxplus-3x3-23 ctrl@RunControlApplication"
```

### OKS dump

The _oks_dump_ binary returns non-null status, if the loaded files have non-resolved references between objects.

It also supports path queries: use '_--path "object" "path-query"_' command line parameters, e.g. to find path between an application and partition objects:
```
bash$ oks_dump --path "onlsw_test_3x3_lxlpus@Partition" '(path-to "lxplus-3x3-21-ctrl@RunControlApplication" (direct "Segments" "OnlineInfrastructure" (nested "Segments" (direct "Applications" "IsControlledBy" "Resources"))))' daq/partitions/lxplus_tests.data.xml  
Found 3 objects in the path "(path-to "lxplus-3x3-21-ctrl@RunControlApplication" (direct "Segments" "OnlineInfrastructure" (nested "Segments" (direct "Applications" "IsControlledBy" "Resources"))))" from object "onlsw_test_3x3_lxlpus@Partition":  
Object "[onlsw_test_3x3_lxlpus@Partition](mailto:onlsw_test_3x3_lxlpus@Partition)" ...  
Object "[lxplus-3x3-2@Segment](mailto:lxplus-3x3-2@Segment)" ...
Object "[lxplus-3x3-21@Segment](mailto:lxplus-3x3-21@Segment)" ...
```


## tdaq-01-01-00

### Database Consistency

* No more identical objects allowed. In the past a warning message was printed out and an anonymous object was created, when identical object was read. Now the error message is printed out, the reading of the database file containing duplicated object is stopped and the bad status of the file is returned. The error message contains the object identity and both names of the files containing such objects.
* Non-existent attributes and relationships of objects are reported as warnings. Before the data stored in extended format were converted without any message in case of schema evolution.
* To avoid possible confusion of users with variables converters provided by the **dal** package, the syntax of environment variables description used by oks in filenames is changed. Now the valid syntax is _$(FOO)_. In previous releases it was _${FOO}_. Note, it is not recommended to use environment variables in includes, since it makes database dependent on user's setup. The recommended way is to define includes either relative to a database repository, or to the parent file.

### Queries Creation and Destruction

*  To allow proper destruction of a query make all internal query-related objects allocated on heap. In the past  a query constructed from string was not properly released and memory leak took place. Now all sub-query objects are created on heap and are properly released, when the query object is destroyed. All code using queries (the oks kernel code, tutorial, examples) has been changed.

### OKS Dump Application

* Add several command line options:
    * --files-only - prints out list names of database files
    * --class - dump given class (all objects of class or matching some query)
    * --query - print objects matching query (can only be used with class)

### Bugs Fixes

* Avoid possible segmentation fault, when read an object without loaded class.
* When load a schema, do not set automatically default value for enumeration attribute, if it was empty. It caused such default value explicitly set, when the schema is saved from the editor and such behavior was not expected by users.
```

### Query grammar implementation
The complete `oks/query.h` header and `src/query.cpp` implementation are embedded below. Key facts extracted:
- Operator tokens (`src/query.cpp:15-31`): `or`, `and`, `not`, `some`, `this`, `all`, `object-id`, `=`, `!=`, `~=`, `<=`, `>=`, `<`, `>`, `path-to`, `direct`, `nested`.
- `OksQuery::RE = "~="` is the regular-expression comparator; `reg_exp_cmp` uses `boost::regex_match` (`src/query.cpp:57-59`).
- `path-to` queries are implemented by the `oks::QueryPath`/`QueryPathExpression` classes (`oks/query.h:328-399`) with `direct`/`nested` relationship-following.
### `oks/query.h`  
*Local path: `repo/oks/oks/query.h`*

```cpp
/**	
 *	\file oks/query.h
 *	
 *	This file is part of the OKS package.
 *      Author: Igor SOLOVIEV "https://phonebook.cern.ch/phonebook/#personDetails/?id=432778"
 *	
 *	This file contains the declarations for the OKS query.
 */

#ifndef __OKS_QUERY
#define __OKS_QUERY

#include <oks/defs.h>
#include <oks/object.h>

#include <list>
#include <exception>

#include <boost/regex.hpp>


class OksQueryExpression;


  ///	OKS query class.
  /**
   *  	The class implements OKS query.
   *  	A query can be executed over some class (and optionally subclasses)
   *	with given query expression. A query expression can be constructed
   *	dynamically for given query expression or can be read from string.
   */

class OksQuery
{
  public:

    OksQuery(bool b, OksQueryExpression *q = 0) : p_sub_classes (b), p_expression (q), p_status (0) {};
    OksQuery(const OksClass *, const std::string &);
    virtual ~OksQuery();

    friend std::ostream& operator<<(std::ostream&, const OksQuery&);

    bool search_in_subclasses() const {return p_sub_classes;}
    void search_in_subclasses(bool b) {p_sub_classes = b;}

    OksQueryExpression * get() const {return p_expression;}
    void set(OksQueryExpression* q) {p_expression = q;}
    
    bool good() const {return (p_status == 0);}

    enum QueryType {
      unknown_type,
      comparator_type,
      relationship_type,
      not_type,
      and_type,
      or_type
    };

    static const char *	 OR;
    static const char *	 AND;
    static const char *	 NOT;
    static const char *	 SOME;
    static const char *	 THIS_CLASS;
    static const char *	 ALL_SUBCLASSES;
    static const char *	 OID;
    static const char *	 EQ;
    static const char *	 NE;
    static const char *	 RE;
    static const char *	 LE;
    static const char *	 GE;
    static const char *	 LS;
    static const char *	 GT;
    static const char *	 PATH_TO;
    static const char *	 DIRECT;
    static const char *	 NESTED;

    static bool equal_cmp(const OksData *, const OksData *);
    static bool not_equal_cmp(const OksData *, const OksData *);
    static bool less_or_equal_cmp(const OksData *, const OksData *);
    static bool greater_or_equal_cmp(const OksData *, const OksData *);
    static bool less_cmp(const OksData *, const OksData *);
    static bool greater_cmp(const OksData *, const OksData *);
    static bool reg_exp_cmp(const OksData *, const OksData * regexp);

    typedef bool (*Comparator)(const OksData *, const OksData *);


  private:  

    bool p_sub_classes;
    OksQueryExpression * p_expression;
    int p_status;
    
    static OksQueryExpression *	create_expression(const OksClass *, const std::string &);
};


  ///	OKS query expression class.
  /**
   *  	The abstract class provides interface to OKS query expression.
   *	A query expression has type and method to check its correctness.
   */

class OksQueryExpression {
  friend std::ostream& operator<<(std::ostream&, const OksQueryExpression&);

  public:

    virtual ~OksQueryExpression() {;}

    OksQuery::QueryType type() const {return p_type;}
    bool CheckSyntax() const;
    bool operator==(const class OksQueryExpression& e) const {return (this == &e);}


  protected:

    OksQueryExpression(OksQuery::QueryType qet = OksQuery::unknown_type) : p_type (qet) {};


  private:

    const OksQuery::QueryType p_type;
};


  ///	OKS query expression comparator class.
  /**
   *  	The query comparator class is a basis of any query.
   *	It returns result of logical comparison between OKS value
   *	(defined by the OksData) and values of tested objects
   *	attributes (e.g. found all objects with attr-x >= 128)
   */

class OksComparator : public OksQueryExpression
{
  friend class OksObject;
  friend class OksQueryExpression;

  public:

    OksComparator(const OksAttribute *a, OksData *v, OksQuery::Comparator f) :
	OksQueryExpression	(OksQuery::comparator_type),
  	attribute		(a),
  	value			(v),
  	m_comp_f		(f),
	m_reg_exp               (0)
  	{};

    virtual ~OksComparator() {
      delete value;
      if(m_reg_exp) delete m_reg_exp;
    }

    const OksAttribute * GetAttribute() const {return attribute;}
    void SetAttribute(const OksAttribute* a) {attribute = a;}

    OksData * GetValue() {return value;}
    void SetValue(OksData *v);

    void clean_reg_exp();

    OksQuery::Comparator GetFunction() const {return m_comp_f;}
    void SetFunction(OksQuery::Comparator f) {m_comp_f = f;}

  private:

    const OksAttribute *  attribute;
    OksData *             value;
    OksQuery::Comparator  m_comp_f;
    boost::regex *        m_reg_exp;

};


  ///	OKS query relationship expression class.
  /**
   *  	The query relationship expression class is used to define
   *	queries via values of attributes for referenced objects, (e.g.
   *	find all persons living in a house with number 13.
   */

class OksRelationshipExpression : public OksQueryExpression
{
  friend class			OksObject;
  friend class			OksQueryExpression;

  public:

    OksRelationshipExpression(const OksRelationship *r, OksQueryExpression *q, bool b = false) :
	OksQueryExpression	(OksQuery::relationship_type),
  	relationship		(r),
  	checkAllObjects		(b),
  	p_expression		(q)
  	{};

    virtual ~OksRelationshipExpression() {delete p_expression;}
  
    const OksRelationship * GetRelationship() const {return relationship;}
    void SetRelationship(const OksRelationship* r) {relationship = r;}
  
    OksQueryExpression * get() const {return p_expression;}
    void set(OksQueryExpression* q) {p_expression = q;}

    bool IsCheckAllObjects() const {return checkAllObjects;}
    void SetIsCheckAllObjects(const bool b) {checkAllObjects = b;}


  private:

    const OksRelationship*	relationship;
    bool			checkAllObjects;
    OksQueryExpression*		p_expression;

};


  ///	OKS query logical NOT expression class.
  /**
   *  	The query not expression is used to change result of expression
   *	to opposite.
   */

class OksNotExpression : public OksQueryExpression
{

  friend class OksObject;
  friend class OksQueryExpression;

  public:

    OksNotExpression(OksQueryExpression *q = 0) : OksQueryExpression(OksQuery::not_type), p_expression (q) {};

    virtual ~OksNotExpression() {delete p_expression;}

    OksQueryExpression * get() const {return p_expression;}
    void set(OksQueryExpression* q) {p_expression = q;}


  private:

    OksQueryExpression		*p_expression;

};


  ///	Abstract class describing list of OKS query expressions.

class OksListBaseQueryExpression
{

  friend class OksObject;
  friend class OksClass;
  friend class OksQueryExpression;

  public:

    virtual ~OksListBaseQueryExpression() {while(!p_expressions.empty()) {OksQueryExpression * qe = p_expressions.front(); p_expressions.pop_front(); delete qe;}}

    const std::list<OksQueryExpression *> & expressions() const {return p_expressions;}
    void add(OksQueryExpression *q) {p_expressions.push_back(q);}


  protected:

    OksListBaseQueryExpression () {};


  private:

    std::list<OksQueryExpression *> p_expressions;

};


  ///	OKS query logical AND expression class.

class OksAndExpression : public OksQueryExpression, public OksListBaseQueryExpression
{
  public:

    OksAndExpression() : OksQueryExpression(OksQuery::and_type) {};

    virtual ~OksAndExpression() {;}
};


  ///	OKS query logical OR expression class.

class OksOrExpression : public OksQueryExpression, public OksListBaseQueryExpression
{
  public:

    OksOrExpression() : OksQueryExpression(OksQuery::or_type) {};

    virtual ~OksOrExpression() {;}

};

inline OksQuery::~OksQuery() {delete p_expression;}


namespace oks {

    /**
     *  The exception is thrown when parsing of query object
     *  (QueryPath object) from string is failed.
     */

  class bad_query_syntax : public std::exception
  {

    std::string p_what;

  public:

    bad_query_syntax(const std::string& what_arg) noexcept : p_what (what_arg)
      {}
    virtual ~bad_query_syntax() noexcept
      {}

    virtual const char * what () const noexcept
      { return p_what.c_str ();}
  };


    /**
     *  The class is used by the QueryPath class to describe relationships
     *  used for path search for given class.
     */

  class QueryPathExpression
  {

    friend class QueryPath;
    friend class OksObject;

    public:

      bool get_use_nested_lookup() const { return p_use_nested_lookup; }
      const std::list<std::string>& get_rel_names() const { return p_rel_names; }
      const QueryPathExpression * get_next() const { return p_next; }

    protected:

      QueryPathExpression(bool v) : p_use_nested_lookup(v) { }
      QueryPathExpression(const std::string& expression);

      ~QueryPathExpression() {delete p_next;}

      bool p_use_nested_lookup;
      std::list<std::string> p_rel_names;
      QueryPathExpression * p_next;

  };



    /**
     *  Class QueryPath describes special type of query to calculate path (i.e list of objects)
     *  between two given objects. The use case is to get a path in several trees using the same
     *  leave objects. Note for composite objects and exclusive relationships, the usage of 
     *  reverse composite relationships is more effective. In such case there is the only tree
     *  built on top of given leaves.
     *
     *  \par Example
     *
     *  The example of query is shown below:
     *    "(path-to "my-id@my-class" (direct "A" "B" (nested "N" (direct "X" "Y" "Z"))))"
     *
     *  The destination object is "my-id@my-class". The search can be started from any object of any class.
     *  In our example the start object has to have two relationships named "A" and "B".
     *  An object referenced via "A" and "B" should have relationship "N". In our example
     *  it is possible to lookup for path via nested objects linked via relationship "N".
     *  Finally all objects referenced via "N" should have relationships "X", "Y" and "Z".
     *  If the destination object is referenced by them, the path is found. The result of path
     *  query execution is list of objects between the start and the destination object.
     */


  class QueryPath
  {

    public:

      QueryPath(const OksObject * o, QueryPathExpression * qpe) : p_goal(o), p_start(qpe) { }
      QueryPath(const std::string& query, const OksKernel&);
      ~QueryPath() {delete p_start;}

      const QueryPathExpression * get_start_expression() const { return p_start; }
      const OksObject * get_goal_object() const { return p_goal; }

    private:

      const OksObject * p_goal;
      QueryPathExpression * p_start;

  };


}

std::ostream& operator<<(std::ostream&, const oks::QueryPathExpression&);
std::ostream& operator<<(std::ostream&, const oks::QueryPath&);

#endif
```

### `src/query.cpp`  
*Local path: `repo/oks/src/query.cpp`*

```cpp
#define _OksBuildDll_

#include <oks/query.h>
#include <oks/attribute.h>
#include <oks/relationship.h>
#include <oks/class.h>
#include <oks/object.h>
#include <oks/kernel.h>
#include <oks/index.h>
#include <oks/profiler.h>

#include <stdexcept>
#include <sstream>

const char * OksQuery::OR = "or";
const char * OksQuery::AND = "and";
const char * OksQuery::NOT = "not";
const char * OksQuery::SOME = "some";
const char * OksQuery::THIS_CLASS = "this";
const char * OksQuery::ALL_SUBCLASSES = "all";
const char * OksQuery::OID = "object-id";
const char * OksQuery::EQ = "=";
const char * OksQuery::NE = "!=";
const char * OksQuery::RE = "~=";
const char * OksQuery::LE = "<=";
const char * OksQuery::GE = ">=";
const char * OksQuery::LS = "<";
const char * OksQuery::GT = ">";
const char * OksQuery::PATH_TO = "path-to";
const char * OksQuery::DIRECT = "direct";
const char * OksQuery::NESTED = "nested";

namespace oks {

  std::string
  QueryFailed::fill(const OksQueryExpression& query, const OksClass& c, const std::string& reason) noexcept
  {
    std::ostringstream text;
    text << "query \"" << query << "\" in class \"" << c.get_name() << "\" failed:\n" << reason;
    return text.str();
  }

  std::string
  BadReqExp::fill(const std::string& what, const std::string& reason) noexcept
  {
    return std::string("failed to create reqular expression \"") + what + "\": " + reason;
  }

}

bool OksQuery::equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 == *d2);}
bool OksQuery::not_equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 != *d2);}
bool OksQuery::less_or_equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 <= *d2);}
bool OksQuery::greater_or_equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 >= *d2);}
bool OksQuery::less_cmp(const OksData *d1, const OksData *d2) {return (*d1 < *d2);}
bool OksQuery::greater_cmp(const OksData *d1, const OksData *d2) {return (*d1 > *d2);}
bool OksQuery::reg_exp_cmp(const OksData *d, const OksData * re) {
  return boost::regex_match(d->str(), *reinterpret_cast<const boost::regex *>(re));
}


void OksComparator::SetValue(OksData *v)
{
  delete value;
  value = v;
  
  clean_reg_exp();
}

void OksComparator::clean_reg_exp()
{
  if(m_reg_exp) {
    delete m_reg_exp;
    m_reg_exp = 0;
  }
}


inline void erase_empty_chars(std::string& s)
{
  while(s[0] == ' ' || s[0] == '\n' || s[0] == '\t') s.erase(0, 1);
}


OksQuery::OksQuery(const OksClass *c, const std::string & str) : p_expression (0), p_status (1)
{
  OSK_PROFILING(OksProfiler::fStringToQuery, c->get_kernel())

  const char * fname = "OksQuery::OksQuery(OksClass *, const char *)";
  const char * error_str = "Can't create query ";

  char delimiter = '\0';

  if(!c) {
    Oks::error_msg(fname) << error_str << "without specified class\n";
    return;
  }

  if(str.empty()) {
    Oks::error_msg(fname) << error_str << "from empty string\n";
    return;
  }

  std::string s(str);
  
  erase_empty_chars(s);

  if(s.empty()) {
    Oks::error_msg(fname) << error_str << "from string which consists of space symbols\n";
    return;
  }

  if(s[0] == '(') {
    s.erase(0, 1);
    delimiter = ')';
  }
  		
  std::string::size_type p = s.find(' ');
	
  if(p == std::string::npos) {
    Oks::error_msg(fname)
      << "Can't parse query expression \"" << str << "\"\n"
         "it must consists of as minimum two tokens separated by space\n";
    return;
  }
  
  if(s.substr(0, p) == OksQuery::ALL_SUBCLASSES)
    p_sub_classes = true;
  else if(s.substr(0, p) == OksQuery::THIS_CLASS)
    p_sub_classes = false;
  else {
    Oks::error_msg(fname)
      << "Can't parse query expression \"" << str << "\"\n"
         "the first token must be \'"<< OksQuery::ALL_SUBCLASSES
      << "\' or \'"<< OksQuery::THIS_CLASS << "\'\n";
    return;
  }

  s.erase(0, p + 1);

  if(delimiter == ')') {
    p = s.rfind(delimiter);
    if(p == std::string::npos) {
      Oks::error_msg(fname)
        << "Can't parse query expression \"" << str << "\"\n"
           "it must contain closing bracket \')\' if it has opening bracket \'(\'\n";
      return;
    }

    s.erase(p);
  }

  
  erase_empty_chars(s);


  if(s[0] == '(') {
    p = s.rfind(')');

    if(p == std::string::npos) {
      Oks::error_msg(fname)
        << "Can't parse query expression \"" << s << "\"\n"
           "it must contain closing bracket \')\' if it has opening bracket \'(\'\n";
      return;
    }

    s.erase(p);
    s.erase(0, 1);

    p_expression = create_expression(c, s);
 	
    if(p_expression) p_status = 0;
  }
  else
    Oks::error_msg(fname)
      << "Can't parse subquery expression \"" << s << "\"\n"
         "it must be enclosed by brackets\n";
}


OksQueryExpression *
OksQuery::create_expression(const OksClass *c, const std::string & str)
{
  const char * fname = "OksQuery::create_expression()";

  OSK_PROFILING(OksProfiler::fStringToQueryExpression, c->get_kernel())

  OksQueryExpression *qe = 0;

  if(!c) {
    Oks::error_msg(fname) << "Can't create query without specified class\n";
    return qe;
  }

  if(str.empty()) {
    Oks::error_msg(fname) << "Can't create query from empty string\n";
    return qe;
  }

  std::string s(str);

  std::list<std::string> slist;

  while(s.length()) {
    erase_empty_chars(s);

    if(!s.length()) break;	

    if(
     s[0] == '\"' ||
     s[0] == '\'' ||
     s[0] == '`'
    ) {
      char delimiter = s[0];
      s.erase(0, 1);

      std::string::size_type p = s.find(delimiter);

      if(p == std::string::npos) {
        Oks::error_msg(fname)
          << "Can't parse query expression \"" << str << "\"\n"
             "the delimiter is \' "<< delimiter << " \'\n"
             "the rest of the expression is \"" << s << "\"\n";
        return qe;
      }

      s.erase(p, 1);
      slist.push_back(std::string(s, 0, p));

      s.erase(0, p + 1);
    }
    else if(s[0] == '(') {
      std::string::size_type p = 1;
      size_t strLength = s.length();
      size_t r = 1;
		
      while(p < strLength) {
        if(s[p] == '(') r++;
        if(s[p] == ')') {
          r--;
          if(!r) break;
        }
        p++;
      }

      if(r) {
        Oks::error_msg(fname)
          << "Can't parse query expression \"" << str << "\"\n"
          << "There is no closing \')\' for " << '\"' << s << "\"\n";
        return qe;
      }

      s.erase(p, 1);
      s.erase(0, 1);

      slist.push_back(std::string(s, 0, p - 1));

      s.erase(0, p - 1);
    }
    else {
      std::string::size_type p = 0;
      size_t strLength = s.length();
		
      while(p < strLength && s[p] != ' ') p++;
		
      slist.push_back(std::string(s, 0, p));
		
      s.erase(0, p);
    }
  }
  
  if(slist.empty()) {
    Oks::error_msg(fname)
      << "Can't create query from empty string \"" << str << "\"\n";
    return qe;
  }

  const std::string first = slist.front();
  slist.pop_front();

  if(
   first == OksQuery::AND ||
   first == OksQuery::OR
  ) {
    if(slist.size() < 2) {
      Oks::error_msg(fname) << "\'" << first << "\' must have two or more arguments: (" << str << ")'\n";
      return qe;
    }

    qe = (
      (first == OksQuery::AND)
        ? (OksQueryExpression *)new OksAndExpression()
        : (OksQueryExpression *)new OksOrExpression()
    );

    while(!slist.empty()) {
      const std::string item2 = slist.front();
      slist.pop_front();

      OksQueryExpression *qe2 = create_expression(c, item2);

      if(qe2) {
        if(first == OksQuery::AND) 
          ((OksAndExpression *)qe)->add(qe2);
        else
          ((OksOrExpression *)qe)->add(qe2);
      }
    }

    return qe;	/* SUCCESS */
  }
  else if(first == OksQuery::NOT) {
    if(slist.size() != 1) {
      Oks::error_msg(fname) << "\'" << first << "\' must have exactly one argument: (" << str << ")\n";
      return qe;
    }

    qe = (OksQueryExpression *)new OksNotExpression();

    const std::string item2 = slist.front();
    slist.pop_front();

    OksQueryExpression *qe2 = create_expression(c, item2);

    if(qe2) ((OksNotExpression *)qe)->set(qe2);

    return qe;	/* SUCCESS */
  }
  else if(slist.size() != 2) {
    Oks::error_msg(fname) << "Can't parse query expression \"" << str << "\"\n";
    return qe;
  }
  else {
    const std::string second = slist.front();
    slist.pop_front();

    const std::string third = slist.front();
    slist.pop_front();
	
    if(second == OksQuery::SOME || second == OksQuery::ALL_SUBCLASSES) {
      OksRelationship *r = c->find_relationship(first);
		
      if(!r) {
        Oks::error_msg(fname)
          << "For expression \"" << str << "\"\n"
             "can't find relationship \"" << first << "\" in class \"" << c->get_name() << "\"\n";

        return qe;
      }

      bool b;

      if(second == OksQuery::SOME) b = false;
      else if(second == OksQuery::ALL_SUBCLASSES) b = true;
      else {
        Oks::error_msg(fname)
          << "For relationship expression \"" << str << "\"\n"
              "second parameter \'" << second << "\' must be \'" << *OksQuery::SOME
	  << "\' or \'" << *OksQuery::ALL_SUBCLASSES << "\'\n";
        return qe;
      }

      OksClass *relc = c->get_kernel()->find_class(r->get_type());

      if(!relc) {
        Oks::error_msg(fname)
          << "For expression \"" << str << "\"\n"
          << "can't find class \"" << r->get_type() << "\"\n";
        return qe;
      }

      OksQueryExpression *qe2 = create_expression(relc, third);

      if(qe2) qe = (OksQueryExpression *)new OksRelationshipExpression(r, qe2, b);

      return qe;	/* SUCCESS */
    }
    else {
      OksAttribute *a = ((first != OksQuery::OID) ? c->find_attribute(first) : 0);
		
      if(first != OksQuery::OID && !a) {
        Oks::error_msg(fname)
          << "For expression \"" << str << "\"\n"
          << "can't find attribute \"" << first << "\" in class \""
	  << c->get_name() << "\"\n";
        return qe;
      }

      OksData * d = new OksData();

      OksQuery::Comparator f = (
        (third == OksQuery::EQ) ? OksQuery::equal_cmp :
        (third == OksQuery::NE) ? OksQuery::not_equal_cmp :
        (third == OksQuery::RE) ? OksQuery::reg_exp_cmp :
        (third == OksQuery::LE) ? OksQuery::less_or_equal_cmp :
        (third == OksQuery::GE) ? OksQuery::greater_or_equal_cmp :
        (third == OksQuery::LS) ? OksQuery::less_cmp :
        (third == OksQuery::GT) ? OksQuery::greater_cmp :
        0
      );

      if(a) {
        if(f == OksQuery::reg_exp_cmp) {
	  d->type = OksData::string_type;
	  d->data.STRING = new OksString(second);
        }
        else {
          d->type = OksData::unknown_type;
          d->SetValues(second.c_str(), a);
        }
      }
      else {
        d->Set(second);
      }

      if(!f)
        Oks::error_msg(fname)
          << "For expression \"" << str << "\"\n"
          << "can't find comparator function \"" << third << "\"\n";
      else
        qe = (OksQueryExpression *)new OksComparator(a, d, f);

      return qe;	/* (UN)SUCCESS */
    }
  }
}



OksObject::List *
OksClass::execute_query(OksQuery *qe) const
{
  const char * fname = "OksClass::execute_query()";

  OSK_PROFILING(OksProfiler::Classexecute_query, p_kernel)

  
  OksObject::List * olist = 0;
  OksQueryExpression *sqe = qe->get();
  
  if(sqe->CheckSyntax() == false) {
    Oks::error_msg(fname) << "Can't execute query \"" << *sqe << "\"\n";
    return 0;
  }

  if(p_objects && !p_objects->empty()) {
    bool indexedSearch = false;
  	
    if(p_indices) {
      if(sqe->type() == OksQuery::comparator_type) {
        OksComparator *cq = (OksComparator *)sqe;
	OksIndex::Map::iterator j = p_indices->find(cq->GetAttribute());
	
        if(j != p_indices->end()) {
          indexedSearch = true;
          olist = (*j).second->find_all(cq->GetValue(), cq->GetFunction());
        }
      }
      else if(
       (sqe->type() == OksQuery::and_type) ||
       (sqe->type() == OksQuery::or_type)
      ) {
        std::list<OksQueryExpression *> * qlist = &((OksListBaseQueryExpression *)sqe)->p_expressions;
        OksQueryExpression *q1, *q2;
        OksComparator *cq1 = 0, *cq2 = 0;
			
        if(
         (qlist->size() == 2) &&
         ((q1 = qlist->front())->type() == OksQuery::comparator_type) &&
         ((q2 = qlist->back())->type() == OksQuery::comparator_type) &&
         ((cq1 = (OksComparator *)q1) != 0) &&
         ((cq2 = (OksComparator *)q2) != 0) &&
         (cq1->GetAttribute() == cq2->GetAttribute())
        ) {
	  OksIndex::Map::iterator j = p_indices->find(cq1->GetAttribute());
				
          if(j != p_indices->end()) {
            indexedSearch = true;

            olist = (*j).second->find_all(
              ((sqe->type() == OksQuery::and_type) ? true : false),
              cq1->GetValue(),
              cq1->GetFunction(),
              cq2->GetValue(),
              cq2->GetFunction()
            );
          }
        }
      }
    }
	
    if(indexedSearch == false) {
      for(OksObject::Map::iterator i = p_objects->begin(); i != p_objects->end(); ++i) {
        OksObject *o = (*i).second;

        try {
          if(o->SatisfiesQueryExpression(sqe) == true) {
            if(!olist) olist = new OksObject::List();
            olist->push_back(o);
          }
        }
        catch(oks::exception& ex) {
          throw oks::QueryFailed(*sqe, *this, ex);
        }
        catch(std::exception& ex) {
          throw oks::QueryFailed(*sqe, *this, ex.what());
        }
      }
    }
  }


  if(qe->search_in_subclasses() == true && p_all_sub_classes && !p_all_sub_classes->empty()) {
    for(OksClass::FList::iterator i = p_all_sub_classes->begin(); i != p_all_sub_classes->end(); ++i) {
      OksClass *c = *i;

      if(c->p_objects && !c->p_objects->empty()) {
        for(OksObject::Map::iterator i2 = c->p_objects->begin(); i2 != c->p_objects->end(); ++i2) {
          OksObject *o = (*i2).second;

          try {
            if(o->SatisfiesQueryExpression(sqe) == true) {
              if(!olist) olist = new OksObject::List();
              olist->push_back(o);
            }
          }
          catch(oks::exception& ex) {
            throw oks::QueryFailed(*sqe, *this, ex);
          }
          catch(std::exception& ex) {
            throw oks::QueryFailed(*sqe, *this, ex.what());
          }
        }
      }
    }
  }

  return olist;
}


bool
OksQueryExpression::CheckSyntax() const
{
  const char * fname = "OksQueryExpression::CheckSyntax()";

  switch(p_type) {
    case OksQuery::comparator_type:
      if(!((OksComparator *)this)->attribute && !((OksComparator *)this)->value) {
      	Oks::error_msg(fname)
          << "OksComparator: Can't execute query for nil attribute or nil object-id\n";
      	return false;
      }
      else if(!((OksComparator *)this)->m_comp_f) {
      	Oks::error_msg(fname)
          << "OksComparator: Can't execute query for nil compare function\n";
      	return false;
      }

      return true;

    case OksQuery::relationship_type:
      if(!((OksRelationshipExpression *)this)->relationship) {
      	Oks::error_msg(fname)
          << "OksRelationshipExpression: Can't execute query for nil relationship\n";
      	return false;
      }
      else if(!((OksRelationshipExpression *)this)->p_expression) {
      	Oks::error_msg(fname)
          << "OksRelationshipExpression: Can't execute query for nil query expression\n";
      	return false;
      }
      else
      	return (((OksRelationshipExpression *)this)->p_expression)->CheckSyntax();

    case OksQuery::not_type:
      if(!((OksNotExpression *)this)->p_expression) {
      	Oks::error_msg(fname)
          << "OksNotExpression: Can't execute \'not\' for nil query expression\n";
      	return false;
      }
      
      return (((OksNotExpression *)this)->p_expression)->CheckSyntax();

    case OksQuery::and_type:
      if(((OksAndExpression *)this)->p_expressions.size() < 2) {
      	Oks::error_msg(fname)
          << "OksAndExpression: Can't execute \'and\' for "
          << ((OksAndExpression *)this)->p_expressions.size() << " argument\n"
             "Two or more arguments are required\n";
      	return false;
      }
      else {
        std::list<OksQueryExpression *> & elist = ((OksAndExpression *)this)->p_expressions;
      	
      	for(std::list<OksQueryExpression *>::iterator i = elist.begin(); i != elist.end(); ++i)
          if((*i)->CheckSyntax() == false) return false;
      	
      	return true;
      }

    case OksQuery::or_type:
      if(((OksOrExpression *)this)->p_expressions.size() < 2) {
      	Oks::error_msg(fname)
          << "OksOrExpression: Can't execute \'or\' for "
          << ((OksOrExpression *)this)->p_expressions.size() << " argument\n"
             "Two or more arguments are required\n";
	
      	return false;
      }
      else {
        std::list<OksQueryExpression *> & elist = ((OksOrExpression *)this)->p_expressions;

      	for(std::list<OksQueryExpression *>::iterator i = elist.begin(); i != elist.end(); ++i)
          if((*i)->CheckSyntax() == false) return false;
      	
      	return true;
      }
	
    default:
      Oks::error_msg(fname)
        << "Unexpected query type " << (int)p_type << std::endl;

      return false;
  }
}


bool
OksObject::SatisfiesQueryExpression(OksQueryExpression *qe) const
{
  OSK_PROFILING(OksProfiler::ObjectSatisfiesQueryExpression, uid.class_id->p_kernel)

  if(!qe) {
    throw std::runtime_error("cannot execute nil query");
  }

  switch(qe->type()) {
    case OksQuery::comparator_type: {
      OksComparator *cmp = (OksComparator *)qe;
      const OksAttribute *a = cmp->attribute;
      OksQuery::Comparator f = cmp->m_comp_f;

      if(!a && !cmp->value) {
        throw std::runtime_error("cannot execute query for nil attribute");
      }
      else if(!f) {
        throw std::runtime_error("cannot execute query for nil compare function");
      }

      const OksData * cmp_value(cmp->value);

      if(f == OksQuery::reg_exp_cmp) { 
        if(!cmp->m_reg_exp) {
          try {
            std::string s(cmp->value->str());
            cmp->m_reg_exp = new boost::regex(s.c_str());
          }
          catch(std::exception& ex) {
            throw oks::BadReqExp(cmp->value->str(), ex.what());
          }
	}
	cmp_value = reinterpret_cast<const OksData *>(cmp->m_reg_exp);
      }

      if(!a) {
        OksData d(GetId());
	return (*f)(&d, cmp_value);
      }

      return (*f)(
        &(data[(*(uid.class_id->p_data_info->find(a->get_name()))).second->offset]),
        cmp_value
      );
    }

    case OksQuery::relationship_type:
      if(!((OksRelationshipExpression *)qe)->relationship) {
        throw std::runtime_error("cannot execute query for nil relationship");
      }
      else {
        OksData *d = &data[((*(uid.class_id->p_data_info->find(((OksRelationshipExpression *)qe)->relationship->get_name()))).second)->offset];

        if(((OksRelationshipExpression *)qe)->relationship->get_high_cardinality_constraint() == OksRelationship::Many) {
          if(!d->data.LIST || d->data.LIST->empty()) return false;

          for(OksData::List::iterator i = d->data.LIST->begin(); i != d->data.LIST->end(); ++i) {
            OksData *d2 = (*i);

            if(d2->type == OksData::uid2_type) {
              std::ostringstream text;
              text << "cannot process relationship expression: object \"" << *d2->data.UID2.object_id << '@' << *d2->data.UID2.class_id
                   << "\" referenced through multi values relationship \"" << ((OksRelationshipExpression *)qe)->relationship->get_name()
                   << "\" is not loaded in memory";
              throw std::runtime_error(text.str().c_str());
            }

            if(((OksRelationshipExpression *)qe)->checkAllObjects == true) {
              if(
               !d2->data.OBJECT ||
               d2->data.OBJECT->SatisfiesQueryExpression(((OksRelationshipExpression *)qe)->p_expression) == false
              ) return false;
            }
            else {
              if(
               d2->data.OBJECT &&
               d2->data.OBJECT->SatisfiesQueryExpression(((OksRelationshipExpression *)qe)->p_expression) == true
              ) return true;
            }
          }
			
          return (((OksRelationshipExpression *)qe)->checkAllObjects == true) ? true : false;
        }
        else {
          if(d->type != OksData::object_type) {
            std::ostringstream text;
            text << "cannot process relationship expression: object \"" << *d << "\" referenced through single value relationship \""
                 << ((OksRelationshipExpression *)qe)->relationship->get_name() << "\" is not loaded in memory";
            throw std::runtime_error(text.str().c_str());
          }

          return (
            d->data.OBJECT
	      ? d->data.OBJECT->SatisfiesQueryExpression(((OksRelationshipExpression *)qe)->p_expression)
	      : false
          );
        }
      }

    case OksQuery::not_type:
      if(!((OksNotExpression *)qe)->p_expression) {
        throw std::runtime_error("cannot process \'not\' expression: referenced query expression is nil");
      }

      return (SatisfiesQueryExpression(((OksNotExpression *)qe)->p_expression) ? false : true);

    case OksQuery::and_type:
      if(((OksAndExpression *)qe)->p_expressions.size() < 2) {
        std::ostringstream text;
        text << "cannot process \'and\' expression for " << ((OksAndExpression *)qe)->p_expressions.size()
             << " argument (two or more arguments are required)";
        throw std::runtime_error(text.str().c_str());
      }
      else {
        std::list<OksQueryExpression *> & elist = ((OksAndExpression *)qe)->p_expressions;

        for(std::list<OksQueryExpression *>::iterator i = elist.begin(); i != elist.end();++i)
          if(SatisfiesQueryExpression(*i) == false) return false;

        return true;
      }

    case OksQuery::or_type:
      if(((OksOrExpression *)qe)->p_expressions.size() < 2) {
        std::ostringstream text;
        text << "cannot process \'or\' expression for " << ((OksAndExpression *)qe)->p_expressions.size()
             << " argument (two or more arguments are required)";
        throw std::runtime_error(text.str().c_str());
      }
      else {
        std::list<OksQueryExpression *> & elist = ((OksOrExpression *)qe)->p_expressions;

        for(std::list<OksQueryExpression *>::iterator i = elist.begin(); i != elist.end();++i)
          if(SatisfiesQueryExpression(*i) == true) return true;

        return false;
      }

    default: {
      std::ostringstream text;
      text << "unexpected query type " << (int)(qe->type());
      throw std::runtime_error(text.str().c_str());
    }
  }
}


std::ostream&
operator<<(std::ostream& s, const OksQueryExpression& qe)
{
  s << '(';
  
  switch(qe.type()) {
    case OksQuery::comparator_type: {
      OksComparator *cmpr = (OksComparator *)&qe;
      const OksAttribute *a = cmpr->GetAttribute();
      OksData *v = cmpr->GetValue();
      OksQuery::Comparator f = cmpr->GetFunction();

      if(a) {
        s << '\"' << a->get_name() << "\" ";
      }
      else if(v) {
        s << OksQuery::OID << ' ';
      }
      else {
        s << "(null) ";
      }

      if(v) {
        s << *v << ' ';
      }
      else {
        s << "(null) ";
      }

      if(f) {
        if(f == OksQuery::equal_cmp) s << OksQuery::EQ;
        else if(f == OksQuery::not_equal_cmp) s << OksQuery::NE;
        else if(f == OksQuery::reg_exp_cmp) s << OksQuery::RE;
        else if(f == OksQuery::less_or_equal_cmp) s << OksQuery::LE;
        else if(f == OksQuery::greater_or_equal_cmp) s << OksQuery::GE;
        else if(f == OksQuery::less_cmp) s << OksQuery::LS;
        else if(f == OksQuery::greater_cmp) s << OksQuery::GT;
      }
      else
        s << "(null)";

      break; }

    case OksQuery::relationship_type: {
      OksRelationshipExpression *re = (OksRelationshipExpression *)&qe;
      const OksRelationship *r = re->GetRelationship();
      bool b = re->IsCheckAllObjects();
      OksQueryExpression *rqe = re->get();

      if(r)
        s << '\"' << r->get_name() << "\" ";
      else
        s << "(null) ";

      s << (b == true ? OksQuery::ALL_SUBCLASSES : OksQuery::SOME) << ' ';

      if(rqe) s << *rqe;
      else s << "(null)";

      break; }

    case OksQuery::not_type:
      s << OksQuery::NOT << ' ' << *(((OksNotExpression *)&qe)->get());

      break;

    case OksQuery::and_type: {
      s << OksQuery::AND << ' ';

      const std::list<OksQueryExpression *> & elist = ((OksAndExpression *)&qe)->expressions();

      if(!elist.empty()) {
        const OksQueryExpression * last = elist.back();

        for(std::list<OksQueryExpression *>::const_iterator i = elist.begin(); i != elist.end(); ++i) {
          s << *(*i);
          if(*i != last) s << ' ';
        }
      }

      break;
    }

    case OksQuery::or_type: {
      s << OksQuery::OR << ' ';

      const std::list<OksQueryExpression *> & elist = ((OksOrExpression *)&qe)->expressions();

      if(!elist.empty()) {
        const OksQueryExpression * last = elist.back();

        for(std::list<OksQueryExpression *>::const_iterator i = elist.begin(); i != elist.end(); ++i) {
          s << *(*i);
          if(*i != last) s << ' ';
        }
      }

      break;
    }

    case OksQuery::unknown_type: {
      s << "(unknown)";

      break;
    }
  }

  s << ')';

  return s;
}


std::ostream&
operator<<(std::ostream& s, const OksQuery& gqe)
{
  s << '('
    << (gqe.p_sub_classes ? OksQuery::ALL_SUBCLASSES : OksQuery::THIS_CLASS)
    << ' ';

  if(gqe.p_expression)
    s << *gqe.p_expression;
  else
    s << "(null)";

  s << ')';

  return s;
}


std::ostream&
operator<<(std::ostream& s, const oks::QueryPath& query)
{
  s << '(' << OksQuery::PATH_TO << ' ' << query.get_goal_object() << ' ' << *query.get_start_expression() << ')';
  return s;
}


std::ostream&
operator<<(std::ostream& s, const oks::QueryPathExpression& e)
{
  s << '(' << (e.get_use_nested_lookup() ? OksQuery::NESTED : OksQuery::DIRECT) << ' ';

  for(std::list<std::string>::const_iterator i = e.get_rel_names().begin(); i != e.get_rel_names().end(); ++i) {
    if(i != e.get_rel_names().begin()) s << ' ';
    s << '\"' << *i << '\"';
  }

  if(e.get_next()) s << ' ' << *(e.get_next());

  s << ')';

  return s;
}


OksObject::List *
OksObject::find_path(const oks::QueryPath& query) const
{
  OksObject::List * path = new OksObject::List();
  
  if(satisfies(query.get_goal_object(), *query.get_start_expression(), *path) == false) {
    delete path;
    path = 0;
  }

  return path;
}


bool
OksObject::satisfies(const OksObject * goal, const oks::QueryPathExpression& expression, OksObject::List& path) const
{
    // check the object is not in the path

  {
    for(std::list<OksObject *>::const_iterator i = path.begin(); i != path.end(); ++i) {
      if(*i == this) return false;
    }
  }

  path.push_back(const_cast<OksObject *>(this));


  for(std::list<std::string>::const_iterator i = expression.get_rel_names().begin(); i != expression.get_rel_names().end(); ++i) {
    OksData * d = 0;

    if(!(*i).empty() && (*i)[0] == '?') {
      std::string nm = (*i).substr(1);
      OksDataInfo::Map::iterator i = uid.class_id->p_data_info->find(nm);

      if(i != uid.class_id->p_data_info->end()) {
        d = GetRelationshipValue((*i).second);
      }
      else {
        continue;
      }
    }
    else {
      try {
        d = GetRelationshipValue(*i);
      }
      catch(oks::exception& ex) {
        Oks::error_msg("OksObject::satisfies") << ex.what() << std::endl;
        continue;
      }
    }

      // check if given relationship points to destination object

    if(d->type == OksData::object_type && d->data.OBJECT == goal) return true;
    else if(d->type == OksData::list_type && d->data.LIST) {
      for(OksData::List::iterator i2 = d->data.LIST->begin(); i2 != d->data.LIST->end(); ++i2) {
        OksData * d2 = (*i2);
        if(d2->type == OksData::object_type && d2->data.OBJECT == goal) return true;
      }
    }


      // go to next path, if there are no more expressions

    if(!expression.get_next()) {
      continue;
    }


      // check, if there is need for nested path lookup

    else if(expression.get_use_nested_lookup()) {

        // go directly

      path.pop_back();
      if(satisfies(goal, *expression.get_next(), path) == true) return true;
      path.push_back(const_cast<OksObject *>(this));

        // go nested

      if(d->type == OksData::object_type && d->data.OBJECT) {
        if(d->data.OBJECT->satisfies(goal, expression, path) == true) return true;
      }
      else if(d->type == OksData::list_type && d->data.LIST) {
        for(OksData::List::iterator i2 = d->data.LIST->begin(); i2 != d->data.LIST->end(); ++i2) {
          OksData * d2 = (*i2);
          if(d2->type == OksData::object_type && d2->data.OBJECT) {
            if(d2->data.OBJECT->satisfies(goal, expression, path) == true) return true;
	  }
        }
      }
    }

    else {
      if(d->type == OksData::object_type && d->data.OBJECT) {
        if(d->data.OBJECT->satisfies(goal, *expression.get_next(), path) == true) return true;
      }
      else if(d->type == OksData::list_type && d->data.LIST) {
        for(OksData::List::iterator i2 = d->data.LIST->begin(); i2 != d->data.LIST->end(); ++i2) {
          OksData * d2 = (*i2);
          if(d2->type == OksData::object_type && d2->data.OBJECT) {
            if(d2->data.OBJECT->satisfies(goal, *expression.get_next(), path) == true) return true;
	  }
        }
      }
    }
  }

  path.pop_back();
  return false;
}

oks::QueryPath::QueryPath(const std::string& str, const OksKernel& kernel) : p_start(0)
{
  std::string s(str);
  erase_empty_chars(s);

  if(s.empty()) {
    throw oks::bad_query_syntax( "Empty query" );
  }

  if(s[0] == '(') {
    std::string::size_type p = s.rfind(')');

    if(p == std::string::npos) {
      throw oks::bad_query_syntax(std::string("Query expression \'") + str + "\' must contain closing bracket");
    }

    s.erase(p);
    s.erase(0, 1);
  }
  else {
    throw oks::bad_query_syntax(std::string("Query expression \'") + str + "\' must be enclosed by brackets");
  }

  erase_empty_chars(s);

  Oks::Tokenizer t(s, " \t\n");
  std::string token;
  t.next(token);

  if(token != OksQuery::PATH_TO) {
    throw oks::bad_query_syntax(std::string("Expression \'") + s + "\' must start from " + OksQuery::DIRECT + " or " + OksQuery::NESTED + " keyword");
  }

  s.erase(0, token.size());
  erase_empty_chars(s);
  
  if( s[0] == '\"' ) {
    std::string::size_type p = s.find('\"', 1);

    if(p == std::string::npos) {
      throw oks::bad_query_syntax(std::string("No trailing delimiter of object name in query \'") + str + "\'");
    }

    std::string::size_type p2 = s.find('@');

    if(p2 == std::string::npos || p2 > p) {
      throw oks::bad_query_syntax(std::string("Bad format of object name ") + s.substr(0, p+1) + " in query \'" + str + "\'");
    }

    std::string object_id = std::string(s, 1, p2 - 1);
    std::string class_name = std::string(s, p2 + 1, p - p2 - 1);

    if(OksClass * c = kernel.find_class(class_name)) {
      if((p_goal = c->get_object(object_id)) == 0) {
        throw oks::bad_query_syntax(std::string("Cannot find object ") + s.substr(0, p+1) + " in query \'" + str + "\': no such object");
      }
    }
    else {
      throw oks::bad_query_syntax(std::string("Cannot find object ") + s.substr(0, p+1) + " in query \'" + str + "\': no such class");
    }

    s.erase(0, p + 1);
  }
  else {
    throw oks::bad_query_syntax(std::string("No name of object in \'") + str + "\'");
  }

  try {
    p_start = new QueryPathExpression(s);
  }
  catch ( oks::bad_query_syntax& e ) {
    throw oks::bad_query_syntax(std::string("Failed to parse expression \'") + str + "\' because \'" + e.what() + "\'");
  }
}

oks::QueryPathExpression::QueryPathExpression(const std::string& str) : p_next(0)
{
  std::string s(str);
  erase_empty_chars(s);

  if(s.empty()) {
    throw oks::bad_query_syntax( "Empty expression" );
  }

  if(s[0] == '(') {
    std::string::size_type p = s.rfind(')');

    if(p == std::string::npos) {
      throw oks::bad_query_syntax(std::string("Expression \'") + str + "\' must contain closing bracket");
    }

    s.erase(p);
    s.erase(0, 1);

      // build nested expression if any

    std::string::size_type p1 = s.find('(');

    if(p1 != std::string::npos) {
      std::string::size_type p2 = s.rfind(')');

      if(p2 == std::string::npos) {
        throw oks::bad_query_syntax(std::string("Nested expression of \'") + str + "\' must contain closing bracket");
      }

      p_next = new QueryPathExpression(s.substr(p1, p2));
      
      s.erase(p1, p2);
    }

    erase_empty_chars(s);

    Oks::Tokenizer t(s, " \t\n");
    std::string token;
    t.next(token);

    if(token == OksQuery::DIRECT) {
      p_use_nested_lookup = false;
    }
    else if(token == OksQuery::NESTED) {
      p_use_nested_lookup = true;
    }
    else {
      delete p_next; p_next = 0;
      throw oks::bad_query_syntax(std::string("Expression \'") + s + "\' must start from " + OksQuery::DIRECT + " or " + OksQuery::NESTED + " keyword");
    }

    s.erase(0, token.size());

    while(s.length()) {
      erase_empty_chars(s);

      if(!s.length()) break;	

      if( s[0] == '\"' || s[0] == '\'' || s[0] == '`' ) {
        char delimiter = s[0];

        p = s.find(delimiter, 1);

        if(p == std::string::npos) {
          delete p_next; p_next = 0;
          throw oks::bad_query_syntax(std::string("No trailing delimiter of \'") + s + "\' (expression \'" + str + "\')");
        }

        p_rel_names.push_back(std::string(s, 1, p-1));

        s.erase(0, p + 1);
      }
      else {
        delete p_next; p_next = 0;
        throw oks::bad_query_syntax(std::string("Name of relationship \'") + s + "\' must start from a delimiter (expression \'" + str + "\')");
      }
    }

    if(p_rel_names.empty()) {
      delete p_next; p_next = 0;
      throw oks::bad_query_syntax(std::string("An expression of \'") + str + "\' has no relationship names defined");
    }
  }
  else {
    throw oks::bad_query_syntax(std::string("Expression \'") + str + "\' must be enclosed by brackets");
  }
}
```

### GIT repository utilities and scripts
`bin/oks_git_repository.cpp` prints `OksKernel::get_repository_root()` (i.e. the `TDAQ_DB_REPOSITORY` value); `bin/oks_clone_repository.cpp` clones an OKS config GIT repository; `bin/oks_dump.cpp` and `bin/oks_validate_repository.cpp` walk/validate the OKS files of a repository working area. The `scripts/oks-*.sh` shell scripts wrap git operations for OKS config databases: checkout, commit, copy, diff, edit-branch, import, log, status, tag, update, version.
### `bin/oks_clone_repository.cpp`  
*Local path: `repo/oks/bin/oks_clone_repository.cpp`*

```cpp
/**
 *  \file oks_clone_repository.cpp
 *
 *  This file is part of the OKS package.
 *  Author: <Igor.Soloviev@cern.ch>
 */

#include <oks/kernel.h>

#include <string.h>
#include <stdlib.h>

#include <boost/program_options.hpp>

int
main(int argc, char **argv)
{
  std::string config_version, user_dir, branch_name;
  bool verbose = false;

  try
    {
      boost::program_options::options_description desc("Clone and checkout oks repository.\n\n"
          "By default the master branch is checkout. The \"branch\" command line option can be used to specify particular one. A branch will be created, if does not exist yet.\n"
          "TDAQ_DB_VERSION process environment variable or \"version\" command line option can be used to specify particular version.\n"
          "The output directory can be specified via command line, otherwise temporal directory will be created and its name will be reported.\n"
          "If TDAQ_DB_USER_REPOSITORY process environment variable is set, the utility makes no effect.\n\n"
          "The command line options are");

      std::vector<std::string> app_types_list;
      std::vector<std::string> segments_list;

      desc.add_options()
        ("branch,b", boost::program_options::value<std::string>(&branch_name), "checkout or create given branch name")
        ("version,e", boost::program_options::value<std::string>(&config_version), "oks config version in type:value format, where type is \"hash\", \"date\" or \"tag\"")
        ("output-directory,o", boost::program_options::value<std::string>(&user_dir), "output directory; if not defined, create temporal")
        ("verbose,v", "print verbose information")
        ("help,h", "print help message");

      boost::program_options::variables_map vm;
      boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);

      if (vm.count("help"))
        {
          std::cout << desc << std::endl;
          return EXIT_SUCCESS;
        }

      if (vm.count("verbose"))
        verbose = true;

      boost::program_options::notify(vm);
    }
  catch (std::exception& ex)
    {
      std::cerr << "Command line parsing errors occurred:\n" << ex.what() << std::endl;
      return EXIT_FAILURE;
    }

  if (!getenv("TDAQ_DB_USER_REPOSITORY"))
    {
      if(!user_dir.empty())
        setenv("TDAQ_DB_USER_REPOSITORY_PATH", user_dir.c_str(), 1);

      OksKernel k(user_dir.empty() && !verbose, verbose, false, true, config_version.empty() ? nullptr : config_version.c_str(), branch_name);

      if (!k.get_user_repository_root().empty())
        {
          k.unset_repository_created();

          if (user_dir.empty())
            std::cout << k.get_user_repository_root() << std::endl;
        }
    }

  return EXIT_SUCCESS;
}
```

### `bin/oks_dump.cpp`  
*Local path: `repo/oks/bin/oks_dump.cpp`*

```cpp
/**
 *  \file oks_dump.cpp
 *
 *  This file is part of the OKS package.
 *  Author: <Igor.Soloviev@cern.ch>
 *
 *  This file contains the implementation of the OKS application to dump
 *  contents of the OKS database files.
 *
 */

#include <vector>
#include <iostream>

#include <string.h>
#include <stdlib.h>

#include <oks/kernel.h>
#include <oks/query.h>
#include <oks/exceptions.h>


enum __OksDumpExitStatus__ {
  __Success__ = 0,
  __BadCommandLine__,
  __BadOksFile__,
  __BadQuery__,
  __NoSuchClass__,
  __FoundDanglingReferences__,
  __ExceptionCaught__
};


static void
printUsage(std::ostream& s)
{
  s << "Usage: oks_dump\n"
       "    [--files-only | --files-stat-only | --schema-files-only | --schema-files-stat-only | --data-files-only | --data-files-stat-only]\n"
       "    [--class name-of-class [--query query [--print-references recursion-depth [class-name*] [--]] [--print-referenced_by [name] [--]]]]\n"
       "    [--path object-from object-to query]\n"
       "    [--allow-duplicated-objects-via-inheritance]\n"
       "    [--version]\n"
       "    [--help]\n"
       "    [--input-from-files] database-file [database-file(s)]\n"
       "\n"
       "Options:\n"
       "    -f | --files-only                                 print list of oks files names\n"
       "    -F | --files-stat-only                            print list of oks files with statistic details (size, number of items\n" 
       "    -s | --schema-files-only                          print list of schema oks files names\n"
       "    -S | --schema-files-stat-only                     print list of oks schema files with statistic details\n"
       "    -d | --data-files-only                            print list of data oks files names\n"
       "    -D | --data-files-stat-only                       print list of oks data files with statistic details\n"
       "    -c | --class class_name                           dump given class (all objects or matching some query)\n"
       "    -q | --query query                                print objects matching query (can only be used with class)\n"
       "    -r | --print-references N C1 C2 ... CX            print objects referenced by found objects (can only be used with query), where:\n"
       "                                                       * the parameter N defines recursion depth for referenced objects (> 0)\n"
       "                                                       * the optional set of names {C1 .. CX} defines [sub-]classes for above objects\n"
       "    -b | --print-referenced_by [name]                 print objects referencing found objects (can only be used with query), where:\n"
       "                                                       * the optional parameter name defines name of relationship\n"
       "    -p | --path obj query                             print path from object \'obj\' to object of query expression\n"
       "    -i | --input-from-files                           read oks files to be loaded from file(s) instead of command line\n"
       "                                                      (to avoid problems with long command line, when there is huge number of files)\n"
       "    -a | --allow-duplicated-objects-via-inheritance   do not stop if there are duplicated object via inheritance hierarchy\n"
       "    -v | --version                                    print version\n"
       "    -h | --help                                       print this text\n"
       "\n"
       "Description:\n"
       "    Dumps contents of the OKS database.\n"
       "\n"
       "Return Status:\n"
       "    0 - no problems found\n"
       "    1 - bad command line parameter\n"
       "    2 - bad oks file(s)\n"
       "    3 - bad query passed via -q or -p options\n"
       "    4 - cannot find class passed via -c option\n"
       "    5 - loaded objects have dangling references\n"
       "    6 - caught an exception\n"
       "\n";
}

static void
no_param(const char * s)
{
  Oks::error_msg("oks_dump") << "no parameter(s) for command line argument \'" << s << "\' provided\n\n";
  exit(EXIT_FAILURE);
}

OksObject*
find_object(char * s, OksKernel& k)
{
  char * id = s;

  if((s = strchr(id, '@')) == 0) return 0;

  *s = '\0';
  s++;

  if(OksClass * c = k.find_class(s)) {
    if(OksObject * o = c->get_object(id)) {
      return o;
    }
    else {
      Oks::error_msg("oks_dump::find_object()") << "cannot find object \"" << id << '@' << s << "\"\n";
    }
  }
  else {
    Oks::error_msg("oks_dump::find_object()") << "cannot find class \"" << s << "\"\n";
  }

  return 0;
}

int
main(int argc, char **argv)
{
  if(argc == 1) {
    printUsage(std::cerr);
    return __BadCommandLine__;
  }

  OksKernel kernel;
  kernel.set_test_duplicated_objects_via_inheritance_mode(true);

  try {

    int dump_files_only = 0; // 0 - none, 12 - data, 1 - schema, 2 - schema & data
    const char * class_name = 0;
    const char * query = 0;
    const char * object_from = 0;
    const char * path_query = 0;
    long recursion_depth = 0;
    bool print_referenced_by = false;
    const char * ref_by_rel_name = "*";
    std::vector<std::string> ref_classes;
    bool input_from_files = false;
    bool print_files_stat = false;

    for(int i = 1; i < argc; i++) {
      const char * cp = argv[i];

      if(!strcmp(cp, "-h") || !strcmp(cp, "--help")) {
        printUsage(std::cout);		
        return __Success__;
      }
      else if(!strcmp(cp, "-v") || !strcmp(cp, "--version")) {
        std::cout << "OKS kernel version " << OksKernel::GetVersion() << std::endl;		
        return __Success__;
      }
      else if(!strcmp(cp, "-a") || !strcmp(cp, "--allow-duplicated-objects-via-inheritance")) {
        kernel.set_test_duplicated_objects_via_inheritance_mode(false);
      }
      else if(!strcmp(cp, "-f") || !strcmp(cp, "--files-only")) {
        dump_files_only = 2;
      }
      else if(!strcmp(cp, "-F") || !strcmp(cp, "--files-stat-only")) {
        dump_files_only = 2;
        print_files_stat = true;
      }
      else if(!strcmp(cp, "-s") || !strcmp(cp, "--schema-files-only")) {
        dump_files_only = 1;
      }
      else if(!strcmp(cp, "-S") || !strcmp(cp, "--schema-files-stat-only")) {
        dump_files_only = 1;
        print_files_stat = true;
      }
      else if(!strcmp(cp, "-d") || !strcmp(cp, "--data-files-only")) {
        dump_files_only = 12;
      }
      else if(!strcmp(cp, "-D") || !strcmp(cp, "--data-files-stat-only")) {
        dump_files_only = 12;
        print_files_stat = true;
      }
      else if(!strcmp(cp, "-c") || !strcmp(cp, "--class")) {
        if(++i == argc) { no_param(cp); } else { class_name = argv[i]; }
      }
      else if(!strcmp(cp, "-q") || !strcmp(cp, "--query")) {
        if(++i == argc) { no_param(cp); } else { query = argv[i]; }
      }
      else if(!strcmp(cp, "-i") || !strcmp(cp, "--input-from-files")) {
        input_from_files = true;
      }
      else if(!strcmp(cp, "-r") || !strcmp(cp, "--print-references")) {
        if(++i == argc) { no_param(cp); } else { recursion_depth = atol(argv[i]); }
        int j = 0;
        for(; j < argc - i - 1; ++j) {
          if(argv[i+1+j][0] != '-') { ref_classes.push_back(argv[i+1+j]); } else { break; }
        }
        i += j;
      }
      else if(!strcmp(cp, "-b") || !strcmp(cp, "--print-referenced_by")) {
        print_referenced_by = true;
	if((i+1) < argc && argv[i+1][0] != '-') {
	  ref_by_rel_name = argv[++i];
	}
      }
      else if(!strcmp(cp, "-p") || !strcmp(cp, "--path")) {
        if(++i > argc - 1) { no_param(cp); } else { object_from = argv[i]; path_query = argv[++i];}
      }
      else if(strcmp(cp, "--")) {
        if(input_from_files) {
          std::ifstream f(cp);
  	  if(f.good()) {
	    while(f.good() && !f.eof()) {
	      std::string file_name;
	      std::getline(f, file_name);
	      if(!file_name.empty() && kernel.load_file(file_name) == 0) {
                Oks::error_msg("oks_dump") << "\tCan not load file \"" << file_name << "\", exiting...\n";
                return __BadOksFile__;
              }
	    }
	  }
	  else {
            Oks::error_msg("oks_dump") << "\tCan not open file \"" << cp << "\" for reading, exiting...\n";
            return __BadCommandLine__;
	  }
        }
        else {
          if(kernel.load_file(cp) == 0) {
            Oks::error_msg("oks_dump") << "\tCan not load file \"" << cp << "\", exiting...\n";
            return __BadOksFile__;
          }
        }
      }
    }

    if(kernel.schema_files().empty()) {
      Oks::error_msg("oks_dump") << "\tAt least one oks file have to be provided, exiting...\n";
      return __BadCommandLine__;
    }

    if(query && !class_name) {
      Oks::error_msg("oks_dump") << "\tQuery can only be executed when class name is provided (use -c option), exiting...\n";
      return __BadCommandLine__;
    }

    if(dump_files_only) {
      long total_size = 0;
      long total_items = 0;
      const OksFile::Map * files [2] = {&kernel.schema_files(), &kernel.data_files()};
      for(int j = (dump_files_only / 10); j < (dump_files_only % 10); ++j) {
        if(!files[j]->empty()) {
          for(OksFile::Map::const_iterator i = files[j]->begin(); i != files[j]->end(); ++i) {
            if(print_files_stat) {
              total_size += i->second->get_size();
              total_items += i->second->get_number_of_items();
              std::cout << *(i->first) << " (" << i->second->get_number_of_items() << " items, " << i->second->get_size() << " bytes)" << std::endl;
            }
            else {
              std::cout << *(i->first) << std::endl;
            }
          }
        }
      }

      if(print_files_stat) {
        std::cout << "Total number of items: " << total_items << "\n"
                     "Total size of files: " << total_size << " bytes" << std::endl;
      }
    }
    else if(class_name && *class_name) {
      if(OksClass * c = kernel.find_class(class_name)) {
        if(query && *query) {
          OksQuery * q = new OksQuery(c, query);
  	  if(q->good()) {
	    OksObject::List * objs = c->execute_query(q);
	    size_t num = (objs ? objs->size() : 0);
	    std::cout << "Found " << num << " matching query \"" << query << "\" in class \"" << class_name << "\"";
	    if(num) {
	      std::cout << ':' << std::endl;
	      while(!objs->empty()) {
	        OksObject * o = objs->front();
	        objs->pop_front();
		
	        if(recursion_depth > 0 || print_referenced_by) {
		  if(recursion_depth) {
                    oks::ClassSet all_ref_classes;
                    kernel.get_all_classes(ref_classes, all_ref_classes);
	            OksObject::FSet refs;
		    o->references(refs, recursion_depth, false, &all_ref_classes);
	            std::cout << o << " references " << refs.size() << " object(s)" << std::endl;
		    for(OksObject::FSet::const_iterator i = refs.begin(); i != refs.end(); ++i) {
		      std::cout << " - " << *i << std::endl;
		    }
		  }
		  if(print_referenced_by) {
		    if(OksObject::FList * ref_by_objs = o->get_all_rels(ref_by_rel_name)) {
	              std::cout << o << " is referenced by " << ref_by_objs->size() << " object(s) via relationship \"" << ref_by_rel_name << "\":" << std::endl;

                      for(OksObject::FList::const_iterator i = ref_by_objs->begin(); i != ref_by_objs->end(); ++i) {
                        std::cout << " - " << *i << std::endl;
                      }
		      
		      delete ref_by_objs;
		    }
		    else {
	              std::cout << o << " is not referenced by any object via relationship \"" << ref_by_rel_name << '\"' << std::endl;
		    }
		  }
	        }
	        else {
	          std::cout << *o << std::endl;
	        }
	      }
	      delete objs;
	    }
	    else {
	      std::cout << std::endl;
	    }
	  }
	  else {
            Oks::error_msg("oks_dump") << "\tFailed to parse query \"" << query << "\" in class \"" << class_name << "\"\n";
            return __BadQuery__;
	  }
	  delete q;
        }
        else {
          std::cout << *c << std::endl;
        }
      }
      else {
        Oks::error_msg("oks_dump") << "\tCan not find class \"" << class_name << "\"\n";
        return __NoSuchClass__;
      }
    }
    else if(object_from && *object_from && path_query && *path_query) {
      OksObject * obj_from = find_object((char *)object_from, kernel);
      try {
        oks::QueryPath q(path_query, kernel);
        OksObject::List * objs = obj_from->find_path(q);

        size_t num = (objs ? objs->size() : 0);
        std::cout << "Found " << num << " objects in the path \"" << q << "\" from object " << obj_from << ":" << std::endl;

        if(num) {
          while(!objs->empty()) {
            OksObject * o = objs->front();
            objs->pop_front();
            std::cout << *o << std::endl;
          }
          delete objs;
        }
      }
      catch ( oks::bad_query_syntax& e ) {
        Oks::error_msg("oks_dump") << "\tFailed to parse query: " << e.what() << std::endl;
        return __BadQuery__;
      }
    }
    else {
      std::cout << kernel;
    }

    if(!kernel.get_bind_classes_status().empty())
      {
        Oks::error_msg("oks_dump") << "The schema contains dangling references to non-loaded classes:\n" << kernel.get_bind_classes_status();
      }

    if(!kernel.get_bind_objects_status().empty())
      {
        Oks::error_msg("oks_dump") << "\tThe data contain dangling references to non-loaded objects\n";
      }

    if(!kernel.get_bind_classes_status().empty() || !kernel.get_bind_objects_status().empty())
      {
        return __FoundDanglingReferences__;
      }
  }
  catch (oks::exception & ex) {
    std::cerr << "Caught oks exception:\n" << ex << std::endl;
    return __ExceptionCaught__;
  }
  catch (std::exception & e) {
    std::cerr << "Caught standard C++ exception: " << e.what() << std::endl;
    return __ExceptionCaught__;
  }
  catch (...) {
    std::cerr << "Caught unknown exception" << std::endl;
    return __ExceptionCaught__;
  }

  return __Success__;
}
```

### `bin/oks_git_repository.cpp`  
*Local path: `repo/oks/bin/oks_git_repository.cpp`*

```cpp
/**
 *  \file oks_git_repository.cpp
 *
 *  This file is part of the OKS package.
 *  Author: <Igor.Soloviev@cern.ch>
 */

#include <oks/kernel.h>

#include <string.h>
#include <stdlib.h>


int
main(int argc, char **argv)
{
  if(argc > 1)
    {
      if(!strcmp("-h", argv[1]) || !strcmp("--help", argv[1]))
        {
          std::cout << "This program extracts OKS git repository from TDAQ_DB_REPOSITORY process environment variable." << std::endl;
          return EXIT_SUCCESS;
        }
    }

  std::cout << OksKernel::get_repository_root() << std::endl;

  return EXIT_SUCCESS;
}
```

### `bin/oks_validate_repository.cpp`  
*Local path: `repo/oks/bin/oks_validate_repository.cpp`*

```cpp
/**
 *  \file oks_validate_repository.cpp
 *
 *  This file is part of the OKS package.
 *  Author: <Igor.Soloviev@cern.ch>
 */

#include <algorithm>
#include <chrono>
#include <vector>
#include <iostream>
#include <filesystem>
#include <mutex>

#include <boost/program_options.hpp>

#include <ers/ers.h>

#include <daq_tokens/verify.h>

#include <AccessManager/util/ErsIssues.h>
#include <AccessManager/client/RequestorInfo.h>
#include <AccessManager/client/ServerInterrogator.h>
#include <AccessManager/xacml/impl/DBResource.h>

#include <oks/kernel.h>
#include <oks/pipeline.h>
#include <oks/exceptions.h>

enum __OksValidateRepositoryExitStatus__ {
  __Success__ = 0,
  __BadCommandLine__,
  __UserAuthenticationFailure__,
  __NoRepository__,
  __ConsistencyError__,
  __IncludesCircularDependencyError__,
  __AccessManagerAuthorizationFailed__,
  __AccessManagerNoPermission__,
  __NoIncludedFile__,
  __ExceptionCaught__
};


ERS_DECLARE_ISSUE( oks, TokenError, "Cannot verify daq token", ERS_EMPTY )

static int
report_am_error(const daq::am::Exception &ex)
{
  oks::log_timestamp(oks::Error) << "The Access Manager authorization failed:\n" << ex << std::endl;
  return __AccessManagerAuthorizationFailed__;
}

static int
report_am_no_permission(const std::string& user, const char* action, const std::string& path)
{
  oks::log_timestamp(oks::Error) << "Access Manager grants no permission for user " << user << " to " << action << " \'" << path << '\'' << std::endl;
  return __AccessManagerNoPermission__;
}

std::string s_load_error;

static void
init_file_load_error(const std::string& file)
{
  s_load_error = "repository validation failed for file \'";
  s_load_error += file;
  s_load_error += "\':\n";
}

struct OksValidateJob : public OksJob
{
public:

  OksValidateJob(OksKernel& kernel, const std::string& file_name) :
      m_kernel(kernel), m_file_name(file_name)
  {
    ;
  }

  void
  run()
  {
    static std::mutex s_mutex;

    try
      {
        auto start_usage = std::chrono::steady_clock::now();

        m_kernel.set_silence_mode(true);

        m_kernel.load_file(m_file_name);

        if (!m_kernel.get_bind_classes_status().empty() || !m_kernel.get_bind_objects_status().empty())
          {
            std::lock_guard lock(s_mutex);

            if (s_load_error.empty())
              {
                init_file_load_error(m_file_name);

                if (!m_kernel.get_bind_classes_status().empty())
                  {
                    s_load_error += "the schema contains dangling references to non-loaded classes:\n";
                    s_load_error += m_kernel.get_bind_classes_status();
                  }

                if (!m_kernel.get_bind_objects_status().empty())
                  {
                    s_load_error += "the data contain dangling references to non-loaded objects:\n";
                    s_load_error += m_kernel.get_bind_objects_status();
                  }
              }
          }

        static std::mutex s_log_mutex;
        std::lock_guard scoped_lock(s_log_mutex);

        oks::log_timestamp() << "validated file \"" << m_file_name << "\" in " << std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start_usage).count() / 1000. << " ms\n";
      }
    catch (std::exception& ex)
      {
        std::lock_guard lock(s_mutex);

        if (s_load_error.empty())
          {
            init_file_load_error(m_file_name);
            s_load_error += ex.what();

            const std::string& user_repository(m_kernel.get_user_repository_root());
            const std::size_t user_repository_len(m_kernel.get_user_repository_root().length() + 1);

            std::size_t pos;
            while ((pos = s_load_error.find(user_repository)) != std::string::npos)
              s_load_error.replace(pos, user_repository_len, "");
          }
      }
  }

private:

  OksKernel m_kernel;
  const std::string& m_file_name;

  // protect usage of copy constructor and assignment operator

private:

  OksValidateJob(const OksValidateJob&);
  OksValidateJob&
  operator=(const OksValidateJob&);

};


struct FoundCircularDependency
{
  unsigned int m_count;
  std::ostringstream m_text;

  FoundCircularDependency() :
      m_count(0)
  {
    ;
  }
} s_circular_dependency_message;


struct TestCircularDependency
{
  TestCircularDependency(const std::string * file)
  {
    p_set_includes.insert(file);
    p_vector_includes.push_back(file);
  }

  bool
  push(const std::string * file)
  {
    auto it = p_set_includes.insert(file);
    if (it.second == false)
      {
        std::ostringstream s;

        bool report = false;

        for (const auto& x : p_vector_includes)
          {
            if (x == *it.first)
              {
                s_circular_dependency_message.m_text << "\nCircular dependency [" << ++s_circular_dependency_message.m_count << "]:";
                report = true;
              }

            if (report)
              s_circular_dependency_message.m_text << '\n' << " - \"" << *x << "\"";
          }

        return false;
      }

    p_vector_includes.push_back(file);

    return true;
  }

  void
  pop()
  {
    p_set_includes.erase(p_vector_includes.back());
    p_vector_includes.pop_back();
  }

  std::vector<const std::string *> p_vector_includes;
  std::set<const std::string *, OksFile::SortByName> p_set_includes;
};


std::set<std::string>&
define_includes(const std::string& f, const std::set<std::string>& s, std::map<std::string, std::set<std::string>>& file_all_includes, std::map<std::string, std::set<std::string>>& file_explicit_includes, TestCircularDependency& cd_fuse)
{
  std::set<std::string>& all_includes = file_all_includes[f];

  if(all_includes.empty())
    {
      for(auto& x : s)
        {
          if(cd_fuse.push(&x))
            {
              all_includes.insert(x);

              std::set<std::string>& includes = define_includes(x, file_explicit_includes[x], file_all_includes, file_explicit_includes, cd_fuse);
              for(const auto& y : includes)
                all_includes.insert(y);

              cd_fuse.pop();
            }
        }
    }

  return all_includes;
}


int
main(int argc, char **argv)
{
  boost::program_options::options_description desc("This program validates OKS git repository for commit by pre-receive hook");

  std::vector<std::string> created, updated, deleted;
  bool circular_dependency_between_includes_is_error = true;
  bool use_am = true;
  bool verbose = false;
  std::string user;
  std::size_t pipeline_size = 4;

  try
    {
      std::vector<std::string> app_types_list;
      std::vector<std::string> segments_list;
      std::string token;

      desc.add_options()
        ("add,a", boost::program_options::value<std::vector<std::string> >(&created)->multitoken(), "list of new OKS files and directories to be added to the repository")
        ("update,u", boost::program_options::value<std::vector<std::string> >(&updated)->multitoken(), "list of new OKS files and directories to be updated in the repository")
        ("remove,r", boost::program_options::value<std::vector<std::string> >(&deleted)->multitoken(), "list of new OKS files and directories to be removed from the repository")
        ("permissive-circular-dependencies-between-includes,C", "downgrade severity of detected circular dependencies between includes from errors to warnings")
        ("no-access-manager,A", "do not use the access manager")
        ("user,U", boost::program_options::value<std::string>(&user), "user id")
        ("token,T", boost::program_options::value<std::string>(&token), "daq token to provide user id")
        ("threads-number,t", boost::program_options::value<std::size_t>(&pipeline_size)->default_value(pipeline_size), "number of threads used by validation pipeline")
        ("verbose,v", "Print debug information")
        ("help,h", "Print help message");

      boost::program_options::variables_map vm;
      boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);

      if (vm.count("help"))
        {
          std::cout << desc << std::endl;
          return __Success__;
        }

      if (vm.count("permissive-circular-dependencies-between-includes"))
        circular_dependency_between_includes_is_error = false;

      if (vm.count("verbose"))
        verbose = true;

      if (vm.count("no-access-manager"))
        use_am = false;

      boost::program_options::notify(vm);

      if (!token.empty())
        {
          if (!user.empty())
            throw std::runtime_error("both \"user\" and \"token\" parameters cannot be used simultaneously");

          auto start_usage = std::chrono::steady_clock::now();

          try
            {
              user = daq::tokens::verify(token).get_subject();
            }
          catch(const ers::Issue& ex)
            {
              ers::fatal(oks::TokenError(ERS_HERE, ex));
              return __UserAuthenticationFailure__;
            }

          oks::log_timestamp() << "verified daq token of user " << user << " in " << std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start_usage).count() / 1000. << " ms" << std::endl;
        }

      if (use_am && user.empty())
        throw std::runtime_error("the \"user\" must be provided when the Acceess Manager is enabled");
    }
  catch (std::exception& ex)
    {
      std::cerr << "Command line parsing errors occurred:\n" << ex.what() << std::endl;
      return __BadCommandLine__;
    }


  try
    {
      OksKernel kernel;

      kernel.set_allow_duplicated_objects_mode(false);
      kernel.set_test_duplicated_objects_via_inheritance_mode(true);

      if(kernel.get_user_repository_root().empty())
        {
          std::cerr << "There is no OKS repository set (check TDAQ_DB_REPOSITORY)" << std::endl;
          return __NoRepository__;
        }

      std::filesystem::current_path(kernel.get_user_repository_root());

      auto start_usage = std::chrono::steady_clock::now();

      // directories

      std::set<std::string> directories;


      // file: explicit includes
      std::map<std::string, std::set<std::string>> file_explicit_includes;

      for (auto& p : std::filesystem::recursive_directory_iterator("."))
        if (std::filesystem::is_directory(p))
          directories.insert(p.path().native().substr(2));
        else if (std::filesystem::is_regular_file(p) && p.path().native().find("./.git") != 0 && p.path().native().find("./admin") != 0 && p.path().native().find("./README.md") != 0)
          kernel.get_includes(p.path().native(), file_explicit_includes[p.path().native().substr(2)], true);

      if (verbose)
        oks::log_timestamp(oks::Debug) << "scan " << file_explicit_includes.size() << " repository files in " << std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start_usage).count() / 1000. << " ms\n";


      auto start_usage2 = std::chrono::steady_clock::now();

      std::set<std::string> all_includes;

      // check every include exists
      for (const auto& f : file_explicit_includes)
        {
          for (const auto& i : f.second)
            {
              if(file_explicit_includes.find(i) != file_explicit_includes.end())
                {
                  all_includes.insert(i);
                }
              else
                {
                  std::cerr << "Cannot find file \"" << i << "\" included by \"" << f.first << "\"" << std::endl;
                  return __NoIncludedFile__;
                }
            }
        }

      if (verbose)
        oks::log_timestamp(oks::Debug) << "check existence of includes in " << std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start_usage2).count() / 1000. << " ms\n";


      auto start_usage3 = std::chrono::steady_clock::now();

      // file: all includes
      std::map<std::string, std::set<std::string>> file_all_includes;

      for(auto& x : file_explicit_includes)
        {
          TestCircularDependency cd_fuse(&x.first);
          define_includes(x.first, x.second, file_all_includes, file_explicit_includes, cd_fuse);
        }

      auto stop_usage3 = std::chrono::steady_clock::now();

      if (verbose)
        oks::log_timestamp(oks::Debug) << "calculated inclusion graph in " << std::chrono::duration_cast<std::chrono::microseconds>(stop_usage3-start_usage3).count() / 1000. << " ms\n";

      oks::log_timestamp() << "process " << file_explicit_includes.size() << " repository files and their includes in " << std::chrono::duration_cast<std::chrono::microseconds>(stop_usage3-start_usage).count() / 1000. << " ms" << std::endl;


      if (s_circular_dependency_message.m_count)
        {
          oks::log_timestamp((circular_dependency_between_includes_is_error == true ? oks::Error : oks::Warning)) << "Detected " << s_circular_dependency_message.m_count << " circular dependencies between includes of the repository files:" << s_circular_dependency_message.m_text.str() << std::endl;

          if (circular_dependency_between_includes_is_error == true)
            return __IncludesCircularDependencyError__;
        }

      if (ers::debug_level() >= 2)
        {
          std::ostringstream text;
          text << "ALL INCLUDES:\n";

          for (const auto& x : file_all_includes)
            {
              text << "FILE \"" << x.first << "\" has " << x.second.size() << " includes:\n";

              for (const auto& y : x.second)
                text << " - \"" << y << "\"\n";
            }

          ERS_DEBUG(2, text.str());
        }


      // check AM permissions for given user

      if (use_am)
        {
          start_usage = std::chrono::steady_clock::now();

          daq::am::RequestorInfo * s_access_subject = new daq::am::RequestorInfo(user, OksKernel::get_host_name());
          daq::am::ServerInterrogator si;

          bool s_is_db_admin(false);

            {
              std::unique_ptr<const daq::am::DBResource> db_admin_res(daq::am::DBResource::getInstanceForAdminOperations());

              try
                {
                  s_is_db_admin = si.isAuthorizationGranted(*db_admin_res, *s_access_subject);
                }
              catch (daq::am::Exception &ex)
                {
                  return report_am_error(ex);
                }
            }

          ERS_DEBUG(1, "user " << user << " has db-admin privileges: " << std::boolalpha << s_is_db_admin);


          if (s_is_db_admin == false)
            {
              // check permissions for created paths
              for (const auto& x : created)
                {
                  if (directories.find(x) != directories.end())
                    {
                      ERS_DEBUG(1, "test permission to create directory \'" << x << "\'...");

                      std::unique_ptr<const daq::am::DBResource> db_dir_res(daq::am::DBResource::getInstanceForDirectoryOperations(x, daq::am::DBResource::ACTION_ID_CREATE_SUBDIR));

                      try
                        {
                          if (!si.isAuthorizationGranted(*db_dir_res, *s_access_subject))
                            return report_am_no_permission(user, "create directory", x);
                        }
                      catch(daq::am::Exception &ex)
                        {
                          return report_am_error(ex);
                        }

                    }
                  else
                    {
                      ERS_DEBUG(1, "test permission to create file \'" << x << "\'...");

                      std::unique_ptr< const daq::am::DBResource > db_dir_res( daq::am::DBResource::getInstanceForDirectoryOperations(x, daq::am::DBResource::ACTION_ID_CREATE_FILE) );

                      try
                        {
                          if (!si.isAuthorizationGranted(*db_dir_res, *s_access_subject))
                            return report_am_no_permission(user, "create file", x);
                        }
                      catch(daq::am::Exception &ex)
                        {
                          return report_am_error(ex);
                        }
                    }
                }

              // check permissions for updated files
              for (const auto& x : updated)
                {
                  ERS_DEBUG(1, "test permission to update file \'" << x << "\'...");

                  std::unique_ptr< const daq::am::DBResource > db_file_res( daq::am::DBResource::getInstanceForFileOperations(x, daq::am::DBResource::ACTION_ID_UPDATE_FILE) );

                  try
                    {
                      if(!si.isAuthorizationGranted(*db_file_res, *s_access_subject))
                        return report_am_no_permission(user, "update file", x);
                    }
                  catch(daq::am::Exception &ex)
                    {
                      return report_am_error(ex);
                    }
                }

              // process deleted files
              // check permissions for deleted paths
              for (const auto& x : deleted)
                {
                  ERS_DEBUG(1, "test permission to delete file \'" << x << "\'...");

                  std::unique_ptr< const daq::am::DBResource > db_dir_res( daq::am::DBResource::getInstanceForDirectoryOperations(x, daq::am::DBResource::ACTION_ID_DELETE_FILE) );

                  try
                    {
                      if (!si.isAuthorizationGranted(*db_dir_res, *s_access_subject))
                        return report_am_no_permission(user, "delete file", x);
                    }
                  catch(daq::am::Exception &ex)
                    {
                      return report_am_error(ex);
                    }
                }
            }

          oks::log_timestamp() << "got Access Manager authorisation in " << std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start_usage).count() / 1000. << " ms\n";
        }

      OksPipeline pipeline(pipeline_size);

      // do not run check for README file
      auto ignore_files = [](std::string& x)
      {
        static const std::string readme_file("README.md");
        return x != readme_file;
      };

      // all modified file paths
      std::set<std::string> modified;
      std::copy_if(created.begin(), created.end(), std::inserter(modified, modified.end()), ignore_files);
      std::copy_if(updated.begin(), updated.end(), std::inserter(modified, modified.end()), ignore_files);

      // validate independently every created or updated file
      for (const auto& x : modified)
        pipeline.addJob(new OksValidateJob(kernel, x));

      std::copy_if(deleted.begin(), deleted.end(), std::inserter(modified, modified.end()), ignore_files);

      for (const auto& f : file_explicit_includes)
        if (all_includes.find(f.first) == all_includes.end())
          {
            if (modified.empty() == false)
              {
                if (modified.find(f.first) == modified.end())
                  {
                    const auto& file_includes = file_all_includes[f.first];

                    bool found = false;

                    for (const auto& x : modified)
                      if (file_includes.find(x) != file_includes.end())
                        {
                          found = true;
                          ERS_DEBUG(1, "file \"" << f.first << "\" contains modified include \"" << x << '\"');
                          break;
                        }

                    if(found == false)
                      {
                        ERS_DEBUG(1, "skip file \"" << f.first << '\"');
                        continue;
                      }
                  }
                else
                  {
                    ERS_DEBUG(1, "list of modified files contains file \"" << f.first << '\"');
                  }
              }

            if (modified.find(f.first) == modified.end())
              pipeline.addJob(new OksValidateJob(kernel, f.first));
          }

      pipeline.waitForCompletion();

      if (!s_load_error.empty())
        {
          oks::log_timestamp(oks::Error) << s_load_error << std::endl;
          return __ConsistencyError__;
        }
    }
  catch (oks::exception & ex)
    {
      oks::log_timestamp(oks::Error) << "Caught oks exception:\n" << ex << std::endl;
      return __ExceptionCaught__;
    }
  catch (std::exception & e)
    {
      oks::log_timestamp(oks::Error) << "Caught standard C++ exception:\n" << e.what() << std::endl;
      return __ExceptionCaught__;
    }
  catch (...)
    {
      oks::log_timestamp(oks::Error) << "Caught unknown exception" << std::endl;
      return __ExceptionCaught__;
    }

  return __Success__;
}
```

### `scripts/oks-checkout.sh`  
*Local path: `repo/oks/scripts/oks-checkout.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

if [ -z "${TDAQ_DB_REPOSITORY}" ]
then
  echo 'ERROR [oks-checkout.sh]: variable TDAQ_DB_REPOSITORY is not set'
  exit 1
fi

git_repo=`oks_git_repository`

if [ -z "${git_repo}" ]
then
  echo 'ERROR [oks-checkout.sh]: failed to get oks get repository'
  exit 1
fi

########################################################################################################################

trace=0
hash=''
tag=''
date=''
branch='master'

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      echo " -> [oks-checkout.sh]: git repository: ${git_repo}"
      ;;

    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-checkout.sh]: export TDAQ_DB_USER_REPOSITORY=$TDAQ_DB_USER_REPOSITORY"
      fi
      ;;

    -t | --tag)
      shift
      tag="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-checkout.sh]: tag: ${tag}"
      fi
      ;;

    -d | --date)
      shift
      date="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-checkout.sh]: date: ${date}"
      fi
      ;;

    -c | --commit-hash | --hash)
      shift
      hash="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-checkout.sh]: commit hash: ${hash}"
      fi
      ;;

    -b | --branch)
      shift
      branch="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-checkout.sh]: branch: ${branch}"
      fi
      ;;

    -h* | --he*)
      echo 'Usage: oks-checkout.sh [-v] [-u user-repository-dir] [-b branch] [-c commit-hash] [-t tag] [-d date] [-h]'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose       trace this script execution'
      echo '   -u | --user-rep-dir  define user repository directory'
      echo '   -b | --branch        checkout branch, create if does not exist, use master branch by default'
      echo '   -c | --commit-hash   checkout repository with given commit hash'
      echo '   -t | --tag           checkout repository with given tag'
      echo '   -d | --date          checkout repository for given timestamp'
      echo '   -h | --help          print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS checkout utility allows to checkout files and directories from OKS'
      echo '   git repository into user repository, where they can be modified and committed back.'
      echo '   The variable TDAQ_DB_REPOSITORY defines the OKS database repository directory of git repository.'
      echo '   The variable TDAQ_DB_USER_REPOSITORY defines the user database repository.'
      echo '   If the latter one is not set, the files are check out into current working directory.'
      echo ''
      exit 0
      ;;
  esac
  shift
done

if [ ! -z "${hash}" ] && [ ! -z "${tag}" ]
then
	echo "ERROR [oks-checkout.sh]: cannot use commit-hash and tag parameters simultaneously"
	exit 1
fi

if [ ! -z "${hash}" ] && [ ! -z "${date}" ]
then
  echo "ERROR [oks-checkout.sh]: cannot use commit-hash and date parameters simultaneously"
  exit 1
fi

if [ ! -z "${tag}" ] && [ ! -z "${date}" ]
then
  echo "ERROR [oks-checkout.sh]: cannot use tag and date parameters simultaneously"
  exit 1
fi

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-checkout.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

if [ $trace -eq 1 ]
then
  echo " -> [oks-checkout.sh]: cd ${TDAQ_DB_USER_REPOSITORY}"
fi

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-checkout.sh]: cannot change directory to user repository ${TDAQ_DB_USER_REPOSITORY}"
  exit 1
fi

########################################################################################################################

echo "git clone -q -n ${git_repo} ."
git clone -q -n "${git_repo}" .

if [ $? -ne 0 ]
then
  echo "ERROR [oks-checkout.sh]: git clone has failed"
  exit 1
fi

echo "git config pull.rebase true"
git config pull.rebase true

if [ $? -ne 0 ]
then
  echo "ERROR [oks-checkout.sh]: git config has failed"
  exit 1
fi

command="git checkout -q -B ${branch}"

if [ ! -z "${tag}" ]
then
  echo "$command tags/${tag}"
  $command tags/${tag}
  if [ $? -ne 0 ]
  then
    echo "ERROR [oks-checkout.sh]: git checkout has failed"
    exit 1
  fi
else
  if [ ! -z "${date}" ]
  then
    if [ $trace -eq 1 ]
    then
      echo " -> [oks-checkout.sh]: calculate commit hash for date ${date}: git rev-list -1 --before="${date}" ${branch}"
    fi

    hash=$(git rev-list -1 --before="${date}" "${branch}")

    if [ $? -ne 0 ]
    then
      echo "ERROR [oks-checkout.sh]: checkout has failed"
      exit 1
    fi
  fi

  if [ -z "${hash}" ] && git ls-remote --exit-code --heads origin "$branch" > /dev/null
  then
    hash="origin/${branch}"
  fi

  echo "$command ${hash}"
  $command ${hash}
  if [ $? -ne 0 ]
  then
    echo "ERROR [oks-checkout.sh]: git checkout has failed"
    exit 1
  fi
fi

if [ "${OKS_GIT_DEBUG}" != "no" ]
then
  DEBUG_DIR=".git/oks_proc_info"

  mkdir "${DEBUG_DIR}"
  if [ $? -eq 0 ]
  then
    printenv > "${DEBUG_DIR}/env"
    ps xuww > "${DEBUG_DIR}/ps"
    pstree -s $$ > "${DEBUG_DIR}/pstree"
    echo "$$" > "${DEBUG_DIR}/pid"
  fi
fi

if [ $trace -eq 1 ]
then
  echo " -> [oks-checkout.sh]: checkout completed"
fi

echo "checkout oks version `git rev-parse HEAD`"

########################################################################################################################
```

### `scripts/oks-commit.sh`  
*Local path: `repo/oks/scripts/oks-commit.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

trace=0
message=''
file=''
branch=''

########################################################################################################################

# temporary branch name
temp='temp_oks_commit_branch'

########################################################################################################################

# cover exit from sub-shell case

trap "exit 4" 10
PROC="$$"

########################################################################################################################


# An error exit function

error_exit()
{
  echo "ERROR [oks-commit.sh]: $1" 1>&2
  exit 1
}

cleanup_exit()
{
  echo "ERROR [oks-commit.sh]: $1" 1>&2
  echo "cleanup:"

  echo "git checkout $branch"
  git checkout "$branch"

  echo "git branch -D $temp"
  git branch -D $temp >/dev/null 2>&1
  
  exit 2
}

undo_merge()
{
  echo "ERROR [oks-commit.sh]: $1" 1>&2
  echo "cleanup and undo merge:"

  echo 'git rebase --skip'
  git rebase --skip

  exit 3
}

undo_exit()
{
  echo "ERROR [oks-commit.sh]: $1" 1>&2
  echo "cleanup and undo commit:"

  echo "git checkout $branch"
  git checkout "$branch"

  echo "git branch -D $temp"
  git branch -D $temp >/dev/null 2>&1

  echo "git reset HEAD~"
  git reset HEAD~
  
  kill -10 $PROC
  #exit 4
}

########################################################################################################################

pull()
{
  if [ "$branch" = 'master' ] || git ls-remote --exit-code --heads origin "$branch"
  then
    echo "git pull --no-edit -r origin $branch"
    git pull --no-edit -r origin "$branch" || undo_merge 'cannot merge changes with oks git repository'
  fi
}

########################################################################################################################

commit_cmd='git'

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      ;;

    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-commit.sh]: export TDAQ_DB_USER_REPOSITORY=$TDAQ_DB_USER_REPOSITORY"
      fi
      ;;

    -m | --message)
      shift
      message="$1"
      ;;

    -f | --file)
      shift
      file="$1"
      ;;

    -e )
      shift
      commit_cmd="$commit_cmd -c user.email='$1'"
      ;;

    -n )
      shift
      commit_cmd="$commit_cmd -c user.name='$1'"
      ;;

    -h* | --he*)
      echo 'Usage: oks-commit.sh [-v] [-u user-repository-dir] [-h] -m message | -f commit-message-file'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose       trace this script execution'
      echo '   -u | --user-rep-dir  define user repository directory'
      echo '   -h | --help          print this message'
      echo '   -m | --message       user commit message (avoid quotes inside message)'
      echo '   -f | --file          take the commit message from the given file'
      echo ''
      echo 'Description:'
      echo '   The OKS commit utility allows to commit changes in OKS database stored on git server.'
      echo '   The variable TDAQ_DB_USER_REPOSITORY defines the user database repository.'
      echo ''
      exit 0
      ;;
  esac
  shift
done

if [ -z "${message}" ] && [ -z "${file}" ]
then
  error_exit 'there is no commit message or file with commit message'
fi

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  error_exit 'user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
fi

########################################################################################################################

if [ $trace -eq 1 ]
then
  echo " -> [oks-commit.sh]: cd ${TDAQ_DB_USER_REPOSITORY}"
fi

cd "${TDAQ_DB_USER_REPOSITORY}" || error_exit "cannot change directory to user repository ${TDAQ_DB_USER_REPOSITORY}"

echo "git rev-parse --abbrev-ref HEAD"
branch=`git rev-parse --abbrev-ref HEAD` || error_exit "cannot detect branch name"
echo $branch

########################################################################################################################

echo "git checkout -b $temp"
git checkout -b $temp || error_exit 'cannot create temporary branch'

echo 'for f in `git ls-files -o | grep "\.xml$"`; do echo "git add $f"; git add "$f"; done'
for f in `git ls-files -o | grep '\.xml$'`; do echo "git add $f"; git add "$f"; done
if [ $? -ne 0 ]; then error_exit 'git add has failed'; fi

echo 'git update-index --refresh'
git update-index --refresh

echo 'git diff-index --quiet HEAD'
git diff-index --quiet HEAD

if [ $? -ne 0 ]
then	
  commit_cmd="$commit_cmd commit -a"
  if [ ! -z "${message}" ]
  then
    commit_cmd="${commit_cmd} -m \"${message}\""
  elif [ ! "${file}" = "/dev/null" ]
  then
    commit_cmd="${commit_cmd} -F \"${file}\""
  fi

  echo "$commit_cmd"
  eval "$commit_cmd"

  if [ $? -ne 0 ]; then cleanup_exit 'git commit has failed'; fi

  echo "git checkout $branch"
  git checkout "$branch" || undo_exit "cannot checkout $branch branch"

  echo "git merge --no-edit $temp"
  git merge --no-edit $temp || undo_exit 'failed to merge changes'

  echo "git branch -d $temp"
  git branch -d $temp || undo_exit 'failed to remove temporary branch'
  
  lock_file="/var/tmp/oks-git-commit-${CMTRELEASE}-`whoami`"
  
  (
    start_wait=$SECONDS

    if flock -x -w 60 198
    then
      pull

      git_push_out=`mktemp`
      echo "git push origin $branch"
      git push origin "$branch" 2>&1 | tee $git_push_out

      if [ ${PIPESTATUS[0]} -ne 0 ]
      then
        grep -q -i 'error.*is at .* but expected .*' $git_push_out
        if [ $? -ne 0 ] ; then undo_exit 'cannot store changes in oks git repository'; fi

        echo 'WARNING [oks-commit.sh]: detected git lock conflict, try to recover ...'

        pull
    
        echo "git push origin $branch"
        git push origin "$branch" || undo_exit 'git push has failed second time'
      fi

      rm $git_push_out
    else
      end=$SECONDS
      duration_wait=$(( end - start_wait ))
      undo_exit "cannot lock ${lock_file} after $duration_wait seconds timeout";
    fi
  ) 198>${lock_file}
  
else
  echo 'nothing to commit'

  echo "git checkout $branch"
  git checkout "$branch" || undo_exit "cannot checkout $branch branch"

  echo "git branch -d $temp"
  git branch -d $temp || undo_exit 'failed to remove temporary branch'
fi

if [ $trace -eq 1 ]
then
  echo " -> [oks-commit.sh]: commit completed"
fi

echo "commit oks version `git rev-parse HEAD`"

########################################################################################################################
```

### `scripts/oks-copy.sh`  
*Local path: `repo/oks/scripts/oks-copy.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

if [ -z "${TDAQ_DB_REPOSITORY}" ]
then
  echo 'ERROR [oks-copy.sh]: variable TDAQ_DB_REPOSITORY is not set'
  exit 1
fi

git_repo=`oks_git_repository`

if [ -z "${git_repo}" ]
then
  echo 'ERROR [oks-copy.sh]: failed to get oks get repository'
  exit 1
fi

########################################################################################################################

trace=0
source=''
destination=''
hash=''

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      ;;

    -s | --source)
      shift
      source="$1"
      ;;

    -d | --destination)
      shift
      destination="$1"
      ;;
      
    -c | --commit-hash | --hash)
      shift
      hash="$1"
      ;;

    -h* | --he*)
      echo 'Usage: oks-copy.sh -s source-dir -d destination-dir -c commit-hash [-h]'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose       trace this script execution'
      echo '   -s | --source        existing repository directory'
      echo '   -d | --destination   destination repository directory'
      echo '   -c | --commit-hash   checkout repository with given commit hash'
      echo '   -h | --help          print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS copy utility allows to copy git repository files and directories into a new location for update.'
      echo ''
      exit 0
      ;;
  esac
  shift
done


if [ -z "${source}" ] 
then
  echo "ERROR [oks-copy.sh]: the source directory is not defined"
  exit 1
fi

if [ -z "${destination}" ] 
then
  echo "ERROR [oks-copy.sh]: the destination directory is not defined"
  exit 1
fi

########################################################################################################################

echo "cd ${destination}"
cd "${destination}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-copy.sh]: cannot change directory to ${destination}"
  exit 1
fi

echo "git clone -q -n --reference ${source} ${git_repo} ."
git clone -q -n --reference ${source} ${git_repo} .

if [ $? -ne 0 ]
then
  echo "ERROR [oks-copy.sh]: git clone failed"
  exit 1
fi

echo "git checkout -q -B master ${hash}"
git checkout -q -B master ${hash}

if [ $? -ne 0 ]
then
  echo "ERROR [oks-copy.sh]: git checkout failed"
  exit 1
fi

echo "checkout oks version `git rev-parse HEAD`"

########################################################################################################################
```

### `scripts/oks-diff.sh`  
*Local path: `repo/oks/scripts/oks-diff.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

trace=0
unmerged=0
sha1=''
sha2=''

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      ;;

    -n | --unmerged)
      unmerged=1
      ;;

    -s | --sha)
      shift
      sha1="$1"
      shift
      sha2="$1"
      ;;

    -h* | --he*)
      echo 'Usage: oks-diff.sh [-v] [-u user-repository-dir] [--unmerged] [--sha sha1 sha2] [-h]'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose          trace this script execution'
      echo '   -u | --user-rep-dir     define user repository directory'
      echo '   -n | --unmerged         show names of unmerged files'
      echo '   -s | --sha sha1 sha2    show names of files modified between revisions sha1 and sha2'
      echo '   -h | --help             print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS diff utility shows unmerged files or files modified between revisions.'
      echo '   The variable TDAQ_DB_USER_REPOSITORY can be used to define the user database repository.'
      echo ''
      exit 0
      ;;

    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-diff]: export TDAQ_DB_USER_REPOSITORY=$TDAQ_DB_USER_REPOSITORY"
      fi
      ;;
  esac
  shift
done

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-diff.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

if [ $trace -eq 1 ]
then
  echo " -> [oks-diff.sh]: cd ${TDAQ_DB_USER_REPOSITORY}"
fi

########################################################################################################################

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-diff.sh]: cannot change directory to TDAQ_DB_USER_REPOSITORY"
  exit 1
fi

########################################################################################################################

opts=''

if [ "$unmerged" -eq 1 ]
then
  opts="--diff-filter=U"
elif [ ! -z $sha2 ]
then
  opts="--diff-filter=M $sha1 $sha2"
  echo "git fetch --all"
  git fetch --all
  if [ $? -ne 0 ]
  then
	echo "ERROR [oks-diff.sh]: git fetch has failed"
	exit 1
  fi
else
  echo "ERROR [oks-diff.sh]: choose unmerged or sha option"
  exit 1
fi

########################################################################################################################

echo "git diff --name-only $opts"
git diff --name-only $opts
if [ $? -ne 0 ]
then
	echo "ERROR [oks-diff.sh]: git diff has failed"
	exit 1
fi

########################################################################################################################
```

### `scripts/oks-edit-branch.sh`  
*Local path: `repo/oks/scripts/oks-edit-branch.sh`*

```sh
#!/bin/sh

########################################################################################################################

path=''
create_path=''
editor='vim'
branch=''
log_message=''
commit=0

########################################################################################################################

# An error exit function

cleanup()
{
  if [ ! -z ${create_path} ]
  then
    echo "clean temporary repository area ${create_path}"
    rm -rf ${create_path}
  fi

}

error_exit()
{
  echo "ERROR [oks-edit-branch.sh]: $1" 1>&2
  cleanup
  exit 1
}

########################################################################################################################

if [ -z ${TDAQ_DB_REPOSITORY} ]
then
  error_exit 'oks git repository is not set; set TDAQ_DB_REPOSITORY or use oks-git-on'
fi

if [ ! -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  error_exit 'unset $TDAQ_DB_USER_REPOSITORY'
fi

if [ ! -z ${TDAQ_DB_VERSION} ]
then
  error_exit ' unset TDAQ_DB_VERSION'
fi


########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -c | --commit-anyway)
      commit=1
      ;;

    -p | --path)
      shift
      path="$1"
      ;;

    -e | --editor)
      shift
      editor="$1"
      ;;

    -m | --message)
      shift
      log_message="$1"
      ;;

    -b | --branch)
      shift
      branch="$1"
      ;;

    -h | --help)
      echo 'Usage: oks-edit-branch.sh [-c] [-p directory] [-e editor] [-m \"log message\"] -b branch file+'
      echo ''
      echo 'Arguments/Options:'
      echo '   -c | --commit-anyway  commit changes immediately after successful termination of the editor process; ask user otherwise'
      echo '   -p | --path           define existing empty repository directory; create temporary one otherwise'
      echo "   -e | --editor         specify name of text or config editor [default: \"$editor\"]"
      echo '   -b | --branch         branch name (new or already existing)'
      echo '   -m | --message        commit log message; ask user if not provided'
      echo '   -h | --help           print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS edit branch utility allows to create new or checkout existing git branch, modify and commit changes into it.'
      echo '   The TDAQ_DB_REPOSITORY process environment variable has to be defined. The TDAQ_DB_USER_REPOSITORY and TDAQ_DB_VERSION'
      echo '   have to be unset. A branch name needs to be provided. If branch does not exist, it will be created.' 
      echo '   At least one existing repository file name needs to be provided. Such file or files will be open in an editor.'
      echo '   An editor can be a text editor or an oks configuration editor. If an editor requires command line options, they can be'
      echo '   passed as well. For example use -e "dbe -f" to start dbe with -f option, or -e "oks_data_editor --no-message-window" to'
      echo '   redirect output of oks data editor to standard out.'
      echo ''
      exit 0
      ;;

    *)
      file="$@"
      break
      ;;
  esac
  shift
done

if [ ! -v file ]
then
  error_exit 'there is no any file provided'
fi

for f in $file
do
  echo $f
done

if [ -z ${branch} ]
then
  error_exit 'there is no branch name parameter'
fi


########################################################################################################################

if [ -z "${path}" ]
then
  pushd `mktemp -d`
  create_path=`pwd`
else
  pushd "${path}" || error_exit "cannot cd ${path}"
fi

echo "cd `pwd`"

echo "oks_clone_repository -o . -b ${branch}"
oks_clone_repository -o . -b "${branch}" || error_exit 'cannot clone oks git repository'

echo TDAQ_DB_USER_REPOSITORY=`pwd` $editor $file
TDAQ_DB_USER_REPOSITORY=`pwd` $editor $file || error_exit 'editor failed'

########################################################################################################################

if [ $commit -eq 0 ]
then
  message="Your changes have not been committed to GIT.\nDo you want to commit now?\nIf you do, then, please, follow instructions on terminal."

  if hash kdialog 2> /dev/null; then
    kdialog --title="oks-edit-branch" --warningyesno "$message" 1>/dev/null 2>&1
    result=$?
    if [ $result -eq 0 ]; then
       commit=1
    fi
  elif hash zenity 2> /dev/null; then
    zenity --ellipsize --title="oks-edit-branch" --question --text="$message" 1>/dev/null 2>&1
    result=$?
    if [ $result -eq 0 ]; then
       commit=1
    fi    
  else    
    while true; do
       read -p "Do you wish commit changes? " answer
       case $answer in
       [Yy]* ) commit=1; break;;
       [Nn]* ) break;;
       * ) echo "Please answer yes or no.";;
       esac
    done
  fi
fi

if [ $commit -eq 0 ]
then
  echo 'exit without committing to git'
  cleanup
  exit 0
fi

########################################################################################################################

commit_cmd='oks-commit.sh -u `pwd`'

if [ ! -z "${log_message}" ]
then
  commit_cmd="${commit_cmd} -m \"${log_message}\""
else
  commit_cmd="${commit_cmd} -f /dev/null"
fi

########################################################################################################################

echo "$commit_cmd"
eval "$commit_cmd" || error_exit 'commit failed'

########################################################################################################################
```

### `scripts/oks-import.sh`  
*Local path: `repo/oks/scripts/oks-import.sh`*

```sh
#!/bin/sh

########################################################################################################################

if [ -z "${TDAQ_DB_REPOSITORY}" ]
then
  echo 'ERROR [oks-import.sh]: variable TDAQ_DB_REPOSITORY is not set'
  exit 1
fi

git_repo=`oks_git_repository`

if [ -z "${git_repo}" ]
then
  echo 'ERROR [oks-import.sh]: failed to get oks get repository'
  exit 1
fi

########################################################################################################################

trace=0
update=1
message=''
file=''

user_files="/tmp/oks.import.`whoami`.$$.txt"

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      echo " -> [oks-import.sh]: git repository: ${git_repo}"
      ;;

    -n | --dry-run)
      update=0
      ;;

    -m | --message)
      shift
      message="$1"
      ;;

    -f | '--file')
      shift
      file="$1"
      ;;

    -h* | --he*)
      echo 'Usage: oks-import.sh [-v] [-t] [-n] -m message | -f commit-message-file what ...'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose       trace this script execution'
      echo '   -n | --dry-run       print commands to update git repository, but do not commit'
      echo '   -m | --message       commit message'
      echo '   -f | --file          take the commit message from the given file'
      echo '   -h | --help          print this message'
      echo '   what+                list of directories and files to be imported'
      echo ''
      echo 'Description:'
      echo '   Import files into OKS git repository.'
      echo '   Only new and different files will be imported.'
      echo ''
      echo '   The current working directory has to correspond to repository root, e.g.:'
      echo '     bash$ cd ${TDAQ_INST_PATH}/share/data'
      echo '     bash$ oks-import.sh -m "commit message" daq/schema daq/sw/*.data.xml daq/segments/common-environment.data.xml'
      echo '   or:'
      echo '     bash$ cd /atlas/oks/tdaq-09-00-00'
      echo '     bash$ oks-import.sh -m "commit message" det-x'
      echo ''
      exit 0
      ;;

    *)
      if [ -d "$1" ]
      then
        echo find "$1" -name '*.xml'
        find "$1" -name '*.xml' >> $user_files
      elif [ -f "$1" ]
      then
        echo "$1" >> $user_files
      else
        echo "ERROR: parameter $1 is not directory or file"
        exit 1
      fi

  esac
  shift
done

src_path=`pwd`

if [ -z "${message}" ] && [ -z "${file}" ]
then
    echo "ERROR [oks-import.sh]: there is no commit message or file with commit message"
	exit 1
fi

if [ ! -f "$user_files" ]
then
  echo "ERROR [oks-import.sh]: there are no files for import"
  exit 1
fi	

########################################################################################################################
#Sort user files

user_files2="$user_files.tmp"
cat "$user_files" | sort -u > $user_files2
mv "$user_files2" "$user_files"

if [ $trace -eq 1 ]
then
  echo '-------------------------------------------------------------------'
  echo 'User files:'
  cat "$user_files"
  echo '-------------------------------------------------------------------'
fi


########################################################################################################################

work_dir=`mktemp -d --tmpdir oks.import.XXXXXX`

echo "create working area directory ${work_dir}"

echo "git clone ${git_repo} ${work_dir}"
git clone "${git_repo}" ${work_dir}

if [ $? -ne 0 ]
then
  echo "ERROR [oks-import.sh]: git clone has failed"
  exit 1
fi

cleanup_git_repo()
{
	echo "rm -rf ${work_dir}"
	rm -rf ${work_dir}
	echo "rm -f ${user_files}"
	rm -f ${user_files}
}

trap cleanup 1 2 3 6

cleanup()
{
	cleanup_git_repo
    echo "Done cleanup ... quitting."
    exit 1
}

echo '-------------------------------------------------------------------'
echo "Database git repository: ${git_repo}"
echo "User repository area: ${work_dir}"

########################################################################################################################

echo 'Process user files:'

old_tdaq_db_repo=${TDAQ_DB_REPOSITORY}
unset TDAQ_DB_REPOSITORY

TDAQ_DB_PATH=${src_path}:${work_dir}
export TDAQ_DB_PATH

for f in `cat $user_files`
do
  rf="${work_dir}/$f"
	    
  if [ -f ${rf} ]
  then
    diff -q -B -I '^<info name=' -I '^ <comment ' -I '^<comments>' -I '^</comments>' $f $rf > /dev/null
    if [ $? -eq 0 ]
    then
      echo " [=] file $f exists in repository and there is no difference"
    else
      echo " [~] file $f exists in repository and is different"
      echo "   cp -f ${src_path}/$f $rf"
      cp -f ${src_path}/$f $rf
    fi
  else
    echo " [+] file $f does not exist in repository"
    echo "   mkdir -p $(dirname $rf) && cp -f ${src_path}/$f $rf"
    mkdir -p $(dirname $rf) && cp -f ${src_path}/$f $rf
  fi
done

########################################################################################################################

if [ $update -eq 1 ]
then
  TDAQ_DB_REPOSITORY=${old_tdaq_db_repo}
  export TDAQ_DB_REPOSITORY
    
if [ -z "${file}" ]
  then
  	echo "oks-commit.sh -u ${work_dir} -m \"${message}\""
    oks-commit.sh -u ${work_dir} -m "${message}"
  else
    echo "oks-commit.sh -u ${work_dir} -f \"${file}\""
    oks-commit.sh -u ${work_dir} -f "${file}"
  fi
fi

########################################################################################################################

cleanup_git_repo
exit 0

########################################################################################################################
```

### `scripts/oks-log.sh`  
*Local path: `repo/oks/scripts/oks-log.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

trace=0
since=''
until=''
num=''
args=''

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      ;;

    -h* | --he*)
      echo 'Usage: oks-log.sh [-v] [-u user-repository-dir] [-h] ...'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose       trace this script execution'
      echo '   -u | --user-rep-dir  define user repository directory'
      echo '   -h | --help          print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS log utility shows the details of git repository commit logs (hash, author, date and updated files).'
      echo '   The variable TDAQ_DB_USER_REPOSITORY defines the user database repository.'
      echo ''
      exit 0
      ;;

    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-log.sh]: export TDAQ_DB_USER_REPOSITORY=$TDAQ_DB_USER_REPOSITORY"
      fi
      ;;

    *)
      break
      ;;

  esac
  shift
done

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-log.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

if [ $trace -eq 1 ]
then
  echo " -> [oks-log.sh]: cd ${TDAQ_DB_USER_REPOSITORY}"
fi

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-log.sh]: cannot change directory to TDAQ_DB_USER_REPOSITORY"
  exit 1
fi

########################################################################################################################

echo "git fetch --all"
git fetch --all

if [ $? -ne 0 ]
then
	echo "ERROR [oks-log.sh]: git fetch has failed"
	exit 1
fi

echo "git log -m --date=raw --pretty=format:'%H|%an|%ad|%s' --first-parent ${TDAQ_DB_BRANCH:-master} --name-only $@"
git log -m --date=raw --pretty=format:"%H|%an|%ad|%s" --first-parent ${TDAQ_DB_BRANCH:-master} --name-only $@

if [ $? -ne 0 ]
then
	echo "ERROR [oks-log.sh]: git log has failed"
	exit 1
fi

########################################################################################################################
```

### `scripts/oks-status.sh`  
*Local path: `repo/oks/scripts/oks-status.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      ;;

    -h* | --he*)
      echo 'Usage: oks-status.sh [-u user-repository-dir] [-h]'
      echo ''
      echo 'Arguments/Options:'
      echo '   -u | --user-rep-dir  define user repository directory'
      echo '   -h | --help          print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS git status utility allows to get list of updated, removed and added repository files.'
      echo '   The variable TDAQ_DB_USER_REPOSITORY defines the user database repository.'
      echo ''
      exit 0
      ;;
  esac
  shift
done

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-status.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-status.sh]: cannot change directory to user repository ${TDAQ_DB_USER_REPOSITORY}"
  exit 1
fi

########################################################################################################################

echo "git status --porcelain"
ff=`git status --porcelain`

if [ $? -ne 0 ]
then
  echo "ERROR [oks-status.sh]: git status has failed with code $?"
  exit 1
fi

if [ ! -z "$ff" ]
then
  echo "$ff" | grep '\.xml$'
fi

exit 0

########################################################################################################################
```

### `scripts/oks-tag.sh`  
*Local path: `repo/oks/scripts/oks-tag.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

trace=0
tag=''
sha=''

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      ;;

    -h* | --he*)
      echo 'Usage: oks-tag.sh [-v] [-u user-repository-dir] [-h] -c sha -t tag'
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose       trace this script execution'
      echo '   -u | --user-rep-dir  define user repository directory'
      echo '   -c | --commit-hash   the commit checksum to be tagged'
      echo '   -t | --tag           the tag name'
      echo '   -h | --help          print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS tag utility can be used to tag existing commit.'
      echo '   The variable TDAQ_DB_USER_REPOSITORY defines the user database repository.'
      echo ''
      exit 0
      ;;

    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-tag.sh]: export TDAQ_DB_USER_REPOSITORY=$TDAQ_DB_USER_REPOSITORY"
      fi
      ;;

    -t | --tag)
      shift
      tag="$1"
      ;;

    -c | --commit-hash)
      shift
      sha="$1"
      ;;

    *)
      break
      ;;

  esac
  shift
done

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-tag.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

if [ $trace -eq 1 ]
then
  echo " -> [oks-tag.sh]: cd ${TDAQ_DB_USER_REPOSITORY}"
fi

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-tag.sh]: cannot change directory to TDAQ_DB_USER_REPOSITORY"
  exit 1
fi

if [ -z "${sha}" ]
then
	echo "ERROR [oks-tag.sh]: the commit hash is not set"
	exit 1
fi

if [ -z "${tag}" ]
then
	echo "ERROR [oks-tag.sh]: the commit tag is not set"
	exit 1
fi


########################################################################################################################

echo "git tag ${tag} ${sha}"
git tag "${tag}" "${sha}"

if [ $? -ne 0 ]
then
	echo "ERROR [oks-tag.sh]: git tag has failed"
	exit 1
fi

echo "git push origin ${tag}"
git push origin "${tag}"

if [ $? -ne 0 ]
then
	echo "ERROR [oks-tag.sh]: git push has failed"
	exit 1
fi


########################################################################################################################
```

### `scripts/oks-update.sh`  
*Local path: `repo/oks/scripts/oks-update.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

trace=0
hash=''
tag=''
date=''
option=''

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -v | --verbose)
      trace=1
      ;;

    -f | --discard* | --force*)
      option=' --force'
      ;;

    -m | --merge*)
      option=' --merge'
      ;;

    -h* | --he*)
      echo 'Usage: oks-update.sh [-v] [-u user-repository-dir] [-c commit-hash] [-t tag] [-d date] [-f | -m] [-h] '
      echo ''
      echo 'Arguments/Options:'
      echo '   -v | --verbose            trace this script execution'
      echo '   -u | --user-rep-dir       define user repository directory'
      echo '   -c | --commit-hash        checkout repository with given commit hash'
      echo '   -t | --tag                checkout repository with given tag'
      echo '   -d | --date               checkout repository for given timestamp'
      echo '   -f | --force | --discard  discard local changes (force update)'
      echo '   -m | --merge              merge changes'
      echo '   -h | --help               print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS update utility allows to update files and directories in user git repository.'
      echo '   Without options it updates to HEAD of the master branch.'
      echo '   Otherwise options allow to choose concrete commit hash, tag or timestamp.'
      echo '   The variable TDAQ_DB_USER_REPOSITORY defines the user database repository.'
      echo ''
      exit 0
      ;;

    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-update.sh]: export TDAQ_DB_USER_REPOSITORY=$TDAQ_DB_USER_REPOSITORY"
      fi
      ;;

    -t | --tag)
      shift
      tag="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-update.sh]: tag: ${tag}"
      fi
      ;;

    -d | --date)
      shift
      date="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-update.sh]: date: ${date}"
      fi
      ;;

    -c | --commit-hash | --hash)
      shift
      hash="$1"
      if [ $trace -eq 1 ]
      then
        echo " -> [oks-update.sh]: commit hash: ${hash}"
      fi
      ;;

  esac
  shift
done

if [ ! -z "${hash}" ] && [ ! -z "${tag}" ]
then
	echo "ERROR [oks-update.sh]: cannot use commit-hash and tag parameters simultaneously"
	exit 1
fi

if [ ! -z "${hash}" ] && [ ! -z "${date}" ]
then
	echo "ERROR [oks-update.sh]: cannot use commit-hash and date parameters simultaneously"
	exit 1
fi

if [ ! -z "${tag}" ] && [ ! -z "${date}" ]
then
	echo "ERROR [oks-update.sh]: cannot use tag and date parameters simultaneously"
	exit 1
fi


if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-update.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

if [ $trace -eq 1 ]
then
  echo " -> [oks-update.sh]: cd ${TDAQ_DB_USER_REPOSITORY}"
fi

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-update.sh]: cannot change directory to TDAQ_DB_USER_REPOSITORY"
  exit 1
fi

########################################################################################################################

git_cmd="git checkout${option}"

if [ ! -z "${tag}" ]
then
	echo "${git_cmd} -q tags/${tag}"
	${git_cmd} -q tags/${tag}
	if [ $? -ne 0 ]
	then
		echo "ERROR [oks-update.sh]: git checkout has failed"
		exit 1
	fi
else
	if [ ! -z "${date}" ]
	then
		if [ $trace -eq 1 ]
		then
			echo " -> [oks-update.sh]: calculate commit hash for date ${date}: git rev-list -1 --before="${date}" master"
		fi
		
		hash=$(git rev-list -1 --before="${date}" master)
		
		if [ $? -ne 0 ]
		then
			echo "ERROR [oks-update.sh]: git rev-list has failed"
			exit 1
		fi
	fi


	if [ ! -z "${hash}" ] && [ ! "${hash}" == "origin/master" ]
	then
	    echo "${git_cmd} -q -B master ${hash}"
	    ${git_cmd} -q -B master ${hash}
	    if [ $? -ne 0 ]
	    then
		    echo "ERROR [oks-update.sh]: git checkout has failed"
		    exit 1
	    fi
    else
    	echo "${git_cmd} -q -B master origin/master"
    	${git_cmd} -q -B master origin/master
	    if [ $? -ne 0 ]
	    then
		    echo "ERROR [oks-update.sh]: git checkout has failed"
		    exit 1
	    fi
    fi
fi


if [ $trace -eq 1 ]
then
  echo " -> [oks-update.sh]: update completed"
fi

echo "update oks version `git rev-parse HEAD`"

########################################################################################################################
```

### `scripts/oks-version.sh`  
*Local path: `repo/oks/scripts/oks-version.sh`*

```sh
#!/bin/sh

########################################################################################################################

PATH=$PATH:/bin:/usr/bin:/usr/local/bin
export PATH

########################################################################################################################

while (test $# -gt 0)
do
  case "$1" in
    -u* | --user-re*)
      shift
      TDAQ_DB_USER_REPOSITORY="$1"
      export TDAQ_DB_USER_REPOSITORY
      ;;

    -h* | --he*)
      echo 'Usage: oks-version.sh [-u user-repository-dir] [-h]'
      echo ''
      echo 'Arguments/Options:'
      echo '   -u | --user-rep-dir  define user repository directory'
      echo '   -h | --help          print this message'
      echo ''
      echo 'Description:'
      echo '   The OKS version utility allows to read GIT revision of the oks repository'
      echo ''
      exit 0
      ;;
  esac
  shift
done

if [ -z ${TDAQ_DB_USER_REPOSITORY} ]
then
  echo 'ERROR [oks-version.sh]: user repository is not set; use TDAQ_DB_USER_REPOSITORY or -u option'
  exit 1
fi

########################################################################################################################

cd "${TDAQ_DB_USER_REPOSITORY}"

if [ $? -ne 0 ]
then
  echo "ERROR [oks-version.sh]: cannot change directory to user repository ${TDAQ_DB_USER_REPOSITORY}"
  exit 1
fi

########################################################################################################################

echo "oks version `git rev-parse HEAD`"

########################################################################################################################
```

### Tests
`test/all_types.schema.xml` defines a schema exercising all OKS attribute types; `test/test.data.xml` is a data file for it (note the `oks-version` value `"oks-08-04-00-3-g816241d built "Aug 29 2024""` in its `<info>` element — the version is a git describe string); `test/test_update.cpp` tests the update-data functionality.
### `test/all_types.schema.xml`  
*Local path: `repo/oks/test/all_types.schema.xml`*

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

<info name="" type="" num-of-items="2" oks-format="schema" oks-version="4949f80 built &quot;Jan 31 2024&quot;" created-by="isolov" created-on="pcatddev02.dyndns.cern.ch" creation-time="20240716T163837" last-modified-by="isolov" last-modified-on="pcatddev02" last-modification-time="20240823T110456"/>

 <class name="Container" description="It is a class to describe a department">
  <attribute name="Boolean" type="bool"/>
  <attribute name="IntS8" type="s8"/>
  <attribute name="IntU8" type="u8"/>
  <attribute name="IntS16" type="s16"/>
  <attribute name="IntU16" type="u16"/>
  <attribute name="IntS32" type="s32"/>
  <attribute name="IntU32" type="u32"/>
  <attribute name="IntS64" type="s64"/>
  <attribute name="Int64" type="u64"/>
  <attribute name="Float" type="float"/>
  <attribute name="Double" type="double"/>
  <attribute name="String" type="string"/>
  <attribute name="Date" type="date"/>
  <attribute name="Time" type="time"/>
  <attribute name="Enum" type="enum" range="one,two,three,four,five" init-value="one"/>
  <attribute name="Class" type="class" init-value="Container"/>
  <attribute name="ArrayBoolean" type="bool" is-multi-value="yes"/>
  <relationship name="Root" description="A department has zero or many employess" class-type="Element" low-cc="one" high-cc="one" is-composite="no"/>
  <relationship name="Contains" description="A department has zero or many employess" class-type="Element" low-cc="zero" high-cc="many" is-composite="no"/>
 </class>

 <class name="Element" description="It is a class to describe a person">
  <attribute name="Boolean" type="bool"/>
  <attribute name="IntS8" type="s8"/>
  <attribute name="IntU8" type="u8"/>
  <attribute name="IntS16" type="s16"/>
  <attribute name="IntU16" type="u16"/>
  <attribute name="IntS32" type="s32"/>
  <attribute name="IntU32" type="u32"/>
  <attribute name="IntS64" type="s64"/>
  <attribute name="Int64" type="u64"/>
  <attribute name="Float" type="float"/>
  <attribute name="Double" type="double"/>
  <attribute name="String" type="string"/>
  <attribute name="Date" type="date"/>
  <attribute name="Time" type="time"/>
  <attribute name="Enum" type="enum" range="one,two,three,four,five" init-value="one"/>
  <attribute name="Class" type="class" init-value="Container"/>
  <attribute name="ArrayBoolean" type="bool" is-multi-value="yes"/>
  <attribute name="ArrayIntS8" type="s8" is-multi-value="yes"/>
  <attribute name="ArrayIntU8" type="u8" is-multi-value="yes"/>
  <attribute name="ArrayIntS16" type="s16" is-multi-value="yes"/>
  <attribute name="ArrayIntU16" type="u16" is-multi-value="yes"/>
  <attribute name="ArrayIntS32" type="s32" is-multi-value="yes"/>
  <attribute name="ArrayIntU32" type="u32" is-multi-value="yes"/>
  <attribute name="ArrayIntS64" type="s64" is-multi-value="yes"/>
  <attribute name="ArrayInt64" type="u64" is-multi-value="yes"/>
  <attribute name="ArrayFloat" type="float" is-multi-value="yes"/>
  <attribute name="ArrayDouble" type="double" is-multi-value="yes"/>
  <attribute name="ArrayString" type="string" is-multi-value="yes"/>
  <attribute name="ArrayDate" type="date" is-multi-value="yes"/>
  <attribute name="ArrayTime" type="time" is-multi-value="yes"/>
  <attribute name="ArrayEnum" type="enum" range="one,two,three,four,five" is-multi-value="yes" init-value="one"/>
  <attribute name="ArrayClass" type="class" is-multi-value="yes"/>
  <attribute name="HexIntU8" type="u8" format="hex"/>
  <attribute name="HexIntU16" type="u16" format="hex"/>
  <attribute name="HexIntU32" type="u32" format="hex"/>
  <attribute name="HexIntU64" type="u64" format="hex"/>
  <attribute name="HexArrayIntU8" type="u8" format="hex" is-multi-value="yes"/>
  <attribute name="HexArrayIntU16" type="u16" format="hex" is-multi-value="yes"/>
  <attribute name="HexArrayIntU32" type="u32" format="hex" is-multi-value="yes"/>
  <attribute name="HexArrayIntU64" type="u64" format="hex" is-multi-value="yes"/>
 </class>

</oks-schema>
```

### `test/test.data.xml`  
*Local path: `repo/oks/test/test.data.xml`*

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

<info name="" type="" num-of-items="3" oks-format="data" oks-version="oks-08-04-00-3-g816241d built &quot;Aug 29 2024&quot;" created-by="isolov" created-on="pcatddev02" creation-time="20240809T150705" last-modified-by="isolov" last-modified-on="pcatddev02" last-modification-time="20240829T104929"/>

<include>
 <file path="all_types.schema.xml"/>
</include>

<comments>
 <comment creation-time="20240809T150955" created-by="isolov" created-on="pcatddev02" author="Unknown" text="first comment"/>
</comments>

<obj class="Container" id="o1-good-container">
 <attr name="Date" type="date" val="20240829"/>
 <attr name="Time" type="time" val="20240829T104831"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <rel name="Root" class="Element" id="o1-good"/>
 <rel name="Contains">
  <ref class="Element" id="o1-good"/>
  <ref class="Element" id="o1-bad-container"/>
 </rel>
</obj>

<obj class="Container" id="o1-bad-container">
 <attr name="Date" type="date" val="20240829"/>
 <attr name="Time" type="time" val="20240829T104831"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <rel name="Root" class="Element" id="o1-bad-unknown-attributes"/>
 <rel name="Contains">
  <ref class="Element" id="o1-good2"/>
  <ref class="Element" id="o1-no-exist"/>
 </rel>
</obj>

<obj class="Container" id="o2-bad-container-mv-stored-as-sv">
 <attr name="Date" type="date" val="20240829"/>
 <attr name="Time" type="time" val="20240829T104831"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <rel name="Root" class="Element" id="o1-bad-unknown-attributes"/>
 <rel name="Contains" class="Element" id="o1-good"/>
</obj>

<obj class="Container" id="o3-bad-container-sv-stored-as-nv">
 <attr name="Class" type="class" val="Container"/>
 <rel name="Root">
  <ref class="Element" id="o1-good"/>
 </rel>
 <rel name="Contains">
  <ref class="Element" id="o1-good"/>
  <ref class="Element" id="o1-no-exist"/>
 </rel>
</obj>

<obj class="Container" id="o4-bad-container-mv-stored-as-sv">
 <attr name="Date" type="date" val="20240829"/>
 <attr name="Time" type="time" val="20240829T104831"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <rel name="Root" class="Element" id="o1-bad-unknown-attributes"/>
 <rel name="Contains" class="Element" id="o1-good"/>
</obj>

<obj class="Container" id="o5-bad-container-sv-stored-as-nv">
 <attr name="Class" type="class" val="Container"/>
 <rel name="Root">
  <ref class="Element" id="o1-good"/>
 </rel>
 <rel name="Contains">
  <ref class="Element" id="o1-good"/>
  <ref class="Element" id="o1-no-exist"/>
 </rel>
</obj>

<obj class="Element" id="o1-bad-unknown-attributes">
 <attr name="IntS8" type="s8" val="1"/>
 <attr name="UnknownIntS8" type="s8" val="1"/>
 <attr name="UnknownIntS64" type="s64" val="-10000000000"/>
 <attr name="IntS16" type="s8"/>
 <!-- <attr name="IntU16" val="1"/> -->
 <attr name="Date" type="date" val="20240827"/>
 <attr name="Time" type="time" val="20240827T132603"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <attr name="UnknownEmptyArrayIntS8" type="s8">
 </attr>
 <attr name="UnknownEmptyArrayIntU8" type="u8"/>
 <attr name="UnknownArrayIntS8" type="s8">
  <data val="1"/>
  <data val="-1"/>
 </attr>
 <attr name="ArrayTime" type="time"/>
 <attr name="ArrayEnum" type="enum">
  <data val="one"/>
 </attr>
</obj>

<obj class="Element" id="o2-bad-mv-attribute-stored-as-sv">
 <attr name="Date" type="date" val="20240827"/>
 <attr name="Time" type="time" val="20240827T132603"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <attr name="ArrayIntS8" type="s8" val="1"/>
 <!-- <attr name="ArrayIntS16" type="s16" val=""/> -->
 <attr name="ArrayEnum" type="enum">
  <data val="one"/>
 </attr>
</obj>

<obj class="Element" id="o3-bad-sv-attribute-stored-as-mv">
 <attr name="IntU8" type="u8">
  <data val="111"/>
 </attr>
 <attr name="IntS8" type="s8" val="127"/>
</obj>

<obj class="Element" id="o5-good-special-symbols">
 <attr name="String" type="string" val=" &#xA;quote: &apos;&#xA;double quotes: &quot;&#xA;amp: &amp;&#xA;hash: #&#xA;double hash: ##&#xA;many symbols: &apos;&quot;,#&amp;&amp;#,&quot;"/>
</obj>

<obj class="Element" id="o1-good">
 <attr name="Boolean" type="bool" val="1"/>
 <attr name="IntS8" type="s8" val= "-128"/>
 <attr name="IntU8" type="u8" val="127" />
 <attr name="IntS16" type="s16" val="-999"/>
 <attr name="IntU16" type="u16" val="50000"/>
 <attr name="IntS32" type="s32" val="-1"/>
 <attr name="IntU32" type="u32" val="1"/>
 <attr name="IntS64" type="s64" val="-10000000000"/>
 <attr name="Int64" type="u64" val="1000000000000"/>
 <attr name="Float" type="float" val="3.1415"/>
 <attr name="Double" type="double" val="2.1928"/>
 <attr name="String" type="string" val="The quick brown fox jumps over the lazy dog."/>
 <attr name="Date" type="date" val="20240809"/>
 <attr name="Time" type="time" val="20240809T150647"/>
 <attr name="Enum" type="enum" val="one"/>
 <attr name="Class" type="class" val="Container"/>
 <attr name="ArrayIntS8" type="s8">
  <data val="1"/>
  <data val="-1"/>
  <data val="2"/>
  <data val="-2"/>
  <data val="-127"/>
  <data val="127"/>
  <data val="0"/>
 </attr>
 <attr name="ArrayIntU8" type="u8">
  <data val="1"/>
  <data val="2"/>
  <data val="4"/>
  <data val="8"/>
  <data val="16"/>
  <data val="32"/>
  <data val="64"/>
  <data val="128"/>
  <data val="255"/>
  <data val="0"/>
 </attr>
 <attr name="ArrayString" type="string">
  <data val="The"/>
  <data val="quick"/>
  <data val="brown"/>
  <data val="fox"/>
  <data val="jumps"/>
  <data val="over"/>
  <data val="the"/>
  <data val="lazy"/>
  <data val="dog"/>
 </attr>
 <attr name="ArrayDate" type="date"/>
 <attr name="ArrayTime" type="time"/>
 <attr name="ArrayEnum" type="enum">
  <data val="one"/>
 </attr>
 <attr name="HexIntU8" type="u8" val="0xff"/>
 <attr name="HexIntU16" type="u16" val="0x1"/>
 <attr name="HexIntU32" type="u32" val="0xffffffff"/>
 <attr name="HexIntU64" type="u64" val="0x123456789abcdef"/>
 <attr name="HexArrayIntU16" type="u16">
  <data val="0x100"/>
  <data val="0xff"/>
 </attr>
</obj>

</oks-data>
```

### `test/test_update.cpp`  
*Local path: `repo/oks/test/test_update.cpp`*

```cpp
/**
 *  \file oks_dump.cpp
 *
 *  This file is part of the OKS package.
 *  Author: <Igor.Soloviev@cern.ch>
 *
 *  This file contains the implementation of the OKS application to dump
 *  contents of the OKS database files.
 *
 */

#include <vector>
#include <iostream>

#include <string.h>
#include <stdlib.h>

#include <oks/relationship.h>
#include <oks/kernel.h>
#include <oks/exceptions.h>


enum __OksDumpExitStatus__ {
  __Success__ = 0,
  __BadCommandLine__,
  __ExceptionCaught__
};

int
main(int argc, char **argv)
{
  if(argc < 3) {
    std::cerr << "provide \"data file name\", \"test number\" and optional parameter\n";
    return __BadCommandLine__;
  }

  try {
      OksKernel k;
      auto f = k.load_file(argv[1]);
      auto i = atoi(argv[2]);
      const char * param = (argc > 3 ? argv[3] : nullptr);
      const char * param2 = (argc > 4 ? argv[4] : nullptr);
      const char * param3 = (argc > 5 ? argv[5] : nullptr);
      const char * param4 = (argc > 6 ? argv[6] : nullptr);
      const char * param5 = (argc > 7 ? argv[7] : nullptr);

      if (i == 1)
        {
          if (argc != 4)
            {
              std::cerr << "provide \"data file name\", \"test number\" and optional parameter\n";
              return __BadCommandLine__;
            }

          std::cout << "[TEST]: add include \"" << param << "\"\n";
          f->add_include_file(param);
        }
      else if (i == 2)
        {
          if (!f->get_include_files().empty())
            {
              auto include = *f->get_include_files().begin();
              std::cout << "[TEST]: remove include \"" << include << "\"\n";
              f->remove_include_file(include);
            }
        }
      else if (i == 3)
        {
          if (!f->get_include_files().empty())
            {
              auto old_include = *f->get_include_files().begin();
              std::cout << "[TEST]: rename include \"" << old_include << "\" to \"" << param << "\"\n";
              f->remove_include_file(old_include);
              f->add_include_file(param);
            }
        }
      else if (i == 11)
        {
          if (argc != 5)
            {
              std::cerr << "provide \"data file name\", \"test number\" and two parameters: author and text\n";
              return __BadCommandLine__;
            }

          std::cout << "[TEST]: add comment author=\"" << param << "\" and text=\"" << param2 << "\"\n";

          f->add_comment(param2, param);
        }
      else if (i == 12)
        {
          if (argc != 4)
            {
              std::cerr << "provide \"data file name\", \"test number\" and one parameters: number of comments to be removed\n";
              return __BadCommandLine__;
            }

          auto n = atoi(param);

          while (n-- > 0 && !f->get_comments().empty())
            {
              const std::string ts = f->get_comments().begin()->first;
              std::cout << "[TEST]: remove comment ts=\"" << ts << "\"\n";
              f->remove_comment(ts);
            }
        }
      else if (i == 13)
        {
          if (argc != 5)
            {
              std::cerr << "provide \"data file name\", \"test number\" and two parameters: author and text\n";
              return __BadCommandLine__;
            }

          if (!f->get_comments().empty())
            {
              const std::string ts = f->get_comments().begin()->first;
              std::cout << "[TEST]: modify comment at \"" << ts << "\" author=\"" << param << "\" and text=\"" << param2 << "\"\n";
              f->modify_comment(ts, param2, param);
            }
        }
      else if (i == 21)
        {
          // 21 class obj attribute new value
          if (argc != 7)
            {
              std::cerr << "update attribute: provide \"data file name\", \"test number\", \"class-name\", \"object-id\", \"attribute-name\", \"value\"\n";
              return __BadCommandLine__;
            }

          if (OksClass* c = k.find_class(param))
            {
              if (OksObject * o = c->get_object(param2))
                {
                  if (OksAttribute * a = c->find_attribute(param3))
                    {
                      OksData d;
                      d.SetValues(param4, a);
                      o->SetAttributeValue(param3, &d);
                    }
                  else
                    {
                      throw std::runtime_error(std::string("Cannot find attribute: ") + param3 + " in class " + param);
                    }
                }
              else
                {
                  throw std::runtime_error(std::string("Cannot find object: ") + param2 + "@" + param);
                }
            }
          else
            {
              throw std::runtime_error(std::string("Cannot find class: ") + param);
            }
        }
      else if (i == 23)
        {
          // 23 class obj attribute new value
          if (argc < 5)
            {
              std::cerr << "new object: provide \"data file name\", \"test number\", \"class-name\", \"object-id1\", [\"object-id1\"*]\n";
              return __BadCommandLine__;
            }

          if (OksClass* c = k.find_class(param))
            {
              k.set_active_data(f);

              for (int idx = 4; idx < argc; ++idx)
                new OksObject(c, argv[idx]);
            }
          else
            {
              throw std::runtime_error(std::string("Cannot find class: ") + param);
            }
        }
      else if (i == 31)
        {
          // 21 class obj attribute new value
          if (argc != 8)
            {
              std::cerr << "update relationship: provide \"data file name\", \"test number\", \"class-name\", \"object-id\", \"attribute-name\", \"class\", \"id\"n";
              return __BadCommandLine__;
            }

          if (OksClass* c = k.find_class(param))
            {
              if (OksObject * o = c->get_object(param2))
                {
                  if (OksRelationship * r = c->find_relationship(param3))
                    {
                      if (OksClass * c2 = k.find_class(param4))
                        {
                          OksData d;

                          if (OksObject * o2 = c2->get_object(param5))
                            d.Set(o2);
                          else
                            d.Set(c2, param5);

                          if (r->get_high_cardinality_constraint() == OksRelationship::Many)
                            {
                              OksData d2(new OksData::List());
                              d2.data.LIST->push_back(&d);
                              o->SetRelationshipValue(param3, &d2);
                              d2.data.LIST->clear(); // avoid delete on "&d"
                            }
                          else
                            {
                              o->SetRelationshipValue(param3, &d);
                            }
                        }
                      else
                        {
                          throw std::runtime_error(std::string("Cannot find class: ") + param4);
                        }
                    }
                  else
                    {
                      throw std::runtime_error(std::string("Cannot find relationship: ") + param3 + " in class " + param);
                    }
                }
              else
                {
                  throw std::runtime_error(std::string("Cannot find object: ") + param2 + "@" + param);
                }
            }
          else
            {
              throw std::runtime_error(std::string("Cannot find class: ") + param);
            }
        }
      k.update_data(f);
  }
  catch (oks::exception & ex) {
    std::cerr << "Caught oks exception:\n" << ex << std::endl;
    return __ExceptionCaught__;
  }
  catch (std::exception & e) {
    std::cerr << "Caught standard C++ exception: " << e.what() << std::endl;
    return __ExceptionCaught__;
  }
  catch (...) {
    std::cerr << "Caught unknown exception" << std::endl;
    return __ExceptionCaught__;
  }

  return __Success__;
}
```

### Java commit hook support
`jsrc/oks/CommitError.java` implements the OKS repository commit error handling for the OKS Java client library.
### `jsrc/oks/CommitError.java`  
*Local path: `repo/oks/jsrc/oks/CommitError.java`*

```java
package oks;

/**
 * Describe properties of an attribute.
 */

public final class CommitError {

	public enum type_t {

		/** no Access Manager permission */
		no_access_manager_permission("Access Manager grants no permission", "\n"),

		/** Access Manager service error */
		access_manager_failure(null /* TODO: reserved for AM service failure */, null),

		/** database is inconsistent or xml syntax error */
		consistency_error("repository validation failed for file", "\nremote: ERROR: oks validation failed"),

		/** cannot merge database changes */
		merge_conflict("Merge conflict in ", "\n"),
		
		/** cannot merge database changes */
		lock_conflict("failed to lock", "\n"),

		/** git service failure */
		git_failure(null /* TODO: reserved for git service failure */, null),

		/** unknown */
		unknown(null, null);

		private final String m_begin_text;
		private final String m_end_text;

		private type_t(String begin_text, String end_text) {
			m_begin_text = begin_text;
			m_end_text = end_text;
	    }
	};

	private String p_commit_log;
	private String p_error;
	private type_t p_type;

	public CommitError(String log) {
		p_commit_log = log;
        p_error = "";
		p_type = type_t.unknown;
		
		for (type_t e : type_t.values()) {
			String s = search(e.m_begin_text, e.m_end_text);

			if (s.isEmpty() == false) {
				p_error = s;
				p_type = e;
			}
		}

	}

	/** Get the commit log */
	public String get_commit_log() {
		return p_commit_log;
	}
	
	/** Get the error text */
	public String get_error_text() {
		return p_error;
	}
	
	/** Get the error type */
	public type_t get_error_type() {
		return p_type;
	}
	
	private String search(String start_text, String end_text) {
		if(start_text == null)
			return "";

		int begin_idx = p_commit_log.indexOf(start_text);

		if (begin_idx == -1)
			return "";

		int end_idx = p_commit_log.indexOf(end_text, begin_idx);
		
		if (end_idx == -1) {
			end_idx = p_commit_log.indexOf('\n', begin_idx);
		}
		
		return (end_idx == -1) ? p_commit_log.substring(begin_idx) : p_commit_log.substring(begin_idx, end_idx);  
	}
}
```

### `jsrc/oks/TestCommitError.java`  
*Local path: `repo/oks/jsrc/oks/TestCommitError.java`*

```java
package oks;

public class TestCommitError {

	public static void main(String args[]) {
		StringBuilder log = new StringBuilder();
		
		// read log from standard input
		java.util.Scanner in = new java.util.Scanner(System.in);
		while (in.hasNextLine()) {
			log.append(in.nextLine());
			log.append("\n");
		}
		in.close();
        
		CommitError error = new CommitError(log.toString());
		
		System.out.println("type: " + error.get_error_type().name());
		System.out.println("error: \"" + error.get_error_text() + "\"");

	}
	
}
```

### `NOTICE`  
*Local path: `repo/oks/NOTICE`*

```text
Copyright (C) 2001-2020 CERN for the benefit of the ATLAS collaboration.
Licensed under the Apache License, version 2.0.

Contributors
============
 Igor Soloviev <Igor.Soloviev@cern.ch>
```

### `LICENSE`  
*Local path: `repo/oks/LICENSE`*

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


## 2. `oks_utils` — examples, tutorial, GUI help and docs (GitLab)

### The 16 API examples (`examples/*.cpp`)
Each example is a self-contained `main()` demonstrating one OKS API facet; all embedded verbatim below: `alloc.cpp` (OksAllocator use), `and_expression.cpp`, `attribute.cpp`, `class.cpp`, `comparator.cpp` (OksQuery::Comparator + equal_cmp), `data.cpp` (OksData), `index.cpp` (OksIndex), `kernel.cpp` (OksKernel + new_data), `method.cpp`, `not_expression.cpp`, `object.cpp`, `or_expression.cpp`, `profiler.cpp`, `query.cpp` (OksQuery from strings: `this (...)`/`all (...)`), `r_expression.cpp` (OksRelationshipExpression), `relationship.cpp`.
### `examples/alloc.cpp`  
*Local path: `repo/oks_utils/examples/alloc.cpp`*

```cpp
#include <sys/time.h>
#include <sys/resource.h>

#include <chrono>
#include <list>
#include <iostream>

#include <boost/pool/pool_alloc.hpp>
#include <tbb/scalable_allocator.h>

  // Normal structure

class Test {
  int i;
  void * p;
};


  // Use Boost pool (with mutexes)

class Test3 : public Test {

public:
  void * operator new(size_t) {return boost::fast_pool_allocator<Test3>::allocate();}
  void operator delete(void *ptr) {boost::fast_pool_allocator<Test3>::deallocate(reinterpret_cast<Test3*>(ptr));}

};


  // Use Boost pool (without mutexes)

class Test4 : public Test {

public:
  void * operator new(size_t) {return boost::fast_pool_allocator<Test4, boost::default_user_allocator_new_delete, boost::details::pool::null_mutex>::allocate();}
  void   operator delete(void *ptr) {boost::fast_pool_allocator<Test4, boost::default_user_allocator_new_delete, boost::details::pool::null_mutex>::deallocate(reinterpret_cast<Test4*>(ptr));}
};

// Use Boost pool (with mutexes)

class Test5 : public Test {

public:
void * operator new(size_t) {return scalable_malloc(sizeof(Test5));}
void operator delete(void *ptr) {scalable_free(ptr);}

};



const size_t ArraySize  =  50000000;
const size_t ListSize   =  50000000;


int main()
{
  size_t count;

  Test  ** t_array  = new Test  * [ArraySize];
  Test3	** t3_array = new Test3 * [ArraySize];
  Test4	** t4_array = new Test4 * [ArraySize];
  Test5 ** t5_array = new Test5 * [ArraySize];

  for(count=0; count < ArraySize; count++) {
    t_array[count] = 0;
    t3_array[count] = 0;
    t4_array[count] = 0;
    t5_array[count] = 0;
  }

  std::cout << "Create and delete " << ArraySize << " objects (" << sizeof(Test) << " bytes per object)\n";

////////////////////////////////////////////////////////////////////////////////

  auto tp = std::chrono::steady_clock::now();

  for(count=0; count < ArraySize; count++)
    t_array[count] = new Test();

  for(count=0; count < ArraySize; count++)
    delete t_array[count];

  std::cout << " * standard operators new and delete require " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds" << std::endl;


////////////////////////////////////////////////////////////////////////////////

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ArraySize; count++)
    t4_array[count] = new Test4();

  for(count=0; count < ArraySize; count++)
    delete t4_array[count];

  std::cout << " * Boost operators new and delete require " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds (no mutexes)" << std::endl;


////////////////////////////////////////////////////////////////////////////////

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ArraySize; count++)
    t3_array[count] = new Test3();

  for(count=0; count < ArraySize; count++)
    delete t3_array[count];

  std::cout << " * Boost operators new and delete require " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds (with mutexes)" << std::endl;

////////////////////////////////////////////////////////////////////////////////

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ArraySize; count++)
    t5_array[count] = new Test5();

  for(count=0; count < ArraySize; count++)
    delete t5_array[count];

  std::cout << " * TBB operators new and delete require " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds" << std::endl;

////////////////////////////////////////////////////////////////////////////////


  delete [] t_array;
  delete [] t3_array;
  delete [] t4_array;
  delete [] t5_array;

////////////////////////////////////////////////////////////////////////////////

  std::cout << "Create and free list with " << ListSize << " integers\n";

  std::list<size_t> l;

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ListSize; count++)
    l.push_back(count);

  while(!l.empty()) l.pop_front();

  std::cout << " * operation with list's standard allocator requires " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds" << std::endl;

////////////////////////////////////////////////////////////////////////////////

  std::list<size_t, boost::fast_pool_allocator<size_t, boost::default_user_allocator_new_delete, boost::details::pool::null_mutex> > l4;

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ListSize; count++)
    l4.push_back(count);

  while(!l4.empty()) l4.pop_front();

  std::cout << " * operation with list's Boost allocator requires " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds (no mutexes)" << std::endl;

////////////////////////////////////////////////////////////////////////////////

  std::list<size_t, boost::fast_pool_allocator<size_t> > l3;

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ListSize; count++)
    l3.push_back(count);

  while(!l3.empty()) l3.pop_front();

  std::cout << " * operation with list's Boost allocator requires " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds (with mutexes)" << std::endl;

////////////////////////////////////////////////////////////////////////////////

  std::list<size_t, tbb::scalable_allocator<size_t> > l5;

  tp = std::chrono::steady_clock::now();

  for(count=0; count < ListSize; count++)
    l5.push_back(count);

  while(!l5.empty()) l5.pop_front();

  std::cout << " * operation with list's TBB allocator requires " << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " seconds" << std::endl;

////////////////////////////////////////////////////////////////////////////////

  return 0;
}
```

### `examples/and_expression.cpp`  
*Local path: `repo/oks_utils/examples/and_expression.cpp`*

```cpp
#include <oks/attribute.h>
#include <oks/query.h>

int main()
{
  OksAttribute a(
        "Weight",
        OksAttribute::float_type,
        false,
	"",
        "75",
        "person's weight",
        true
  );
 
  OksAndExpression and_q;

	/* Looking for 60 >= weight <= 90 */

  and_q.add(new OksComparator(&a, new OksData((float)60.0), OksQuery::greater_or_equal_cmp));
  and_q.add(new OksComparator(&a, new OksData((float)90.0), OksQuery::less_or_equal_cmp));

  std::cout << and_q << std::endl;
 
  return 0;
}
```

### `examples/attribute.cpp`  
*Local path: `repo/oks_utils/examples/attribute.cpp`*

```cpp
#include <oks/attribute.h>

int main()
{
  try
    {
      //  create simple attribute
      OksAttribute a(
	"Address", /* name is 'Address' */
	OksAttribute::string_type, /* the type is 'string' */
	false, /* attribute is 'single value' */
	"", /* any range */
	"unknown", /* initial value */
	"describes address", /* desription */
	true /* can not be empty */
      );

      std::cout << a;


      // check multi-value attribute's  get_init_values()
      OksAttribute b(
	"Numbers",
	OksAttribute::s32_int_type,
	true, /* attribute is 'multi-value' */
	"",
	"1,2, 4, 9, 16, 25, \"36\", \'49\',\'64\',81, 100",
	"just a test",
	true
      );

      std::cout << b;


      std::list<std::string> init_vals = b.get_init_values();
  
      std::cout << "initial values of attribute \"" << b.get_name() << "\" are:\n";
  
      for(auto & i : init_vals)
        {
          std::cout << " - \'" << i << '\'' << std::endl;
        }
    }
  catch (const std::exception& ex)
    {
      std::cerr << "Caught exception:\n" << ex.what() << std::endl;
    }

  return 0;
}
```

### `examples/class.cpp`  
*Local path: `repo/oks_utils/examples/class.cpp`*

```cpp
#include <oks/class.h>
#include <oks/attribute.h>
#include <oks/relationship.h>

int main()
{
  try
    {
      OksClass * c = new OksClass(
            "Person", /* class name */
            "Describes a person", /* description */
            false, /* is not abstract */
            0 /* no kernel */
      );
	
      OksAttribute * a = new OksAttribute(
            "Name",
            OksAttribute::string_type,
            false,
            "",
            "Unknown",
            "Describes person name",
            true
      );

      OksRelationship * r = new OksRelationship(
            "Works at",
            "Department",
            OksRelationship::Zero, OksRelationship::Many,
            false, false, false, false,
            "Can have many work places"
      );

      c->add(a); /* add attribute to class */
      c->add(r); /* add relationship to class */

      std::cout << "Class description is:\n" << *c << std::endl;

      OksClass::destroy(c);
    }
  catch (const std::exception & ex)
    {
      std::cerr << "Caught exception: " << ex.what() << std::endl;
    }

  return 0;
}
```

### `examples/comparator.cpp`  
*Local path: `repo/oks_utils/examples/comparator.cpp`*

```cpp
#include <oks/attribute.h>
#include <oks/query.h>

int main()
{
  try
    {
      const OksAttribute a("Name", OksAttribute::string_type, false, "", "unknown", "describes address", true);

      OksComparator qc(&a, new OksData("Peter"), OksQuery::equal_cmp);

      std::cout << qc << std::endl;
    }
  catch (const std::exception& ex)
    {
      std::cerr << "Caught exception:\n" << ex.what() << std::endl;
    }
 
  return 0;
}
```

### `examples/data.cpp`  
*Local path: `repo/oks_utils/examples/data.cpp`*

```cpp
#include <oks/attribute.h>
#include <oks/object.h>

int main()
{
  OksData d(new OksData::List()); /* creates list */

  d.data.LIST->push_back(new OksData((uint32_t)123456789));
  d.data.LIST->push_back(new OksData((double)123.456789));
  d.data.LIST->push_back(new OksData(boost::posix_time::second_clock::universal_time()));
  d.data.LIST->push_back(new OksData("Class-X", "Obj-1"));
  
  std::cout.precision(9); /* default is 6 */
  std::cout << d << std::endl;

  return 0;
}
```

### `examples/index.cpp`  
*Local path: `repo/oks_utils/examples/index.cpp`*

```cpp
#include <oks/kernel.h>
#include <oks/class.h>
#include <oks/object.h>
#include <oks/query.h>

#include <stdlib.h>

#include <sstream>
 

int main()
{
  try
    {
      // create OKS kernel
      OksKernel k;

      // create new schema and data files
      k.new_schema("/tmp/index.schema");
      k.new_data("/tmp/index.data");

      // define class 'Randomizer'
      OksClass * p = new OksClass("Randomizer", "Describes a Randomizer", false, &k);

      // define attribute 'Value'
      OksAttribute * a = new OksAttribute("Value", OksAttribute::double_type, false, "", "0.5", "random value", false);

      p->add(a);


      // Create 100,000 instances of the class
      size_t i = 0;
      OksDataInfo * odi = p->data_info("Value");

      while (i++ < 100000)
        {
          std::ostringstream s;
          s << i;

          std::string buf = s.str();

          OksObject *o = new OksObject(p, buf.c_str());
          OksData d((double) (random() % (1 << 16)) / (double) (1 << 16));

          o->SetAttributeValue(odi, &d);
        }

      // Create index for attribute 'Value'
      OksIndex index(p, a);

      // Search values >= 0.9 using index
      OksData d(double(0.9));
      std::list<OksObject *> * result = index.FindGreatEqual(&d);

      // Prints number of found instances
      // The expected value should be about 10,000
      if (result)
        {
          std::cout << "Found " << result->size() << " instances >= 0.9\n";
          delete result;
        }
    }
  catch (const std::exception & ex)
    {
      std::cerr << "Caught exception: " << ex.what() << std::endl;
    }

  return 0;
}
```

### `examples/kernel.cpp`  
*Local path: `repo/oks_utils/examples/kernel.cpp`*

```cpp
#include <oks/kernel.h>
#include <oks/class.h>

int main(int argc, char **argv)
{
  OksKernel k;

  if(argc != 2) return 1;

  k.load_schema(argv[1]);

  std::cout << "Schema file contains:\n";
  for(OksClass::Map::const_iterator i = k.classes().begin(); i != k.classes().end(); ++i)
    std::cout << "\t\"" << i->first << "\" class\n";

  return 0;
}
```

### `examples/method.cpp`  
*Local path: `repo/oks_utils/examples/method.cpp`*

```cpp
#include <oks/method.h>

int main()
{
  OksMethod m(
    "print",       /* name */
    "it is a test" /* description */
  );

  m.add_implementation(
    "c++",
    "void print(const char * s)",
    "std::cout << s << std::endl;"
  );

  m.add_implementation(
    "c",
    "void print(const char * s)",
    "printf(\"%s\\n\", s);"
  );

  std::cout << m;

  return 0;
}
```

### `examples/not_expression.cpp`  
*Local path: `repo/oks_utils/examples/not_expression.cpp`*

```cpp
#include <oks/attribute.h>
#include <oks/query.h>

int main()
{
  OksAttribute a(
        "age",
        OksAttribute::u16_int_type,
        false,
	"",
        "33",
        "describes age",
        true
  );
 
  OksNotExpression ne(new OksComparator(&a, new OksData((unsigned short)25), OksQuery::less_cmp));

  std::cout << ne << std::endl;
 
  return 0;
}
```

### `examples/object.cpp`  
*Local path: `repo/oks_utils/examples/object.cpp`*

```cpp
#include <oks/kernel.h>
#include <oks/class.h>
#include <oks/object.h>

int main()
{
  try
    {
      OksKernel k;                         // create OKS kernel

      k.set_silence_mode(true);
      k.new_schema("/tmp/test.schema.xml"); // create new schema
      k.new_data("/tmp/test.data.xml");     // create new data

      // define class 'Person'
      OksClass * p = new OksClass("Person", "Describes a person", false, &k);

      // define attribute 'Name'
      OksAttribute * n = new OksAttribute("Name", OksAttribute::string_type, false, "", "Unknown", "is used to set person's name", true);

      // define attribute 'Birthday'
      OksAttribute * a = new OksAttribute("Birthday", OksAttribute::date_type, false, "", "1997-04-19", "is used to set person's birthday", true);

      // add attributes to class
      p->add(n);
      p->add(a);

      // create object
      OksObject * o = new OksObject(p, "aPerson");

      // change 'Name'
      OksData d("Peter");
      o->SetAttributeValue("Name", &d);

      std::cout << *o;
    }
  catch (const std::exception & ex)
    {
      std::cerr << "Caught exception: " << ex.what() << std::endl;
    }

  return 0;
}
```

### `examples/or_expression.cpp`  
*Local path: `repo/oks_utils/examples/or_expression.cpp`*

```cpp
#include <oks/attribute.h>
#include <oks/query.h>

int main()
{
  OksAttribute a(
        "Heigth",
        OksAttribute::float_type,
        false,
	"",
        "1.77",
        "person's heigth",
        true
  );
 
  OksOrExpression or_q;

	/* Looking for tall (h >= 1.88) and short (h <= 1.65) */

  or_q.add(new OksComparator(&a, new OksData((float)1.65), OksQuery::greater_or_equal_cmp));
  or_q.add(new OksComparator(&a, new OksData((float)1.88), OksQuery::less_or_equal_cmp));

  std::cout << or_q << std::endl;
 
  return 0;
}
```

### `examples/profiler.cpp`  
*Local path: `repo/oks_utils/examples/profiler.cpp`*

```cpp
#include <oks/kernel.h>
#include <oks/class.h>

int main(int argc, char **argv)
{
  OksKernel k;

  if(argc != 3) return 1;

  k.set_profiling_mode(true);
  k.load_schema(argv[1]);
  k.load_data(argv[2]);

  return 0;
}
```

### `examples/query.cpp`  
*Local path: `repo/oks_utils/examples/query.cpp`*

```cpp
#include <oks/kernel.h>
#include <oks/class.h>
#include <oks/object.h>
#include <oks/query.h>

int main()
{
  try
    {
      OksKernel k; /* create OKS kernel */

      k.set_silence_mode(true);
      k.new_schema("/tmp/car.schema"); /* create new schema */
      k.new_data("/tmp/car.data"); /* create new data */

      /* define class 'Car' */
      OksClass * p = new OksClass("Car", "Describes a car", false, &k);

      /* define attribute 'Max Speed' */
      OksAttribute * a = new OksAttribute("Max Speed", OksAttribute::u16_int_type, false, "", "160", "max speed of car (km/h)", true);

      p->add(a);

      /* Creates three instances of Car class */
      OksObject * bmw316i = new OksObject(p, "BMW 316i");
      OksObject * bmw318i = new OksObject(p, "BMW 318i");
      OksObject * bmw320i = new OksObject(p, "BMW 320i");

      /* set max speeds */
      OksData d((uint16_t) 196);
      bmw316i->SetAttributeValue("Max Speed", &d);
      d.Set((uint16_t) 201);
      bmw318i->SetAttributeValue("Max Speed", &d);
      d.Set((uint16_t) 214);
      bmw320i->SetAttributeValue("Max Speed", &d);

      OksQuery q(false, new OksComparator(a, new OksData((unsigned short) 200), OksQuery::greater_cmp));

      std::list<OksObject *> * result = p->execute_query(&q);

      std::cout << "Query \'" << q << '\'' << ' ' << "found " << result->size() << ' ' << "objects in class \"" << p->get_name() << "\":\n";

      int i = 1;
      while (!result->empty())
        {
          OksObject * o = result->front();
          result->pop_front();
          std::cout << i++ << '.' << ' ' << *o;
        }

      delete result;

      OksObject::destroy(bmw320i);
      OksObject::destroy(bmw318i);
      OksObject::destroy(bmw316i);
    }
  catch (const std::exception & ex)
    {
      std::cerr << "Caught exception: " << ex.what() << std::endl;
    }

  return 0;
}
```

### `examples/r_expression.cpp`  
*Local path: `repo/oks_utils/examples/r_expression.cpp`*

```cpp
#include <oks/attribute.h>
#include <oks/relationship.h>
#include <oks/query.h>

int main()
{
  OksRelationship r(
	"has car", "Car",
	OksRelationship::Zero, OksRelationship::Many,
	true, true, false, false,
	"A person has zero or more cars"
  );

  OksAttribute a(
	"Type",
	OksAttribute::string_type,
	false,
	"",
	"unknown",
	"describes car type",
	true
  );

 
  OksRelationshipExpression rqe(&r, new OksComparator(&a, new OksData("BMW"), OksQuery::equal_cmp), false);

  std::cout << rqe << std::endl;
 
  return 0;
}
```

### `examples/relationship.cpp`  
*Local path: `repo/oks_utils/examples/relationship.cpp`*

```cpp
#include <oks/relationship.h>

int main()
{
  try
    {
      OksRelationship r(
	"consists of", /* name */
	"Element", /* class type */
	OksRelationship::Zero, /* low cc in Zero */
	OksRelationship::Many, /* high cc is Many */
	true, /* is composite */
	true, /* is exclusive */
	true, /* is dependent */
	false, /* is not ordered */
	"A structure consists of zero or many elements" /* description */
      );

      std::cout << r;
    }
  catch (const std::exception& ex)
    {
      std::cerr << "Caught exception:\n" << ex.what() << std::endl;
    }

  return 0;
}
```

### `src/bin/oks_tutorial.cpp`
The canonical OKS tutorial program (Car / Manufacturer / Garage example classes).
### `src/bin/oks_tutorial.cpp`  
*Local path: `repo/oks_utils/src/bin/oks_tutorial.cpp`*

```cpp
/************************************************************************
*                                                                       *
* tutorial.cpp                                                          *
*        Explains basics of OKS C++ API including:                      *
*                - kernel initialization                                *
*                - schema design                                        *
*                - data creation                                        *
*                - data manipulation                                    *
*                - notification                                         *
*                                                                       *
* Author Igor Soloviev                                                  *
*                                                                       *
* Created: 14 Oct 1996                                                  *
*                                                                       *
* Modified:                                                             *
*        11 Feb 1998                                                    *
*                - add database quering                                 *
*                                                                       *
************************************************************************/

#include <boost/date_time/gregorian/gregorian.hpp>

#include <oks/kernel.h>
#include <oks/object.h>
#include <oks/class.h>
#include <oks/attribute.h>
#include <oks/relationship.h>
#include <oks/query.h>
#include <oks/exceptions.h>


  //
  // This function sets attribute values of class 'Person'
  //

void
setPersonValues(
  OksObject *o,                    // OKS object describing person
  const char *name,                // new person name
  boost::gregorian::date birthday, // new person birthday
  const char *familySituation      // new person family situation
)
{
  OksData d;                       // creates OKS data with unknown type

  d.Set(name);                     // sets OKS data to string 'name'
  o->SetAttributeValue("Name", &d);

  d.Set(birthday);                 // sets OKS data to date 'birthday'
  o->SetAttributeValue("Birthday", &d);

  d.Set(familySituation);          // sets OKS data to 'familySituation'
  d.type = OksData::enum_type;     // sets OKS data type to enumeration
  o->SetAttributeValue("Family Situation", &d);
}


  //
  // This function prints an instance of class 'Person'
  //

void
printPerson(
  const OksObject *o               // OKS object describing person
)
{
  OksData * name(o->GetAttributeValue("Name"));                 // is used to store 'Name'
  OksData * birthday(o->GetAttributeValue("Birthday"));         // is used to store 'Birthday'
  OksData * family(o->GetAttributeValue("Family Situation"));   // is used to store 'Family Situation'

  std::cout << "Object " << o << " \n"
             " Name: " << *name << " \n"
             " Birthday: \'" << *birthday << "\" \n"
             " Family Situation: " << *family << std::endl;
}


  //
  // This function sets attribute values of class 'Employee'
  //

void
setEmployeeValues(
  OksObject *o,                    // OKS object that describes employee
  const char *name,                // new employee name
  boost::gregorian::date birthday, // new employee birthday
  const char *familySituation,     // new employee family situation
  uint32_t salary                  // new employee salary situation
) 
{
    // we can use setPersonValues() because 'Employee' class
    // derived from 'Person' class

  setPersonValues(o, name, birthday, familySituation);

  OksData d(salary);               // creates OKS data with ulong 'salary'
  o->SetAttributeValue("Salary", &d);
}


  //
  // This function prints an instance of class 'Employee'
  //

void
printEmployee(
  const OksObject *o               // OKS object that describes employee
)
{
    // we can use printPerson() because 'Employee' class
    // is derived from 'Person' class

  printPerson(o);

  OksData *department(o->GetRelationshipValue("Works at")),  // is used to store 'Works at'
          *salary(o->GetAttributeValue("Salary"));           // is used to store 'salary'

  std::cout << " Salary: " << *salary << " \n"
               " Works at: \"" << department->data.OBJECT->GetId() << "\"\n";
}


  //
  // This function sets attribute values of class 'Department'
  //

void
setDepartmentValues(
  OksObject *o,                    // OKS object that describes department
  const char *name                 // new department name
) 
{
  OksData d(name);                 // creates OKS data with string 'name'

  o->SetAttributeValue("Name", &d);
}


  //
  // This function prints an instance of class 'Department'
  //

void
printDepartment(
  const OksObject *o               // OKS object that describes department
)
{
  OksData *name(o->GetAttributeValue("Name")),       // is used to store 'Staff'
          *staff(o->GetRelationshipValue("Staff"));  // is used to store 'Name'

  std::cout << "Object " << o << "\n"
               " Name: " << *name << " \n"
               " Staff: \"" << *staff << "\"\n";
}


int
main(int argc, char **argv)
{
  const char * schema_file = "/tmp/tutorial.oks"; // default schema file
  const char * data_file   = "/tmp/tutorial.okd"; // default data file

  if(
    argc > 1 &&
    (
      !strcmp(argv[1], "--help") ||
      !strcmp(argv[1], "-help") ||
      !strcmp(argv[1], "--h") ||
      !strcmp(argv[1], "-h")
    )
  ) {
    std::cout << "Usage: " << argv[0] << " [new_schema new_data]\n";
    return 0;
  }

  if(argc == 3) {
    schema_file = argv[1];
    data_file = argv[2];
  }


    // Creates OKS kernel

  std::cout << "[OKS TUTORIAL]: Creating OKS kernel...\n";

  OksKernel kernel(false, false, false, false);

  std::cout << "[OKS TUTORIAL]: Done creating OKS kernel\n\n";


  try {        


      // Creates new schema file and tests return status

    std::cout << "[OKS TUTORIAL]: Creating new schema file...\n";

    OksFile * schema_h = kernel.new_schema(schema_file);

    std::cout << "[OKS TUTORIAL]: Done creating new schema file...\n\n"
                 "[OKS TUTORIAL]: Define database class schema...\n\n"
                 "  **********        ************     1..1 **************\n"
                 "  * Person *<|------* Employee *--------<>* Department *\n"
                 "  **********        ************ 0..N     **************\n\n";


      // Creates class Person with three attributes "Name", "Birthday" and "Family Situation"

    OksClass * Person = new OksClass(
      "Person",
      "It is a class to describe a person",
      false,
      &kernel
    );

    Person->add(
      new OksAttribute(
        "Name",
        OksAttribute::string_type,
        false,
        "",
        "Unknown",
        "A string to describe person name",
        true
      )
    );

    OksAttribute * PersonBirthday = new OksAttribute(
      "Birthday",
      OksAttribute::date_type,
      false,
      "",
      "2009/01/01",
      "A date to describe person birthday",
      true
    );

    Person->add(PersonBirthday);

    Person->add(
      new OksAttribute(
        "Family Situation",
        OksAttribute::enum_type,
        false,
        "Single,Married,Widow(er)",
        "Single",
        "A enumeration to describe a person family state",
        true
      )
    );


      // Creates class Person with superclass Person, add "Salary" attribute and "Works at" relationship

    OksClass * Employee = new OksClass(
      "Employee",
      "It is a class to describe an employee",
      false,
      &kernel
    );

    OksAttribute * EmployeeSalary = new OksAttribute(
      "Salary",
      OksAttribute::u32_int_type,
      false,
      "",
      "1000",
      "An integer to describe employee salary",
      false
    );

    OksRelationship * WorksAt = new OksRelationship(
      "Works at",
      "Department",
      OksRelationship::One,
      OksRelationship::One,
      false,
      false,
      false,
      false,
      "A employee works at one and only one department"
    );
  
    Employee->add_super_class("Person");
    Employee->add(EmployeeSalary);
    Employee->add(WorksAt);


      // Creates class Department with one attribute and one relationship

    OksClass * Department = new OksClass(
      "Department",
      "It is a class to describe a department",
      false,
      &kernel
    );

    OksAttribute * DepartmentName = new OksAttribute(
      "Name",
      OksAttribute::string_type,
      false,
      "",
      "Unknown",
      "A string to describe department name",
      true
    );

    OksRelationship *DepartmentStaff = new OksRelationship(
      "Staff",
      "Employee",
      OksRelationship::Zero,
      OksRelationship::Many,
      true,
      true,
      true,
      false,
      "A department has zero or many employess"
    );

    Department->add(DepartmentName);
    Department->add(DepartmentStaff);


      // Saves created schema file

    std::cout << "[OKS TUTORIAL]: Saves created OKS schema file...\n";

    kernel.save_schema(schema_h);


      // Creates new data file and tests return status

    std::cout << "[OKS TUTORIAL]: Creating new data file...\n";

    OksFile * data_h = kernel.new_data(data_file, "OKS TUTORIAL DATA FILE");

    data_h->add_include_file(schema_file);


      // Creates instances of the classes

    OksObject * person1     = new OksObject(Person, "peter");
    OksObject * person2     = new OksObject(Person, "mick");
    OksObject * person3     = new OksObject(Person, "baby");
    OksObject * employee1   = new OksObject(Employee, "alexander");
    OksObject * employee2   = new OksObject(Employee, "michel");
    OksObject * employee3   = new OksObject(Employee, "maria");
    OksObject * department1 = new OksObject(Department, "IT");
    OksObject * department2 = new OksObject(Department, "EP");


      // Sets attribute values for instances of class 'Person'

    setPersonValues(person1, "Peter", boost::gregorian::from_string("1960/02/01"), "Married");
    setPersonValues(person2, "Mick", boost::gregorian::from_string("1956-09-01"), "Single");
    setPersonValues(person3, "Julia", boost::gregorian::from_string("2000-May-25"), "Single");


      // Sets attribute values for instances of class 'Employee'

    setEmployeeValues(employee1, "Alexander", boost::gregorian::from_string("1972/05/12"), "Single", 3540) ;
    setEmployeeValues(employee2, "Michel", boost::gregorian::from_string("1963/01/28"), "Married", 4950) ;
    setEmployeeValues(employee3, "Maria", boost::gregorian::from_string("1951/08/18"), "Widow(er)", 4020) ;


      // Sets attribute values for instance of class 'Department'

    setDepartmentValues(department1, "IT Department"); 
    setDepartmentValues(department2, "EP Department"); 


      // Sets relationships

    department1->AddRelationshipValue("Staff", employee1);
    department1->AddRelationshipValue("Staff", employee2);
    department2->AddRelationshipValue("Staff", employee3);
    employee1->SetRelationshipValue("Works at", department1);
    employee2->SetRelationshipValue("Works at", department1);
    employee3->SetRelationshipValue("Works at", department2);


      // Print out database contents

    std::cout << "\n[OKS TUTORIAL]: Database contains the following data:\n";

    printPerson(person1);
    printPerson(person2);
    printPerson(person3);
    printEmployee(employee1);
    printEmployee(employee2);
    printEmployee(employee3);
    printDepartment(department1);
    printDepartment(department2);
  
  
      // Saves created data file

    std::cout << "\n[OKS TUTORIAL]: Saves created OKS data file...\n";

    kernel.save_data(data_h);


    std::cout << "[OKS TUTORIAL]: Done with saving created OKS data file\n";


      // **********************************************************************
      //   ***** At this moment the database has been created and saved *****
      // **********************************************************************


    std::cout << "\n[OKS TUTORIAL]: Start database querying tests\n\n";


      // This is a test for OksComparator and OksQuery

    {
      std::cout << "[QUERY]: Start simple database querying...\n";

        // Looking for persons were born after 01 January 1960

      boost::gregorian::date aDate(boost::gregorian::from_string("1960/01/01")); // query date
      OksQuery query(true, new OksComparator(PersonBirthday, new OksData(aDate), OksQuery::greater_cmp));
        

        // executes query

      std::cout << "[QUERY]: Looking for persons were born after " << aDate << " ...\n\n";
        
      OksObject::List * queryResult = Person->execute_query(&query);


        // builds iterator over results if something was found

      if(queryResult) {
        std::cout << "[QUERY]: Query \'" << query
                  << "\'\n  founds the following objects in class \'"
                  << Person->get_name() << "\' and subclasses:\n";

        for(OksObject::List::iterator i = queryResult->begin(); i != queryResult->end(); ++i) {
          OksObject * o = *i;
          OksData * d(o->GetAttributeValue("Birthday"));
          std::cout << "   - " << o << " was born " << *d << std::endl;
        }


          // free list: we do not need it anymore

        delete queryResult;
      }
        
      std::cout << "[QUERY]: Done with simple database querying\n\n";
    }
  
    {
      std::cout << "[QUERY]: Start database querying with logical function...\n";


          // Looking for persons were born after 01 January 1960
          // and before 01 January 1970

      boost::gregorian::date lowDate(boost::gregorian::from_string("1960/01/01"));  // low date
      boost::gregorian::date highDate(boost::gregorian::from_string("1970/01/01")); // high date

      OksAndExpression * andExpression = new OksAndExpression();

      andExpression->add(new OksComparator(PersonBirthday, new OksData(lowDate), OksQuery::greater_cmp));
      andExpression->add(new OksComparator(PersonBirthday, new OksData(highDate), OksQuery::less_cmp));

      OksQuery query(true, andExpression);


        // executes query

      std::cout << "[QUERY]: Looking for persons were born between " << lowDate
                << " and " << highDate << " ...\n\n";
        
      OksObject::List * queryResult = Person->execute_query(&query);


        // builds iterator over results if something was found

     if(queryResult) {
        std::cout << "[QUERY]: Query \'" << query
                  << "\'\n  founds the following objects in class \'"
                  << Person->get_name() << "\' and subclasses:\n";

        for(OksObject::List::iterator i = queryResult->begin(); i != queryResult->end(); ++i) {
          OksObject * o = *i;
          OksData * d(o->GetAttributeValue("Birthday"));
          std::cout << "   - " << o << " was born " << *d << std::endl;
        }


          // free list: we do not need it anymore

        delete queryResult;
      }

      std::cout << "[QUERY]: Done database querying with logical function\n\n";

    }
  
    {

      std::cout << "[QUERY]: Start database querying with relationship expression...\n";


        // Looking for employee were born after 01 January 1971
        // and which works at IT Department

      boost::gregorian::date aDate(boost::gregorian::from_string("1971/01/01"));  // a date
      const char * departmentName = "IT Department"; 

      OksAndExpression * andExpression = new OksAndExpression();
  
      andExpression->add(new OksComparator(PersonBirthday, new OksData(aDate), OksQuery::greater_cmp));
      andExpression->add(new OksRelationshipExpression(WorksAt, new OksComparator(DepartmentName, new OksData(departmentName), OksQuery::equal_cmp)));
                
      OksQuery query(true, andExpression);


        // executes query

      std::cout << "[QUERY]: Looking for employee were born after " << aDate
                << " and works at department " << departmentName << " ...\n\n";

      OksObject::List * queryResult = Employee->execute_query(&query);


        // builds iterator over results if something was found

     if(queryResult) {
        std::cout << "[QUERY]: Query \'" << query
                  << "\'\n  founds the following objects in class \'"
                  << Employee->get_name() << "\' and subclasses:\n";

        for(OksObject::List::iterator i = queryResult->begin(); i != queryResult->end(); ++i) {
          OksObject * o = *i;
          OksData * d(o->GetAttributeValue("Birthday"));
          std::cout << "   - " << o << " was born " << *d << std::endl;
        }


          // free list: we do not need it anymore

        delete queryResult;
      }
  
      std::cout << "[QUERY]: Done database querying with relationship expression...\n";
    }

    std::cout << "\n[OKS TUTORIAL]: Done with database querying tests\n\n";

      // It is not necessary to free data or schema because all instances of OKS
      // classes are automatic C++ objects and they will deleted before last
      // close bracket `}`.

  }
  catch (const std::exception & ex) {
    std::cerr << "Caught exception:\n" << ex.what() << std::endl;
  }

    // returns success

  return 0;
}
```

### Online-help HTML pages (`data/online-help/data-editor/`)
The full HTML text content of the OKS Data Editor help pages, embedded verbatim: `Index.html`, `OksDataEditor.html`, `MainWindow.html`, `ClassWindow.html`, `ObjectWindow.html`, `ObjectCreation.html`, `DataFileWindow.html`, `QueryWindow.html`, `GraphicalWindow.html`, `ReplaceWindow.html`, `MessageLogWindow.html`. The `QueryWindow.html` page documents the query window and query grammar as shown in the OKS Data Editor GUI.
### `data/online-help/data-editor/Index.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/Index.html`*

```html
<HTML>
<HEAD>
   <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
   <META NAME="GENERATOR" CONTENT="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
   <META NAME="Author" CONTENT="Igor Soloviev">
   <TITLE>Index</TITLE>
</HEAD>
<BODY>

<DIV ALIGN=right>
<DT>
<I><FONT SIZE=-1>OKS Data Editor</FONT></I></DT></DIV>

<HR WIDTH="100%">
<H1>
<A NAME="Index"></A>Index</H1>
<A HREF="#A">[A]</A> <A HREF="#B">[B]</A> <A HREF="#C">[C]</A> <A HREF="#D">[D]</A>
<A HREF="#E">[E]</A> <A HREF="#F">[F]</A> <A HREF="#G">[G]</A> <A HREF="#H">[H]</A>
<A HREF="#I">[I]</A> <A HREF="#J">[J]</A> <A HREF="#K">[K]</A> <A HREF="#L">[L]</A>
<A HREF="#M">[M]</A> <A HREF="#N">[N]</A> <A HREF="#O">[O]</A> <A HREF="#P">[P]</A>
<A HREF="#Q">[Q]</A> <A HREF="#R">[R]</A> <A HREF="#S">[S]</A> <A HREF="#T">[T]</A>
<A HREF="#U">[U]</A> <A HREF="#V">[V]</A> <A HREF="#W">[W]</A> <A HREF="#X">[X]</A>
<A HREF="#Y">[Y]</A> <A HREF="#Z">[Z]</A>
<BR>
<HR WIDTH="100%">
<CENTER>
<H1>
<A NAME="A"></A><FONT COLOR="#FF0000">A</FONT></H1></CENTER>
<A HREF="OksDataEditor.html#Appearance">Appearance</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="B"></A><FONT COLOR="#FF0000">B</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="C"></A><FONT COLOR="#FF0000">C</FONT></H1></CENTER>
<A HREF="MainWindow.html#ClassesTable">Classes Table</A>
<BR><A HREF="OksDataEditor.html#CommandLineOptions">Command Line Options</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="D"></A><FONT COLOR="#FF0000">D</FONT></H1></CENTER>
<A HREF="MainWindow.html#DataFilesTable">Data Files Table</A>
<BR><A HREF="OksDataEditor.html">Data Editor</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="E"></A><FONT COLOR="#FF0000">E</FONT></H1></CENTER>
<A HREF="OksDataEditor.html#EnvironmentNeeded">Environment Needed</A>
<BR><A HREF="OksDataEditor.html#EnvironmentVariables">Environment Variables</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="F"></A><FONT COLOR="#FF0000">F</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="G"></A><FONT COLOR="#FF0000">G</FONT></H1></CENTER>
<A HREF="OksDataEditor.html#TheGUI_Customization">GUI Customization</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="H"></A><FONT COLOR="#FF0000">H</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="I"></A><FONT COLOR="#FF0000">I</FONT></H1></CENTER>
<A HREF="OksDataEditor.html#Installation">Installation</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="J"></A><FONT COLOR="#FF0000">J</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="K"></A><FONT COLOR="#FF0000">K</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="L"></A><FONT COLOR="#FF0000">L</FONT></H1></CENTER>
<FONT COLOR="#000000">List of</FONT>
<BR><FONT COLOR="#FF0000">&nbsp;&nbsp;&nbsp; <A HREF="MainWindow.html#ClassesTable">classes</A></FONT><FONT COLOR="#000000">
(Main Window)</FONT>
<BR><FONT COLOR="#FF0000">&nbsp;&nbsp;&nbsp; <A HREF="MainWindow.html#DataFilesTable">data
files</A></FONT><FONT COLOR="#000000"> (Main Window)</FONT>
<BR><FONT COLOR="#FF0000">&nbsp;&nbsp;&nbsp; <A HREF="MainWindow.html#SchemaFilesList">schema
files</A></FONT><FONT COLOR="#000000"> (Main Window)</FONT>
<BR>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="M"></A><FONT COLOR="#FF0000">M</FONT></H1></CENTER>
<A HREF="MainWindow.html">Main Window</A>
<BR><A HREF="MainWindow.html#MenuBar">Menu Bar</A>
<BR><A HREF="MessageLogWindow.html#MessageLogWindow">Message Log Window</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="N"></A><FONT COLOR="#FF0000">N</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="O"></A><FONT COLOR="#FF0000">O</FONT></H1></CENTER>
<A HREF="OksDataEditor.html">OKS Data Editor</A>
<BR><A HREF="OksDataEditor.html#CommandLineOptions">Options</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="P"></A><FONT COLOR="#FF0000">P</FONT></H1></CENTER>
<A HREF="OksDataEditor.html#PossibleProblems">Possible Problems</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="Q"></A><FONT COLOR="#FF0000">Q</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="R"></A><FONT COLOR="#FF0000">R</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="S"></A><FONT COLOR="#FF0000">S</FONT></H1></CENTER>
<FONT COLOR="#000000"><A HREF="MainWindow.html#SchemaFilesList">Schema
Files List</A></FONT>
<BR>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="T"></A><FONT COLOR="#FF0000">T</FONT></H1></CENTER>
<FONT COLOR="#000000">Table of</FONT>
<BR><FONT COLOR="#FF0000">&nbsp;&nbsp;&nbsp; <A HREF="MainWindow.html#ClassesTable">classes</A></FONT><FONT COLOR="#000000">
(Main Window)</FONT>
<BR><FONT COLOR="#FF0000">&nbsp;&nbsp;&nbsp; <A HREF="MainWindow.html#DataFilesTable">data
files</A></FONT><FONT COLOR="#000000"> (Main Window)</FONT>
<BR><FONT COLOR="#FF0000">&nbsp;&nbsp;&nbsp; <A HREF="MainWindow.html#SchemaFilesList">schema
files</A></FONT><FONT COLOR="#000000"> (Main Window)</FONT>
<BR>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="U"></A><FONT COLOR="#FF0000">U</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="V"></A><FONT COLOR="#FF0000">V</FONT></H1></CENTER>
<A HREF="OksDataEditor.html#EnvironmentVariables">Variables</A>

<P>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="W"></A><FONT COLOR="#FF0000">W</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="X"></A><FONT COLOR="#FF0000">X</FONT></H1></CENTER>
<FONT COLOR="#000000"><A HREF="OksDataEditor.html#TheGUI_Customization">X
Resources</A></FONT>
<BR>
<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="Y"></A><FONT COLOR="#FF0000">Y</FONT></H1></CENTER>

<HR WIDTH="100%">
<BR>&nbsp;
<CENTER>
<H1>
<A NAME="Z"></A><FONT COLOR="#FF0000">Z</FONT></H1></CENTER>
&nbsp;

<P>
<HR WIDTH="100%">
<BR><A HREF="OksDataEditor.html">Home</A>
<BR>
<HR WIDTH="100%">
<ADDRESS>
<FONT SIZE=-1>Modified 6 August 1998</FONT></ADDRESS>

<ADDRESS>
<FONT SIZE=-1>Author Igor Soloviev</FONT></ADDRESS>

</BODY>
</HTML>
```

### `data/online-help/data-editor/OksDataEditor.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/OksDataEditor.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>OKS Data Editor</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>OKS Data Editor</h1>
<i>
The OKS Data Editor provides an interactive Motif based GUI to
graphically manipulate
objects stored in the OKS database files. An OKS object can be
inspected and
edited visually.<br>
The editor supports the following OKS data file changes:
<ul>
  <li>create a new data file</li>
  <li>modify the contents of a data file
    <ul>
      <li>add / remove / rename included files</li>
      <li>add / remove comment</li>
      <li>create new object, copy an object, remove an object, modify
an
object (modify value of an attribute and modify value of an
relationship)</li>
      <li>move an object across different data files</li>
    </ul>
  </li>
  <ul>
  </ul>
  <li>save data file </li>
</ul>
The editor supports OKS server including:</i><br>
<i>
<ul>
  <li>create user repository area</li>
  <li>checkout, update and release files in the user area</li>
  <li>commit modified files on the OKS server</li>
</ul>
The editor presents
instances of a class in matrix form. A matrix may be sorted by a class'
attribute or relationship. For complicated search of instances there is
graphical query constructor.
</i>
<hr width="100%">
<h2>Contents</h2>
<a href="#CommandLineOptions">1. Command Line Options</a><br>
<a href="#EditorOptions">&nbsp; 1.1 The Editor Options</a><br>
<a href="#EnvironmentVariables">2. Environment Variables</a>
<br>
<a href="#Appearance">3. Appearance</a>
<br>
<a href="#TheGUI_Customization">&nbsp;&nbsp;&nbsp; 3.1. The GUI
Customization</a>
<br>
<br>
<hr width="100%">
<h2><a name="CommandLineOptions"></a>1. Command Line Options</h2>
<b>oks_data_editor</b> [&lt;<i>X Toolkit options&gt;</i>] [editor
options] [<i>&lt;schema_files&gt;</i>]
[<i>&lt;data_files&gt;</i>]<br>
where:
<ul>
  <li> <i>X Toolkit options </i>are standard X Toolkit command line
options (e.g. <tt><font size="-1">-display hostname:0.0 -fg black -bg
white</font></tt>)</li>
  <li>editor options allow to run without graphical messages window, to
set configurable graphical window parameters, etc. (see below) <br>
  </li>
  <li> <i>schema_files</i> are names of the OKS schema files (usually
are
not needed, since data files are including the required schema files)<br>
  </li>
  <li> <i>data_files </i>are names of the OKS data files</li>
</ul>
<hr align="left" width="50"><img src="note.gif" alt="NOTE" nosave=""
 align="bottom" height="18" hspace="5" width="25"><b>Note:</b>
the order of options is important and X Toolkit command line arguments
(if used) must be placed before any other options, and the schema /
data files must be put last.<br>
<hr align="left" width="50">
<br>
An example of command:<br>
<br>
<div style="margin-left: 40px;"><big><tt><font size="-1"><big>oks_data_editor
-bg grey -fg white --no-message-window
combined/partitions/ATLAS.data.xml<br>
</big></font></tt></big></div>
<h3><a name="EditorOptions"></a>1.1. The Editor Options</h3>
<table style="text-align: left;" border="0" cellpadding="2"
 cellspacing="2">
  <tbody>
    <tr>
      <th colspan="2" rowspan="1" align="center" bgcolor="#ccccff"
 valign="top">Options</th>
      <th colspan="1" rowspan="2" align="center" bgcolor="#ccccff"
 valign="top">Description of options</th>
    </tr>
    <tr>
      <th align="center" bgcolor="#ccccff" valign="top">Short format</th>
      <th align="center" bgcolor="#ccccff" valign="top">Long format<br>
      </th>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">&nbsp;</td>
      <td bgcolor="#eeeeee">--no-message-window</td>
      <td bgcolor="#eeeeee">do not create graphical window for messages
and errors and do not redirect output (same as OKS_GUI_NO_MSG_WINDOW
environment variable)</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-V</td>
      <td bgcolor="#ffffff">--oks-verbose</td>
      <td bgcolor="#ffffff">run OKS in verbose mode to display OKS
kernel messages</td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee"> -v</td>
      <td bgcolor="#eeeeee">--verbose</td>
      <td bgcolor="#eeeeee">display editor debug messages</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-a</td>
      <td bgcolor="#ffffff">--allow-duplicated-objects-via-inheritance</td>
      <td bgcolor="#ffffff">do not stop if there are duplicated object
via inheritance hierarchy (usually used for debug purposes)<br>
      </td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-I</td>
      <td bgcolor="#eeeeee">--init-dirs <i>init-directories</i></td>
      <td bgcolor="#eeeeee">colon-separated list of directories
containing initialization files for user graphical windows (same as
OKS_GUI_PATH environment variable)<br>
      </td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-D</td>
      <td bgcolor="#ffffff">--init-data-files <i>data-files</i></td>
      <td bgcolor="#ffffff">colon-separated list of initialisation data
files with absolute or relative to init-dirs names (same as
OKS_GUI_INIT_DATA environment variable)<br>
      </td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-P</td>
      <td bgcolor="#eeeeee">--pixmap-dirs <i>pixmap-dirs</i></td>
      <td bgcolor="#eeeeee">colon-separated list of pixmap directories
with absolute or relative to init-dirs names (same as OKS_GUI_XPM_DIRS
environment variable)</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-B</td>
      <td bgcolor="#ffffff">--bitmap-dirs <i>bitmap-dirs</i></td>
      <td bgcolor="#ffffff">colon-separated list of bitmap directories
with absolute or relative to init-dirs names (same as OKS_GUI_XBM_DIRS
environment variable)</td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-W</td>
      <td bgcolor="#eeeeee">--icon_width <i>width</i></td>
      <td bgcolor="#eeeeee"><u>graphical window parameter</u>: width of
the icon</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-H</td>
      <td bgcolor="#ffffff">--ch-obj-dx <i>width</i></td>
      <td bgcolor="#ffffff"><u>graphical window parameter</u>: children
objects horisontal spacing</td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-R</td>
      <td bgcolor="#eeeeee">--ch-obj-dy <i>width</i></td>
      <td bgcolor="#eeeeee"><u>graphical window parameter</u>: children
objects vertical spacing</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-A</td>
      <td bgcolor="#ffffff">--ch-obj-max-width <i>width</i></td>
      <td bgcolor="#ffffff"><u>graphical window parameter</u>: maximum
width of child object (wrap relationship branch)</td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-O</td>
      <td bgcolor="#eeeeee">--font-dx <i>width</i></td>
      <td bgcolor="#eeeeee"><u>graphical window parameter</u>: text
horisontal spacing</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-E</td>
      <td bgcolor="#ffffff">--font-dy <i>width</i></td>
      <td bgcolor="#ffffff"><u>graphical window parameter</u>: text
vertical spacing</td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-Z</td>
      <td bgcolor="#eeeeee">--obj-dx <i>width</i></td>
      <td bgcolor="#eeeeee"><u>graphical window parameter</u>:
graphical objects horisontal spacing</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff">-T</td>
      <td bgcolor="#ffffff">--obj-dy <i>width</i></td>
      <td bgcolor="#ffffff"><u>graphical window parameter</u>:
graphical objects vertical spacing</td>
    </tr>
    <tr>
      <td bgcolor="#eeeeee">-N</td>
      <td bgcolor="#eeeeee">--da-x-margin <i>width</i></td>
      <td bgcolor="#eeeeee"><u>graphical window parameter</u>: drawing
area top/bottom margins</td>
    </tr>
    <tr>
      <td bgcolor="#ffffff"> -C</td>
      <td bgcolor="#ffffff">--da-y-margin <i>width</i></td>
      <td bgcolor="#ffffff"><u>graphical window parameter</u>: drawing
area left/right margins</td>
    </tr>
  </tbody>
</table>
<br>
<p>
</p>
<hr width="100%">
<h2><a name="EnvironmentVariables"></a>2. Environment Variables</h2>
Set environment variable <b><font size="-1">OKS_DATA_EDITOR_NO_MSG_WINDOW</font></b>
to any value to avoid appearance of Messages Window. By default all
load
time and run time errors and information messages generated by OKS
kernel
and Data Editor are listed in Message Window. Setting of the
environment
variable mentioned above will redirect them to the terminal window from
which Data Editor was started.
<p>Another environment variables can be useful as well:
</p>
<ul>
  <li><b><tt>OKS_KERNEL_VERBOSE</tt></b> sets OKS kernel to <b><i>verbose
mode</i></b> (running in verbose mode, OKS kernel will report all OKS
kernel calls)</li>
  <li><b><tt>OKS_KERNEL_SILENCE</tt></b> sets OKS kernel to <b><i>silence
mode</i></b> (running in silence mode, OKS kernel will report error
messages only)</li>
  <li><b><tt>OKS_KERNEL_PROFILING</tt></b> sets OKS kernel to <b><i>profiling
mode</i></b> (running in profiling mode, OKS kernel will retrieve
information about how many times each kernel method is executed and the
total and average time used; it is useful without Message Window only)</li>
  <li><b><tt>OKS_GUI_HELP_URL</tt></b> specifies base URL for online
help (e.g. 'file://local/share/online-help/data-editor/')</li>
  <li><b><tt>OKS_GUI_PATH</tt></b> same as '--init-dirs' command line
parameter</li>
  <li><b><tt>OKS_GUI_INIT_DATA</tt></b> same as '--init-data-files'
command line parameter</li>
  <li><b><tt>OKS_GUI_XPM_DIRS</tt></b>same as '--pixmap-dirs' command
line parameter</li>
  <li><b><tt>OKS_GUI_XBM_DIRS</tt></b> same as '--bitmap-dirs' command
line parameter</li>
  <li><b><tt>TDAQ_INST_PATH</tt></b> default place for configuration
files for online sw release (obsolete way, use OKS_GUI_PATH)</li>
  <li><b><tt>OKS_GUI_PATH</tt></b> = '${TDAQ_INST_PATH}/share/data'</li>
</ul>
<hr width="100%">
<h2><a name="Appearance"></a>3. Appearance</h2>
The OKS Data Editor Main Window appears after successful start of the
application.
Depending on the environment variable discussed above, the Message
Log
Window may appear as well. The Main Window stays on screen during an
operation
with Data Editor. Other windows are created dynamically when required
and is deleted when is not needed. The different types of windows are
listed below:
<ul>
  <li> <a href="MainWindow.html">Main window</a></li>
  <li> <a href="MessageLogWindow.html">Message Log window</a></li>
  <li> <a href="DataFileWindow.html">Data File window</a></li>
  <li> <a href="ClassWindow.html">Class window</a></li>
  <li> <a href="ObjectWindow.html">Object window</a></li>
  <li> <a href="QueryWindow.html">Query window</a></li>
  <li><a href="GraphicalWindow.html">Graphical Window</a></li>
  <li><a href="ReplaceWindow.html">Search/Replace Window</a><br>
  </li>
</ul>
<h3>
<a name="TheGUI_Customization"></a>3.1. The GUI Customization</h3>
<h4>
X Toolkit resource names</h4>
The applications understand all of the core X Toolkit resource names
and
classes as well as:
<ul>
  <li> <b>menu_bar</b> - specifies application menu bar widget,</li>
  <li> <b>popup</b> - specifies popup menu,</li>
  <li> <b>simple</b> - specifies general label widget;</li>
  <li> <b>header</b> - specifies label widget, used as a header.</li>
</ul>
<h4>
X resource database file</h4>
It is possible to customize appearance of the editor via setting user
preferences about color, fonts, and so on. Then the <i>OksEditor</i>
class should
be used as base prefix. For example, put into <i>~/.Xdefaults</i> file
the
following fonts and
colours preferences of first editor version:
<p><tt><b>OksEditor</b>*Background:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;LightGrey<br>
<b>OksEditor</b>*menu_bar*Background:&nbsp;&nbsp;&nbsp;&nbsp;CornFlowerBlue<br>
<b>OksEditor</b>*popup*Background:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Grey<br>
<b>OksEditor</b>*menu_bar*Foreground:&nbsp;&nbsp;&nbsp;&nbsp;White<br>
<b>OksEditor</b>*XmList*Background:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Grey<br>
<b>OksEditor</b>*XmTextField*Background:&nbsp;Grey<br>
<b>OksEditor</b>*DrawingArea*Background:&nbsp;Grey<br>
<b>OksEditor</b>*XmText*Background:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Grey<br>
<b>OksEditor</b>*FontList:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-adobe-helvetica-bold-r-normal--14-140-75-75-p-82-iso8859-1<br>
<b>OksEditor</b>*popup*FontList:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-adobe-helvetica-bold-r-normal--14-140-75-75-p-82-iso8859-1<br>
<b>OksEditor</b>*simple*FontList:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-adobe-helvetica-medium-o-normal--14-140-75-75-p-78-iso8859-1<br>
<b>OksEditor</b>*header*FontList:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-adobe-helvetica-bold-o-normal--14-140-75-75-p-82-iso8859-1<br>
</tt></p>
Then run:<br>
<ul>
  <tt>xrdb -load ~/.Xdefaults</tt><br>
</ul>
restart the editor and see result :-)<br>
<hr width="100%"><a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 09-JUN-2009<br>
</font></address>
<address>
<font size="-1">Author Igor Soloviev</font></address>
</body>
</html>
```

### `data/online-help/data-editor/MainWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/MainWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Main Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>Main Window<br>
</h1>
The Main Window contains the following items:
<ul>
  <li> <a href="#MenuBar">Menu Bar</a></li>
  <li> <a href="#SchemaFilesList">List of loaded OKS Schema Files</a></li>
  <li> <a href="#DataFilesTable">Table of loaded OKS Data Files</a></li>
  <li> <a href="#ClassesTable">Table of OKS Classes</a></li>
</ul>
<h2>
<a name="MenuBar"></a>Menu Bar</h2>
The Menu Bar allows to perform actions listed below. In some cases the
actions are available via combination of key accelerators, e.g. to exit
editor press simultaneously &lt;Ctrl&gt; and Q keys.<br>
<ul>
  <li> <b><u>F</u>ile</b>
    <ul>
      <li> <b>Save All Updated &lt;Ctrl+S&gt;</b> - Save all updated
files. The comments dialog will appear. If non-empty comment will be
provided, it will be added to all saving files.</li>
      <li> <b>Create User Repository</b> - Create [temporal] user
repository to work with OKS server (only available, if
TDAQ_DB_REPOSITORY process environment is defined).</li>
      <li> <b>Release User Repository &lt;Ctrl+D&gt;</b> - When OKS
server is used, remove all files from user repository area (uncommitted
changes can be lost!).</li>
      <li> <b>Update User Repository &lt;Ctrl+U&gt;</b> - When OKS
server is used, update from server all files in user repository area
(uncommitted changes can be lost!).</li>
      <li> <b>Commit User Repository &lt;Ctrl+C&gt;</b> - When OKS
server is used, commit all modified files in user repository area.</li>
      <li> <b>Check consistency &lt;Ctrl+Y&gt;</b> - Apply consistency
checks to loaded data files; in case of any reported problem it has to
be
fixed, if problematic file is going to be saved.</li>
      <li><b><u>E</u>xit &lt;Ctrl+Q&gt;</b> - Exit the OKS Data Editor.
The 'Exit Confirmation Dialog' will appear. Choose [Exit] to exit or
[Cancel] to continue work with Data Editor. You will be asked on
unsaved and uncommitted files.</li>
    </ul>
  </li>
  <li><b>Edit</b>
    <ul>
      <li><b>Find &lt;Ctrl+F&gt;</b> -
bring up <a href="ReplaceWindow.html">Find</a> dialog allowing to find
objects by value of an attribute or a relationship.<br>
      </li>
      <li><b>Replace &lt;Ctrl+R&gt;</b>
- bring up <a href="ReplaceWindow.html">Replace</a> dialog allowing to
find and replace values of an attributes or a relationships.<br>
        <hr align="left" width="100"><small><i>various <a
 href="GraphicalWindow.html">graphical
windows </a>customized by users, e.g.:</i></small></li>
      <li><b>Software Repository</b></li>
      <li><b>Data Quolity Tree</b></li>
      <li><b>Tests Repository</b></li>
      <li><b>Control Tree</b></li>
      <li><b>Partition</b></li>
      <li><b>Data Quality Algorithms</b></li>
      <li><b>Hardware</b></li>
    </ul>
  </li>
  <li><b>Options</b>
    <ul>
      <li><b>Silence Mode</b> - Select toggle button to switch OKS
kernel in <i>silence</i> mode.</li>
      <li><b>Verbose Mode</b> - Select toggle button to switch OKS
kernel in <i>verbose</i> mode.</li>
      <li><b>Profiling Mode</b> - Select toggle button to switch OKS
kernel in <i>profiling</i> mode.</li>
      <li><b>Check externally modified
files</b> - Select toggle button to periodically check if loaded
file was modified by an external process. In such case ask user, if the
file has to be saved or reloaded. </li>
      <li><b>Set period of check</b> - Set period of check for above
option. </li>
      <li><b>Recovery mode for modified files</b> - Select toggle
button to periodically save modified
files. In case of a problem the recovery file with latest update can be
used found. </li>
      <li><b>Set backup period</b> -
Set period of save for above option.</li>
      <li><b>Ask comment on file save</b>
- Select toggle button to enable / disable dialog box asking for
comments of file saving. </li>
      <li><b>Restore position on restart</b>
- Save positions of the main and message windows, when exit application
and restore them, when the editor is restarted. The options are saved
on exit, if this toggle is on.  </li>
      <li><b>Save Options</b> - Save given options on <i>~/.oks-data-editor-rc.xml</i>
file and use them, when the editor will be used next time. </li>
    </ul>
  </li>
  <li><b>Windows</b>
    <ul>
      <li><b>Help &lt;Ctrl+H&gt;</b> - select to popup Help Window</li>
      <li><b>Message Log &lt;Ctrl+M&gt;</b> - select to popup <a
 href="MessageLogWindow.html">Message Log Window</a><br>
        <hr align="left" width="100"></li>
      <li><b>Window 1</b> - Select to popup first child window (if it
is opened)</li>
      <li><b>Window 2</b> - Select to popup second child window (if it
is opened)<br>
        <b>...</b></li>
      <li><b>Window N</b> - Select to popup n-th child window (if it is
opened)</li>
    </ul>
  </li>
  <li><b>Help</b>
    <ul>
      <li>General</li>
      <li>Index<br>
        <hr align="left" width="100"></li>
      <li>Main Window</li>
      <li>Message Log</li>
      <li>Data File Window</li>
      <li>Class Window</li>
      <li>Object Window</li>
      <li>Query Window</li>
      <li>Graphical Window</li>
      <li>Find/replace Window<br>
        <hr align="left" width="100"></li>
      <li><b>About...</b> - Select to popup About OKS Data Editor
Dialog Box. It contains copyrights info and OKS version.<br>
      </li>
    </ul>
  </li>
</ul>
&nbsp;
<h2><a name="SchemaFilesList"></a>OKS Schema Files List</h2>
The OKS Schema Files List shows loaded schema files and allows several
operations
with them. It is possible to load schema file, to close selected or all
schema files. To display a list of the available actions with
OKS schema files, it is necessary press right mouse button, when mouse
pointer will be over the scheme list, as it shown on the figure below:<br>
<div align="center"><img style="width: 627px; height: 120px;"
 alt="Schema Files" src="schema-files.gif" hspace="5" vspace="5"></div>
<p>The popup menu allows the following actions:
</p>
<ul>
  <li>item <b>[Open...]</b> allows open already existing OKS schema
file</li>
  <li>item <b>[Close <i>filename</i>]</b> closes selected OKS schema
file&nbsp; (if there is no selected schema file, it will be disabled)</li>
  <li>item <b>[Close All]</b> closes all loaded schema files (if there
are no loaded schema files, it will be disabled)</li>
</ul>
Note, that the close operation results close of data files using
classes from closing schema file.<br>
<h2>
<a name="DataFilesTable"></a>OKS Data Files Table</h2>
The OKS Data Files Table selectively shows loaded data files and allows
several operations with them:<br>
<div align="center"><img style="width: 790px; height: 231px;"
 alt="Data Files" src="data-files.gif" hspace="5" vspace="5"></div>
<h3>Popup Menu<br>
</h3>
To display a list of the available
actions with OKS data files, it is necessary to press right mouse
button,
when mouse pointer will be over the data files table. The popup menu
allows the following actions (some of them can be disabled, if the file
is not selected or the OKS server is not used):<br>
<ul>
  <li><b>[New...]</b> - Create new OKS data file</li>
  <li><b>[Open...]</b> - Open already existing OKS data file</li>
  <li><b>[Close <i>filename</i>]</b> - Close selected OKS data file</li>
  <li><b>[Close All]</b> - Closes all loaded data files</li>
  <li><b>[Save <i>filename</i>]</b> - Save selected OKS data file in
extended format</li>
  <li><b>[Force Save <i>filename</i>]</b> - Save selected OKS data
file in extended format ignoring consistency rules (non-recommended!)</li>
  <li><b>[Save As... <i>filename</i>]</b> - Save selected OKS data
file with other name. It is also possible to choose between <i>extended</i>
(default) and <i>normal</i> (compact) data file formats.</li>
  <li><b>[Checkout <i>filename</i>]</b> - Checkout file from OKS
server for local modifications in user repository area.</li>
  <li><b>[Update <i>filename</i>]</b> - Update file located in user
repository area from OKS server (uncommitted changes can be lost!) and
reload it.</li>
  <li><b>[Commit <i>filename</i>]</b> - Commit modifications made in
user repository area on the OKS server.</li>
  <li><b>[Release <i>filename</i>]</b> - Remove file located in user
repository area (uncommitted changes can be lost!) and reload it from
OKS server repository.</li>
  <li><b>[Save All]</b> - Save all loaded data files, for which teher
are write permissions.</li>
  <li><b>[Set Active <i>filename</i>]</b> or [<b>Unset Active <i>filename</i></b>]
- Set or unset selected data file. The active file means: any created
object will be placed in this data file; it is possible move an
existing object to this data file.</li>
  <li><b>[Details <i>filename</i>]</b> - Display the <a
 href="DataFileWindow.html">Data File Window</a> that will show the
table of objects, loaded from selected data file.</li>
</ul>
The double-click on data files table brings <a
 href="DataFileWindow.html">Data
File Window</a>.
<p>The table shows the following information about data file:
</p>
<ul>
  <li><b>File</b> - Fully qualified filename.</li>
  <li><b>Access</b> - Direct filesystem access rights (<i>read-write</i>,
    <i>read-only</i>, <i>no access</i>).</li>
  <li><b>Repository</b> - Display which OKS repository the file is
located on or <i>none</i>, if the file is not stored on
OKS server. For a repository file the access permissions are shown: <font
 color="#006600">RW - read-write</font> access, <font color="#990000">R
- read-only</font> access (i.e. commit on
OKS server is not allowed).<br>
  </li>
  <li> <b>Status</b> - Updated, active, locked or none</li>
</ul>
The press of table's column header button sorts contents of table
by
this column. For example, sort by "Status" column to get list of all
modified files.<br>
<h3>Search Panel</h3>
The bottom panel of Data Files table allows to display a sub-set of
loaded data files. If there are no any symbols in the "<i>Matching
names of files:</i>" text
filed, then all files are shown. Otherwise only those files, which
match the search mask are shown.<br>
<br>
If the "<i>Reqular expression</i>"
toggle button is selected, to apply the mask press appeared <img
 style="width: 24px; height: 24px;" alt="Search Button" src="search.gif">
button. Otherwise the
modified selection is applied automatically, when the mask is modified.<br>
<h2><a name="ClassesTable"></a>OKS Classes Table</h2>
The OKS Classes Table shows loaded OKS classes and allows some
operations
with them. The user is able to browse instances of a class, create new
instance of a class, create or load a query for a class. To display a
list
of the available actions with OKS data files, it is necessary press
right
mouse button, when mouse pointer will be over the classes' table, as it
shown on the figure below:<br>
<div align="center"><img style="width: 627px; height: 254px;"
 alt="Classes" src="classes.gif" hspace="5" vspace="5"></div>
<p>The popup menu allows the following actions:
</p>
<ul>
  <li><b>[Show]</b> - Display the <a href="ClassWindow.html">Class
Window</a> that will show the table of instances, created for selected
class (if the class is <i>abstract</i>, the item will be disabled).</li>
  <li><b>[New Object]</b> - Create new instance of selected class. The
item is disabled if the class is <i>abstract</i>, or when there is no
active data file.</li>
  <li><b>[Query]</b> - Create <a href="QueryWindow.html">Query Window</a>
for selected class.</li>
  <li><b>[Load Query]</b> - Create <a href="QueryWindow.html">Query
Window</a>
for selected class and loads already existing query.</li>
</ul>
The double-click on data files table will bring <a
 href="ClassWindow.html">Class
Window</a>.
<p>The table shows the following information about class:
</p>
<ul>
  <li> <b>Name</b></li>
  <li> <b>Number of instances</b></li>
  <li> <b>Is abstract</b> (yes, no)</li>
</ul>
The press of table's column header button will sort contents of table
by
this column.<br>
<h3>Search Panel</h3>
The bottom panel of Classes table allows to display a sub-set of
classes. If there are no any symbols in the "<i>Matching names of
classes:</i>" text
filed, then all classes are shown. Otherwise only those classes, which
match the search mask are shown.<br>
<br>
If the "<i>Reqular expression</i>"
toggle button is selected, to apply the mask press appeared <img
 style="width: 24px; height: 24px;" alt="Search Button" src="search.gif">
button. Otherwise the
modified selection is applied automatically, when the mask is modified.<br>
<br>
<hr width="100%">
<a href="OksDataEditor.html">Home</a> - <a href="MessageLogWindow.html">Next</a>
- <a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 09-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/ClassWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/ClassWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Class Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>Class Window</h1>
The <i>main window</i> of the OKS
Data Editor allows to display <i>class
window</i> with list of their instances. To do this double click the
name of the class from the Classes list or press right mouse button,
when mouse pointer will be over the OKS Data Editor main window classes
list and select Show (see <a href="MainWindow.html#ClassesTable">OKS
Classes Table from main window</a>).<br>
<br>
OKS Data Editor Class Window allows to browse list of objects and
perform several actions with them. To do this select an object and/or
click right mouse:<br>
<div align="center"><img
 style="width: 825px; height: 321px;" alt="Classes Window"
 src="classes-window.gif" vspace="5"><br>
</div>
<h3><a name="ObjectCreation"></a>Object Creation</h3>
Before creation of a new object it is necessary to decide which data
file it goes to. A data file can be made active using the <a
 href="MainWindow.html#DataFilesTable">Data Files Table from main window</a>.
To create a new object it is enough select <b>[New]</b> menu item. The
<a href="ObjectCreation.html">object creation prompt dialog</a> that
will
appear. Note, the <b>[New]</b> menu item
remains disabled, if no active file is selected.<br>
<h3><a name="ShowObject"></a>Show Object Window<br>
</h3>
An object can be selected and removed directly from the class table
(see below). Also, most of the values of it's attributes and
relationships can be seen directly in the class table. However their
modification and several other actions with object can only be done
from the <a href="ObjectWindow.html">Object window</a>. To open the
window select <b>[Show <i>object_id</i>]</b> from popup menu
or double click the object row.<br>
<h3><a name="Find"></a>Find Objects</h3>
There are two possible ways to find and object:<br>
<ul>
  <li>by object unique ID</li>
  <li>by query (e.g. by values of object attributes and it's relations
with other objects)<br>
  </li>
</ul>
<h4>Find by Identity</h4>
To find an object by ID one can to use <b>[Find by ID]</b> function
from popup menu. In such case put exact UID in
the prompt dialog. If object with such ID exists in the class, it will
be selected in the class table.<br>
<br>
Also it is possible to use matching UID panel from the bottom of the
class window. If there are no any symbols in the "Matching UIDs:" text
filed, then all objects are shown. Otherwise only those objects, which
IDs match the search mask are shown.<br>
<br>
If the "Regular expression" toggle button is selected, to apply the
mask press appeared <img style="width: 24px; height: 24px;"
 alt="Search Button" src="search.gif">
button. Otherwise the modified selection is applied automatically, when
the mask is modified.<br>
<h4>Query</h4>
A query can be constructed and executed in the <a
 href="QueryWindow.html">query window</a>. Select <b>[Query]</b> item
from popup menu to
create new query or select [Load Query] to load an existing query from
file.<br>
<h2><a name="Delete"></a>Delete Object</h2>
To delete an existing object it is necessary to select it and choose <b>[Delete]</b>
menu item. An object can
only be deleted, if it is not referenced by other objects and the user
has write permissions on file containing the object. In case of
problems the error is printed to the <a href="MessageLogWindow.html">message
log window</a>.<br>
<br>
<hr width="100%"><a href="OksDataEditor.html">Home</a> - <a
 href="ObjectWindow.html">Next</a>
- <a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 10-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/ObjectWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/ObjectWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Object Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>Object Window</h1>
To display object window it is necessary select desired object in the
objects list of <a href="ClassWindow.html">class</a> or <a
 href="DataFileWindow.html">data file</a> windows, press the right
mouse button and select Show object menu item, or double click desired
object in the objects list of class window.<br>
<br>
The OKS Data Editor Object Window displays the objects properties
including object ID, class name, container data file, values of
attributes and relationships. The single-value attributes are presented
as text fields or option menus (boolean and enumerations). The
single-value relationships are presented as text field. The multi-value
attributes and relationships are presented as lists:<br>
<div align="center"><img style="width: 581px; height: 678px;"
 alt="Object Window" src="object.gif" vspace="5"></div>
The actions and changes of object properties are described below.<br>
<h2>Actions</h2>
<table style="text-align: left; width: 100%;" border="0" cellpadding="2"
 cellspacing="2">
  <tbody>
    <tr>
      <td style="vertical-align: top;"><img
 style="width: 198px; height: 158px;" alt="Object Icon Popup"
 src="object-icon-popup.gif" align="top"> <br>
      </td>
      <td style="vertical-align: top;">The OKS Data Editor Object
Window allows the user to select displayed
object, move the object to another data file, make a copy of the
object, rename the object, delete the object and change values of the
object's attributes and relationships. To access actions menu move
sursor oven icon in the left-up corner of window and press right mouse
button. Popup menu similar to shown one will appear (depending on
selection of active file and asscess permissions some menu items can be
disabled).</td>
    </tr>
  </tbody>
</table>
<h3><a name="SelectObject"></a>Select Object<br>
</h3>
Selection of object means putting it's identity to the data editor
clipboard.
If ths identity is the clipboard, it can be used to paste
this object's reference to a relationship's value.<br>
<h3><a name="ReferencedBy"></a>Referenced By<br>
</h3>
Sometimes it is necessary to know which objects reference given one.
The selection of <b>[Referenced By]</b>
popup menu items results appearance of window listing referencing
objects:<br>
<div align="center"><img style="width: 377px; height: 305px;"
 alt="Referenced By Window" src="object-ref-by.gif" vspace="5"></div>
Double click on an object opens it's data window.
<h3>Move Object<br>
</h3>
To move object from one OKS data file to another, it is necessary to
select desired data file from OKS Main Window, set this data file
active, press right mouse button on OKS Object pixmap and choose <b>[Move
to: <i>datafile</i>]</b>
menu item. If object currently is stored in data file which is active,
this menu item will be disabled.<br>
<h3>Copy object</h3>
To copy an OKS object press right mouse button on OKS Object pixmap and
choose <b>[Copy]</b> menu item. When
popup prompt dialog will appear, input new
unique object identity (empty string means that the name for new object
will be chosen automatically).<br>
When an object is copied, the values of composite exclusive
relationships are not copied.<br>
<h3>Rename object</h3>
To rename object (i.e. to change object identity) press right mouse
button on OKS Object pixmap and choose Rename menu item. When popup
prompt dialog will appear, input new unique object identity (it can not
be empty!). When an object is renamed, more than one data file may be
affected and marcked as modified.<br>
<h2>Change value of attributes</h2>
It is only possible to change attribute value, if the object is stored
on a file writable by user. Otherwise appropriate item representing the
value will be disabled.<br>
<br>
To change value of single-value attribute it is necessary to press
the right mouse button, when mouse pointer is over corresponding text
field, and to select desired action:<br>
<div align="center"><img style="width: 215px; height: 92px;"
 alt="Single Value Attribute Popup" src="object-sv-attr-popup.gif"
 vspace="5"></div>
The set value dialog allows to set any allowed value. The reset default
value function sets default value.<br>
<br>
If an object has an single-value attribute with enumeration, boolean or
class type, it is
displayed as option menu. To modify the attribute select new value from
option menu:<br>
<div align="center"><img style="width: 169px; height: 114px;"
 alt="Set Enumeration Value" src="object-set-sv-enum.gif" vspace="5"></div>
<br>
To change value of multi-value attribute it is necessary to press
the right mouse button, when mouse pointer is over corresponding list
box, and to select desired action:<br>
<div align="center"><img style="width: 523px; height: 289px;"
 alt="Multi-Value Attribute Popup" src="object-mv-attr-popup.gif"
 vspace="5"></div>
Modification Actions are listed below:<br>
<ul>
  <li>The <b>[Modify Value]</b> allows to change currently selected
value.</li>
  <li>The <b>[Add Value]</b> allows to add to the end of the list new
value.</li>
  <li>The <b>[Delete Value]</b> allows to remove selected value.</li>
  <li>The <b>[Move Up Value]</b> moves up selected value one more
position in the list.</li>
  <li>The <b>[Move Down Value]</b> moves down selected value one
position in the list.</li>
</ul>
<a name="MultiValueViewActions"></a>The View Actions are listed below:<br>
<ul>
  <li>The <b>[Show more (+1 row)]</b> increases height of list for one
more row.</li>
  <li>The <b>[Show all rows]</b> increases height of list to show all
items of the attribute value.</li>
  <li>The <b>[Show less (-1 row)]</b> decreases height of list by one
row.</li>
  <li>The <b>[Show only two rows]</b> sets height of list to two items.</li>
</ul>
<h2>Value of relationships</h2>
It is only possible to change relationship value, if the object is
stored
on a file writable by user. Otherwise appropriate item representing the
value will be disabled.<br>
<br>
To change value of single-value relationship it is necessary to press
the right mouse button, when mouse pointer is over corresponding text
field, and to select desired action:<br>
<div align="center"><img style="width: 463px; height: 146px;"
 alt="Single-Value Realtionship Popup" src="object-sv-rel-popup.gif"
 vspace="5"></div>
<ul>
  <li>To browse referenced object select <b>[Show Object]</b> menu
item.</li>
  <li><a name="Clipboard"></a>To set value of relationship the
referenced object has to be
previously selected (i.e. put into editor clipboard) in an <a
 href="#SelectObject">object</a>, <a href="ClassWindow.html#ShowObject">class</a>
or <a href="DataFileWindow.html#Objects">data file</a> window. If
there is an
object in the clipboard, the <b>[Set Object <i>reference</i>]</b>
allows to link value of relationship with given object.</li>
  <li>If cardinality of relationship allows (i.e. it is <i>"0..1"</i>),
the value of relationship
can be set to NULL using <b>[Clear]</b> menu item.<br>
  </li>
</ul>
To change value of multi-value relationship it is necessary to press
the right mouse button, when mouse pointer is over corresponding list
box, and to select desired action:<br>
<div align="center"><img style="width: 457px; height: 305px;"
 alt="Multi-Value Relationship Popup" src="object-mv-rel-popup.gif"
 vspace="5"></div>
To browse one of referenced objects select it in the list and choose <b>[Show
Object <i>reference</i>]</b> menu item.<br>
<br>
Modification Actions are listed below:<br>
<ul>
  <li>To add reference to a new object it has to be previously selected
(see above for single-value relationship). If there is an object in the
clipboard, use the <b>[Add Object <i>reference</i>]</b> menu item.</li>
  <li>To remove object reference from relationship value select the
object and choose <b>[Remove Object <i>reference</i>]</b>. Note, it
there is only one object in the relationship, it can be removed only if
cardinality of relationship allows to do this (i.e. it is <i>"0..N"</i>).</li>
  <li>The <b>[Move Up <i>reference</i>]</b> moves up selected object
one more position in the list.</li>
  <li>The <b>[Move Down <i>reference</i>]</b> moves down selected
object one position in the list.</li>
</ul>
The View Actions are similar to multi-value attribute ones described <a
 href="#MultiValueViewActions">above</a>.<br>
<h2>Descriptions</h2>
The OKS schema contains descriptions of attributes and relationships,
which should help user to browse and to modify attribtes and
relationships of an object. To access the documentation select <b>[Show
Desription]</b> item available in
most popup menus described above:<br>
<div align="center"><img style="width: 629px; height: 234px;"
 alt="Description Dialog" src="object-description.gif" vspace="5"></div>
Another way to see description is too move mouse pointer above text
filed box, option menu or list box used for attribute and relationship
values and keep it still for a second. This results automatic
appearance of tips box containing description similar to above:<br>
<div align="center"><img style="width: 399px; height: 151px;"
 alt="Tips Description" src="object-description-tips.gif" vspace="5"></div>
Note, the descrition or any other long text is automatically wrapped by
80 symbols. To change this value&nbsp; use OKS_GUI_TIPS_MAX_WIDTH
environment variable.<br>
<br>
<hr width="100%"><a href="OksDataEditor.html">Home</a> - <a
 href="QueryWindow.html">Next</a>
- <a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 10-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/ObjectCreation.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/ObjectCreation.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Class Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>Object Creation Dialog<br>
</h1>
Put unique ID for
new object in the prompt dialog, otherwise the object
will be anonymous.<br>
<br>
The object creation dialog is accessible from the <a
 href="ClassWindow.html#ObjectCreation">class</a> or <a
 href="MainWindow.html#ClassesTable">main</a> windows. In both cases to
create new object the active data file has to be set.<br>
<hr width="100%"><a href="OksDataEditor.html">Home</a> - <a
 href="ObjectWindow.html">Next</a>
- <a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 10-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/DataFileWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/DataFileWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.05 [en] (X11; I; SunOS 5.5.1 sun4u) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Data File Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1><a name="DataFileWindow"></a>Data File Window</h1>
The
data file window allows to browse and to modify list of files included
by given data file, to access list of objects in the file, to add,
remove and browse comments stored on the file.<br>
<div align="center"><img
 style="width: 569px; height: 723px;" alt="Data File Window"
 src="data-window.gif" vspace="5"><br>
</div>
<h2><a name="Includes"></a>Include Files</h2>
A data files has to be consistent from <i>included files</i> point of
view.
This means, all required schema files and data files with objects
referenced by objects of given file have to be included.<br>
<br>
To modify included files select a file and / or press right mouse
button
on the include files list box. A popup menu similar to shown below one
will appear:<br>
<div align="center"><img
 style="width: 552px; height: 131px;" alt="Include Files"
 src="data-window-includes.gif" vspace="5"><br>
</div>
<br>
The actions of the popup window are listed below:<br>
<ul>
  <li><b>[Show]</b> action opens data file window of included file (it
is
disabled for schema file).</li>
  <li><b>[Add From]</b> action allows to add include file from
TDAQ_DB_PATH,
TDAQ_DB_REPOSITORY, TDAQ_DB_USER_REPOSITORY and working areas. When a
file is selected from file selection dialog, the prompt dialog proposes
to strip it's name. The recommendation is always to strip the file
name, since inclusion of files with absolute paths makes database
hardly supportable. When OKS server is used, the inclusion of files
with absolute filenames is not allowed. If a file is successfully
included and it was not yet loaded by the editor, it is automatically
loaded.</li>
  <li><b>[Remove]</b> action removes selected include.</li>
  <li><b>[Rename]</b> action allows to change name of include.<br>
  </li>
</ul>
<h2><a name="Objects"></a>Objects</h2>
It is possible to show, to select and to delete an object using the
objects table as shown below:<br>
<div align="center"><img
 style="width: 553px; height: 171px;" alt="Objects"
 src="data-window-objects.gif" vspace="5"><br>
</div>
Also, it is possible to see only objects belonging to certain classes
and/or having certain identities. To do this use matching class names
and object UIDs selection panels below the objects table.<br>
<h2><a name="Comments"></a>Comments</h2>
The comments should contain description of file modifications. It is
always possible to add a comment using [Add Comment] push button
located above the comments table.<br>
It is possible to see or to to delete an existing comment using the
comments table as shown below:
<div align="center"><img
 style="width: 553px; height: 123px;" alt="Comments"
 src="data-window-comments.gif" vspace="5"></div>
Note, when OKS server is used it is more
important to put the comments on commit. Any comments stored on file
after last commit are automatically added in the OKS server commit
window.
<br>
<hr width="100%">
<a href="OksDataEditor.html">Home</a> - <a href="MessageLogWindow.html">Previous</a>
- <a href="ClassWindow.html">Next</a> - <a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 10-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/QueryWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/QueryWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Query Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>Query Window</h1>
The
OKS Data Editor provides database query builder. Created query can be
used by user application via OKS and config APIs. An OKS query can be
edited visually, saved in a file, loaded from file and executed. The
query window consists of two main parts: the graphical query
constructor and the result table:<br>
<div align="center"><img style="width: 429px; height: 780px;"
 alt="Query Window" src="query.gif" vspace="5">
</div>
<h2><a name="BuildingQuery"></a>Building query</h2>
To begin building a query, select desired class from the <a
 href="MainWindow.html#ClassesTable">main window</a> or from the <a
 href="ClassWindow.html">class window</a>, press right mouse
button and select <b>[Query]</b> item from popup menu.
OKS Data Editor will bring up query window with empty query form.<br>
<br>
It is necessary to decide, if the query scope is limited by objects of
the selected class, or also include objects of derived classes. This
can be changed using toggle button <b>[Search in subclasses]</b>: if
it is
selected, the query will be performed over class and all subclasses,
otherwise scope will be one class only.<br>
<br>
Then press
right mouse button in empty query form:<br>
<div align="center"><img style="width: 313px; height: 294px;"
 alt="Empty Form" src="query-empty.gif" align="middle" vspace="5"></div>
<br>
The attribute expression allows to run query selecting objects by
attribute or UID value. The relationship expressions allow to apply
attribute expression on referenced objects. The <i>"Not"</i>, <i>"And"</i>
and <i>"Or"</i>
expressions allow to build query using arbitrary number of attribute
and relationship expressions.<br>
<h3><a name="AttributeExpression"></a>Attribute Expression</h3>
The attribute expression query form is simplest query form
and it describes search by value of single attribute, for example
<i>"search all objects with initialisation timeout greater 20"</i>:<br>
<div align="center"><img style="width: 241px; height: 153px;"
 alt="Attribute Form" src="query-attr.gif" vspace="5"><br>
</div>
This form
consists of the following items:<br>
<ul>
  <li>Selection radio-group <i>"Attribute Value"</i> vs. <i>"Object
ID"</i>. If <i>"Attribute Value"</i> is selected, the value of
attribute is
compared.
Else, the object UID is compared.<br>
  </li>
  <li>Attribute
option menu allows to select an attribute defined in class (disabled,
if the <i>"Object ID"</i> is selected above).<br>
  </li>
  <li>Value text field allows to put any desired value of attribute
that will
be used during the search;</li>
  <li>Comparator allows to define a function that will be used by query
and predefined functions are:
    <ul>
      <li><tt>"="&nbsp;</tt> - equal,</li>
      <li><tt>"!="</tt> - not equal,</li>
      <li><tt>"~="</tt> - like (use regular expression),</li>
      <li><tt>"&lt;="</tt> - less or equal,</li>
      <li><tt>"&gt;="</tt> - great or equal,</li>
      <li><tt>"&lt;"&nbsp;</tt> - less,</li>
      <li><tt>"&gt;"&nbsp;</tt> - great.</li>
    </ul>
  </li>
</ul>
The attribute name can be changed at any moment. If the attribute type
of new selected attribute is different from previous one, the value can
be converted to default of selected attribute type.<br>
<h3><a name="RelationshipExpression"></a>Relationship Expression</h3>
The relationship expression query form describes search
through relationship attribute using nested query form, for example <i>"search
all segments which have infrastructure applications defining
infrastructure environment variables with names ended by IS_SERVER"</i>:<br>
<div align="center"><img style="width: 335px; height: 255px;"
 alt="Relationship Form" src="query-rel.gif" vspace="5"><br>
</div>
<br>
This form
consists of the following items:<br>
<ul>
  <li>Relationship option menu allows to select a relationship defined
in class.</li>
  <li><i>"Some Objects Match Query"</i> vs. <i>"All Objects Match
Query"</i> toggle button defines either
an object referenced by relationship matches query from nested query
form
or at least one object referenced by relationship matches the query.</li>
  <li>Nested Query
Form allows to build nested query expression (e.g. attribute or even
nested relationship expression). Press right mouse button
to see popup menu and use the same rules to build query as for top
level query form. Note, once the nested form is inserted, it is not
possible to change the relationship name (the option menu becomes
disabled).</li>
</ul>
<div align="center"><img style="width: 247px; height: 202px;"
 alt="Relationship Form Popup" src="query-rel-popup.gif" vspace="5"><br>
</div>
<h3>Logical Expressions</h3>
Logical Query Expression Form can be used with any type
of query form to build complex query expression. There are three types
of logical query expressions:<br>
<ul>
  <li><i>"Not"</i> query expression</li>
  <li><i>"And"</i> query expression</li>
  <li><i>"Or"</i> query expression</li>
</ul>
<br>
The <i>"Not"</i> query expression form can be concatenated
with any another single query expression form. The <i>"And"</i> query
expression form and <i>"Or"</i> query expression form can be used with
any two
or more query expression forms.<br>
<br>
It is possible to build multi-level tree
structure that consists of logical query expression forms. The leaves
of that structure must be either <a href="#AttributeExpression">attribute</a>
or <a href="#RelationshipExpression">relationship</a> query expression
form. An incomplete tree and popup menu is shown below:<br>
<div align="center"><img style="width: 391px; height: 414px;"
 alt="Incomplete Logical Tree and Popup Menu"
 src="query-logical-tree.gif" vspace="5"><br>
</div>
<h2><a name="ExecutingQuery"></a>Executing Query</h2>
To execute a complete OKS query it is necessary either to create it
(see <a href="#BuildingQuery">Building Query</a>) or to load already
existing one (see <a href="#LoadingQuery">Loading
Query</a>). Press right mouse button on any free space of the query
form and
select <b>[Execute Query]</b> item from popup menu:<br>
<div align="center"><img style="width: 420px; height: 174px;"
 alt="Prepare Execution" src="query-exe.gif" vspace="5">
</div>
<br>
The result of
query will
appear in the query result table:<br>
<div align="center"><img style="width: 430px; height: 325px;"
 alt="Result" src="query-result.gif" vspace="5"><br>
</div>
<h2><a name="SavingQuery"></a>Saving Query</h2>
To save a complete query to file press right mouse button on any free
space of Query Form and select Save Query item from popup menu. This
will bring up dialog with prompt for query file name. Enter desired
filename and press OK button, e.g.:<br>
<div align="center"><img style="width: 316px; height: 188px;" alt="Save"
 src="query-save.gif" vspace="5">
</div>
<br>
Note, incomplete query can not be saved.<br>
<br>
The format of the query file is simple (it looks like a statement of
LISP language) and can be edited manually by any text editor.<br>
<br>
An OKS query does not strongly depend from class type. If two classes
have an attribute with the same name, possibly a query can be applied
to both classes.<br>
<h2><a name="LoadingQuery"></a>Loading Query</h2>
To load a query, select query related class from <a
 href="MainWindow.html#ClassesTable">main window</a> or <a
 href="ClassWindow.html">class
window</a>, press right mouse button and
select [Load Query] item from popup menu. The OKS Data
Editor will bring up Open OKS Query window. Choose query file name and
the Query window with stored query will appear.
<hr width="100%"><a href="OksDataEditor.html">Home</a> - <a
 href="file:///home/isolov/working/online/oks/data/online-help/data-editor/QueryWindow.html">Next</a>
- <a href="Index.html#Index">Index</a>
<hr width="100%">
<address><font size="-1">Modified 11-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/GraphicalWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/GraphicalWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.04 [en] (X11; I; SunOS 5.5.1 sun4m) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Query Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1>Graphical Window</h1>
<font color="red"><b>==== under construction ====</b></font><br>
<br>
<br>
The OKS Data Editor provides a way for graphical representation of
relations between objects. A group of objects have to be described in
special configuration file explaining to the OKS data editor objects of
which classes have to be displayed, what graphical icons and cursors to
use, which relationships and attributes have to be suppressed, which
relationships have dependencies, what to show on top, etc. For example,
below there is typical Partition view accessible via <b>Partition</b>
menu of
<b>Edit</b> menu bar of the <a href="MainWindow.html#MenuBar">main
window</a>:<br>
<div align="center"><img style="width: 583px; height: 830px;"
 alt="Graphical Window" src="g_win.gif" vspace="5"></div>
The popup window appearing in result of right mouse button click in an
object-free area (see above picture) allows to:<br>
<ul>
  <li><a href="#CreateObject">create</a> new object (allowed for given
type of graphical window)</li>
  <li><a href="#SelectTopLevelObjects">select </a>objects shown on top
level</li>
  <li><a href="#WindowProperties">define</a> user graphical preferences</li>
  <li><a href="#PrintWindow">print</a> contents of window</li>
  <li>sort objects and refresh<br>
  </li>
</ul>
Otherwise user can browse and update an object as described in <a
 href="#BrowseAndUpdateObject">second next section</a>.<br>
<h2><br>
</h2>
<h2><a name="SelectTopLevelObjects"></a>Top Level Objects</h2>
<br>
<h2><a name="BrowseAndUpdateObject"></a>Browse and Update Objects</h2>
Each object can be shown in two states:<br>
<ul>
  <li>Icon State (compact, no visible attributes)</li>
  <li>Table State (extended, the attributes are visible and can be
modified)</li>
</ul>
The switch between above states and many other actions on object are
available from popup menu available on right mouse button click when
object is in icon state, or left mouse click on object's table system
button:<br>
<div align="center">
<table cellpadding="2" cellspacing="5">
  <caption align="bottom"><small>Icon State Popup - left. Table State
Popup - right.</small><br>
  </caption> <tbody>
    <tr>
      <td><img style="width: 285px; height: 329px;" alt="Icon Popup"
 src="g_win_icon_popup.gif"></td>
      <td><img style="width: 284px; height: 267px;" alt="Table Popup"
 src="g_win_table_popup.gif"><br>
      </td>
    </tr>
  </tbody>
</table>
</div>
The popup menu allows:<br>
<ul>
  <li><b>[Hide]</b> - Remove object from given graphical window. To
restore
object close and open window again or modify <b>[Show on Top]</b>
window configuration.</li>
  <li><b>[Maximize]</b> - Switch from icon to table state. <b>[Minimize]</b>
- Switch
from table to icon state.</li>
  <li><b>[Hide Relationships]</b> - Do not show object relationships
(if
shown). <b>[Show Relationships]</b> - Show object relationships (if
not shown).</li>
  <li><b>[Copy Reference]</b> - Put reference on given object into
editor
clipboard (is the same as <a href="ObjectWindow.html#Clipboard">select</a>
operation)</li>
  <li><b>[Link with reference]</b> - Link current object with another
selected
object (if there is a one in editor clipboard).</li>
  <li><b>[Referenced By]</b> - Show objects referencing given one in
this
window (to get all references use <a
 href="ObjectWindow.html#ReferencedBy">referenced by</a> function of
object window).<br>
  </li>
  <li><b>[Contained in]</b> - Show name of file containing given object.</li>
  <li><b>[Copy]</b> - Copy given object.</li>
  <li><b>[Rename]</b> - Change unique identity of given object.</li>
  <li><b>[Modify]</b> - Is the same as [Maximize].</li>
  <li><b>[Create Child &gt;]</b> - Create new object and link it with
given
one.</li>
  <li><b>[Delete]</b> - Delete given object.<br>
  </li>
</ul>
<h3>Object table</h3>
When an object is shown as table, one can to browse the attributes,
class name and unique identity, e.g.:<br>
<div align="center"><img style="width: 424px; height: 218px;"
 alt="Table" src="g_win_table.gif" vspace="5"><br>
</div>
To edit an attribute click left mouse button on it's value. A textfield
box will appear allowing to change the value. If the value cannot be
changed (e.g. object's file is read-only or locked by someone else),
the value will be shown as disabled.<br>
<div align="center">
<table cellpadding="2" cellspacing="5">
  <caption align="bottom"><small>Edit an attribute in text field -
left. Modification is not allowed, the text field box is disabled -
right.</small><br>
  </caption> <tbody>
    <tr>
      <td><img style="width: 424px; height: 218px;" alt="Edit Attribute"
 src="g_win_table_edit_attr.gif"><br>
      </td>
      <td><img style="width: 255px; height: 149px;"
 alt="Disabled Text Field" src="g_win_table_edit_dsbl.gif"></td>
    </tr>
  </tbody>
</table>
</div>
When modification of a value is finished, to update object press [Tab]
key or slect any other attrubute.<br>
<br>
If an attribute has enumeration type, instead of text filed box popup
menu with allowed values appears (to change value select a new value
from the popup). In the attrubute's type is unsigned integer, then it's
value can be
edited in decimal or hexadecimal format (click right mouse button and
select desired format):<br>
<div align="center">
<table cellpadding="2" cellspacing="5">
  <caption align="bottom"><small>Edit enumeration value - left. Select
numeric format to edit unsigned integer value - right.</small><br>
  </caption> <tbody>
    <tr>
      <td><img style="width: 353px; height: 260px;"
 alt="Edit Enumeration Value" src="g_win_table_edit_enum.gif" vspace="5"></td>
      <td><img style="width: 255px; height: 148px;"
 alt="Edit unsigned integer value" src="g_win_table_edit_int_format.gif"
 vspace="5"></td>
    </tr>
  </tbody>
</table>
</div>
<br>
<h3>Object relationships</h3>
<br>
<br>
<h3><a name="ContainedIn"></a>Object File</h3>
To see which file contains an object select <b>[Contained in]</b> from
object's popup menu, e.g.:<br>
<div align="center"><img style="width: 820px; height: 156px;"
 alt="Contained In" src="g_win_contained_in.gif" vspace="5"><br>
</div>
<h3><a name="ReferencedBy"></a>References on Object</h3>
To see which objects referencing given object in this window select
<b>[Referenced By]</b> from object's popup menu. The references are
starting
from the window top-level objects and show relationship names and
intermediate objects, e.g.:<br>
<div align="center"><img style="width: 1167px; height: 552px;"
 alt="Refernced By" src="g_win_ref_by.gif" vspace="5"><br>
</div>
<br>
Note, to get list of all references from loaded database use <a
 href="ObjectWindow.html#ReferencedBy">referenced by</a> function of
object window.<br>
<h2><a name="CreateObject"></a>Create New Object</h2>
Select database file for new object and create<br>
<h3>Relationship Objects</h3>
Create new object and link with existing one<br>
<br>
<h2><a name="DeleteObject"></a>Delete Object</h2>
<h2><a name="WindowProperties"></a>Window Properties</h2>
The properties window allows to set fond, various distances, layouts,
etc.:<br>
<div align="center"><img style="width: 471px; height: 617px;"
 alt="Parameters" src="g_win_params.gif" vspace="5"><br>
</div>
<h2><a name="PrintWindow"></a>Print Window</h2>
The print window allows to print current window into encapsulated
PostScript file, to save as <i>mif</i> file for future import to Adobe
Frame
Maker, or to send to printer.<br>
<div align="center"><img style="width: 610px; height: 616px;"
 alt="Print Window" src="g_win_print.gif" vspace="5"><br>
</div>
<h2>Create Configuration for New View</h2>
How to create OKS config file for data editor and add to the editor
configuration.<br>
<br>
<hr width="100%"><a href="OksDataEditor.html">Home</a> - <a
 href="MainWindow.html">Next</a>
- <a href="Index.html#Index">Index</a>
<hr width="100%">
<address><font size="-1">Modified 12-JUN-2009</font></address>
<address>
<font size="-1">Author <a
 href="http://consult.cern.ch/xwho/people/432778">Igor Soloviev</a></font></address>
</body>
</html>
```

### `data/online-help/data-editor/ReplaceWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/ReplaceWindow.html`*

```html
<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
   <meta name="GENERATOR" content="Mozilla/4.61 [en] (X11; I; SunOS 5.6 sun4u) [Netscape]">
   <meta name="Author" content="Igor Soloviev">
   <title>Main Window</title>
</head>
<body>

<div ALIGN=right>
<dt>
<i><font size=-1>OKS Data Editor</font></i></dt></div>

<hr WIDTH="100%">
<h1>
Find/Replace Dialog Window</h1>
The <b>Find</b> dialog window is used to find objects containg given value
of attributes or relationships.
<br>The <b>Replace</b> dialog window is used to find such objects and substitute
the found values by some other value.
<center><img SRC="replace-dlg.gif" ALT="[replace dialog]" HSPACE=5 VSPACE=5 height=296 width=444></center>

<p>The "<i>Replace</i>" group of radio buttons defines type of search:
<UL>
 <LI>by value of an attribute;</LI>
 <LI>by value of a relationship.</LI>
</UL>
If "<i>search by attribute value</i>" is choosen, the search is performed
by all objects that contain attributes with some user-specified type, e.g.
search all objects with attribute of type "<i>signed short integer</i>"
equal to <i>123</i>, or search all attribute of type "<i>string</i>" containg
"<i>@cern.ch</i>".
<br>If "<i>search by relationship value</i>" is choosen, the search is
performed by all objects that contain relationships pointing to some object,
e.g. search all objects that have a reference to the object X of class
A.
<p>If "<b>Find</b>" button is pressed, the found objects with details are
printed to the standard output (message log window), e.g.:
<br><b><tt><font size=-1>Find '"@cern.ch"' (case sensitive match)</font></tt></b>
<br><tt><font size=-1>&nbsp;- match attribute 'Authors' of object 'SW_Object@mrs-server'</font></tt>
<br><tt><font size=-1>&nbsp;&nbsp;&nbsp; * found (case sensitive match)
substring "@cern.ch" in '&lt;Doris.Burckhart@cern.ch>'</font></tt>
<br><tt><font size=-1>&nbsp;- match attribute 'Authors' of object 'SW_Object@mrs-server'</font></tt>
<br><tt><font size=-1>&nbsp;&nbsp;&nbsp; * found (case sensitive match)
substring "@cern.ch" in '&lt;Mihai.Caprini@cern.ch>'</font></tt>
<br><tt><font size=-1>&nbsp;- match attribute 'Authors' of object 'SW_Object@rc-intera-controller'</font></tt>
<br><tt><font size=-1>&nbsp;&nbsp;&nbsp; * found (case sensitive match)
substring "@cern.ch" in '&lt;Robert.Jones@cern.ch>'</font></tt>
<br><tt><font size=-1>&nbsp;- match attribute 'Authors' of object 'SW_Object@confdb-print-hosts'</font></tt>
<br><tt><font size=-1>&nbsp;&nbsp;&nbsp; * found (case sensitive match)
substring "@cern.ch" in '&lt;Igor.Soloviev@cern.ch>'</font></tt>
<br><tt><font size=-1>&nbsp;- match attribute 'Authors' of object 'SW_Object@ipc-server'</font></tt>
<br><tt><font size=-1>&nbsp;&nbsp;&nbsp; * found (case sensitive match)
substring "@cern.ch" in '&lt;Serguei.Kolos@cern.ch>'</font></tt>
<p>If "<b>Replace</b>"button is pressed, the modified objects with details
are printed to the standard output (message log window), e.g.:
<br><b><tt><font size=-1>Replace '[Workstation@sunatdaq01.cern.ch]' to
'[Workstation@sunatdaq02]'</font></tt></b>
<br><tt><font size=-1>&nbsp;- update relatioship 'RunsOn' of object 'RunControlApplication@ROC1Ctrl'</font></tt>
<br><tt><font size=-1>&nbsp;- update relatioship 'RunsOn' of object 'RunControlApplication@ROC2Ctrl'</font></tt>
<br><tt><font size=-1>&nbsp;- update relatioship 'RunsOn' of object 'RunControlApplication@RootCtrl'</font></tt>
<br><tt><font size=-1>&nbsp;- update relatioship 'RunsOn' of object 'RunControlApplication@SFC1Ctrl'</font></tt>
<br><tt><font size=-1>&nbsp;- update relatioship 'RunsOn' of object 'RunControlApplication@SFC2Ctrl'</font></tt>
<br><tt><font size=-1>&nbsp;- update relatioship 'RunsOn' of object 'RunControlApplication@DFMCtrl'</font></tt>
<p>Before search, the input values typed by the user, are converted to
given attribute or object types and input fields are updated accordanly.
The find is not started if object specified by the user does not exist.
The replace is not started, if after conversion the '<i>from value</i>'
is equal to the '<i>to value</i>'.
<p>If search by string value is performed, it is possible to define two additional parameters of the search:
<ul>
 <li>case sensitive search;</li>
 <li>matching to whole string.</li>
</ul>
If replace by string attribute value is used and matching to whole string
is not required, each found matching token is replaced, e.g. case insensitive
replacement of string "<i>abcxyXyxYXYcba</i>" by "<i>XY</i>" to "<i>YX</i>"
produces new string "<i>abcYXYXYXYXcba</i>".
<br>
<hr WIDTH="100%">
<br><a href="OksDataEditor.html">Home</a> - <a href="QueryWindow.html">Previous</a>
- <a href="Index.html#Index">Index</a>
<br>
<hr WIDTH="100%">
<address>
<font size=-1>Modified 8 November 1999</font></address>

<address>
<font size=-1>Author Igor Soloviev</font></address>

</body>
</html>
```

### `data/online-help/data-editor/MessageLogWindow.html`  
*Local path: `repo/oks_utils/data/online-help/data-editor/MessageLogWindow.html`*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=ISO-8859-1">
  <meta name="GENERATOR"
 content="Mozilla/4.05 [en] (X11; I; SunOS 5.5.1 sun4u) [Netscape]">
  <meta name="Author" content="Igor Soloviev">
  <title>Message Log Window</title>
</head>
<body>
<div align="right">
<dt><i><font size="-1">OKS Data Editor</font></i></dt>
</div>
<hr width="100%">
<h1><a name="MessageLogWindow"></a>Message Log Window</h1>
The Message Log is used to keep messages coming from OKS library and
the editor. When error or warning occurs, the Message Log pops up over
the other windows. The errors are highlighted by red and the warnings
are highlighted by dark blue colors.<br>
<br>
To avoid the Message Log window appearance and redirection of the
messages to standard out, run OKS Data Editor with <span
 style="font-style: italic;">--no-message-window</span> option.<br>
<br>
To bring up the Message Log window on top, press <b>&lt;Window&gt; |
&lt;Message Log&gt;</b> menu button from the OKS Data Editor main
window menu bar.<br>
<br>
The following actions are available from the Message Log pop-up menu
(press right mouse button, when mouse's pointer
will be over the message's list):<br>
<ul>
  <li><span style="font-weight: bold;">Clear Log</span> - Clear all
messages.<br>
  </li>
  <li><span style="font-weight: bold;">Make Log File</span> - Type file
name when prompted and press OK. To save
log on exit of the Data Editor, switch on <b>&lt;Save When Exit&gt;</b>
toggle
button (this may be useful for debug and profiling purposes). </li>
  <li><span style="font-weight: bold;">Copy to Clipboard</span> - Copy
all messages to clipboard.<br>
  </li>
</ul>
Above items from pop-up menu are disabled, if there are no messages.<br>
To select a text in a single line press left mouse button and drag the
pointer across the text. The selected text is displayed in reverse video.
The selection can be extended either by pressing the SHIFT key and then
dragging the pointer with the left mouse button down, or by pressing left
or right arrow keys while holding down the SHIFT key. In addition to the
click-and-drag technique for text selection, the Message Log also
supports multiple-clicking techniques: double-clicking selects a word,
triple-clicking selects the current line.
<br>
<br>
<hr width="100%"><br>
<a href="OksDataEditor.html">Home</a> - <a href="MainWindow.html">Previous</a>
- <a href="DataFileWindow.html">Next</a> - <a href="Index.html#Index">Index</a>
<br>
<hr width="100%">
<address><font size="-1">Modified 3 March 2010</font></address>
<address>
<font size="-1">Author Igor Soloviev</font></address>
</body>
</html>
```

### Release notes (HTML, converted to text)
The `doc/RELEASE_NOTES.tdaq-02-01-00.html` and `doc/RELEASE_NOTES.tdaq-04-00-00.html` pages record the oks_utils release notes for those TDAQ releases. Text extracted from HTML below.
#### `doc/RELEASE_NOTES.tdaq-02-01-00.html` (text-extracted)

```text
Untitled 1

OKS Server

 In case of the probe file
usage (e.g. test any commit against ATLAS combined partition) the OKS
server does not validate the same file twice (see tdaq-02-00-03
patch 3453).

 The OKS server can be
used on any platform of TDAQ release; before only one platform was
supported, i.e. the OKS server has been configured for SLC4 opt (see tdaq-02-00-03 patch
 3453).

 The OKS server utilities support operations with directories (see
 tdaq-02-00-03 patch
3497).

 Avoid OKS commit infinite loop in case of file system errors
like "cannot open file" 
(see tdaq-02-00-03
patch 3619).

 Restore current working
directory after any OKS server operation (see tdaq-02-00-03 patch 3656).

 Fix problem with removal of files included by other repository
files (see Savannah bug
67304)

 Add a possibility of PAM auth to OKS
commit (reserved for future multi-session RDB server).

 Duplicated classes are not allowed.

Relational OKS

 When look for appropriate
schema version, test compatibility of schema without read of data to
avoid oks2coral slowness (see tdaq-02-00-03 patch 3497).

 The oks_ls_data utility
takes into account usage of archived
configurations, when 'since' and 'till' parameters are used (see tdaq-02-00-03 patch 3833).

OKS Data Editor

 Fix bug in query
constructor for multi-value attribute comparators (see
 tdaq-02-00-03 patch 3497).

 Fix problem causing editor
crashes in data file dialog (see tdaq-02-00-03 patch 4031 and Savannah bug 67505).

 Use Motif ComboBox widget
instead of options menu in case of potentially big number of items
(e.g. list of classes).

 Allow query in
search/replace dialog.

 Fixed tips for attribute and relationship
description. 

 Online help improvements.

OKS Schema Editor

 Avoid editor crash if
command line parameter is not a file (see tdaq-02-00-03 patch
3798).
```
#### `doc/RELEASE_NOTES.tdaq-04-00-00.html` (text-extracted)

```text
RELEASE_NOTES

 OKS Editors Bug Fixes and
 Feature Requests

 Remember matrix sorting
 criteria after refresh (see bug 73648).

 Fix slow redraw of log messages window on SLC5
 (see bug

 74304); the log message was
 re-implemented using Xbae matrix widget; add a possible to select arbitrary
 text in a single message log line, e.g. to copy name of file,
 object or error text.

 The editors ask for a
 confirmation to overwrite existing file (see bug 80019).

 OKS Archival

 Increase query fetch
 size and add query execution plan hints (see bug 80596).

 OKS Server

 OKS commit adds commands execution timestamps (see feature request
 82792).
```
### Tests and misc
`tests/DAQ-Configuration.schema.xml` is the ATLAS DAQ-Configuration test schema; `tests/generate_data.cpp`, `tests/test_indexies.cpp`, `tests/time_tests.cpp`, `tests/test.sh`, `tests/do-tests`, `tests/make-sciplot-data` are the test programs; `src/lib/oks_access.cpp` and `oks/ral.h`/`src/lib/oks_ral.cpp` implement the RAL (Relational Access Layer, ~100 KB) for relational storage back-ends; `cmt/requirements` is the legacy CMT build description.
### `tests/DAQ-Configuration.schema.xml`  
*Local path: `repo/oks_utils/tests/DAQ-Configuration.schema.xml`*

```xml
<?xml version="1.0" encoding="ASCII"?>

<!-- oks-schema version 2.0 -->


<!DOCTYPE oks-schema [
  <!ELEMENT oks-schema (info, (include)?, (class)+)>
  <!ELEMENT info EMPTY>
  <!ATTLIST info
      name CDATA #REQUIRED
      type CDATA #REQUIRED
      num-of-objects CDATA #REQUIRED
      oks-format CDATA #FIXED "extended"
      oks-version CDATA #REQUIRED
      created-by CDATA #REQUIRED
      created-on CDATA #REQUIRED
      creation-time CDATA #REQUIRED
      last-modified-by CDATA #REQUIRED
      last-modified-on CDATA #REQUIRED
      last-modification-time CDATA #REQUIRED
  >
  <!ELEMENT include (file)+>
  <!ELEMENT file EMPTY>
  <!ATTLIST file
      path CDATA #REQUIRED
  >
  <!ELEMENT class (superclass | attribute | relationship | method)*>
  <!ATTLIST class
      name ID #REQUIRED
      description CDATA ""
      is-abstract (yes|no) "no"
  >
  <!ELEMENT superclass EMPTY>
  <!ATTLIST superclass name CDATA #REQUIRED>
  <!ELEMENT attribute EMPTY>
  <!ATTLIST attribute
      name CDATA #REQUIRED
      description CDATA ""
      type (bool|s8|u8|s16|u16|s32|u32|float|double|date|time|string|uid|enum) #REQUIRED
      range CDATA ""
      format (dec|hex|oct) "dec"
      is-multi-value (yes|no) "no"
      multi-value-implementation (list|vector) "list"
      init-value CDATA ""
      is-not-null (yes|no) "no"
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
      multi-value-implementation (list|vector) "list"
  >
  <!ELEMENT method (body+, method-action*)>
  <!ATTLIST method
      name CDATA #REQUIRED
      description CDATA ""
      condition CDATA #REQUIRED
  >
  <!ELEMENT body (#PCDATA)>
  <!ELEMENT method-action EMPTY>
  <!ATTLIST method-action
      return-value CDATA #REQUIRED
      action CDATA #REQUIRED
  >
]>

<oks-schema>

<info name="" type="" num-of-includes="0" num-of-items="7" oks-format="schema" oks-version="2.8.5" created-by="isolov" created-on="lxplus011" creation-time="26/3/03 18:58:54" last-modified-by="isolov" last-modified-on="lxplus011" last-modification-time="26/3/03 18:58:54"/>

 <class name="SW_Resource" description="The Resource class is used to describe shared and exclusive resources used by the processes: the name of the resource, the maximum numbers of copies per partition and per system (i.e. total), and documentation (help URL and comments). The dynamic part of a resource includes the list of processes that allocated this resource.
An example of a resource could be a run-time license (for example we can start limited number of processes with GUI that use some commercial widget). A resource can describe some hardware resources (for example we can not have two concurrent processes that write on the same type recorder device). The use of resources can be connected with the architecture of the process (for example, we do not want to allow start simultaneously several GUI editors for the same data, if there is no concurrent update of graphical view or the creator of software objects knows that it must be started only once per system or per partition, etc.)." is-abstract="no">
  <attribute name="Name" description="" type="string" is-multi-value="no" init-value="Unknown" is-not-null="no"/>
  <attribute name="MaxCopyPerPartition" description="" type="s32" is-multi-value="no" init-value="1" is-not-null="no"/>
  <attribute name="MaxCopyTotal" description="" type="s32" is-multi-value="no" init-value="1" is-not-null="no"/>
  <attribute name="HelpLink" description="" type="string" is-multi-value="no" init-value="http://" is-not-null="no"/>
  <attribute name="Description" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <relationship name="AllocatedBy" description="" class-type="Process" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SW_Object" description="This class is used to desribe platform independent part of DAQ software component from logical point of view.
The platform dependent part is described by &apos;Program&apos; class.
To start DAQ software component it is necessary to create an instance of &apos;SW_Module&apos; class." is-abstract="no">
  <attribute name="Name" description="A string is used to desribe unique name of the software object." type="string" is-multi-value="no" init-value="Unknown" is-not-null="no"/>
  <attribute name="Description" description="A string is used to desribe unique name of the software object." type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Authors" description="A string is used to desribe unique name of the software object." type="string" is-multi-value="yes" init-value="" is-not-null="no"/>
  <attribute name="HelpLink" description="A string is used to desribe unique name of the software object." type="string" is-multi-value="no" init-value="http://" is-not-null="no"/>
  <attribute name="DefaultParameter" description="A string is used to desribe unique name of the software object." type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="DefaultPriority" description="A string is used to desribe unique name of the software object." type="s32" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="DefaultPrivileges" description="A string is used to desribe unique name of the software object." type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <relationship name="NeedsResources" description="" class-type="SW_Resource" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="NeedsEnvironment" description="" class-type="Environment" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ImplementedBy" description="The software object is implemented by one or more programs." class-type="Program" low-cc="one" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="yes"/>
 </class>

 <class name="Computer" description="Describes an abstract computer.
Has subclasses to describe workstation
and build-in CPU." is-abstract="no">
  <attribute name="OsType" type="enum" range="linux,lynx,solaris,hpux,wnt" init-value="linux"/>
  <attribute name="Name" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <relationship name="Executes" description="" class-type="Process" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="IsIn" description="" class-type="Network" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="HasRecordingDevice" description="" class-type="RecordingDevice" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="Environment" description="The Environment class is used to describe environment variables and their values. These variables are defined and values are assigned before starting the corresponding process. The SW_Object defines general environment variables (for example, they can describe the name of some configuration database, the name of workstation, where some server is running and so on). The Program defines platform specific environment variables or redefines general environment variables for the actual program. The SW_Configuration defines configuration specific environment (for example the name of the configuartion). The SW_Module defines the environment which is specific for concrete started program." is-abstract="no">
  <attribute name="Variable" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Value" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
 </class>

 <class name="Program" description="This class is used to describe platform dependent part of DAQ software component. An instance of this class describes a release of package (a program more exactly). It defines default parameters to start a program (command line, environment, priority, etc.) as well." is-abstract="no">
  <attribute name="OsType" type="enum" range="linux,lynx,solaris,hpux,wnt" init-value="linux"/>
  <attribute name="ExecutableFile" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="DefaultParameters" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="DefaultPriority" description="" type="s32" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="DefaultPrivileges" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <relationship name="NeedsEnvironment" description="" class-type="Environment" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="DescribedBy" description="" class-type="SW_Object" low-cc="one" high-cc="one" is-composite="yes" is-exclusive="no" is-dependent="yes"/>
 </class>

 <class name="Application" description="This class is used to describe DAQ software component from &apos;setup/shutdown&apos; database. If we need to start a new DAQ software component, we have to create an instance of this class and put references to software object (SW_Object class) which we need to start and CPU where we want to start it. The &apos;Initialization&apos; and &apos;Shutdown&apos; dependencies are used in case if we want to start a component synshronosly and we know whict components we must start before." is-abstract="no">
  <attribute name="Name" description="" type="string" is-multi-value="no" init-value="Unknown Application" is-not-null="no"/>
  <attribute name="Parameters" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Priority" description="" type="s32" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Privileges" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="InitTimeout" description="" type="u32" is-multi-value="no" init-value="5" is-not-null="no"/>
  <attribute name="CreationType" description="Creation Type attribute enumeration has the following valid tokens:
1. Default	- all applications
2. DAQ_Setup	- started by Supervisor at setup
3. DAQ_Shutdown	- started by Supervisor at shutdown
4. SOR		- started by ??? at Start Of Run
5. EOR		- started by ??? at End Of Run
6. Supervised	- must be monitored by DAQ supervisor and at least 2-5 must be set" type="Enumeration, Default, DAQ_Setup, DAQ_Shutdown, SOR, EOR, Supervised" is-multi-value="yes" init-value="Default" is-not-null="no"/>
  <relationship name="SWObject" description="" class-type="SW_Object" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="RunsOn" description="" class-type="Computer" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="InitializationDependsFrom" description="" class-type="Application" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="NeedsEnvironment" description="" class-type="Environment" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ExecutedAs" description="" class-type="Process" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="ShutdownDependsFrom" description="" class-type="Application" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="HasParameters" description="" class-type="Parameter" low-cc="zero" high-cc="many" is-composite="yes" is-exclusive="no" is-dependent="yes"/>
 </class>

 <class name="Process" description="The Process class is used to describe a dynamic physical part of a software object: logical name of the process (for example, TRD_DetController and TILES_DetController are different processes, but they are started from the same program), process id, date and time of start, real process priority and privileges. An instance of Process class has a reference to Program from which it has been started and a reference to CPU where it is executed. An instance of Process class has a list of allocated resources, and it has a reference to the partition (configuration), where it was running." is-abstract="no">
  <attribute name="Handle" description="" type="s32" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Type" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="PID" description="" type="s32" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="TimeOfStart" description="" type="time" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Priority" description="" type="s32" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Privileges" description="" type="string" is-multi-value="no" init-value="" is-not-null="no"/>
  <attribute name="Name" description="" type="string" is-multi-value="no" init-value="Unknown Process" is-not-null="no"/>
  <relationship name="RunsOn" description="" class-type="Computer" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="HoldsResource" description="" class-type="SW_Resource" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="StartedFrom" description="" class-type="Program" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="RanBy" description="" class-type="Application" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

</oks-schema>
```

### `tests/generate_data.cpp`  
*Local path: `repo/oks_utils/tests/generate_data.cpp`*

```cpp
#include <stdlib.h>
#include <stdio.h>

#include <chrono>
#include <fstream>

#include <oks/kernel.h>
#include <oks/class.h>
#include <oks/object.h>
#include <oks/attribute.h>
#include <oks/relationship.h>


static OksClass*
findClassAndReport(const OksKernel& kernel, const std::string & name)
{
  OksClass *c = kernel.find_class(name);
  
  if(!c) {
    Oks::error_msg("3") << "Can`t find class \"" << name << "\", exiting ...\n";
    exit(3);
  }
  
  return c;
}


static void
createInstances(
  unsigned long n,		// Number of instances
  const char *instance_prefix,	// Prefix for instance id
  OksObject **objs,		// Array of instances
  OksClass *cl			// Pointer to class
)
{
  long j;
 
  std::cout << "Create " << n << " instances of " << cl->get_name() << " class...\n";

  for(j=0; j<(int)n; j++) {
    char buf[32];
    sprintf(buf, "%s%ld", instance_prefix, j);

    objs[j] = new OksObject(cl, buf);
  }
}

int main(int argc, char **argv)
{
  unsigned long	totalNumberOfObjects = 0L;
  unsigned long	numberOfLinksPerSW = 0L;
  unsigned long	numberOfSWObjects = 0L;
  unsigned long	numberOfPrograms = 0L;
  unsigned long	numberOfSWResources = 0L;
  unsigned long	numberOfProcess = 0L;
  unsigned long	numberOfComputers = 0L;
  unsigned long	numberOfApplications = 0L;
  unsigned long	numberOfEnvironment = 0L;

  bool doNotBind = false;
  bool fastExit = false;	// if true do not call OksKernel destructor

  const char *schemaFile = 0;
  const char *dataFile = 0;
 
  for(int m = 1; m < argc; m++) {
    if     (!strcmp(argv[m], "-nbind"))     doNotBind = true;
    else if(!strcmp(argv[m], "-fast-exit")) fastExit = true;
    else if(!strcmp(argv[m], "-n"))         totalNumberOfObjects = atol(argv[++m]);
    else if(!strcmp(argv[m], "-nlinks"))    numberOfLinksPerSW = atol(argv[++m]);
    else if(!strcmp(argv[m], "-schema"))    schemaFile = argv[++m];
    else if(!strcmp(argv[m], "-data"))      dataFile = argv[++m];
    else
      Oks::warning_msg("data-generator")
        << "Unknown parameter: \"" << argv[m] << "\"\n";
  }

  if(!totalNumberOfObjects) totalNumberOfObjects = 2000;
  if(!numberOfLinksPerSW) numberOfLinksPerSW = 40;
  
  if(numberOfLinksPerSW < 10) {
    Oks::warning_msg("data-generator")
      << "Number of links per sw object can not be less 10, set minimal\n";

    numberOfLinksPerSW = 10;
  }

  numberOfSWObjects = totalNumberOfObjects / numberOfLinksPerSW;
  numberOfPrograms = (numberOfSWObjects * 5 * numberOfLinksPerSW) / 40;
  numberOfSWResources = (numberOfSWObjects * 2 * numberOfLinksPerSW) / 40;
  numberOfProcess = (numberOfSWObjects * 8 * numberOfLinksPerSW) / 40;
  numberOfComputers = (numberOfSWObjects * 4 * numberOfLinksPerSW) / 40;
  numberOfApplications = numberOfProcess;
  numberOfEnvironment = totalNumberOfObjects - numberOfSWObjects - numberOfPrograms -
  			numberOfSWResources - numberOfProcess - numberOfComputers -
  			numberOfApplications;


  if(!schemaFile) schemaFile = PATH_TO_SCHEMA;

  if(!dataFile) {
    static char buf[132];
    dataFile = buf;
	
    sprintf(buf, "data.%lu.%lu", totalNumberOfObjects, numberOfLinksPerSW);
  }


  OksKernel kernel;
  OksFile * new_fp = 0;

  try {
    OksFile * schema_fp = kernel.load_schema(schemaFile);
    new_fp = kernel.new_data(dataFile);
std::cout << "ADD INCLUDE FILE \"" << schema_fp->get_full_file_name() << '\"' << std::endl;
    new_fp->add_include_file(schema_fp->get_full_file_name());
  }
  catch (oks::exception & ex) {
    Oks::error_msg("1") << "Caught OKS exception: " << ex.what() << std::endl;
    return 1;
  }


    //
    // Test that schema file contains necessary classes
    //

  OksClass *SWObjectClass    = findClassAndReport(kernel, "SW_Object");
  OksClass *ProgramClass     = findClassAndReport(kernel, "Program");
  OksClass *SWResourceClass  = findClassAndReport(kernel, "SW_Resource");
  OksClass *ProcessClass     = findClassAndReport(kernel, "Process");
  OksClass *ComputerClass    = findClassAndReport(kernel, "Computer");
  OksClass *ApplicationClass = findClassAndReport(kernel, "Application");
  OksClass *EnvironmentClass = findClassAndReport(kernel, "Environment");


    //
    // Allocate space for arrays which contain instances of objects
    //

  OksObject **SWObjectObjects    = new OksObject * [numberOfSWObjects];
  OksObject **ProgramObjects     = new OksObject * [numberOfPrograms];
  OksObject **SWResourceObjects  = new OksObject * [numberOfSWResources];
  OksObject **ProcessObjects     = new OksObject * [numberOfProcess];
  OksObject **ComputerObjects    = new OksObject * [numberOfComputers];
  OksObject **ApplicationObjects = new OksObject * [numberOfApplications];
  OksObject **EnvironmentObjects = new OksObject * [numberOfEnvironment];


    //
    // Create instances of objects
    //

  createInstances(numberOfSWObjects, "o_", SWObjectObjects, SWObjectClass);
  createInstances(numberOfPrograms, "p_", ProgramObjects, ProgramClass);
  createInstances(numberOfSWResources, "r_", SWResourceObjects, SWResourceClass);
  createInstances(numberOfProcess, "pr_", ProcessObjects, ProcessClass);
  createInstances(numberOfComputers, "c_", ComputerObjects, ComputerClass);
  createInstances(numberOfApplications, "a_", ApplicationObjects, ApplicationClass);
  createInstances(numberOfEnvironment, "e_", EnvironmentObjects, EnvironmentClass);


    //
    // Use 'OksDataInfo' instead of string name when
    // access attributes and relationships to
    // improve performance
    //

  OksDataInfo *ApplicationTimeout_odi		= ApplicationClass->data_info("InitTimeout");
  OksDataInfo *ApplicationNeedsEnvironment_odi	= ApplicationClass->data_info("NeedsEnvironment");
  OksDataInfo *ApplicationRunsOn_odi		= ApplicationClass->data_info("RunsOn");
  OksDataInfo *ApplicationExecutedAs_odi	= ApplicationClass->data_info("ExecutedAs");
  OksDataInfo *ApplicationSWObject_odi		= ApplicationClass->data_info("SWObject");

  OksDataInfo *ComputerOsType_odi		= ComputerClass->data_info("OsType");
  OksDataInfo *ComputerExecutes_odi		= ComputerClass->data_info("Executes");
  
  OksDataInfo *ProcessStartedFrom_odi		= ProcessClass->data_info("StartedFrom");
  OksDataInfo *ProcessRunsOn_odi		= ProcessClass->data_info("RunsOn");
  OksDataInfo *ProcessRanBy_odi			= ProcessClass->data_info("RanBy");
  OksDataInfo *ProcessHoldsResource_odi		= ProcessClass->data_info("HoldsResource");

  OksDataInfo *ProgramOsType_odi		= ProgramClass->data_info("OsType");
  OksDataInfo *ProgramDescribedBy_odi		= ProgramClass->data_info("DescribedBy");
  OksDataInfo *ProgramNeedsEnvironment_odi	= ProgramClass->data_info("NeedsEnvironment");
  OksDataInfo *ProgramExecutableFile_odi	= ProgramClass->data_info("ExecutableFile");
  OksDataInfo *ProgramDefaultParameters_odi	= ProgramClass->data_info("DefaultParameters");
  OksDataInfo *ProgramDefaultPriority_odi	= ProgramClass->data_info("DefaultPriority");
  OksDataInfo *ProgramDefaultPrivileges_odi	= ProgramClass->data_info("DefaultPrivileges");
  
  OksDataInfo *SWObjectImplementedBy_odi	= SWObjectClass->data_info("ImplementedBy");
  OksDataInfo *SWObjectNeedsEnvironment_odi	= SWObjectClass->data_info("NeedsEnvironment");
  OksDataInfo *SWObjectNeedsResources_odi	= SWObjectClass->data_info("NeedsResources");
  OksDataInfo *SWObjectName_odi			= SWObjectClass->data_info("Name");
  OksDataInfo *SWObjectDescription_odi		= SWObjectClass->data_info("Description");
  OksDataInfo *SWObjectAuthors_odi		= SWObjectClass->data_info("Authors");
  OksDataInfo *SWObjectHelpLink_odi		= SWObjectClass->data_info("HelpLink");
  OksDataInfo *SWObjectDefaultParameter_odi	= SWObjectClass->data_info("DefaultParameter");
  OksDataInfo *SWObjectDefaultPriority_odi	= SWObjectClass->data_info("DefaultPriority");
  OksDataInfo *SWObjectDefaultPrivileges_odi	= SWObjectClass->data_info("DefaultPrivileges");

  OksDataInfo *SWResourceAllocatedBy_odi	= SWResourceClass->data_info("AllocatedBy");


    // Set Application Timeouts

  {
    std::cout << "Set applications timeouts...\n";
  
    for(int i=0; i<(int)numberOfApplications; ++i) {
      OksData *d_timeout(ApplicationObjects[i]->GetAttributeValue(ApplicationTimeout_odi));
      d_timeout->data.U32_INT = (uint32_t)(rand() % 256);
    }
  }

    // set operating system type for instances of Program and Computer classes

  {
    std::cout << "Set operating system types...\n";
  
    OksAttribute *a = ProgramClass->find_attribute("OsType");
	
    for(int i=0; i<(int)numberOfPrograms; i++) {
      OksData d_osType;
	
      switch((unsigned int)(rand() % 4)) {
        case 0: d_osType.SetValues("lynx", a);    break;
        case 1: d_osType.SetValues("wnt", a);     break;
        case 2: d_osType.SetValues("solaris", a); break;
        case 3: d_osType.SetValues("hpux", a);    break;
      }

      try {
        ProgramObjects[i]->SetAttributeValue(ProgramOsType_odi, &d_osType);
      }
      catch(oks::exception& ex) {
        Oks::error_msg("10") << "Failed to set attribute value of " << ProgramObjects[i] << ": " << ex.what() << std::endl;
	return 10;
      }
    }

    for(int i=0; i<(int)numberOfComputers; i++) {
      OksData d_osType;

      switch((unsigned int)(rand() % 4)) {
        case 0: d_osType.SetValues("lynx", a);    break;
        case 1: d_osType.SetValues("wnt", a);     break;
        case 2: d_osType.SetValues("solaris", a); break;
        case 3: d_osType.SetValues("hpux", a);    break;
      }

      try {
        ComputerObjects[i]->SetAttributeValue(ComputerOsType_odi, &d_osType);
      }
      catch(oks::exception& ex) {
        Oks::error_msg("11") << "Failed to set attribute value of " << ComputerObjects[i] << ": " << ex.what() << std::endl;
	return 11;
      }
    }
  }


  if(!doNotBind) {
    std::cout << "Bind instances..." << std::endl;
	
    register int i, j, j2;
    OksData *d;
	
    for(i=0; i<(int)numberOfPrograms; ++i) {
      j = (
        (i<(int)numberOfSWObjects)
          ? i
          : (rand() % numberOfSWObjects)
      );

      ProgramObjects[i]->SetRelationshipValue(ProgramDescribedBy_odi, SWObjectObjects[j]);
      SWObjectObjects[j]->AddRelationshipValue(SWObjectImplementedBy_odi, ProgramObjects[i]);

      if(!((i+1) % 2000)) {std::cout << '*' << ' '; std::cout.flush();}
    }

    for(i=0; i<(int)numberOfProcess; ++i) {
      j = rand() % numberOfPrograms;

      ProcessObjects[i]->SetRelationshipValue(ProcessStartedFrom_odi, ProgramObjects[j]);
      OksData *d_osType(ProgramObjects[j]->GetAttributeValue(ProgramOsType_odi));

      for(;;) {
        j2 = rand() % numberOfComputers;
        OksData *d_osType2(ComputerObjects[j2]->GetAttributeValue(ComputerOsType_odi));
        if(*d_osType2 == *d_osType) break;
      }

      ComputerObjects[j2]->AddRelationshipValue(ComputerExecutes_odi, ProcessObjects[i]);
      ProcessObjects[i]->SetRelationshipValue(ProcessRunsOn_odi, ComputerObjects[j2]);
      ApplicationObjects[i]->SetRelationshipValue(ApplicationRunsOn_odi, ComputerObjects[j2]);

      ProcessObjects[i]->SetRelationshipValue(ProcessRanBy_odi, ApplicationObjects[i]);
      ApplicationObjects[i]->SetRelationshipValue(ApplicationExecutedAs_odi, ProcessObjects[i]);

      d = ProgramObjects[j]->GetRelationshipValue(ProgramDescribedBy_odi);
      ApplicationObjects[i]->SetRelationshipValue(ApplicationSWObject_odi, d->data.OBJECT);

      j = rand() % numberOfSWResources;
		
      if(j == (int)numberOfSWResources) j--;

      ProcessObjects[i]->AddRelationshipValue(ProcessHoldsResource_odi, SWResourceObjects[j]);
      SWResourceObjects[j]->AddRelationshipValue(SWResourceAllocatedBy_odi, ProcessObjects[i]);
      d->data.OBJECT->AddRelationshipValue(SWObjectNeedsResources_odi, SWResourceObjects[j]);

      if(!((i+1) % 1000)) {std::cout << "@ "; std::cout.flush();}
    }

    for(i=0; i<(int)numberOfEnvironment; ++i) {
      j = rand() % 100;
	
      if(j<25 || !(j%10))		/* needs for sw_object (32%) */
        SWObjectObjects[(rand() % numberOfSWObjects)]->AddRelationshipValue(SWObjectNeedsEnvironment_odi, EnvironmentObjects[i]);
      if((j>25 && j<50) || !(j%8))	/* needs for program  (34%) */
        ProgramObjects[(rand() % numberOfPrograms)]->AddRelationshipValue(ProgramNeedsEnvironment_odi, EnvironmentObjects[i]);
      else if(j>50 || !(j%7))		/* needs for application (57%) */
        ApplicationObjects[(rand() % numberOfApplications)]->AddRelationshipValue(ApplicationNeedsEnvironment_odi, EnvironmentObjects[i]);

      if(!((i+1) % 2500)) {std::cout << '#' << ' '; std::cout.flush();}
    }

    if(numberOfEnvironment > 2500 || numberOfProcess > 1000 || numberOfPrograms > 2000) std::cout << std::endl;
  }

  register int i;
  
  std::cout << "Set attributes...\n";
  
  for(i=0; i<(int)numberOfSWObjects; i++) {
    char buf[128];
  	
    sprintf(buf, "a server #%ld", (unsigned long)rand());
    OksData d_Name(buf);

    OksData d_Desc("This is a test server");
	
    OksData d_Auth(new OksData::List()); 
    register int j = (int)(rand() % 7) + 1;
    while(j) {
      sprintf(buf, "atdsoft #%d", j--);
      d_Auth.data.LIST->push_back(new OksData(buf));
    }

    sprintf(buf, "http://atddoc.cern.ch/Atlas/online/sw/%d.html", i);
    OksData d_Help(buf);
	
    sprintf(buf, "-test -n %d", i);
    OksData d_Prms(buf);
	
    int32_t priority = rand() % ((1<<15)-1);
    OksData d_Prir(priority);
	
    OksData d_Priv("no");
	
    SWObjectObjects[i]->SetAttributeValue(SWObjectName_odi, &d_Name);
    SWObjectObjects[i]->SetAttributeValue(SWObjectDescription_odi, &d_Desc);
    SWObjectObjects[i]->SetAttributeValue(SWObjectAuthors_odi, &d_Auth);
    SWObjectObjects[i]->SetAttributeValue(SWObjectHelpLink_odi, &d_Help);
    SWObjectObjects[i]->SetAttributeValue(SWObjectDefaultParameter_odi, &d_Prms);
    SWObjectObjects[i]->SetAttributeValue(SWObjectDefaultPriority_odi, &d_Prir);
    SWObjectObjects[i]->SetAttributeValue(SWObjectDefaultPrivileges_odi, &d_Priv);
  }


    // free list of SWObject class instances

  delete[] SWObjectObjects;
  

  for(i=0; i<(int)numberOfPrograms; i++) {
    char buf[128];
    OksData *d_osType(ProgramObjects[i]->GetAttributeValue("OsType"));
 
    sprintf(
      buf,
      "/usr/local/dist/last/installed/g++/%s/bin/s%d",
      d_osType->data.ENUMERATION->c_str(),
      rand()
    );
    OksData d_ExecutableFile(buf);
	
    sprintf(buf, "-test -n %d", i);
    OksData d_Prms(buf);
	
    int32_t priority = rand() % ((1<<15)-1);
    OksData d_Prir(priority);

    OksData d_Priv("no");
	
    ProgramObjects[i]->SetAttributeValue(ProgramExecutableFile_odi, &d_ExecutableFile);
    ProgramObjects[i]->SetAttributeValue(ProgramDefaultParameters_odi, &d_Prms);
    ProgramObjects[i]->SetAttributeValue(ProgramDefaultPriority_odi, &d_Prir);
    ProgramObjects[i]->SetAttributeValue(ProgramDefaultPrivileges_odi, &d_Priv);
  }


    // free list of Program class instances

  delete[] ProgramObjects;


    // free list of other class instances

  delete[] SWResourceObjects;
  delete[] ProcessObjects;
  delete[] ComputerObjects;
  delete[] ApplicationObjects;
  delete[] EnvironmentObjects;

  auto tp = std::chrono::steady_clock::now();

  try {
    kernel.save_data(new_fp, true);
  }
  catch (oks::exception & e) {
    Oks::error_msg("4") << "cannot save oks database data file \"" << dataFile << "\": " << e.what() << std::endl;
    return 4;
  }
  catch (...) {
    Oks::error_msg("4") << "cannot save oks database data file \"" << dataFile << '\"' << std::endl;
    return 4;
  }

  std::cout << "Time to save data is " << std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-tp).count() / 1000. << " ms" << std::endl;


  if(fastExit) {
    new_fp->unlock();
    exit(0);
  }

  return 0;
}
```

### `tests/test_indexies.cpp`  
*Local path: `repo/oks_utils/tests/test_indexies.cpp`*

```cpp
#include <iostream>
#include <stdlib.h>

#include <oks/kernel.h>
#include <oks/object.h>
#include <oks/class.h>
#include <oks/index.h>
#include <oks/attribute.h>

const char *appName;
const char *appTitle = "OKS indices tester.";

static void printUsage(const char *appName)
{
  std::cerr << appTitle << " Oks Kernel version " << OksKernel::GetVersion() << "\n"
	  "Usage: " << appName << " [-h[elp]] [-v] SchemaFile DataFile ClassName AttributeName options [options]\n"
	  "  Options:\n"
	  "\te value              - search == \'value\'\n"
	  "\tl value              - search < \'value\'\n"
	  "\tle value             - search <= \'value\'\n"
	  "\tg value              - search > \'value\'\n"
	  "\tge value             - search >= \'value\'\n"
	  "\tlog value1 value2    - search < \'value1\' or > \'value2\'\n"
	  "\tloge value1 value2   - search < \'value1\' or >= \'value2\'\n"
	  "\tleog value1 value2   - search <= \'value1\' or > \'value2\'\n"
	  "\tleoge value1 value2  - search <= \'value1\' or >= \'value2\'\n"
	  "\teoe value1 value2    - search == \'value1\' or == \'value2\'\n"
	  "\teol value1 value2    - search == \'value1\' or < \'value2\'\n"
	  "\teole value1 value2   - search == \'value1\' or <= \'value2\'\n"
	  "\teog value1 value2    - search == \'value1\' or > \'value2\'\n"
	  "\teoge value1 value2   - search == \'value1\' or >= \'value2\'\n"
	  "\tlag value1 value2    - search < \'value1\' and > \'value2\'\n"
	  "\tlage value1 value2   - search < \'value1\' and >= \'value2\'\n"
	  "\tleag value1 value2   - search <= \'value1\' and > \'value2\'\n"
	  "\tleage value1 value2  - search <= \'value1\' and >= \'value2\'\n"
	  "\teae value1 value2    - search == \'value1\' and == \'value2\'\n"
	  "\teal value1 value2    - search == \'value1\' and < \'value2\'\n"
	  "\teale value1 value2   - search == \'value1\' and <= \'value2\'\n"
	  "\teag value1 value2    - search == \'value1\' and > \'value2\'\n"
	  "\teage value1 value2   - search == \'value1\' and >= \'value2\'\n"
	  "\t-v    prints version\n"
	  "\t-h\n"
	  "\t-help prints this text\n\n";
}


int main(int argc, char** argv)
{
  OksKernel kernel;
  
  appName = argv[0];
  
  argv++;
  argc--;
  
  if(argc > 0) {
	if(
		!strcmp(argv[0], "-h") ||
		!strcmp(argv[0], "-help")
	) {
		printUsage(appName);
		return 0;
	}
	
	if(!strcmp(argv[0], "-v")) {
		std::cout << appTitle << " Oks Kernel version " << OksKernel::GetVersion() << std::endl;
		argv++;
		argc--;
	}
	
  }
  
  if(argc < 6) {
	printUsage(appName);
	return -1;
  }
  
  char *schemaFile = argv[0];
  char *dataFile = argv[1];
  char *className = argv[2];
  char *attributeName = argv[3];
  
  if(kernel.load_schema(schemaFile) == 0) {
    std::cerr << "ERROR[1]: Can`t load oks database schema file \"" << schemaFile << "\", exiting ...\n";
    return 1;
  }
  
  
  if(kernel.load_data(dataFile) == 0) {
    std::cerr << "ERROR[2]: Can`t load database data file \"" << dataFile << "\", exiting ...\n";
    return 2;
  }
  
  OksClass *classPnt = kernel.find_class(className);

  if(!classPnt) {
    std::cerr << "ERROR[3]: Can`t find class \"" << className << "\", exiting ...\n";
    return 3;
  }

  OksAttribute *attributePnt = classPnt->find_attribute(attributeName);

  if(!attributePnt) {
    std::cerr << "ERROR[4]: Can`t find attribute \"" << attributeName << "\" in class \"" << className << "\", exiting ...\n";
    return 4;
  }

  OksIndex index(classPnt, attributePnt);

  argv += 4;
  argc -= 4;
  
  try { while(argc > 1) {
    std::cout << std::endl;

    OksObject::List * olist = 0;
    OksData d, d2;

    if(!strcmp(argv[0], "e")) {
      d.SetValues(argv[1], attributePnt);
      
      std::cout << "Find all equal to " << d << std::endl;
      olist=index.FindEqual(&d);
      argv += 2;
      argc -= 2;
    }
    else if(!strcmp(argv[0], "l")) {
      d.SetValues(argv[1], attributePnt);
      
      std::cout << "Find all less then " << d << std::endl;
      olist=index.FindLess(&d);
      argv += 2;
      argc -= 2;
    }
    else if(!strcmp(argv[0], "le")) {
      d.SetValues(argv[1], attributePnt);
      
      std::cout << "Find all less-equal then " << d << std::endl;
      olist=index.FindLessEqual(&d);
      argv += 2;
      argc -= 2;
    }
    else if(!strcmp(argv[0], "g")) {
      d.SetValues(argv[1], attributePnt);
      
      std::cout << "Find all greate then " << d << std::endl;
      olist=index.FindGreat(&d);
      argv += 2;
      argc -= 2;
    }
    else if(!strcmp(argv[0], "ge")) {
      d.SetValues(argv[1], attributePnt);
      
      std::cout << "Find all greate-equal then " << d << std::endl;
      olist=index.FindGreatEqual(&d);
      argv += 2;
      argc -= 2;
    }
    else if(!strcmp(argv[0], "log")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less then " << d << " or greate then " << d2 << std::endl;
      olist=index.FindLessOrGreat(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "loge")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less then " << d << " or greate-equal then " << d2 << std::endl;
      olist=index.FindLessOrGreatEqual(&d, &d2);
      argv += 3;
      argc -= 3;
      }
    else if(!strcmp(argv[0], "leog")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less-equal then " << d << " or greate then " << d2 << std::endl;
      olist=index.FindLessEqualOrGreat(&d, &d2);
      argv += 3;
      argc -= 3;
      }
    else if(!strcmp(argv[0], "leoge")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less-equal then " << d << " or greate-equal then " << d2 << std::endl;
      olist=index.FindLessEqualOrGreatEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eoe")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " or equal to " << d2 << std::endl;
      olist=index.FindEqualOrEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eol")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " or less then " << d2 << std::endl;
      olist=index.FindEqualOrLess(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eole")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " or less-equal then " << d2 << std::endl;
      olist=index.FindEqualOrLessEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eog")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " or greate then " << d2 << std::endl;
      olist=index.FindEqualOrGreat(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eoge")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " or greate-equal then " << d2 << std::endl;
      olist=index.FindEqualOrGreatEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "lag")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less then " << d << " and greate then " << d2 << std::endl;
      olist=index.FindLessAndGreat(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "lage")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less then " << d << " and greate-equal then " << d2 << std::endl;
      olist=index.FindLessAndGreatEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "leag")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less-equal then " << d << " and greate then " << d2 << std::endl;
      olist=index.FindLessEqualAndGreat(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "leage")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all less-equal then " << d << " and greate-equal then " << d2 << std::endl;
      olist=index.FindLessEqualAndGreatEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eae")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " and equal to " << d2 << std::endl;
      olist=index.FindEqualAndEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eal")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " and less then " << d2 << std::endl;
      olist=index.FindEqualAndLess(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eale")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " and less-equal then " << d2 << std::endl;
      olist=index.FindEqualAndLessEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eag")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " and greate then " << d2 << std::endl;
      olist=index.FindEqualAndGreat(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else if(!strcmp(argv[0], "eage")) {
      d.SetValues(argv[1], attributePnt);
      d2.SetValues(argv[2], attributePnt);
      
      std::cout << "Find all equal to " << d << " and greate-equal then " << d2 << std::endl;
      olist=index.FindEqualAndGreatEqual(&d, &d2);
      argv += 3;
      argc -= 3;
    }
    else {
      std::cerr << "ERROR[5]: Unknown option \"" << argv[0] << "\", exiting ...\n";
      return 5;
    }
    
    if(olist) {
      std::cout << "Query returns " << olist->size() << " objects:\n";
    
      OksObject::List::iterator it = olist->begin();
    
      size_t idLength = 5, valueLength = 7;

      for(;it != olist->end();++it) {
        OksData *d((*it)->GetAttributeValue(attributeName));
        std::string s = d->str();

        if((*it)->GetId().length() > idLength) idLength = (*it)->GetId().length();
        if(s.length() > valueLength) valueLength = s.length();
      }

      std::cout.fill('=');
      std::cout.width(idLength + valueLength + 7);
      std::cout << "" << std::endl;
      
      std::cout.fill(' ');

      std::cout.width(idLength + 3);
      std::cout << '|' << "Id |";

      std::cout.width(valueLength + 3);
      std::cout << "Value |" << std::endl;

      std::cout.fill('=');
      std::cout.width(idLength + valueLength + 7);
      std::cout << "" << std::endl;

      std::cout.fill(' ');

      for(it = olist->begin();it != olist->end();++it) {
        OksData *d((*it)->GetAttributeValue(attributeName));

        std::cout.width(idLength);
        std::cout << '|' << ' ' << (*it)->GetId().c_str() << ' ' << '|'; 

        std::cout.width(valueLength);

        std::string s = d->str();
        std::cout << ' ' << s << ' ' << '|' << std::endl;
      }

      std::cout.fill('=');
      std::cout.width(idLength + valueLength + 7);
      std::cout << "" << std::endl;

      delete olist;
    }
    else
      std::cout << "Nothing was found\n";

    std::cout << std::endl << std::endl;
  }
  } catch(oks::exception & ex) {
    std::cerr << "Caught exception: " << ex.what() << std::endl;
    return 1;
  }

  return 0;
}
```

### `tests/test.sh`  
*Local path: `repo/oks_utils/tests/test.sh`*

```sh
#!/bin/sh

########################################################################

echo "CHECKING ALLOC and MEMORY-ALLOCATION-MUTEX MECHANISMS..."

if ${1}/oks_utils_alloc_test
then
  echo "alloc check passed";
else
  echo "OKS Error: alloc check failed"
  exit 1
fi

########################################################################

schema_file="/tmp/oks_tutorial.schema.$$.xml"
data_file="/tmp/oks_tutorial.data.$$.xml"

########################################################################

echo "CHECKING OKS LIBRARY..."

if ${1}/oks_tutorial ${schema_file} ${data_file}
then
  echo "oks_tutorial check passed";
else
  echo "OKS Error: check failed with oks_tutorial"
  exit 1
fi

if oks_dump ${schema_file} ${data_file}
then
  echo "oks_dump check passed"
else
  echo "OKS Error: check failed with oks_dump"
  exit 1
fi

rm -f ${schema_file} ${data_file}

echo "DONE CHECKING OKS LIBRARY..."

########################################################################
```

### `cmt/requirements`  
*Local path: `repo/oks_utils/cmt/requirements`*

```text
package oks_utils

##########################################################################################

author	Igor.Soloviev@cern.ch
manager	Igor.Soloviev@cern.ch

##########################################################################################

use OnlinePolicy

##########################################################################################

# the variable OKS_GUI_PATH defines a token directory to search for online configuration
# files used by the OKS Data Editor

path_remove     OKS_GUI_PATH                		"$(prefix)/share/data"
path_append     OKS_GUI_PATH                		"$(prefix)/share/data"


# the variable OKS_GUI_HELP_URL defines path to the OKS Data Editor online help

set		OKS_GUI_HELP_URL			"file:${TDAQ_INST_PATH}/share/data/oks/online-help/data-editor/"


# the variable BOOST_DATE_TIME_TZ_SPEC defines path
# to the Boost date_time_zonespec.csv file missing in LCG installation

set             BOOST_DATE_TIME_TZ_SPEC                 "${prefix}/share/data/Boost/date_time_zonespec.csv"

##########################################################################################

private

use Boost  * TDAQCExternal
use CORAL  * TDAQExternal

use oks
use xmext
use ers
use config
use cmdl
use system
use AccessManager

##########################################################################################

# uncomment this for local build in case of headers changes
macro_prepend  includes                                 '-I../src'

##########################################################################################

set             OKS_DB_ROOT                             $(TDAQ_DB_PATH)

##########################################################################################

macro		LcgLibs "-llcg_RelationalAccess -llcg_CoralBase -lboost_date_time-$(boost_libsuffix)"

library         roks $(lib_opts)                        ../src/rlib/*.cpp
macro           lib_roks_pp_cppflags                    $(LcgIncludes)
macro           roks_shlibflags                         " -loks $(LcgLibs)"

library         oks_utils $(lib_opts)                   ../src/lib/*.cpp
macro           oks_utils_shlibflags                    " -lboost_date_time-$(boost_libsuffix) -lAccessManager -loks "

application     OKS_commit -no_prototypes               ../src/bin/oks_commit.c
macro           OKS_commitlinkopts                      "-lpam"

application     OKS_commit_exec -no_prototypes          ../src/bin/oks_commit_exec.cpp
macro           OKS_commit_execlinkopts                 "-loks -lAccessManager -lcmdline -lboost_filesystem-$(boost_libsuffix)"

application     oks_report_equal_objects -no_prototypes ../src/bin/oks_report_equal_objects.cpp
macro           oks_report_equal_objectslinkopts        "-loks -lboost_program_options-$(boost_libsuffix)"

application     oks_put_schema -no_prototypes           ../src/bin/oks_put_schema.cpp
macro           oks_put_schemalinkopts                  "-lroks -loks "
macro           oks_put_schema_dependencies             roks

application     oks_put_data -no_prototypes             ../src/bin/oks_put_data.cpp
macro           oks_put_datalinkopts                    "-lroks -loks "
macro           oks_put_data_dependencies               roks

application     oks_get_schema -no_prototypes           ../src/bin/oks_get_schema.cpp
macro           oks_get_schemalinkopts                  "-lroks -loks "
macro           oks_get_schema_dependencies             roks

application     oks_get_data -no_prototypes             ../src/bin/oks_get_data.cpp
macro           oks_get_datalinkopts                    "-lroks -loks "
macro           oks_get_data_dependencies               roks

application     oks_tag_data -no_prototypes             ../src/bin/oks_tag_data.cpp
macro           oks_tag_datalinkopts                    "-lroks -loks "
macro           oks_tag_data_dependencies               roks

application     oks_ls_data -no_prototypes              ../src/bin/oks_ls_data.cpp
macro           oks_ls_datalinkopts                     "-loks_utils -lroks -loks "
macro           oks_ls_data_dependencies                "roks oks_utils"

library         xmoks $(lib_opts)                       ../src/xm-lib/*.cpp
macro           lib_xmoks_pp_cppflags                   '$(X_includes) -I../src'
macro           xmoks_shlibflags                        " $(X_linkopts) -loks -lxmext "

application     oks_report_bad_classes -no_prototypes   ../src/bin/oks_report_bad_classes.cpp
macro           oks_report_bad_classeslinkopts          "-loks"

application	oks_merge -no_prototypes		../src/bin/oks_merge.cpp
macro		oks_mergelinkopts			"-loks"

application	oks_diff_data -no_prototypes		../src/bin/oks_diff_data.cpp
macro		oks_diff_datalinkopts			"-loks"

application	oks_diff_schema -no_prototypes		../src/bin/oks_diff_schema.cpp
macro		oks_diff_schemalinkopts			"-loks"

application	oks_tutorial -no_prototypes	 	../src/bin/oks_tutorial.cpp
macro		oks_tutoriallinkopts			"-loks"

application	oks_data_editor -no_prototypes		../src/xm-gui/data_editor*.cpp		\
							../src/xm-gui/g_class.cpp		\
							../src/xm-gui/g_context.cpp		\
							../src/xm-gui/g_dnd.cpp			\
							../src/xm-gui/g_ref_tree.cpp		\
							../src/xm-gui/g_window*.cpp		\
							../src/xm-gui/g_object*.cpp
macro		app_oks_data_editor_pp_cppflags		'$(X_includes) -I../src'
macro           oks_ral_cpp_cppflags                    '-DTDAQ_CMT_RELEASE=\"${CMTRELEASE}\" '
macro           oks_get_schema_cppflags                 '-DTDAQ_CMT_RELEASE=\"${CMTRELEASE}\" '
macro           oks_get_data_cppflags                   '-DTDAQ_CMT_RELEASE=\"${CMTRELEASE}\" '
macro           oks_tag_data_cppflags                   '-DTDAQ_CMT_RELEASE=\"${CMTRELEASE}\" '
macro		data_editor_main_dlg_cpp_cppflags	'-DOKS_DATA_EDITOR_ONLINE_HELP_DIR=\"$(help_dir)/\" '
macro		oks_data_editorlinkopts			"-loks_utils -lxmoks -loks $(xmext_libs) -lboost_filesystem-$(boost_libsuffix) $(X_linkopts)"
macro		oks_data_editor_dependencies		"xmoks oks_utils"

application	oks_schema_editor -no_prototypes	../src/xm-gui/schema_editor*.cpp
macro		app_oks_schema_editor_pp_cppflags	'$(X_includes) -I../src'
macro		oks_schema_editorlinkopts		"-lxmoks -loks $(xmext_libs) $(X_linkopts)"
macro		oks_schema_editor_dependencies		xmoks

##########################################################################################

# TESTS

macro		PATH_TO_SCHEMA				"../tests/DAQ-Configuration.schema.xml"

application	oks_generate_data -no_prototypes	../tests/generate_data.cpp
macro		generate_data_cpp_cppflags		'-DPATH_TO_SCHEMA=\"$(PATH_TO_SCHEMA)/\" '
macro		oks_generate_datalinkopts		"-loks"

application	oks_time_tests -no_prototypes		../tests/time_tests.cpp
macro		time_tests_cpp_cppflags			'-DPATH_TO_SCHEMA=\"$(PATH_TO_SCHEMA)/\" '
macro		oks_time_testslinkopts			"-loks"

application	oks_test_indexies -no_prototypes	../tests/test_indexies.cpp
macro		oks_test_indexieslinkopts		"-loks"

##########################################################################################

# EXAMPLES

application	alloc -no_prototypes			../examples/alloc.cpp
macro           alloclinkopts                           "-l boost_system-$(boost_libsuffix)"

application	attribute -no_prototypes		../examples/attribute.cpp
macro		attributelinkopts			"-loks"

application	relationship -no_prototypes		../examples/relationship.cpp
macro		relationshiplinkopts			"-loks"

application	method -no_prototypes			../examples/method.cpp
macro		methodlinkopts				"-loks"

application	class -no_prototypes			../examples/class.cpp
macro		classlinkopts				"-loks"

application	data -no_prototypes			../examples/data.cpp
macro		datalinkopts				"-loks"

application	object -no_prototypes			../examples/object.cpp
macro		objectlinkopts				"-loks"

application	kernel -no_prototypes			../examples/kernel.cpp
macro		kernellinkopts				"-loks"

application	comparator -no_prototypes		../examples/comparator.cpp
macro		comparatorlinkopts			"-loks"

application	r_expression -no_prototypes		../examples/r_expression.cpp
macro		r_expressionlinkopts			"-loks"

application	not_expression -no_prototypes		../examples/not_expression.cpp
macro		not_expressionlinkopts			"-loks"

application	and_expression -no_prototypes		../examples/and_expression.cpp
macro		and_expressionlinkopts			"-loks"

application	or_expression -no_prototypes		../examples/or_expression.cpp
macro		or_expressionlinkopts			"-loks"

application	query -no_prototypes			../examples/query.cpp
macro		querylinkopts				"-loks"

application	index -no_prototypes			../examples/index.cpp
macro		indexlinkopts				"-loks"

application	profiler -no_prototypes			../examples/profiler.cpp
macro		profilerlinkopts			"-loks"

##########################################################################################

#### install libraries ####

apply_pattern	install_libs                            files="                           \
                                                                libroks.so              \
                                                                libxmoks.so             \
                                                                liboks_utils.so         \
                                                      "

#### install binaries ####

apply_pattern	install_apps				files="				\
								oks_schema_editor	\
								oks_data_editor		\
								oks_tutorial		\
								oks_diff_schema		\
								oks_diff_data		\
								oks_merge		\
                                                                oks_report_equal_objects\
								oks_put_schema		\
								oks_put_data		\
								oks_get_schema		\
								oks_get_data		\
                                                                oks_tag_data            \
                                                                oks_ls_data             \
                                                                OKS_commit              \
                                                                OKS_commit_exec         \
							"


#### install online help for OKS data editor ####

macro		help_src				"../data/online-help/data-editor"
macro		help_dest				"../oks/online-help/data-editor"
macro		help_dir				"$(prefix)/share/data/oks/$(help_dest)"

apply_pattern   install_data name=online_help_html 	src_dir="$(help_src)"		\
							target_dir="$(help_dest)"	\
							files="*.html"

apply_pattern   install_data name=online_help_gif 	src_dir="$(help_src)"		\
							target_dir="$(help_dest)"	\
							files="*.gif"


#### install headres ####

ignore_pattern  inst_headers_auto
apply_pattern   install_headers name=oks_h              src_dir="../oks"                \
                                                        target_dir="../oks"             \
                                                        files="ral.h tz.h access.h"

#### install configuration schema file for oks-data-editor ####

apply_pattern   install_data    name=data_editor_xml	src_dir="../src/xm-gui"         \
							target_dir="../oks/gui"         \
							files="*.xml"

apply_pattern   install_data    name=gui_def_params_xml src_dir="../src/xm-lib"         \
                                                        target_dir="../oks/gui"         \
                                                        files="*.xml"

#### install oks xsl file ####

apply_pattern   install_data    name=xsl                src_dir="../data/xsl"		\
							target_dir="../oks/xsl"		\
							files="*.xsl"


#install Boost date_time_zonespec.csv file missing in LCG installation

apply_pattern   install_data name=boost_tz_info         src_dir="../src/rlib"           \
                                                        target_dir="../Boost"           \
                                                        files="date_time_zonespec.csv"

##########################################################################################

#### check ####

apply_pattern   check_target name=oks 			file="../cmt/test.sh" args="$(bin)"

##########################################################################################
```


## 3. `swrod` — Software Readout Driver (GitLab)

The SW ROD (Software Readout Driver) uses OKS/DUNE DAQ configuration for its data-link and module definitions (schema `schema/swrod.schema.xml`, data files in `data/`). `test/oks2json.cpp` shows OKS config being translated to JSON. Only the OKS-relevant subset is embedded.
### `README.md`  
*Local path: `repo/swrod/README.md`*

```markdown
# SW ROD

This is the implementation of SW ROD readout application of the ATLAS TDAQ system that is based on the [Phase-I SW ROD Architectural Analysis and Design](https://cds.cern.ch/record/2671987) document, which addresses the requirements provided by detector community, which are described in the [Phase-I SW ROD User Requirements](https://edms.cern.ch/document/1832704/1.10) document. The package is distributed as part of the [ATLAS TDAQ software release](http://atlas-tdaq-sw.web.cern.ch/atlas-tdaq-sw/). Custom SW ROD components development shall follow the [TDAQ software development procedure](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DaqHltCMake).

## Introduction
SW ROD is envisaged to act in the ATLAS data flow chain as the data-handling interface between the FELIX readout system and the ATLAS High-Level Trigger (HLT). SW ROD implements ROB fragment building and formatting, which in the Run-1/2 systems were done by the detector specific Readout Driver (ROD) components. SW ROD also furnishes the same buffering and HLT request processing capabilities as provided by the Readout System (ROS) of the legacy DAQ.

## SW ROD Application
SW ROD functionality is provided by multiple homogeneous SW processes running on a cluster of commodity computers. All processes originate from the same binary executable, called **swrod_application**, but they diverge by using different configuration parameters such as a set of FELIX E-Links for receiving data, data processing algorithms, HLT request processing parameters and so on.

The SW ROD application is fully integrated with the TDAQ online infrastructure. It implements the Run Control Finite State Machine (FSM) and is configured using the standard TDAQ Configuration service. It also implements the Event Monitoring Sampler interface and publishes its operational statistics to the TDAQ Information Service.

## Integrating Custom Processing into the SW ROD Application
The SW ROD Application provides a framework for executing detector specific code that is required for:
 * Extracting TTC information (L1ID and BCID) from input data packets.
 * Verifying integrity of input data packets.
 * Applying custom detector-specific processing to fully aggregated ROB fragments.

The corresponding procedures must be implemented by a custom detector specific shared library, which should provide three functions with well-defined signatures as described in the following sections. Such a library is advertised to the SW ROD Application via an object of the **SwRodCustomProcessingLib** OKS configuration class that must declare the names of the custom functions. This object must be linked with each data channel, aka ROD, that is represented by an instance of the **SwRodDataChannel** OKS class.

> **NOTE:** Custom functions must be declared using **extern "C"** specifier that guarantees that the functions run-time symbolic references will be the same as the function names.

### TTC Information Extraction Function
A function that implements TTC information extraction is mandatory and should be implemented along the lines demonstrated by the following example:

~~~cpp
extern "C"
std::tuple<uint32_t, uint32_t, uint16_t> testTriggerInfoExtractor(const uint8_t * data, uint32_t size) {
  if (size < 2) {
    throw swrod::Exception(std::format("Data packet is too short: {} byte(s)", size));
  }
  uint8_t type = data[0]>>6;
  if (type == 1) {
    return std::tuple(
        data[1],     // L1ID
        0xff,        // L1ID width is 8 bits
        0xffff);     // no BCID
  } else if (type == 2) {
    if (size < 4) {
      throw swrod::Exception(std::format("Data packet is too short: {} byte(s)", size));
    }
    return std::tuple(
        data[2] | data[3]<<8),           // 2 LSBs of the L1ID (little-endian)
        0xffff,                          // L1ID width is 16 bits
        (data[0] | data[1]<<8) & 0xFFF); // 12-bit BCID
  } else {
    throw swrod::Exception(std::format("Data packet has invalid type: {}", +type));
  }
}
~~~

A TTC information extraction function has two parameters: a pointer to the memory block that contains data packet to be processed and the size of this data packet in bytes. The first parameter points to the beginning of the data packet payload meaning that any meta-data, like for example FELIX header or communication protocol header, are intentionally omitted. This function must return a 3-tuple with the following values extracted from the given data packet:
 * **l1id**: 32-bit value that contains all available bits of the extended L1ID.
 * **l1id_mask**: 32-bit mask that defines how many bits of extended L1ID are provided by the first value. The bits, which are present in the L1ID value must be set to 1 in this mask, while all other bits must be set to 0. For example if the data packet contains only the 8 least significant bits of the extended L1ID then the mask value must be set to **0xFF**. If a full extended L1ID is present in the given data packet, then the mask value must be set to **0xFFFFFFFF**.
 * **bcid**: 16-bit BCID value from the given data packet. If no BCID is present in the data packet the value must be set to **0xFFFF**.

This function may also throw **swrod::Exception** if TTC information cannot be reliably extracted from the given data packet. Any implementation of the SW ROD fragment builder algorithm must handle such an exception gracefully. A custom TTC information extraction function may use existing **swrod::Exception** class that is declared in the **swrod/exceptions.h** file or it can declare a custom exception class that in this case must inherit from **swrod::Exception**.

### Data Integrity Check Function
Optionally, a custom plugin library can provide a function to be used to check integrity of a given data packet. If data packet format contains a CRC value that was calculated using a known algorithm, then such a function can apply the same algorithm to this packet and compare its result with that value. The following pseudo-code illustrates this idea:

~~~cpp
extern "C"
std::optional<bool> testDataIntegrityChecker(const uint8_t * data, uint32_t size) {
  if (not contains_checksum_value(packet)) {
    return std::nullopt; // packet has no checksum
  }
  else {
    return (calculate_checksum(packet) == get_checksum_value(packet));
  }
}
~~~

It is up to the fragment building algorithm implementation how to use this function. For performance reasons the existing algorithm implementations call this function only in case of TTC information mismatch between data and L1A packets.

### Custom Processing
The last function that may be provided by a custom plugin library is also optional and should be implemented only if a detector specific processing must be applied to the ROB fragments produced by the fragment building algorithm. In this case such a function has to implement a factory for detector-specific class that implements the **swrod::CustomProcessor** interface. The following code demomnstrates a possible implementation of this function:

~~~cpp
extern "C"
swrod::CustomProcessor * createTestCustomProcessor(const boost::property_tree::ptree & config) {
    return new TestCustomProcessor(config.get<int64_t>("CustomLongIntAttribute"));
}
~~~

> **Note**: The **config** object passed to this function contains configuration parameters declared in the corresponding instance of the **SwRodDataChannel** OKS class. It is possible to add an arbitrary number of custom parameters to the **config** object by creating a new OKS class that inherits from the **SwRodDataChannel** and declares these parameters as its attributes. To retrieve the value of a custom attribute one should use the *boost::property_tree::ptree::get()* function specifying the corresponding attribute type as template parameter and the attribute name as the function argument.

A custom class that inherits the from the **swrod::CustomProcessor** interface must implement the _processROBFragment(swrod::ROBFragment & )_ pure virtual function. For scalability, SW ROD may create multiple instances of the **swrod::CustomProcessor** class as defined by the **WorkersNumber** attribute of the corresponding **SwRodCustomProcessor** configuration object. Each instance runs in a dedicated thread, meaning that an implementation of the **SwRodCustomProcessor** interface does not need to handle thread safety unless it accesses global resources. It is guaranteed that each object of the custom processing class will be used by exactly one thread, so there is no need to protect access to the object's member variables.

> **Note**: To activate custom processing an instance of the **SwRodCustomProcessor** class must be created in the SWROD configuration and linked to the **SwRodRob** objects via the _Consumers_ relationship.

The _processROBFragment(swrod::ROBFragment & )_ function is called for every ROB fragment produced by the fragment building algorithm of the corresponding ROB. The ROB fragment is passed to this function as a reference to an instance of the **swrod::ROBFragment** class. This class declares several constant attributes. that describe the read-only properties of the fragment. The other, non-read-only attributes can be freely modified by the custom processing procedure:
 * **m_detector_type**: 32-bit value that will be set to the _Detector Event Type_ field of the ROD header.
 * **m_rod_minor_version**: 16-bit value that will be set to the lower 2 bytes of the _Format Version Number_ field of the ROD header.
 * **m_status_front**: if set to true the ROD fragment status words will be placed right after the ROD header, otherwise they will be put at the end of the ROD fragment. Default value is true.
 * **m_status_words**: an originally empty vector of status words. Custom processor may add any number of 32-bit words to this vector. All these words will be added to the ROD fragment status section.
 * **m_data**: this is a vector containing the fragment payload, which may be split into multiple memory blocks. Normally, the number of memory blocks equals the number of data-receiving threads, but this is not always guaranteed, as it may depend on the specific implementation of the fragment-building algorithm Each memory block is managed by an instance of the **swrod::ROBFragment::DataBlock** class, which provides several functions for accessing and modifying the data within the block. The format of the data in a memory block depends on the fragment-building algorithm used to generate the ROB fragment. A detailed description of the data format for fragments produced by existing SW ROD algorithms is provided in the following sections.

### ROB Fragment Memory Management
For performance reasons, fragment-building algorithms use pre-allocated memory blocks of fixed size to store ROB fragments they produce. The size of these blocks is determined using the **SwRodFragmentBuilder::MaxMessageSize** and **MemoryPool::PageSize** configuration parameters. Different algorithms may calculate this size in different ways, as explained in the following sections. This approach minimizes the memory footprint of SW ROD applications. The goal is to set the memory block size to the smallest value sufficient to accommodate the majority (e.g., ~99%) of the ROB fragments produced by the corresponding detector component. Rare, larger fragments will be split across multiple memory blocks.

The memory pool can be configured using the the **MemoryPool** configuration class. Each **SwRodApplication** object must be linked to an instance of the **MemoryPool**, which defines default configuration for all ROBs handled by the given SW ROD application. This configuration can be overridden for a specific ROB by linking another instance of the **MemoryPool** with the corresponding **SwRodRob** object.  The **MemoryPool** class has two parameters:
 * **PageSize**: This parameter defines the default size of individual memory pages allocated by this memory pool. Note that this value can be overridden by fragment builder implementation, in which case this must be explained in the algorithm's description.
 * **NumberOfPages**: This parameter defines the number of pages that will be pre-allocated before a new run is started. The maximum number of pages that can be allocated by the memory pool is unlimited.

Custom processing function may need to reformat ROB fragment's payload in a way that would require to increase its size. In such a case it is strongly recommended to adjust the **SwRodFragmentBuilder::MaxMessageSize** and **MemoryPool::PageSize** parameters of the SW ROD configuration such that the memory blocks allocated by the algorithm will have enough spare space to accommodate the extra amount of data (at least for the bulk of the fragments). If modifying the configuration is not possible, then the custom processing function may allocate a new contiguous memory block of sufficient size using either the standard C++ **new** operator or a custom memory management routine and copy the reformatted data into the new block. The following example demonstrates this process.

~~~cpp
class TestCustomProcessor: public swrod::CustomProcessor {
public:
    explicit TestCustomProcessor(uint64_t tag) {
        m_tag = tag;
    }

    void processROBFragment(swrod::ROBFragment & fragment) override {
        fragment.m_status_words.push_back(0x0a);
        fragment.m_status_words.push_back(0x0b);
        fragment.m_status_words.push_back(0x0c);
        fragment.m_rod_minor_version = 15;
        fragment.m_detector_type = 0x222;
        fragment.m_status_front = false;

        for (auto & block : fragment.m_data) {
            swrod::GBTChunk::Header header{0, 0, 0, 0xffffffff};
            if (!block.append(header, &m_tag, sizeof(m_tag))) {
                // The memory block is not large enough to accommodate extra data
                // Allocate a new memory block of sufficient size, copy the
                // original data there and add the custom tag at the end

                // The size is in 4-byte words
                uint32_t size = block.dataSize() +
                        ((sizeof(m_tag) + sizeof(swrod::GBTChunk::Header) + 3)>>2);
                uint32_t * data = new uint32_t[size];
                memcpy(data, block.dataBegin(), block.dataSize()<<2);

                block = swrod::ROBFragment::DataBlock(data, size, block.dataSize());
                block.append(header, &m_tag, sizeof(m_tag));
            }
        }
    }
private:
    uint64_t m_tag;
};
~~~

A custom processing function may also modify the size of the **m_data** vector by either adding new memory blocks or removing obsolete ones. For example, if **m_data** vector contains multiple memory blocks that need to be completely restructured, it may be more efficient to allocate a single memory block of sufficient size and copy the contents of the original memory blocks into the new one after applying the necessary transformations. Finally, the original memory blocks must be replaced with the new block in the **m_data** vector.

### Using Custom Plugin Test application
The **swrod** package provides an application for validating and profiling custom plugins. This application, called swrod_custom_plugin_test, can be used as follows:

 * On the first invocation, the following parameters must be specified:

   *  The name of the data file to be used as the data source.
   *  The name of the shared library that implements the plugin to be tested.
   *  The names of the three custom functions implemented by this plugin. Optionally, the -o <json file name> option can be used to save the new configuration to a specified JSON file.

 * If a JSON configuration file has been generated, the test application can be started using this file as the sole input parameter by specifying it with the -i <json file name> command-line option.

## Fragment Building Algorithms
A SW ROD fragment-building algorithm is designed to collect data packets that share the same unique identifier — such as the L1 Trigger ID (L1ID) — from a given set of input links and combine them with the corresponding TTC information into an instance of the **swrod::ROBFragment** class.

This class provides a _serialize()_ function, which can be used to convert a swrod::ROBFragment object into a series of contiguous memory chunks. These chunks store the content of the ROB fragment, formatted according to the [ATLAS Event Format specification](https://cds.cern.ch/record/683741). The structure of an ATLAS-compliant ROB fragment is shown in the following table.

 Field       | Description
 :--------   | --------
 ROB Header  | Contains the event formatting information required to decode the ROB fragment.
 ROD Header  | Contains the event formatting information required to decode the detector specific data payload (ROD Data).
 ROD Data    | Contains the infromation received from the specific portion of the detector readout. Formatting is detector specific and may also depend on the fragment-building algorithm implementation.
 ROD Trailer | Contains detector specific information that can be altered by the SW ROD custom processing.

The contents of the ROB and ROD headers and trailer are defined by the ATLAS Event Format specification and are independent of the fragment-building algorithm implementation. The _ROD Data_ section of the fragment consists of aggregated data chunks received from the detector Front-End electronics, which use a detector-specific data format internally. The method used to aggregate these data chunks depends on the algorithm implementation.

The **swrod** package provides two fragment building algorithms that can be used to handle data received from FELIX:

 * **GBT mode algorithm**: This algorithm aggregates data chunks from all E-links associated with a given **SwRodDataChannel** object into a single _ROD Data_ block, aligning them using their L1IDs. It takes at most one data chunk from a given E-link for each ROB fragment. Receiving more than one data chunk in a row with the same L1ID from the same E-link is considered an error. Additionally, the algorithm expects each individual data chunk to have a size that is a multiple of 4 bytes. If this condition is not met, padding zeros are added at the end of the chunk to ensure 4-byte alignment.
 * **FULL mode algorithm**: This algorithm treats each data chunk from any E-link associated with the given **SwRodDataChannel** as a fully built ROD Data block, which may optionally include _ROD Header_ and _ROD Trailer_ elements. Like the GBT mode, it expects each incoming data chunk to be a multiple of 4 bytes in size. If this condition is not met, padding zeros are added at the end of the chunk to ensure 4-byte alignment.

Both the GBT and FULL mode algorithms can operate in either TTC-driven or data-driven mode. In data-driven mode, no Level-1 Accept (L1A) packets are received. The mode of operation is determined by the state of the L1AHandler relationships in the **SwRodConfiguration** and **SwRodModule** configuration objects. If both relationships are empty, the event builders do not subscribe to L1A messages and run in data-driven mode. Otherwise, they subscribe to the TTC E-Link to receive L1 Accept messages and use them for fragment building.

Additional fragment-building algorithms can be implemented and integrated into SW ROD via its plugin mechanism.

### SwRodFragmentBuilder configuration class

This is an abstract class that defines several parameters that are common for any fragment building algorithm implementation. These parameters are:
 * **BuildersNumber**: The number of dedicated threads, which are notified when a new ROB fragment data payload is ready and take care of creating a new instance of the **swrod::ROBFragment** class for this data and passing it to the ROB Fragment Consumers. These threads are used to disentangle fragment builders from fragment consumers and reduce a possible impact of slow consumers on fragment building performance. If **BuildersNumber** number is set to zero, then no building threads are used, in which case one of the fragment builder's working threads will execute the above procedure.
 * **DropCorruptedPackets**: This parameter defines what to do with data chunks that cannot be unanimously attributed to any ROB fragment due to containing corrupt data or arriving too late. If this parameter is set to 1 then such data chunks will be discarded. Otherwise, the chunks will be assigned to the currently being built ROB fragments. In such a case the error bits, that explain the origin of the error, will be set to the **swrod_status** byte of the chunk's local header as well as to status word of the ROB fragment header.
 * **FlushBufferAtStop**: Defines fragment builder behavior during Stop-of-Run procedure. If set to 1, the algorithm stops data processing immediately upon receiving SoR command. The data which were present in the internal buffers are flushed. If set to 0, the algorithm keeps processing data from its internal buffers until they get empty.
 * **L1AWaitTimeout**: Building a ROB fragment requires information from the corresponding L1 Accept packet. The timeout defines the maximum time in milliseconds to wait for L1A packet to arrive. If the required L1A packet does not arrive within this timeout the ROB fragment is considered as fully built but it will miss a proper Trigger Type information in the ROB header, where the corresponding attribute will be set to zero.
 * **ReadyQueueSize**: The size of the queue that is used to hold references to completely aggregated data blocks. This queue is used by the building threads that are defined via **BuildersNumber** parameters. The building threads take the references from this queue and use them to create new instances of the **swrod::ROBFragment** class. If **BuildersNumber** is set to zero, this parameter is ignored as no queue will be used in this case.
 * **ResynchTimeout**: This value defines time in milliseconds to wait for building the ROB fragment that corresponds to the last L1ID produced before the Trigger was put on hold. This timeout is used for the stopless recovery procedure to make sure that the fragment builder will be properly synchronized with the rest of the read-out system when the Trigger is resumed. If the given ROB fragment is not built within this timeout, the stopless recovery procedure will continue but its result will not be guaranteed.
  * **PacketDumpPath**: The name of a directory to store files with dumps of corrupted packets. A corrupted packet will be dumped either if L1 ID cannot be reliable extracted from it or the **DropCorruptedPackets** parameter is set to true.
  * **PacketDumpLimit**: The maximum number of packets to dump per run.
  * **LinkLoggingLimit**: The maximum number of data corruption incidents reported for a single E-Link. When this limit is reached further incidents will not be reported.

### GBT Fragment Building Algorithm

The _ROD Data_ element produced by this algorithm is split into several contiguous memory blocks, with each block containing copies of data packets received from a subset of the E-Links associated with the given ROB in the SW ROD configuration. In most cases, the number of blocks equals the number of data-receiving threads defined by the **WorkersNumber** attribute of the corresponding **SwRodModule** configuration object. However, the number of blocks may be greater if the default memory page size is insufficient to accommodate data from all input E-Links. In such cases, additional memory blocks will be automatically allocated by the fragment builder.

Each memory block contains a sequence of data packets received from the associated E-Links, with each packet preceded by a 64-bit header structured as follows:

 * **size**: 16-bit value that contains a total size (in 4-byte words) of the data packet including the size of the header itself.
 * **felix_status**: 8-bit status of the data packet provided by FELIX.
 * **swrod_status**: 8-bit status of the data packet assigned by the fragment building algorithm. This status may contain any combination of the following flags:
    * **swrod::GBTChunk::Status::Ok (0)**: no errors detected for this packet.
    * **swrod::GBTChunk::Status::Corrupt (1)**: custom TTC information extraction has thrown exception for this packet.
    * **swrod::GBTChunk::Status::CRCError (2)**: custom data integrity checking function has returned false for this packet.
    * **swrod::GBTChunk::Status::L1IdMismatch (4)**: the packet's L1 ID does not match L1 ID from the corresponding L1A packet.
    * **swrod::GBTChunk::Status::BCIdMismatch (8)**: the packet's BC ID does not match BC ID from the corresponding L1A packet.
 * **link_id**: 32-bit detector resource ID that identifies the origin of this data packet.

> **Note:** The _link_id_ field contains **DetectorResourceId** value, which corresponds to the FELIX E-Link ID as defined by the respective instance of the **SwRodInputLink** configuration class.

#### SwRodGBTModeBuilder configuration class

This OKS configuration class inherits from the **SwRodFragmentBuilder** and adds a few configuration parameters that are specific for the FULL mode algorithm, namely:
 * **BufferSize**: defines the maximum size of the main aggregation buffer in terms of the number of ROB fragments. This buffer size determines how many fragments can be built simultaneously. The parameter also indirectly affects the data input timeout, which is the time to wait before terminating the aggregation of a ROB fragment that is still missing data chunks from one or more input links.
The timeout value can be explicitly set in the SW ROD configuration using the **DataReceivingTimeout**. However, incomplete fragments may still be produced by the GBT algorithms if the aggregation buffer size is insufficient. This can occur when the **BufferSize**, divided by the current input data rate, is smaller than the **DataReceivingTimeout** value. In such cases, the effective timeout (in milliseconds) can be calculated using the following formula:

`EffectiveTimeout = min(DataReceivingTimeout, BufferSize / InputRate(kHz))`

 * **DataReceivingTimeout**: Defines a timeout in milliseconds for ROB fragment data aggregation. If the specified number of milliseconds elapses after receiving the first data chunk for a particular ROB fragment, that fragment is considered built and will be passed to the fragment consumers, even if it does not contain data chunks from all the E-links associated with the given ROB. By default, this attribute is set to zero, which disables the time-based timeout. In this case, the effective timeout will be determined by the buffer size, as explained in the previous paragraph.
 * **L1AInitiatesTimeout**: If this value is set to true, the data receiving timeout will be activated when the corresponding L1A packet is received. Otherwise, the timeout will be triggered by the first data packet with the specific L1ID.
* **MinimumBufferSize**: Defines the minimum size of the main aggregation buffer in terms of the number of ROB fragments. The buffer will always attempt to shrink to this value (but not below it) whenever the number of concurrently built fragments decreases.
 * **RecoveryDepth**: If an incoming data chunk contains L1ID and BCID values that do not match the algorithm's expectations, the algorithm will check if this mismatch can be explained by assuming that a number of previous data packets from the same E-link have been missed. To verify this hypothesis, the algorithm will attempt to match the packet's L1ID and BCID to the corresponding values in the current L1 Accept packets. The RecoveryDepth parameter defines the maximum number of L1A packets to be checked during this procedure, as this is the only reliable way to terminate the recovery if the error was caused by data corruption (e.g., a bit flip).

The **MaxMessageSize** attribute of the base **SwRodFragmentBuilder** class class has a specific purpose in this algorithm: it defines the maximum size, in bytes, for a single data packet that may arrive from an individual input link. Any data packet exceeding this size will be discarded. The algorithm also uses this value to calculate the size of the memory blocks that will be used for ROB fragments. This size will be set to the maximum of the **MaxMessageSize** value and the **PageSize** value of the **MemoryPool** object associated with the given SwRodRob instance. If the **SwRodRob**'s _MemoryConfiguration_ relationship is empty, the **MemoryPool** object associated with the **SwRodApplication** object will be used instead.

#### Memory Management Configuration
This section provides an example that demonstrates how to choose the optimal values of the **SwRodGBTModeBuilder::MaxMessageSize** and **MemoryPool::PageSize** parameters to ensure the best performance and minimize memory footprint of GBT mode algorithm.

##### SwRodGBTModeBuilder::MaxMessageSize
As explained in the previous paragraph, the primary purpose of this parameter is to define the maximum size of an individual data packet (a packet received from a single E-Link) that will be accepted by the algorithm. For example, if the maximum number of hits a single data packet may contain and the size of each hit are known, the value for this parameter can be easily calculated by multiplying these two values and adding the size of the fixed portion of the data packet format (e.g., L1ID, BCID, etc.).

For instance, if the maximum number of hits a single data packet can contain is 500, the hit size is 3 bytes, and the size of the fixed portion of the data packet is 20 bytes, then this parameter should be set to:

`500*3 + 20 = 1520`

##### MemoryPool::PageSize
This parameter should be used to minimize the memory footprint of the SW ROD. The optimal value of this parameter can be calculated by multiplying the following three values:
 * The size of a single hit
 * The maximum number of hits in the bulk of the data packets
 * The number of input E-Links for the current ROB

For example, if it is known that 99.9% of data packets contain no more than 5 hits and the number of E-Links used to provide data for the current ROB is 150, then the **PageSize** parameter should be set to the following value:

`(5 * 3 + 20) * 150 = 5250`

Here, 20 bytes represents the size of the fixed portion of a data packet. With this configuration, the majority of the ROB fragments produced by the current algorithm will fit into a single memory block. Rare fragments, which contain unusually large data packets, will be automatically split into multiple data blocks.

> **Note**: If the **MaxMessageSize** exceeds the **PageSize**, the former will override the latter, setting the page size to the greater value. This ensures that a single data packet will never need to be split across multiple memory pages. With this approach, this situation is avoided, as any data packet larger than the **PageSize** will also exceed the **MaxMessageSize** and therefore be discarded.

#### Error Handling

The default GBT fragment-building algorithm implements error handling as described by the [SW ROD Error Use Cases](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/SWRodInputErrors) page. The algorithm may produce incomplete ROB fragments, i.e. fragments that are missing data chunks from one or several E-Links. This can occur if data from these E-Links did not arrive within the defined timeout, as specified in the algorithm configuration, or if the data was not present in the corresponding E-Link data streams.

### FULL Mode Fragment Building Algorithm

This algorithm receives data packets from a set of E-Links defined by the corresponding SW ROD configuration. It assumes that each data packet contains fully built _ROD Data_ element and may optionally also contain the _ROD Header_ and _ROD Trailer_ elements. The presence of the latter is controlled by the **RODHeaderPresent** attribute of the **SwRodFullModeBuilder** configuration object. The algorithm combines these data packets into objects of the **swrod::ROBFragment** class. If **RODHeaderPresent** attribute is set to true the algorithm performs a few consistency checks of the ROD fragment header and sets the error bits in the ROB header status word if any of these checks fail. Complete information about the error bits that may appear in the ROB header status words can be found in the [following page](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/ROBFragmentHeaderStatusWords).

The following attributes of the base **SwRodFragmentBuilder** class are specifically relevant for this algorithm:
 * **DropCorruptedPackets**: This parameter is considered only if the **RODHeaderPresent** parameter is set to **1**. In this case, the algorithm will discard any fragment that contains errors in its header or is too short to contain complete _ROD Header_ and _ROD Trailer_ elements.
 * **MaxMessageSize**: The maximum size (in bytes) of a single data packet that may arrive from an individual input link. A data packet exceeding this size will be truncated to **MaxMessageSize** bytes. If the **MaxMessageSize** value is greater than the **PageSize** value of the **MemoryPool** object associated with the given **SwRodRob** instance, data packets larger than the **PageSize** will be split into multiple data blocks. If the **SwRodRob**'s _MemoryConfiguration_ relationship is empty, the **MemoryPool** object associated with the **SwRodApplication** object will be used.

#### SwRodFullModeBuilder configuration class

This OKS configuration class inherits from the **SwRodFragmentBuilder** and adds the **RODHeaderPresent** parameter. If this parameter is set to **1**, the algorithm assumes that each incoming data packet already contains the **ROD header** and **ROD trailer** elements, and thus will not add them. Otherwise, the algorithm will generate the **ROD header** and **ROD trailer** itself.

#### Memory Management Configuration

This section contains an example that demonstrates how to choose the optimal values of the **SwRodGBTModeBuilder::MaxMessageSize** and **MemoryPool::PageSize** parameters to assure the best performance and minimize memory footprint of FULL mode fragment-building algorithm.

##### SwRodFullModeBuilder::MaxMessageSize

Unlike the GBT mode algorithm the FULL mode algorithm never discards incoming data packets, but may truncate them if they are excessively large. This is where the **MaxMessageSize** parameter comes into play. It defines the maximum size of an individual data packet that the algorithm will accept without truncation. If a data packet exceeds the **MaxMessageSize** value, the algorithm will truncate it to that size.

To calculate the appropriate value for this parameter, one can multiply the maximum number of hits a single data packet may contain by the size of each hit and then add the size of the fixed portion of the data packet format (e.g., ROD Header and ROD Trailer).

For example, if the maximum number of hits is 500 and the hit size is 3 bytes and the fixed portion of a data packet is equal to 50 bytes, then the **MaxMessageSize** parameter should be set to the following value:

`500*3 + 50 = 1550`

##### MemoryPool::PageSize
This parameter is used to minimize the memory footprint of the SW ROD application. The optimal value of this parameter can be calculated by multiplying the size of a single hit by the maximum number of hits that the majority of data packets may contain, and then adding the size of the fixed portion of the data packet format.

For example, if it is known that 99.9% of data packets contain no more than 100 hits, and the size of the fixed portion of a data packet is 20 bytes, then this parameter should be set to:

`100 * 5 + 20 = 520`

The goal is for the majority of ROB fragments produced by the algorithm to fit into a single memory block. Rare data packets that are larger than the **PageSize** will automatically be split into multiple data blocks.

> **Note:** The **PageSize** value can be set to be equal to or greater than the **MaxMessageSize**, ensuring that every fragment of the given ROB will always consist of a single memory block.

## Configuring SW ROD Application
A SW ROD application must be configured using OKS configuration service. For convenience all OKS classes that can be used for this purpose have their names started with **SwRod** prefix. These classes are defined in the **daq/schema/swrod.schema.xml** OKS schema file that must be included by any SW ROD OKS configuration. A fully functional example of a SW ROD configuration can be found in the
[data/SwRodSegment.data.xml](data/SwRodSegment.data.xml) file located in the **swrod** package.

The SW ROD configuration schema enables splitting a SW ROD application configuration across multiple files, making a clear distinction between the detector-specific and TDAQ-specific parts, thus simplifying maintenance. The following diagram illustrates a recommended approach for handling the SW ROD configuration. The green boxes represent classes to be instantiated in the detector-specific portion of the configuration, while the yellow boxes denote the classes used for creating the TDAQ portion. Further details will be provided in the following sections.

![](doc/configuration.png "SW ROD configuration")
<table height=0><tr><td>
@image latex doc/configuration.png "SW ROD configuration" width=400px
</td></tr></table>

> **Note:** **SwRodApplication**, **SwRodModule** and **SwRodRob** classes inherit from the legacy read-out configuration classes to make the new SW ROD-based readout configuration compatible with the legacy ROS-based one.

### Detector Specific Configuration

Detector-specific portion of a SW ROD configuration is expected to contain the objects of the following three classes:
 * **SwRodInputLink**: The objects of this class define a set of E-Links for receiving data.
 * **SwRodDataChannel**: These objects define a mapping of E-Links to ROBs.
 * **SwRodCustomProcessingLib**: This class defines configuration of a detector specific custom processing plugin.

#### SwRodInputLink class

This class is used to describe a set of input E-Links for a particular detector and implements the mapping of FELIX-specific E-Link IDs to detector specific Resource IDs. This class has three attributes:
 * **FelixId**: The ID of this link as defined by the FELIX system. This ID must be unique within ATLAS.
 * **DetectorResourceId**: The ID of the detector read-out element connected to this FELIX link. This ID must be unique for a given sub-detector.
 * **DetectorResourceName**: A human-readable name for the detector read-out element.

It is recommended to place all instances of this class in a specific OKS configuration file (or a set of files), which then can be effectively shared by SW ROD configuration segments.

#### SwRodDataChannel class

An object of this class defines a set of input links for a given ATLAS data channel (ROD) as well as a custom processing plugin that has to be used for this channel. It has the following relationships:
 * **Contains**: Inherited from **ResourceSetAND** class, this relationship must contain references to the objects of the **SwRodInputLink** class that represent the corresponding E-Links.
 * **CustomLib**: A reference to an instance of the **SwRodCustomProcessingLib** class.

This class also includes several attributes that influence the procedure manipulating ECR counters maintained by the FELIX cards, such as:
 * **TTCControllerName**: Defines the name of the segment controller used to determine whether the SW ROD application must send the ECR reset command to the FELIX cards when a new run starts. By default, this is set to _"RootController"_. When the SW ROD application receives the _PrepareForRun_ command, it checks the controller's state. If the controller is not yet in the _RUNNING_ state (as when a new run is starting), the SW ROD application sends the ECR reset command. If the value of this parameter is empty, the command is not sent.
 * **UpdateECRCounter**: If set to **1**, the SW ROD application updates the ECR counters of the FELIX cards it is subscribed to with the last known ECR value during the the _TTC Restart_, _Stopless Recovery_ and _Resynchronise_ procedures.

It is recommended that all instances of this class be placed in a separate OKS configuration file, which should also include files defining the objects of the **SwRodInputLink** class.

#### SwRodCustomProcessingLib class

This class should be used for configuring custom detector plugins for the SW ROD. It has the following attributes:
 * **LibraryName**: Specifies the name of the shared library that implements the custom plugin.
 * **TrigInfoExtractor**: The name of the mandatory function used to extract trigger information from the incoming data.
 * **DataIntegrityChecker**: The name of the optional function responsible for performing data integrity checks. If the plugin does not provide this function, the attribute should be left empty.
 * **ProcessorFactory**: The name of the optional custom processor factory function. This function creates custom processors that handle the data as it flows through the system. If the plugin does not provide a processor factory, this attribute should be left empty.

Each instance of the **SwRodDataChannel** class, which represents a data channel for the SW ROD application, must be linked to an appropriate instance of the **SwRodCustomProcessingLib** class. This linkage ensures that the necessary custom processing logic is applied to the data channel's data, as defined by the custom processing library.

### TDAQ Specific Configuration

This portion of the SW ROD configuration defines:
 * Computers where the SW ROD applications will be running
 * The mapping of the SW ROD data channels (RODs) to the respective SW ROD applications
 * The HLT request handling and event monitoring parameters

#### SwRodApplication Class

An instance of the **SwRodApplication** class serves as the entry point to the SW ROD configuration, fulfilling several roles:
 * Defines the standard Run Control application parameters for the _swrod_application_ process.
 * Points to an instance of the **SwRodConfiguration** class, which specifies the TDAQ-specific portion of the SW ROD configuration.
 * Contains a set of **SwRodRob** objects that define the standard ATLAS ROB-to-ROD mapping. RODs are represented by the corresponding instances of the **SwRodDataChannel** class, as defined by the detector-specific portion of the SW ROD configuration.

#### SwRodConfiguration Class

The **SwRodConfiguration** class declares the following parameters:
 * **Plugins**: A list of **SwRodPluginLib** objects, which reference shared libraries that provide implementation of the core SW ROD interfaces. At a minimum, this list must contain a reference to the  **libswrod_core_impl.so** library, which provides default implementations of these interfaces.
 * **L1AHandler**: A reference to an instance of a class that inherits **SwRodL1AInputHandler** interface. By default, this relationship should point to an instance of the **SwRodDefaultL1AHandler** class, which provides the default implementation of the L1 accept message handler.
 * **Consumers**: A list of objects implementing the **SwRodFragmentConsumer** interface. Consumers from this list will receive all fragments for all ROBs produced by the current SW ROD application. Note that the order of objects in this list matters. ROB fragments will be passed to the consumers in the same order as they are linked to the **SwRodConfiguration** instance. For example, if the **SwRodEventSampler** consumer precedes the **SwRodCustomProcessor**, any monitoring task connected to the current SW ROD application will receive ROB fragments without custom processing applied.
 * **InputMethod**: A reference to an object implementing **SwRodInputMethod** interface. For getting data from FELIX, one should reference an instance of the **SwRodFelixInput** class.

![](doc/swrod-configuration.png "Top level configuration of a SW ROD application")
<table height=0><tr><td>
@image latex doc/swrod-configuration.png "Top level configuration of a SW ROD application" width=400px
</td></tr></table>

#### SwRodFragmentConsumer interface implementations

The **SwRodFragmentConsumer** is an abstract base class for any resource that processes fully built ROB fragments. It declares three attributes:
 * **Type**: A string ID representing the specific fragment builder type used to create an instance of the respective consumer at runtime. Each subclass of SwRodFragmentConsumer must provide a unique type name for its instantiation.
 * **WorkersNumber**: Specifies the number of worker threads for this consumer.
 * **CPU**: Defines the CPU affinity for the worker threads of this consumer. It is a string parameter that contains CPU core numbers separated by commas and may include ranges. For example: `0,5,7,9-11`.

SW ROD provides several implementations of the **SwRodFragmentConsumer** interface, each serving a different purpose and configurable through corresponding OKS classes:
 * **SwRodFileWriter**: This implementation writes data produced by the SW ROD application to the standard ATLAS raw data file using the ATLAS event format.
It can be used for individual ROBs or for the whole SW ROD application. When used at the application level, it combines fragments from different ROBs with the same L1ID into a single ATLAS event.
 * **SwRodHLTRequestHandler**: Implements the standard High-Level Trigger (HLT) to Readout Subsystem (ROS) communication protocol. From the perspective of the HLT, a SW ROD application is indistinguishable from a ROS application.
 * **SwRodEventSampler**: This implementation creates an Event Sampler for the SW ROD application. It collates fragments from all ROBs handled by the SW ROD application into a single ATLAS event based on their L1IDs and provides these events to monitoring applications through the TDAQ Event Monitoring interface.
Monitoring applications can connect to the Event Sampler using the  _"SWROD"_ string as sampler type and the ID of the SW ROD application as sampler name.
 * **SwRodDebugStream**: This is an alternative Event Sampler implementation designed to sample fragments that contain non-zero status words in their headers. When an instance of this configuration class is connected to a **SwRodConfiguration** object, it creates an Event Sampler of type _"SWROD"_ with the name formatted as <em>"\<SW ROD Application ID>-Debug"</em>. This sampler forwards to the connected monitoring application individual fragments belonging to any ROB handled by the given SW ROD that have a non-zero status in their ROB headers. Unlike the default Event Sampler implementation, this one does not align fragments from different ROBs into a single event. Instead, each fragment is sent individually as a separate event. Alternatively, when the configuration class is connected to a **SwRodRob** instance, it creates an Event Sampler of the _"SWROD"_ type named <em>"\<ROB ID>-Debug"</em>. In this case, the sampler will send only the fragments of that specific ROB which contain non-zero status words in their headers.
 * **SwRodCustomProcessor**: Applies detector-specific custom processing to fully built ROB fragments.

Fragment consumers in SW ROD can be attached at two levels:
 * **Per ROB**: This is done via the **SwRodRob::Consumers** relationship, where consumers are specific to individual ROBs. This allows for fragment handling at a granular level, with each ROB having its own set of consumers that process its fragments.
 * **Per Application**: This is done via the **SwRodConfiguration::Consumers** relationship, where consumers are shared across the entire SW ROD application.
This is useful when you need to process all fragments produced by the application in a unified way.

While both approaches are supported, there are certain implementation-specific limitations that need to be considered when configuring specific consumers. These limitations may include constraints on how consumers handle data, how fragments are passed to them, and potential conflicts when attaching multiple consumers at different levels. The following table outlines these limitations.

 SwRodConsumer        	| SwRodRob 	| SwRodConfiguration
 :-------------   		| :------:  | :-----------:
 SwRodFileWriter 		| Yes		| Yes
 SwRodHLTRequestHandler | Yes 		| No
 SwRodEventSampler	    | No	    | Yes
 SwRodDebugStream	    | Yes	    | Yes
 SwRodCustomProcessor   | Yes 		| No

#### SwRodInputMethod interface implementations

The **SwRodInputMethod** is an abstract class that defines interface for getting data into SW ROD. SW ROD provides several implementations of this interface, which can be configured using the corresponding OKS schema class:
 * **SwRodBufferInput** can be used to read data directly from the DMA buffer filled by the FELIX card. For that the corresponding SW ROD application must be running on the same computer where the FELIX card is installed. This input class has the following configuration parameters:
    * **DMABufferID**: A numeric ID of the DMA buffer to read data from. The tens digit of this number specifies the FELIX device ID, while the ones digit specifies the DMA buffer ID within that device.
    * **DMABufferSize** : Size of the DMA buffer in 1KB blocks.
    * **DMABufferNumaNode**: ID of the NUMA node where the buffer memory should be allocated. For optimal performance, this should match the NUMA node of the PCI slot hosting the FELIX card.
 * **SwRodFelixInput** can be used to receive data from **felix-star** via the network. It is implemented using the _FelixClient_ interface provided by the FELIX software release. This class has a few configuration attributes which can be used to configure _FelixClient_ communication interface, including:
    * **DataNetwork**: The name or IP address of the network that shall be used for receiving data
    * **FelixBusGroupName**: The FELIX Bus group name
    * **FelixBusDirectory**: The name of the file system directory which is used by the FELIX Bus for storing its internal data.
    * **FelixBusInterface**: This is the legacy attributed that was used with the previous FELIX Bus implementation and must no longer be used.
    * **FelixBusTimeout**: The timeout (in milliseconds) for link resolution via FELIX bus.
 * **SwRodInternalDataGenerator** is an in-memory data generator used for testing.

#### SwRodRob Class

Each instance of the **SwRodRob** class provides configuration for a specific ROB or in another words defines portion of the detector readout from which data must be combined to a single fragment (ROB fragment). This class has the following parameters:
 * **Id**: The ROB identifier, which must be unique across all SW ROD and ROS components. This ID is used by HLT to request the corresponding ROB fragments.
 * **FragmentBuilder**: A reference to an instance of a class that inherits **SwRodFragmentBuilder** interface. This object provides configuration for the data aggregation algorithm, which is used to build fragments for the given ROB.
 * **Consumers**: A list of objects implementing **SwRodFragmentConsumer** interface. Consumers from this list will receive all fragments that are built for the given ROB.
 * **Contains**: This relationship is inherited from the **ResourceSetAND** class and is used to reference an instance of the **SwRodDataChannel** class. This relationship provides the sole link between the detector and the TDAQ-specific portions of the SW ROD application configuration.

> **Note:** For compatibility with the legacy read-out system configuration **Contains** is a multi-value relationship that potentially could reference more than one **Resource** object. However, for a valid SW ROD configuration this relationship must point to exactly one unique **SwRodDataChannel** instance.

#### SwRodModule Class

This class provides data receiving configuration for a given set of **SwRodRob** objects, which are referenced via its **Contains** relationship. This class has the following attributes:
 * **WorkersNumber**: The number of threads for receiving input data.
 * **CPU**: A string that defines CPU affinity of the data receiving threads. A value may contain CPU numbers separated by commas and may optionally include ranges. For example: 0,5,7,9-11. If this string is empty, then no affinity will be assigned.
 * **L1AHandler**: If this relationship is not empty then a dedicated instance of L1 Accept receiver will be created to be used exclusively by the ROBs that belong to this **SwRodModule**. If this relationship is empty, the ROBs will use the global L1 Accept receiver that is created with respect to the configuration object referenced by the **SwRodConfiguration**. If the **L1AHandler** relationship of this object is empty as well, the fragment building algorithms of the ROBs belonging to the current **SwRodModule** will operate in data-driven mode.
 * **Contains**: This relationship is inherited from the **ResourceSetAND** class and is used to reference objects of the **SwRodRob** class, which will share input parameters defined by the **SwRodModule** instance.

## Customizing SW ROD application

SW ROD declares three abstract interfaces for its main components:
 * **DataInput**: This interface can be used for receiving input data from a given source, e.g. from FELIX.
 * **ROBFragmentBuilder**: This interface can be used to implement an algorithm of building ROB fragments from the data received via the **DataInput** interface.
 * **ROBFragmentConsumer**: This interface can used for implementing specific processing of fully built ROB fragments.

Default implementations of these interfaces are provided by the **libswrod_core_impl.so** library and can be used via the corresponding classes in the SW ROD configuration. SW ROD also provides a way to integrate custom implementations of these interfaces into the standard SW ROD application.

### Making a Custom Interface Implementation

The following example demonstrates a simple implementation of the **ROBFragmentConsumer** interface, which counts the incoming ROB fragments.

~~~cpp
class ROBFragmentCounter : public swrod::ROBFragmentConsumer {
public:
    ROBFragmentCounter(const boost::property_tree::ptree & config, const swrod::Core & core)
     : m_counter(0),
       m_ROB_id(-1) {
       m_output_frequency = config.get<uint32_t>("OutputFrequency");
       if (config.count("RobConfig")) {
           m_ROB_id = config.get<uint32_t>("RobConfig.Id");
       }
    }

    void insertROBFragment(const std::shared_ptr<swrod::ROBFragment> & fragment) override {
       if ((++m_counter % m_output_frequency) == 0) {
           std::cout << m_counter << " fragments have been built for ROB " << m_ROB_id << std::endl;
       };
       forwardROBFragment(fragment);
    }

    void runStarted(const RunParams & run_params) {
       m_counter = 0;
    }
private:
    uint32_t m_output_frequency;
    uint32_t m_ROB_id;
    uint64_t m_counter;
};
~~~

An instance of this consumer can be used at the level of an individual ROB as well as at the level of the entire SW ROD application. Each time a new ROB fragment is produced, it is passed to the instance of the **ROBFragmentCounter** class via the _insertROBFragment()_ function. In this example the implementation of this function increments the fragment counter and then forwards the given ROB fragment to the other consumers by calling the _forwardROBFragment()_ function. Additionally, every **m_output_frequency** fragments the function prints the fragment counter to the standard output. The value of the **m_output_frequency** parameter is taken from the OKS configuration. The following section explains how that is implemented.

### Configuring Custom Interface Implementation

The **ROBFragmentCounter** class constructor takes a reference to the **boost::property_tree::ptree** instance that represents parameters taken from the corresponding OKS class. For the new consumer type a new OKS class that inherits from the **SwRodFragmentConsumer** must be declared. This can be done using the following procedure:
 * Run the OKS schema editor and create a new OKS schema file
 * Add include of the **daq/schema/swrod.schema.xml** OKS schema file into the new file
 * Create a new class (in this case **ROBFragmentCounter**) inheriting it from the **SwRodFragmentConsumer** class
 * Add a new attribute(s) (in this case the attributed called **OutputFrequency**) to the new class
 * Save the new schema file

The new schema file must be included by the SW ROD configuration. After that one can create a new instance of the **ROBFragmentCounter** class and add it either to a **SwRodRob** or to a **SwRodConfiguration** instances depending on whether counting has to be done at the level of an individual ROB or for the entire SW ROD application.

> **Note**: **ROBFragmentCounter** constructor implementation uses the _"RobConfig"_ configuration object that is obtained by calling _config.get_child("RobConfig")_ function with the given **boost::property_tree::ptree** instance. The _"RobConfig"_ parameter is available only if consumer configuration object was linked to an instance of the **SwRodRob** class via its _Contains_ relationship. In this case this parameter will contain the corresponding **SwRodRob** configuration. For an instance of the consumer that is attached to the **SwRodConfiguration** object, the _"RobConfig"_ configuration parameter will not be set and an attempt to call the _config.get_child("RobConfig")_ function result in an exception.

### Registering Custom Interface Implementation with the SW ROD

Finally, the SW ROD application must be made aware of the new interface implementation in order to be able to use it at runtime. To achieve this the corresponding interface implementation class must be registered with the **swrod::Core** singleton, as shown in the following example.

~~~cpp
using namespace swrod;

namespace {
    Factory<ROBFragmentConsumer>::Registrator reg_1_(
            "ROBFragmentCounter",
            [](const boost::property_tree::ptree& config, const Core& core) {
                return std::make_shared<ROBFragmentCounter>(config, core);
            });
}
~~~

This code creates a new factory object that will be used for creating new instances of the **ROBFragmentCounter** class. The factory will be registered with the _"ROBFragmentCounter"_ name. This name will be used in the OKS configuration as described in the next section. Note that the base class of the new component (**ROBFragmentConsumer**) must be used as template parameter of the **Factory** class.

The code must be compiled and linked together with the **ROBFragmentCounter** class implementation into a shared library that will be dynamically loaded by SW ROD application. Let's assume that such a library is called **libswrod_custom_test.so**. To make this library known to the SW ROD application a new instance of the **SwRodPluginLib** class must be created in the corresponding OKS configuration and the shared library name has to be set to its **LibraryName** attribute. One can either use a full path-name of the shared library or use a short file-name and add the library location to the _LD_LIBRARY_PATH_ environment variable. Finally, the new instance of the **SwRodPluginLib** class must be linked with the **SwRodConfiguration** object via the _Plugins_ relationship.

## Testing SW ROD Custom Processing library

A custom implementation of the **DataInput** interface can be used to validate detector-specific custom processing plugins. This chapter explains how this can be done.

### Implementing internal data generator for SW ROD

The simplest way of providing custom input to SW ROD is to implement internal data generator that produces data with desired formatting in memory of the SW ROD application. The **swrod** package contains an example of such generator in **test/core/InternalDataGenerator.h(cpp)** files. One can customize internal data generation by declaring a new class that inherits from the **swrod::test::InternalDataGenerator** and overrides the _generatePacket(InputLinkId link, uint32_t l1id, uint16_t bcid)_ virtual function. This function is called for every new packet to be produced and is expected to pass the packet to the _dataReceived(InputLinkId link, const uint8_t * data, uint32_t size, uint8_t status)_ function of the **swrod::DataInput** interface, as shown in the following example.

~~~cpp
 void MyDataGenerator::generatePacket(InputLinkId link, uint32_t l1id, uint16_t bcid) {
    // For efficiency m_packet memory block had been preallocated in the constructor
    // Here we just calculate the size of the new packet.
    // It must not exceed the size of the m_packet memory block
    uint32_t new_packet_size = ...;

    // set TTC values to the appropriate places of the new packet, for example
    memcpy(m_packet+2, &l1id, sizeof(l1id));
    memcpy(m_packet+6, &bcid, sizeof(bcid));

    dataReceived(link, m_packet, new_packet_size, 0);
}
~~~

Note that if a custom implementation produces packets of fixed size, it can calculate the packet size only once in the class constructor. A custom implementation that needs to generate packets of varying size must calculate a new packet size each time a new packet is produced. Finally, the new packet must be passed to the _dataReceived(...)_ function, which in turn will pass it to the SW ROD fragment builder.

The **swrod::test::InternalDataGenerator** class also provides another virtual function called _beforeStart()_. This function is called each time a new run is about to be started and can be used to reset the internal counters of the custom data generator.

The new data generator must be advertised to the SW ROD by creating and registering a new object factory, as shown in the following example.

~~~cpp
namespace {
    Factory<DataInput>::Registrator __reg__(
            "MyDataGenerator",
            [](const boost::property_tree::ptree& config, const Core& ) {
                return std::make_shared<MyDataGenerator>(config);
            });
}
~~~

Finally, the new generator class must be compiled into a shared library and the library name must be set to the **LibraryName** attribute of the new instance of the **SwRodPluginLib** object created in OKS configuration. This OKS object must be linked with the **SwRodConfiguration** via the _Plugins_ relationship. This will make the new input method implementation known to the SW ROD application.

In order to use the new generator a new instance of the **SwRodInternalDataGenerator** class must be created and its **Type** attribute must be set to the same _"MyDataGenerator"_ string, that was used for registering the corresponding class with the SW ROD plugins factory. Finally, this object has to be linked either with the  **SwRodConfiguration** or **SwRodModule** via the **InputMethod** relationship.

> **Note**: An internal data generator must be used in conjunction with **InternalL1AGenerator** class provided by the **swrod** package. The **InternalL1AGenerator** produces L1A packets which are used as seeds for data packets generation.
```

### `doc/RELEASE_NOTES.md`  
*Local path: `repo/swrod/doc/RELEASE_NOTES.md`*

```markdown
# swrod

SW ROD supports now so called direct readout mode, which allows to read data directly from the FELIX cards without using the Netio protocol. This mode is implemented by the new **BufferInput** interface, which can be configured via the **SwRodBufferInput** OKS class. To receive data from the FELIX card the SW ROD application must be running on the same machine.

There are two variants of this interface: the standard and the zero copy one. One can control which variant to use via the Type attribute of the **SwRodBufferInput** OKS class. For the standard mode the default "BufferInput" value must be used, for zero copy the value must be changed to "ZeroCopyBufferInput". The latter can only be used in the FULL mode, which assumes that every data packet received from every e-link rpresents a fully built ROD fragment. The standard mode can be used in both FULL and GBT modes. For the descrition of the other configuration parameters of the **SwRodBufferInput** class see the updated User's Guide.

Receiving data from FELIX via Netio protocol is still supported via the **FelixClient** interface, which can be configured via the **SwRodFelixInput** OKS class.

## tdaq-12-00-00

### Memory Management

Memory management of the SW ROD fragment builders can now be configured via the **MemoryPool** OKS class, which in the previous releases used to be ignored. Each **SwRodApplication** object has been already linked with an instance of the **MemoryPool**, but in the new release it will be used to define the default configuration for all ROBs handled by the given SW ROD application. This configuration can be overridden for a particular ROB by linking another instance of the **MemoryPool** with the corresponding **SwRodRob** object. The meaning of the two **MemoryPool** attributes is the following:

* **PageSize** - default size of individual memory pages allocated by this memory pool. Note that this value can be overridden by fragment builder implementation, which is explained by the algorithm's description in the updated User's Guide.

* **NumberOfPages** - the number of pages that will be pre-allocated before a new run is started. The maximum number of pages that can be allocated by the memory pool is unlimited.

If one memory page is not large enough to hold the data of a particular ROB fragment the fragment builders will allocate extra pages. More information is given in the updated User's Guide.

Note that the _MaxMessageSize_ parameter of the **SwRodFragmentBuilder** class has now slightly different meaning with respect to the previous SW ROD versions. Now it truly means what its name implies, i.e. it defines the maximum size of a single data packet that will be accepted by the algorithm. Packets with the sizes exceeding this limit will be discarded. Packets of a smaller size are guaranteed to be added to the ROB fragment payload without truncation.

### Support of netio and netio-next

Starting from this release SW ROD doesn't support any more the legacy **netio** protocol and therefore cannot be used to receive data from the old **felix-core** systems. For receiving data from **felix-star** via the new **netio-next** protocol one must use the **FelixClient** interface, which can be configured via the **SwRodFelixInput** OKS class. The direct use of the **netio-next** API is also no longer supported. Because of this both the **SwRodNetioInput** and the **SwRodNetioNextInput** classes have been removed from the SW ROD OKS schema file.

## tdaq-10-00-00

### IS Information Update

Several new attributes have been added to the **ROBStatistics** IS information type:
* **enabled** is set to false when the corresponding ROB is stoplessly removed from the ongoing run, true otherwise.
* **latePackets** - per ROB counter of data packets that arrive to the SW ROD when the corresponding fragments have been already built due to the timeout. The same counter has been added to the **LinkStatistcis** IS class.

A new **gcDeletedFragments** attribute has been added to the **HLTRequestStatistics** IS class. This is a counter of ROB fragments which were removed by the garbage collector rather than by a normal Clear request.

If the **DF** IS server contains the IS objects published by the previous version of the SW ROD, they must be removed to release publication of the new objects. This can be done using the **is_rm** command, e.g.:

```
is_rm -p <partition name> -n DF -r "swrod.*"
```

### Configuration schema changes

* **EnableGarbageCollection** attribute has been added to the **SwRodHLTRequestHandler** class. If its value is set to 1 (default) then SW ROD will remove the oldest ROB fragments from the HLT buffer when the buffer gets full.

* **UnsubscribeDisabledLinks** attribute has been added to the **SwRodFragmentBuilder** class. If its value is set to 1 (default) then SW ROD will unsubscribe from the stoplessly removed input links, otherwise just mark them as disabled and discard all data received through them.

* **MaxReorder** attribute has been added to the **SwRodHLTRequestHandler** class. It defines the maximum size of latest L1 ID derandomising map, that is used to optimize HLT request handling.

* **DropCorruptedPackets** attribute has been moved from the **SwRodGBTModeBuilder** class to the **SwRodFragmentBuilder**. This way it was made available to the **SwRodFullModeBuilder** as well.

* Two attributes have been added to the **SwRodDataChannel** class.
    * **TTCControllerName** - defines the name of the closest TTC segment controller. Used to detect when _TTC Restart_ operation is ongoing. When SW ROD application is executing  _PrepareForRun_ Run Control transition it checks the state of the corresponding controller. If the controller is in the _RUNNING_ state then the SW ROD application assumes that it is just being restarted. In another case it is assumed that the _TTC Restart_ procedure is taking place. By default this parameter is set to the "RootController" string.
    * **UpdateECRCounter** - If this parameter is set to **true** the SW ROD application sets ECR counters of the FELIX cards it is subscribed to the last known ECR value during _TTC Restart_, _Stopless Recovery_ and _Resynchronise_ procedures.

* Three attributes have been added to the **SwRodFragmentBuilder** class.
    * **PacketDumpPath** - The name of a directory to store files with dumps of corrupted packets. A corrupted packet will be dumped either if L1 ID can not be reliable extracted from it or the **DropCorruptedPackets** parameter is set to true.
    * **PacketDumpLimit** - The maximum number of packets to dump per run.
    * **LinkLoggingLimit** - The maximum number of data corruption incidents reported for a single E-Link

* A new **DataReceivingTimeout** attribute has been added to the **SwRodGBTModeBuilder** class. It defines a timeout in milliseconds for ROB fragments building. If the given number of milliseconds is passed after receiving the first data chunk for a particular ROB fragment this fragment will be considered as built and will be passed to the fragment consumers even if it does not contain data chunks from all the E-links associated with the given ROB.

* A new **DeferProcessing** attribute has been added to the **SwRodCustomProcessor** class. If it is set to **true** the processing will be applied only when serialization of the ROB fragment is requested. This happens for example when the fragment is about to be written to a file or been sent over the network. This may be used to reduce computing resources for the fragments that require heavy processing but are rarely requested by the HLT. Default value of this attribute is **false**.

* A new **ProfileExecution** attribute has been added to the **SwRodCustomProcessor** class. If it is set to **true** the processor will keep a record of total time of the custom processing execution and will print it to the standard output when SW ROD is terminated. Default value is **false**.

### GBT Fragment Building Timeout

This version implements fragment building timeout for GBT fragment building algorithm. One can specify the timeout value via the new attribute of the **SwRodGBTModeBuilder** class called **DataReceivingTimeout**. This attribute contains a number of milliseconds to wait after receiving the first data chunk for a particular ROB fragment to consider this fragment as built even if not all data chunks have been received. By default this attribute is set to zero, which disables the timeout.

### Custom Plugin Test application

A new application that can be used for validation and profiling of a custom plugin has been added. The application is called **swrod_custom_plugin_test** and can be used in the following way:
  * For the first time it has to be given five parameters: a name of the data file to be used as data source, a name of the shared library that implements the plugin to be tested and the names of the three custom functions which this plugin implements. Optionally one can use _-o <json file name>_ option to save the new configuration to the given Json file.
  * If the Json configuration file has been produced the test application can be started with this file as a sole input parameter using _-i <json file name>_ command line option.


## tdaq-09-03-00

### Data Alignment

Fragment building algorithms have been modified to produce 4-byte aligned data. Both GBT and FULL mode algorithms expect that every incoming data chunk has a size that is multiple of 4 bytes. If this is not the case the algorithms add padding zeros at the end of the chunk to make it 4-byte aligned.

### Public API changes

The type of the **swrod::ROBFragment::m_data** attribute has been changed. This affects custom processing code that deals with ROB fragments payload. See the updated [User's Guide](https://gitlab.cern.ch/atlas-tdaq-software/swrod#rob-fragment-memory-management) for the detailed explanation of the new API.

### Configuration schema changes

* A new class **SwRodMonitoringApplication** has been added. It can be used in place of the normal **SwRodApplication** class if data fragments produced by the corresponding SW ROD shall not be used for event building and therefore shall be hiden from HLT.

* **SwRodModule** class has a number of new parameters:
    * **InputMethod** relationship has been moved to this class from the **SwRodRob** one. This is done to be able to share the same input object by multiple ROBs if they belong to the same module.
    * **CPU** attribute has been moved to this class from the **SwRodRob** one. It can be used to set CPU affinity for the data receiving threads.
    * **WorkersNumber** attribute has been moved from the **SwRodFragmentBuilder** class. This attribute defines the number of data receiving threads that will be used by the input object.
    * **L1AHandler** is a new optional relationship. This relationship allows to define a specific TTC-to-Host e-link for the ROBs that are referenced by a given module. If this relationship is left empty then TTC-to-Host e-link from the default **L1AHandler** object referenced by the **SwRodConfiguration** will be used instead. If the latter is also empty then fragment building will be data-driven.

* Two attributes of the **SwRodFragmentBuilder** class have been renamed, which affects as well **SwRodFullModeBuilder** and **SwRodGBTModeBuilder** classes, which inherit from it:
    * **SendersNumber** attribute has been renamed to **BuildersNumber**
    * **FlashBufferAtStop** attribute has been renamed to **FlushBufferAtStop**

* A new attribute **FlushBufferAtStop** has been added to the **SwRodFragmentConsumer** class. This attribute is inherited by all specific Consumer classes.

* **BufferPages** and **BufferPageSize** attributes have been removed from the **SwRodNetioNextInput** as now these parameters are taken directly from the FelixBus where they are published by the service providers.

* The type of **CPU** attribute of the SW ROD configuration classes have been changed from integer to string. A string value may contain comma separated list of CPU core numbers and optionally may contain ranges, for example: 0,5,7,9-11. By default the attribute value is set to an empty string, which means that no affinity is set for the corresponding worker threads.


## tdaq-09-02-01

This release introduces an OKS configuration schema change to facilitate splitting of the TDAQ and detector specific portions of SW ROD configuration. The new schema has a new class called **SwRodDataChannel** that should be used by detector experts to configure how data for a given data channel has to be collected and processed. This class emerges from the legacy **SwRodRob** one and steals two relationships from it:

* **Contains** relationship should contain a set of e-links to be used to receive data for the data channel **SwRodDataChannel**

* **CustomLib** relationship shall point to the custom plugin that will be used for data assembling and post-processing of the fragments produced for the given data channel

Finally an instance of the **SwRodDataChannel** class has to be linked to an instance of the **SwRodRob** class via the **Contains** relationship of the latter. Note that despite the fact that this relationship allows multiple objects to be referenced an instance of the **SwRodRob** must point to exactly one instance of the **SwRodDataChannel** class. If that is not the case SW ROD configuration will fail and an error message will be produced.

More details about the new way of configuring SW ROD can be found in the updated Reference Manual as well as in the README file of the package.

## tdaq-09-01-00

* Two attributes of the SwRodInputLink class have been renamed:
    * **DetectorID** => **DetectorResourceId**
    * **DetectorName** => **DetectorResourceName**

* HLT Request Handler implementation has been updated to improve performance. As a result an object of the **SwRodHLTRequestHandler** class has to be linked with each **SwRodRob** object via its _Consumers_ relationship. A link between **SwRodConfiguration** and **SwRodHLTRequestHandler** objects must be removed.

* By default ROBs and E-Links IDs in a SW ROD OKS configuration are shown in hexadecimal format.

* Common SW ROD configuration objects, which don't normally require customization have been placed to the **daq/sw/swrod-common.data.xml** OKS configuration class that is installed to the **installed/share/data** area of the TDAQ release. Any SW ROD OKS configuration is advised to use these objects instead of creating custom ones unless any parameters modification is required.

* **GBTModeBuilder** and **FullModeBuilder** algorithms now automatically detect if the respective SW ROD application uses TTC data handler for getting L1 Accept packets from FELIX. If that is the case the algorithms will run in TTC-aware mode, otherwise they will be data-driven. Contrary to the previous release there is no need to change the value of the Type parameter of the **ROBFragmentBuilder** class in the OKS configuration to change the fragment building mode. In the new implementation one should either link an instance of the **SwRodL1AInputHandler** with the **SwRodConfiguration** object via the _L1AHandler_ relationship to use TTC-aware variant of the chosen algorithm or otherwise to leave this relationship empty to use the fragment building algorithm in data-driven mode.

* Each detector custom plugin may now provide a function for data integrity validation following the example given below. If a plugin provides such a function the function name shall be set to the _DataIntegrityChecker_ attribute of the **SwRodCustomProcessingLib** OKS configuration object that describes this plugin.

```cpp
extern "C"
std::optional<bool> dataIntegrityChecker(const uint8_t * data) {
	if (contains_checksum(data)) {
		uint8_t checksum = get_checksum(data);
		return checksum == calculate_checksum(data) ? true : false;
	}
	return std::nullopt;
}
```

* The package provides so called Felix Emulator that can be used to send input data to an arbitrary SW ROD Application via Netio protocol. OKS file **data/FelixEmulatorSegment.data.xml** shows how to configure Felix Emulator. This example defines a FelixEmulator that can provide input to the SW ROD Application defined in the **data/SwRodSegment.data.xml** file. The FelixEmulator uses internal data generators to create L1A and data packets and sends these packets to the SW ROD Application. The Emulator is implemented by the SW ROD framework using a special plugin that can publish generated data via Netio protocol. Generated data packets can be customized either by modifying the _DataInput_ interface implementation provided by the **test/core/InternalDataGenerator.h(cpp)** files or by creating a new plugin that declares and implements a new generator class that inherits the **swrod::test::InternalDataGenerator** and overrides its _generatePacket()_ virtual function.
```

### `schema/swrod.schema.xml`  
*Local path: `repo/swrod/schema/swrod.schema.xml`*

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

<info name="" type="" num-of-items="26" oks-format="schema" oks-version="oks-08-03-04-1-gf920aa4 built &quot;May 12 2022&quot;" created-by="kolos" created-on="pcatd88.cern.ch" creation-time="20091027T171136" last-modified-by="kolos" last-modified-on="pc-tbed-swrod-01.cern.ch" last-modification-time="20221129T103212"/>

<include>
 <file path="daq/schema/core.schema.xml"/>
 <file path="daq/schema/df.schema.xml"/>
</include>


 <class name="FelixLink">
  <superclass name="Resource"/>
  <attribute name="FelixId" description="Identifier of the input channel. Unique across the system." type="u64" format="hex"/>
  <attribute name="DetectorResourceId" description="ID of detector element" type="u32" format="hex"/>
  <attribute name="DetectorResourceName" description="Name of detector element" type="string"/>
 </class>

 <class name="SwRodApplication" description="Defines configuration for a SW ROD aplication">
  <superclass name="ROS"/>
  <attribute name="CPU" description="Affinity of the application&apos;s threads will be set to the given CPU cores. The numbers are separated by commas and may include ranges. For example: 0,5,7,9-11" type="string"/>
 </class>

 <class name="SwRodBufferInput">
  <superclass name="SwRodInputMethod"/>
  <attribute name="Type" type="string" init-value="BufferInput"/>
  <attribute name="DMABufferId" description="ID of DMA buffer to read data from. The tens digit specifies the FELIX device ID, while the ones digit specifies the DMA buffer ID within that device." type="u32" init-value="0"/>
  <attribute name="DMABufferSize" description="Size of the DMA buffer in 1KB blocks." type="u32" format="hex" init-value="0x100000"/>
  <attribute name="DMABufferNumaNode" description="Defines the NUMA node ID where the buffer memory should be allocated. For optimal performance, this should match the NUMA node of the PCI slot hosting the FELIX card." type="u32" init-value="0"/>
 </class>

 <class name="SwRodConfiguration">
  <superclass name="ReadoutConfigurationBase"/>
  <attribute name="ISServerName" description="Name of IS server for publishing statistics" type="string" init-value="DF" is-not-null="yes"/>
  <relationship name="Plugins" description="List of plugin libraries" class-type="SwRodPluginLib" low-cc="one" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="L1AHandler" description="A handler of L1Accept packets" class-type="SwRodL1AInputHandler" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="yes" is-dependent="no"/>
  <relationship name="Consumers" description="List of ROBFragment consumers" class-type="SwRodFragmentConsumer" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="InputMethod" class-type="SwRodInputMethod" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SwRodCustomProcessingLib">
  <attribute name="LibraryName" description="Name of the cutom processing library (excluding lib prefix and .so suffix)" type="string"/>
  <attribute name="TrigInfoExtractor" description="Name of the function to extract L1 ID etc. from incoming data" type="string" is-not-null="yes"/>
  <attribute name="DataIntegrityChecker" description="Name of the function to check integrity of incoming data" type="string"/>
  <attribute name="ProcessorFactory" description="Name of the custom processor factory function" type="string"/>
 </class>

 <class name="SwRodCustomProcessor" description="Implements framework for custom prosessing of fully assembled ROB fragments">
  <superclass name="SwRodFragmentConsumer"/>
  <attribute name="Type" description="Class name of consumer" type="string" init-value="ROBFragmentProcessor"/>
  <attribute name="ProfileExecution" description="If the value is &apos;true&apos; the time of the processing execution will be recorded." type="bool" init-value="false"/>
 </class>

 <class name="SwRodDataChannel" description="Definition of a ROB granularity SW ROD input">
  <superclass name="HW_InputChannel"/>
  <superclass name="ResourceSetAND"/>
  <attribute name="TTCControllerName" description="Name of the closest TTC segment controller. Used to detect when TTC Restart operation is ongoing." type="string" init-value="RootController"/>
  <attribute name="UpdateECRCounter" description="Defines whether SW ROD sets ECR counters in FELIX to the last known ECR value during TTC Restart, Stopless recovery and Resynchronise procedures" type="bool" init-value="true"/>
  <relationship name="CustomLib" description="This library provides trigger information extraction and custom processing procedures" class-type="SwRodCustomProcessingLib" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SwRodDebugStream" description="ROBFragmentConsumer to hold and share ROB fragments with errors">
  <superclass name="SwRodFragmentConsumer"/>
  <attribute name="Type" description="Class name of consumer" type="string" init-value="DebugStream"/>
  <attribute name="EventBufferSize" description="Size of the internal event buffer (in number of events)" type="u32" init-value="100" is-not-null="yes"/>
 </class>

 <class name="SwRodDefaultL1AHandler" description="Level 1 accept input handler configuration">
  <superclass name="SwRodL1AInputHandler"/>
  <attribute name="Type" description="Type of input handler" type="string" init-value="L1AInputHandler"/>
  <attribute name="Link" type="u64" format="hex"/>
  <attribute name="ResynchTimeout" description="Timeout in milliseconds for arrival of the last known L1 Accept packet" type="u32" init-value="1000"/>
 </class>

 <class name="SwRodEventSampler" description="ROBFragmentConsumer to sample fragments for online monitoring">
  <superclass name="SwRodFragmentConsumer"/>
  <attribute name="Type" description="Class name of consumer" type="string" init-value="EventSampler"/>
  <attribute name="MaximumChannels" description="Maximum number of sampling channels, i.e. monitors connected with different selection criteria" type="u32" init-value="1" is-not-null="yes"/>
  <attribute name="EventBufferSize" description="Size of the internal event buffer (in number of events)" type="u32" init-value="100" is-not-null="yes"/>
  <attribute name="SampleAll" description="If the value is &apos;true&apos; sends all matched avents to every monitoring task attached. Shall be used with care as it may create backpressure in the data-flow path." type="bool" init-value="false"/>
  <attribute name="SamplingRatio" description="Sampler will consider every Nth event where N is the value of this attribute" type="u32" range="1..1000000000" init-value="10" is-not-null="yes"/>
 </class>

 <class name="SwRodFelixInput">
  <superclass name="SwRodInputMethod"/>
  <attribute name="Type" type="string" init-value="FelixInput"/>
  <attribute name="DataNetwork" description="Defines network interface to be used for receiving data" type="string" is-not-null="yes"/>
  <attribute name="FelixBusDirectory" description="Directory to be used for storing felixbus information" type="string"/>
  <attribute name="FelixBusGroupName" type="string" init-value="FELIX"/>
  <attribute name="FelixBusInterface" description="Network interface that is used for communication with the FELIX bus service" type="string" init-value="ZSYS_INTERFACE"/>
  <attribute name="FelixBusTimeout" description="Timeout for E-Link ID resolution in milliseconds" type="u32" init-value="1000"/>
 </class>

 <class name="SwRodFileWriter" description="ROBFragmentConsumer to write fragments to file">
  <superclass name="SwRodFragmentConsumer"/>
  <attribute name="Type" description="Class name of consumer" type="string" init-value="FileWriter"/>
  <attribute name="QueueSize" description="Size limit on internal data queue" type="u32" init-value="1024"/>
  <attribute name="IgnoreRecordingEnable" description="Ignore the recording enable flag set in the RunParams IS from the IGUI. Always write to file." type="bool" init-value="false"/>
  <relationship name="EventStorage" description="Event stirage configuration" class-type="EventStorage" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SwRodFragmentBuilder" description="Defines event builder algorithm to be used" is-abstract="yes">
  <attribute name="Type" description="Type of event builder (GBT, Full, etc.)" type="string"/>
  <attribute name="BuildersNumber" description="Number of threads that implement the final phase of event building - create ROB fragments and pass them to consumers" type="u32" range="0..128" init-value="1"/>
  <attribute name="DropCorruptedPackets" description="If this value is set to 1 then corrupted data packets will be dropped" type="bool" init-value="false"/>
  <attribute name="UnsubscribeDisabledLinks" description="If this value is set to 1 then SW ROD will unsubscribe from the stoplessly removed input links, otherwise just mark them as disabled and discard all data received from them." type="bool" init-value="true"/>
  <attribute name="FlushBufferAtStop" description="If set to true flushes input buffers when Stop-of-Run command received and immediatley stops data processing. Otherwise keeps working until buffers get empty." type="bool" init-value="true"/>
  <attribute name="L1AWaitTimeout" description="Timeout in milliseconds to wait for a specific L1 Accept packet to arrive" type="u32" init-value="20"/>
  <attribute name="MaxMessageSize" description="The maximum size of a data packet. Packets of larger size will be either discarded or truncated depending on the specific algorithm implementation." type="u32" init-value="4096"/>
  <attribute name="ReadyQueueSize" description="Output queue size (in fragments number)" type="u32" init-value="100000"/>
  <attribute name="ResynchTimeout" description="Timeout in milliseconds for the fragment with the last known L1 ID been built" type="u32" init-value="4000"/>
  <attribute name="PacketDumpPath" description="Directory to store files with dumps of corrupted packets" type="string" init-value="/tmp"/>
  <attribute name="PacketDumpLimit" description="Maximum number of packets to dump per E-Link" type="u32" init-value="0"/>
  <attribute name="LinkLoggingLimit" description="Maximum number of issues reported per E-Link" type="u32" init-value="1000"/>
  <attribute name="AssemblyBufferSize" description="Maximum number of ROB fagments with either L1 Accept or data packets been missed that can be simultaneusly kept in memory." type="u32" init-value="100000" is-not-null="yes"/>
  <attribute name="AddPacketHeader" description="If set to true, each data packet in the fragment payload will be preceeded by 8-bytes header that cntains the packet size, error status and detector specific E-Link ID." type="bool" init-value="true"/>
  <attribute name="LinkSubscriptionMask" description="This mask is applied to E-Link IDs and the resulting value is used to group &#xA;E-Links to the data receiving threads if the number of the groups is equal &#xA;to the number of these threads as defined by the SwRodModule::WorkersNumber&#xA;parameter. &#xA;Otherwise the mask will be ignored and the E-Links will be equally split&#xA;between the data receiving threads based on the order of their appearence&#xA;in the SwRodDataChannel::Contains relationship." type="u64" format="hex" init-value="0"/>
 </class>

 <class name="SwRodFragmentConsumer" description="Consumer of ROBFragments" is-abstract="yes">
  <attribute name="Type" description="Class name of this consumer" type="string"/>
  <attribute name="FlushBufferAtStop" description="If set to true flushes input buffers when Stop-of-Run command received and immediatley stops data processing. Otherwise keeps working until buffers get empty." type="bool" init-value="true"/>
  <attribute name="QueueSize" description="Input queue size (in fragments number) for this consumer" type="u32" init-value="100000"/>
  <attribute name="WorkersNumber" description="Number of worker threads" type="u32" range="0..128" init-value="1"/>
  <attribute name="CPU" description="Affinity of the worker threads will be set to the given CPU cores. The numbers are separated by commas and may include ranges. For example: 0,5,7,9-11" type="string"/>
 </class>

 <class name="SwRodFullModeBuilder" description="Parameters for Full Mode event builder algorithm">
  <superclass name="SwRodFragmentBuilder"/>
  <attribute name="Type" type="string" init-value="FullModeBuilder"/>
  <attribute name="AddPacketHeader" type="bool" init-value="false"/>
  <attribute name="RODHeaderPresent" description="Defines if input packets already contain ROD headers" type="bool" init-value="false"/>
  <attribute name="MaxMessageSize" description="The maximum size of a data packet. Packets of larger size will be truncated." type="u32" init-value="4096"/>
 </class>

 <class name="SwRodGBTModeBuilder" description="Parameters for GBT event builder algorithm">
  <superclass name="SwRodFragmentBuilder"/>
  <attribute name="Type" type="string" init-value="GBTModeBuilder"/>
  <attribute name="BufferSize" description="Maximum size (# of ROB fragments) of the buffer for aggregating data chunks from differnt E-Links. This value defines a maximum number of ROB fragments that can be built concurrently." type="u32" init-value="10000" is-not-null="yes"/>
  <attribute name="MinimumBufferSize" description="Minimum size (# of ROB fragments) of the data aggregation buffer." type="u32" init-value="64" is-not-null="yes"/>
  <attribute name="RecoveryDepth" description="Maximum number of L1A packets to be checked if the latest data and L1A packets don&apos;t matcheach other. If no matchis is found the algorithm behavior will depend on the value of the DropCorruptedPackets parameter" type="u32" init-value="10"/>
  <attribute name="DataReceivingTimeout" description="Timeout in milliseconds for all data packets with a given L1 ID to arrive. Zero means waiting until the main buffer gets full. The size of the buffer is set via the BufferSize property of the same object." type="u32" init-value="0"/>
  <attribute name="L1AInitiatesTimeout" description="If this value is set to 1 then data receiving timeout will be activated when the corresponding L1A packet is received. Otherwise the timeout is applied to the interval between receving the first and the last data packets with the given L1ID." type="bool" init-value="true"/>
  <attribute name="MaxMessageSize" description="The maximum size of a data packet. Packets of larger size will be discarded." type="u32" init-value="4096"/>
 </class>

 <class name="SwRodHLTRequestHandler" description="ROBFragmentConsumer to serve fragments to HLT">
  <superclass name="SwRodFragmentConsumer"/>
  <attribute name="Type" description="Class name of consumer" type="string" init-value="HLTRequestHandler"/>
  <attribute name="DataServerThreads" description="Number of threads to allocate to the boost::asio::io_server in the DataServer" type="u32" range="0..128" init-value="1"/>
  <attribute name="IOServices" description="Number of io_services to allocate to the boost::asio::io_server in the DataServer" type="u32" range="0..128" init-value="2"/>
  <attribute name="DataRequestTimeout" description="Data request timeout in milliseconds" type="u32" init-value="500"/>
  <attribute name="ClearTimeout" description="Clear request timeout in milliseconds" type="u32" init-value="1000"/>
  <attribute name="IgnoreClearXId" description="Ignore the transaction ID in Clear messages. This is used when running with multiple sources of Clear messages (e.g. ROSTesters), when running with the HLTSV the transaction IDs will be sequential and should be checked for sequence errors." type="bool" init-value="false"/>
  <attribute name="MaxIndex" description="Maximum events to store in index" type="u32" init-value="1000000"/>
  <attribute name="MaxReorder" description="Maximum size of latest L1 derandomising map" type="u32" init-value="100"/>
  <attribute name="MaxClearAge" description="Maximum age in seconds that a failed clear will be considered valid" type="u32" init-value="600"/>
 </class>

 <class name="SwRodInputLink">
  <superclass name="FelixLink"/>
 </class>

 <class name="SwRodInputMethod" description="Defines input data protocol" is-abstract="yes">
  <attribute name="Type" description="Type of input (netio, internal etc.)" type="string"/>
 </class>

 <class name="SwRodInternalDataGenerator">
  <superclass name="SwRodInputMethod"/>
  <attribute name="Type" type="string" init-value="InternalData"/>
  <attribute name="PacketSize" type="u32"/>
  <attribute name="Pileup" type="u32" init-value="1"/>
  <attribute name="EcrInterval" type="u32" init-value="50000"/>
  <attribute name="TargetRate" type="u32" init-value="0xffffffff"/>
  <attribute name="SyncInterval" type="u32" init-value="10000"/>
  <attribute name="TTCQueueSize" type="u32" init-value="100000"/>
  <attribute name="L1idBitMask" type="u32" format="hex" init-value="0xffffffff"/>
  <attribute name="TotalFullModeLinks" description="Total number of FULL mode links" type="u32" init-value="0"/>
  <attribute name="IsFullMode" description="In FULL mode each generated data packet has a distinct L1 ID." type="bool" init-value="true"/>
  <attribute name="IsZeroCopy" description="Uze zero copy mode, which is available only if IsFullMode is set to true." type="bool" init-value="false"/>
 </class>

 <class name="SwRodL1AInputHandler" description="Level 1 accept input handler configuration" is-abstract="yes">
  <attribute name="Type" description="Type of input handler" type="string"/>
  <attribute name="CPU" description="Affinity of the input handler thread will be set to the given CPU cores. The numbers are separated by commas and may include ranges. For example: 0,5,7,9-11" type="string"/>
  <relationship name="InputMethod" class-type="SwRodInputMethod" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SwRodModule">
  <superclass name="ReadoutModule"/>
  <superclass name="ResourceSetAND"/>
  <attribute name="WorkersNumber" description="Number of data receiving threads" type="u32" range="0..128" init-value="1"/>
  <attribute name="CPU" description="Affinity of the input threads will be set to the given CPU cores. The numbers are separated by commas and may include ranges. For example: 0,5,7,9-11" type="string"/>
  <relationship name="L1AHandler" description="A handler of L1Accept packets" class-type="SwRodL1AInputHandler" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="yes" is-dependent="no"/>
  <relationship name="InputMethod" description="This input method overrides the one defined in the SwRodConfiguration object. The input object will be shared by all SwRodRob objects belonging to this module." class-type="SwRodInputMethod" low-cc="zero" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SwRodMonitoringApplication" description="Defines configuration for a non-data-flow SW ROD aplication">
  <superclass name="ReadoutApplication"/>
  <attribute name="CPU" description="Affinity of the application&apos;s threads will be set to the given CPU cores. The numbers are separated by commas and may include ranges. For example: 0,5,7,9-11" type="string"/>
 </class>

 <class name="SwRodPluginLib">
  <attribute name="LibraryName" description="Name of a shared library that implements SW ROD data handling interfaces" type="string" init-value="libswrod_core_impl.so" is-not-null="yes"/>
 </class>

 <class name="SwRodRob" description="Definition of a ROB granularity SW ROD input">
  <superclass name="HW_InputChannel"/>
  <superclass name="ResourceSetAND"/>
  <attribute name="Id" description="Identifier of the ROB. Unique across ATLAS." type="u32" format="hex" init-value="0" is-not-null="yes"/>
  <attribute name="CPU" description="Affinity of the fragment building threads will be set to the given CPU cores. The numbers are separated by commas and may include ranges. For example: 0,5,7,9-11" type="string"/>
  <relationship name="FragmentBuilder" class-type="SwRodFragmentBuilder" low-cc="one" high-cc="one" is-composite="no" is-exclusive="no" is-dependent="no"/>
  <relationship name="Consumers" description="List of ROB fragment consumers local to this ROB" class-type="SwRodFragmentConsumer" low-cc="zero" high-cc="many" is-composite="no" is-exclusive="no" is-dependent="no"/>
 </class>

 <class name="SwRodShredder" description="ROBFragmentConsumer to dispose fragments">
  <superclass name="SwRodFragmentConsumer"/>
  <attribute name="Type" description="Class name of consumer" type="string" init-value="FragmentShredder"/>
  <attribute name="Pileup" description="Number of fragments to be held in memory" type="u32" init-value="1000000"/>
  <attribute name="BatchSize" description="Number of fragments to be released in one go" type="u32" init-value="100"/>
  <attribute name="ReleaseOnly" description="Do not release fragments, just mark them as ready to be released" type="bool" init-value="0"/>
 </class>

</oks-schema>
```

### `data/SwRodTestPartition.data.xml`  
*Local path: `repo/swrod/data/SwRodTestPartition.data.xml`*

```xml
<?xml version="1.0" encoding="ASCII"?>

<!-- oks-data version 2.0 -->


<!DOCTYPE oks-data [
  <!ELEMENT oks-data (info, (include)?, (comments)?, (obj)+)>
  <!ELEMENT info EMPTY>
  <!ATTLIST info
      name CDATA #REQUIRED
      type CDATA #REQUIRED
      num-of-items CDATA #REQUIRED
      oks-format CDATA #FIXED "data"
      oks-version CDATA #REQUIRED
      created-by CDATA #REQUIRED
      created-on CDATA #REQUIRED
      creation-time CDATA #REQUIRED
      last-modified-by CDATA #REQUIRED
      last-modified-on CDATA #REQUIRED
      last-modification-time CDATA #REQUIRED
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

<info name="" type="" num-of-items="12" oks-format="data" oks-version="oks-07-00-08 built &quot;Mar 30 2020&quot;" created-by="dliko" created-on="pcatd84" creation-time="20030414T160243" last-modified-by="kolos" last-modified-on="pc-tbed-pub-24.cern.ch" last-modification-time="20200330T141519"/>

<include>
 <file path="daq/schema/core.schema.xml"/>
 <file path="daq/segments/common-environment.data.xml"/>
 <file path="daq/segments/setup.data.xml"/>
 <file path="daq/hw/hosts.data.xml"/>
 <file path="SwRodSegment.data.xml"/>
 <file path="FelixEmulatorSegment.data.xml"/>
</include>

<obj class="Binary" id="swrod_dummy_trigger">
 <attr name="BinaryName" type="string" val="swrod_dummy_trigger"/>
 <attr name="Description" type="string" val="SW ROD dummy trigger binary"/>
 <attr name="HelpURL" type="string" val=""/>
 <rel name="BelongsTo" class="SW_Repository" id="swrod-patch-repository"/>
</obj>

<obj class="SW_Repository" id="swrod-patch-repository">
 <attr name="Name" type="string" val="swrod-patch-repository"/>
 <attr name="InstallationPath" type="string" val="/afs/cern.ch/user/k/kolos/public/installed/"/>
 <rel name="Uses">
  <ref class="SW_Repository" id="Online"/>
 </rel>
 <rel name="Tags">
  <ref class="Tag" id="x86_64-el9-gcc13-opt"/>
 </rel>
</obj>

<obj class="DFParameters" id="DET-ID_DataFlowParameters">
 <attr name="BasePortEFD_SFI" type="u16" val="10000"/>
 <attr name="BasePortEFD_SFO" type="u16" val="11000"/>
 <attr name="MulticastAddress" type="string" val="tcp:"/>
 <attr name="DefaultDataNetworks" type="string">
  <data val="10.193.176.59/255.255.255.0"/>
 </attr>
</obj>

<obj class="IS_EventsAndRates" id="SwRodLVL1ISInfo">
 <attr name="EventCounter" type="string" val="DF.swrod.DET-ID_SWROD.ROB-00000001.fragmentsBuilt"/>
 <attr name="Rate" type="string" val="DF.swrod.DET-ID_SWROD.ROB-00000001.instantBuildingRate"/>
</obj>

<obj class="IS_EventsAndRates" id="SwRodRecordingISInfo">
 <attr name="EventCounter" type="string" val="DF.swrod.DET-ID_SWROD.FileWriter.eventsWritten"/>
</obj>

<obj class="IS_InformationSources" id="SwRodISMonitoring">
 <rel name="LVL1" class="IS_EventsAndRates" id="SwRodLVL1ISInfo"/>
 <rel name="Recording" class="IS_EventsAndRates" id="SwRodRecordingISInfo"/>
</obj>

<obj class="RunControlApplication" id="MasterTrigger">
 <attr name="InterfaceName" type="string" val="rc/commander"/>
 <attr name="ActionTimeout" type="s32" val="10"/>
 <attr name="ProbeInterval" type="s32" val="1"/>
 <attr name="FullStatisticsInterval" type="s32" val="63"/>
 <attr name="ControlsTTCPartitions" type="bool" val="0"/>
 <attr name="Logging" type="bool" val="1"/>
 <attr name="InitTimeout" type="u32" val="10"/>
 <attr name="ExitTimeout" type="u32" val="5"/>
 <attr name="RestartableDuringRun" type="bool" val="0"/>
 <attr name="IfExitsUnexpectedly" type="enum" val="Error"/>
 <attr name="IfFailsToStart" type="enum" val="Error"/>
 <rel name="Program" class="Binary" id="swrod_dummy_trigger"/>
</obj>

<obj class="MasterTrigger" id="SWROD_MasterTrigger">
 <rel name="Controller" class="RunControlApplication" id="MasterTrigger"/>
</obj>

<obj class="Segment" id="Trigger">
 <rel name="Applications">
  <ref class="RunControlApplication" id="MasterTrigger"/>
 </rel>
 <rel name="IsControlledBy" class="RunControlTemplateApplication" id="DefRC"/>
</obj>

<obj class="Partition" id="SwRodTest">
 <attr name="RepositoryRoot" type="string" val="/afs/cern.ch/user/k/kolos/public/installed/"/>
 <attr name="IPCRef" type="string" val="$(TDAQ_IPC_INIT_REF)"/>
 <attr name="DBPath" type="string" val="$(TDAQ_DB_PATH)"/>
 <attr name="DBName" type="string" val="$(TDAQ_DB_DATA)"/>
 <attr name="DBTechnology" type="enum" val="rdbconfig"/>
 <attr name="LogRoot" type="string" val="/logs/${TDAQ_VERSION}"/>
 <attr name="WorkingDirectory" type="string" val="/logs"/>
 <attr name="RunTypes" type="string">
  <data val="calibration"/>
  <data val="physics"/>
  <data val="cosmics"/>
 </attr>
 <rel name="Segments">
  <ref class="Segment" id="Trigger"/>
  <ref class="Segment" id="DET-ID_SWROD_Segment"/>
  <ref class="Segment" id="DET-ID_Felix_Emulator_Segment"/>
 </rel>
 <rel name="OnlineInfrastructure" class="OnlineSegment" id="setup"/>
 <rel name="DefaultTags">
  <ref class="Tag" id="x86_64-el9-gcc13-opt"/>
 </rel>
 <rel name="ProcessEnvironment">
  <ref class="Variable" id="ERS_DEBUG_PRIVATE"/>
  <ref class="Variable" id="ERS_DEBUG_LEVEL_PRIVATE"/>
  <ref class="Variable" id="ERS_INFO_CONFIG_PRIVATE"/>
  <ref class="VariableSet" id="External-environment"/>
  <ref class="VariableSet" id="CommonEnvironment"/>
 </rel>
 <rel name="Parameters">
  <ref class="VariableSet" id="CommonParameters"/>
 </rel>
 <rel name="DataFlowParameters" class="DFParameters" id="DET-ID_DataFlowParameters"/>
 <rel name="IS_InformationSource" class="IS_InformationSources" id="SwRodISMonitoring"/>
 <rel name="RunTagList" class="RunTagList" id="ExampleUserTags"/>
 <rel name="MasterTrigger" class="MasterTrigger" id="SWROD_MasterTrigger"/>
 <rel name="Disabled">
  <ref class="SwRodInputLink" id="ELink-401"/>
 </rel>
</obj>

<obj class="RunTagList" id="ExampleUserTags">
 <attr name="RunTags" type="string">
  <data val="Tag1={low,medium,high}"/>
  <data val="Threshold={100,3500,48000}"/>
  <data val="CalibrationType={alignment,radioactive source,gain scan}}"/>
 </attr>
</obj>

<obj class="Variable" id="ERS_DEBUG_LEVEL_PRIVATE">
 <attr name="Description" type="string" val="Debug level above which messages are not filtered in dbg mode"/>
 <attr name="Name" type="string" val="TDAQ_ERS_DEBUG_LEVEL"/>
 <attr name="Value" type="string" val="0"/>
</obj>

<obj class="Variable" id="ERS_DEBUG_PRIVATE">
 <attr name="Description" type="string" val="Debug stream configuration"/>
 <attr name="Name" type="string" val="TDAQ_ERS_DEBUG"/>
 <attr name="Value" type="string" val="filter(swrod),lstdout"/>
</obj>

<obj class="Variable" id="ERS_INFO_CONFIG_PRIVATE">
 <attr name="Description" type="string" val="Configuration of the INFO ERS stream"/>
 <attr name="Name" type="string" val="TDAQ_ERS_INFO"/>
 <attr name="Value" type="string" val="mts,lstdout"/>
</obj>

</oks-data>
```

### `test/oks2json.cpp`  
*Local path: `repo/swrod/test/oks2json.cpp`*

```cpp
/*
 * oks2json.cpp
 *
 *  Created on: Jul 25, 2019
 *      Author: kolos
 */

#include <string>

#include <boost/program_options.hpp>
#include <boost/property_tree/json_parser.hpp>

#include <swrod/exceptions.h>

#include "application/Configuration.h"

using namespace boost::program_options;
using namespace boost::property_tree;

int main(int ac, char *av[]) {
    options_description description("Options");

    description.add_options()("help,h", "produce help message")
        ("database-path,d", value<std::string>()->required(),
                "Database path: 'oksconfig:<xml_file_name>' or 'rdbconfig:<rdb_server_name>[@partition_name]'")
        ("json-file,o", value<std::string>()->required(), "Output file name")
        ("partition,p", value<std::string>()->required(), "Partition name")
        ("swrod-app-name,a", value<std::string>()->required(), "SwRodApplication ID in OKS database");

    variables_map arguments;
    try {
        store(parse_command_line(ac, av, description), arguments);
        notify(arguments);
    } catch (error & ex) {
        std::cerr << ex.what() << std::endl;
        description.print(std::cout);
        return 1;
    }

    if (arguments.count("help")) {
        std::cout << "Converts SW ROD OKS configuration to Json format" << std::endl;
        description.print(std::cout);
        return 0;
    }

    try {
        swrod::Configuration config(
                arguments["database-path"].as<std::string>(),
                IPCPartition(arguments["partition"].as<std::string>()),
                arguments["swrod-app-name"].as<std::string>(),
                true);

        std::string out_file_name = arguments["json-file"].as<std::string>();
        json_parser::write_json(out_file_name.c_str(), config.propertyTree());
    } catch (swrod::Exception & ex) {
        ers::fatal(ex);
        return 1;
    } catch (ers::Issue & ex) {
        ers::fatal(ex);
        return 1;
    } catch (ptree_error & ex) {
        ers::fatal(swrod::BadConfigurationException(ex.what(), ex));
        return 1;
    }

    return 0;
}
```

### `LICENSE`  
*Local path: `repo/swrod/LICENSE`*

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


## 4. `oks2coral` — OKS to Coral archiving (GitLab)

`oks2coral` archives OKS data into a relational (CORAL/MySQL/SQLite/Oracle) archive. `oks2coral/ConfigVersions.h` declares the archive-versioning interface; `src/oks2coral.cpp` is the main archiver; `scripts/oks2coral_mk_tmp_file.sh` builds the archive command. Release notes (HTML) converted to text below.
### `oks2coral/ConfigVersions.h`  
*Local path: `repo/oks2coral/oks2coral/ConfigVersions.h`*

```cpp
#ifndef CONFIGVERSIONS_H
#define CONFIGVERSIONS_H

#include <is/info.h>

#include <string>
#include <ostream>


// <<BeginUserCode>>

// <<EndUserCode>>

/**
 * The class is used to store archive versions of the OKS database used for given run.
 * 
 * @author  generated by the IS tool
 * @version 02/07/13
 */

class ConfigVersions : public ISInfo {
public:

    /**
     * The version of the schema from OKS Archive.
     */
    int                           SchemaVersion;

    /**
     * The version of the data from OKS Archive.
     */
    int                           DataVersion;


    static const ISType & type() {
	static const ISType type_ = ConfigVersions( ).ISInfo::type();
	return type_;
    }

    virtual std::ostream & print( std::ostream & out ) const {
	ISInfo::print( out );
	out << std::endl;
	out << "SchemaVersion: " << SchemaVersion << "\t// The version of the schema from OKS Archive." << std::endl;
	out << "DataVersion: " << DataVersion << "\t// The version of the data from OKS Archive.";
	return out;
    }

    ConfigVersions( )
      : ISInfo( "ConfigVersions" )
    {
	initialize();
    }

    ~ConfigVersions(){

// <<BeginUserCode>>

// <<EndUserCode>>
    }

protected:
    ConfigVersions( const std::string & type )
      : ISInfo( type )
    {
	initialize();
    }

    void publishGuts( ISostream & out ){
	out << SchemaVersion << DataVersion;
    }

    void refreshGuts( ISistream & in ){
	in >> SchemaVersion >> DataVersion;
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
inline std::ostream & operator<<( std::ostream & out, const ConfigVersions & info ) {
    info.print( out );
    return out;
}

#endif // CONFIGVERSIONS_H
```

### `src/oks2coral.cpp`  
*Local path: `repo/oks2coral/src/oks2coral.cpp`*

```cpp
#include <unistd.h>
#include <dirent.h>
#include <string.h>
#include <signal.h>
#include <errno.h>

#include <fstream>
#include <stdexcept>
#include <sstream>

#include <CoralBase/Exception.h>
#include <CoralKernel/Context.h>
#include "RelationalAccess/ConnectionService.h"
#include "RelationalAccess/ISessionProxy.h"
#include <RelationalAccess/ITransaction.h>

#include <oks/kernel.h>
#include <oks/ral.h>

#include <ipc/core.h>
#include <ipc/partition.h>
#include <is/infodictionary.h>

#include <rc/RunParams.h>
#include <oks2coral/ConfigVersions.h>

#include <ers/ers.h>


////////////////////////////////////////////////////////////////////////////////////////////////////

  /** Failed to read run number from online Information Service. */

ERS_DECLARE_ISSUE(
  oks2coral,
  NoRunNumber,
  "Failed to read run number from Information Service in partition \"" << partition_name << '\"',
  ((const char*)partition_name)
)

  /** Failed to read run number from online Information Service. */

ERS_DECLARE_ISSUE(
  oks2coral,
  FailedToCheckin,
  "Failed to check in RunParams.ConfigVersions to IS in partition \"" << partition_name << '\"',
  ((const char*)partition_name)
)

ERS_DECLARE_ISSUE(
  oks2coral,
  FoundAnotherRun,
  "The RunParams.ConfigVersions in partition \"" << partition_name << "\" was already set by another ongoing run, skip update...",
  ((const char*)partition_name)
)

  /** Failed to parse command line. */

ERS_DECLARE_ISSUE(
  oks2coral,
  BadCommandLine,
  "Bad command line: \"" << what << '\"',
  ((const char*)what)
)


  /** Failed to find required information in the OKS database. */

ERS_DECLARE_ISSUE(
  oks2coral,
  BadDatabase,
  "Bad database: \"" << what << '\"',
  ((const char*)what)
)


  /** Failed to find required information in the name of the OKS database (when scan directory). */

ERS_DECLARE_ISSUE(
  oks2coral,
  BadDatabaseName,
  "Bad name of the database: \"" << what << '\"',
  ((const char*)what)
)


  /** Failed to archive. */

ERS_DECLARE_ISSUE(
  oks2coral,
  CannotArchiveFile,
  "Failed to archive file \"" << file << "\": " << what,
  ((const char *)file)
  ((const char *)what)
)


  /** Failed to read directory. */

ERS_DECLARE_ISSUE(
  oks2coral,
  CannotReadDirectory,
  "Failed to read directory \"" << dir << "\": " << what,
  ((const char *)dir)
  ((const char *)what)
)


  /** Failed to delete archived file. */

ERS_DECLARE_ISSUE(
  oks2coral,
  CannotRemoveFile,
  "Failed to remove archived file \"" << file << "\": " << what,
  ((const char *)file)
  ((const char *)what)
)


  /** Failed to read OKS database file. */

ERS_DECLARE_ISSUE(
  oks2coral,
  CaughtException,
  "Caught " << what << " exception: \'" << text << "\'",
  ((const char *)what)
  ((const char *)text)
)


  /** The archived data are very differed from the base version. Ask to create new base version. */

ERS_DECLARE_ISSUE(
  oks2coral,
  TooManyChanges,
  "The configuration description of " << partition_name << " partition is too different from stored in base version (schema=" << schema_base_version << ", data=" << data_base_version << "). "
  "The archiving requires creation of incremental version containing " << number_of_created_rows << " rows, while maximum allowed number is set to " << max_number_of_rows << ". " << text,
  ((const char*)partition_name)
  ((int)schema_base_version)
  ((int)data_base_version)
  ((long)number_of_created_rows)
  ((long)max_number_of_rows)
  ((const char*)text)
)

////////////////////////////////////////////////////////////////////////////////////////////////////

class OksToCoral {

  public:

      // initialize object parsing command line

    OksToCoral(int argc, char *argv[]);

    void run();


  private:
  
    int p_verbose_level;
    std::string p_connect_string;
    std::string p_partition_name;
    long p_run_number;
    std::string p_description;
    std::string p_working_schema;
    int p_schema_version;
    int p_base_version;
    long p_warn_max_num_of_new_rows;
    long p_error_max_num_of_new_rows;
    std::string p_file;
    std::string p_dir;

  public:
    
    static bool s_interrupted;


  private:

      // is used by command line parser

    void no_param(const char * cp);


      // read run number from Information Service (archive single file and exit)

    void get_run_number_from_is();


      // read run number and partition name from the file name

    void parse_file_name(const std::string& file);


      // archives single file

    void archive_file(const std::string& file);

};

bool OksToCoral::s_interrupted = false;

////////////////////////////////////////////////////////////////////////////////////////////////////

extern "C" void
signal_handler(int num)
{
  std::cout << "got signal " << num << ", stopping..." << std::endl; 
  OksToCoral::s_interrupted = true;
}

////////////////////////////////////////////////////////////////////////////////////////////////////


void
OksToCoral::get_run_number_from_is()
{
  IPCPartition p(p_partition_name);
  ISInfoDictionary isInfoDict(p);

  RunParams runParameter;
  runParameter.run_number = 0;

  try {
    isInfoDict.findValue("RunParams.RunParams", runParameter);
    p_run_number = runParameter.run_number;
    ERS_DEBUG(1, "Read from Information Service (partition \'" << p_partition_name << "\') run number = " << runParameter.run_number);
  }
  catch( daq::is::Exception & ex ) {
    ers::error(oks2coral::NoRunNumber(ERS_HERE, p_partition_name.c_str(), ex));
    p_run_number = 0;
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

void
OksToCoral::parse_file_name(const std::string& file)
{
    // find first dot in the file name: the index points to the end of run number

  std::string::size_type idx1 = file.find('.');
  if(idx1 == std::string::npos) {
    std::string s = std::string("failed to find first separator dot in the name of file \"") + file + "\" (expected \"RunNumber.PartitionName.TimeStamp.data.xml\").";
    throw oks2coral::BadDatabaseName(ERS_HERE, s.c_str());
  }

  p_run_number = (unsigned long)strtol(file.substr(0, idx1).c_str(), 0, 10);


    // find suffix ".data.xml" to start searching for partition name

  std::string::size_type idx2 = file.rfind(".data.xml");
  if(idx2 == std::string::npos || idx2 < 2) {
    std::string s = std::string("failed to find \".data.xml\" suffix in the name of file \"") + file + "\" (expected \"RunNumber.PartitionName.TimeStamp.data.xml\").";
    throw oks2coral::BadDatabaseName(ERS_HERE, s.c_str());
  }



    // skip numeric timestamp and get partition name

  std::string::size_type idx3 = file.rfind('.', idx2 - 1);
  if(idx3 == std::string::npos) {
    std::string s = std::string("failed to find partition name in the name of file \"") + file + "\" (expected \"RunNumber.PartitionName.TimeStamp.data.xml\").";
    throw oks2coral::BadDatabaseName(ERS_HERE, s.c_str());
  }
  else {
    idx3++;
  }

  p_partition_name = file.substr(idx1 + 1, idx3 - idx1 - 2);

  if(p_partition_name.empty()) {
    std::string s = std::string("failed to find partition name in the file \"") + file + "\" (expected \"RunNumber.PartitionName.TimeStamp.data.xml\").";
    throw oks2coral::BadDatabaseName(ERS_HERE, s.c_str());
  }


    // set description including partition name

  p_description = std::string("oks2coral: partition ") + p_partition_name + " (" + RELEASE_VERSION + ')';
}

////////////////////////////////////////////////////////////////////////////////////////////////////

void
OksToCoral::run()
{
    // if file is explicitly provided via the command line, then archive it and exit

  if(!p_file.empty()) {

      // get Run Number from IS server
    get_run_number_from_is();

      // archive the file
    try {
      archive_file(p_file);
    }
    catch(ers::Issue& e) {
      ers::error(e);
    }

    return;

  }

  {
    OksKernel k;
    std::string fq_dir = k.get_file_path(p_dir);
    if(fq_dir != p_dir) {
      std::cout << "The \'" << p_dir << "\' is non-fully-qualified name. Will use \'" << fq_dir << "\' instead." << std::endl;
      p_dir = fq_dir;
    }
  }

  std::set<std::string> bad_names;          // bad formatted file names
  std::set<std::string> bad_files;          // bad files (no partition object, non-oks file, etc.)
  std::set<std::string> bad_files_pre;      // first attempt to mark file as "bad": sometimes NFS shows file as empty and sync it later
  std::set<std::string> unremovable_files;  // file has been archived but cannot be removed
  std::set<std::string> problematic_files;  // cannot archive (e.g. require new base version, more space; to be re-tested with low frequency)

  const unsigned int sleep_interval = 10;   // sleep this amount of seconds before reading directory next time
  const unsigned int low_frequency = 180;   // test problematic files once per given value (e.g. 10" x 180 = 30')

  unsigned int count = 0;

  while(!s_interrupted) {
    count++;

    if(DIR * dir = opendir(p_dir.c_str())) {
      std::set<std::string> files;

      for(struct dirent * d = readdir(dir); d != 0; d = readdir(dir)) {
        std::string test(d->d_name);
        std::string::size_type idx = test.rfind(".data.xml");

        if(idx == std::string::npos || (idx + 9) != test.size()) {
	  ERS_DEBUG(2, "skip \"" << d->d_name << "\" (does not have .data.xml suffix)");
	  continue;
	}

        if(test.find(".oks-lock-") == 0) {
          ERS_DEBUG(2, "skip lock file \"" << test << '\"');
          continue;
        }

        {
          std::string s = p_dir + "/.oks-lock-" + test;
          std::ifstream file(s.c_str());
          if(file) {
            ERS_DEBUG(2, "skip temporary locked file \"" << test << '\"');
            continue;
          }
        }

	if(bad_names.find(test) != bad_names.end()) {
	  ERS_DEBUG(2, "skip file with bad name \"" << test << '\"');
	  continue;
	}

	if(bad_files.find(test) != bad_files.end()) {
	  ERS_DEBUG(2, "skip file with bad contents \"" << test << '\"');
	  continue;
	}

	if(unremovable_files.find(test) != unremovable_files.end()) {
	  ERS_DEBUG(2, "skip unremovable file \"" << test << "\" (it was archived already)");
	  continue;
	}

	if(problematic_files.find(test) != problematic_files.end()) {
	  if((count%low_frequency) == 0) {
	    ERS_DEBUG(2, "add problematic file \"" << test << "\" (counter = " << count << ')');
	  }
	  else {
	    ERS_DEBUG(2, "skip problematic file \"" << test << '\"');
	    continue;
	  }
	}

        files.insert(d->d_name);
      }

      closedir(dir);

      for(std::set<std::string>::const_iterator i = files.begin(); (i != files.end()) && !s_interrupted; ++i) {
        try {
          ERS_LOG("Trying to archive file \"" << *i << "\"...");
	  parse_file_name(*i);
          std::string the_file = p_dir + '/' + *i;
	  archive_file(the_file);
          ERS_LOG("File \'" << the_file << "\' has been archived");

	  if(unlink(the_file.c_str())) {
            std::ostringstream text;
            text << "unlink() function failed: \'" << strerror(errno) << '\'';
            ers::error(oks2coral::CannotRemoveFile(ERS_HERE, the_file.c_str(), text.str().c_str()));
	    unremovable_files.insert(*i);
	  }
	  else {
	    std::string schema_file(the_file.substr(0, the_file.rfind(".data.xml")));
	    schema_file += ".schema.xml";
	    if(unlink(schema_file.c_str())) {
              std::ostringstream text;
              text << "unlink() function failed: \'" << strerror(errno) << '\'';
              ers::error(oks2coral::CannotRemoveFile(ERS_HERE, schema_file.c_str(), text.str().c_str()));
	    }
	  }
	}
	catch(oks2coral::BadDatabaseName & e) {
	  ers::error(e);
	  bad_names.insert(*i);
	  std::cout << "Name of file \'" << *i << "\' is bad; ignore it in future\n";
	}
	catch(oks2coral::BadDatabase & e) {
	  ers::error(e);
	  if(bad_files_pre.find(*i) == bad_files_pre.end()) {
	    bad_files_pre.insert(*i);
	    std::cout << "once ignore bad file \"" << *i << "\"\n";
	  }
	  else {
	    bad_files.insert(*i);
	    std::cout << "Contents of file \'" << *i << "\' is bad; ignore it in future\n";
	  }
	}
	catch(oks2coral::CannotArchiveFile & e) {
	  ers::error(e);
	  problematic_files.insert(*i);
	  std::cout << "Cannot archive file \'" << *i << "\'; try again later (wait " << (sleep_interval * low_frequency) << " seconds)\n";
	}
      }
    }
    else {
      std::ostringstream text;
      text << "opendir() function failed: \'" << strerror(errno) << '\'';
      ers::error(oks2coral::CannotReadDirectory(ERS_HERE, p_dir.c_str(), text.str().c_str()));
    }

    sleep(sleep_interval);
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

void
OksToCoral::no_param(const char * cp)
{
  std::ostringstream s;
  s << "no parameter(s) for argument \"" << cp << "\" been provided";
  throw oks2coral::BadCommandLine(ERS_HERE,s.str().c_str());
}

////////////////////////////////////////////////////////////////////////////////////////////////////

OksToCoral::OksToCoral(int argc, char *argv[]) :
  p_verbose_level(1),
  p_schema_version(0),
  p_base_version(0),
  p_warn_max_num_of_new_rows(-1),
  p_error_max_num_of_new_rows(-1)
{
  for(int i = 1; i < argc; i++) {
    const char * cp = argv[i];

    if(!strcmp(cp, "-h") || !strcmp(cp, "--help")) {
      std::cout <<
        "Usage: oks2coral\n"
        "       -c | --connect-string connect_string\n"
        "       -w | --working-schema schema_name\n"
        "       [-p | --partition-name\n" 
        "       [-s | --schema-version schema_version]\n"
        "       [-b | --use-base-version data_version]\n"
	"       [-x | --warn-max-update-size size]\n"
        "       [-X | --error-max-update-size size]\n"
        "       [-d | --description text]\n"
        "       [-f | --oks-files file]\n"
        "       [-r | --directory dir]\n"
        "       [-v | --verbose-level verbosity_level]\n"
        "       [-h | --help]\n"
        "\n"
        "Options/Arguments:\n"
        "       -c connect_string    database connection string\n"
        "       -w schema_name       name of working schema\n"
        "       -p partition_name    UID of the partition to work on\n" 
        "       -s schema_version    use given schema version number\n"
        "       -b base_version      use given data version number as base version\n"
        "       -x size              if a base version is used and number of new rows to be created exceeds limit, report error\n"
        "       -X size              if a base version is used and number of new rows to be created exceeds limit, report fatal error\n"
        "       -d description_text  provide description for this data version\n"
        "       -f file              the oks database file to be archived (cannot be used with -r)\n"
        "       -r dir               the directory where oks files to be archived can appear (cannot be used with -f)\n"
        "       -v verbosity_level   set verbose output level (0 - silent, 1 - normal, 2 - extended, 3 - debug, ...)\n"
        "       -h                   print this message\n"
        "\n"
        "Description:\n"
        "       The utility archives oks objects from xml files into relational database.\n"
        "       It is only supposed to be used for incremental versioning. To put new schema\n"
	"       or base data version use oks-create-new-base-version.sh utility.\n"
        "       Depending on command line options -f and -r, the utility either:\n"
        "        - archives oks file(s) once and then exits (-f option), or\n"
        "        - scans for *.data.xml files in directory specified using -r option\n"
        "          once files X.data.xml and X.schema.xml will be found, they will be archived and then removed\n";

      exit (EXIT_SUCCESS);
    }
    else if(!strcmp(cp, "-v") || !strcmp(cp, "--verbose-level")) {
      if(++i == argc) { no_param(cp); } else { p_verbose_level = atoi(argv[i]); }
    }
    else if(!strcmp(cp, "-s") || !strcmp(cp, "--schema-version")) {
      if(++i == argc) { no_param(cp); } else { p_schema_version = atoi(argv[i]); }
    }
    else if(!strcmp(cp, "-b") || !strcmp(cp, "--use-base-version")) {
      if(++i == argc) { no_param(cp); } else { p_base_version = atoi(argv[i]); }
    }
    else if(!strcmp(cp, "-x") || !strcmp(cp, "--warn-max-update-size")) {
      if(++i == argc) { no_param(cp); } else { p_warn_max_num_of_new_rows = atoi(argv[i]); }
    }
    else if(!strcmp(cp, "-X") || !strcmp(cp, "--error-max-update-size")) {
      if(++i == argc) { no_param(cp); } else { p_error_max_num_of_new_rows = atoi(argv[i]); }
    }
    else if(!strcmp(cp, "-d") || !strcmp(cp, "--description")) {
      if(++i == argc) { no_param(cp); } else { p_description = argv[i]; }
    }
    else if(!strcmp(cp, "-c") || !strcmp(cp, "--connect-string")) {
      if(++i == argc) { no_param(cp); } else { p_connect_string = argv[i]; }
    }
    else if(!strcmp(cp, "-w") || !strcmp(cp, "--working-schema")) {
      if(++i == argc) { no_param(cp); } else { p_working_schema = argv[i]; }
    }
    else if(!strcmp(cp, "-p") || !strcmp(cp, "--partition-name")) {
      if(++i == argc) { no_param(cp); } else { p_partition_name = argv[i]; }
    }
    else if(!strcmp(cp, "-f") || !strcmp(cp, "--oks-file")) {
      if(++i == argc) { no_param(cp); } else { p_file = argv[i]; }
    }
    else if(!strcmp(cp, "-r") || !strcmp(cp, "--directory")) {
      if(++i == argc) { no_param(cp); } else { p_dir = argv[i]; }
    }
    else {
      std::ostringstream s;
      s << "Unexpected parameter \"" << cp << '\"';
      throw oks2coral::BadCommandLine(ERS_HERE,s.str().c_str());
    }
  }

  if(p_schema_version < 0) {
    throw oks2coral::BadCommandLine(ERS_HERE,"the schema version is required; use -s or -l option");
  }

  if(p_base_version > 0 && p_schema_version < 0) {
    throw oks2coral::BadCommandLine(ERS_HERE,"if base version is provided, the explicit schema version is required");
  }

  if(p_partition_name.empty()) {
    if(!p_file.empty()) {
      if(char * s = getenv("TDAQ_PARTITION")) {
        ERS_DEBUG(1, "use partition \'" << s << "\' (read from TDAQ_PARTITION environment variable)");
        p_partition_name = s;
      }
      else {
        throw oks2coral::BadCommandLine(ERS_HERE,"the partition name is required. Set TDAQ_PARTITION environment variable or pass the name via command line.");
      }
    }
  }
  else if(!p_dir.empty()) {
    throw oks2coral::BadCommandLine(ERS_HERE,"the partition name command line option is not needed, when -r option is used");
  }

  if(p_description.empty()) {
    if(p_dir.empty()) {
      p_description = std::string("oks2coral: partition ") + p_partition_name + " (" + RELEASE_VERSION + ')';
    }
  }
  else {
    if(!p_dir.empty()) {
      throw oks2coral::BadCommandLine(ERS_HERE, "the description cannot be set, when -r option is used");
    }
  }

  if(p_connect_string.empty()) {
    throw oks2coral::BadCommandLine(ERS_HERE,"the connect string is required");
  }

  if(p_working_schema.empty()) {
    throw oks2coral::BadCommandLine(ERS_HERE,"the working schema is required");
  }

  if(p_file.empty() && p_dir.empty()) {
    throw oks2coral::BadCommandLine(ERS_HERE,"at least an oks file (-f) or a directory (-r) is required");
  }

  if(!p_file.empty() && !p_dir.empty()) {
    throw oks2coral::BadCommandLine(ERS_HERE,"cannot use simultaneously -f and -r options");
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

  // archive list of files

void
OksToCoral::archive_file(const std::string& file)
{
    // load oks file

  ::OksKernel kernel;
  kernel.set_silence_mode(true);

  try {
    kernel.load_file(file);
  }
  catch (oks::exception & ex) {
    throw oks2coral::BadDatabase(ERS_HERE, ex.what());
  }


    // compute data (select data referenced by partition object)

  OksObject::FSet objects;

  if(OksClass * c = kernel.find_class("Partition")) {
    if(OksObject * p = c->get_object(p_partition_name)) {
      objects.insert(p);
      p->references(objects, 1000000);
    }
    else {
      std::string s = std::string("failed to find object \"") + p_partition_name + "@Partition\".";
      throw oks2coral::BadDatabase(ERS_HERE, s.c_str());
    }

    if(ers::debug_level() >= 3) {
      std::ostringstream text;

      text << objects.size() << " objects are going to be archived:\n";
      for(OksObject::FSet::const_iterator j = objects.begin(); j != objects.end(); ++j) {
        text << *j << std::endl;
      }

      ERS_DEBUG(3, text.str());
    }
  }
  else {
    std::ostringstream s;
    s << "cannot find class \'Partition\'.";
    throw oks2coral::BadDatabase(ERS_HERE,s.str().c_str());
  }


  try {

      // be sure that connection is always closed, even in case of exception

    std::unique_ptr<coral::ConnectionService> connection;

    {
      std::unique_ptr<coral::ISessionProxy> session (oks::ral::start_coral_session(p_connect_string, coral::Update, connection, p_verbose_level));

      std::vector<int> versions;

      if(p_schema_version == 0) {
        versions = oks::ral::get_schema_versions(session.get(), p_working_schema, 0, p_verbose_level);
	if(versions.empty()) {
          versions.push_back(0); // a proper exception with release name will be thrown by put_data()
	}
      }
      else {
        versions.push_back(p_schema_version);
      }

      for(unsigned int i = 0; i <= versions.size(); ++i) {
        int schema_version = 0;
        int base_version = p_base_version;

	  // create new schema version, if the schema was not explicitly defined
	  // and all existing versions were tested

	if(i == versions.size()) {
	  if(p_schema_version == 0) {
	    p_error_max_num_of_new_rows = p_warn_max_num_of_new_rows = -1;
            oks::ral::put_schema(kernel.classes(), session.get(), p_working_schema, 0, "auto create version by oks2coral", p_verbose_level);
	    base_version = -1;
            ERS_INFO("create new schema version");
	  }
	  else {
	    throw std::runtime_error("cannot archive file (the schema was explicitly set in command line)");
	  }
	}
	else {
	  schema_version = versions[i];
          ERS_DEBUG(1, "Test schema version " << schema_version);
	}

        int data_version = 0; // create new head version incrementing max defined data version for given schema
        oks::ral::InsertedDataDetails rv;
	
	try {
	  rv = oks::ral::put_data(kernel, (objects.empty() ? 0 : &objects), session.get(), p_working_schema, schema_version, data_version, base_version, p_description, p_error_max_num_of_new_rows, p_verbose_level);
        }
	catch(std::exception& ex) {
	  if(strstr(ex.what(), "differs from one stored in database (schema version")) {
            ERS_DEBUG(1, "Assume exception \'" << ex.what() << "\' took place because of schema mismatch");
            continue;	    
	  }
	  else {
            ERS_LOG("oks::ral::put_data(\'" << file << "\') has failed, rollback transaction and end user session ...");
            session->transaction().rollback();
	    throw;
	  }
	}

        int ret_value1 = rv.m_insertedOksObjectRowsThis + rv.m_insertedOksDataRelRowsThis + rv.m_insertedOksDataValRowsThis;
        int ret_value2 = rv.m_insertedOksObjectRowsBase + rv.m_insertedOksDataRelRowsBase + rv.m_insertedOksDataValRowsBase;

        if(ret_value1 != 0 || ret_value2 != 0) {
          if(p_error_max_num_of_new_rows >= 0 && ret_value1 > p_error_max_num_of_new_rows) {
            oks2coral::TooManyChanges issue(
              ERS_HERE, p_partition_name.c_str(), schema_version, data_version, ret_value1, p_warn_max_num_of_new_rows,
              "Create new base version to re-enable archiving!");
            ers::error(issue);
            throw std::runtime_error("number of new rows to be inserted exceeds the hard limit.");
          }
          else if(p_warn_max_num_of_new_rows >= 0 && ret_value1 > p_warn_max_num_of_new_rows) {
            oks2coral::TooManyChanges issue(
              ERS_HERE, p_partition_name.c_str(), schema_version, data_version, ret_value1, p_warn_max_num_of_new_rows,
              "Create new base version as soon as possible!");
            ers::warning(issue);
          }

          if(rv.m_use_base == false) {
            ERS_DEBUG(2, "The oks objects have been imported, committing transaction...");
            session->transaction().commit();
          }
          else {
            ERS_DEBUG(2, "There is no need to import oks objects (use base version " << data_version << "), aborting transaction...");
            session->transaction().rollback();
          }
        }
        else {
          ERS_DEBUG(2, "No oks objects have been imported (use base version " << data_version << "), aborting transaction...");
          session->transaction().rollback();
        }

        {
          std::ostringstream s;

          s << "oks2coral: configuration data have been archived\n";

          if((ret_value1 != 0 || ret_value2 != 0) && rv.m_use_base == false) {
            s << "* new incremental version " << schema_version << '.' << data_version << " has been created\n"
	         "* insert " << ret_value1 << " row(s) into incremental version (" << schema_version << '.' << data_version << ")\n"
	         "* insert " << ret_value2 << " row(s) into base version (" << schema_version << '.' << base_version << ')';
          }
          else {
            s << "* keep existing version " << schema_version << '.' << data_version << " unchanged";
          }

          ERS_INFO(s.str());
        }


          // publish in IS to be used by CDI

        {
          ERS_DEBUG(1, "Publish data in IS (partition \'" << p_partition_name << "\')");

          IPCPartition p(p_partition_name);
          ISInfoDictionary dict(p);

          try {

              // test that the data were not set already

            ConfigVersions cv;
            dict.findValue("RunParams.ConfigVersions", cv);
            ers::warning(oks2coral::FoundAnotherRun(ERS_HERE,p_partition_name.c_str()));

          }
          catch(daq::is::Exception & ex) {

              // insert data if they were not set by ongoing run

            ERS_DEBUG(4, "did not find RunParams.ConfigVersions (OK)");

            ConfigVersions cv;
            cv.SchemaVersion = schema_version;
            cv.DataVersion = data_version;

            try {
              dict.checkin("RunParams.ConfigVersions", cv);
            }
            catch( daq::is::Exception & ex ) {
              ers::warning(oks2coral::FailedToCheckin(ERS_HERE,p_partition_name.c_str(), ex));
            }
          }
        }


          // archive in OKS Arcive table (e.g. if there is no CDI)

        ERS_DEBUG(2, "Starting a new transaction...");
        session->transaction().start();

        oks::ral::create_archive_record(session.get(), p_working_schema, schema_version, data_version, p_partition_name, p_run_number, p_verbose_level);

        ERS_DEBUG(2, "Committing...");
        session->transaction().commit();

        break;
      }
      ERS_DEBUG(2, "Ending user session..."); // delete session by unique_ptr<>
    }
    ERS_DEBUG(2, "Disconnecting..."); // delete connection by unique_ptr<>
  }

  catch ( coral::Exception& e ) {
    throw oks2coral::CannotArchiveFile(ERS_HERE, file.c_str(), e.what());
  }

  catch ( std::exception& e ) {
    throw oks2coral::CannotArchiveFile(ERS_HERE, file.c_str(), e.what());
  }

  catch ( ... ) {
    throw oks2coral::CannotArchiveFile(ERS_HERE, file.c_str(), "unknown exception");
  }

}

////////////////////////////////////////////////////////////////////////////////////////////////////

int main(int argc, char *argv[])
{

    // initialize IPC core

  try {
    IPCCore::init(argc, argv);
  }
  catch(ers::Issue & ex) {
    ers::warning(ers::Message(ERS_HERE, ex));
  }


    // register handlers for user's signals

  signal(SIGINT,signal_handler);
  signal(SIGTERM,signal_handler);


    // run archiving

  try {

    ERS_LOG("Starting oks2coral...");

    OksToCoral obj(argc, argv);
    obj.run();

    ERS_LOG("Exiting oks2coral...");

  }

  catch ( coral::Exception& e ) {
    ers::fatal(oks2coral::CaughtException(ERS_HERE, "CORAL", e.what()));
    return 1;
  }

  catch (ers::Issue & e ) {
    ers::fatal(oks2coral::CaughtException(ERS_HERE, "ERS", e.what()));
    return 2;
  }

  catch ( std::exception& e ) {
    ers::fatal(oks2coral::CaughtException(ERS_HERE, "Standard C++", e.what()));
    return 3;
  }

  catch ( ... ) {
    ers::fatal(oks2coral::CaughtException(ERS_HERE, "Unknown", ""));
    return 4;
  }

  return 0;
}
```

### `scripts/oks2coral_mk_tmp_file.sh`  
*Local path: `repo/oks2coral/scripts/oks2coral_mk_tmp_file.sh`*

```sh
#!/bin/sh

is_ls_out="/tmp/oks2coral-is_ls.$$"

###############################################################################

PATH="$PATH:/bin:/usr/bin:/usr/local/bin"
export PATH

###############################################################################

# parse command line

out_dir=''
partition_name=''
#file=''
verbose='1'
group=''

while (test $# -gt 0)
do
  case "$1" in

    -v | --verb*)
      verbose="$2" ; shift ;
      ;;

#    -f | --file*)
#      file="$2" ; shift ;
#      ;;
#
    -p | --partition*)
      partition_name="$2" ; shift ;
      ;;

    -o | --out*)
      out_dir="$2" ; shift ;
      ;;

    -g | --group*)
      group="$2" ; shift ;
      ;;

    -h* | --he*)
      echo 'Usage: oks2coral_mk_tmp_file.sh -o out_dir -p partition -f oks_file [-g group] [-v level] [-h]'
      echo ''
      echo 'Arguments/Options:'
      echo '   -o | --out output_directory          name of output directory contating merged oks files'
      echo '   -p | --partition partition_name      name of partition'
#      echo '   -f | --file oks_file                 name of OKS configuration'
      echo '   -g | --group group_name              if defined, add write permission on created files for such group'
      echo "   -v | --verbose level                 set level for verbose output passed to rOKS [default=${verbose}]"
      echo '   -h | --help                          print this message'
      echo ''
      echo 'Description:'
      echo '   Loads OKS configuration and creates OKS schema and data files contating all objects referenced by'
      echo '   partition object. The names of created files: RunNumber.PartitionName.TimeStamp.[schema|data].xml'
      echo '   Such file will be used and removed after archiving by the oks2coral running in initial partition.'
      echo ''
      exit 0
      ;;

    *)
      echo "Unexpected parameter '$1', type --help, exiting..."
      exit 1
      ;;

  esac
  shift
done

###############################################################################

if [ -z "${out_dir}" ]
then
  echo "ERROR: output directory is not defined, check -o command line option"
  exit 2
fi

if [ -z "${partition_name}" ]
then
  echo "ERROR: partition name is not defined, check -p command line option"
  exit 2
fi

#if [ -z "${file}" ]
#then
#  echo "ERROR: database file is not defined, check -f command line option"
#  exit 2
#fi

###############################################################################

# CLEAN RunParams.ConfigVersions possibly restored from IS server backup

echo "is_rm -p ${partition_name} -n RunParams -r ConfigVersions"
is_rm -p ${partition_name} -n RunParams -r ConfigVersions

###############################################################################

# GET RUN NUMBER

run_number='0'

echo "is_ls -p ${partition_name} -n RunParams -v -N -R SOR_RunParams.*"
is_ls -p ${partition_name} -n RunParams -v -N -R SOR_RunParams.* > ${is_ls_out}

if [ $? -eq 0 ]
then
  run_number=`cat ${is_ls_out} | grep run_number | sed 's/run_number//g;s/ //g'`
  if [ -z ${run_number} ]
  then
    echo 'ERROR: is_ls returned unexpected result:'
    echo '*********************************************'
    cat ${is_ls_out}
    echo '*********************************************'
    echo 'Will use run number = 0'
    run_number='0'
  else
    echo "Run number = ${run_number}"
  fi
  rm -f ${is_ls_out}
else
  echo 'is_ls has failed; will use run number = 0'
  run_number='0'
fi

###############################################################################

# prepare query
query=`echo '(all (object-id "XXX" =))' | sed "s/XXX/$partition_name/"`

# take a timestamp (in case of equal run numbers)
ts=`date '+%y%m%d%H%M%S'`

# out schema and data files
data_file="${out_dir}/${run_number}.${partition_name}.${ts}.data.xml"
schema_file="${out_dir}/${run_number}.${partition_name}.${ts}.schema.xml"

# merge configuration files into above two files
#echo "oks_merge -c Partition -q "$query" -r 1000 -s ${schema_file} -o ${data_file} ${file}"
#oks_merge -c Partition -q "$query" -r 1000 -s ${schema_file} -o ${data_file} ${file}
echo "rdb_admin -p ${partition_name} -d RDB -e ${schema_file} ${data_file}  Partition "$query" 1000"
rdb_admin -p ${partition_name} -d RDB -e ${schema_file} ${data_file}  Partition "$query" 1000

if [ $? -eq 0 ]
then

  if [ ! -z "${group}" ]
  then
    echo 'Change group write permissions...'
    echo "chmod g+w ${schema_file} ${data_file}"
    chmod g+w ${schema_file} ${data_file}
    echo "chgrp ${group} ${schema_file} ${data_file}"
    chgrp ${group} ${schema_file} ${data_file}
  fi

  echo "ls -la ${schema_file} ${data_file}"
  ls -la ${schema_file} ${data_file}
else
  echo "ERROR: rdb_admin has failed, cannot create ${data_file} to be used by the oks archival applications"
  echo "rm -f ${schema_file} ${data_file}"
  rm -f ${schema_file} ${data_file}
  exit 1
fi

exit 0
```

#### `doc/RELEASE_NOTES.tdaq-01-06-00.html` (text-extracted)

```text
New Page 1

The oks2coral is used to archive configuration databases and stores 
reference of used configuration into conditions database. The application should 
be integrated with online setup segment to be started automatically at the 
moment, when new run is configured or updated in running state.

The Sequence of Actions

After the oks2coral application is running, it does the following list of 
actions:

 Reads configuration data from oks xml files using oks library.

 Gets head version of configuration data from archive using roks library.

 Compares above configuration data. If they are different, the oks2coral 
 tries to create new incremental version relative to last base version using 
 roks library.

 Puts newly created or last data version of configuration data from 
 archive into conditions database using CDI via information service.

Integration with Online Setup

The oks2coral is a resource application in the online segment. To disable the 
archiving of configuration data (e.g. for test purposes) put oks2coral resource 
into disabled relationship of the partition object.

Request for New Base Version

The oks2coral application creates incremental version. In case if the 
configuration databases have been significantly modified comparing with base 
version (i.e. size of changes exceeds some threshold) or the configuration 
schema has been modified, the oks2coral reports the problem via ers. In such 
case it is necessary to create new base version using utility 
oks-create-new-base-version.sh from oks package.

Reference in the Conditions Database

The oks2coral publishes reference on archived version in the 
Runparams.ConfigVersions object, that can be inspected at running state using 
Information Service monitors.
```
#### `doc/RELEASE_NOTES.tdaq-01-07-00.html` (text-extracted)

```text
New Page 1

 add hard limit on number of new rows for creation of incremental 
 version:
 the limit is defined by -X command line option (do not mix up 
 with old lower case -x option used for soft limit); if it is not 
 provided, then the limit is ignored

 when the limit is achieved, no archiving is performed and oks2coral 
 reports fatal ERS error

 when soft limit (defined by -x command line option) is exceeded, 
 oks2coral issues ERS error to inform shifter about necessity to create new 
 base version and performs archiving
```
#### `doc/RELEASE_NOTES.tdaq-01-08-03.html` (text-extracted)

```text
Untitled 1

The oks2coral is permanently running in the initial partition. When a new run 
is started, the oks2coral_mk_tmp_file.sh script merges used oks configuration 
files into single schema and data files and puts them into directory defined by 
the OKS2CORAL_TMP_DIR config parameter. The oks2coral binary is running in the 
initial partition and periodically scans this directory looking for new .data.xm 
files. When new file is found, it tries to archive it and in case of success 
removes the data file and corresponding schema one. If found file is bad (e.g. 
cannot be loaded, cannot find corresponding partition object), the oks2coral 
ignores it in future scans. If a file cannot be archived because of the RDBMS / 
CORAL problems (timeouts, quota, wrong OKS schema in HEAD version), the 
oks2coral will try to archive it again with low frequency (once per several tens 
of minutes); it may succeed in future if one fixes the problem without 
restarting the oks2coral.
```
#### `doc/RELEASE_NOTES.tdaq-01-08-04.html` (text-extracted)

```text
Untitled 1

Several bug fixes:

 Ignore OKS lock files appeared in the cache directory

 Skip locked files appeared in the cache directory during work of
oks_merge (i.e. only save non-locked files)

 Properly close connection in case of exceptions to avoid many
simultaneously open connections

 Properly manage situation, when the cache directory is a soft link

 oks_merge reports any errors using ERS; for the moment this is
the
only possibility to notify shifter, if files to be archived cannot be
created in cache directory

 Fix lost-precision bug when archive double number (avoid
unexpected intermediate conversion of them to float type by CORAL)

 Use new schema version if it appears while oks2coral is running
```
#### `doc/RELEASE_NOTES.tdaq-01-09-01.html` (text-extracted)

```text
New Page 1

Changes in the oks2coral_mk_tmp_file.sh script 

 fix bug appearing because the RunParams.ConfigVersions IS info is
restored between runs from the IS server backup. Now the
RunParams.ConfigVersions is always clean by the script using is_rm
utility

 use new rdb_admin instead of oks_merge:

 the files merged by RDB server guaranty they are exactly the
same as used for data taking run

 remove useless option -f (the rdb_server RDB is used to produce
merged files)
```
#### `doc/RELEASE_NOTES.tdaq-02-00-00.html` (text-extracted)

```text
Untitled 1

 Migrate to deSEALed
version of CORAL.
```

