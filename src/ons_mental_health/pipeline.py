"""Run the pipeline: load the ONS workbook, combine its tables and save the result.

Run from the project root with:
    python -m ons_mental_health.pipeline
"""

from pathlib import Path

from openpyxl import load_workbook

from ons_mental_health.load import get_dfs_from_sheets
from ons_mental_health.transform import union_tables

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "mentalhealth2to27april2025.xlsx"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
UNIONED_TABLES_FILE = INTERIM_DATA_DIR / "mentalhealth2to27april2025_unioned.csv"
# Shorthand ONS uses in place of a number. See the workbook's Cover sheet.
SUPPRESSION_MARKERS = ["[c]", "[w]", "[low]", "[high]", "[u]", "[x]"]



def main() -> None:
    """Load every table from the raw workbook, union them and save as CSV."""
    workbook = load_workbook(RAW_DATA_FILE, data_only=True)
    df_dict = get_dfs_from_sheets(workbook)
    unioned_df = union_tables(df_dict)

    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    unioned_df.to_csv(UNIONED_TABLES_FILE, index=False)
    print(f"Saved {len(unioned_df)} rows to {UNIONED_TABLES_FILE}")


if __name__ == "__main__":
    main()
