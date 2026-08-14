# Source 1: DUNE-DAQ/oks (GitHub, public, branch `develop`)

- **Source URL:** https://github.com/DUNE-DAQ/oks (branch `develop`)
- **Local mirror:** `repo/dune-oks/` (git clone, depth 1, commit as of 2026-08-08)
- **Caption:** DUNE DAQ fork of the ATLAS OKS configuration database, forked from ATLAS tag `oks-08-03-04` (2022-04-14). All headers carry the notice:
  ```cpp
  // DUNE DAQ modification notice:
  // This file has been modified from the original ATLAS oks source for the DUNE DAQ project.
  // Fork baseline commit: oks-08-03-04 (2022-04-14).
  ```
- **Mapping to sections:** A (concepts, docs/README.md), B (storage format, src/file.cpp DTDs), C (query grammar, src/query.cpp), D (C++ API, include/oks/*.hpp), E (CLI tools, apps/*.cxx), F (Python, pybindsrc/module.cpp), G (versioning, scripts/*.sh + kernel.hpp repository API), H (worked examples, oks_dump.cxx).

The DUNE version is a *cleaned* fork of ATLAS `oks-08-03-04`: same parser core, but several CLI tools differ (e.g. `oks_validate_repository.cxx` here is DUNE/CERN-hybrid with `logging`/`ers` includes). The canonical grammar/version history lives in the CERN GitLab sources (see `03-*` files).

---

## A) docs/README.md — canonical prose description (21 lines, verbatim)

```markdown
<!-- DUNE DAQ modification notice: This file has been modified from the original ATLAS oks source for the DUNE DAQ project. Fork baseline commit: oks-08-03-04 (2022-04-14). Renamed since fork: yes (from README.md to docs/README.md). -->

**_JCF, Jul-15-2023: the documentation below this line is the original README.md contents of the oks repo from ATLAS. For the documentation of the OKS suite for DUNE DAQ, please go [here](https://dune-daq-sw.readthedocs.io/en/latest/packages/dal/)_**

The OKS (Object Kernel Support) is a library to support a simple active persistent in-memory object manager. It is suitable for applications which need to create persistent structured information with fast access but do not require full database functionality.

OKS is based on an object model that supports objects, classes, associations, methods, data abstraction, inheritance, polymorphism, object identifiers, composite objects, integrity constraints, schema evolution, data migration and active notification. OKS stores the class definitions and their instances in XML files (which can be used across different platforms). It provides query facilities. The OKS has C++ API and includes Motif based GUI applications to design class schema and to manipulate objects.

### Authors

Igor Soloviev

### Origin

The OKS was designed at the Information Technology (IT) Department of Petersburg Nuclear Physics Institute (PNPI) Russain Academy of Science in 1996.

### More information

[Release Notes](https://gitlab.cern.ch/atlas-tdaq-software/oks/-/blob/master/doc/RELEASE_NOTES.md)

[TWiki](https://twiki.cern.ch/twiki/bin/view/Atlas/DaqHltOks)
```

Note: the two typos ("offersivity", "tools", "included", "and Java bindings" removed) are in the original. OKS is described as **"a simple active persistent in-memory database"** — NOT a full DB. Core concepts: objects, classes, associations, methods, data abstraction, inheritance, polymorphism, object identifiers, composite objects, integrity constraints, schema evolution, data migration, active notification. Storage: XML schema + data files. GUI apps existed in ATLAS (Motif: "OKS Data Editor").

---

## C-1: Query grammar — reserved tokens (src/query.cpp:23-39, verbatim)

```cpp
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
```

The seven comparators (`=`, `!=`, `~=`, `<=`, `>=`, `<`, `>`) bind to function pointers in the same file (lines 56-64, verbatim):

```cpp
bool OksQuery::equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 == *d2);}
bool OksQuery::not_equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 != *d2);}
bool OksQuery::less_or_equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 <= *d2);}
bool OksQuery::greater_or_equal_cmp(const OksData *d1, const OksData *d2) {return (*d1 >= *d2);}
bool OksQuery::less_cmp(const OksData *d1, const OksData *d2) {return (*d1 < *d2);}
bool OksQuery::greater_cmp(const OksData *d1, const OksData *d2) {return (*d1 > *d2);}
bool OksQuery::reg_exp_cmp(const OksData *d, const OksData * re) {
  return boost::regex_match(d->str(), *reinterpret_cast<const boost::regex *>(re));
}
```

Regex comparator uses **boost::regex** (implemented via lazy compilation in `OksObject::SatisfiesQueryExpression`).

---

## C-2. Query string parser (src/query.cpp)

Top-level grammar enforced by `OksQuery::OksQuery(const OksClass*, const std::string&)` (lines 90-183). Rules, verbatim:

```cpp
// the first token must be 'all' or 'this'
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
```

The recursive-descent expression parser is `OksQuery::create_expression(const OksClass*, const std::string&)` (lines 186-431). Tokenizer: splitting on spaces, with quoted strings `"` / `'` / `` ` `` as delimiters, and nested parens balanced with a depth counter `(lines 214-274)`. The grammar in code form:

```cpp
  const std::string first = slist.front();
  slist.pop_front();

  if(
   first == OksQuery::AND ||
   first == OksQuery::OR
  ) {
    if(slist.size() < 2) { /* error: 'and'/'or' must have two or more args */ }
    qe = ((first == OksQuery::AND)
            ? (OksQueryExpression *)new OksAndExpression()
            : (OksQueryExpression *)new OksOrExpression());
    while(!slist.empty()) { ... qe2 = create_expression(c, item2); ... }
  }
  else if(first == OksQuery::NOT) {
    if(slist.size() != 1) { /* error: 'not' must have exactly one command */ }
    qe = new OksNotExpression(); ...
  }
  else if(slist.size() != 2) { /* error */ }
  else {
    const std::string second = ...; const std::string third = ...;
    if(second == OksQuery::SOME || second == OksQuery::ALL_SUBCLASSES) {
      // relationship expression: "name some/any subquery"
      OksRelationship *r = c->find_relationship(first);
      ...
      qe = new OksRelationshipExpression(r, qe2, b);   // b = true for 'all'
    }
    else {
      // comparator expression: name value op
      OksAttribute *a = ((first != OksQuery::OID) ? c->find_attribute(first) : 0);
      ...
      OksQuery::Comparator f = (
        (third == OksQuery::EQ) ? OksQuery::equal_cmp :
        (third == OksQuery::NE) ? OksQuery::not_equal_cmp :
        (third == OksQuery::RE) ? OksQuery::reg_exp_cmp :
        (third == OksQuery::LE) ? OksQuery::less_or_equal_cmp :
        (third == OksQuery::GE) ? OksQuery::greater_or_equal_cmp :
        (third == OksQuery::LS) ? OksQuery::less_cmp :
        (third == OksQuery::GT) ? OksQuery::greater_cmp :
        0);
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
        d->Set(second);      // object-id comparison
      }
      ...
      qe = new OksComparator(a, d, f);
    }
  }
