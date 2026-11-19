from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
from threading import Barrier
from uuid import uuid4

from mysql.connector import Error
import pytest

from database.validate_schema import validate
from models.db import connection, execute, query
from services.reporting import call, dashboard

def test_connect_and_validate_schema():
    assert query("SELECT VERSION() AS version")[0]["version"].startswith("8.0.")
    counts = validate()
    assert len(counts) == 13 and min(counts.values()) >= 25 and sum(counts.values()) >= 325

def test_views_have_consistent_totals():
    summary = query("SELECT SUM(cultivations) AS total FROM Farmer_Cultivation_Summary")[0]
    assert summary["total"] == query("SELECT COUNT(*) AS total FROM Cultivation_Record")[0]["total"]
    seed = query("""SELECT quantity_unit, SUM(available_quantity) AS total FROM Indigenous_Seed_Availability
              WHERE quantity_unit IS NOT NULL GROUP BY quantity_unit ORDER BY quantity_unit""")
    assert seed == query("""SELECT quantity_unit, SUM(current_quantity) AS total FROM Seed_Storage
        WHERE status='available' AND (expected_expiry_on IS NULL OR expected_expiry_on>=CURRENT_DATE)
        GROUP BY quantity_unit ORDER BY quantity_unit""")
    assert query("SELECT SUM(harvests) AS total FROM Seasonal_Harvest_Report")[0]["total"] == (
        query("SELECT COUNT(*) AS total FROM Harvest_Record")[0]["total"])

def test_procedures_return_seeded_records():
    farmer = query("SELECT farmer_id FROM Farmer_Cultivation_Summary WHERE cultivations > 0 LIMIT 1")[0]
    assert call("farmer_cultivations", (farmer["farmer_id"],))
    rows = call("seasonal_harvest", (2025, "Kharif"))
    assert rows and all(row["harvest_year"] == 2025 and row["season"] == "Kharif" for row in rows)

def test_queries_script():
    sql = Path("database/queries.sql").read_text(encoding="utf-8")
    with connection() as db, db.cursor() as cursor:
        cursor.execute(sql)
        results = []
        while True:
            if cursor.with_rows:
                results.append(cursor.fetchall())
            if not cursor.nextset():
                break
    assert len(results) == 14
    assert query("SELECT id FROM Farmer WHERE registration_code='SQL-DEMO'") == []

@pytest.fixture
def batch():
    variety = query("SELECT id FROM Seed_Variety LIMIT 1")[0]["id"]
    farm = query("SELECT id FROM Farm LIMIT 1")[0]["id"]
    prefix = f"TEST-{uuid4().hex[:12]}"
    storage = execute("""INSERT INTO Seed_Storage
        (seed_variety_id,batch_number,storage_location,initial_quantity,current_quantity,quantity_unit,stored_on)
        VALUES (%s,%s,'Isolated test batch',10,10,'kg','2024-01-01')""", (variety, prefix))
    yield storage, farm, prefix
    execute("DELETE FROM Cultivation_Record WHERE cultivation_code LIKE %s", (prefix + "%",))
    execute("DELETE FROM Seed_Storage WHERE id=%s", (storage,))

def stock(batch_id):
    return query("SELECT current_quantity, quantity_history FROM Seed_Storage WHERE id=%s", (batch_id,))[0]

def test_stock_audit_and_negative_constraints(batch):
    batch_id, _, _ = batch
    call("adjust_seed_stock", (batch_id, Decimal("-2")))
    row = stock(batch_id)
    assert row["current_quantity"] == 8
    audit = json.loads(row["quantity_history"])
    assert [(item["before"], item["after"], item["unit"]) for item in audit] == [(10, 8, "kg")]
    with pytest.raises(Error, match="ck_stock_nonnegative"):
        execute("UPDATE Seed_Storage SET current_quantity=-1 WHERE id=%s", (batch_id,))
    with pytest.raises(Error, match="insufficient"):
        call("adjust_seed_stock", (batch_id, Decimal("-9")))
    assert stock(batch_id) == row

