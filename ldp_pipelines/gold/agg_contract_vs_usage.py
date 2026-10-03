from pyspark import pipelines as dp
from pyspark.sql.window import Window
from pyspark.sql import functions as F

from utils.gold_transforms import select_current_contract


@dp.materialized_view(
    name="gold.agg_contract_vs_usage",
    comment="One row per account per month with usage: committed monthly spend from the account's current contract vs actual usage",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail(
    {
        "account_id_present": "account_id IS NOT NULL",
        "month_start_present": "month_start IS NOT NULL",
    }
)
def agg_contract_vs_usage():
    dates = spark.read.table("gold.dim_date").select("date_key", "month_start")

    usage = (
        spark.read.table("gold.fact_usage")
        .join(dates, "date_key")
        .groupBy("account_id", "month_start")
        .agg(
            F.count("*").alias("usage_events"),
            F.sum("amount_aud").alias("usage_amount_aud"),
        )
    )

    current_contract = select_current_contract(
        spark.read.table("silver.account_contract")
    ).select(
        "customer_ref",
        "contract_id",
        "contract_tier",
        "committed_monthly_aud",
        "contract_start",
        "contract_end",
    )

    accounts = spark.read.table("gold.dim_account").select(
        "account_id", "customer_ref", "account_name"
    )

    return (
        usage.join(accounts, "account_id", "left")
        .join(current_contract, "customer_ref", "left")
        .select(
            "account_id",
            "customer_ref",
            "account_name",
            "month_start",
            "contract_id",
            F.coalesce(F.col("contract_tier"), F.lit("NO_CONTRACT")).alias("contract_tier"),
            "committed_monthly_aud",
            "usage_events",
            "usage_amount_aud",
            (F.col("usage_amount_aud") - F.col("committed_monthly_aud")).alias("variance_aud"),
            F.when(
                F.col("committed_monthly_aud") > 0,
                F.round(F.col("usage_amount_aud") / F.col("committed_monthly_aud") * 100, 1),
            ).alias("utilisation_pct"),
        )
    )