```

Relationship expressions pick up the target class from the relationship type: `create_expression(relc, third)` where `relc = c->get_kernel()->find_class(r->get_type())`.

### Examples of the grammar (embedded in QueryPath class doc, include/oks/query.hpp lines 372-384, verbatim):

```
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
```

---

## C-3. Query execution

`OksClass::execute_query(OksQuery*)` (src/query.cpp lines 435-544) — verbatim highlights:

- checks `sqe->CheckSyntax()`; on false prints `"Can't execute query \"..."\"` and returns 0
- indexes: if class `p_indices` has an index on the comparator attribute, `OksIndex::find_all()` is used (indexed search)
- for `and`/`or` with 2 comparator-type expressions on the same attribute, two-sided index lookup
- otherwise linear scan over `p_objects->begin()..end()`, calling `o->SatisfiesQueryExpression(sqe)`
- if `qe->search_in_subclasses()`, loops over `p_all_sub_classes`, same scan
- throws `oks::QueryFailed` wrapping any `oks::exception`/`std::exception`

`OksObject::SatisfiesQueryExpression` (lines 634-780): for comparator type, if attribute is nil compares `OksData d(GetId())` (object-ID query), else compares `data[offset]`. For relationship type: many-cardinality loops over list; `checkAllObjects==true` means ALL-of, false means SOME-of; single-value returns whether referenced object satisfies. Unbound references (uid2 in memory) throw `std::runtime_error` with verbatim text. And: all must satisfy; Or: any must satisfy; Not: negate.

`operator<<` (serialization back to string, lines 783-911) prints `(all|this (<expr>))` — this is the canonical printed query form.

---

## C-4. QueryPath (path-to) parser — full verbatim (src/query.cpp 1054-1216)

```cpp
oks::QueryPath::QueryPath(const std::string& str, const OksKernel& kernel) : p_start(0)
{
  std::string s(str);
  erase_empty_chars(s);

  if(s.empty()) {
    throw oks::bad_query_syntax( "Empty query" );
  }

  if(s[0] == '(') {
    std::string::size_type p = s.rfind(')');
    if(p == std::string::npos)
      throw oks::bad_query_syntax(std::string("Query expression \'") + str + "\' must contain closing bracket");
    s.erase(p);  s.erase(0, 1);
  }
  else
    throw oks::bad_query_syntax(std::string("Query expression \'") + str + "\' must be enclosed by brackets");

  erase_empty_chars(s);

  Oks::Tokenizer t(s, " \t\n");
  std::string token;
  t.next(token);

  if(token != OksQuery::PATH_TO)
    throw oks::bad_query_syntax(std::string("Expression \'") + s + "\' must start from " + OksQuery::DIRECT + " or " + OksQuery::NESTED + " keyword");

  s.erase(0, token.size());
  erase_empty_chars(s);

  if( s[0] == '\"' ) {
    // destination object is "class@id"
    std::string::size_type p = s.find('\"', 1);
    if(p == std::string::npos)
      throw oks::bad_query_syntax(std::string("No trailing delimiter of object name in query \'") + str + "\'");

    std::string::size_type p2 = s.find('@');
    if(p2 == std::string::npos || p2 > p)
      throw oks::bad_query_syntax(std::string("Bad format of object name ") + s.substr(0, p+1) + " in query \'" + str + "\'");

    std::string object_id = std::string(s, 1, p2 - 1);
    std::string class_name = std::string(s, p2 + 1, p - p2 - 1);

    if(OksClass * c = kernel.find_class(class_name)) {
      if((p_goal = c->get_object(object_id)) == 0)
        throw oks::bad_query_syntax(std::string("Cannot find object ") + s.substr(0, p+1) + " in query \'" + str + "\': no such object");
    }
    else
      throw oks::bad_query_syntax(std::string("Cannot find object ") + s.substr(0, p+1) + " in query \'" + str + "\': no such class");

    s.erase(0, p + 1);
  }
  else
    throw oks::bad_query_syntax(std::string("No name of object in \'") + str + "\'");

  try { p_start = new QueryPathExpression(s); }
  catch ( oks::bad_query_syntax& e ) {
    throw oks::bad_query_syntax(std::string("Failed to parse expression \'") + str + "\' because \'" + e.what() + "\'");
  }
}
```

`QueryPathExpression` parser (lines 1129-1231): each element is `(direct|nested "rel1" "rel2" ... (nested-expr))`; relationship names **must** be quoted; nested expression parsed recursively; `p_use_nested_lookup` set true for `nested` (a path may look through recursively nested objects). The path search itself is in `OksObject::satisfies()` (lines 954-1052) — explores each relationship, checks whether it points at the goal object, then recurses; cycles prevented by checking `path` membership. `OksObject::find_path(const oks::QueryPath&)` returns newly-allocated `OksObject::List *` (0 if none).

---

## B: Storage format — XML DTDs (src/file.cpp lines 48-199, verbatim)

Header + both DTDs:

```cpp
const char OksFile::xml_file_header[]  = "<?xml version=\"1.0\" encoding=\"ASCII\"?>";

const char OksFile::xml_schema_file_dtd[] =
  "<!DOCTYPE oks-schema [\n"
  "  <!ELEMENT oks-schema (info, (include)?, (comments)?, (class)+)>\n"
  "  <!ELEMENT info EMPTY>\n"
  "  <!ATTLIST info\n"
  "      name CDATA #IMPLIED\n"
  "      type CDATA #IMPLIED\n"
  "      num-of-items CDATA #REQUIRED\n"
  "      oks-format CDATA #FIXED \"schema\"\n"
  "      oks-version CDATA #REQUIRED\n"
  "      created-by CDATA #IMPLIED\n"
  "      created-on CDATA #IMPLIED\n"
  "      creation-time CDATA #IMPLIED\n"
  "      last-modified-by CDATA #IMPLIED\n"
  "      last-modified-on CDATA #IMPLIED\n"
  "      last-modification-time CDATA #IMPLIED\n"
  "  >\n"
  "  <!ELEMENT include (file)+>\n"
  "  <!ELEMENT file EMPTY>\n"
  "  <!ATTLIST file path CDATA #REQUIRED>\n"
  ...
  "  <!ELEMENT class (superclass | attribute | relationship | method)*>\n"
  "  <!ATTLIST class name CDATA #REQUIRED description CDATA \"\" is-abstract (yes|no) \"no\">\n"
  "  <!ELEMENT superclass EMPTY>\n  <!ATTLIST superclass name CDATA #REQUIRED>\n"
  "  <!ELEMENT attribute EMPTY>\n"
  "  <!ATTLIST attribute\n"
  "      name CDATA #REQUIRED description CDATA \"\"\n"
  "      type (bool|s8|u8|s16|u16|s32|u32|s64|u64|float|double|date|time|string|uid|enum|class) #REQUIRED\n"
  "      range CDATA \"\" format (dec|hex|oct) \"dec\"\n"
  "      is-multi-value (yes|no) \"no\" init-value CDATA \"\"\n"
  "      is-not-null (yes|no) \"no\" ordered (yes|no) \"no\"\n"
  "  >\n"
  "  <!ELEMENT relationship EMPTY>\n"
  "  <!ATTLIST relationship\n"
  "      name CDATA #REQUIRED description CDATA \"\" class-type CDATA #REQUIRED\n"
  "      low-cc (zero|one) #REQUIRED high-cc (one|many) #REQUIRED\n"
  "      is-composite (yes|no) #REQUIRED is-exclusive (yes|no) #REQUIRED is-dependent (yes|no) #REQUIRED\n"
  "      ordered (yes|no) \"no\"\n"
  "  >\n"
  ...
  "]>";

const char OksFile::xml_data_file_dtd[] =
  "<!DOCTYPE oks-data [\n"
  "  <!ELEMENT oks-data (info, (include)?, (comments)?, (obj)+)>\n"
  ...
  "  <!ATTLIST info name CDATA #IMPLIED type CDATA #IMPLIED num-of-items CDATA #REQUIRED\n"
  "      oks-format CDATA #FIXED \"data\" oks-version CDATA #REQUIRED\n"
  "      created-by CDATA #IMPLIED created-on CDATA #IMPLIED creation-time CDATA #IMPLIED\n"
  "      last-modified-by CDATA #IMPLIED last-modified-on CDATA #IMPLIED last-modification-time CDATA #IMPLIED\n"
  "  >\n"
  "  <!ELEMENT include (file)*>\n" "  <!ELEMENT file EMPTY>\n" "  <!ATTLIST file path CDATA #REQUIRED>\n"
  "  <!ELEMENT obj (attr | rel)*>\n"
  "  <!ATTLIST obj class CDATA #REQUIRED id CDATA #REQUIRED>\n"
  "  <!ELEMENT attr (data)*>\n"
  "  <!ATTLIST attr name CDATA #REQUIRED\n"
  "      type (bool|s8|u8|s16|u16|s32|u32|s64|u64|float|double|date|time|string|uid|enum|class|-) \"-\"\n"
  "      val CDATA \"\"\n"
  "  >\n"
  "  <!ELEMENT data EMPTY>\n  <!ATTLIST data val CDATA #REQUIRED>\n"
  "  <!ELEMENT rel (ref)*>\n"
  "  <!ATTLIST rel name CDATA #REQUIRED class CDATA \"\" id CDATA \"\"\n"
  "  <!ELEMENT ref EMPTY>\n  <!ATTLIST ref class CDATA #REQUIRED id CDATA #REQUIRED>\n"
  "]>";
```

