# Source 4: DUNE DAQ ReadTheDocs mirrors (dune-daq-sw.readthedocs.io)

> Generated 2026-08-08 by live fetch of https://dune-daq-sw.readthedocs.io (markdown rendering of the pages).
> All four pages below were successfully fetched and are reproduced in full (markdown-rendered, navigation sidebar trimmed to the package list).

## Access status summary

| URL | Status |
|-----|--------|
| https://dune-daq-sw.readthedocs.io/en/latest/ | OK (fetched, see "DUNE DAQ Software Documentation Home" below) |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/ | OK (fetched, see "DBE (DataBase Editor) package" below) |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/dbe/ | OK (fetched, see "The OKS database editor: dbe_main" below) |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/schemaeditor/ | OK (fetched, see "The OKS schema editor: schemaeditor" below) |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/daqconf/ | OK (fetched, see "Configuration creation, visualization and manipulation" below) |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/ | **404 — page no longer exists** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/+the+dal+package/README.html | **404** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/+the+dal+package/DalReader.html | **404** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/+the+dal+package/DalWriter.html | **404** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/+the+dal+package/ConfigVersion.html | **404** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/+the+dal+package/DAL-schema.html | **404** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/+the+dal+package/DAL-test-schema.html | **404** |
| https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/RELEASE_NOTES.html | **404** |

