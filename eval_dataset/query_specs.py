"""
Curated shifter questions paired with their ground-truth OksQuery.

Every row is written against the schema in ``test_schema/xml`` and the objects
in ``test_data``, so ``build_dataset.py`` can prove two things before the row is
written out:

  1. the gold IR only names classes, attributes and relationships that really
     exist (schema validation), and
  2. the gold query really executes, so the row can carry its expected result
     set for execution-based scoring.

Difficulty follows the project specification's easy / medium / hard split:

  easy    one predicate: an attribute comparison, an object-id test, or a
          scope choice. Nothing nested.
  medium  boolean composition of predicates on one class, or a single
          relationship hop.
  hard    a relationship hop with structure inside it, nested hops, the
          universal ('all') quantifier, or a path query.

``constructs`` is the error-taxonomy axis: it lets a failure be attributed to
"got the regex comparator wrong" rather than to a single pass/fail number.
"""

from typing import Any, Dict, List, Optional

# -- IR constructors -------------------------------------------------------
def A(attribute: str, operator: str, value: str) -> Dict[str, Any]:
    return {"type": "attribute_compare", "attribute": attribute,
            "operator": operator, "value": value}


def OID(object_id: str) -> Dict[str, Any]:
    return {"type": "object_id", "operator": "=", "object_id": object_id}


def R(name: str, quantifier: str, expression: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "relationship", "name": name,
            "quantifier": quantifier, "expression": expression}


def AND(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "and", "operands": list(operands)}


def OR(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "or", "operands": list(operands)}


def NOT(operand: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "not", "operand": operand}


class Spec:
    """One evaluation row before the builder fills in the derived fields."""

    def __init__(self,
                 question: str,
                 target_class: str,
                 difficulty: str,
                 constructs: List[str],
                 expression: Optional[Dict[str, Any]] = None,
                 scope: str = "all",
                 note: str = "",
                 query_oks: Optional[str] = None,
                 ir_expressible: bool = True,
                 allow_empty: bool = False,
                 source_file: str = "test_schema/xml/core.schema.xml"):
        self.question = question
        self.target_class = target_class
        self.difficulty = difficulty
        self.constructs = constructs
        self.expression = expression
        self.scope = scope
        self.note = note
        self.query_oks = query_oks
        self.ir_expressible = ir_expressible
        self.allow_empty = allow_empty
        self.source_file = source_file

    @property
    def ir(self) -> Optional[Dict[str, Any]]:
        if self.expression is None:
            return None
        return {"scope": self.scope, "expression": self.expression}


CORE = "test_schema/xml/core.schema.xml"
TESTREPO = "test_schema/xml/test-repository.schema.xml"
DQM = "test_schema/xml/dqm.schema.xml"
MIG = "test_schema/xml/MonInfoGatherer.schema.xml"

