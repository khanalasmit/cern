# 04 — OksQuery and Configuration Mutation (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

---

## 1. Executive summary

**`OksQuery` is read-only, and the separation from mutation is structural, not conventional.**
Query and mutation live in different classes with different entry points:

- `OksQuery` / `OksClass::execute_query()` — parse, validate against schema, walk objects,
  return a list. No writer is reachable from this path.
- `OksObject::SetValue()` / `SetRelationshipValue()` / `OksObject::destroy()` and, at the
  `config` layer, `Configuration::create()` / `destroy_obj()` / `ConfigObject::set_*()` —
  the mutation API, entirely disjoint from the query API.

Persistence is a **third**, separately-invoked step (`save_data()` / `commit()`), and
publishing to Git requires an explicit `commit_repository()` that runs a validation and
authorization gate.

**Therefore a read-only first prototype is not merely advisable — it is the natural shape of
the API.** Building read-only requires *omitting* calls, not adding guards.

## 2. OksQuery implementation

### 2.1 Declaration and expression model

`OksQuery` (`oks/oks/query.h:33–95`) holds a flag and a parse tree:

```cpp
class OksQuery {
  public:
    OksQuery(bool b, OksQueryExpression *q = 0);
    OksQuery(const OksClass *, const std::string &);   // parse from string
    bool search_in_subclasses() const;
    bool good() const {return (p_status == 0);}
    enum QueryType { unknown_type, comparator_type, relationship_type,
                     not_type, and_type, or_type };
  private:
    bool p_sub_classes;
    OksQueryExpression * p_expression;
    int p_status;
    static OksQueryExpression * create_expression(const OksClass *, const std::string &);
};
```

Expression node types (`oks/oks/query.h:134–300`):

| Node | Class | Holds |
|---|---|---|
| comparator | `OksComparator` | `const OksAttribute*`, `OksData* value`, comparator function pointer |
| relationship | `OksRelationshipExpression` | `const OksRelationship*`, nested expression, `checkAllObjects` flag |
| not | `OksNotExpression` | one nested expression |
| and / or | `OksAndExpression` / `OksOrExpression` | list of expressions |

Note `OksComparator` holds the attribute as `const OksAttribute *`
(`oks/oks/query.h:169`) — the query cannot alter the schema element it references.

### 2.2 Accepted expressions — the grammar

Keywords are string constants (`oks/src/query.cpp:15–31`):

```cpp
const char * OksQuery::OR             = "or";
const char * OksQuery::AND            = "and";
const char * OksQuery::NOT            = "not";
const char * OksQuery::SOME           = "some";
const char * OksQuery::THIS_CLASS     = "this";
const char * OksQuery::ALL_SUBCLASSES = "all";
const char * OksQuery::OID            = "object-id";
const char * OksQuery::EQ             = "=";
const char * OksQuery::NE             = "!=";
const char * OksQuery::RE             = "~=";
const char * OksQuery::LE             = "<=";
const char * OksQuery::GE             = ">=";
const char * OksQuery::LS             = "<";
const char * OksQuery::GT             = ">";
const char * OksQuery::PATH_TO        = "path-to";
const char * OksQuery::DIRECT         = "direct";
const char * OksQuery::NESTED         = "nested";
```

**The operand order is unusual and must be stated exactly.** From the parser
(`oks/src/query.cpp:333–420`), a comparator expression is parsed as three tokens
`first second third`, where:

- `first` = **attribute name** (or the literal `object-id`),
- `second` = **the value**,
- `third` = **the comparator**.

> `oks/src/query.cpp:379` — `OksAttribute *a = ((first != OksQuery::OID) ? c->find_attribute(first) : 0);`
> `oks/src/query.cpp:392–401` — `third` is mapped to the comparator function.
> `oks/src/query.cpp:407` — `d->SetValues(second.c_str(), a);`

So the form is **`(<attribute> <value> <operator>)`**, e.g. `(Name "MyApp" =)` — *not*
`(Name = "MyApp")`. **Confidence: Confirmed.** This is the single most likely thing for an
LLM to get wrong, and it is why generated queries must be validated (§7).

