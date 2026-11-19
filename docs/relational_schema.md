# Relational schema and attribute dictionary

Generated from `database/schema.sql` with `python -m database.schema_docs`.

**13 tables and 329 attributes.** Unmarked optional columns default to NULL. All foreign keys default to RESTRICT. Measurement units appear in names or companion unit fields.

## Farmer (26 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `registration_code` | `VARCHAR(32)` | `NOT NULL UNIQUE` |
| `given_name` | `VARCHAR(80)` | `NOT NULL` |
| `family_name` | `VARCHAR(80)` | `NULL` |
| `email` | `VARCHAR(254)` | `NULL` |
| `phone` | `VARCHAR(30)` | `NULL` |
| `village` | `VARCHAR(100)` | `NULL` |
| `block_name` | `VARCHAR(100)` | `NULL` |
| `district` | `VARCHAR(100)` | `NULL` |
| `state_name` | `VARCHAR(100)` | `NULL` |
| `postal_code` | `VARCHAR(10)` | `NULL` |
| `preferred_language` | `VARCHAR(60)` | `NULL` |
| `farming_since_year` | `SMALLINT` | `CHECK (farming_since_year BETWEEN 1900 AND 2100)` |
| `indigenous_since_year` | `SMALLINT` | `CHECK (indigenous_since_year BETWEEN 1900 AND 2100)` |
| `education_level` | `VARCHAR(80)` | `NULL` |
| `training_topic` | `VARCHAR(160)` | `NULL` |
| `training_provider` | `VARCHAR(160)` | `NULL` |
| `training_completed_on` | `DATE` | `NULL` |
| `specialization` | `VARCHAR(100)` | `NULL` |
| `management_role` | `VARCHAR(100)` | `NULL` |
| `knowledge_participation` | `TEXT` | `NULL` |
| `contact_consent` | `BOOLEAN` | `NOT NULL DEFAULT FALSE CHECK (contact_consent IN (0,1))` |
| `registered_on` | `DATE` | `NOT NULL` |
| `verification_status` | `ENUM('pending','verified','declined')` | `NOT NULL DEFAULT 'pending'` |
| `verified_on` | `DATE` | `NULL` |
| `synthetic` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` |

Table-level rules

- `CHECK (indigenous_since_year >= farming_since_year)`

## Farm (26 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `farmer_id` | `INT` | `NOT NULL; FK → Farmer(id)` |
| `farm_code` | `VARCHAR(32)` | `NOT NULL UNIQUE` |
| `name` | `VARCHAR(120)` | `NOT NULL` |
| `village` | `VARCHAR(100)` | `NOT NULL` |
| `district` | `VARCHAR(100)` | `NOT NULL` |
| `state_name` | `VARCHAR(100)` | `NOT NULL` |
| `latitude` | `DECIMAL(8,5)` | `CHECK (latitude BETWEEN -90 AND 90)` |
| `longitude` | `DECIMAL(8,5)` | `CHECK (longitude BETWEEN -180 AND 180)` |
| `land_area_ha` | `DECIMAL(10,2)` | `NOT NULL CHECK (land_area_ha > 0)` |
| `cultivable_area_ha` | `DECIMAL(10,2)` | `NOT NULL CHECK (cultivable_area_ha >= 0)` |
| `tenure` | `VARCHAR(70)` | `NULL` |
| `elevation_m` | `DECIMAL(8,2)` | `NULL` |
| `terrain` | `VARCHAR(80)` | `NULL` |
| `climate_zone` | `VARCHAR(80)` | `NULL` |
| `baseline_soil` | `VARCHAR(80)` | `NULL` |
| `water_availability` | `VARCHAR(100)` | `NULL` |
| `water_source` | `VARCHAR(100)` | `NULL` |
| `irrigation_infrastructure` | `TEXT` | `NULL` |
| `farming_system` | `VARCHAR(100)` | `NULL` |
| `organic_certificate` | `VARCHAR(100)` | `NULL` |
| `certification_body` | `VARCHAR(120)` | `NULL` |
| `certificate_expires_on` | `DATE` | `NULL` |
| `land_use` | `ENUM('active','fallow','archived')` | `NOT NULL DEFAULT 'active'` |
| `created_at` | `TIMESTAMP` | `NOT NULL DEFAULT CURRENT_TIMESTAMP` |
| `updated_at` | `TIMESTAMP` | `NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` |

Table-level rules

- `FOREIGN KEY (farmer_id) REFERENCES Farmer(id)`
- `CHECK (cultivable_area_ha <= land_area_ha)`
- `INDEX ix_farm_location (state_name,district,village)`

## Indigenous_Crop (26 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `common_name` | `VARCHAR(120)` | `NOT NULL UNIQUE` |
| `scientific_name` | `VARCHAR(160)` | `NOT NULL` |
| `regional_name` | `VARCHAR(120)` | `NULL` |
| `regional_language` | `VARCHAR(80)` | `NULL` |
| `category` | `VARCHAR(80)` | `NOT NULL` |
| `origin_region` | `VARCHAR(120)` | `NOT NULL` |
| `historical_region_notes` | `TEXT` | `NULL` |
| `growing_season` | `ENUM('Kharif','Rabi','Zaid','Perennial')` | `NOT NULL` |
| `climate` | `VARCHAR(100)` | `NULL` |
| `min_temp_c` | `DECIMAL(5,2)` | `NULL` |
| `max_temp_c` | `DECIMAL(5,2)` | `NULL` |
| `min_rainfall_mm` | `DECIMAL(8,2)` | `CHECK (min_rainfall_mm >= 0)` |
| `max_rainfall_mm` | `DECIMAL(8,2)` | `CHECK (max_rainfall_mm >= 0)` |
| `preferred_soil` | `VARCHAR(100)` | `NULL` |
| `growth_days` | `SMALLINT UNSIGNED` | `CHECK (growth_days > 0)` |
| `edible_part` | `VARCHAR(80)` | `NULL` |
| `traditional_uses` | `TEXT` | `NULL` |
| `nutrition_notes` | `TEXT` | `NULL` |
| `pollination` | `VARCHAR(80)` | `NULL` |
| `propagation_method` | `VARCHAR(100)` | `NULL` |
| `drought_response` | `VARCHAR(100)` | `NULL` |
| `cultivation_notes` | `TEXT` | `NULL` |
| `conservation_status` | `VARCHAR(80)` | `NULL` |
| `conservation_notes` | `TEXT` | `NULL` |
| `reference_url` | `VARCHAR(500)` | `NULL` |

Table-level rules

- `CHECK (min_temp_c <= max_temp_c)`
- `CHECK (min_rainfall_mm <= max_rainfall_mm)`

## Seed_Variety (26 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `crop_id` | `INT` | `NOT NULL; FK → Indigenous_Crop(id)` |
| `accession_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `name` | `VARCHAR(120)` | `NOT NULL` |
| `origin_region` | `VARCHAR(120)` | `NULL` |
| `origin_locality` | `VARCHAR(120)` | `NULL` |
| `seed_colour` | `VARCHAR(60)` | `NULL` |
| `seed_shape` | `VARCHAR(60)` | `NULL` |
| `seed_length_mm` | `DECIMAL(6,2)` | `CHECK (seed_length_mm > 0)` |
| `thousand_seed_mass_g` | `DECIMAL(9,3)` | `CHECK (thousand_seed_mass_g > 0)` |
| `germination_pct` | `DECIMAL(5,2)` | `CHECK (germination_pct BETWEEN 0 AND 100)` |
| `germination_days` | `SMALLINT UNSIGNED` | `NULL` |
| `purity_pct` | `DECIMAL(5,2)` | `CHECK (purity_pct BETWEEN 0 AND 100)` |
| `moisture_target_pct` | `DECIMAL(5,2)` | `CHECK (moisture_target_pct BETWEEN 0 AND 100)` |
| `storage_max_temp_c` | `DECIMAL(5,2)` | `NULL` |
| `storage_max_rh_pct` | `DECIMAL(5,2)` | `CHECK (storage_max_rh_pct BETWEEN 0 AND 100)` |
| `storage_container` | `VARCHAR(100)` | `NULL` |
| `dormancy_notes` | `TEXT` | `NULL` |
| `seed_treatment` | `TEXT` | `NULL` |
| `expected_viability_months` | `SMALLINT UNSIGNED` | `NULL` |
| `conservation_status` | `VARCHAR(80)` | `NULL` |
| `sourcing_notes` | `TEXT` | `NULL` |
| `multiplication_method` | `VARCHAR(120)` | `NULL` |
| `documentation_date` | `DATE` | `NULL` |
| `documentation_source` | `VARCHAR(250)` | `NULL` |
| `synthetic` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` |

Table-level rules

- `FOREIGN KEY (crop_id) REFERENCES Indigenous_Crop(id)`

## Soil_Record (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `farm_id` | `INT` | `NOT NULL; FK → Farm(id)` |
| `sample_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `sampled_on` | `DATE` | `NOT NULL` |
| `plot_label` | `VARCHAR(80)` | `NULL` |
| `depth_top_cm` | `DECIMAL(6,2)` | `NOT NULL CHECK (depth_top_cm >= 0)` |
| `depth_bottom_cm` | `DECIMAL(6,2)` | `NOT NULL` |
| `texture` | `VARCHAR(80)` | `NULL` |
| `structure_description` | `VARCHAR(100)` | `NULL` |
| `ph` | `DECIMAL(4,2)` | `CHECK (ph BETWEEN 0 AND 14)` |
| `ec_ds_m` | `DECIMAL(7,3)` | `CHECK (ec_ds_m >= 0)` |
| `nitrogen_mg_kg` | `DECIMAL(9,2)` | `NULL` |
| `phosphorus_mg_kg` | `DECIMAL(9,2)` | `NULL` |
| `potassium_mg_kg` | `DECIMAL(9,2)` | `NULL` |
| `organic_carbon_pct` | `DECIMAL(5,2)` | `CHECK (organic_carbon_pct BETWEEN 0 AND 100)` |
| `moisture_pct` | `DECIMAL(5,2)` | `CHECK (moisture_pct BETWEEN 0 AND 100)` |
| `water_holding_pct` | `DECIMAL(5,2)` | `CHECK (water_holding_pct BETWEEN 0 AND 100)` |
| `drainage` | `VARCHAR(80)` | `NULL` |
| `zinc_mg_kg` | `DECIMAL(9,3)` | `NULL` |
| `iron_mg_kg` | `DECIMAL(9,3)` | `NULL` |
| `boron_mg_kg` | `DECIMAL(9,3)` | `NULL` |
| `fertility` | `ENUM('low','medium','high')` | `NULL` |
| `lab_name` | `VARCHAR(120)` | `NULL` |
| `analysis_method` | `VARCHAR(120)` | `NULL` |
| `management_recommendation` | `TEXT` | `NULL` |