SPECS: List[Spec] = [

    # ==================================================================
    # EASY -- single attribute comparison, one comparator each
    # ==================================================================
    Spec("Which IPC service applications expose the is/repository interface?",
         "IPCServiceApplication", "easy", ["attribute_compare", "eq", "string"],
         A("InterfaceName", "=", "is/repository"),
         note="Plain equality on a string attribute. Values are always quoted in the query text, "
              "whatever the attribute's declared type."),

    Spec("List the IPC service applications that are not is/repository servers.",
         "IPCServiceApplication", "easy", ["attribute_compare", "ne", "string"],
         A("InterfaceName", "!=", "is/repository"),
         note="'!=' is a distinct comparator token, not a negated '='."),

    Spec("Show me every application whose initialisation timeout is longer than 30 seconds.",
         "BaseApplication", "easy", ["attribute_compare", "gt", "numeric"],
         A("InitTimeout", ">", "30"),
         note="InitTimeout is u32, so the comparison is numeric even though the value is written "
              "as a quoted string."),

    Spec("Which applications initialise in 30 seconds or less?",
         "BaseApplication", "easy", ["attribute_compare", "le", "numeric"],
         A("InitTimeout", "<=", "30"),
         note="'<=' on the same u32 attribute. Objects that store no InitTimeout fall back to the "
              "schema init-value of 0, which is why the result set is large."),

    Spec("Find applications that need at least a minute to start up.",
         "BaseApplication", "easy", ["attribute_compare", "ge", "numeric"],
         A("InitTimeout", ">=", "60"),
         note="'at least' maps to '>=', not '>'. Boundary handling is a common translation error."),

    Spec("Which applications have an exit timeout under 5 seconds?",
         "BaseApplication", "easy", ["attribute_compare", "lt", "numeric"],
         A("ExitTimeout", "<", "5"),
         note="'under' is strict '<'.", allow_empty=True),

    Spec("Which applications give up after more than 5 seconds when shutting down?",
         "BaseApplication", "easy", ["attribute_compare", "gt", "numeric"],
         A("ExitTimeout", ">", "5")),

    Spec("Which applications are configured to restart if they exit unexpectedly?",
         "BaseApplication", "easy", ["attribute_compare", "eq", "enum"],
         A("IfExitsUnexpectedly", "=", "Restart"),
         note="Enum value from the range Error,Ignore,Restart,Handle. Enum values are quoted "
              "strings in the query, same as any other value."),

    Spec("Which applications ignore an unexpected exit instead of raising an error?",
         "BaseApplication", "easy", ["attribute_compare", "eq", "enum"],
         A("IfExitsUnexpectedly", "=", "Ignore")),

    Spec("Which applications do not treat a failed start as an error?",
         "BaseApplication", "easy", ["attribute_compare", "ne", "enum"],
         A("IfFailsToStart", "!=", "Error")),

    Spec("List the applications that can be restarted while a run is ongoing.",
         "BaseApplication", "easy", ["attribute_compare", "eq", "bool"],
         A("RestartableDuringRun", "=", "1"),
         note="bool attributes are stored as 1/0 in the data files; the predefined OKS range for "
              "bool is true,false."),

    Spec("Which applications have logging turned off?",
         "BaseApplication", "easy", ["attribute_compare", "eq", "bool"],
         A("Logging", "=", "0"), allow_empty=True,
         note="Logging defaults to true in the schema, so a false hit means an explicit override."),

    Spec("Find the binary called pmgserver.",
         "Binary", "easy", ["attribute_compare", "eq", "string"],
         A("BinaryName", "=", "pmgserver")),

    Spec("Which binaries have a name starting with rdb?",
         "Binary", "easy", ["attribute_compare", "regex"],
         A("BinaryName", "~=", "rdb.*"),
         note="'~=' is a boost::regex full match, so a prefix search needs the trailing '.*'. "
              "There is no glob operator in OKS."),

    Spec("Show binaries whose name ends in _main.",
         "Binary", "easy", ["attribute_compare", "regex"],
         A("BinaryName", "~=", ".*_main"),
         note="Suffix search: anchor the front with '.*' because the match is whole-value."),

    Spec("Which binaries mention monitoring in their description?",
         "Binary", "easy", ["attribute_compare", "regex"],
         A("Description", "~=", ".*[Mm]onitoring.*"),
         note="Substring search needs '.*' on both sides under regex_match semantics."),

    Spec("Which programs have no help URL recorded?",
         "ComputerProgram", "easy", ["attribute_compare", "eq", "string", "empty-value"],
         A("HelpURL", "=", ""),
         note="Comparing against the empty string is how 'unset' is expressed for a string "
              "attribute whose init-value is empty."),

    Spec("List binaries documented on the CERN TWiki.",
         "Binary", "easy", ["attribute_compare", "regex"],
         A("HelpURL", "~=", "https://twiki\\.cern\\.ch/.*"),
         note="The dot in a hostname must be escaped, otherwise it matches any character."),

    Spec("Which scripts run under bash?",
         "Script", "easy", ["attribute_compare", "eq", "string"],
         A("Shell", "=", "bash")),

    Spec("Which scripts are not java-based?",
         "Script", "easy", ["attribute_compare", "ne", "string"],
         A("Shell", "!=", "java")),

    Spec("Find the software repository named Online.",
         "SW_Repository", "easy", ["attribute_compare", "eq", "string"],
         A("Name", "=", "Online")),

    Spec("Which software repositories install under the LCG area?",
         "SW_Repository", "easy", ["attribute_compare", "regex"],
         A("InstallationPath", "~=", "\\$\\{LCG_INST_PATH\\}.*"),
         note="'$' and '{' are regex metacharacters and have to be escaped to match a literal "
              "shell variable reference."),

    Spec("Which repositories publish their installation path through TDAQ_INST_PATH?",
         "SW_Repository", "easy", ["attribute_compare", "eq", "string"],
         A("InstallationPathVariableName", "=", "TDAQ_INST_PATH")),

    Spec("Find the environment variable definition for TDAQ_IPC_TIMEOUT.",
         "Variable", "easy", ["attribute_compare", "eq", "string"],
         A("Name", "=", "TDAQ_IPC_TIMEOUT")),

    Spec("Which environment variables belong to the ERS family?",
         "Variable", "easy", ["attribute_compare", "regex"],
         A("Name", "~=", "TDAQ_ERS_.*")),

    Spec("Which variables are set to the empty value?",
         "Variable", "easy", ["attribute_compare", "eq", "string", "empty-value"],
         A("Value", "=", ""), allow_empty=True),

    Spec("Which variables point somewhere under /eos?",
         "Variable", "easy", ["attribute_compare", "regex"],
         A("Value", "~=", "/eos/.*")),

    Spec("List the platform tags built with gcc13 in optimised mode.",
         "Tag", "easy", ["attribute_compare", "eq", "enum"],
         A("SW_Tag", "=", "gcc13-opt"),
         note="Scope 'all' also picks up TagMapping, which is a subclass of Tag."),

    Spec("Which tags target the aarch64 architecture?",
         "Tag", "easy", ["attribute_compare", "regex", "enum"],
         A("HW_Tag", "~=", "aarch64-.*"),
         note="A regex comparator works on an enum attribute; the enumerator name is matched as "
              "a string."),

    Spec("Which tags are debug builds?",
         "Tag", "easy", ["attribute_compare", "regex", "enum"],
         A("SW_Tag", "~=", ".*-dbg")),

    Spec("Show the tags that are not CentOS 7 builds.",
         "Tag", "easy", ["attribute_compare", "ne", "enum"],
         A("HW_Tag", "!=", "x86_64-centos7")),

    Spec("Which class-level tests time out after more than 15 seconds?",
         "Test4Class", "easy", ["attribute_compare", "gt", "numeric"],
         A("Timeout", ">", "15"), source_file=TESTREPO),

    Spec("Which class-level tests are diagnostics?",
         "Test4Class", "easy", ["attribute_compare", "eq", "enum", "multi-value"],
         A("Scope", "=", "diagnostics"), source_file=TESTREPO,
         note="Scope is a multi-value enum, so the comparison succeeds when any element of the "
              "list equals the value."),

    Spec("Which class-level tests are complex, meaning complexity above 1?",
         "Test4Class", "easy", ["attribute_compare", "gt", "numeric"],
         A("Complexity", ">", "1"), source_file=TESTREPO),

    Spec("Which tests apply to the Computer class?",
         "Test4Class", "easy", ["attribute_compare", "eq", "class-type"],
         A("ClassName", "=", "Computer"), source_file=TESTREPO,
         note="ClassName has OKS type 'class': the value is a class name, compared as a string."),

    Spec("Which tests are interactive?",
         "Test4Class", "easy", ["attribute_compare", "eq", "bool"],
         A("Interactive", "=", "1"), source_file=TESTREPO, allow_empty=True),

    Spec("Which software resources allow only one copy per partition?",
         "RM_SW_Resource", "easy", ["attribute_compare", "eq", "numeric"],
         A("MaxCopyPerPartition", "=", "1")),

    Spec("Which resources allow more than 100 copies in total?",
         "RM_SW_Resource", "easy", ["attribute_compare", "gt", "numeric"],
         A("MaxCopyTotal", ">", "100")),

    Spec("Which data-quality outputs use the libdqmf_io shared library?",
         "DQOutput", "easy", ["attribute_compare", "eq", "string"],
         A("Library", "=", "libdqmf_io.so"), source_file=DQM),

    Spec("Which data-quality inputs are dummies?",
         "DQInput", "easy", ["attribute_compare", "regex"],
         A("Name", "~=", "Dummy.*"), source_file=DQM),

    Spec("Find the run-control application whose object id is RootController.",
         "RunControlApplication", "easy", ["object_id"],
         OID("RootController"),
         note="An object-id test is cheaper than a non-indexed attribute scan and it works even "
              "for objects that carry no searchable attribute."),

    Spec("Look up the partition object called initial.",
         "Partition", "easy", ["object_id"],
         OID("initial")),

    Spec("Fetch the online segment named setup.",
         "OnlineSegment", "easy", ["object_id"],
         OID("setup")),

    Spec("Which run-control applications wait longer than 20 seconds for a transition?",
         "RunControlApplication", "easy", ["attribute_compare", "gt", "numeric"],
         A("ActionTimeout", ">", "20")),

    Spec("Which run-control applications never probe, meaning their probe interval is zero?",
         "RunControlApplication", "easy", ["attribute_compare", "eq", "numeric"],
         A("ProbeInterval", "=", "0")),

    Spec("Which run-control applications control TTC partitions?",
         "RunControlApplication", "easy", ["attribute_compare", "eq", "bool"],
         A("ControlsTTCPartitions", "=", "1"), allow_empty=True),

    Spec("Look at the IPCServiceApplication class only, not its subclasses: which ones serve rdb/cursor?",
         "IPCServiceApplication", "easy", ["scope-this", "attribute_compare", "eq"],
         A("InterfaceName", "=", "rdb/cursor"), scope="this",
         note="'this' restricts the search to the named class; 'all' would also scan its "
              "subclasses. The distinction matches the Data Editor's 'Search in subclasses' toggle."),

    Spec("Across every kind of application, including subclasses, which ones use the rc/commander interface?",
         "RunControlApplicationBase", "easy", ["scope-all", "attribute_compare", "eq"],
         A("InterfaceName", "=", "rc/commander"),
         note="Scope 'all' on an abstract base class is the usual way to ask a question about a "
              "whole family of applications at once."),

    Spec("Restricting the search to the Tag class itself, which tags use gcc11-opt?",
         "Tag", "easy", ["scope-this", "attribute_compare", "eq", "enum"],
         A("SW_Tag", "=", "gcc11-opt"), scope="this",
         note="Contrast with scope 'all', which would also return TagMapping objects."),

    Spec("Which monitoring gatherer applications run more than one instance?",
         "MIGApplication", "easy", ["attribute_compare", "gt", "numeric"],
         A("Instances", ">", "1"), source_file=MIG, allow_empty=True),

    Spec("Which gatherer applications are pinned to the first host?",
         "MIGApplication", "easy", ["attribute_compare", "eq", "enum"],
         A("RunsOn", "=", "FirstHost"), source_file=MIG,
         note="Careful: on MIGApplication 'RunsOn' is an enum attribute, while on Application it "
              "is a relationship to Computer. The same name means different things on different "
              "classes, which is exactly why schema retrieval has to be class-aware."),

    Spec("Which gatherer configurations match every provider?",
         "MIGConfiguration", "easy", ["attribute_compare", "eq", "string"],
         A("ProviderRegExp", "=", ".*"), source_file=MIG,
         note="The value here is itself a regex stored in the configuration, but the query "
              "comparator is plain equality on the stored text."),

    Spec("Which test executables take longer than 2 seconds to initialise?",
         "Executable", "easy", ["attribute_compare", "gt", "numeric"],
         A("InitTimeout", ">", "2"), source_file=TESTREPO),

    Spec("Which test executables run on the object's own host?",
         "Executable", "easy", ["attribute_compare", "eq", "string"],
         A("Host", "=", "#this.UID"), source_file=TESTREPO,
         note="'#this.UID' is a DAL substitution token stored verbatim in the attribute, so it is "
              "compared literally."),

    # ==================================================================
    # MEDIUM -- boolean composition, single relationship hop
    # ==================================================================
    Spec("Which applications initialise in 30 seconds and exit within 5?",
         "BaseApplication", "medium", ["and", "attribute_compare"],
         AND(A("InitTimeout", "=", "30"), A("ExitTimeout", "=", "5")),
         note="'and' needs two or more operands; the scope token appears once, at the top."),

    Spec("Which applications initialise between 30 and 60 seconds inclusive?",
         "BaseApplication", "medium", ["and", "range", "numeric"],
         AND(A("InitTimeout", ">=", "30"), A("InitTimeout", "<=", "60")),
         note="A closed interval is two comparators on the same attribute joined by 'and'. When "
              "the class has an index on that attribute, OKS resolves it as a single two-sided "
              "index lookup."),

    Spec("Which applications either restart or are ignored when they exit unexpectedly?",
         "BaseApplication", "medium", ["or", "attribute_compare", "enum"],
         OR(A("IfExitsUnexpectedly", "=", "Restart"), A("IfExitsUnexpectedly", "=", "Ignore"))),

    Spec("Which applications are not restartable during a run?",
         "BaseApplication", "medium", ["not", "attribute_compare", "bool"],
         NOT(A("RestartableDuringRun", "=", "1")),
         note="'not' takes exactly one operand. Expressing this as ('RestartableDuringRun' '0' =) "
              "is also correct here but changes the treatment of unset values."),

    Spec("Which applications log their output but still ignore a startup failure?",
         "BaseApplication", "medium", ["and", "bool", "enum"],
         AND(A("Logging", "=", "1"), A("IfFailsToStart", "=", "Ignore"))),

    Spec("Which IPC service applications serve rdb but are not the writer?",
         "IPCServiceApplication", "medium", ["and", "regex", "ne"],
         AND(A("InterfaceName", "~=", "rdb/.*"), A("InterfaceName", "!=", "rdb/writer"))),

    Spec("Which run-control applications have a long action timeout and still probe regularly?",
         "RunControlApplication", "medium", ["and", "numeric"],
         AND(A("ActionTimeout", ">=", "20"), A("ProbeInterval", ">", "0"))),

    Spec("Which run-control applications either ignore errors or publish full statistics?",
         "RunControlApplication", "medium", ["or", "enum", "numeric"],
         OR(A("IfError", "=", "Ignore"), A("FullStatisticsInterval", ">", "0"))),

    Spec("Which binaries have a description but no help URL?",
         "Binary", "medium", ["and", "ne", "eq"],
         AND(A("Description", "!=", ""), A("HelpURL", "=", ""))),

    Spec("Which programs are neither documented on TWiki nor on the ATLAS info site?",
         "ComputerProgram", "medium", ["not", "or", "regex"],
         NOT(OR(A("HelpURL", "~=", "https://twiki\\.cern\\.ch/.*"),
                A("HelpURL", "~=", "http://atlasinfo\\.cern\\.ch/.*"))),
         note="'neither A nor B' is a 'not' wrapped around an 'or', not two separate queries."),

    Spec("Which binaries pass the partition on the command line, either with -p or through the environment?",
         "Binary", "medium", ["or", "regex"],
         OR(A("DefaultParameters", "~=", ".*-p env\\(TDAQ_PARTITION\\).*"),
            A("DefaultParameters", "~=", ".*\\$\\{TDAQ_PARTITION\\}.*"))),

    Spec("Which tags are optimised builds on x86_64?",
         "Tag", "medium", ["and", "enum", "regex"],
         AND(A("HW_Tag", "~=", "x86_64-.*"), A("SW_Tag", "~=", ".*-opt"))),

    Spec("Which tag mappings are for EL9 but not the debug flavour?",
         "TagMapping", "medium", ["and", "regex", "ne"],
         AND(A("HW_Tag", "~=", ".*-el9"), A("SW_Tag", "!=", "gcc13-dbg"))),

    Spec("Which class-level tests are quick, under 15 seconds, and non-interactive?",
         "Test4Class", "medium", ["and", "numeric", "bool"],
         AND(A("Timeout", "<", "15"), A("Interactive", "=", "0")), source_file=TESTREPO),

    Spec("Which class-level tests are either preconditions or functional checks?",
         "Test4Class", "medium", ["or", "enum", "multi-value"],
         OR(A("Scope", "=", "precondition"), A("Scope", "=", "functional")), source_file=TESTREPO),

    Spec("Which class-level tests should not be repeated when the result is unresolved and are not diagnostics?",
         "Test4Class", "medium", ["and", "not", "bool", "enum"],
         AND(A("RepeatIfUnresolved", "=", "0"), NOT(A("Scope", "=", "diagnostics"))),
         source_file=TESTREPO),

    Spec("Which resources are limited to a single copy per partition but allow at least a thousand overall?",
         "RM_SW_Resource", "medium", ["and", "numeric"],
         AND(A("MaxCopyPerPartition", "=", "1"), A("MaxCopyTotal", ">=", "1000"))),

    Spec("Which environment variables are ERS settings that are not the debug level?",
         "Variable", "medium", ["and", "regex", "ne"],
         AND(A("Name", "~=", "TDAQ_ERS_.*"), A("Name", "!=", "TDAQ_ERS_DEBUG_LEVEL"))),

    Spec("Which variables send messages to standard error or standard output?",
         "Variable", "medium", ["or", "eq"],
         OR(A("Value", "=", "lstderr"), A("Value", "=", "lstdout"))),

    Spec("Which binaries belong to the Online software repository?",
         "Binary", "medium", ["relationship", "some", "object_id"],
         R("BelongsTo", "some", OID("Online")),
         note="A relationship expression evaluates its nested expression against the *referenced* "
              "object, not against the binary itself."),

    Spec("Which programs come from a repository installed under /sw/atlas?",
         "ComputerProgram", "medium", ["relationship", "some", "attribute_compare", "regex"],
         R("BelongsTo", "some", A("InstallationPath", "~=", "/sw/atlas/.*")),
         note="The nested attribute must exist on the relationship's target class "
              "(SW_Repository), not on the source class."),

    Spec("Which jar files ship with the Online repository?",
         "JarFile", "medium", ["relationship", "some", "object_id"],
         R("BelongsTo", "some", OID("Online"))),

    Spec("Which software objects belong to a repository whose name starts with TDAQ?",
         "SW_Object", "medium", ["relationship", "some", "attribute_compare", "regex"],
         R("BelongsTo", "some", A("Name", "~=", "TDAQ.*"))),

    Spec("Which applications are started from the is_server binary?",
         "BaseApplication", "medium", ["relationship", "some", "object_id"],
         R("Program", "some", OID("is_server")),
         note="Program has cardinality one-to-one, but the quantifier token is still required by "
              "the grammar; 'some' is the safe choice for a single reference."),

    Spec("Which applications run a program that belongs to the Online repository?",
         "BaseApplication", "medium", ["relationship", "some", "nested-relationship"],
         R("Program", "some", R("BelongsTo", "some", OID("Online"))),
         note="Two hops: Application -> ComputerProgram -> SW_Repository. Each hop re-types the "
              "expression against the next target class."),

    Spec("Which applications wait for the ipc-server before starting?",
         "BaseApplication", "medium", ["relationship", "some", "object_id"],
         R("InitializationDependsFrom", "some", OID("ipc-server"))),

    Spec("Which applications wait for the RDB server to come up first?",
         "BaseApplication", "medium", ["relationship", "some", "object_id", "class-type-typing"],
         R("InitializationDependsFrom", "some", OID("RDB")),
         note="A tempting alternative -- ('InitializationDependsFrom' some ('InterfaceName' "
              "'rdb/writer' =)) -- does not parse. InitializationDependsFrom is declared with "
              "class-type BaseApplication, and InterfaceName lives on IPCServiceApplicationBase, "
              "so the nested expression cannot see it. Naming the service by object id is the "
              "correct construction."),

    Spec("Which repositories are built for the x86_64 EL9 optimised tag?",
         "SW_Repository", "medium", ["relationship", "some", "object_id"],
         R("Tags", "some", OID("x86_64-el9-gcc13-opt"))),

    Spec("Which repositories support at least one aarch64 build?",
         "SW_Repository", "medium", ["relationship", "some", "attribute_compare", "regex"],
         R("Tags", "some", A("HW_Tag", "~=", "aarch64-.*"))),

    Spec("Which variable sets contain the TDAQ_AM_AUTHORIZATION variable?",
         "VariableSet", "medium", ["relationship", "some", "object_id"],
         R("Contains", "some", OID("TDAQ_AM_AUTHORIZATION"))),

    Spec("Which variable sets contain at least one documented parameter?",
         "VariableSet", "medium", ["relationship", "some", "attribute_compare", "class-type-typing"],
         R("Contains", "some", A("Description", "!=", "")),
         note="Contains has class-type Parameter, whose only attribute is Description. The Name "
              "attribute belongs to Variable, a subclass, so it is out of reach here even though "
              "every stored member happens to be a Variable."),

    Spec("Which tests run the test_dummy executable?",
         "Test4Class", "medium", ["relationship", "some", "object_id"],
         R("Runs", "some", OID("test_dummy")), source_file=TESTREPO),

    Spec("Which tests execute something that initialises in under 10 seconds?",
         "Test4Class", "medium", ["relationship", "some", "attribute_compare", "numeric"],
         R("Runs", "some", A("InitTimeout", "<", "10")), source_file=TESTREPO),

    Spec("Which object-level tests target the MTS_IS service?",
         "Test4Object", "medium", ["relationship", "some", "object_id"],
         R("Objects", "some", OID("MTS_IS")), source_file=TESTREPO),

    Spec("Which gatherer applications use the TDAQ_IS_Conf configuration?",
         "MIGApplication", "medium", ["relationship", "some", "object_id"],
         R("Configurations", "some", OID("TDAQ_IS_Conf")), source_file=MIG),

    Spec("Which segments are controlled by the RootController?",
         "Segment", "medium", ["relationship", "some", "object_id"],
         R("IsControlledBy", "some", OID("RootController"))),

    Spec("Which segments run the pmgserver agent?",
         "OnlineSegment", "medium", ["relationship", "some", "object_id"],
         R("PmgAgent", "some", OID("pmgserver"))),

    Spec("Which partitions use the setup-initial online infrastructure?",
         "Partition", "medium", ["relationship", "some", "object_id"],
         R("OnlineInfrastructure", "some", OID("setup-initial"))),

    Spec("Which partitions store their configuration through rdbconfig rather than oksconfig?",
         "Partition", "medium", ["attribute_compare", "eq", "enum"],
         A("DBTechnology", "=", "rdbconfig")),

    Spec("Which partitions log to a directory under /tmp?",
         "Partition", "medium", ["attribute_compare", "regex"],
         A("LogRoot", "~=", "/tmp.*")),

    Spec("Which applications either restart on unexpected exit or depend on the ipc-server?",
         "BaseApplication", "medium", ["or", "relationship", "some"],
         OR(A("IfExitsUnexpectedly", "=", "Restart"), R("InitializationDependsFrom", "some", OID("ipc-server"))),
         note="A boolean operator can mix an attribute term and a relationship term at the same "
              "level."),

    Spec("Which binaries do not belong to the Online repository?",
         "Binary", "medium", ["not", "relationship", "some"],
         NOT(R("BelongsTo", "some", OID("Online"))),
         note="Negating a relationship term also covers binaries that hold no reference at all, "
              "because 'some' over an empty reference list is false."),

    Spec("Which repositories are not built for any debug tag?",
         "SW_Repository", "medium", ["not", "relationship", "some", "regex"],
         NOT(R("Tags", "some", A("SW_Tag", "~=", ".*-dbg")))),

    Spec("Restricting the search to the Binary class itself, which binaries belong to the Online repository?",
         "Binary", "medium", ["scope-this", "relationship", "some"],
         R("BelongsTo", "some", OID("Online")), scope="this"),

    Spec("Which data-quality outputs write to SQLite or Oracle?",
         "DQOutput", "medium", ["or", "regex"],
         OR(A("Parameters", "~=", ".*sqlite://.*"), A("Parameters", "~=", ".*oracle://.*")),
         source_file=DQM),

    Spec("Which data-quality inputs are neither dummy nor default?",
         "DQInput", "medium", ["and", "ne"],
         AND(A("Name", "!=", "DummyInput"), A("Name", "!=", "DefaultInput")), source_file=DQM),

    Spec("Which algorithms have no library name set and no parameter names?",
         "DQAlgorithm", "medium", ["and", "eq", "empty-value"],
         AND(A("LibraryName", "=", ""), A("ParametersNames", "=", "")), source_file=DQM),

    Spec("Which test behaviours are synchronous and stop on the first error?",
         "TestBehavior", "medium", ["and", "bool"],
         AND(A("SynchronousTesting", "=", "1"), A("StopOnError", "=", "1")), source_file=TESTREPO),

    Spec("Which test policies apply to applications and test the container last?",
         "TestPolicy4Class", "medium", ["and", "class-type", "enum"],
         AND(A("Class", "=", "BaseApplication"), A("TestOfContainer", "=", "last")),
         source_file=TESTREPO),

    Spec("Which executables launch a program from the Online repository?",
         "Executable", "medium", ["relationship", "some", "nested-relationship"],
         R("Executes", "some", R("BelongsTo", "some", OID("Online"))), source_file=TESTREPO),

    Spec("Which gatherer applications are started by the MonInfoGatherer binary and allow a restart during the run?",
         "MIGApplication", "medium", ["and", "relationship", "bool"],
         AND(R("Program", "some", OID("MonInfoGatherer")), A("RestartableDuringRun", "=", "1")),
         source_file=MIG),

    # ==================================================================
    # HARD -- structure inside a relationship, nested hops, universal
    #         quantifier, path queries
    # ==================================================================
    Spec("Which applications are started by a program that belongs to a repository built for the x86_64 EL9 optimised tag?",
         "BaseApplication", "hard", ["relationship", "nested-relationship", "three-hop"],
         R("Program", "some", R("BelongsTo", "some", R("Tags", "some", OID("x86_64-el9-gcc13-opt")))),
         note="Three hops: Application -> ComputerProgram -> SW_Repository -> Tag. Each level is "
              "re-typed against the next relationship's class-type, and the innermost object-id "
              "test applies to the Tag object."),

    Spec("Which applications run a program that is documented on atddoc and belongs to the Online repository?",
         "BaseApplication", "hard", ["relationship", "and-inside-relationship"],
         R("Program", "some", AND(A("HelpURL", "~=", "http://atddoc\\.cern\\.ch/.*"),
                                  R("BelongsTo", "some", OID("Online")))),
         note="The 'and' lives inside the relationship, so both conditions are checked on the "
              "same referenced program. Hoisting it outside would change the meaning."),

    Spec("Which applications wait for either the ipc-server or the RDB server before they start?",
         "BaseApplication", "hard", ["relationship", "or-inside-relationship"],
         R("InitializationDependsFrom", "some", OR(OID("ipc-server"), OID("RDB"))),
         note="One relationship term with an 'or' of two object-id tests inside. Compare with an "
              "'or' of two relationship terms, which is logically equivalent here but reads the "
              "reference list twice."),

    Spec("Which applications depend on something other than the ipc-server or the RDB server?",
         "BaseApplication", "hard", ["relationship", "not-inside-relationship"],
         R("InitializationDependsFrom", "some", NOT(OR(OID("ipc-server"), OID("RDB")))),
         note="Negation placed inside the relationship means 'has at least one dependency that "
              "is not X', which is different from 'has no dependency that is X'."),

    Spec("Which applications have no dependency on the ipc-server at all?",
         "BaseApplication", "hard", ["not", "relationship", "quantifier-placement"],
         NOT(R("InitializationDependsFrom", "some", OID("ipc-server"))),
         note="The contrast case for the previous row: negating the whole relationship term is "
              "'none of them', negating inside it is 'at least one that is not'. It also covers "
              "applications with no dependencies at all, because 'some' over an empty reference "
              "list is false."),

    Spec("Which repositories are built only for gcc11 and gcc13 toolchains?",
         "SW_Repository", "hard", ["relationship", "all-quantifier", "regex"],
         R("Tags", "all", A("SW_Tag", "~=", "gcc1[13]-.*")),
         note="The universal quantifier: every referenced Tag must satisfy the nested expression. "
              "'some' would only require one. This dataset treats an empty reference list as not "
              "satisfying 'all', so repositories with no tags are excluded."),

    Spec("Which repositories are built exclusively for optimised tags, with no debug build at all?",
         "SW_Repository", "hard", ["relationship", "all-quantifier", "negative-case"],
         R("Tags", "all", A("SW_Tag", "~=", ".*-opt")), allow_empty=True,
         note="A deliberate empty-result case: every repository in this configuration ships a "
              "debug tag too, so the universal quantifier correctly returns nothing. A system "
              "that answers 'some' instead would wrongly return all 61 repositories."),

    Spec("Which tests run only executables that initialise within 5 seconds?",
         "Test4Class", "hard", ["relationship", "all-quantifier", "numeric"],
         R("Runs", "all", A("InitTimeout", "<=", "5")), source_file=TESTREPO),

    Spec("Which segments are controlled by a run-control application that ignores errors?",
         "Segment", "hard", ["relationship", "attribute-inside-relationship"],
         R("IsControlledBy", "some", A("IfError", "=", "Ignore")),
         note="IfError is declared on RunControlApplicationBase, which is exactly the class-type "
              "of IsControlledBy, so the nested expression resolves."),

    Spec("Which variable sets document every parameter they contain?",
         "VariableSet", "hard", ["relationship", "all-quantifier"],
         R("Contains", "all", A("Description", "!=", "")),
         note="Universal quantifier over a composite relationship: every contained Parameter "
              "must carry a description."),

    Spec("Which segments are controlled by an application whose action timeout is over 30 seconds?",
         "Segment", "hard", ["relationship", "attribute-inside-relationship", "numeric"],
         R("IsControlledBy", "some", A("ActionTimeout", ">", "30"))),

    Spec("Which online segments include the RDB service in their infrastructure?",
         "OnlineSegment", "hard", ["relationship", "some", "object_id", "class-type-typing"],
         R("Infrastructure", "some", OID("RDB")),
         note="Infrastructure has class-type InfrastructureBase, which declares only the "
              "SegmentProcEnvVar* attributes. Filtering the infrastructure by InterfaceName is "
              "therefore not expressible; the service has to be named by object id."),

    Spec("Which online segments run at least one application that is not restartable during a run?",
         "OnlineSegment", "hard", ["relationship", "not-inside-relationship", "bool"],
         R("Applications", "some", NOT(A("RestartableDuringRun", "=", "1"))), allow_empty=True),

    Spec("Which online segments default to a debug tag?",
         "OnlineSegment", "hard", ["relationship", "some", "regex", "enum"],
         R("DefaultTags", "some", A("SW_Tag", "~=", ".*-dbg"))),

    Spec("Which online segments default only to CentOS 7 and EL9 platforms?",
         "OnlineSegment", "hard", ["relationship", "all-quantifier", "enum"],
         R("DefaultTags", "all", A("HW_Tag", "~=", ".*-(centos7|el9)")),
         note="Every default tag of this segment targets one of the two supported operating "
              "systems, so 'all' is satisfied. Asking the same question about the architecture "
              "-- x86_64 only -- returns nothing, because the same list also carries aarch64 "
              "builds: the quantifier is doing real work here."),

    Spec("Which online segments run an application started from the oh_rm binary?",
         "OnlineSegment", "hard", ["relationship", "nested-relationship"],
         R("Applications", "some", R("Program", "some", OID("oh_rm")))),

    Spec("Which partitions are backed by an online segment controlled by the DefaultRootController?",
         "Partition", "hard", ["relationship", "nested-relationship"],
         R("OnlineInfrastructure", "some", R("IsControlledBy", "some", OID("DefaultRootController"))),
         note="Partition -> OnlineSegment -> RunControlApplicationBase. The object-id test lands "
              "on the controller, not on the partition or the segment."),

    Spec("Which partitions have an online segment whose parameters include the setup segment parameter set?",
         "Partition", "hard", ["relationship", "nested-relationship"],
         R("OnlineInfrastructure", "some", R("Parameters", "some", OID("SetupSegmentParameters")))),

    Spec("Which partitions run an online segment that still offers a debug build by default?",
         "Partition", "hard", ["relationship", "nested-relationship", "regex"],
         R("OnlineInfrastructure", "some", R("DefaultTags", "some", A("SW_Tag", "~=", ".*-dbg")))),

    Spec("Which applications restart on unexpected exit and are started by a program from the Online repository?",
         "BaseApplication", "hard", ["and", "relationship", "nested-relationship", "enum"],
         AND(A("IfExitsUnexpectedly", "=", "Restart"),
             R("Program", "some", R("BelongsTo", "some", OID("Online"))))),

    Spec("Which IPC service applications serve rdb, initialise in 30 seconds, and depend on the ipc-server?",
         "IPCServiceApplication", "hard", ["and", "three-operand", "relationship"],
         AND(A("InterfaceName", "~=", "rdb/.*"),
             A("InitTimeout", "=", "30"),
             R("InitializationDependsFrom", "some", OID("ipc-server"))),
         note="'and' accepts more than two operands; the parser only rejects fewer than two."),

    Spec("Which applications are either long to start, over 30 seconds, or depend on something that ignores startup failures?",
         "BaseApplication", "hard", ["or", "relationship", "attribute-inside-relationship"],
         OR(A("InitTimeout", ">", "30"),
            R("InitializationDependsFrom", "some", A("IfFailsToStart", "=", "Ignore")))),

    Spec("Which run-control applications restart on error but are not the RootController?",
         "RunControlApplication", "hard", ["and", "not", "object_id"],
         AND(A("IfError", "=", "Restart"), NOT(OID("RootController"))),
         note="An object-id test can be negated like any other expression, which is how an "
              "object is excluded by identity rather than by attribute."),

    Spec("Which binaries belong to a repository installed under /sw/atlas that is not the Online repository?",
         "Binary", "hard", ["relationship", "and-inside-relationship", "regex"],
         R("BelongsTo", "some", AND(A("InstallationPath", "~=", "/sw/atlas/.*"),
                                    A("Name", "!=", "Online")))),

    Spec("Which programs belong to a repository that has both an optimised and a debug build available?",
         "ComputerProgram", "hard", ["relationship", "and-of-relationships"],
         R("BelongsTo", "some", AND(R("Tags", "some", A("SW_Tag", "~=", ".*-opt")),
                                    R("Tags", "some", A("SW_Tag", "~=", ".*-dbg")))),
         note="Two 'some' terms over the same relationship inside one 'and': each may be "
              "satisfied by a different Tag. A single 'some' with an 'and' inside would demand "
              "one Tag that is both optimised and debug, which is impossible."),

    Spec("Which repositories ship a software object documented on the CERN TWiki?",
         "SW_Repository", "hard", ["relationship", "attribute-inside-relationship", "regex"],
         R("SW_Objects", "some", A("HelpURL", "~=", "https://twiki\\.cern\\.ch/.*")),
         allow_empty=True),

    Spec("Which class-level tests fail into a generic CORBA failure and run an executable on the object's own host?",
         "Test4Class", "hard", ["and", "two-relationships"],
         AND(R("Failures", "some", OID("GenericCORBAFailure")),
             R("Runs", "some", A("Host", "=", "#this.UID"))),
         source_file=TESTREPO, allow_empty=True),

    Spec("Which object-level tests target something that is not the IPC server?",
         "Test4Object", "hard", ["relationship", "not-inside-relationship"],
         R("Objects", "some", NOT(OID("ipc-server"))), source_file=TESTREPO),

    Spec("Which gatherer applications use only configurations that match every provider?",
         "MIGApplication", "hard", ["relationship", "all-quantifier"],
         R("Configurations", "all", A("ProviderRegExp", "=", ".*")), source_file=MIG),

    Spec("Which gatherer applications read from the DF_IS source server?",
         "MIGApplication", "hard", ["relationship", "nested-relationship"],
         R("Configurations", "some", R("SourceServers", "some", OID("DF_IS"))),
         source_file=MIG),

    Spec("Looking at the RunControlApplication class alone, which of them restart on error and control no TTC partition?",
         "RunControlApplication", "hard", ["scope-this", "and", "bool", "enum"],
         AND(A("IfError", "=", "Restart"), A("ControlsTTCPartitions", "=", "0")), scope="this"),

    Spec("Which applications initialise in either 15, 20 or 60 seconds?",
         "BaseApplication", "hard", ["or", "three-operand", "numeric"],
         OR(A("InitTimeout", "=", "15"), A("InitTimeout", "=", "20"), A("InitTimeout", "=", "60")),
         note="Three operands under 'or'. A regex alternation on a numeric attribute would not "
              "work: '~=' forces the string comparison path."),

    Spec("Which applications are outside the 30-to-60-second initialisation window?",
         "BaseApplication", "hard", ["not", "and", "range"],
         NOT(AND(A("InitTimeout", ">=", "30"), A("InitTimeout", "<=", "60"))),
         note="De Morgan check: negating the interval is not the same as an 'or' of the two "
              "negated bounds unless both are inverted."),

    Spec("Which applications either run no program from the Online repository or are ignored when they fail to start?",
         "BaseApplication", "hard", ["or", "not", "relationship"],
         OR(NOT(R("Program", "some", R("BelongsTo", "some", OID("Online")))),
            A("IfFailsToStart", "=", "Ignore"))),

    # -- path queries: valid OKS, not expressible in the current IR -----
    Spec("Show the path from the initial partition to the DefaultRootController application.",
         "Partition", "hard", ["path_query", "direct"],
         query_oks='(path-to "DefaultRootController@RunControlApplication" '
                   '(direct "OnlineInfrastructure" "IsControlledBy"))',
         ir_expressible=False,
         note="A path query navigates named relationships toward a destination written id@class; "
              "it is not an attribute filter. The translator's IR has no node for it today, so "
              "this row measures a known coverage gap rather than a translation error."),

    Spec("How does the setup segment reach the pmgserver binary?",
         "OnlineSegment", "hard", ["path_query", "direct"],
         query_oks='(path-to "pmgserver@Binary" (direct "PmgAgent"))',
         ir_expressible=False,
         note="Single-step path query. The destination must resolve to a loaded object or the "
              "parser throws oks::bad_query_syntax."),

    Spec("Trace how the initial partition reaches the ISRepository-initial service through its online segment.",
         "Partition", "hard", ["path_query", "direct", "nested"],
         query_oks='(path-to "ISRepository-initial@IPCServiceApplication" '
                   '(direct "OnlineInfrastructure" (nested "Infrastructure")))',
         ir_expressible=False,
         note="'direct' follows the named relationships once; 'nested' looks through recursively "
              "nested objects. Relationship names must be quoted in a path expression."),

    Spec("Find the route from the setup segment to the x86_64 EL9 optimised tag.",
         "OnlineSegment", "hard", ["path_query", "direct"],
         query_oks='(path-to "x86_64-el9-gcc13-opt@Tag" (direct "DefaultTags"))',
         ir_expressible=False),

    Spec("Show the chain that links the initial partition to the SetupSegmentParameters variable set.",
         "Partition", "hard", ["path_query", "direct", "nested"],
         query_oks='(path-to "SetupSegmentParameters@VariableSet" '
                   '(direct "OnlineInfrastructure" (nested "Parameters")))',
         ir_expressible=False),
]