(Whitespace inside `<!ATTLIST ...>` collapsed for compactness; content is verbatim.)

**Data file formats** (src/kernel.cpp): the `oks-format` info attribute is either `"data"` (old format), `"extended"`, or `"compact"` (new format saved by default, see `save_data()` doc line 1338-1341: "By default the format of data file is compact."). `\"compact\"` = values inside tags (`<data val="...">` with nested/aliased representation); `\"extended\"` = explicit `<attr name type val ...>` tags. The `OksAliasTable` doc in kernel.hpp (lines 430-449) explains the alias technique used to compress class names in data files:

```
The technique of aliases is used to reduce size of OKS data files:
if a class name appears first time somewhere in OKS data file it is marked in front by '@' symbol and the alias to it is used
later, e.g.:
	- first object stored in data file is "Detector@First"
	  and it will be stored as "@Detector@First"
	- second object stored in data file is "Detector@Second"
	  and it will be stored as "0@Second"
	- in this case "0" is alias for "Detector"
```

`OksFile::get_oks_format()` returns `p_oks_format` ("data"/"schema"/"extended"/"compact").

---

## D-1. C++ API — include/oks/*.hpp public surface (verbatim declarations)

### query.hpp (412 lines) — full public API:
```cpp
class OksQuery {
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
    enum QueryType { unknown_type, comparator_type, relationship_type, not_type, and_type, or_type };
    static const char * OR, AND, NOT, SOME, THIS_CLASS, ALL_SUBCLASSES, OID,
                        EQ, NE, RE, LE, GE, LS, GT, PATH_TO, DIRECT, NESTED;
    static bool equal_cmp(const OksData*, const OksData*);
    static bool not_equal_cmp(const OksData*, const OksData*);
    static bool less_or_equal_cmp(const OksData*, const OksData*);
    static bool greater_or_equal_cmp(const OksData*, const OksData*);
    static bool less_cmp(const OksData*, const OksData*);
    static bool greater_cmp(const OksData*, const OksData*);
    static bool reg_exp_cmp(const OksData*, const OksData * regexp);
    typedef bool (*Comparator)(const OksData *, const OksData *);
  private:
    bool p_sub_classes; OksQueryExpression * p_expression; int p_status;
    static OksQueryExpression *create_expression(const OksClass *, const std::string &);
};

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

class OksComparator : public OksQueryExpression {
  friend class OksObject; friend class OksQueryExpression;
  public:
    OksComparator(const OksAttribute *a, OksData *v, OksQuery::Comparator f) :
        OksQueryExpression (OksQuery::comparator_type), attribute (a), value (v),
        m_comp_f (f), m_reg_exp (0) {};
    virtual ~OksComparator() { delete value; if(m_reg_exp) delete m_reg_exp; }
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

class OksRelationshipExpression : public OksQueryExpression {
  public:
    OksRelationshipExpression(const OksRelationship *r, OksQueryExpression *q, bool b = false) : ... ;
    virtual ~OksRelationshipExpression() {delete p_expression;}
    const OksRelationship * GetRelationship() const;
    void SetRelationship(const OksRelationship*);
    OksQueryExpression * get() const;
    void set(OksQueryExpression*);
    bool IsCheckAllObjects() const;
    void SetIsCheckAllObjects(const bool b);
};

class OksNotExpression : public OksQueryExpression {
  public:
    OksNotExpression(OksQueryExpression *q = 0) : ... ;
    virtual ~OksNotExpression() {delete p_expression;}
    OksQueryExpression * get() const; void set(OksQueryExpression*);
};

class OksListBaseQueryExpression {  // abstract list of expressions
  public:
    virtual ~OksListBaseQueryExpression() {while(!p_expressions.empty()) {...}}
    const std::list<OksQueryExpression *> & expressions() const {return p_expressions;}
    void add(OksQueryExpression *q) {p_expressions.push_back(q);}
};

class OksAndExpression : public OksQueryExpression, public OksListBaseQueryExpression {
  public: OksAndExpression() : OksQueryExpression(OksQuery::and_type) {}; virtual ~OksAndExpression() {;}
};
class OksOrExpression : public OksQueryExpression, public OksListBaseQueryExpression {
  public: OksOrExpression() : OksQueryExpression(OksQuery::or_type) {}; virtual ~OksOrExpression() {;}
};

class bad_query_syntax : public std::exception { ... };   // thrown by QueryPath parsing

class QueryPathExpression {
  public:
    bool get_use_nested_lookup() const;
    const std::list<std::string>& get_rel_names() const;
    const QueryPathExpression * get_next() const;
  protected:
    QueryPathExpression(bool v);           // direct
    QueryPathExpression(const std::string&);  // parse "(direct|nested ...)" expr
};

class QueryPath {
  public:
    QueryPath(const OksObject * o, QueryPathExpression * qpe) : p_goal(o), p_start(qpe) { }
    QueryPath(const std::string& query, const OksKernel&);
    ~QueryPath() {delete p_start;}
    const QueryPathExpression * get_start_expression() const { return p_start; }
    const OksObject * get_goal_object() const { return p_goal; }
};
```

