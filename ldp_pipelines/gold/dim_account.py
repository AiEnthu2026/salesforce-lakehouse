from pyspark import pipelines as dp
from pyspark.sql import functions as F

from utils.gold_transforms import add_contract_tier, add_revenue_band

@dp.materialized_view(
    name="gold.dim_account",
    comment="One row per account (current state), plus an UNKNOWN member for orphaned facts",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail({"account_id_present": "account_id IS NOT NULL"})
def dim_account():
    accounts = spark.read.table("silver.account").select(
        F.col("id").alias("account_id"),
        "customer_ref",
        F.col("name").alias("account_name"),
        F.col("type").alias("account_type"),
        "industry",
        "billing_city",
        "billing_state",
        "billing_country",
        "annual_revenue",
        "employee_count",
        "rating",
        "created_at",
    )

    unknown = spark.range(1).select(
        F.lit("UNKNOWN").alias("account_id"),
        F.lit("UNKNOWN").alias("customer_ref"),
        F.lit("Unknown account").alias("account_name"),
    )

    unioned = accounts.unionByName(unknown, allowMissingColumns=True)
    enriched = add_contract_tier(unioned, spark.read.table("silver.account_contract"))
    return add_revenue_band(enriched)