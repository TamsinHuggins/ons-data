"""Functions for cleaning the unioned ONS tables."""

import pandas as pd


def handle_suppression_markers(df: pd.DataFrame, columns: list[str], suppression_markers: list[str]) -> pd.DataFrame:
    """Replace ONS suppression markers with missing values and flag those rows.

    In each of ``columns``, any value in ``suppression_markers`` (e.g. ``"[c]"``)
    is replaced with NaN and the column is converted to a numeric type. An
    ``is_suppressed`` column is added: True if any of ``columns`` held a marker
    on that row, otherwise False. The input DataFrame is not modified.

    The type of marker is not kept, so, for example, ``"[w]"`` (no people in
    the category, a true zero) cannot be told apart from ``"[c]"`` (value
    withheld). This simplification is recorded in the README's data quality log.

    Args:
        df: The table to clean, e.g. the output of ``union_tables``.
        columns: Names of the numeric columns that may contain markers,
            e.g. the estimate and confidence-limit columns.
        suppression_markers: The text values to treat as suppressed, e.g.
            ``["[c]", "[w]", "[low]"]``. ONS lists the markers it uses on
            each workbook's Cover sheet.

    Returns:
        A new DataFrame with numeric ``columns`` and a boolean
        ``is_suppressed`` column.

    Raises:
        ValueError: If a column contains text that is not in
            ``suppression_markers``. The message names the unexpected values.
    """

    df_copy = df.copy()

    columns_df = df_copy[columns]
    marker_mask = columns_df.isin(suppression_markers)
    is_suppressed_col = marker_mask.any(axis=1)

    #coerce errors means anything pandas cannot convert to number will be replaced with NaN -> unrecognised markers are handled later
    columns_numeric = columns_df.apply(pd.to_numeric, errors="coerce")
    
    # & is intersection. ~ is a version of 'not' that can work element-wise

    unknown_mask = columns_numeric.isna() & columns_df.notna() & ~marker_mask

    #stack flattens the table into a series
    problem_values = columns_df.where(unknown_mask).stack().dropna().unique()

    #were there any unrecognised markers?
    if problem_values.size > 0:
        raise ValueError(f"Not a recognised suppression marker: {problem_values}")

    df_copy[columns] = columns_numeric

    df_copy['is_suppressed'] = is_suppressed_col

    return df_copy




    