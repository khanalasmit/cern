from typing import List, Literal, Optional, Union , Annotated
from pydantic import BaseModel, Field, model_validator, TypeAdapter
'''
typing module provides the typehint 
pydantic is used for validation of data type
'''

'''Classes here on are created for to validate the json used for
the generation of the oks query.
This is like the validation of query tree.
'''

'''
It is for the filer on an objects;s attribute with an opeartor and value.
First the translator.py tells the llm to genrate the attribute comparision in json format.
The IR is validated aganist this validator.
'''
class AttributeCompare(BaseModel):
    type: Literal["attribute compare"]
    attribute:str
    operator: Literal["=", "!=", "~=", "<", "<=", ">", ">="]
    value: str



'''
It is for filtering by a specific object's unique ID.
The LLM generates this when the user refers to a known object by name or ID.
Example query: "Find the application with ID app-123"
Example JSON: {"type": "object_id", "operator": "=", "object_id": "app-123"}
Serializes to: (object-id "app-123" =)
'''
class ObjectIdCompare(BaseModel):
    type: Literal["object_id"]
    operator: Literal["="]
    object_id: str


'''
It is for filtering by related objects through a named relationship.
The quantifier "some" means at least one related object must match.
The quantifier "all" means every related object must match.
The nested expression is evaluated against the relationship's target class.
Example query: "Find applications that have some dependency with Status = Running"
Example JSON: {"type": "relationship", "name": "InitializationDependsFrom", "quantifier": "some",
               "expression": {"type": "attribute_compare", "attribute": "Status", "operator": "=", "value": "Running"}}
Serializes to: ("InitializationDependsFrom" some ("Status" "Running" =))
'''
class RelationshipCompare(BaseModel):
    type: Literal["relationship"]
    name: str
    quantifier: Literal["some", "all"]
    expression: "Expression"


'''
It is for combining multiple conditions where ALL must be true.
Requires at least two operands (enforced by the model_validator below).
Example query: "Find applications where Name = app1 AND Timeout > 25"
Example JSON: {"type": "and", "operands": [
                {"type": "attribute_compare", "attribute": "Name", "operator": "=", "value": "app1"},
                {"type": "attribute_compare", "attribute": "Timeout", "operator": ">", "value": "25"}]}
Serializes to: (and ("Name" "app1" =) ("Timeout" "25" >))
'''
class AndExpression(BaseModel):
    type: Literal["and"]
    operands: List["Expression"]

    @model_validator(mode="before")
    @classmethod
    def check_operands(cls, values):
        ops = values.get('operands', []) if isinstance(values, dict) else []
        if len(ops) < 2:
            raise ValueError("'and' expression must have at least two operands")
        return values


'''
It is for combining multiple conditions where at least ONE must be true.
Requires at least two operands (enforced by the model_validator below).
Example query: "Find applications where Name = app1 OR Name = app2"
Example JSON: {"type": "or", "operands": [
                {"type": "attribute_compare", "attribute": "Name", "operator": "=", "value": "app1"},
                {"type": "attribute_compare", "attribute": "Name", "operator": "=", "value": "app2"}]}
Serializes to: (or ("Name" "app1" =) ("Name" "app2" =))
'''
class OrExpression(BaseModel):
    type: Literal["or"]
    operands: List["Expression"]

    @model_validator(mode="before")
    @classmethod
    def check_operands(cls, values):
        ops = values.get('operands', []) if isinstance(values, dict) else []
        if len(ops) < 2:
            raise ValueError("'or' expression must have at least two operands")
        return values


'''
It is for negating a condition, meaning the opposite must be true.
Takes exactly one operand (the expression to negate).
Example query: "Find applications where Status is NOT Stopped"
Example JSON: {"type": "not", "operand":
                {"type": "attribute_compare", "attribute": "Status", "operator": "=", "value": "Stopped"}}
Serializes to: (not ("Status" "Stopped" =))
Note: Placing not inside vs outside a relationship changes semantics:
  - "not (rel some expr)" = NONE of the related objects match
  - "rel some (not expr)" = at least one related object does NOT match
'''
class NotExpression(BaseModel):
    type: Literal["not"]
    operand: "Expression"


#Recurisve type
'''To show expresssion can be any of these'''
Expression = Union[
    AndExpression, OrExpression, NotExpression,
    RelationshipCompare, AttributeCompare, ObjectIdCompare
]

'''
Used to tell pydyantic to go back and re valdiate after the union is created
'''
# Rebuild models to resolve forward references (Pydantic v2)
AndExpression.model_rebuild()
OrExpression.model_rebuild()
NotExpression.model_rebuild()
RelationshipCompare.model_rebuild()