### OksKernel (kernel.hpp, 2226 lines) — key public methods:
```cpp
OksKernel(bool silence_mode = false, bool verbose_mode = false, bool profiling_mode = false,
          bool allow_repository = true, const char * version = nullptr, std::string branch_name = "");
OksKernel(const OksKernel& src, bool copy_repository = false);
~OksKernel();
static const char * GetVersion();                       // CVS tag + date of build
static std::string& get_host_name(); static std::string& get_domain_name(); static std::string& get_user_name();
bool get_verbose_mode/get_silence_mode/get_profiling_mode() const;   void set_* (bool)
bool get_allow_duplicated_classes_mode() const; bool get_allow_duplicated_objects_mode() const; void set_* (bool)
bool get_test_duplicated_objects_via_inheritance_mode() const; void set_... (bool)
static bool get_skip_string_range(); static void set_skip_string_range(const bool b);
std::shared_mutex& get_mutex() {return p_kernel_mutex;}
OksFile * find_schema_file(const std::string&) const; OksFile * find_data_file(const std::string&) const;
std::list<OksClass *> * create_list_of_schema_classes(OksFile *) const;
std::list<OksObject *> * create_list_of_data_objects(OksFile *) const;
OksFile * create_file_info(const std::string& short_file_name, const std::string& file_name);
static bool check_read_only(OksFile * f);
std::string get_file_path(const std::string& path, const OksFile * parent_file = 0, bool strict_paths = true) const;
static const std::string& get_repository_root();          // TDAQ_DB_REPOSITORY
const std::string& get_repository_version();
bool is_user_repository_created() const;
static const std::string& get_repository_mapping_dir();
const std::string& get_user_repository_root() const;
void set_user_repository_root(const std::string& path, const std::string& version = "");
static std::string get_tmp_file(const std::string& file_name);
void get_includes(const std::string& file_name, std::set<std::string>& includes, bool use_repository_name = false);
void k_create_dangling_includes();
OksFile * load_file(const std::string& name, bool bind = true);
OksFile * load_schema(const std::string& name, const OksFile * parent = 0);
OksFile * new_schema(const std::string& name);
void save_schema(OksFile * file_h, bool force = false, OksFile * true_file_h = 0);
void save_schema(OksFile * file_h, bool force, const OksClass::Map& classes);
void backup_schema(OksFile * pf, const char * suffix = ".bak");
void save_as_schema(const std::string& name, OksFile * file_h);
void save_all_schema(); void close_schema(OksFile * file_h); void close_all_schema();
void set_active_schema(OksFile * file_h); void k_set_active_schema(OksFile * file_h);
OksFile * get_active_schema() const {return p_active_schema;}
const OksFile::Map & schema_files() const; const OksFile::Map & data_files() const;
void create_lists_of_updated_schema_files(std::list<OksFile *> **, std::list<OksFile *> **) const;
void get_updated_repository_files(std::set<std::string>&, std::set<std::string>&, std::set<std::string>&);
OksFile * load_data(const std::string& name, bool bind = true);
void reload_data(std::set<OksFile *>& files, bool allow_schema_extension = true);
OksFile * new_data(const std::string& name, const std::string& logical_name = "", const std::string& type = "");
void save_data(OksFile * file_h, bool ignore_bad_objects = false, OksFile * true_file_h = nullptr, bool force_defaults = false);
void save_data(OksFile * file_h, const OksObject::FSet& objects);
void backup_data(OksFile * pf, const char * suffix = ".bak");
void save_as_data(const std::string& new_name, OksFile * file_h);
void save_all_data(bool force_defaults=false);
void close_data(OksFile * file_h, bool unbind_objects = true); void close_all_data();
void set_active_data(OksFile * file_h); void k_set_active_data(OksFile *);
OksFile * get_active_data() const;
void create_lists_of_updated_data_files(std::list<OksFile *> **, std::list<OksFile *> **) const;
void get_modified_files(std::set<OksFile *>& mfs, std::set<OksFile *>& rfs, const std::string& version);
const std::list<std::string>& get_repository_dirs() const;
void commit_repository(const std::string& comments, const std::string& credentials = "");
void tag_repository(const std::string& tag);
std::time_t get_repository_checkout_ts() const;
enum RepositoryUpdateType { DiscardChanges, MergeChanges, NoChanges };
void update_repository(const std::string& hash_val, RepositoryUpdateType update_type);  // "hash"
void update_repository(const std::string& param, const std::string& val, RepositoryUpdateType update_type); // "tag"|"date"|"hash"
std::list<std::string> get_repository_versions_diff(const std::string& sha1, const std::string& sha2);
std::list<std::string> get_repository_unmerged_files();  // == diff("","")
std::vector<OksRepositoryVersion> get_repository_versions(bool skip_irrelevant, const std::string& command_line);
std::vector<OksRepositoryVersion> get_repository_versions_by_hash(bool skip_irrelevant = true,
    const std::string& sha1 = "", const std::string& sha2 = "");
std::vector<OksRepositoryVersion> get_repository_versions_by_date(bool skip_irrelevant = true,
    const std::string& since = "", const std::string& until = "");
std::string read_repository_version();
static const char * get_cwd(); static void reset_cwd(); static void set_use_strict_repository_paths(bool);
std::string insert_repository_dir(const std::string& dir, bool push_back = true);
void remove_repository_dir(const std::string& dir);
const OksClass::Map & classes() const; size_t number_of_classes() const;
const OksObject::Set & objects() const; size_t number_of_objects() const;
OksClass * find_class(const std::string&) const; OksClass * find_class(const char *) const;
void get_all_classes(const std::vector<std::string>& names, ClassSet& classes_out) const;
void registrate_all_classes(bool skip_registered = false);
bool is_dangling(OksClass * class_ptr) const; bool is_dangling(OksObject * obj_ptr) const;
void subscribe_create_class(void (*f)(OksClass *));
void subscribe_change_class(void (*f)(OksClass *, OksClass::ChangeType, const void *));
void subscribe_delete_class(void (*f)(OksClass *));
void subscribe_create_object(OksObject::notify_obj, void * parameter);
void subscribe_change_object(OksObject::notify_obj, void *);
void subscribe_delete_object(OksObject::notify_obj, void *);
void bind_objects(); const std::string& get_bind_objects_status() const;
const std::string& get_bind_classes_status() const;
void unset_repository_created();
```

`OksRepositoryVersion` struct (kernel.hpp lines 514-530, verbatim):
```cpp
struct OksRepositoryVersion
{
  std::string m_commit_hash;
  std::string m_user;
  std::time_t m_date;
  std::string m_comment;
  std::vector<std::string> m_files;

  void clear()
  {
    m_commit_hash.clear();
    m_user.clear();
    m_date = 0;
    m_comment.clear();
    m_files.clear();
  }
};
```

`OksKernel` doc comment (kernel.hpp lines 532-579) summarizes the whole API surface, verbatim intro:
```
It is responsible for loading OKS data and schema files.  Multiple concurrent kernels....
 *  To work with OKS schema the following base methods are available:
 *   - load_schema() - load OKS schema from file (i.e. read description of classes with attributes, relationships and relationships)
...
 *  When schema or data are modified, the process can give callback ...
 *  - subscribe_create_class() - notify, when new class is created
 ...
 *  Most of the OksKernel methods are thread-safe. Those which are not thread-safe, are starting from prefix "k_".
```

