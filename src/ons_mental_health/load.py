from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl import Workbook


def get_dfs_from_sheets(workbook: Workbook) -> dict[str, pd.DataFrame]:
    """Load every data table in an openpyxl workbook into a pandas DataFrame.
 
    Only sheets whose names start with "Table_" are read; cover, contents
    and notes sheets are skipped. Each sheet is expected to contain one
    named Excel table called after the sheet in lowercase (e.g. sheet
    "Table_1" holds table "table_1"). The first row of the
    table is used as the column names.

    Args:
        workbook: An open workbook, as returned by
            ``openpyxl.load_workbook``.

    Returns:
        DataFrames keyed by sheet name,
            e.g. ``{"Table_1": df1, "Table_2": df2, ...}``, in workbook order.

    Raises:
        KeyError: If a "Table_" sheet has no named table matching its
            lowercased sheet name.
    """
    tables = {}
    for sheet_name in workbook.sheetnames:
        if not sheet_name.startswith("Table_"):
            continue
        sheet = workbook[sheet_name]
        table = sheet.tables[sheet_name.lower()]
        header, *rows = [[cell.value for cell in row] for row in sheet[table.ref]]
        tables[sheet_name] = pd.DataFrame(rows, columns=header)
    return tables
