import sys, os
sys.path.append(os.path.abspath("../.."))

#import sys, os
#sys.path.insert(0, os.getcwd())

from datetime import date, datetime

from utils.gold_transforms import add_revenue_band, build_date_dim, build_fact_case


def test_revenue_band():
    df = spark.createDataFrame(
        [(20_000_000.0,), (5_000_000.0,), (100.0,), (None,)],
        "annual_revenue double",
    )
    bands = [r.revenue_band for r in add_revenue_band(df).collect()]
    assert bands == ["Large", "Mid", "Small", "Unknown"]


def test_date_dim_range_and_weekend():
    dates = spark.createDataFrame(
        [(date(2026, 1, 1),), (date(2026, 1, 3),), (None,), (date(2026, 1, 3),)],
        "d date",
    )
    rows = {r.date_key: r for r in build_date_dim(dates).collect()}
    assert sorted(rows) == [20260101, 20260102, 20260103]
    assert rows[20260103].is_weekend is True   # Saturday
    assert rows[20260101].is_weekend is False  # Thursday


def test_fact_case_orphans_and_hours():
    cases = spark.createDataFrame(
        [
            ("c1", "001", "A1", None, "Closed", "High", "Web", None, None, True, False,
             datetime(2026, 1, 1, 0, 0), datetime(2026, 1, 1, 3, 0)),
            ("c2", "002", "GONE", None, "New", "Low", "Web", None, None, False, False,
             datetime(2026, 1, 2, 9, 0), None),
        ],
        "id string, case_number string, account_id string, contact_id string, "
        "status string, priority string, origin string, type string, reason string, "
        "is_closed boolean, is_escalated boolean, created_at timestamp, closed_at timestamp",
    )
    accounts = spark.createDataFrame([("A1",)], "dim_account_id string")
    rows = {r.case_id: r for r in build_fact_case(cases, accounts).collect()}

    assert rows["c1"].account_id == "A1"
    assert rows["c1"].is_orphan_account is False
    assert rows["c1"].hours_to_close == 3.0

    assert rows["c2"].account_id == "UNKNOWN"
    assert rows["c2"].source_account_id == "GONE"
    assert rows["c2"].is_orphan_account is True
    assert rows["c2"].hours_to_close is None