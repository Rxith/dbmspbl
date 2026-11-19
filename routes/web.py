import csv
from datetime import date, timedelta
from io import StringIO
from decimal import Decimal, InvalidOperation
from hmac import compare_digest

from flask import (Blueprint, Response, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)
from mysql.connector import Error

from models.catalog import MODULES, identifier
from models.db import execute, query
from services.records import TABLES, editable_fields, friendly_error, parse_values, schema_fields
from services.reporting import DEMONSTRATIONS, call, dashboard

web = Blueprint("web", __name__)

def operator_only():
    if not session.get("operator"):
        return redirect(url_for("web.login"))
    return None

def module_for(slug):
    return MODULES.get(slug) or abort(404)

def public_guard(slug):
    if slug == "knowledge" and not session.get("operator"):
        return "access_level = 'public'"
    return "1=1"

def lookup(slug, record_id):
    module = module_for(slug)
    rows = query(f"SELECT * FROM {identifier(module.table)} WHERE id=%s AND {public_guard(slug)}", (record_id,))
    return rows[0] if rows else abort(404)

@web.get("/")
def home():
    return render_template("home.html")

@web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = current_app.config["OPERATOR_PASSWORD"]
        if password and compare_digest(password.encode(), request.form.get("password", "").encode()):
            session.clear()
            session["operator"] = True
            return redirect(url_for("web.dashboard_page"))
        flash("The operator password is incorrect or has not been configured.", "danger")
        return render_template("login.html"), 401
    return render_template("login.html")

@web.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.home"))

@web.get("/dashboard")
def dashboard_page():
    if (response := operator_only()) is not None:
        return response
    stats, totals, charts = dashboard()
    return render_template("dashboard.html", stats=stats, totals=totals, charts=charts)

@web.get("/records/<slug>")
def records(slug):
    module = module_for(slug)
    if not module.public and (response := operator_only()) is not None:
        return response
    table = identifier(module.table)
    guard = public_guard(slug)
    where = [guard]
    args = []
    search = request.args.get("q", "").strip()[:120]
    if search:
        where.append("(" + " OR ".join(f"CAST({identifier(field)} AS CHAR) LIKE %s ESCAPE '!'" for field in module.fields) + ")")
        pattern = "%" + search.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
        args.extend([pattern] * len(module.fields))
    filters = {}
    for field in module.filters:
        column = identifier(field)
        filters[field] = [row["value"] for row in query(
            f"SELECT DISTINCT {column} AS value FROM {table} WHERE {column} IS NOT NULL AND {guard} ORDER BY 1")]
        if value := request.args.get(field, "")[:150]:
            where.append(f"{column} = %s")
            args.append(value)
    criteria = " AND ".join(where)
    total = query(f"SELECT COUNT(*) AS total FROM {table} WHERE {criteria}", tuple(args))[0]["total"]
    pages = max(1, (total + 14) // 15)
    page = min(pages, max(1, request.args.get("page", 1, type=int)))
    rows = query(f"SELECT * FROM {table} WHERE {criteria} ORDER BY id DESC LIMIT 15 OFFSET %s",
                 (*args, (page - 1) * 15))
    other_args = {key: request.args[key] for key in ("q", *module.filters) if key in request.args}
    return render_template("records.html", slug=slug, module=module, rows=rows, total=total,
                           filters=filters, page=page, pages=pages, other_args=other_args)

@web.get("/records/<slug>/<int:record_id>")
def detail(slug, record_id):
    module = module_for(slug)
    if not module.public and (response := operator_only()) is not None:
        return response
    row = lookup(slug, record_id)
    fields = schema_fields(module.table)
    related = []
    if slug == "crops":
        related = query("SELECT id,name FROM Seed_Variety WHERE crop_id=%s ORDER BY name", (record_id,))
    return render_template("detail.html", slug=slug, module=module, row=row, fields=fields,
                           related=related, tables=TABLES)

@web.route("/records/<slug>/new", methods=["GET", "POST"])
@web.route("/records/<slug>/<int:record_id>/edit", methods=["GET", "POST"])
def edit(slug, record_id=None):
    if (response := operator_only()) is not None:
        return response
    module = module_for(slug)
    row = lookup(slug, record_id) if record_id else {}
    fields = editable_fields(module.table, updating=bool(record_id))
    values = {field["name"]: row.get(field["name"], field["default_value"]) for field in fields}
    for field in fields:
        value = values[field["name"]]
        if field["kind"] == "time" and isinstance(value, timedelta):
            hours, seconds = divmod(int(value.total_seconds()), 3600)
            minutes, seconds = divmod(seconds, 60)
            values[field["name"]] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    errors = []
    if request.method == "POST":
        values = request.form.to_dict()
        if not record_id:
            for field in fields:
                if field["default_value"] is not None:
                    values.setdefault(field["name"], field["default_value"])
        data, errors = parse_values(fields, values)
        if not errors:
            table = identifier(module.table)
            try:
                if record_id:
                    assignments = ", ".join(f"{identifier(key)}=%s" for key in data)
                    execute(f"UPDATE {table} SET {assignments} WHERE id=%s", (*data.values(), record_id))
                else:
                    columns = ", ".join(map(identifier, data))
                    placeholders = ", ".join(["%s"] * len(data))
                    record_id = execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(data.values()))
                flash("Record saved.", "success")
                return redirect(url_for("web.detail", slug=slug, record_id=record_id))
            except Error as error:
                errors.append(friendly_error(error))
    return render_template("form.html", slug=slug, module=module, record_id=record_id,
                           values=values, fields=fields, errors=errors), 422 if errors else 200

