from datetime import date, time
from decimal import Decimal, InvalidOperation
import re

from models.catalog import MODULES, identifier
from models.db import query

TABLES = {module.table: (slug, module) for slug, module in MODULES.items()}
DISPLAY_TABLES = {name.lower(): name for name in TABLES}
READ_ONLY = {"id", "created_at", "updated_at", "quantity_history"}

def label(name):
    return name.replace("_id", "").replace("_", " ").capitalize()

def schema_fields(table):
    fields = query("""SELECT c.COLUMN_NAME AS name, c.DATA_TYPE AS kind,
        c.COLUMN_TYPE AS definition, c.IS_NULLABLE AS nullable, c.COLUMN_DEFAULT AS default_value,
        c.CHARACTER_MAXIMUM_LENGTH AS max_length, c.NUMERIC_SCALE AS scale,
        k.REFERENCED_TABLE_NAME AS parent
        FROM information_schema.COLUMNS c
        LEFT JOIN information_schema.KEY_COLUMN_USAGE k
          ON k.TABLE_SCHEMA=c.TABLE_SCHEMA AND k.TABLE_NAME=c.TABLE_NAME
          AND k.COLUMN_NAME=c.COLUMN_NAME AND k.REFERENCED_TABLE_NAME IS NOT NULL
        WHERE c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=%s ORDER BY c.ORDINAL_POSITION""", (table,))
    for field in fields:
        if field["parent"]:
            field["parent"] = DISPLAY_TABLES[field["parent"].lower()]
        field["options"] = []
        field["boolean"] = field["definition"] == "tinyint(1)"
        field["required"] = field["nullable"] == "NO" and field["default_value"] is None
        if field["kind"] == "enum":
            field["options"] = [(value, value) for value in re.findall(r"'([^']+)'", field["definition"])]
    return fields

def editable_fields(table, updating=False):
    excluded = READ_ONLY | ({"current_quantity"} if table == "Seed_Storage" and updating else set())
    fields = [field for field in schema_fields(table) if field["name"] not in excluded]
    for field in fields:
        if field["parent"]:
            parent = TABLES[field["parent"]][1]
            key = identifier(parent.fields[0])
            rows = query(f"SELECT id, {key} AS title FROM {identifier(parent.table)} ORDER BY {key}, id")
            field["options"] = [(str(row["id"]), row["title"]) for row in rows]
        if field["boolean"]:
            field["options"] = [("0", "No"), ("1", "Yes")]
    return fields

def parse_values(fields, form):
    values, errors = {}, []
    for field in fields:
        name = field["name"]
        raw = str(form.get(name, "")).strip()
        if not raw:
            if field["required"] or field["nullable"] == "NO":
                errors.append(f"{label(name)} is required.")
            else:
                values[name] = None
            continue
        try:
            if (field["parent"] or field["boolean"] or field["kind"] == "enum") and raw not in {
                str(value) for value, _ in field["options"]
            }:
                raise ValueError
            if field["max_length"] and len(raw) > field["max_length"]:
                raise ValueError
            kind = field["kind"]
            if kind in {"int", "smallint", "tinyint"}:
                raw = int(raw)
            elif kind == "decimal":
                raw = Decimal(raw)
                if not raw.is_finite() or raw.as_tuple().exponent < -field["scale"]:
                    raise ValueError
            elif kind == "date":
                raw = date.fromisoformat(raw)
            elif kind == "time":
                raw = time.fromisoformat(raw)
            if name == "email" and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", raw):
                raise ValueError
            if name == "reference_url" and not re.fullmatch(r"https?://[^\s]+", raw):
                raise ValueError
            values[name] = raw
        except (ValueError, InvalidOperation):
            errors.append(f"Enter a valid value for {label(name).lower()}.")
    return values, errors

def friendly_error(error):
    messages = {
        1062: "A record already uses that unique code or name.",
        1451: "Related records reference this entry. Remove or reassign them first.",
        1452: "A related record no longer exists.",
        3819: "A database rule was violated. Check dates, quantities, and required relationships.",
        1264: "A numeric value exceeds its allowed range.",
        1406: "A field exceeds its allowed length.",
        1644: error.msg,
    }
    return messages.get(error.errno, "MySQL could not save the record.")
