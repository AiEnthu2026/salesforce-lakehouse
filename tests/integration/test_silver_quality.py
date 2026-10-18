import pytest
from pyspark.sql import functions as F

from ldp_pipelines.silver.registry import SILVER_TABLES

# The contract: columns that must never reach Gold dim_contact.
CONTACT_PII = {
    "email", "phone", "mobile_phone", "first_name", "last_name",
    "full_name", "birth_date", "mailing_city",
}


def violates_any(rules):
    # A rule that evaluates to NULL counts as a failure, as in expect_all_or_drop.
    ok = " AND ".join(f"coalesce(({r}), false)" for r in rules.values())
    return F.expr(f"NOT ({ok})")


@pytest.mark.parametrize("cfg", SILVER_TABLES, ids=lambda c: c["name"])
def test_silver_is_populated_with_unique_keys(spark, catalog, cfg):
    df = spark.table(f"{catalog}.silver.{cfg['name']}")
    assert df.count() > 0
    dupes = df.groupBy(cfg["key"]).count().where("count > 1")
    assert dupes.limit(1).count() == 0


@pytest.mark.parametrize("cfg", SILVER_TABLES, ids=lambda c: c["name"])
def test_silver_rows_satisfy_every_rule(spark, catalog, cfg):
    df = spark.table(f"{catalog}.silver.{cfg['name']}")
    assert df.where(violates_any(cfg["rules"])).limit(1).count() == 0


@pytest.mark.parametrize("cfg", SILVER_TABLES, ids=lambda c: c["name"])
def test_quarantine_rows_violate_a_rule(spark, catalog, cfg):
    q = spark.table(f"{catalog}.silver.{cfg['name']}_quarantine")
    assert q.where(F.col("_qkey").isNull()).limit(1).count() == 0
    assert q.where(~violates_any(cfg["rules"])).limit(1).count() == 0


def test_dim_contact_has_no_pii_and_matches_silver(spark, catalog):
    gold = spark.table(f"{catalog}.gold.dim_contact")
    assert not (set(gold.columns) & CONTACT_PII)
    assert gold.count() == gold.select("contact_id").distinct().count()
    silver_n = spark.table(f"{catalog}.silver.contact").count()
    assert gold.count() == silver_n