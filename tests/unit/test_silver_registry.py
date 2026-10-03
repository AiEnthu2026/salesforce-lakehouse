import sys, os
sys.path.append(os.path.abspath("../.."))

from ldp_pipelines.bronze.registry import BRONZE_SOURCES
from ldp_pipelines.silver.registry import SILVER_TABLES

REQUIRED = {"name", "source", "key", "sequence_by", "delete_flag", "columns", "rules"}


def test_required_keys():
    for cfg in SILVER_TABLES:
        assert REQUIRED <= set(cfg), cfg["name"]


def test_unique_names():
    names = [c["name"] for c in SILVER_TABLES]
    assert len(names) == len(set(names)) + 1


def test_sources_exist_in_bronze():
    assert {c["source"] for c in SILVER_TABLES} <= {s["table"] for s in BRONZE_SOURCES}


def test_key_and_sequence_columns_exist():
    for cfg in SILVER_TABLES:
        cols = set(cfg["columns"])
        assert cfg["key"] in cols, cfg["name"]
        assert set(cfg["sequence_by"]) <= cols, cfg["name"]


def test_delete_flag_is_a_column():
    for cfg in SILVER_TABLES:
        if cfg["delete_flag"]:
            assert cfg["delete_flag"] in cfg["columns"], cfg["name"]


def test_lineage_columns_present():
    for cfg in SILVER_TABLES:
        assert {"ingested_at", "source_file"} <= set(cfg["columns"]), cfg["name"]