Table-level rules

- `FOREIGN KEY (farm_id) REFERENCES Farm(id)`
- `CHECK (depth_bottom_cm > depth_top_cm)`
- `CHECK (nitrogen_mg_kg >= 0 AND phosphorus_mg_kg >= 0 AND potassium_mg_kg >= 0)`
- `CHECK (zinc_mg_kg >= 0 AND iron_mg_kg >= 0 AND boron_mg_kg >= 0)`

## Cultivation_Record (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `farm_id` | `INT` | `NOT NULL; FK → Farm(id)` |
| `crop_id` | `INT` | `NULL; FK → Indigenous_Crop(id)` |
| `seed_variety_id` | `INT` | `NULL; FK → Seed_Variety(id)` |
| `cultivation_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `sowing_date` | `DATE` | `NOT NULL` |
| `season` | `ENUM('Kharif','Rabi','Zaid','Perennial')` | `NOT NULL` |
| `plot_label` | `VARCHAR(80)` | `NULL` |
| `land_preparation` | `TEXT` | `NULL` |
| `sowing_method` | `VARCHAR(100)` | `NULL` |
| `seed_quantity` | `DECIMAL(12,3)` | `CHECK (seed_quantity > 0)` |
| `seed_unit` | `ENUM('kg','g','count')` | `NULL` |
| `row_spacing_cm` | `DECIMAL(7,2)` | `CHECK (row_spacing_cm > 0)` |
| `plant_spacing_cm` | `DECIMAL(7,2)` | `CHECK (plant_spacing_cm > 0)` |
| `area_ha` | `DECIMAL(10,2)` | `NOT NULL CHECK (area_ha > 0)` |
| `germination_observed_on` | `DATE` | `NULL` |
| `germination_pct` | `DECIMAL(5,2)` | `CHECK (germination_pct BETWEEN 0 AND 100)` |
| `weed_management` | `TEXT` | `NULL` |
| `traditional_technique` | `TEXT` | `NULL` |
| `growth_stage` | `VARCHAR(100)` | `NULL` |
| `stage_observed_on` | `DATE` | `NULL` |
| `expected_harvest_date` | `DATE` | `NULL` |
| `status` | `ENUM('planned','active','completed','abandoned')` | `NOT NULL DEFAULT 'active'` |
| `weather_notes` | `TEXT` | `NULL` |
| `field_notes` | `TEXT` | `NULL` |

Table-level rules

- `FOREIGN KEY (farm_id) REFERENCES Farm(id)`
- `FOREIGN KEY (crop_id) REFERENCES Indigenous_Crop(id)`
- `FOREIGN KEY (seed_variety_id) REFERENCES Seed_Variety(id)`
- `CHECK ((crop_id IS NULL) <> (seed_variety_id IS NULL))`
- `CHECK ((seed_quantity IS NULL) = (seed_unit IS NULL))`
- `CHECK (expected_harvest_date >= sowing_date)`
- `CHECK (germination_observed_on >= sowing_date AND stage_observed_on >= sowing_date)`
- `INDEX ix_cultivation_sowing (sowing_date)`

## Irrigation_Record (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `farm_id` | `INT` | `NULL; FK → Farm(id)` |
| `cultivation_id` | `INT` | `NULL; FK → Cultivation_Record(id)` |
| `event_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `irrigated_on` | `DATE` | `NOT NULL` |
| `started_at` | `TIME` | `NULL` |
| `method` | `VARCHAR(100)` | `NOT NULL` |
| `traditional_technique` | `VARCHAR(160)` | `NULL` |
| `water_source` | `VARCHAR(100)` | `NULL` |
| `quantity_l` | `DECIMAL(12,2)` | `CHECK (quantity_l > 0)` |
| `duration_minutes` | `SMALLINT UNSIGNED` | `CHECK (duration_minutes > 0)` |
| `distribution_method` | `VARCHAR(100)` | `NULL` |
| `moisture_before_pct` | `DECIMAL(5,2)` | `CHECK (moisture_before_pct BETWEEN 0 AND 100)` |
| `moisture_after_pct` | `DECIMAL(5,2)` | `CHECK (moisture_after_pct BETWEEN 0 AND 100)` |
| `water_availability` | `VARCHAR(100)` | `NULL` |
| `efficiency_observations` | `TEXT` | `NULL` |
| `maintenance_notes` | `TEXT` | `NULL` |
| `environmental_notes` | `TEXT` | `NULL` |
| `plot_label` | `VARCHAR(80)` | `NULL` |
| `irrigated_area_ha` | `DECIMAL(10,2)` | `CHECK (irrigated_area_ha > 0)` |
| `water_ec_ds_m` | `DECIMAL(7,3)` | `CHECK (water_ec_ds_m >= 0)` |
| `pumping_energy_kwh` | `DECIMAL(10,3)` | `CHECK (pumping_energy_kwh >= 0)` |
| `runoff_observed` | `BOOLEAN` | `CHECK (runoff_observed IN (0,1))` |
| `channel_condition` | `VARCHAR(100)` | `NULL` |
| `next_inspection_on` | `DATE` | `NULL` |