'''
QueryIR is the top-level query IR (Intermediate Representation) that the LLM generates.
This is the root model that holds the entire query structure.
Everything else (AttributeCompare, AndExpression, etc.) lives inside expression.

Fields:
- target_class (Optional[str], default=None):
    The OKS class to query against. Tells the system what kind of object you are looking for.
    Examples: "Application", "Segment", "Binary"
    If None, the LLM did not specify (fallback, best-effort).

- scope (Literal["this", "all"]):
    Controls whether to include subclasses of the target class.
    "this" = only the exact class (e.g. only Application, not IPCServiceApplication)
    "all" = class + all subclasses (e.g. Application, IPCServiceApplication, MIGApplication, etc.)
    Most queries use "all" (140 out of 144 in the eval dataset).
    Only use "this" when the user explicitly says "this class only".

- expression (Expression):
    The filter tree — the actual conditions to match. This is where all the complexity lives.
    Expression is a Union of 6 types:
      AndExpression, OrExpression, NotExpression,
      RelationshipCompare, AttributeCompare, ObjectIdCompare
    Can be nested to any depth to represent complex queries.

- explanation (Optional[str], default=None):
    A human-readable breakdown of what the query does. The LLM generates this to explain its reasoning.
    Not used for validation or serialization — purely for debugging and display.

Example 1 - Simple attribute filter:
    Query: "Find all applications where Timeout > 50"
    JSON: {
        "target_class": "Application",
        "scope": "all",
        "expression": {"type": "attribute_compare", "attribute": "Timeout", "operator": ">", "value": "50"},
        "explanation": "Filtering applications with timeout greater than 50"
    }
    OKS: (all ("Timeout" "50" >))

Example 2 - Relationship traversal:
    Query: "Find all applications that depend on something with Status = Running"
    JSON: {
        "target_class": "Application",
        "scope": "all",
        "expression": {
            "type": "relationship",
            "name": "InitializationDependsFrom",
            "quantifier": "some",
            "expression": {"type": "attribute_compare", "attribute": "Status", "operator": "=", "value": "Running"}
        },
        "explanation": "Find applications that have at least one initialization dependency with Status equal to Running"
    }
    OKS: (all ("InitializationDependsFrom" some ("Status" "Running" =)))

Example 3 - Boolean combination with relationship:
    Query: "Find segments controlled by DefaultRootController that have some application with Timeout > 30"
    JSON: {
        "target_class": "Segment",
        "scope": "all",
        "expression": {
            "type": "and",
            "operands": [
                {"type": "relationship", "name": "IsControlledBy", "quantifier": "some",
                 "expression": {"type": "attribute_compare", "attribute": "Name", "operator": "=", "value": "DefaultRootController"}},
                {"type": "relationship", "name": "Applications", "quantifier": "some",
                 "expression": {"type": "attribute_compare", "attribute": "Timeout", "operator": ">", "value": "30"}}
            ]
        },
        "explanation": "Find segments controlled by DefaultRootController that contain at least one application with timeout > 30"
    }
    OKS: (all (and ("IsControlledBy" some ("Name" "DefaultRootController" =)) ("Applications" some ("Timeout" "30" >))))

Flow:
    Natural Language → (LLM generates) → QueryIR JSON → (validate_ir) → QueryIR Pydantic model
    → (serialize_ir_to_oks) → OKS query string → (OKS engine) → Results
'''
class QueryIR(BaseModel):
    target_class: Optional[str] = None
    scope: Literal["this", "all"]
    expression: Expression
    explanation: Optional[str] = None


'''
Custom exception raised when the IR is structurally valid but semantically wrong.
This catches errors that Pydantic structural validation cannot detect:
- target_class does not exist in the OKS schema
- attribute name does not exist on the target class
- relationship name does not exist on the target class
- nested expression references attributes on the wrong class
Example: Using "Timeout" on a class that only has "InitTimeout" raises this error.
'''
class SemanticValidationError(ValueError):
    """Raised when an IR expression violates schema semantics (e.g. invalid attribute, bad rel target)."""
    pass


'''
Performs Layer 1 (structural) validation on the LLM-generated JSON.
Checks that the JSON matches the QueryIR schema:
- All required fields are present
- type discriminators are valid
- operators are from the allowed set
- and/or have at least 2 operands
- nesting is valid (Expression types inside Expression types)
Returns a validated QueryIR Pydantic model on success.
Raises ValidationError if the JSON is malformed.
'''
def validate_ir(ir_json: dict) -> QueryIR:
    """Validates the parsed JSON against the IR schema and returns a Pydantic model."""
    return QueryIR.model_validate(ir_json)



def validate_ir_semantics(ir: QueryIR, indexer)->None:
    """
    Recursively validates that:
    1. target class exits in the schema
    2. Attibutes exist on the target-class
    3. Relationships exits on the target class and any nested expression 
        is valid on the relationship's target class-type.
    """

    #Here indxer is hybrid indexer that loaded the oks-schema contains
    #all classes, attributes, Relationships
    # if indexer has not loaded the schema or llm did not provide the target class
    #cannot validate semantics-so we skip silently
    if not hasattr(indexer, 'resolved_classes') or not indexer.resolved_classes:
        return #Indexer not loaded

    
