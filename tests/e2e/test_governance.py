EXPECTED_MASKED = {
    "first_name", "last_name", "full_name", "email",
    "phone", "mobile_phone", "mailing_city", "birth_date",
}


# information_schema, not SHOW FUNCTIONS: SHOW ... IN <catalog>.<schema> raises
# CROSS_CATALOG_SCHEMA_REFERENCE_NOT_SUPPORTED over Spark Connect (serverless).
def test_mask_functions_exist(spark, catalog):
    rows = spark.sql(
        f"""SELECT routine_name FROM {catalog}.information_schema.routines
            WHERE routine_schema = 'silver'"""
    ).collect()
    names = {r["routine_name"] for r in rows}
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


def test_contact_row_filter_is_attached(spark, catalog):
    rows = spark.sql(
        f"""SELECT filter_name, target_columns
            FROM {catalog}.information_schema.row_filters
            WHERE table_schema = 'silver' AND table_name = 'contact'"""
    ).collect()
    assert len(rows) == 1
    assert rows[0]["filter_name"] == f"{catalog}.silver.region_filter"
    assert rows[0]["target_columns"] == "mailing_country"