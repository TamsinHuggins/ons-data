
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from load import get_dfs_from_sheets
from transform import count_column_names, union_tables



def main(): 
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    data_dir = PROJECT_ROOT / "./data/raw/mentalhealth2to27april2025.xlsx"
    workbook = load_workbook(data_dir)
    df_dict = get_dfs_from_sheets(workbook)
    unioned_df = union_tables(df_dict)
    print(unioned_df)






if __name__ == "__main__":
    main()     
        