"""Populate an empty installation with reproducible, explicitly synthetic records."""
from datetime import date, timedelta
from decimal import Decimal
from random import Random

from models.catalog import MODULES, identifier
from models.db import connection

CROPS = """
Finger millet|Eleusine coracana|Millet|Karnataka|Kharif
Pearl millet|Cenchrus americanus|Millet|Rajasthan|Kharif
Foxtail millet|Setaria italica|Millet|Karnataka|Kharif
Little millet|Panicum sumatrense|Millet|Odisha|Kharif
Kodo millet|Paspalum scrobiculatum|Millet|Madhya Pradesh|Kharif
Barnyard millet|Echinochloa frumentacea|Millet|Uttarakhand|Kharif
Proso millet|Panicum miliaceum|Millet|Madhya Pradesh|Kharif
Sorghum|Sorghum bicolor|Cereal|Maharashtra|Kharif
Asian rice|Oryza sativa|Cereal|West Bengal|Kharif
Emmer wheat|Triticum dicoccum|Cereal|Karnataka|Rabi
Barley|Hordeum vulgare|Cereal|Rajasthan|Rabi
Chickpea|Cicer arietinum|Pulse|Madhya Pradesh|Rabi
Pigeon pea|Cajanus cajan|Pulse|Maharashtra|Kharif
Green gram|Vigna radiata|Pulse|Rajasthan|Zaid
Black gram|Vigna mungo|Pulse|Tamil Nadu|Kharif
Horse gram|Macrotyloma uniflorum|Pulse|Karnataka|Kharif
Moth bean|Vigna aconitifolia|Pulse|Rajasthan|Kharif
Cowpea|Vigna unguiculata|Pulse|Tamil Nadu|Kharif
Lentil|Lens culinaris|Pulse|Madhya Pradesh|Rabi
Field pea|Pisum sativum|Pulse|Uttarakhand|Rabi
Lablab bean|Lablab purpureus|Pulse|Karnataka|Kharif
Sesame|Sesamum indicum|Oilseed|Odisha|Kharif
Indian mustard|Brassica juncea|Oilseed|Rajasthan|Rabi
Niger seed|Guizotia abyssinica|Oilseed|Odisha|Kharif
Linseed|Linum usitatissimum|Oilseed|Madhya Pradesh|Rabi
Safflower|Carthamus tinctorius|Oilseed|Maharashtra|Rabi
Castor|Ricinus communis|Oilseed|Gujarat|Kharif
Brinjal|Solanum melongena|Vegetable|West Bengal|Kharif
Bottle gourd|Lagenaria siceraria|Vegetable|Uttar Pradesh|Zaid
Bitter gourd|Momordica charantia|Vegetable|Odisha|Zaid
Ridge gourd|Luffa acutangula|Vegetable|Karnataka|Zaid
Snake gourd|Trichosanthes cucumerina|Vegetable|Tamil Nadu|Zaid
Ash gourd|Benincasa hispida|Vegetable|Kerala|Zaid
Taro|Colocasia esculenta|Tuber|Odisha|Kharif
Elephant foot yam|Amorphophallus paeoniifolius|Tuber|Kerala|Kharif
Turmeric|Curcuma longa|Spice|Tamil Nadu|Kharif
Ginger|Zingiber officinale|Spice|Kerala|Kharif
Fenugreek|Trigonella foenum-graecum|Spice|Rajasthan|Rabi
Coriander|Coriandrum sativum|Spice|Gujarat|Rabi
Cumin|Cuminum cyminum|Spice|Gujarat|Rabi
""".strip().splitlines()
PLACES = (("Mandya", "Karnataka"), ("Koraput", "Odisha"), ("Nashik", "Maharashtra"),
          ("Barmer", "Rajasthan"), ("Madurai", "Tamil Nadu"), ("Wayanad", "Kerala"))
FERTILIZERS = ("Composted straw", "Leaf compost", "Farmyard compost", "Green manure",
               "Vermicompost", "Plant residue mulch")
FERTILIZER_NOTES = (
    ("Straw and partially decomposed leaves", "Layer the demo residues in a compost bay and log turning and moisture."),
    ("Collected leaves", "Record the source and keep decomposing leaf material in a covered bay."),
    ("Bedding and livestock manure", "Record source and compost maturity before planning field application."),
    ("Cover crop biomass", "Record when the cover crop is terminated and how residues are managed."),
    ("Plant bedding and organic residues", "Log feed additions and separate mature castings from the bedding."),
    ("Chopped plant residues", "Record area covered and keep field notes on soil cover."),
)
CROP_USES = {
    "Finger millet": "Grain flour is used for ragi mudde and porridges.",
    "Pearl millet": "Grain flour is used for bajra roti.",
    "Sorghum": "Grain flour is used for jowar bhakri.",
    "Chickpea": "Milled chickpea is used as besan.",
    "Turmeric": "The rhizome is used as a spice.",
    "Sesame": "Seeds are used in sweets and pressed for oil.",
}
TOPICS = ("Seed selection", "Dry seed storage", "Rainwater collection", "Mixed cropping",
          "Organic matter management", "Manual threshing", "Seasonal crop rotation",
          "Field bund maintenance", "Nursery preparation", "Harvest drying")
