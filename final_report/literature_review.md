# Literature Review

## 2.1 Review of Related Theory

The proposed project develops a natural-language interface for querying the Object Kernel Support (OKS) configuration used by the ATLAS Trigger and Data Acquisition (TDAQ) system. OKS is not a conventional relational database. Jones *et al.* describe it as a persistent in-memory object manager designed for fast access to structured information in configuration and real-time control applications [1]. Its object model supports classes, object identifiers, associations, inheritance, polymorphism, integrity constraints, and schema evolution [1]. Therefore, an OKS query depends on relationships among objects and on the schema version in which those objects are defined.

The ATLAS literature demonstrates the scale of this problem. Almeida *et al.* describe an online configuration service that had to represent information from several DAQ, trigger, and detector groups, preserve historical configurations, and serve many processes during online operation [2]. The configuration contains interconnected classes and objects rather than isolated records. A user's question may consequently require a target class, inherited attributes, related classes, object identifiers, and valid operators at the same time. A language model that generates a query without the relevant schema may produce a syntactically plausible but semantically invalid expression.

Configuration correctness is also a governance concern. Soloviev reports that the ATLAS version-control service was introduced to control access, preserve modification history, and detect XML syntax errors and inconsistent references [3]. The later Git-based service for LHC Run 3 continues to emphasise consistency, performance, access control, traceability, and archiving while managing more than one thousand interconnected XML files [4]. These findings support two requirements for the proposed translator: queries must use an explicitly selected release or revision, and generated queries must pass deterministic validation before execution.

## 2.2 Retrieval-Augmented Generation and Few-Shot Prompting

Large language models can translate natural-language instructions, but their internal knowledge cannot reliably contain a private and changing OKS schema. Retrieval-Augmented Generation (RAG) addresses this limitation by combining a language model with external knowledge retrieved at query time. Lewis *et al.* define RAG as a combination of parametric model memory and non-parametric external memory, and show that retrieval can improve factual specificity in knowledge-intensive tasks [5]. For this project, the external memory is the selected OKS schema and configuration metadata, including class definitions, inherited members, relationships, object identifiers, operators, and verified query examples.

RAG does not guarantee correctness by itself. If the retriever selects the wrong class, omits a relationship, or mixes information from different releases, the model may generate an invalid query. Retrieval must therefore be version-aware and evaluated separately from generation. The system should measure whether the relevant classes, attributes, and relationships were retrieved before measuring the final execution result.

Few-shot prompting is also relevant. Brown *et al.* show that large language models can perform many tasks from instructions and a small number of examples without task-specific parameter updates [6]. In this project, examples can demonstrate OksQuery syntax and structure. However, examples are guidance rather than authority: an example from an older TDAQ release may contain a class or attribute unavailable in the current release. Demonstrations should therefore be filtered using the same version metadata as the retrieved schema.

## 2.3 Natural-Language Query Translation and Validation

Natural-language-to-SQL research provides a useful comparison, although OKS is object-oriented and is not equivalent to SQL. Katsogiannis-Meimarakis and Koutrika identify schema linking—the association of terms in a question with database elements—as a central stage in neural text-to-SQL systems [7]. They also highlight query representation, generation, and execution-based evaluation [7]. These principles transfer to OKS, where schema linking must identify classes, attributes, relationship paths, values, and object identifiers.

Direct generation of a raw OksQuery string is risky because syntax validity is only one part of correctness. A query may be syntactically valid but use a nonexistent attribute, an incompatible operator, an incorrect relationship target, or an object absent from the selected configuration. The proposed system should therefore generate a typed intermediate representation (IR), such as JSON or an abstract syntax tree, before serializing it into OksQuery. The IR can represent the target class, predicates, relationship traversal, values, version, and result limit. A deterministic validator can then check class and attribute existence, relationship typing, operator/value compatibility, and version consistency. Invalid output can be repaired a limited number of times or rejected safely.

Evaluation should focus on execution accuracy rather than exact text matching. Equivalent queries may have different textual forms. The main measure should be whether the validated query runs against the intended configuration version and returns the expected objects. Supporting measures should include schema-linking accuracy, first-pass validation rate, repair success rate, execution latency, and safe-rejection accuracy.

## 2.4 Research Gap and Project Relevance

The reviewed literature provides complementary foundations but does not directly evaluate a natural-language interface for versioned ATLAS OKS configuration queries. The OKS and ATLAS studies establish the domain requirements of interconnected objects, schema evolution, historical access, and consistency control [1]–[4]. RAG and few-shot learning provide methods for grounding a language model and adapting it to a specialised query format [5], [6]. Text-to-SQL research contributes schema-linking and execution-based evaluation principles [7].

The reviewed sources did not identify one evaluated pipeline combining version-scoped OKS schema retrieval, few-shot translation, typed query generation, deterministic schema/type validation, bounded repair, and execution against the matching configuration. This project addresses that integration gap as a read-only research prototype. Its contribution is not a new language model; it is an auditable translation and execution pipeline intended to make LLM-assisted OKS querying more reliable. The system should return the generated query with the selected release or revision, validation outcome, and result provenance. If the required context is missing or inconsistent, it should reject the request rather than execute an unverified query.

## References

[1] R. Jones, L. Mapelli, Y. Ryabov, and I. Soloviev, “The OKS persistent in-memory object manager,” *IEEE Transactions on Nuclear Science*, vol. 45, no. 4, pp. 1958–1964, Aug. 1998. [Online]. Available: https://cds.cern.ch/record/370902/files/cer-000296198.pdf

[2] J. Almeida, M. Dobson, A. Kazarov, G. Lehmann Miotto, J. E. Sloper, I. Soloviev, and R. C. Torres, “The ATLAS DAQ system online configurations database service challenge,” *Journal of Physics: Conference Series*, vol. 119, no. 2, Art. no. 022004, 2008, doi: 10.1088/1742-6596/119/2/022004.

[3] I. Soloviev, “The version control service for the ATLAS data acquisition configuration files,” *Journal of Physics: Conference Series*, vol. 396, Art. no. 012047, 2012, doi: 10.1088/1742-6596/396/1/012047.

[4] I. Soloviev, “The git based ATLAS data acquisition configuration service in LHC Run 3,” *EPJ Web of Conferences*, vol. 337, Art. no. 01038, 2025, doi: 10.1051/epjconf/202533701038.

[5] P. Lewis *et al.*, “Retrieval-augmented generation for knowledge-intensive NLP tasks,” in *Advances in Neural Information Processing Systems*, vol. 33, 2020, pp. 9459–9474. [Online]. Available: https://papers.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html

[6] T. B. Brown *et al.*, “Language models are few-shot learners,” in *Advances in Neural Information Processing Systems*, vol. 33, 2020, pp. 1877–1901. [Online]. Available: https://arxiv.org/abs/2005.14165

[7] G. Katsogiannis-Meimarakis and G. Koutrika, “A survey on deep learning approaches for text-to-SQL,” *The VLDB Journal*, vol. 32, pp. 905–936, 2023, doi: 10.1007/s00778-022-00776-8.