### OksClass (class.hpp, 1099 lines) — public API verbatim:
```cpp
OksClass (const std::string& name, OksKernel * kernel, bool transient = false);
OksClass (const std::string& name, const std::string& description, bool is_abstract, OksKernel * kernel, bool transient = false);
OksClass (OksKernel * kernel, const std::string& name, const std::string& description, bool is_abstract); // fast internal
static void destroy(OksClass * c);
bool operator==(const OksClass&) const; bool operator!=(const OksClass&) const;
bool compare_without_methods(const OksClass & v) const noexcept;
OksKernel * get_kernel() const noexcept {return p_kernel;}
OksFile * get_file() const noexcept {return p_file;}
void set_file(OksFile * f, bool update_owner = true);
const std::string& get_name() const noexcept; const std::string& get_description() const noexcept;
void set_description(const std::string& description); bool get_is_abstract() const noexcept; void set_is_abstract(bool);
const FList * all_super_classes() const noexcept; const std::list<std::string *> * direct_super_classes() const noexcept;
OksClass * find_super_class(const std::string&) const noexcept; bool has_direct_super_class(const std::string&) const noexcept;
void add_super_class(const std::string& name); void k_add_super_class(const std::string&);
void remove_super_class(const std::string& name); void swap_super_classes(const std::string&, const std::string&);
const FList * all_sub_classes() const noexcept;
const std::list<OksAttribute *> * all_attributes() const noexcept;
const std::list<OksAttribute *> * direct_attributes() const noexcept;
OksAttribute * find_attribute(const std::string& name) const noexcept;
OksAttribute * find_direct_attribute(const std::string&) const noexcept;
void add(OksAttribute * a); void k_add(OksAttribute * a); void remove(const OksAttribute * a);
void swap(const OksAttribute * a1, const OksAttribute * a2);
size_t number_of_direct_attributes() const noexcept; size_t number_of_all_attributes() const noexcept;
OksClass * source_class(const OksAttribute * a) const noexcept;
const std::list<OksRelationship *> * all_relationships() const noexcept;
const std::list<OksRelationship *> * direct_relationships() const noexcept;
OksRelationship * find_relationship(const std::string& name) const noexcept;
OksRelationship * find_direct_relationship(const std::string&) const noexcept;
void add(OksRelationship * r); void k_add(OksRelationship * r); void remove(const OksRelationship * r, bool call_delete = true);
void swap(const OksRelationship * r1, const OksRelationship * r2);
size_t number_of_direct_relationships() const noexcept; size_t number_of_all_relationships() const noexcept;
OksClass * source_class(const OksRelationship * r) const noexcept;
// methods:
const std::list<OksMethod *> * all_methods() const noexcept; const std::list<OksMethod *> * direct_methods() const noexcept;
OksMethod * find_method(const std::string&) noexcept; void add(OksMethod *); void remove(const OksMethod *); void swap(...);
size_t number_of_objects() const noexcept; const OksObject::Map * objects() const noexcept;
std::list<OksObject *> * create_list_of_all_objects() const noexcept;
OksObject * get_object(const std::string& id) const noexcept; OksObject * get_object(const std::string* id) const;
OksObject::List * execute_query(OksQuery * query) const;                          // << QUERY API
OksDataInfo * data_info(const std::string&) const noexcept; OksDataInfo * get_data_info(const std::string&) const noexcept;
enum ChangeType { ChangeSuperClassesList, ChangeSubClassesList, ChangeDescription, ChangeIsAbstract,
    ChangeAttributesList, ChangeAttributeType, ChangeAttributeRange, ChangeAttributeFormat,
    ChangeAttributeMultiValueCardinality, ChangeAttributeInitValue, ChangeAttributeDescription, ChangeAttributeIsNoNull,
    ChangeRelationshipOther, ChangeRelationshipClassType, ChangeRelationshipDescription, ChangeRelationshipLowCC,
    ChangeRelationshipHighCC, ChangeRelationshipComposite, ChangeRelationshipExclusive, ChangeRelationshipDependent,
    ChangeMethodsList, ChangeMethodDescription, ChangeMethodImplementation };
typedef void (*NotifyFN)(OksClass *); typedef void (*ChangeNotifyFN)(OksClass *, ChangeType, const void *);
```

### OksObject (object.hpp) — full public API verbatim:
```cpp
OksObject (const OksClass * oks_class, const char * object_id = 0, bool skip_init = false);
OksObject (const OksObject & parent_object, const char * object_id = 0);
static void destroy(OksObject * obj, bool fast = false);
bool operator==(const OksObject&) const; static bool are_equal_fast(const OksObject*, const OksObject*);
bool operator!=(const OksObject&) const = delete;
const OksClass * GetClass() const; const std::string& GetId() const; void set_id(const std::string & id);
OksFile * get_file() const; void set_file(OksFile * file, bool update_owner = true);
OksData * GetAttributeValue(const std::string& name) const;
OksData * GetAttributeValue(const OksDataInfo *i) const noexcept;
OksData * GetRelationshipValue(const std::string&) const;
OksData * GetRelationshipValue(const OksDataInfo *i) const noexcept;
void SetAttributeValue(const std::string& name, OksData * data);
void SetAttributeValue(const OksDataInfo * data_info, OksData * data);
void SetRelationshipValue(const std::string& name, OksData * data, bool skip_non_null_check = false);
void SetRelationshipValue(const OksDataInfo * data_info, OksData * data, bool skip_non_null_check = false);
void SetRelationshipValue(const std::string& name, OksObject * object);
void SetRelationshipValue(const OksDataInfo * data_info, OksObject * object);
void AddRelationshipValue(const std::string& name, OksObject * object);
void AddRelationshipValue(const OksDataInfo * data_info, OksObject * object);
void RemoveRelationshipValue(const std::string& name, OksObject * object);
void RemoveRelationshipValue(const OksDataInfo * data_info, OksObject * object);
void SetRelationshipValue(const std::string& rel_name, const std::string& class_name, const std::string& object_id);
void AddRelationshipValue(const std::string& rel_name, const std::string& class_name, const std::string& object_id);
void RemoveRelationshipValue(const std::string& rel_name, const std::string& class_name, const std::string& object_id);
const std::list<OksRCR *> * reverse_composite_rels() const;   // RCR = reverse composite relationship
FList * get_all_rels(const std::string& name = "*") const;
void SetTransientData(void *d) const; void * GetTransientData() const;
void set_int32_id(int32_t object_id); int32_t get_int32_id() const;
bool SatisfiesQueryExpression(OksQueryExpression * query_exp) const;       // << QUERY
bool satisfies(const OksObject * goal, const QueryPathExpression& expression, OksObject::List& path) const;
OksObject::List * find_path(const QueryPath& query) const;              // << PATH-TO
bool is_consistent(const std::set<OksFile *>&, const char * msg) const;
std::string report_dangling_references() const;
void references(OksObject::FSet& refs, unsigned long recursion_depth, bool add_self = false, ClassSet * classes = 0) const;
bool is_duplicated() const;
```

`struct OksData` (object.hpp lines 454-748) — runtime typed value: `enum Type { unknown_type=0, s8..., u8..., s16..., u16..., s32..., u32..., s64..., u64..., float_type, double_type, bool_type, class_type, object_type, date_type, time_type, string_type, list_type, uid_type, uid2_type, enum_type }` — plus constructors per type, `Set*`/`ReadFrom*`/`str()`/`check_range()`/`set_init_value()`/comparison operators/`sort(bool ascending = true)`.

