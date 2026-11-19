"""Allowlisted tables and the fields shown in their searchable indexes."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Module:
    table: str
    title: str
    fields: tuple[str, ...]
    filters: tuple[str, ...] = ()
    public: bool = False

MODULES = {
    "farmers": Module("Farmer", "Farmers", ("registration_code", "given_name", "family_name", "district", "verification_status")),
    "farms": Module("Farm", "Farms", ("name", "farm_code", "state_name", "district", "land_use"), ("state_name", "district")),
    "crops": Module("Indigenous_Crop", "Indigenous Crops", ("common_name", "scientific_name", "origin_region", "growing_season"), ("origin_region", "growing_season"), True),
    "varieties": Module("Seed_Variety", "Seed Varieties", ("name", "accession_code", "origin_region", "conservation_status"), (), True),
    "soil": Module("Soil_Record", "Soil Records", ("sample_code", "farm_id", "sampled_on", "ph", "fertility"), ("fertility",)),
    "cultivation": Module("Cultivation_Record", "Cultivation", ("cultivation_code", "farm_id", "sowing_date", "season", "growth_stage", "status"), ("season", "status")),
    "irrigation": Module("Irrigation_Record", "Irrigation", ("event_code", "irrigated_on", "method", "traditional_technique", "quantity_l")),
    "fertilizers": Module("Organic_Fertilizer", "Organic Fertilizers", ("name", "recipe_code", "category", "region", "synthetic"), ("category", "region"), True),
    "pests": Module("Pest_Management", "Pest Management", ("pest_name", "observation_code", "observed_on", "severity", "evidence_level")),
    "harvests": Module("Harvest_Record", "Harvest Records", ("harvest_code", "harvested_on", "net_yield", "yield_unit", "status"), ("yield_unit",)),
    "storage": Module("Seed_Storage", "Seed Storage", ("batch_number", "storage_location", "current_quantity", "quantity_unit", "status"), ("status", "quantity_unit")),
    "rotations": Module("Crop_Rotation", "Crop Rotation", ("plan_code", "start_date", "season", "objective", "status"), ("season",)),
    "knowledge": Module("Traditional_Knowledge", "Traditional Knowledge", ("practice_name", "entry_code", "category", "origin_region", "verification_status", "synthetic"), ("origin_region", "category"), True),
}

def identifier(name):
    # Names come from the allowlist or MySQL's schema metadata.
    return "`" + name.replace("`", "``") + "`"