Table-level rules

- `FOREIGN KEY (farm_id) REFERENCES Farm(id)`
- `FOREIGN KEY (cultivation_id) REFERENCES Cultivation_Record(id)`
- `CHECK ((farm_id IS NULL) <> (cultivation_id IS NULL))`
- `CHECK (next_inspection_on >= irrigated_on)`

## Organic_Fertilizer (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `recipe_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `name` | `VARCHAR(120)` | `NOT NULL` |
| `category` | `VARCHAR(80)` | `NOT NULL` |
| `preparation_method` | `TEXT` | `NULL` |
| `main_ingredients` | `TEXT` | `NULL` |
| `preparation_days` | `SMALLINT UNSIGNED` | `NULL` |
| `fermentation_conditions` | `TEXT` | `NULL` |
| `mixing_schedule` | `VARCHAR(120)` | `NULL` |
| `maturity_indicators` | `TEXT` | `NULL` |
| `application_method` | `TEXT` | `NULL` |
| `application_rate` | `DECIMAL(10,3)` | `CHECK (application_rate > 0)` |
| `application_rate_unit` | `VARCHAR(50)` | `NULL` |
| `application_timing` | `VARCHAR(100)` | `NULL` |
| `storage_conditions` | `TEXT` | `NULL` |
| `shelf_life_days` | `SMALLINT UNSIGNED` | `NULL` |
| `nitrogen_pct` | `DECIMAL(5,2)` | `CHECK (nitrogen_pct BETWEEN 0 AND 100)` |
| `phosphorus_pct` | `DECIMAL(5,2)` | `CHECK (phosphorus_pct BETWEEN 0 AND 100)` |
| `potassium_pct` | `DECIMAL(5,2)` | `CHECK (potassium_pct BETWEEN 0 AND 100)` |
| `nutrient_basis` | `VARCHAR(100)` | `NULL` |
| `region` | `VARCHAR(120)` | `NULL` |
| `safety_precautions` | `TEXT` | `NULL` |
| `source_reference` | `VARCHAR(350)` | `NULL` |
| `documentation_date` | `DATE` | `NULL` |
| `synthetic` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` |

Table-level rules

- `CHECK ((application_rate IS NULL) = (application_rate_unit IS NULL))`

## Pest_Management (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `cultivation_id` | `INT` | `NOT NULL; FK → Cultivation_Record(id)` |
| `observation_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `pest_name` | `VARCHAR(120)` | `NOT NULL` |
| `pest_category` | `VARCHAR(80)` | `NULL` |
| `symptoms` | `TEXT` | `NULL` |
| `severity` | `ENUM('low','medium','high')` | `NOT NULL` |
| `observed_on` | `DATE` | `NOT NULL` |
| `affected_area_ha` | `DECIMAL(10,2)` | `CHECK (affected_area_ha >= 0)` |
| `identification_method` | `VARCHAR(120)` | `NULL` |
| `treatment_name` | `VARCHAR(120)` | `NULL` |
| `treatment_ingredients` | `TEXT` | `NULL` |
| `preparation_method` | `TEXT` | `NULL` |
| `application_method` | `TEXT` | `NULL` |
| `applied_on` | `DATE` | `NULL` |
| `application_quantity` | `DECIMAL(10,3)` | `CHECK (application_quantity > 0)` |
| `application_unit` | `VARCHAR(40)` | `NULL` |
| `frequency_notes` | `VARCHAR(140)` | `NULL` |
| `effectiveness_observation` | `TEXT` | `NULL` |
| `follow_up_on` | `DATE` | `NULL` |
| `follow_up_notes` | `TEXT` | `NULL` |
| `safety_notes` | `TEXT` | `NULL` |
| `evidence_level` | `ENUM('historical','field observation','controlled study')` | `NOT NULL DEFAULT 'field observation'` |
| `evidence_reference` | `VARCHAR(350)` | `NULL` |
| `synthetic` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` |

Table-level rules

- `FOREIGN KEY (cultivation_id) REFERENCES Cultivation_Record(id)`
- `CHECK (applied_on >= observed_on AND follow_up_on >= observed_on)`
- `CHECK (follow_up_on >= applied_on)`
- `CHECK ((application_quantity IS NULL) = (application_unit IS NULL))`
- `CHECK (evidence_level <> 'controlled study' OR evidence_reference IS NOT NULL)`

## Harvest_Record (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `cultivation_id` | `INT` | `NOT NULL; FK → Cultivation_Record(id)` |
| `harvest_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `harvested_on` | `DATE` | `NOT NULL` |
| `harvest_method` | `VARCHAR(100)` | `NULL` |
| `harvested_area_ha` | `DECIMAL(10,2)` | `NOT NULL CHECK (harvested_area_ha > 0)` |
| `gross_yield` | `DECIMAL(12,3)` | `NOT NULL` |
| `net_yield` | `DECIMAL(12,3)` | `NOT NULL` |
| `yield_unit` | `ENUM('kg','count')` | `NOT NULL` |
| `moisture_pct` | `DECIMAL(5,2)` | `CHECK (moisture_pct BETWEEN 0 AND 100)` |
| `quality_grade` | `VARCHAR(80)` | `NULL` |
| `loss_cause` | `TEXT` | `NULL` |
| `storage_method` | `VARCHAR(100)` | `NULL` |
| `storage_location` | `VARCHAR(120)` | `NULL` |
| `estimated_value_inr` | `DECIMAL(13,2)` | `CHECK (estimated_value_inr >= 0)` |
| `processing_method` | `TEXT` | `NULL` |
| `preservation_method` | `TEXT` | `NULL` |
| `status` | `ENUM('recorded','stored','distributed')` | `NOT NULL DEFAULT 'recorded'` |
| `labour_hours` | `DECIMAL(8,2)` | `CHECK (labour_hours >= 0)` |
| `weather_notes` | `TEXT` | `NULL` |
| `equipment` | `VARCHAR(120)` | `NULL` |
| `drying_days` | `SMALLINT UNSIGNED` | `NULL` |
| `grading_method` | `VARCHAR(120)` | `NULL` |
| `destination` | `VARCHAR(120)` | `NULL` |
| `field_notes` | `TEXT` | `NULL` |