def allocate(batch_id, quantity, farm, code):
    call("allocate_seed", (batch_id, Decimal(quantity), farm, code, date.today(), "Kharif", Decimal("0.5")))

def test_allocation_commit(batch):
    batch_id, farm, code = batch
    allocate(batch_id, "3", farm, code)
    row = query("SELECT seed_quantity, seed_unit FROM Cultivation_Record WHERE cultivation_code=%s", (code,))[0]
    assert row == {"seed_quantity": Decimal("3"), "seed_unit": "kg"}
    assert stock(batch_id)["current_quantity"] == 7

def test_allocation_rolls_back_insert_failure_and_audit(batch):
    batch_id, farm, code = batch
    allocate(batch_id, "1", farm, code)
    before = stock(batch_id)
    with pytest.raises(Error) as err:
        allocate(batch_id, "2", farm, code)
    assert err.value.errno == 1062
    assert stock(batch_id) == before

def test_allocation_contention(batch):
    batch_id, farm, prefix = batch
    gate = Barrier(2)
    def attempt(index):
        gate.wait(timeout=10)
        try:
            allocate(batch_id, "7", farm, f"{prefix}-{index}")
        except Error as error:
            assert "insufficient" in str(error)
            return False
        return True
    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(attempt, range(2))) == [False, True]
    assert stock(batch_id)["current_quantity"] == 3
    assert query("SELECT COUNT(*) AS n FROM Cultivation_Record WHERE cultivation_code LIKE %s",
                 (prefix + "%",))[0]["n"] == 1

def test_primary_foreign_and_harvest_constraints():
    with pytest.raises(Error) as err:
        execute("""INSERT INTO Farm (farmer_id,farm_code,name,village,district,state_name,land_area_ha,cultivable_area_ha)
            VALUES (-999,'TEST-INVALID-FK','Test','Test','Test','Test',1,1)""")
    assert err.value.errno == 1452
    with pytest.raises(Error) as err:
        execute("""INSERT INTO Farmer(id,registration_code,given_name,registered_on)
            SELECT id,'TEST-INVALID-PK','Test',CURRENT_DATE FROM Farmer LIMIT 1""")
    assert err.value.errno == 1062
    with pytest.raises(Error, match="ck_harvest_quantities"):
        execute("""INSERT INTO Harvest_Record
            (cultivation_id,harvest_code,harvested_on,harvested_area_ha,gross_yield,net_yield,yield_unit)
            SELECT id,'TEST-INVALID-YIELD',CURRENT_DATE,1,2,3,'kg' FROM Cultivation_Record LIMIT 1""")

def test_dashboard_queries():
    metrics, yields, charts = dashboard()
    assert metrics["farmers"] == query("SELECT COUNT(*) AS n FROM Farmer")[0]["n"]
    assert metrics["active"] >= 20
    assert {item["unit"] for item in yields} == {"count", "kg"}
    assert len(charts) == 5 and all(rows for _, _, rows in charts)

def test_sample_data_targets():
    targets = {
        "Farmer": 30, "Farm": 30, "Indigenous_Crop": 40, "Seed_Variety": 50,
        "Soil_Record": 100, "Cultivation_Record": 100, "Irrigation_Record": 100,
        "Organic_Fertilizer": 30, "Pest_Management": 60, "Harvest_Record": 100,
        "Seed_Storage": 60, "Crop_Rotation": 50, "Traditional_Knowledge": 50,
    }
    for table, minimum in targets.items():
        assert query(f"SELECT COUNT(*) AS n FROM {table}")[0]["n"] >= minimum

def test_allocation_form_commits(operator, batch):
    from conftest import token_from

    batch_id, farm, code = batch
    token = token_from(operator.get("/allocate"))
    response = operator.post("/allocate", data={
        "csrf": token, "batch": batch_id, "farm": farm, "sowing": date.today(),
        "code": code, "season": "Rabi", "quantity": "4", "area": "0.60",
    })
    assert response.status_code == 302
    assert stock(batch_id)["current_quantity"] == 6
    assert query("SELECT id FROM Cultivation_Record WHERE cultivation_code=%s", (code,))