### OksAttribute (attribute.hpp, 723 lines) — public API verbatim:
```cpp
enum Format { Oct = 8, Dec = 10, Hex = 16 };
OksAttribute (const std::string& name, OksClass * p = nullptr);
OksAttribute (const std::string& name, const std::string& type, bool is_mv, const std::string& range,
              const std::string& init_v, const std::string& description, bool no_null,
              Format format = Dec, OksClass * p = nullptr);
const std::string& get_name() const noexcept;   void set_name(const std::string& name);
const std::string& get_type() const noexcept;   void set_type(const std::string& type, bool skip_init = false);
const std::string& get_range() const noexcept;  void set_range(const std::string& range);
static OksData::Type get_data_type(const std::string& type) noexcept;
static OksData::Type get_data_type(const char * type, size_t len) noexcept;
OksData::Type get_data_type() const noexcept;
Format get_format() const noexcept; void set_format(Format format);
bool is_integer() const noexcept;    bool is_number() const noexcept;
bool get_is_multi_values() const noexcept; void set_is_multi_values(bool);
const std::string& get_init_value() const noexcept; void set_init_value(const std::string&);
std::list<std::string> get_init_values() const;    // mv-init, "class_type" -> AttributeReadError
const std::string& get_description() const noexcept; void set_description(const std::string&);
bool get_is_no_null() const noexcept; void set_is_no_null(bool);
static bool find_token(const char * token, const char * range) noexcept;
int  get_enum_index(const char * s, size_t length) const noexcept;
int  get_enum_index(const std::string&) const noexcept;
const std::string * get_enum_value(const char * s, size_t length) const;
const std::string * get_enum_value(const std::string&) const;
uint16_t get_enum_value(const OksData& d) const noexcept;
const std::string * get_enum_string(uint16_t idx) const noexcept;
static const char * bool_type; static const char * s8_int_type; ... static const char * u64_int_type;
static const char * float_type; static const char * double_type; static const char * date_type;
static const char * time_type; static const char * string_type; static const char * uid_type;
static const char * enum_type; static const char * class_type;
static Format str2format(const char *) noexcept; static const char * format2str(Format) noexcept;
```

`set_range` doc (verbatim, notation UML): `"A,B,C..D,*..F,G..*"` means: `A`, `B`, `C..D` (closed interval), `*..F` (<=F), `G..*` (>=G); spaces not allowed; `enum` attrs must have non-empty range; `bool` has predefined range "true,false". Range validation implemented by `OksRange` class (attribute.hxx lines 36-90): conditions decomposed into `m_less, m_equal, m_interval, m_great, m_like(+) boost::regex` lists.

### OksRelationship (relationship.hpp, 406 lines) — public API verbatim + doc example:
```cpp
enum CardinalityConstraint { Zero, One, Many };
OksRelationship (const std::string& name, OksClass * p = nullptr);
OksRelationship (const std::string& name, const std::string& type, CardinalityConstraint low_cc,
                 CardinalityConstraint high_cc, bool composite, bool exclusive, bool dependent,
                 const std::string& description, OksClass * p = nullptr);
const std::string& get_name() const noexcept; void set_name(const std::string&);
OksClass * get_class_type() const noexcept;  const std::string& get_type() const noexcept; void set_type(const std::string&);
const std::string& get_description() const noexcept; void set_description(const std::string&);
CardinalityConstraint get_low_cardinality_constraint() const noexcept; void set_low_cardinality_constraint(CardinalityConstraint cc);
CardinalityConstraint get_high_cardinality_constraint() const noexcept; void set_high_cardinality_constraint(CardinalityConstraint);
bool get_is_composite() const noexcept;  void set_is_composite(bool);
bool get_is_exclusive() const noexcept;  void set_is_exclusive(bool);
bool get_is_dependent() const noexcept;  void set_is_dependent(bool);
static CardinalityConstraint str2card(const char *) noexcept; static const char * card2str(CardinalityConstraint) noexcept;
```

Conceptual doc paragraph (relationship.hpp lines 36-56, verbatim):
```
A relationship can be either a general (weak) or composite (strong) reference.
... A composite reference may be exclusive or shared (an exclusive object is component of only one object,
a shared object may be referenced by more than one object). ... a composite reference can be dependent or independent.
The existence of object, referenced though dependent composite reference, is dependent from existence of their composite parents.
The deleting of all composite parents results the deleting of their own composite child objects.
```

Code example (relationship.hpp lines 58-95) — `main()` showing construction & stream operator output; output:
```
Relationship name: "consists of"
 class type: "Element"
 low cardinality constraint is zero
 high cardinality constraint is many
 is composite reference
 is exclusive reference
 is dependent reference
 has description: "A structure consists of zero or many elements"
```

### OksIndex (index.hpp, 104 lines) — verbatim:
```cpp
class OksObjectSortBy { public: OksObjectSortBy(size_t i = 0) : offset(i) {};
    bool operator() (const OksObject * o1, const OksObject * o2) const { return o1->data[offset] < o2->data[offset]; } };

class OksIndex : public std::multiset<OksObject *, OksObjectSortBy> {
  public:
    struct SortByAttribute { ... };   typedef std::map<const OksAttribute *, OksIndex *, SortBy> Map;
    OksIndex (OksClass *, OksAttribute *);
    ~OksIndex ();
    OksObject *         FindFirst(OksData *d) const;
    OksObject::List *   FindEqual(OksData *d) const;         // equal_cmp
    OksObject::List *   FindLessEqual(OksData *d) const;     // less_or_equal_cmp
    OksObject::List *   FindGreatEqual(OksData *d) const;    // greater_or_equal_cmp
    OksObject::List *   FindLess(OksData *d) const;          // less_cmp
    OksObject::List *   FindGreat(OksData *d) const;         // greater_cmp
    OksObject::List *   FindLessAndGreat(...), FindLessAndGreatEqual(...), FindLessEqualAndGreat(...),
                        FindLessEqualAndGreatEqual(...), FindEqualAndEqual(...), FindEqualAndLess(...),
                        FindEqualAndLessEqual(...), FindEqualAndGreat(...), FindEqualAndGreatEqual(...);
    OksObject::List *   FindLessOrGreat(...), FindLessOrGreatEqual(...), FindLessEqualOrGreat(...),
                        FindLessEqualOrGreatEqual(...), FindEqualOrEqual(...), FindEqualOrLess(...),
                        FindEqualOrLessEqual(...), FindEqualOrGreat(...), FindEqualOrGreatEqual(...);
  private:
    OksClass * c; OksAttribute * a; size_t offset;
    void find_all(OksData *, OksQuery::Comparator) const;
    OksObject::List * find_all(bool, OksData *, OksQuery::Comparator, OksData *, OksQuery::Comparator) const;
    void find_interval(OksData *, OksQuery::Comparator, ConstPosition&, ConstPosition&) const;
    static size_t get_offset(OksClass *, OksAttribute *);
};
```

(Function-pointer complication is lifted from the CERN original; in this DUNE fork the comparator is a `std::function`. The complete member list is folded onto mnemonicized lines above.)

### OksFile (file.hpp, 821 lines) — public API verbatim:
```cpp
enum Mode { ReadOnly, ReadWrite };
enum FileStatus { FileNotModified, FileModified, FileWasNotSaved, FileRemoved };
void lock(); static void set_nolock_mode(bool nl);  // Nasty hack to allow code generation on the fly (off by default)
void unlock();
void add_include_file(const std::string& name);
void remove_include_file(const std::string& name);
void rename_include_file(const std::string& from, const std::string& to);
void add_comment(const std::string& text, const std::string& author);
void modify_comment(const std::string& creation_time, const std::string& text, const std::string& author);
void remove_comment(const std::string& creation_time);
const std::map<std::string, oks::Comment *>& get_comments() const;
void set_logical_name(const std::string& name); void set_type(const std::string& type);
const std::string& get_short_file_name() const; const std::string& get_full_file_name() const;
bool is_repository_file() const;
const std::string& get_repository_name() const;
const std::string& get_well_formed_name() const;
const std::string& get_lock_file() const; const std::string& get_logical_name() const;
const std::string& get_oks_format() const; long get_number_of_items() const; long get_size() const;
const std::string& get_created_by() const; const boost::posix_time::ptime get_creation_time() const;
const std::string& get_created_on() const; const std::string& get_last_modified_by() const;
const boost::posix_time::ptime get_last_modification_time() const; const std::string& get_last_modified_on() const;
bool is_locked() const; bool is_updated() const; bool is_read_only() const;
const std::list<std::string>& get_include_files() const;
void get_all_include_files(const OksKernel * kernel, std::set<OksFile *>& out);
FileStatus get_status_of_file() const; void update_status_of_file(bool update_local = true, bool update_repository = true);
bool get_lock_string(std::string& info) const;
static bool compare(const char * file1_name, const char * file2_name); bool compare(const char * name) const;
const OksFile * get_parent() const; OksFile * check_parent(const OksFile * parent_h);
```