The `dal` package documentation has been removed from the DUNE DAQ docs site (the `packages/dal/` directory no longer exists; links in the dal repo's own README point to these dead URLs). The docs page for the *dbe* package (GUI interface to OKS) and for *daqconf* (the OKS database generation/manipulation scripts) are still live and are reproduced in full below. The dbe/dbe_main + dbe/schemaeditor pages were last updated by Gordon Crone (2026-01-13 / 2026-04-10); the daqconf page by Henry Wallace (2026-02-04).

---

# DUNE DAQ Software Documentation Home

(URL: https://dune-daq-sw.readthedocs.io/en/latest/ — full page content fetched and preserved; the package navigation list is given in the source above; key OKS-related entries: `Control` → `confmodel` ("A core schema for DAQ configuration"), `daqconf` ("application to read out Felix data and store it in HDF5 files on disk" — sic), `dbe` ("A GUI interface for the OKS-based configuration design"), plus `runconftools` ("Constructs configurations from a base of ehn1 configurations").)

# DBE (DataBase Editor) package

(URL: https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/)

The DBE package provides a GUI interface to the OKS suite, allowing you to edit both schema files and data files.

While DBE was [originally written as part of the ATLAS TDAQ effort](https://gitlab.cern.ch/atlas-tdaq-software/dbe.git), it has been modified and enhanced to build within the DUNE DAQ framework. To get started working with DBE, you'll need to run `spack load dbe`. This command is needed since dbe is not loaded by default when setting up the release since loading in `dbe` will cause emacs to no longer work in the terminal, an undesirable side effect developers don't want to have to experience whenever they set up a work area for reasons unrelated to dbe.

See the individual documents [dbe.md](https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/dbe/) and [schemaeditor.md](https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/schemaeditor/) for more information on running the editors.

# The OKS database editor: `dbe_main`

(URL: https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/dbe/ — full text reproduced below)

## Prerequisite

Before running either `dbe` or `schemaeditor` you must load the dbe spack package with `spack load dbe`. This can have unwanted side effects like running the wrong version of Python due to spack messing with your PATH and LD_LIBRARY_PATH. To avoid this, keep your editing sessions in a different window to your normal development or create an alias /shell function like:

```
function dbe_main () 
{ 
    bash -c "spack load dbe; command dbe_main $@"
}
```

## Starting the editor

Just running the command `dbe_main` will bring up the database editor with no database loaded. You can then open an existing database or create a new database from the items on the File menu or the tool-bar. If you want to specify an existing database on the command line, you must include the `-f` option before the name of the file. File names not beginning with '/' are taken to be relative to first the current directory, then each member of the list in `DUNEDAQ_DB_PATH` until a match is found.

## Structure of the editor

The main window below the tool-bar is initially split into 3 main parts, the `Class View` (1), the `Table View` (2) and the `Info Tabs`(3). The `Class View` and the `Info Tabs` can be undocked and moved out of the main window. Each of the views can also be enabled or disabled from the `View` menu.

## Navigating with the `Class view` (1)

The `Class View` is a dock-able widget originally on the left of the main window. The `Class View` is a tree which displays a list of class names and the number of objects of that class that exist in the database. Where the number of objects of a class is non-zero, the item can be expanded to display the list of objects. Further, if an object has relationships to other objects, the object can be expanded to show the list of relationships which in turn can be expanded to list the objects they are referencing.

- Activating a class name will display all instances of the class in the current `Table View`.
- Activating an instance in the `Tree view` will open the `Object Editor` to edit that instance.

### Abstract classes

Abstract classes are usually shown in grey on the `Class View` and are not selectable. If you want to see objects of all the subclasses of an abstract class, you can check the `Enable abstract classes` check box. With this selected, the abstract classes become selectable and activating them will show all instances of of all subclasses in the `Table View`. **Beware** the column headings are taken from the base class and derived classes may have more attributes/resources or a different ordering.

### Tooltips

Tooltips show the descriptions of the classes (assuming they have one).

### Filtering the view

To filter the list of classes to see just a subset that you are interested in, there is a text entry field at the bottom of the `Class View` where you can enter a regular expression to be matched against the class names. The matching can be done on class name or object name and case sensitive or not according to the settings of the check box and combo box just above the text input.

For example to find all objects including 'ers' in their name, enter 'ers' in the search box and select `Search by Object` from the combo box above it.

## Using the `Table view` (2)

The `Table View` area is a set of tabs which display the attributes and relationships of objects in the database. A new tab can be opened by selecting the '+' in the top left corner.

The content of a tab is selected from the `Class View` widget. Activating a class name will add all instances of that class to the current `Table View` tab. Activating individual instances will add only those selected to the tab. Instances can also be dragged from the `Class View` and dropped onto the `Table View`.

Attributes which are set to their default values are marked with a coloured background.

- Activating a row in the `Table View` will open the `Object Editor` on that instance.
- Double clicking on an attribute will allow editing of the attribute directly in the cell
- Double clicking on a relationship will pop up a dialogue box allowing selection of objects of the correct type.

### Filtering the view

Like the `Class View`, there is an edit box for an object name filter to limit the display to only matching objects.

### Context menu

The `Table view` context menu gives you several options, allowing you to find all objects that refer to the current object, find an object within the current view by name, copy edit or delete the current object.

## The `Info Tabs` (3)

The `Info Tabs` section consists of 3 tabs, the `File View`, the `Undo` control and the `Commits log`.

### The `File View` tab

The `File View` lists all the loaded data files along with their read/write access and modified status. The list of files included by the currently selected file can be updated by pulling up the include file editor by selecting `Add/Remove Files` from the context menu. A window showing information about the file, including a list of objects defined in it, can be activated by selecting `File information` from the context menu or by double-clicking on the appropriate row.

#### File Information window

The File Information window has 3 panels showing a list of all the objects in the file and lists of all the schema and data files that this file includes. The schema and data file panels have buttons allowing you to add further includes and this functionality is also available via the context menu. This is a simpler interface to updating the list of includes than using the `Include file editor`.

If the file contains any objects with relationships to objects in files that are not included or the schema file in which the class is defined is not loaded, a 4th panel with warning messages will be shown.

Both the schema file and data file panels have an 'Add' button allowing more includes to be added. These will bring up a standard file selection dialogue with the left-hand column populated by the paths from `DUNEDAQ_DB_PATH`.

### The `Undo` tab

The `Undo` tab lists all the modifications that have been made since the last commit to the database. You can go back to any point in the history by selecting the line above the change you want to revert. Apart from navigating the Undo list with the mouse or keyboard, there are also buttons on the tool-bar to undo/redo changes.

## Creating new objects

New objects can be created by from the `Class View` panel by using the context menu or the short cut `Ctrl-N` (also from the context menu in an active `Table View` tab). This brings up the `Object Editor` for the selected class. Before you can set the values of the attributes and relationships, you have to set the UID and select the file to store the object in.

New objects can also be created from the context menu in the `Table View`, either an empty one or a copy of an existing object.

## Renaming objects or moving to a different file

To rename or move an object, bring up the object editor for that object and use the buttons in the top right-hand corner.

## Finding what uses a specific object

To find all objects that refer to an object, first select the object in the table view. Then use one of the `Referenced By` items on the context menu. This will pop up a new window showing a class tree of all the objects that refer to it.

## Changing values in multiple objects in one go (batch changes)

Occasionally, you may need to change the value of the same attribute across many objects. Hidden away on the `Edit` menu are two batch change items to do this. `Batch Change` and `Batch Change Table`

- `Batch Change` allows you to change attributes/relationships of all objects of a class with a UID matching an expression.
- `Batch Change Table` allows you to change attributes/relationships of objects in the current `Table View`.

Both menu items will pop up dialogue boxes with both attributes and relationship sections. You have to select the appropriate check-box to determine which you are changing.

`Batch Change Table` only allows you to set a new value for all items in the table.

`Batch Change` is more flexible in that it allows you to filter on the current values of attributes/relationships and apply new values for only matching objects. In the example screen-shot shown above, we changed the `request_handler` relationship for all `DataHandlerConf` objects whose `template_for` attribute started with 'FD'.

# The OKS schema editor: `schemaeditor`

(URL: https://dune-daq-sw.readthedocs.io/en/latest/packages/dbe/schemaeditor/ — full text reproduced below)

## Prerequisite

Before running either `schemaeditor` or `dbe` you must load the dbe spack package with `spack load dbe`. This can have unwanted side effects like running the wrong version of Python due to spack messing with your PATH and LD_LIBRARY_PATH. To avoid this, keep your editing sessions in a different window to your normal development or create an alias /shell function like:

```
function schemaeditor () 
{ 
    bash -c "spack load dbe; command schemaeditor $@"
}
```

## Starting the editor

Just running the command `schemaeditor` will bring up the schemaeditor with no schema files loaded. You can then either open an existing schema file `File -> Open Schema` (or Ctrl+O) or create a new empty schema file with `File->Create new schema` (or Ctrl+N).

To start with an existing schema file, use the `-f` option e.g. `schemaeditor -f schema/appmodel/application.schema.xml`

## Structure of the editor

The main window is initially split into 3 main parts, the `Class View` (1), the `SchemaView Tab area` (2) and the `Info Tabs` (3) with a menu bar and tool-bar at the top and a staus bar at the bottom. The `Class View` and the `Info Tabs` can be undocked and moved out of the main window. Each of the views can also be enabled or disabled from the `View` menu.

After adjusting the layout, the current layout can be saved at any point by selecting the `Save layout` option from the `Settings` menu. You can also use this menu to restore the default layout or the last layout you saved.

The Settings menu also has a `Preferences` option which will open a window where you can set fonts colours and default options for schema view diagram tabs.

## Setting the 'Active' schema file

All new classes are created in the active schema file. This will initially be the file you loaded or created above unless the loaded file is read-only or locked by another process. To make another file the active schema file, use the context menu in the files tab (right-click).

_NB:_ You cannot add new classes unless you have made a schema file 'Active'.

## Handling include files

Most schema files will want to include at least the core dunedaq schema (dunedaq.schema.xml) from confmodel. To add an include to the currently active schema file, either `File->Show schema file info`(I) or right click on the name of the schema file in the File panel. This will bring up a dialog box showing information about the selected or active schema file with a list of included files and the classes contained in this file. This dialog box has a button for adding include files and if any of the classes refer to classes that are not contained in any included file another button to automatically add all the required schema files. The `Add Include File` button brings up a standard open file dialog with all the elements of `DUNEDAQ_DB_PATH` in the sidebar (use the tooltips to distinguish among the multiple `share` entries).

A list of which classes are in a given schema file can also be seen by opening a file info window from the file tab conext menu (or for the active file Ctl-I). This class list has a context menu allowing adding, editing and removing classes.

## Saving files

To save all modified schema files, `File->Save Schema` (Ctrl+S). To save only a single file, use the context menu in the File tab. This also allows you to save files that have not been updated (sometimes useful to ensure proper formatting of files edited outside of the schemaeditor).

## Editing classes

To edit a class, activate (double click or select and hit enter) the class name in the `classes` panel, double click on the class in the `class view` panel or select the edit option from the context menu in either panel. It is possible to open the class editor for a read only class from the `classes` panel but the editor will not allow you to make any changes.

## Adding new classes

To add a new class Ctrl+A anywhere will bring up the new class dialogue box. From here you can define the attributes and relationships of your new class and set its superclass inheritance from the list of existing classes.

Selecting "Add New Class" from the context menu of the class list in a file info window will add a new class to that file, automatically switching the 'active' file.

New classes can also be added from the context menu in the schema view tabs. This will place the new class on the schema diagram at the current cursor position.

## Moving classes between files

To move a class to a different file, open the class editor for the class and press the Move button near the top. Alternatively, from a file info window for the file that currently contains the class, select the class from the class list and activate the "Move Selected Class" item from the context menu. This will open a dialog box asking you to select the destination. Unfortunately, drag and drop between file info windows is not (yet) available.

## Schema diagrams

To create a class diagram of the defined classes, simply drag the classes you are interested in from the 'Class Name' list onto a schema view tab. Relationships and inheritance connections will be automatically drawn. By default, only the direct properties of the classes are shown. To display all properties, including those inherited from super-classes, the context menu in the schema view panel includes an option to toggle viewing inherited properties. The context menu on an individual class within the view allows the addition of all its parent/child/related classes to the view. They will all appear in the top left corner and will need to be moved to appropriate places one by one.

Multiple views of the schema can be created by selecting the "+" button next to the view tabs. A tab can be renamed by selecting the 'Name View' button on the toolbar. Tabs can be closed by selecting the cross on the top corner of the tab or with the short cut Ctl-W.

### Moving the diagram

To move the whole digram, move the mouse pointer to the point you want the current origin to move to and select `Move scene` from the context menu.

### Highlighting classes

Classes may be highlighted in different colors/fonts. The colors and fonts can be set from the `Preferences` item on the `Settings` menu.

#### Highlighting classes from the active schema file

The classes contained in the current schema fie can be highlighted by selecting this option from the context menu. This can be useful to see at a glance which classes are in which file. Changing the active file from the `File info` tab will change which classes are highlighted accordingly.

#### Highlighting selected class

The class under the cursor can be highlighted by selecting the appropriate item from the context menu.

### Tool-tips

Hovering the mouse over a class in the schema view will bring up a tool-tip with the description fields of the class and all its direct attributes, relationships and methods.

### View files

The current schema diagram can be saved from the 'Save View' or 'Save View as' buttons on the toolbar or printed via the 'Print View' button. These options also exist in the SchemaViews menu along with an option to export to an SVG file.

Views can be loaded from files by using the Ctl-V short cut or selecting 'Load View' from the SchemaViews menu. Views load into new tabs unless the current tab is empty.

### Notes

Notes can be added to the view by selecting 'Add note to view' from the context menu. Notes are currently written in very simple boxes with plain text. Line breaks should be added by hand.

## Keyboard short cuts

| Key   | Action                                | Notes                                                |
| ----- | ------------------------------------- | ---------------------------------------------------- |
| Ctl-A | Add new schema class                  | Only available when there is an 'Active' schema file |
| Ctl-N | Create New schema file                |                                                      |
| Ctl-O | Open new schema file                  |                                                      |
| Ctl-I | Open file info dialog for active file | Only available when there is an 'Active' schema file |
| Ctl-S | Save modified schema files            |                                                      |
| Ctl-V | Load View                             |                                                      |
| Ctl-K | Save View                             |                                                      |
| Ctl-E | Export View as SVG                    |                                                      |
| Ctl-P | Print View                            |                                                      |
| Ctl-W | Close View tab                        |                                                      |
| Ctl-Q | Quit                                  |                                                      |

# Configuration creation, visualization and manipulation (daqconf)

(URL: https://dune-daq-sw.readthedocs.io/en/latest/packages/daqconf/ — full text reproduced below)

This repository contains scripts for generating and manipulating OKS database files.

## Visualization tools

### `daqconf_inspector`

Commandline utility to visually inspect and verify configurations databases and the objects they contain. Documenation available here: packages/daqconf/Inspector/.

### `create_config_plot`

Commandline utility to generate a graphical flow diagram of a full configuration session or one of its applications or segments. Documentation available here: packages/daqconf/ConfigPlotting/.

## Manipulation Tools

### `oks_enable`

Add Resource objects to or remove from the `disabled` relationship of a Session

### `consolidate`

Merge the contents of several database files, putting all objects into a single output file. The output file's include list will contain the schema files included by the source databases (or their includes), but will not contain any object databases (the schema themselves).

### `consolidate_files`

Merge the contents of several database files, preserving included databases. Output file will contain only objects defined in files given on command line. The output files' include list will contain the schema files included by the source databases (or their includes), but will not contain any object databases (the schema themselves).

### `copy_configuration`

Copy the input file(s) to the specified directory, also moving any included files and updating include paths, to create a clone of the configuration databases.

### `get_apps`

Retrieve the DAQ applications defined in the given configuration

### `oks-format`

Ensure that database files are in the "DBE format", alphabetized and with correct spacing

### `oks_enable_tpg`

Enable or disable TPG for a Session's ReadoutApplications

### `validate`

Attempt to determine if a given Session configuration is valid and does not contain common errors

### `uniqueness_enforcer`

Attempt to enforce all object names to be unique in a configuration/folder of configurations.

### textual_dbe

Attempt to replicate OKS' Data Base editor within Python. Full details are here: packages/daqconf/TextualDBE/. Current implementation is very incomplete so use with caution.

## Generation Tools

### `createOKSdb`

A script that generates an 'empty' OKS database, just containging the include files for the core schema and any other schema/data files you specify on the commad line.

### `dromap2oks`

Convert a JSON readout map file from dunedaq v4 to an OKS file.

### `generate_readoutOKS`

Create an OKS configuration file defining ReadoutApplications for all readout groups defined in a readout map.

## Additional Python Utilities

### `assets.py`

Read the DUNE-DAQ asset file database and return a path to a referenced asset file

### `generate.py`

A collection of methods to generate segments and sessions.

### `generate_hwmap.py`

Create a set of DetectorToDaqConnection objects, GeoIDs, and streams for the given number of links and applications.

### `utils.py`

Utilities for parsing OKS databases. Currently contains an include file search routine.
