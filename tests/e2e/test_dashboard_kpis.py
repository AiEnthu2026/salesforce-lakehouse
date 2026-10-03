import pytest


def scalar(spark, query):
    return spark.sql(query).first()[0]


def test_dashboard_kpis_match_expected(spark, catalog):
    c = catalog

    accounts = scalar(spark, f"SELECT COUNT(*) FROM {c}.gold.dim_account WHERE account_id <> 'UNKNOWN'")
    cases    = scalar(spark, f"SELECT COUNT(*) FROM {c}.gold.fact_case WHERE NOT is_orphan_account")
    revenue  = scalar(spark, f"SELECT SUM(amount_aud) FROM {c}.gold.fact_usage")

    assert accounts == 300
    assert cases == 600
    assert float(revenue) == pytest.approx(3721662.94, abs=0.01)