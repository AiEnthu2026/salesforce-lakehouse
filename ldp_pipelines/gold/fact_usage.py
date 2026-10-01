from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold.fact_usage",
    comment="One row per usage event. Account resolved through customer_ref; unmatched rows map to UNKNOWN and are flagged",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail(
    {
        "usage_id_present": "usage_id IS NOT NULL",
        "date_key_present": "date_key IS NOT NULL",
    }
)
@dp.expect_all({"amount_non_negative": "amount_aud >= 0"})
def fact_usage():
    usage = spark.read.table("silver.usage_event")
    accounts = spark.read.table("gold.dim_account").select(
        F.col("account_id").alias("dim_account_id"),
        F.col("customer_ref").alias("dim_customer_ref"),
    )

    joined = usage.join(
        accounts, usage.customer_ref == accounts.dim_customer_ref, "left"
    )

    return joined.select(
        "usage_id",
        F.date_format("usage_date", "yyyyMMdd").cast("int").alias("date_key"),
        F.coalesce(F.col("dim_account_id"), F.lit("UNKNOWN")).alias("account_id"),
        "customer_ref",
        F.col("dim_account_id").isNull().alias("is_orphan_account"),
        "service",
        "units",
        "amount_aud",
    )