Comment in file.hpp on `is_repository_file()` (verbatim): "If the `TDAQ_DB_REPOSITORY` env var is set and file is on it: GlobalRepository; if `TDAQ_DB_USER_REPOSITORY`: UserRepository; else NoneRepository." — detailing the G-version/repository concepts.

---

## E-1. CLI tools

### oks_dump (apps/oks_dump.cxx) — full usage banner (verbatim lines 43-84) and exit codes:

```text
Usage: oks_dump
    [--files-only | --files-stat-only | --schema-files-only | --schema-files-stat-only | --data-files-only | --data-files-stat-only]
    [--class name-of-class [--query query [--print-references recursion-depth [class-name*] [--]] [--print-referenced_by [name] [--]]]]
    [--path object-from object-to query]
    [--allow-duplicated-objects-via-inheritance]
    [--version]
    [--help]
    [--input-from-files] database-file [database-file...]

Options:
    -f | --files-only                                 print list of oks files names
    -F | --files-stat-only                            print list of oks files with statistic details (size, number of items)
    -s | --schema-files-only                          print list of schema oks files names
    -S | --schema-files-stat-only                     print list of oks schema files with statistic details
    -d | --data-files-only                            print list of data oks files names
    -D | --data-files-stat-only                       print list of oks data files with statistic details
    -c | --class class_name                           dump given class (all objects or matching some query)
    -q | --query query                                print objects matching query (can only be used with class)
    -r | --print-references N C1 C2 ... CX            print objects referenced by found objects (can only be used with query), where:
                                                          * the parameter N defines recursion depth for referenced objects (> 0)
                                                          * the optional set of names {C1 .. CX} defines [sub-]classes for above objects
    -b | --print-referenced_by [name]                 print objects referencing found objects (can only be used with query), where:
                                                          * the optional parameter name defines name of relationship
    -p | --path object-from path-expression           print path from object 'object-from' to object of path-expression
    -i | --input-from-files                           read oks files to be loaded from file(s) instead of command line
                                                      (to avoid problems with long command line, when there is huge number of files)
    -a | --allow-duplicated-objects-via-inheritance   do not stop if there are duplicated object via inheritance hierarchy
    -v | --version                                    print version
    -h | --help                                       print this text

Description:
    Dumps contents of the OKS database.

Return Status:
    0 - no problems found
    1 - bad command line parameter
    2 - bad oks file(s)
    3 - bad query passed via -q or -p options
    4 - cannot find class passed via -c option
    5 - loaded objects have dangling references
    6 - caught an exception
```

(Source has short forms -f/-F/-s/-S/-d/-D/-c/-q/-r/-b/-p/-i/-a/-v/-h; enum at lines 29-37: `__Success__=0, __BadCommandLine__, __BadOksFile__, __BadQuery__, __NoSuchClass__, __FoundDanglingReferences__, __ExceptionCaught__`.)

Query usage example from source (line 269): `OksQuery * q = new OksQuery(c, query); if(q->good()) { OksObject::List * objs = c->execute_query(q); ...}` — full flow shown above.

### oks_clone_repository (apps/oks_clone_repository.cxx, 84 lines) — verbatim usage text:

```text
usage: oks_clone_repository
    --branch=B | --version=V | --output-directory=D | --verbose | --help

By default the master branch is cloned. The branch is created. If TDAQ_DB_VERSION env var
is set, or versions via --version, the repository is checked-out for that hash/date/tag.
If TDAQ_DB_USER_REPOSITORY is set, the utility makes no effect.
```
(Literal banner from source, lines 30-35: `"Clone and checkout oks repo.\\n\\n...By default the master branch is checkout. The \\"branch\\" command line option can be used to specify particular one. A branch will be created, if does not exist yet. TDAQ_DB_VERSION process environment variable or \\"version\\" command line option can be used to specify particular version... If TDAQ_DB_USER_REPOSITORY process environment variable is set, the utility makes no effect."`)

Options (verbatim):
```text
  -b [ --branch ] arg            checkout or create given branch name
  -e [ --version ] arg          oks config version in type:value format, where type is "hash", "date" or "tag"
  -o [ --output-directory ] arg output directory; if not defined, create temporal
  -v [ --verbose ]              print verbose information
  -h [ --help ]                 print help message
```
Exit codes: `EXIT_SUCCESS` (0) on success; `EXIT_FAILURE` (1) on command line parsing error. It sets env `TDAQ_DB_USER_REPOSITORY_PATH` from `--output-directory` before constructing the kernel; prints the created user repository root to stdout when no output dir given.

### oks_check_schema (apps/oks_check_schema.cxx, 176 lines) — DUNE-written (2025) integrity checker. Verbatim:

