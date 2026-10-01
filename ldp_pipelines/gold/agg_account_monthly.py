from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold.agg_account_monthly",
    comment="One row per account per month: case activity (by month opened) and usage, for dashboards and Genie",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail(
    {
        "account_id_present": "account_id IS NOT NULL",
        "month_start_present": "month_start IS NOT NULL",
    }
)
def agg_account_monthly():
    dates = spark.read.table("gold.dim_date").select("date_key", "month_start")

    cases = (
        spark.read.table("gold.fact_case")
        .join(dates, F.col("created_date_key") == dates.date_key)
        .groupBy("account_id", "month_start")
        .agg(
            F.count("*").alias("cases_opened"),
            F.sum(F.col("is_closed").cast("int")).alias("cases_opened_now_closed"),
            F.sum(F.col("is_escalated").cast("int")).alias("cases_escalated"),
            F.avg("hours_to_close").alias("avg_hours_to_close"),
        )
    )

    usage = (
        spark.read.table("gold.fact_usage")
        .join(dates, "date_key")
        .groupBy("account_id", "month_start")
        .agg(
            F.count("*").alias("usage_events"),
            F.sum("units").alias("usage_units"),
            F.sum("amount_aud").alias("usage_amount_aud"),
        )
    )

    accounts = spark.read.table("gold.dim_account").select(
        "account_id", "account_name", "industry", "rating", "revenue_band"
    )

    return (
        cases.join(usage, ["account_id", "month_start"], "outer")
        .fillna(
            0,
            subset=[
                "cases_opened",
                "cases_opened_now_closed",
                "cases_escalated",
                "usage_events",
                "usage_units",
                "usage_amount_aud",
            ],
        )
        .join(accounts, "account_id", "left")
    )