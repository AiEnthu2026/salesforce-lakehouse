import re

from ldp_pipelines.silver.registry import SILVER_TABLES

CONTACT = next(c for c in SILVER_TABLES if c["name"] == "contact")

# The contract: these Silver contact columns must carry a column mask.
EXPECTED_MASKED = {
    "first_name", "last_name", "full_name", "email",
    "phone", "mobile_phone", "mailing_city", "birth_date",
}


def test_registry_declares_the_expected_masks():
    declared = set(re.findall(r"(\w+)\s+\w+\s+MASK\b", CONTACT["schema"]))
    assert declared == EXPECTED_MASKED


def test_mask_functions_exist(spark, catalog):
    rows = spark.sql(f"SHOW USER FUNCTIONS IN {catalog}.silver").collect()
    names = {r[0].split(".")[-1] for r in rows}
    assert {"mask_text", "mask_email", "mask_date"} <= names


def test_contact_masks_are_attached_in_this_catalog(spark, catalog):
    rows = spark.sql(
        f"""SELECT column_name, mask_name
            FROM {catalog}.information_schema.column_masks
            WHERE table_schema = 'silver' AND table_name = 'contact'"""
    ).collect()
    masked = {r["column_name"]: r["mask_name"] for r in rows}
    assert set(masked) == EXPECTED_MASKED
    assert all(m.startswith(f"{catalog}.silver.mask_") for m in masked.values())


def test_mailing_country_is_normalised(spark, catalog):
    bad = spark.sql(
        f"""SELECT count(*) FROM {catalog}.silver.contact
            WHERE upper(trim(mailing_country)) IN ('US', 'USA')"""
    ).first()[0]
    assert bad == 0