A relationship expression is `(<relationship> some|all <nested-expression>)`
(`oks/src/query.cpp:339–376`), and `and`/`or` take two or more sub-expressions
(`oks/src/query.cpp:280–300`). Tokens may be quoted with `"`, `'` or `` ` ``
(`oks/src/query.cpp:208–228`); parenthesised groups are matched by bracket counting
(`oks/src/query.cpp:231–257`).

A separate query form, `QueryPath` (`oks/oks/query.h:~340–400`), computes a *path between
objects* — `"(path-to \"my-id@my-class\" (direct \"A\" \"B\" (nested \"N\" (direct \"X\" \"Y\" \"Z\"))))"`
— and is surfaced at the `config` layer as
`Configuration::get(obj_from, query, objects, ...)` (`config/config/Configuration.h:716`).

### 2.3 Validation — parsing is schema-checked

This is the most valuable property of the implementation for this project. The parser
resolves every name against the **loaded schema**, and fails if it cannot:

> `oks/src/query.cpp:341–349` (relationship must exist on the class)
> ```cpp
> OksRelationship *r = c->find_relationship(first);
> if(!r) {
>   Oks::error_msg(fname) << "For expression \"" << str << "\"\n"
>        "can't find relationship \"" << first << "\" in class \"" << c->get_name() << "\"\n";
>   return qe;
> }
> ```
> `oks/src/query.cpp:363–370` (the relationship's target class must exist)
> ```cpp
> OksClass *relc = c->get_kernel()->find_class(r->get_type());
> if(!relc) { ... "can't find class \"" << r->get_type() << "\"" ... }
> ```
> `oks/src/query.cpp:379–387` (attribute must exist on the class)
> ```cpp
> OksAttribute *a = ((first != OksQuery::OID) ? c->find_attribute(first) : 0);
> if(first != OksQuery::OID && !a) { ... "can't find attribute \"" << first
>      << "\" in class \"" << c->get_name() << "\"" ... }
> ```
> `oks/src/query.cpp:415–417` (comparator must be one of the seven)
> ```cpp
> if(!f) Oks::error_msg(fname) << ... "can't find comparator function \"" << third << "\"";
> ```

Failure sets `p_status` non-zero, so `OksQuery::good()` returns false, and `oksconfig`
converts that into a `daq::config::Generic("bad query syntax ... in scope of class ...")`
(`oksconfig/src/OksConfiguration.cpp:706–710`).

A second, structural check runs at execution time:

> `oks/src/query.cpp:441–444`
> ```cpp
> if(sqe->CheckSyntax() == false) {
>   Oks::error_msg(fname) << "Can't execute query \"" << *sqe << "\"\n";
>   return 0;
> }
> ```
(`OksQueryExpression::CheckSyntax()`, `oks/src/query.cpp:543–620`, recurses the tree.)

**Confidence: Confirmed.**

**Implication for the MCP prototype.** There is a **free, exact, schema-aware validator**:
construct the query against the class and check `good()`. No re-implementation of OKS
semantics is needed, and no guessing about whether an attribute exists.

### 2.4 Execution — and the proof that it is read-only

> `oks/src/query.cpp:431–535` — `OksClass::execute_query(OksQuery *qe) const`

The method is `const`. Its body does exactly three things:

1. Validate (`CheckSyntax`, above).
2. If an index exists for a comparator's attribute, use it:
   `olist = (*j).second->find_all(cq->GetValue(), cq->GetFunction());`
   (`oks/src/query.cpp:452–455`), with a two-comparator `and`/`or` fast path
   (`oks/src/query.cpp:466–490`).
3. Otherwise iterate objects and test each:
   > `oks/src/query.cpp:491–505`
   > ```cpp
   > for(OksObject::Map::iterator i = p_objects->begin(); i != p_objects->end(); ++i) {
   >   OksObject *o = (*i).second;
   >   try {
   >     if(o->SatisfiesQueryExpression(sqe) == true) {
   >       if(!olist) olist = new OksObject::List();
   >       olist->push_back(o);
   >     }
   >   }
   >   catch(oks::exception& ex) { throw oks::QueryFailed(*sqe, *this, ex); }
   >   ...
   > ```
   and repeats the loop over subclasses when `search_in_subclasses()` is set
   (`oks/src/query.cpp:511–533`).

`OksObject::SatisfiesQueryExpression()` (`oks/src/query.cpp:630–770`) likewise only reads —
it compares `OksData` values and recurses through relationships.

**What this proves.** The only heap effect of executing a query is the returned
`OksObject::List`. No object, class, file or kernel state is modified.
**`OksQuery` is read-only. Confidence: Confirmed.**

### 2.5 Result type, errors, indexes, tools

- **Results**: `OksObject::List *` — a list of pointers to objects already in the kernel,
  or `nullptr` when nothing matched (`oks/src/query.cpp:437, :534`). The caller owns the
  list, not the objects (`oksconfig/src/OksConfiguration.cpp:719–723` deletes the list only).
- **Errors**: `oks::QueryFailed` thrown from execution; `oks::bad_query_syntax` from
  `QueryPath` parsing (`oks/oks/query.h:~305–320`); plain `Oks::error_msg` + `good()==false`
  from `OksQuery` string parsing. **Note the inconsistency**: the main query parser reports
  by return-status, while `QueryPath` throws. An MCP must handle both.
- **Indexes**: `OksIndex` (`oks/oks/index.h`, `oks/src/index.cpp`) accelerates comparator
  queries on indexed attributes; purely an optimisation.
- **Tools**: `oks_dump` accepts a query on the command line —
  > `oks/bin/oks_dump.cpp:262–266`
  > ```cpp
  > if(query && *query) {
  >   OksQuery * q = new OksQuery(c, query);
  >   if(q->good()) {
  >     OksObject::List * objs = c->execute_query(q);
  > ```
- **Tests**: `oks/test/test_update.cpp`, with `oks/test/all_types.schema.xml` and
  `oks/test/test.data.xml`.

## 3. Mutation APIs

Mutation is available at three levels. None of them is reachable from `OksQuery`.

### 3.1 `oks` level — `OksObject`, `OksClass`, `OksKernel`

> `oks/oks/object.h`
> ```cpp
> void SetValue(const char * s, const OksAttribute * a);                       // :601
> void SetValues(const char *, const OksAttribute * a);                        // :607
> static void destroy(OksObject * obj, bool fast = false);                     // :937
> void set_file(OksFile * file, bool update_owner = true);                     // :1037
> void SetRelationshipValue(const std::string& name, OksData * data, bool skip_non_null_check = false);  // :1155
> void SetRelationshipValue(const std::string& name, OksObject * object);      // :1186
> void AddRelationshipValue(const std::string& name, OksObject * object);      // :1217
> void RemoveRelationshipValue(const std::string& name, OksObject * object);   // :1247
> ```

`OksObject::destroy()` is documented at `oks/oks/object.h:926` as
*"the only way available to user to destroy OKS object since ~OksObject() is private"* —
i.e. destruction is deliberately funnelled through one static method.

Schema mutation exists too (`OksClass` add/remove attribute/relationship; `new_schema()`).

### 3.2 `config` level — `Configuration`, `ConfigObject`

> `config/config/Configuration.h`
> ```cpp
> void create(const std::string& at, const std::string& class_name, const std::string& id, ConfigObject& object);  // :568
> void create(const ConfigObject& at, const std::string& class_name, const std::string& id, ConfigObject& object); // :585
> template<class T> const T * create(const std::string& at, const std::string& id, bool init_object = false);      // :602
> void destroy_obj(ConfigObject& object);                                                                          // :632
> template<class T> void destroy(T& obj);                                                                          // :645
> void create(const std::string& db_name, const std::list<std::string>& includes);   // new database  :1102
> ```
> `config/config/ConfigObject.h`
> ```cpp
> void set_obj(...);      // :302        void set_objs(...);    // :318
> template<class T> void set_by_val(...);  // :344   set_by_ref(...);  // :365
> void set_enum(...);  // :382    set_class(...);  // :399    set_date(...);  // :416    set_time(...);  // :433
> ```

### 3.3 Python level

The Python binding exposes mutation as well as reading:
`create_obj`, `destroy_obj`, `create_db`, `add_dal`, `update_dal`, `destroy_dal`,
`add_include`, `remove_include`
(`config/python/config/Configuration.py:213, :253, :271, :302, :339, :401, :574, :590`).

**This matters for the MCP:** the Python API a prototype would use is *not* a read-only API.
Read-only is the MCP's responsibility (§8).

## 4. Persistence

Modification in memory and persistence are separate, and persistence to Git is separate
again.

| Step | API | Evidence |
|---|---|---|
| Write objects to XML | `OksKernel::save_data(OksFile*, ...)`, `save_data(OksFile*, const OksObject::FSet&)` | `oks/oks/kernel.h:1383, :1399` |
| Write schema to XML | `OksKernel::save_schema(...)` | `oks/oks/kernel.h:1119, :1137` |
| Create new files | `new_data()`, `new_schema()` | `oks/oks/kernel.h:1365, :1102` |
| Commit at `config` level | `Configuration::commit(log_message, credentials)` | `config/config/Configuration.h:1217` |
| Publish to Git | `OksKernel::commit_repository(comments, credentials)` → `oks-commit.sh` | `oks/oks/kernel.h:1599`; `oks/src/kernel.cpp:6127` |
| Tag | `OksKernel::tag_repository(tag)` → `oks-tag.sh` | `oks/src/kernel.cpp:6278` |
| List uncommitted files | `Configuration::get_updated_dbs(...)` | `config/config/Configuration.h:1180–1184` |
| Rollback | documented at `config/config/Configuration.h:1223` | |

**Git *is* involved — proven, not assumed.** `commit_repository()` builds the command
`oks-commit.sh` and runs it (`oks/src/kernel.cpp:6127`), and that script performs real Git
operations: `git rev-parse --abbrev-ref HEAD` (:172–173), `git checkout -b $temp` (:178–179),
`git pull --no-edit -r origin $branch` (:87–88), with rollback paths using
`git rebase --skip`, `git reset HEAD~`, `git branch -D` (:47, :58, :75).

**Confidence: Confirmed.**

## 5. C1 — What are OksQuery's capabilities; can it mutate objects?

**Repository finding.** Capabilities: attribute comparison with seven operators
(`=`, `!=`, `~=` regex, `<=`, `>=`, `<`, `>`), object-id matching, boolean composition
(`and`, `or`, `not`), traversal into relationships (`some` / `all`), optional inclusion of
subclasses, and a separate `path-to` form. **It cannot mutate**: see §2.4.

**Evidence.** `oks/src/query.cpp:15–31` (operators), `:431–535` (`const`, read-only
execution), `:630–770` (predicate evaluation), `oks/oks/query.h:169` (`const OksAttribute*`).

**Confidence: Confirmed.**

## 6. C2 — Which APIs create, modify and delete OKS objects?

**Repository finding.** §3 above: `OksObject` setters + `OksObject::destroy()` at kernel
level; `Configuration::create()` / `destroy_obj()` and `ConfigObject::set_*()` at config
level; the same operations re-exported in Python.

**Confidence: Confirmed.**

## 7. C3 — Architectural separation between querying and modifying

**Repository finding. The separation is real and enforced by class design.**

| Aspect | Query path | Mutation path |
|---|---|---|
| Entry point | `OksClass::execute_query()` (`const`) | `OksObject::Set*` / `destroy()` (non-const, static) |
| Owning class | `OksQuery`, `OksClass` | `OksObject`, `OksKernel`, `OksClass` (schema) |
| Schema element access | `const OksAttribute *` | non-const |
| Effect | returns a list | changes in-memory state |
| Reaching disk | never | only via a separate `save_data()` |
| Reaching Git | never | only via a separate `commit_repository()` |
| Authorization | none | token + AccessManager at commit (§9) |

**Confidence: Confirmed** — with the caveat that this is separation *by construction*, not
by an access-control flag. There is no "open read-only" mode (document `03` §11).

## 8. C4 — Should a first MCP prototype be read/query-only?

**Yes, and the repository evidence supports it on four independent grounds:**

1. **The query API cannot mutate** (§2.4), so a query-only MCP has no accidental-write path
   through its main function.
2. **Mutation is a different, separately-invoked API** (§3) — read-only is achieved by not
   calling those methods, not by defending against them.
3. **Publishing requires more than code**: a commit needs credentials, passes a token +
   AccessManager authorization gate, and rebases against origin (§9). A prototype would have
   to acquire production write credentials to mutate anything — a large operational ask.
4. **Historical configurations have no write protection** (document `03` §11), so a
   mutation-capable prototype pointed at a historical checkout carries real risk with no
   library-level backstop.

**Confidence: Confirmed** for grounds 1–3; ground 4 is Confirmed as a *risk statement*.

## 9. D1–D4 — Existing tools, revisions, target API, validation

### D1 — Existing GUI/CLI/API tools for creating and modifying configurations

| Tool | Kind | Evidence |
|---|---|---|
| `dbe` | GUI database editor | package `dbe`, pin `3dd750d2…` |
| `oks_dump` | CLI reader (with query) | `oks/bin/oks_dump.cpp` |
| `oks_validate_repository` | CLI validator | `oks/bin/oks_validate_repository.cpp` |
| `oks_clone_repository`, `oks_git_repository` | CLI repository helpers | `oks/bin/` |
| `oks-*.sh` (11 scripts) | Git operations: checkout, commit, update, tag, diff, log, status, copy, import, edit-branch, version | `oks/scripts/` |
| `config_dump`, `config_export_schema`, `config_export_data` | CLI over `config` | `config/bin/` |
| `PartitionMaker` | configuration generation (ships 20 `.data.xml`) | package `PartitionMaker` |
| C++ / Python / Java APIs | §3 | |

**Confidence: Confirmed** for existence. Whether any is *the* recommended interface is
**Not established from the new-release repository.**

### D2 — How does a modification become a Git revision?

`Configuration::commit()` → `OksKernel::commit_repository()` → `oks-commit.sh`, which
creates a temporary branch, commits, rebases onto `origin/<branch>`, and pushes; on conflict
it undoes via `git rebase --skip` / `git reset HEAD~` / `git branch -D`
(`oks/scripts/oks-commit.sh:43–88, :172–179`).

**Confidence: Confirmed.**

### D3 — Which API should a future NL modification system call?

**Repository finding.** `config::Configuration` — `create()`, `destroy_obj()`,
`ConfigObject::set_*()`, then `commit()`. Rationale from evidence: it is the layer that both
the Python and Java bindings and `webis_server` already use, and it is the layer that owns
`commit()` with credentials (`config/config/Configuration.h:1203–1217`).

**Confidence: Strongly indicated** — the repository shows this is *the common* layer; it does
not state a recommendation. Flagged as an **engineering proposal**, and an expert question.

### D4 — What validation happens before a changed configuration is accepted?

**Repository finding.** `oks_validate_repository` performs a combined
**authentication + authorization + consistency** gate.

**Evidence.** `oks/bin/oks_validate_repository.cpp`:
- Authentication by DAQ token: `#include <daq_tokens/verify.h>` (:19);
  `user = daq::tokens::verify(token).get_subject();` (:303).
- Authorization via AccessManager XACML on a `DBResource`
  (:21–24), with dedicated exit codes `__AccessManagerAuthorizationFailed__` and
  `__AccessManagerNoPermission__` (:37–38).
- Consistency: `__ConsistencyError__` (:35), `__NoIncludedFile__` (:41),
  and circular-include detection `__IncludesCircularDependencyError__` (:36), reported at
  :190–195, downgradable by `--permissive-circular-dependencies-between-includes` (:266, :283–284).

**Confidence: Confirmed** that the tool exists and performs these checks.
**Not established from the new-release repository:** whether the OKS Git server enforces it
as a hook — i.e. whether a commit that bypasses the tool would be rejected. *Searched:*
`oks/scripts/oks-commit.sh` for a call to `oks_validate_repository` — **there is none**;
the script performs Git operations only. So the validator appears to be a tool an operator
or CI runs, not an inline gate in the commit path.

## 10. Answers to the extra questions

| Question | Answer | Confidence |
|---|---|---|
| Is OksQuery read-only? | Yes — `execute_query()` is `const` and only collects matches | Confirmed |
| What is the actual mutation API? | `OksObject` setters + `destroy()`; `Configuration::create`/`destroy_obj`; `ConfigObject::set_*` | Confirmed |
| What validation exists? | (a) schema-aware query parsing; (b) `CheckSyntax()`; (c) `oks_validate_repository` token+XACML+consistency gate | Confirmed |
| What tools use these APIs? | `oks_dump`, `config_dump`, `dbe`, `PartitionMaker`, `oks-*.sh`, Python/Java bindings | Confirmed |

## 11. Read-only prototype implications

1. **Use query construction as the validator.** `OksQuery(cl, text)` + `good()` gives exact,
   schema-aware validation with a class-scoped error message, for free.
2. **Generate `(class, query)` pairs, never a bare query.** The class is a separate argument
   at every layer (`Configuration::get`, `OksConfiguration::get`, `OksQuery` ctor).
3. **Get the operand order right — `(attribute value operator)`.** This is the highest-risk
   detail for an LLM (§2.2).
4. **Treat empty query as a distinct "list all" case** — `oksconfig` branches on it
   (`oksconfig/src/OksConfiguration.cpp:700–702`).
5. **Expose no mutating call.** The Python API offers mutation freely (§3.3); the MCP tool
   surface must simply not include it.
6. **Expect two error styles** — status-flag for `OksQuery`, exceptions for `QueryPath` and
   for execution failures (§2.5).

## 12. Unknowns

1. Whether `oks_validate_repository` is enforced server-side (§D4).
2. Whether `dbe` performs additional validation beyond the kernel's — `dbe` was inventoried
   but its validation logic was not traced. **Not established from the new-release repository.**
3. Whether regex comparison `~=` uses ECMAScript or POSIX semantics. `OksComparator` holds a
   `boost::regex *` (`oks/oks/query.h:172`) but the construction flags were not traced.
   Relevant because an LLM will emit regexes. **Not established from the new-release repository.**
4. Whether indexes exist on the production configuration's attributes (affects query cost,
   not correctness).

## 13. Evidence index

| File | Symbols / lines |
|---|---|
| `oks/oks/query.h` | `OksQuery` :33–95; `QueryType` :51–58; keyword decls :62–77; `OksComparator` :134–180; `OksRelationshipExpression` :190–225; `OksNotExpression` :230–250; and/or :275–300; `bad_query_syntax`, `QueryPath` :305–400 |
| `oks/src/query.cpp` | keywords :15–31; `OksQuery(class,string)` :85; `create_expression` :182–425 (tokeniser :208–257, and/or :280–300, relationship :339–376, comparator :377–420); `execute_query` :431–535; `CheckSyntax` :543–620; `SatisfiesQueryExpression` :630–770 |
| `oks/oks/object.h` | `SetValue` :601; `SetValues` :607; `destroy` :926–937; `set_file` :1037; relationship mutators :1155–1310 |
| `oks/oks/kernel.h` | `new_schema` :1102; `save_schema` :1119, :1137; `new_data` :1365; `save_data` :1383, :1399; `commit_repository` :1599 |
| `oks/src/kernel.cpp` | `commit_repository` :6127; `tag_repository` :6278 |
| `oks/scripts/oks-commit.sh` | undo paths :43–75; `git pull -r` :87–88; branch detection :172–173; temp branch :178–179 |
| `oks/bin/oks_dump.cpp` | query execution :262–266 |
| `oks/bin/oks_validate_repository.cpp` | includes :19–24; exit codes :31–41; circular-dependency report :165–195; options :250–284; token verify :303 |
| `config/config/Configuration.h` | `create` :568, :585, :602, :1102; `destroy_obj` :632; `destroy` :645; path query :716; `get_updated_dbs` :1180; credentials :1203; `commit` :1217; rollback :1223 |
| `config/config/ConfigObject.h` | setters :302–468 |
| `config/python/config/Configuration.py` | mutation surface :213, :253, :271, :302, :339, :401, :574, :590 |
| `oksconfig/src/OksConfiguration.cpp` | empty-query branch :700–702; parse+error :705–710; execute :711; result copy/delete :719–723 |
