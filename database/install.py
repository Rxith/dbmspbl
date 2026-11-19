"""Install on an empty, already-created database: python -m database.install."""
from pathlib import Path

from models.db import connection

def install():
    with connection() as db, db.cursor() as cursor:
        cursor.execute("SHOW FULL TABLES")
        if cursor.fetchall():
            raise SystemExit("Use an empty database. MySQL DDL commits implicitly.")
        for filename in ("schema", "views", "triggers", "procedures", "transactions"):
            sql = Path(__file__).with_name(f"{filename}.sql").read_text(encoding="utf-8")
            cursor.execute(sql)
            while cursor.nextset():
                if cursor.with_rows:
                    cursor.fetchall()

if __name__ == "__main__":
    install()