@web.post("/records/<slug>/<int:record_id>/delete")
def delete(slug, record_id):
    if (response := operator_only()) is not None:
        return response
    module = module_for(slug)
    lookup(slug, record_id)
    try:
        execute(f"DELETE FROM {identifier(module.table)} WHERE id=%s", (record_id,))
    except Error as error:
        flash(friendly_error(error), "danger")
        return redirect(url_for("web.detail", slug=slug, record_id=record_id))
    flash("Record deleted.", "success")
    return redirect(url_for("web.records", slug=slug))

def decimal_input(name, precision, scale):
    value = Decimal(request.form[name])
    if not value.is_finite() or value.as_tuple().exponent < -scale or abs(value) >= 10**(precision-scale):
        raise ValueError
    return value

@web.post("/records/storage/<int:record_id>/adjust")
def adjust_stock(record_id):
    if (response := operator_only()) is not None:
        return response
    try:
        call("adjust_seed_stock", (record_id, decimal_input("delta", 12, 3)))
        flash("Stock adjusted.", "success")
    except (ValueError, InvalidOperation, KeyError):
        flash("Enter a quantity adjustment with up to three decimal places.", "danger")
    except Error as error:
        flash(friendly_error(error), "danger")
    return redirect(url_for("web.detail", slug="storage", record_id=record_id))

SEASONS = ("Kharif", "Rabi", "Zaid", "Perennial")

@web.route("/allocate", methods=["GET", "POST"])
def allocate():
    if (response := operator_only()) is not None:
        return response
    if request.method == "POST":
        try:
            farm = int(request.form["farm"])
            batch = int(request.form["batch"])
            sowing = date.fromisoformat(request.form["sowing"])
            code = request.form["code"].strip()
            season = request.form["season"]
            if not code or len(code) > 40 or season not in SEASONS:
                raise ValueError
            call("allocate_seed", (batch, decimal_input("quantity", 12, 3), farm,
                                   code, sowing, season, decimal_input("area", 10, 2)))
            flash("Seed allocated and cultivation created.", "success")
            return redirect(url_for("web.records", slug="cultivation"))
        except (ValueError, InvalidOperation, KeyError):
            flash("Enter valid allocation, farm, and cultivation values.", "danger")
        except Error as error:
            flash(friendly_error(error), "danger")
    return render_template("allocate.html", farms=query("SELECT id,name FROM Farm ORDER BY name"),
                           batches=query("""SELECT id,batch_number,current_quantity,quantity_unit
                             FROM Seed_Storage WHERE status='available' AND current_quantity>0
                             AND (expected_expiry_on IS NULL OR expected_expiry_on>=CURRENT_DATE)
                             ORDER BY batch_number"""), seasons=SEASONS)

@web.get("/reports")
def reports():
    if (response := operator_only()) is not None:
        return response
    season = request.args.get("season") or None
    year = request.args.get("year", type=int)
    if season and season not in SEASONS:
        abort(400)
    if request.args.get("year") and (year is None or not 1000 <= year <= 9999):
        abort(400)
    rows = call("seasonal_harvest", (year, season))
    if request.args.get("format") == "csv":
        output = StringIO()
        writer = csv.writer(output)
        fields = ("harvest_year", "season", "yield_unit", "harvests", "gross_yield", "net_yield", "losses")
        writer.writerow(fields)
        writer.writerows([row[field] for field in fields] for row in rows)
        return Response(output.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=seasonal-harvest.csv"})
    return render_template("reports.html", rows=rows, seasons=SEASONS, season=season, year=year)

@web.get("/dbms")
def demo():
    if (response := operator_only()) is not None:
        return response
    selected = request.args.get("example", next(iter(DEMONSTRATIONS)))
    sql = DEMONSTRATIONS.get(selected) or abort(400)
    farmer_id = request.args.get("farmer", type=int)
    farmers = query("SELECT id,registration_code FROM Farmer ORDER BY registration_code")
    rows = call("farmer_cultivations", (farmer_id,)) if farmer_id else query(sql)
    if farmer_id:
        sql = "CALL farmer_cultivations(?)"
    return render_template("demo.html", rows=rows, sql=sql, selected=selected,
                           examples=DEMONSTRATIONS, farmers=farmers, farmer_id=farmer_id)
