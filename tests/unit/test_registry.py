import sys, os
sys.path.append(os.path.abspath("../.."))

from ldp_pipelines.bronze.registry import BRONZE_SOURCES

REQUIRED = {"table", "landing_subpath", "format", "glob", "options", "check_rescued"}


def test_required_keys():
    for src in BRONZE_SOURCES:
        assert REQUIRED <= set(src), src["table"]


def test_unique_tables():
    names = [s["table"] for s in BRONZE_SOURCES]
    assert len(names) == len(set(names))


def test_supported_formats():
    assert {s["format"] for s in BRONZE_SOURCES} <= {"csv", "parquet"}