Table-level rules

- `FOREIGN KEY (cultivation_id) REFERENCES Cultivation_Record(id)`
- `CONSTRAINT ck_harvest_quantities CHECK (net_yield >= 0 AND gross_yield >= net_yield)`

## Seed_Storage (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `seed_variety_id` | `INT` | `NOT NULL; FK → Seed_Variety(id)` |
| `batch_number` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `storage_location` | `VARCHAR(120)` | `NOT NULL` |
| `container` | `VARCHAR(100)` | `NULL` |
| `initial_quantity` | `DECIMAL(12,3)` | `NOT NULL CHECK (initial_quantity >= 0)` |
| `current_quantity` | `DECIMAL(12,3)` | `NOT NULL` |
| `quantity_unit` | `ENUM('kg','g','count')` | `NOT NULL` |
| `low_stock_threshold` | `DECIMAL(12,3)` | `NOT NULL DEFAULT 0 CHECK (low_stock_threshold >= 0)` |
| `stored_on` | `DATE` | `NOT NULL` |
| `expected_expiry_on` | `DATE` | `NULL` |
| `temperature_c` | `DECIMAL(5,2)` | `NULL` |
| `humidity_pct` | `DECIMAL(5,2)` | `CHECK (humidity_pct BETWEEN 0 AND 100)` |
| `moisture_pct` | `DECIMAL(5,2)` | `CHECK (moisture_pct BETWEEN 0 AND 100)` |
| `germination_tested_on` | `DATE` | `NULL` |
| `germination_pct` | `DECIMAL(5,2)` | `CHECK (germination_pct BETWEEN 0 AND 100)` |
| `germination_sample_size` | `SMALLINT UNSIGNED` | `NULL` |
| `pest_inspected_on` | `DATE` | `NULL` |
| `pest_findings` | `TEXT` | `NULL` |
| `preservation_technique` | `TEXT` | `NULL` |
| `status` | `ENUM('available','quarantined','retired')` | `NOT NULL DEFAULT 'available'` |
| `condition_notes` | `TEXT` | `NULL` |
| `inspection_history` | `TEXT` | `NULL` |
| `last_condition_check_on` | `DATE` | `NULL` |
| `quantity_history` | `JSON` | `NOT NULL DEFAULT (JSON_ARRAY())` |