```text
Options: -f, --file (required)   Schema file

Return codes:
  0 Success, file is OK
  1 Bad command line
  2 Failed to find file
  3 Failed to load file -- invalid schema
  4 File contains relationship to non loaded class
  5 File contains object with relationship to non loaded class/object
  6 File refers to class in file not directly included
```
Behavior: loads file; works on `*.schema.xml` (checks every class in it: superclass existence implied by load success, direct relationship class type loaded (`rel->get_class_type() == nullptr` → `Exitcode::BADRELATIONSHIP`), and `file->get_include_files()` coverage → `MISSING_INCLUDE`), and on `*.data.xml` (checks each object's class's schema-file inclusion, and every relationship target object's file inclusion); finally `kernel.get_bind_objects_status()` non-empty → `UNRESOLVED`.

### oks_validate_repository (apps/oks_validate_repository.cxx, 464 lines) — repo pre-receive hook validator. Verbatim options:

```text
usage: oks_validate_repository
  -a [ --add ] arg                 list of new OKS files and directories to be added to the repository
  -u [ --update ] arg              list of new OKS files and directories to be updated in the repository
  -r [ --remove ] arg              list of new OKS files and directories to be removed from the repository
  -C [ --permissive-circular-dependencies-between-includes ]
                                   downgrade severity of detected circular dependencies between includes from errors to warnings
  -U [ --user ] arg                user id
  -t [ --threads-number ] (=4)     number of threads used by validation pipeline
  -v [ --verbose ]                 print debug information
  -h [ --help ]                    print help message
```
Exit codes enum (lines 32-43): `__Success__=0, __BadCommandLine__=1, __UserAuthenticationFailure__=2, __NoRepository__=3, __ConsistencyError__=4, __IncludesCircularDependencyError__=5, __NoIncludedFile__=6, __ExceptionCaught__=7` (names in source: `__Success__`/`__BadCommandLine__`/`__UserAuthenticationFailure__`/`__NoRepository__`/`__ConsistencyError__`/`__IncludesCircularDependencyError__`/`__NoIncludedFile__`/`__ExceptionCaught__`). Behavior: requires `TDAQ_DB_REPOSITORY` env; runs `get_includes()` on every file (skipping `.git`, `admin`, `README.md`), checks every include exists, builds transitive include graph and circular dependency detection, then validates every create/update file (and files whose includes changed) via `OksPipeline` parallel jobs that `load_file()` in silence mode and inspect bind status.

### oks_git_repository (apps/oks_git_repository.cxx, 35 lines) — verbatim:
```text
Usage: oks_git_repository [-h|--help]
   Prints repository root from $TDAQ_DB_REPOSITORY to stdout
```

---

## G-1. Python bindings (pybindsrc/module.cpp, 248 lines) — exposed surface

Module name: `_daq_oks_py`, wrapped by `python/oks/__init__.py` (`from ._daq_oks_py import *`). Verbatim binding list:

```cpp
PYBIND11_MODULE(_daq_oks_py, m)
{
  m.doc() = "C++ implementation of the application dal modules";

  py::class_<OksFile>(m, "OksFile");
  py::class_<OksClass, std::unique_ptr<OksClass, py::nodelete>>(m, "OksClass")
      .def("get_name",&OksClass::get_name, py::return_value_policy::reference_internal)
      .def("get_description",&OksClass::get_description, ...)
      .def("get_is_abstract",&OksClass::get_is_abstract)
      .def("all_super_classes",&OksClass::all_super_classes, ...)
      .def("direct_super_classes",&OksClass::direct_super_classes, ...)
      .def("all_sub_classes",&OksClass::all_sub_classes, ...)
  ;
  py::class_<OksObject, std::unique_ptr<OksObject, py::nodelete>>(m, "OksObject");

  py::class_<OksKernel>(m, "OksKernel")
      .def(py::init<bool, bool, bool, bool, const char *, std::string>(),
        "silence_mode"_a = false, "verbose_mode"_a = false, "profiling_mode"_a = false,
        "allow_repository"_a = true, "version"_a = nullptr, "branch_name"_a = "")
      .def("get_host_name",...).def("get_domain_name",...).def("get_user_name",...)
      .def("get_verbose_mode"/"set_verbose_mode")
      .def("get_silence_mode"/"set_silence_mode")
      .def("set_profiling_mode")
      .def("get_allow_duplicated_classes_mode"/"set_allow_duplicated_classes_mode")
      .def("get_allow_duplicated_objects_mode"/"set_allow_duplicated_objects_mode")
      .def("get_test_duplicated_objects_via_inheritance_mode"/"set_...")
      .def("find_schema_file"/"find_data_file")
      .def("create_list_of_schema_classes"/"create_list_of_data_objects")
      .def("create_file_info")
      .def("get_file_path","path"_a,"parent_file"_a=nullptr,"strict_path"_a=true)
      .def("get_repository_version")
      .def("is_user_repository_created")
      .def("get_user_repository_root"/"set_user_repository_root")
      .def("get_includes")
      .def("load_file","name"_a,"bind"_a=true)
      .def("load_schema","name"_a,"parent"_a=nullptr)
      .def("new_schema","name"_a)
      .def("backup_schema","pf"_a,"suffix"_a=".bak")
      .def("save_as_schema"/"save_all_schema"/"close_schema"/"close_all_schema"/"set_active_schema"/"get_active_schema")
      .def("schema_files")
      .def("load_data","name"_a,"bind"_a=true)
      .def("reload_data","files"_a,"allow_schema_extension"_a=true)
      .def("new_data","name"_a,"logical_name"_a="","type"_a="")
      .def("save_all_data","force_defaults"_a=false)
      .def("close_all_data")
      .def("set_active_data"/"get_active_data"/"data_files")
      .def("insert_repository_dir"/"remove_repository_dir")
      .def("classes"/"number_of_classes"/"objects"/"number_of_objects")
      .def("find_class",static_cast<OksClass*(OksKernel::*)(const std::string&) const>(&OksKernel::find_class), "class_name"_a)
      .def("registrate_all_classes")
      .def("bind_objects").def("get_bind_objects_status").def("get_bind_classes_status")
      .def("unset_repository_created")
  ;
}
```

Note: the OksData/OksQuery classes are NOT exposed; commented-out placeholders in the file (lines 46-66, 138-139, 168-197) show future intent (load_data/save_data with overloads, commit_repository/tag_repository/get_repository_versions, etc.)

---

## G-2. Versioning — repository env vars and git helpers

Env vars referenced by source code (kernel.hpp / file.hpp / apps):
- `TDAQ_DB_REPOSITORY` — global (server) repository root; git-based
- `TDAQ_DB_USER_REPOSITORY` — per-user checkout dir (used by all oks-*.sh)
- `TDAQ_DB_PATH` — extra search path for data files (get_file_path docs)
- `OKS_DB_ROOT` — old-style OKS root
- `TDAQ_DB_VERSION` — version selector (used by oks_clone_repository)
- `OKS_KERNEL_VERBOSE`, `OKS_KERNEL_SILENCE`, `OKS_KERNEL_PROFILING`, `OKS_KERNEL_ALLOW_DUPLICATED_CLASSES`, `OKS_KERNEL_ALLOW_DUPLICATED_OBJECTS`, `OKS_KERNEL_TEST_DUPLICATED_OBJECTS_VIA_INHERITANCE`, `OKS_KERNEL_SKIP_STRING_RANGE` — mode toggles.

Script family (all `scripts/*.sh`), usage banners verbatim:

- `oks-checkout.sh`: `Usage: oks-checkout.sh [-v] [-u user-repository-dir] [-b branch] [-c commit-hash] [-t tag] [-d date] [-h]` — "checkout files and directories from OKS git repository into user repository..." (TDAQ_DB_REPOSITORY = git repo, TDAQ_DB_USER_REPOSITORY = user dir; else cwd).
- `oks-update.sh`: `Usage: oks-update.sh [-v] [-u user-repository-dir] [-c commit-hash] [-t tag] [-d date] [-f | -m] [-h]` — update to HEAD of master by default; `-f|--force|--discard` vs `-m|--merge`.
- `oks-commit.sh`: `Usage: oks-commit.sh [-v] [-u user-repository-dir] [-h] -m message | -f commit-message-file` — commits xml files via temp branch `temp_oks_commit_branch`, pull --rebase, push with lock-conflict retry. Exit codes 1-4 (error / cleanup / undo_merge / undo_exit).
- `oks-tag.sh`: `Usage: oks-tag.sh [-v] [-u user-repository-dir] [-h] -c sha -t tag` — "tag existing commit".
- `oks-import.sh`: `Usage: oks-import.sh [-v] [-t] [-n] -m message | -f commit-message-file what ...` — import files/dirs into git repo; `-n` dry-run.
- `oks-copy.sh`: `Usage: oks-copy.sh -s source-dir -d destination-dir -c commit-hash [-h]` — clone part of repo at given hash.
- `oks-diff.sh`: `Usage: oks-diff.sh [-v] [-u user-repository-dir] [--unmerged] [--sha sha1 sha2] [-h]` — diff between repository versions.
- `oks-log.sh`: `Usage: oks-log.sh [-v] [-u user-repository-dir] [-h] [-s date/time] [-t date/time] [-n num]` — show repository versions (git log).
- `oks-version.sh`: `Usage: oks-version.sh [-u user-repository-dir] [-h]` — prints `oks version <git rev-parse HEAD>` (verbatim line 53).
- `oks-status.sh`: `Usage: oks-status.sh [-u user-repository-dir] [-h]` — repo status.
- `oks-edit-branch.sh`: `Usage: oks-edit-branch.sh [-c] [-p directory] [-e editor] [-m "log message"] -b branch file+` — edit files on branch.