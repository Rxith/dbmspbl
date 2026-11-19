# Viva preparation

1. **What does this project do?** It links farms and seasonal cultivation to crops, seed varieties, stock, soil, irrigation, pest observations, and harvest while providing a separate knowledge catalogue.
2. **How large is the database?** There are 13 base tables and 329 columns. Views are saved queries and do not add base tables.
3. **What is a candidate key?** A minimal way to uniquely identify a row. A farmer ID and a non-null unique registration code are each candidate keys.
4. **Why are crop and seed variety separate?** One crop can have multiple accessions. Crop-wide traits and accession-specific traits change independently.
5. **Show one-to-many and many-to-many.** A farmer can manage many farms. Many farms can cultivate many crops via cultivation records. Each event holds its farm, date, area, and either a crop or variety.
6. **Why can the cultivation crop FK be NULL?** If the variety is supplied, its parent already tells us the crop. The CHECK enforces exactly one path.
7. **What are the normal forms?** 1NF asks for atomic values, 2NF for full-key dependence, and 3NF eliminates non-key dependencies. The documented stock journal is a deliberate JSON exception to the strict atomic-value rule.
8. **What do the joins demonstrate?** INNER requires matching rows. LEFT and RIGHT preserve unmatched rows on their named sides. A multi-table report resolves crop, farm, cultivation and harvest.
9. **What is a correlated query?** The inner query refers to a row from the outer query. `EXISTS` can find crops with at least one seed variety.
10. **How is HAVING different from WHERE?** WHERE filters input rows. HAVING filters groups after aggregation.
11. **Why group harvests by unit?** Ten kilograms and ten items cannot be added into a meaningful single number.
12. **Why use DECIMAL?** It stores fixed-precision numbers, including fractional kilograms, without the rounding behavior of floating-point storage.
13. **What happens when two users allocate seven units from a batch of ten?** One transaction writes first. The next waits and re-evaluates current quantity, then fails instead of deducting seven again.
14. **What rolls back on a duplicate cultivation code?** The insert fails and the routine rolls back the quantity deduction and audit entry together.
15. **Why use a trigger for the seed journal and a CHECK for non-negative stock?** A CHECK states the permitted values. A trigger can compare old and new rows and record the change.
16. **Why does the database refuse to delete some farmers?** A farm FK references that farmer. Reassign or remove dependent records before deleting the parent.
17. **What does EXPLAIN show?** It estimates how MySQL will access each table, including relevant indexes and row counts. Small tables may be cheaper to scan.
18. **How do you deal with sensitive knowledge and unverified treatments?** Store access level and provenance. Keep restricted entries operator-only and distinguish historical practice, observation, and controlled study.
19. **How do you defend against SQL injection?** Bind input as query parameters, allowlist tables and procedures, and quote identifiers from known schema metadata.
20. **What would you change with more than 13 tables?** Move stock audit events to an append-only relation with its own retention policy and add associative tables for multi-crop knowledge and longer crop sequences.
