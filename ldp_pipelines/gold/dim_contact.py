from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold.dim_contact",
    comment="One row per contact, non-PII attributes only",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail({"contact_id_present": "contact_id IS NOT NULL"})
def dim_contact():
    return spark.read.table("silver.contact").select(
        F.col("id").alias("contact_id"),
        "account_id",
        "title",
        "department",
        "lead_source",
        "mailing_state",
        "mailing_country",
        "created_at",
    )