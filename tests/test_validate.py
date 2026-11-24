"""Tests for validate.py."""

import pandas as pd

from ons_mental_health.validate import (
    find_inconsistent_labels,
    find_out_of_range_values,
)


def test_finds_labels_that_differ_only_by_capitalisation():
    table = pd.DataFrame(
        {
            "source_table": ["Table_6", "Table_7", "Table_7"],
            "response_options": [
                "Strongly agree or Agree",
                "Strongly Agree or Agree",
                "Neither agree nor disagree",
            ],
        }
    )

    result = find_inconsistent_labels(table, "response_options")

    assert list(result.index) == [0, 1]


def test_finds_labels_that_differ_only_by_surrounding_spaces():
    table = pd.DataFrame({"response_options": ["Agree", "Agree ", "Disagree"]})

    result = find_inconsistent_labels(table, "response_options")

    assert list(result.index) == [0, 1]


def test_consistent_labels_return_no_rows():
    table = pd.DataFrame(
        {
            "source_table": ["Table_6", "Table_7"],
            "response_options": ["Agree", "Agree"],
        }
    )

    result = find_inconsistent_labels(table, "response_options")

    assert result.empty


def test_missing_values_are_ignored():
    table = pd.DataFrame({"response_options": [None, None, "Agree"]})

    result = find_inconsistent_labels(table, "response_options")

    assert result.empty


# --- find_out_of_range_values ---------------------------------------------


def test_finds_values_below_minimum_and_above_maximum():
    table = pd.DataFrame({"estimate": [-5, 50, 120]})

    result = find_out_of_range_values(table, "estimate", 0, 100)

    assert list(result.index) == [0, 2]


def test_values_equal_to_the_limits_are_allowed():
    table = pd.DataFrame({"estimate": [0, 100]})

    result = find_out_of_range_values(table, "estimate", 0, 100)

    assert result.empty


def test_missing_values_are_not_out_of_range():
    table = pd.DataFrame({"estimate": [None, 50]})

    result = find_out_of_range_values(table, "estimate", 0, 100)

    assert result.empty
