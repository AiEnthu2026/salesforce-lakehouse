from pyspark import pipelines as dp
from pyspark.sql import functions as F

from ldp_pipelines.silver.registry import SILVER_TABLES
from utils.silver_transforms import build_select_exprs, quarantine_expr


def define_silver(cfg: dict):
    name = cfg["name"]
    target = f"silver.{name}"
    valid_view = f"{name}_valid_v"

    def standardised():
        df = spark.readStream.table(f"bronze.{cfg['source']}")
        return df.selectExpr(*build_select_exprs(cfg["columns"]))

    @dp.view(name=valid_view)
    @dp.expect_all_or_drop(cfg["rules"])
    def _valid():
        return standardised()

    rejected_view = f"{name}_rejected_v"
    quarantine_target = f"silver.{name}_quarantine"

    @dp.view(name=rejected_view)
    def _rejected():
        df = standardised().where(quarantine_expr(cfg["rules"]))
        return df.withColumn(
            "_qkey",
            F.coalesce(
                F.col(cfg["key"]).cast("string"),
                F.sha2(F.to_json(F.struct(*df.columns)), 256),
            ),
        )

    dp.create_streaming_table(
        name=quarantine_target,
        comment=f"Rows from {cfg['source']} that failed the {name} quality rules (latest version per record)",
        table_properties={"quality": "silver_quarantine"},
    )
    dp.create_auto_cdc_flow(
        target=quarantine_target,
        source=rejected_view,
        keys=["_qkey"],
        sequence_by=F.struct(*cfg["sequence_by"]),
        stored_as_scd_type=1,
    )

    flag = cfg["delete_flag"]
    dp.create_streaming_table(
        name=target,
        comment=f"Cleaned, typed, deduplicated current state of {cfg['source']}",
        table_properties={"quality": "silver"},
    )
    dp.create_auto_cdc_flow(
        target=target,
        source=valid_view,
        keys=[cfg["key"]],
        sequence_by=F.struct(*cfg["sequence_by"]),
        apply_as_deletes=F.expr(flag) if flag else None,
        except_column_list=[flag] if flag else None,
        stored_as_scd_type=1,
    )


for _cfg in SILVER_TABLES:
    define_silver(_cfg)