# Functional dependencies and normalization

The schema models one fact type per table. Numeric IDs are surrogate primary keys. An alternate key is a declared, non-null unique business identifier. The functional dependencies below assume catalogue codes are stable identifiers and that descriptive fields such as district names and category labels can occur in multiple rows.

| Relation | Candidate keys | Key determines | Non-key dependency considered |
| --- | --- | --- | --- |
| Farmer | id, registration_code | One person's registration, experience and current contact details | Villages and blocks may share names. Postal codes may cover multiple locations, so the address uses entered labels and makes no postal hierarchy assertion. |
| Farm | id, farm_code | One holding and its attributes | Farmer identity is referenced via FK. Farm address and farmer address describe separate places. |
| Indigenous_Crop | id, common_name | One catalogue entry and its preferred cultivation profile | Scientific synonyms and multi-language common names are outside this catalogue scope. A scientific name is descriptive here. |
| Seed_Variety | id, accession_code | One accession including seed and storage traits | Crop-wide description lives in the crop. Variety origin is its accession source, which can differ from crop origin. |
| Soil_Record | id, sample_code | A single sample's measurements and interpretation | Fertility is a lab assessment across context and tests, without a universal scalar derivation from one reported value. |
| Cultivation_Record | id, cultivation_code | One sowing cycle and its field observations | Seed variety determines crop. The CHECK stores either a variety or a direct crop designation. |
| Irrigation_Record | id, event_code | One irrigation event's observations | Cultivation determines farm. The CHECK stores either cultivation or the farm for a stand-alone event. |
| Organic_Fertilizer | id, recipe_code | One documented preparation and application profile | Category permits many recipes with distinct ingredients, processes and rates. |
| Pest_Management | id, observation_code | One sighting and its associated application or follow-up | Pest names permit distinct symptoms, severity and treatment in different contexts. This table records an episode. |
| Harvest_Record | id, harvest_code | One harvest event and its measured outputs | Loss quantity is computed as gross minus net in the view. The store uses one unit per event. |
| Seed_Storage | id, batch_number | One batch, latest inspection and quantity journal | Low stock derives from quantity and threshold. Availability and sizing are queried separately from accession attributes. |
| Crop_Rotation | id, plan_code | One planned rotation window | Crop sequence uses three named FK roles. Stages with more than three crop positions require a separate design. |
| Traditional_Knowledge | id, entry_code | One documented practice statement and its permissions | Community attribution, custodian and consent describe this particular publication agreement. |

## 1NF

Each record has a key and one value per scalar field. Ingredients, materials, and inspection notes are authored text. Individual items inside them are outside relational query scope. The deliberate exception is `Seed_Storage.quantity_history`, an ordered JSON journal holding multiple events in one column to keep an audit inside the 13-table limit. In the strict atomic-value interpretation this column is outside 1NF and the whole relation cannot be called strictly 3NF. The other storage columns form the 3NF operational batch relation. The smallest correction is a 14th table `Seed_Quantity_Audit(id, batch_id, changed_at_utc, account, before_quantity, after_quantity, unit)`, written by the trigger, with separate retention controls. Keep the journal limited to classroom-sized histories.

## 2NF and 3NF

All candidate keys in the table above are single-column keys, so no partial-key dependency exists. In the scalar design, the non-key attributes depend on one of the listed candidate keys. Parent descriptive attributes remain in parent tables and quantities derived from sibling fields are computed by views or the UI. The last column above states the scope of the remaining dependencies. Applying a fixed policy such as a derived fertility classification would require computing that classification or storing a policy reference.

The scalar relations are in 3NF under these business rules. The `CHECK`-guarded alternatives ensure that a crop identified by a variety and a farm identified by a cultivation appear only through those relationships. The two branches can also be viewed as disjoint event subtypes.

## Relationship choices

Farmer → Farm and Farm → Soil Record are one-to-many. Cultivation is an associative entity with its own attributes and identity. It supports repeat visits by a crop to a farm over time and thereby realizes the many-to-many Farm ↔ Crop relationship. The resolved crop is `COALESCE(crop_id, Seed_Variety.crop_id)` after the variety join. Each practice entry may carry one crop association and each crop may have many entries. Broader knowledge-to-crop tagging would require an additional associative table. Likewise, individual fertilizer ingredients and long crop sequences would need separate relations if they became independently queried entities.

The synthetic records use chronological dates across records. Checks enforce dates within single records. Production cross-event policies such as prohibiting pre-sowing harvests, occupancy limits, and independent storage inspection history would require additional policy design. The full schema includes each type, constraint, and foreign key. [Final relational schema](relational_schema.md) · [ER diagrams](er_diagram.md)
