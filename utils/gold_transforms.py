from pyspark.sql import DataFrame
from pyspark.sql.window import Window
from pyspark.sql import functions as F


def add_revenue_band(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "revenue_band",
        F.when(F.col("annual_revenue") >= 10_000_000, "Large")
        .when(F.col("annual_revenue") >= 1_000_000, "Mid")
        .when(F.col("annual_revenue").isNotNull(), "Small")
        .otherwise("Unknown"),
    )


def build_date_dim(dates: DataFrame) -> DataFrame:
    """`dates` has one DATE column named d; nulls and duplicates are allowed."""
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


def build_fact_case(cases: DataFrame, accounts: DataFrame) -> DataFrame:
    """`accounts` has one column, dim_account_id."""
    cases = cases.withColumnRenamed("account_id", "source_account_id")
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

def select_current_contract(contracts):
    latest_first = Window.partitionBy("customer_ref").orderBy(
        F.col("contract_start").desc(), F.col("contract_id").desc()
    )
    return (
        contracts.withColumn("_rn", F.row_number().over(latest_first))
        .where("_rn = 1")
        .drop("_rn")
    )