SYNTHETIC_NOTE = "Synthetic classroom record. No historical or community attribution is asserted."

def seed():
    rng = Random(2407)
    with connection() as db, db.cursor() as cursor:
        for module in MODULES.values():
            cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {identifier(module.table)})")
            if cursor.fetchone()[0]:
                raise SystemExit("Seed the demo only into an empty application database.")

        def add(table, **fields):
            columns = ", ".join(map(identifier, fields))
            placeholders = ", ".join(["%s"] * len(fields))
            cursor.execute(f"INSERT INTO {identifier(table)} ({columns}) VALUES ({placeholders})",
                           tuple(fields.values()))
            return cursor.lastrowid

        crops = []
        for line in CROPS:
            name, scientific, category, region, season = line.split("|")
            key = add("Indigenous_Crop", common_name=name, scientific_name=scientific, category=category,
                      origin_region=region, growing_season=season, traditional_uses=CROP_USES.get(name),
                      historical_region_notes="Region and season are illustrative catalogue classifications.",
                      reference_url="https://powo.science.kew.org/")
            crops.append((key, name, region, season, category))

        farms = []
        for i in range(30):
            district, state = PLACES[i % len(PLACES)]
            farmer = add("Farmer", registration_code=f"DEMO-F{i+1:03}", given_name=f"Demo grower {i+1:02}",
                         district=district, state_name=state, farming_since_year=2003 + i % 17,
                         indigenous_since_year=2019 + i % 4, registered_on=date(2024, 1, 1),
                         specialization=("Mixed cropping", "Dryland crops", "Seed saving")[i % 3],
                         synthetic=True)
            area = Decimal(rng.randint(24, 80)) / 10
            farm = add("Farm", farmer_id=farmer, farm_code=f"DEMO-A{i+1:03}", name=f"{district} demo plot {i+1:02}",
                       village=f"Demo village {i % 9 + 1}", district=district, state_name=state,
                       land_area_ha=area, cultivable_area_ha=area - Decimal("0.20"),
                       tenure="Family holding (demo)", terrain=("Flat", "Gently sloping")[i % 2],
                       water_availability=("Seasonal", "Year-round")[i % 2], farming_system="Mixed farming")
            farms.append(farm)

        varieties = []
        for i in range(50):
            crop, name, region, season, category = crops[i % len(crops)]
            variety = add("Seed_Variety", crop_id=crop, accession_code=f"DEMO-V{i+1:03}",
                          name=f"{name} demo accession {i // len(crops) + 1}", origin_region=region,
                          germination_pct=rng.randint(74, 96), conservation_status="Demonstration accession",
                          documentation_date=date(2024, 2, 10), documentation_source=SYNTHETIC_NOTE, synthetic=True)
            varieties.append((variety, season, category))

        for i in range(60):
            variety, _, category = varieties[i % len(varieties)]
            quantity = rng.randint(2, 40)
            add("Seed_Storage", seed_variety_id=variety, batch_number=f"DEMO-B{i+1:03}",
                storage_location=f"Demo seed bank {i % 6 + 1}", container="Lidded container",
                initial_quantity=quantity + 2, current_quantity=quantity,
                quantity_unit="count" if category == "Tuber" else "kg", low_stock_threshold=6,
                stored_on=date(2025, 1, 1), expected_expiry_on=date(2030, 12, 31),
                temperature_c=rng.randint(17, 25), humidity_pct=rng.randint(38, 57),
                germination_tested_on=date(2025, 4, 1), germination_pct=rng.randint(71, 95),
                pest_inspected_on=date(2025, 4, 1), pest_findings="None observed (simulated)",
                condition_notes=SYNTHETIC_NOTE, status="quarantined" if i % 11 == 10 else "available")

        for i in range(100):
            farm = farms[i % len(farms)]
            variety, season, category = varieties[i % len(varieties)]
            month = {"Kharif": 7, "Rabi": 11, "Zaid": 3}[season]
            sowing = date(2024 + i % 2, month, 1 + i % 20)
            harvest = sowing + timedelta(days=100 + i % 25)
            add("Soil_Record", farm_id=farm, sample_code=f"DEMO-S{i+1:03}", sampled_on=sowing - timedelta(days=14),
                depth_top_cm=0, depth_bottom_cm=20, texture=("Loam", "Sandy loam", "Clay loam")[i % 3],
                ph=Decimal(rng.randint(55, 80)) / 10, organic_carbon_pct=Decimal(rng.randint(35, 110)) / 100,
                ec_ds_m=Decimal("0.47"), moisture_pct=rng.randint(16, 26),
                fertility=("medium", "low", "high")[i % 3], lab_name="Simulated lab")
            count_unit = category == "Tuber"
            code = f"DEMO-C{i+1:03}"
            cultivation = add("Cultivation_Record", farm_id=farm, seed_variety_id=variety, cultivation_code=code,
                              sowing_date=sowing, season=season, seed_quantity=rng.randint(2, 8),
                              seed_unit="count" if count_unit else "kg", area_ha=Decimal(rng.randint(5, 17))/10,
                              sowing_method="Direct planting", growth_stage="Harvested", stage_observed_on=harvest,
                              expected_harvest_date=harvest, status="completed")
            if i < 20:
                add("Cultivation_Record", farm_id=farm, seed_variety_id=variety,
                    cultivation_code=f"DEMO-ACT{i+1:03}", sowing_date=date(2026, month, 1 + i % 20), season=season,
                    area_ha=Decimal("0.50"), growth_stage="Sown", status="active")
            add("Irrigation_Record", cultivation_id=cultivation, event_code=f"DEMO-I{i+1:03}",
                irrigated_on=sowing + timedelta(days=12), method=("Furrow", "Drip", "Basin")[i % 3],
                traditional_technique="Gravity-fed field channels (illustrative)" if i % 3 == 0 else None,
                water_source="Farm reservoir", quantity_l=rng.randint(600, 1300),
                duration_minutes=rng.randint(20, 70), moisture_before_pct=16, moisture_after_pct=24)
            net = rng.randint(140, 960)
            add("Harvest_Record", cultivation_id=cultivation, harvest_code=f"DEMO-H{i+1:03}",
                harvested_on=harvest, harvest_method="Manual", harvested_area_ha=Decimal("0.45"),
                gross_yield=net + rng.randint(4, 38), net_yield=net, yield_unit="count" if count_unit else "kg",
                loss_cause="Sorting and field losses (simulated)", quality_grade=("A", "B")[i % 2])
            if i < 60:
                observed = sowing + timedelta(days=24)
                add("Pest_Management", cultivation_id=cultivation, observation_code=f"DEMO-P{i+1:03}",
                    pest_name=("Aphid", "Leaf spot", "Stem borer")[i % 3],
                    symptoms=("Leaf curling", "Small lesions", "Stem damage")[i % 3],
                    severity=("low", "medium", "high")[i % 3], observed_on=observed,
                    treatment_name="Hand removal" if i % 3 == 2 else None,
                    applied_on=observed + timedelta(days=1) if i % 3 == 2 else None,
                    follow_up_on=observed + timedelta(days=7), follow_up_notes="Simulated follow-up",
                    evidence_level="field observation", synthetic=True)
            if i < 50:
                add("Crop_Rotation", farm_id=farm, previous_crop_id=crops[(i+3) % 40][0],
                    current_crop_id=crops[i % 40][0], next_crop_id=crops[(i+11) % 40][0],
                    plan_code=f"DEMO-R{i+1:03}", start_date=sowing, end_date=harvest, season=season,
                    objective=("Diversify crop families", "Maintain soil cover")[i % 2], planned_area_ha=1)

        for i in range(30):
            topic = FERTILIZERS[i % len(FERTILIZERS)]
            ingredients, preparation = FERTILIZER_NOTES[i % len(FERTILIZERS)]
            add("Organic_Fertilizer", recipe_code=f"DEMO-O{i+1:03}", name=f"{topic} · demo {i+1:02}",
                category="Plant residue" if i % 3 == 0 else "Organic amendment",
                main_ingredients=ingredients, preparation_method=preparation,
                safety_precautions="Demo entry only. Consult local extension guidance before use.",
                source_reference=SYNTHETIC_NOTE, region=PLACES[i % len(PLACES)][1], synthetic=True)
        for i in range(50):
            crop, _, region, season, category = crops[i % 40]
            topic = TOPICS[i % len(TOPICS)]
            add("Traditional_Knowledge", crop_id=crop, entry_code=f"DEMO-K{i+1:03}",
                practice_name=f"{topic} · demo {i+1:02}", category=topic,
                origin_region=region, description=f"Example catalogue entry for documenting {topic.lower()}.",
                procedure_notes="Example recording workflow: note the material, timing and reason for each step.",
                seasonal_relevance=season, documented_on=date(2025, 1, 1), limitations=SYNTHETIC_NOTE,
                access_level="restricted" if i % 9 == 8 else "public", synthetic=True)

if __name__ == "__main__":
    seed()
