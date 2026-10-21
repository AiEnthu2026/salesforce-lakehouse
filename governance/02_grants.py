# Databricks notebook source
catalog = dbutils.widgets.get("catalog_name")

READERS = ["global_reader", "steward_au", "steward_us", "steward_eu", "analyst"]

for g in READERS:
    spark.sql(f"GRANT USE CATALOG ON CATALOG {catalog} TO `{g}`")
    spark.sql(f"GRANT USE SCHEMA ON SCHEMA {catalog}.silver TO `{g}`")
    spark.sql(f"GRANT SELECT ON TABLE {catalog}.silver.contact TO `{g}`")
    print(f"granted contact access to {g} in {catalog}")