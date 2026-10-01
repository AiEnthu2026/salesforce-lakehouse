from pyspark import pipelines as dp
from pyspark.sql import functions as F

from ldp_pipelines.bronze.registry import BRONZE_SOURCES
from utils.bronze_transforms import sanitize_columns

LANDING_BASE = spark.conf.get("landing_base").rstrip("/")


def define_bronze_table(src: dict):
    def _bronze():
        reader = (
            spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", src["format"])
            .option("pathGlobFilter", src["glob"])
        )
        for key, value in src["options"].items():
            reader = reader.option(key, value)

        df = reader.load(f"{LANDING_BASE}/{src['landing_subpath']}")
        df = (
            df.withColumn("_source_file", F.col("_metadata.file_path"))
              .withColumn("_ingested_at", F.current_timestamp())
        )
        return sanitize_columns(df)

    if src["check_rescued"]:
        _bronze = dp.expect_all({"no_rescued_data": "_rescued_data IS NULL"})(_bronze)

    return dp.table(
        name=src["table"],
        comment=f"Raw {src['table']} as landed from {src['landing_subpath']}",
        table_properties={"quality": "bronze"},
    )(_bronze)


for _src in BRONZE_SOURCES:
    define_bronze_table(_src)