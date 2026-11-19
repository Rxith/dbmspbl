"""Generate the attribute dictionary and Mermaid diagrams from the checked-in DDL."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = ROOT / "docs"

def definitions():
    sql = (ROOT / "database/schema.sql").read_text(encoding="utf-8")
    for match in re.finditer(r"CREATE TABLE (\w+) \(\n(.*?)\n\);", sql, re.S):
        table, body = match.groups()
        columns, rules, foreign_keys = [], [], {}
        for raw in body.splitlines():
            line = raw.strip().removesuffix(",")
            fk = re.fullmatch(r"FOREIGN KEY \((\w+)\) REFERENCES (\w+)\(id\)", line)
            if fk:
                foreign_keys[fk[1]] = fk[2]
                rules.append(line)
            elif line.startswith(("CHECK ", "INDEX ", "CONSTRAINT ")):
                rules.append(line)
            else:
                name, kind, constraints = re.fullmatch(r"(\w+) (\w+(?:\([^)]*\))?)(?: (.*))?", line).groups()
                if constraints and constraints.startswith("UNSIGNED"):
                    kind += " UNSIGNED"
                    constraints = constraints.removeprefix("UNSIGNED").strip()
                columns.append((name, kind, constraints or "NULL"))
        yield table, columns, rules, foreign_keys

def generate():
    tables = list(definitions())
    total = sum(len(columns) for _, columns, _, _ in tables)
    spec = ["# Relational schema and attribute dictionary", "",
            "Generated from `database/schema.sql` with `python -m database.schema_docs`.",
            "", f"**{len(tables)} tables and {total} attributes.** Unmarked optional columns default to NULL. "
            "All foreign keys default to RESTRICT. Measurement units appear in names or companion unit fields."]
    diagrams = [[], []]
    edges = []
    for table, columns, rules, foreign_keys in tables:
        spec += ["", f"## {table} ({len(columns)} attributes)", "",
                 "| Attribute | MySQL type | Constraints and default |",
                 "| --- | --- | --- |"]
        for diagram in diagrams:
            diagram.append(f"    {table} {{")
        for index, (name, kind, constraints) in enumerate(columns):
            fk = f"; FK → {foreign_keys[name]}(id)" if name in foreign_keys else ""
            spec.append(f"| `{name}` | `{kind}` | `{constraints}{fk}` |")
            pk_mark = " PK" if name == "id" else ""
            fk_mark = " FK" if fk else ""
            safe_kind = re.sub(r"[^a-z0-9]", "_", kind.lower()).strip("_")
            entry = f"        {safe_kind} {name}{pk_mark}{fk_mark}"
            diagrams[0].append(entry)
            if index < 4 or pk_mark or fk_mark:
                diagrams[1].append(entry)
            if fk:
                cardinality = "||" if "NOT NULL" in constraints else "o|"
                edges.append(f"    {foreign_keys[name]} {cardinality}--o{{ {table} : {name}")
        for diagram in diagrams:
            diagram.append("    }")
        if rules:
            spec += ["", "Table-level rules", ""] + [f"- `{rule}`" for rule in rules]
    er = ["# Entity relationship diagrams", "",
          "Generated from the actual DDL. A child may reference an optional parent when its FK is nullable.",
          "Cultivation and irrigation each enforce exactly one of their two alternative references.",
          "A farm and a crop can each participate in many cultivations.", ""]
    for title, diagram in zip(("Presentation diagram", "Complete diagram"), reversed(diagrams)):
        er += [f"## {title}", "", "```mermaid", "erDiagram", *diagram, *edges, "```", ""]
    (DOCUMENTS / "relational_schema.md").write_text("\n".join(spec) + "\n", encoding="utf-8")
    (DOCUMENTS / "er_diagram.md").write_text("\n".join(er), encoding="utf-8")

if __name__ == "__main__":
    generate()
