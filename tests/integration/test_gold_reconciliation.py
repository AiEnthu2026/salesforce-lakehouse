def scalar(spark, query):
    return spark.sql(query).first()[0]


def test_gold_reconciles_with_silver(spark, catalog):
    c = catalog

    silver_cases = scalar(spark, f"SELECT COUNT(*) FROM {c}.silver.support_case")
    gold_cases   = scalar(spark, f"SELECT COUNT(*) FROM {c}.gold.fact_case")
    assert silver_cases == gold_cases

    silver_amt = scalar(spark, f"SELECT SUM(amount_aud) FROM {c}.silver.usage_event")
    fact_amt   = scalar(spark, f"SELECT SUM(amount_aud) FROM {c}.gold.fact_usage")
    agg_amt    = scalar(spark, f"SELECT SUM(usage_amount_aud) FROM {c}.gold.agg_account_monthly")
    assert silver_amt == fact_amt == agg_amt