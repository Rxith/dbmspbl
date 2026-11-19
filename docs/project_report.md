# KrishiParampara project report

## Abstract

KrishiParampara keeps crop and seed catalogues, farms, soil samples, seasonal work, yield reports, and knowledge records in a MySQL relational database. Flask provides a public catalogue and an operator workspace. The system demonstrates keys, referential integrity, views, routines, validation, and a transactional seed allocation.

## Problem and objectives

Farm records can become difficult to reconcile when stock, cultivation, and harvest are recorded separately. Traditional knowledge also needs provenance, permission and attribution. The project links records with foreign keys, preserves measured units, offers searchable CRUD and reports, and demonstrates how a database prevents a stock deduction from surviving a failed cultivation insert.

## Indian Knowledge Systems context

The repository provides fields to record oral or written sources, terminology, regional context, custodianship, community attribution, and reuse terms. Keep restricted records limited to authorized operators. A community-reviewed entry records provenance or consent within the documented scope. It carries no automatic scientific endorsement. Pest field observations and controlled evidence are distinguished, and the latter requires a reference. The provided knowledge entries are fictional and do not attribute practices to actual communities.

For further research use ICAR's crop and extension publications, source-specific records from the ICAR National Bureau of Plant Genetic Resources, and Kew's Plants of the World Online for taxonomic names. Confirm local names and sharing terms with custodians before publication. [ICAR](https://icar.gov.in/) · [NBPGR](https://nbpgr.icar.gov.in/) · [Kew POWO](https://powo.science.kew.org/)

## Architecture

```mermaid
flowchart LR
    Browser["Browser · Bootstrap and Chart.js"] --> Flask["Flask routes and Jinja templates"]
    Flask --> Services["Record validation and reporting"]
    Services --> Connector["Parameterized MySQL Connector/Python"]
    Connector --> MySQL["MySQL 8.0 · InnoDB tables, views and routines"]
```

The application reads schema metadata for CRUD fields and foreign-key selectors. It allowlists dynamic SQL identifiers and binds submitted values. HTML forms and Flask verify required fields and formats. MySQL enforces invariants for every client. The session gates farmer details and restricted knowledge.

## ER model and SQL implementation

The 13-table design includes master records, event records, inventory, and seasonal planning. Foreign keys enforce parent existence and prevent destructive deletion of referenced rows. Primary/unique keys cover farmer identification and crop name, and secondary indexes cover farm location and cultivation dates. InnoDB adds indexes to support the seed variety foreign keys. `EXPLAIN` in the demonstration shows the selected access path, which depends on data size and statistics.

Views aggregate farmer cultivations, available seed by variant and unit, and harvests by harvest year, cultivation season, and unit. The trigger appends stock changes in the same transaction. CHECK constraints protect stock and harvest quantities for INSERT and UPDATE. The atomic seed deduction takes an InnoDB write lock and rechecks quantity after a competing update. A handler rolls back the change and audit if cultivation creation fails.

- [Relational schema](relational_schema.md)
- [ER diagram and presentation diagram](er_diagram.md)
- [Functional dependencies and normalization](normalization.md)
- [Executable SQL examples](../database/queries.sql)

## Testing and screenshot checklist

Run the schema validator and integration tests on a disposable seeded MySQL database. They exercise schema metadata, foreign keys, all CRUD routes, SQL results, authorization, validation, and transaction commit, rollback, and contention. See [setup and test commands](../README.md).

For a presentation, capture the home page, dashboard charts, a filtered catalogue, a crop with related varieties, a cultivation form, the seed batch audit before and after allocation, the seasonal report, the DBMS demonstration, and the schema validation/test output. Use fictional records in screenshots.

## Conclusion and future scope

The system gives a common source of farm and seed records and uses the database to enforce consistency at write time. A next iteration could add fine-grained accounts, consent review workflows, a separate audit relation, normalized multilingual names, longer rotation sequences, and more verified sources reviewed with communities.