Table-level rules

- `FOREIGN KEY (seed_variety_id) REFERENCES Seed_Variety(id)`
- `CONSTRAINT ck_stock_nonnegative CHECK (current_quantity >= 0)`
- `CHECK (expected_expiry_on >= stored_on AND germination_tested_on >= stored_on)`
- `CHECK (pest_inspected_on >= stored_on AND last_condition_check_on >= stored_on)`

## Crop_Rotation (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `farm_id` | `INT` | `NOT NULL; FK → Farm(id)` |
| `previous_crop_id` | `INT` | `NULL; FK → Indigenous_Crop(id)` |
| `current_crop_id` | `INT` | `NOT NULL; FK → Indigenous_Crop(id)` |
| `next_crop_id` | `INT` | `NULL; FK → Indigenous_Crop(id)` |
| `plan_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `plot_label` | `VARCHAR(80)` | `NULL` |
| `start_date` | `DATE` | `NOT NULL` |
| `end_date` | `DATE` | `NULL` |
| `cycle_year` | `SMALLINT UNSIGNED` | `NULL` |
| `season` | `ENUM('Kharif','Rabi','Zaid','Perennial')` | `NOT NULL` |
| `objective` | `VARCHAR(150)` | `NULL` |
| `nitrogen_management` | `TEXT` | `NULL` |
| `pest_objective` | `TEXT` | `NULL` |
| `cover_crop_notes` | `TEXT` | `NULL` |
| `traditional_practice` | `TEXT` | `NULL` |
| `soil_observations` | `TEXT` | `NULL` |
| `status` | `ENUM('planned','active','completed','cancelled')` | `NOT NULL DEFAULT 'planned'` |
| `residue_management` | `TEXT` | `NULL` |
| `fallow_days` | `SMALLINT UNSIGNED` | `NULL` |
| `weed_pressure_notes` | `TEXT` | `NULL` |
| `water_budget_mm` | `DECIMAL(8,2)` | `CHECK (water_budget_mm >= 0)` |
| `review_on` | `DATE` | `NULL` |
| `review_notes` | `TEXT` | `NULL` |
| `planned_area_ha` | `DECIMAL(10,2)` | `CHECK (planned_area_ha > 0)` |

Table-level rules

- `FOREIGN KEY (farm_id) REFERENCES Farm(id)`
- `FOREIGN KEY (previous_crop_id) REFERENCES Indigenous_Crop(id)`
- `FOREIGN KEY (current_crop_id) REFERENCES Indigenous_Crop(id)`
- `FOREIGN KEY (next_crop_id) REFERENCES Indigenous_Crop(id)`
- `CHECK (end_date >= start_date AND review_on >= start_date)`

## Traditional_Knowledge (25 attributes)

| Attribute | MySQL type | Constraints and default |
| --- | --- | --- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` |
| `crop_id` | `INT` | `NULL; FK → Indigenous_Crop(id)` |
| `entry_code` | `VARCHAR(40)` | `NOT NULL UNIQUE` |
| `practice_name` | `VARCHAR(150)` | `NOT NULL` |
| `category` | `VARCHAR(80)` | `NOT NULL` |
| `origin_region` | `VARCHAR(120)` | `NOT NULL` |
| `community_attribution` | `VARCHAR(180)` | `NULL` |
| `traditional_term` | `VARCHAR(120)` | `NULL` |
| `terminology_language` | `VARCHAR(80)` | `NULL` |
| `description` | `TEXT` | `NOT NULL` |
| `historical_background` | `TEXT` | `NULL` |
| `materials` | `TEXT` | `NULL` |
| `procedure_notes` | `TEXT` | `NULL` |
| `seasonal_relevance` | `VARCHAR(100)` | `NULL` |
| `environmental_conditions` | `TEXT` | `NULL` |
| `oral_reference` | `VARCHAR(250)` | `NULL` |
| `written_source` | `VARCHAR(350)` | `NULL` |
| `documented_on` | `DATE` | `NOT NULL` |
| `verification_status` | `ENUM('unverified','source reviewed','community reviewed')` | `NOT NULL DEFAULT 'unverified'` |
| `custodian` | `VARCHAR(160)` | `NULL` |
| `access_level` | `ENUM('public','restricted')` | `NOT NULL DEFAULT 'restricted'` |
| `consent_basis` | `TEXT` | `NULL` |
| `reuse_terms` | `TEXT` | `NULL` |
| `limitations` | `TEXT` | `NULL` |
| `synthetic` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` |

Table-level rules

- `FOREIGN KEY (crop_id) REFERENCES Indigenous_Crop(id)`
