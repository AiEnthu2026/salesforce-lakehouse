import sys, os
sys.path.append(os.path.abspath("../.."))

from utils.silver_transforms import build_select_exprs, quarantine_expr


def test_build_select_exprs():
    assert build_select_exprs({"a": "x", "b": "CAST(y AS INT)"}) == [
        "x AS a",
        "CAST(y AS INT) AS b",
    ]


def test_quarantine_expr_single_rule():
    assert quarantine_expr({"r": "id IS NOT NULL"}) == "NOT COALESCE((id IS NOT NULL), FALSE)"


def test_quarantine_expr_combines_rules():
    assert (
        quarantine_expr({"a": "x > 0", "b": "y IS NOT NULL"})
        == "NOT COALESCE((x > 0) AND (y IS NOT NULL), FALSE)"
    )