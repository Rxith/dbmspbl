from uuid import uuid4

import pytest

from conftest import token_from
from models.catalog import MODULES, identifier
from models.db import execute, query
from services.records import READ_ONLY

@pytest.mark.parametrize("slug", MODULES)
def test_crud_for_each_module(operator, slug):
    module = MODULES[slug]
    table = identifier(module.table)
    sample = query(f"SELECT * FROM {table} ORDER BY id LIMIT 1")[0]
    unique = query("""SELECT COLUMN_NAME AS field FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_KEY='UNI'""", (module.table,))[0]["field"]
    code = f"TEST-{uuid4().hex[:16]}"
    data = {key: str(value) if value is not None else "" for key, value in sample.items() if key not in READ_ONLY}
    data[unique] = code
    form = operator.get(f"/records/{slug}/new")
    assert form.status_code == 200
    data["csrf"] = token_from(form)
    assert operator.post(f"/records/{slug}/new", data=data).status_code == 302
    created = query(f"SELECT id FROM {table} WHERE {identifier(unique)}=%s", (code,))[0]["id"]
    address = f"/records/{slug}/{created}"
    try:
        page = operator.get(address)
        assert page.status_code == 200 and code.encode() in page.data
        listing = operator.get(f"/records/{slug}", query_string={"q": code})
        assert listing.status_code == 200 and address.encode() in listing.data
        data[unique] += "-EDIT"
        assert operator.get(f"{address}/edit").status_code == 200
        assert operator.post(f"{address}/edit", data=data).status_code == 302
        assert data[unique].encode() in operator.get(address).data
        assert operator.post(f"{address}/delete", data={"csrf": data["csrf"]}).status_code == 302
        assert operator.get(address).status_code == 404
    finally:
        execute(f"DELETE FROM {table} WHERE id=%s", (created,))

def test_auth_and_restricted_knowledge(client):
    restricted = query("SELECT id,entry_code FROM Traditional_Knowledge WHERE access_level='restricted' LIMIT 1")[0]
    assert client.get("/records/farmers").status_code == 302
    assert client.get(f"/records/knowledge/{restricted['id']}").status_code == 404
    response = client.get("/records/knowledge", query_string={"q": restricted["entry_code"]})
    assert b"No matching records" in response.data
    assert client.get("/records/crops").status_code == 200
    assert client.post("/login", data={"password": "integration-test"}).status_code == 400

def test_input_validation_and_farm_reference_protection(operator):
    endpoint = "/records/farmers/new"
    token = token_from(operator.get(endpoint))
    response = operator.post(endpoint, data={"csrf": token, "email": "bad", "registered_on": "2026-02-30"})
    assert response.status_code == 422
    assert b"valid value for email" in response.data and b"Given name is required" in response.data
    farmer = query("SELECT farmer_id FROM Farm LIMIT 1")[0]["farmer_id"]
    response = operator.post(f"/records/farmers/{farmer}/delete", data={"csrf": token}, follow_redirects=True)
    assert b"Related records reference" in response.data

def test_dashboard_reports_and_demo_pages(operator):
    assert operator.get("/dashboard").data.count(b"<canvas") == 5
    assert operator.get("/reports?year=2025&season=Kharif").status_code == 200
    report = operator.get("/reports?year=2025&season=Kharif&format=csv")
    assert report.mimetype == "text/csv" and b"2025,Kharif" in report.data
    assert operator.get("/dbms").status_code == 200
    assert operator.get("/allocate").status_code == 200

def test_catalogue_filters_and_pagination(client):
    response = client.get("/records/crops?origin_region=Karnataka&growing_season=Kharif")
    assert b"Finger millet" in response.data and b"Pearl millet" not in response.data
    response = client.get("/records/crops?page=2&slug=ignored")
    assert b"Page 2 of 3" in response.data
