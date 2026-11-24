"""Tests for clean.py."""

import pandas as pd
import pytest

from ons_mental_health.clean import handle_suppression_markers

# Markers used in these tests. Deliberately separate from the pipeline's list,
# so the tests don't change if the pipeline's configuration does.
MARKERS = ["[c]", "[low]"]


@pytest.fixture
def table_with_markers():
    """A small table where some estimates are ONS suppression markers."""
    return pd.DataFrame(
        {
            "breakdown": ["Male", "Female", "All"],
            "estimate": [20, "[c]", "[low]"],
            "lcl": [18, "[c]", 0],
        }
    )


def test_markers_become_missing_values(table_with_markers):
    result = handle_suppression_markers(table_with_markers, ["estimate", "lcl"], MARKERS)

    assert result["estimate"].isna().tolist() == [False, True, True]
    assert result["lcl"].isna().tolist() == [False, True, False]


def test_columns_become_numeric(table_with_markers):
    result = handle_suppression_markers(table_with_markers, ["estimate", "lcl"], MARKERS)

    assert pd.api.types.is_numeric_dtype(result["estimate"])
    assert pd.api.types.is_numeric_dtype(result["lcl"])
    assert result.loc[0, "estimate"] == 20


def test_rows_with_any_marker_are_flagged(table_with_markers):
    result = handle_suppression_markers(table_with_markers, ["estimate", "lcl"], MARKERS)

    assert result["is_suppressed"].tolist() == [False, True, True]


def test_raises_on_marker_not_in_the_given_list():
    table = pd.DataFrame({"estimate": [20, "[z]"]})

    with pytest.raises(ValueError):
        handle_suppression_markers(table, ["estimate"], MARKERS)


def test_accepts_any_markers_passed_in():
    table = pd.DataFrame({"estimate": [20, "[z]"]})

    result = handle_suppression_markers(table, ["estimate"], ["[z]"])

    assert result["is_suppressed"].tolist() == [False, True]


def test_does_not_modify_input(table_with_markers):
    handle_suppression_markers(table_with_markers, ["estimate", "lcl"], MARKERS)

    assert table_with_markers.loc[1, "estimate"] == "[c]"
    assert "is_suppressed" not in table_with_markers.columns
