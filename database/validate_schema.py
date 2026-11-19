"""Verify contract with live MySQL metadata: python -m database.validate_schema."""
from collections import Counter

from models.catalog import MODULES
from models.db import query

EXPECTED_FKS = {
    "Farm": {"farmer_id": "Farmer"},
    "Seed_Variety": {"crop_id": "Indigenous_Crop"},
    "Soil_Record": {"farm_id": "Farm"},
    "Cultivation_Record": {"farm_id": "Farm", "crop_id": "Indigenous_Crop", "seed_variety_id": "Seed_Variety"},
    "Irrigation_Record": {"farm_id": "Farm", "cultivation_id": "Cultivation_Record"},
    "Pest_Management": {"cultivation_id": "Cultivation_Record"},
    "Harvest_Record": {"cultivation_id": "Cultivation_Record"},
    "Seed_Storage": {"seed_variety_id": "Seed_Variety"},
    "Crop_Rotation": {"farm_id": "Farm", "previous_crop_id": "Indigenous_Crop",
                      "current_crop_id": "Indigenous_Crop", "next_crop_id": "Indigenous_Crop"},
    "Traditional_Knowledge": {"crop_id": "Indigenous_Crop"},
}

def validate():
    expected = {module.table for module in MODULES.values()}
    canonical = {name.lower(): name for name in expected}

    def canonical_name(name):
        return canonical.get(name.lower(), name)

    tables = query("""SELECT TABLE_NAME AS name FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'""")
    actual = {canonical_name(row["name"]) for row in tables}
    if len(actual) != 13 or actual != expected:
        raise ValueError(f"Missing tables: {expected - actual}. Unexpected tables: {actual - expected}.")
    columns = query("""SELECT TABLE_NAME AS name, COLUMN_NAME AS col, COLUMN_KEY AS key_type
        FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()""")
    for row in columns:
        row["name"] = canonical_name(row["name"])
    counts = Counter(row["name"] for row in columns if row["name"] in actual)
    if sum(counts.values()) < 325 or any(counts[table] < 25 for table in actual):
        raise ValueError(f"Attribute minimum not met: {counts}")
    primary_keys = {(row["name"], row["col"]) for row in columns
                    if row["key_type"] == "PRI" and row["name"] in actual}
    if primary_keys != {(table, "id") for table in actual}:
        raise ValueError(f"Unexpected primary keys: {primary_keys}")
    foreign_keys = query("""SELECT TABLE_NAME AS name, COLUMN_NAME AS col,
        REFERENCED_TABLE_NAME AS parent, REFERENCED_COLUMN_NAME AS parent_col
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_SCHEMA = DATABASE()""")
    expected_keys = {(table, col, parent, "id")
                     for table, keys in EXPECTED_FKS.items() for col, parent in keys.items()}
    actual_keys = {(canonical_name(row["name"]), row["col"], canonical_name(row["parent"]), row["parent_col"])
                   for row in foreign_keys}
    if actual_keys != expected_keys:
        raise ValueError("Live foreign keys differ from the schema contract")
    return dict(sorted(counts.items()))

if __name__ == "__main__":
    counts = validate()
    for table, count in counts.items():
        print(f"{table}: {count}")
    print(f"{len(counts)} tables, {sum(counts.values())} attributes")
