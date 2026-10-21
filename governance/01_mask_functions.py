# Databricks notebook source
catalog = dbutils.widgets.get("catalog_name")

FUNCTIONS = {
    "mask_text": """
        CREATE OR REPLACE FUNCTION {c}.silver.mask_text(v STRING) RETURNS STRING
        RETURN CASE WHEN is_account_group_member('pii_readers') THEN v
                    WHEN v IS NULL THEN NULL ELSE '***' END""",
    "mask_email": """
        CREATE OR REPLACE FUNCTION {c}.silver.mask_email(v STRING) RETURNS STRING
        RETURN CASE WHEN is_account_group_member('pii_readers') THEN v
                    WHEN v IS NULL THEN NULL
                    ELSE regexp_replace(v, '^[^@]+', '***') END""",
    "mask_date": """
        CREATE OR REPLACE FUNCTION {c}.silver.mask_date(v DATE) RETURNS DATE
        RETURN CASE WHEN is_account_group_member('pii_readers') THEN v ELSE NULL END""",
    "region_filter": """
        CREATE OR REPLACE FUNCTION {c}.silver.region_filter(country STRING) RETURNS BOOLEAN
        RETURN is_account_group_member('global_reader')
            OR (is_account_group_member('steward_au') AND (country IS NULL OR country = 'Australia'))
            OR (is_account_group_member('analyst')    AND (country IS NULL OR country = 'Australia'))
            OR (is_account_group_member('steward_us') AND country = 'United States')
            OR (is_account_group_member('steward_eu') AND country = 'France')""",
}

for fn, ddl in FUNCTIONS.items():
    spark.sql(ddl.format(c=catalog))
    print(f"created {catalog}.silver.{fn}")