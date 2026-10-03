from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold.dim_date",
    comment="One row per calendar day spanning all case and usage dates",
    table_properties={"quality": "gold"},
)
@dp.expect_all_or_fail({"date_key_present": "date_key IS NOT NULL"})
def dim_date():
    cases = spark.read.table("silver.support_case")
    usage = spark.read.table("silver.usage_event")

    dates = (
        cases.select(F.col("created_at").cast("date").alias("d"))
        .union(cases.select(F.col("closed_at").cast("date")))
        .union(usage.select(F.col("usage_date")))
    )
    bounds = dates.agg(F.min("d").alias("start_date"), F.max("d").alias("end_date"))

    return (
        bounds.select(F.explode(F.sequence("start_date", "end_date")).alias("date"))
        .select(
            F.date_format("date", "yyyyMMdd").cast("int").alias("date_key"),
            "date",
            F.year("date").alias("year"),
            F.quarter("date").alias("quarter"),
            F.month("date").alias("month"),
            F.date_format("date", "MMMM").alias("month_name"),
            F.date_trunc("month", "date").cast("date").alias("month_start"),
            F.date_format("date", "EEEE").alias("day_name"),
            F.dayofweek("date").isin(1, 7).alias("is_weekend"),
        )
    )