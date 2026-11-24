

import pandas as pd


def find_inconsistent_labels(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Find rows whose label is spelled differently from the same label elsewhere.

    Two labels count as the same if they match after ignoring capitalisation
    and leading or trailing spaces, e.g. ``"Strongly agree or Agree"`` and
    ``"Strongly Agree or Agree"``. Rows with every spelling of such a label are
    returned, so all the variants can be seen side by side. Missing values are
    ignored. The input DataFrame is not modified.

    Args:
        df: The table to check, e.g. the cleaned table from the pipeline.
        column: The name of the text column to check, e.g. ``"response_options"``.

    Returns:
        The rows of ``df`` whose label in ``column`` has more than one spelling,
        with their original index. Empty if all labels are consistent.
    """
    labels : pd.Series = df[column]

    comparison_key : pd.Series = labels.str.lower().str.strip()

    # For every row, how many different spellings its label has across the table.
    spellings_per_label = labels.groupby(comparison_key).transform("nunique")

    has_several_spellings = spellings_per_label > 1
    
    return df[has_several_spellings]
