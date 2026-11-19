from models.db import connection, query

YIELD_TOTALS = "SELECT yield_unit AS unit, SUM(net_yield) AS total FROM Harvest_Record GROUP BY yield_unit ORDER BY yield_unit"

DEMONSTRATIONS = {
    "Right join": """SELECT f.registration_code, a.name AS farm
FROM Farm a RIGHT JOIN Farmer f ON f.id=a.farmer_id ORDER BY f.id LIMIT 12""",
    "Multi-table join": """SELECT a.name AS farm, i.common_name AS crop, h.net_yield, h.yield_unit
FROM Harvest_Record h JOIN Cultivation_Record c ON c.id=h.cultivation_id
JOIN Farm a ON a.id=c.farm_id LEFT JOIN Seed_Variety v ON v.id=c.seed_variety_id
JOIN Indigenous_Crop i ON i.id=COALESCE(c.crop_id,v.crop_id) ORDER BY h.id LIMIT 12""",
    "Aggregation and HAVING": """SELECT yield_unit, COUNT(*) AS entries, SUM(net_yield) AS total,
AVG(net_yield) AS average, MIN(net_yield) AS minimum, MAX(net_yield) AS maximum
FROM Harvest_Record GROUP BY yield_unit HAVING COUNT(*) > 1""",
    "Correlated EXISTS": """SELECT i.common_name FROM Indigenous_Crop i
WHERE EXISTS (SELECT 1 FROM Seed_Variety v WHERE v.crop_id=i.id) ORDER BY i.id LIMIT 12""",
    "Farmer cultivation view": "SELECT * FROM Farmer_Cultivation_Summary ORDER BY farmer_id LIMIT 12",
    "Seed availability view": "SELECT * FROM Indigenous_Seed_Availability ORDER BY variety_id LIMIT 12",
    "Seasonal harvest view": "SELECT * FROM Seasonal_Harvest_Report ORDER BY harvest_year DESC, season, yield_unit",
    "Location index EXPLAIN": "EXPLAIN SELECT id FROM Farm WHERE state_name='Karnataka' AND district='Mandya'",
}

def dashboard():
    stats = query("""SELECT
     (SELECT COUNT(*) FROM Farmer) AS farmers,
     (SELECT COUNT(*) FROM Farm) AS farms,
     (SELECT COUNT(*) FROM Indigenous_Crop) AS crops,
     (SELECT COUNT(*) FROM Seed_Variety) AS varieties,
     (SELECT COUNT(*) FROM Cultivation_Record WHERE status='active') AS active,
     (SELECT COUNT(*) FROM Seed_Storage WHERE status='available' AND current_quantity>0
        AND (expected_expiry_on IS NULL OR expected_expiry_on>=CURRENT_DATE)) AS seed_batches,
     (SELECT COUNT(*) FROM Traditional_Knowledge) AS practices""")[0]
    charts = [
        ("Crop distribution", "doughnut", query("SELECT category AS label, COUNT(*) AS value FROM Indigenous_Crop GROUP BY category ORDER BY category")),
        ("Seasonal cultivation", "bar", query("SELECT season AS label, COUNT(*) AS value FROM Cultivation_Record GROUP BY season ORDER BY season")),
        ("Soil fertility", "doughnut", query("""SELECT COALESCE(fertility,'Unclassified') AS label,
          COUNT(*) AS value FROM Soil_Record GROUP BY fertility""")),
        ("Harvest trends", "line", query("""SELECT DATE_FORMAT(harvested_on,'%Y-%m') AS label,
          yield_unit AS series, SUM(net_yield) AS value FROM Harvest_Record
          GROUP BY label, series ORDER BY label, series""")),
        ("Indigenous seed availability", "bar", query("""SELECT common_name AS label, quantity_unit AS series,
          SUM(available_quantity) AS value FROM Indigenous_Seed_Availability
          WHERE available_quantity > 0 GROUP BY label, series ORDER BY label, series""")),
    ]
    return stats, query(YIELD_TOTALS), charts

PROCEDURES = {"farmer_cultivations", "seasonal_harvest", "adjust_seed_stock", "allocate_seed"}

def call(procedure, args):
    if procedure not in PROCEDURES:
        raise ValueError("Unknown procedure")
    placeholders = ", ".join(["%s"] * len(args))
    with connection() as db, db.cursor(dictionary=True) as cursor:
        cursor.execute(f"CALL {procedure}({placeholders})", args)
        rows = []
        while True:
            if cursor.with_rows:
                rows.extend(cursor.fetchall())
            if not cursor.nextset():
                break
        return rows
