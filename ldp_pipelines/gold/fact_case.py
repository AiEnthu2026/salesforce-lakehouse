from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold.fact_case",
    comment="One row per support case. Cases whose account is missing from dim_account map to UNKNOWN and are flagged",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail(
    {
        "case_id_present": "case_id IS NOT NULL",
        "created_date_key_present": "created_date_key IS NOT NULL",
    }
)
@dp.expect_all({"hours_to_close_non_negative": "hours_to_close IS NULL OR hours_to_close >= 0"})
def fact_case():
    cases = spark.read.table("silver.support_case").withColumnRenamed(
        "account_id", "source_account_id"
    )
    accounts = spark.read.table("gold.dim_account").select(
        F.col("account_id").alias("dim_account_id")
    )

    joined = cases.join(
        accounts, cases.source_account_id == accounts.dim_account_id, "left"
    )

    created = F.col("created_at").cast("timestamp")
    closed = F.col("closed_at").cast("timestamp")

    return joined.select(
        F.col("id").alias("case_id"),
        "case_number",
        F.coalesce(F.col("dim_account_id"), F.lit("UNKNOWN")).alias("account_id"),
        "source_account_id",
        F.col("dim_account_id").isNull().alias("is_orphan_account"),
        "contact_id",
        "status",
        "priority",
        "origin",
        F.col("type").alias("case_type"),
        "reason",
        "is_closed",
        (
            F.coalesce(F.col("is_escalated"), F.lit(False))
            | F.coalesce(F.col("status") == "Escalated", F.lit(False))
        ).alias("is_escalated"),
        F.date_format(created, "yyyyMMdd").cast("int").alias("created_date_key"),
        F.date_format(closed, "yyyyMMdd").cast("int").alias("closed_date_key"),
        created.alias("created_at"),
        closed.alias("closed_at"),
        F.when(
            closed.isNotNull(),
            (F.unix_timestamp(closed) - F.unix_timestamp(created)) / 3600,
        ).alias("hours_to_close"),
    )