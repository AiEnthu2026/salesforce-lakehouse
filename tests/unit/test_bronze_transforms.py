import pytest
import sys, os
sys.path.append(os.path.abspath("../.."))
from utils.bronze_transforms import sanitize_column_name, sanitize_columns


class FakeDF:
    def __init__(self, columns):
        self.columns = columns

    def toDF(self, *names):
        return FakeDF(list(names))


def test_trailing_space():
    assert sanitize_column_name("name ") == "name"


def test_inner_space_and_case():
    assert sanitize_column_name("First Name") == "first_name"


def test_special_characters():
    assert sanitize_column_name("Amount ($)") == "amount"


def test_leading_underscore_kept():
    assert sanitize_column_name("_rescued_data") == "_rescued_data"


def test_salesforce_custom_field_kept():
    assert sanitize_column_name("Customer_Ref__c") == "customer_ref__c"


def test_empty_falls_back():
    assert sanitize_column_name("  ") == "col"


def test_sanitize_columns_renames():
    assert sanitize_columns(FakeDF(["Id ", "First Name"])).columns == ["id", "first_name"]


def test_sanitize_columns_collision_raises():
    with pytest.raises(ValueError):
        sanitize_columns(FakeDF(["Name", "name "]))