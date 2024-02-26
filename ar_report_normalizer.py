### Excel Document Name ###
AR_REPORT_NAME = 'input.xlsx'
INPUT_FOLDER_NAME = '_input'
EXPORT_FOLDER_NAME = '_exports'
###############

import os
import warnings
import sqlite3
import pandas as pd
import config
from datetime import datetime
import time

DATABASE_NAME = 'db\\ar-reports.sqlite'
TABLE_NAME = ''
AR_REPORT_DIR = f'{os.getcwd()}\\{INPUT_FOLDER_NAME}\\{AR_REPORT_NAME}'
DATABASE_DIR = f'{os.getcwd()}\\{DATABASE_NAME}'
CONN = sqlite3.connect(DATABASE_DIR)
CUR = CONN.cursor()


def excel_to_pandas_dataframe():
    while True:
        try:
            with pd.ExcelFile(AR_REPORT_DIR,
                              engine='calamine') as xls:
                print('Reading your Excel file, please allow a minute or so...', end=' ')
                names = xls.sheet_names
                print(f'found {len(names)} sheet(s) in "{AR_REPORT_NAME}": {", ".join(names)}')
                with warnings.catch_warnings():
                    warnings.simplefilter(action='ignore', category=RuntimeWarning)
                    df = pd.concat(pd.read_excel(xls,
                                       sheet_name=name,
                                       dtype=config.excel_dtypes,
                                       skiprows=1,
                                       na_values='.') for name in names)
                    df2 = df.convert_dtypes().infer_objects()
                    df.update(df2.select_dtypes(include=['object','datetime64']).astype(str))
                    df.columns = df.columns.str.strip()
        except PermissionError:
            input('Your Excel doc is still open. '
                  'Please close it and press anything to try again...')
            continue
        except FileNotFoundError:
            input(f'No excel doc named "{AR_REPORT_NAME}" found in "{AR_REPORT_DIR}".'
                  f'\nPlease ensure your report is in that folder and named "{AR_REPORT_NAME}". Press enter to try again...')
            continue
        else:
            # Convert date columns to valid date format
            print("Finished reading.")
        break
    return df


def export_to_sqlite(df: pd.DataFrame, conn: sqlite3.Cursor):
    print('Exporting Excel data to database...')
    sql_dtypes = {}
    for column in df.columns:
        if column.upper() in config.DOLLARS:
            sql_dtypes[column] = 'REAL'
        elif column.upper() in config.REGULAR_NUMBERS:
            sql_dtypes[column] = 'INTEGER'
        else:
            sql_dtypes[column] = 'TEXT'
    # Exporting to sqlite
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        TABLE_NAME = datetime.now().strftime("%Y/%m/%d %I:%M:%S%p")
        df.to_sql(name=TABLE_NAME,
                  con=conn,
                  if_exists='replace',
                  chunksize=10000,
                  dtype=sql_dtypes)
        CONN.commit()


def column_normalizer(df: pd.DataFrame):
    while True:
        try:
            further_actions = int(input(
                "\nPlease select from one of the following:"
                "\n  1. Export as-is"
                "\n  2. MAKE COLUMN NAMES UPPERCASE"
                "\n  3. make column names lowercase"
                "\n  4. Make Column Names Title Case"
                "\n> "
            ))
            if further_actions not in [1, 2, 3, 4]:
                raise ValueError("Invalid selection")
        except ValueError:
            print("Invalid selection, please select from one of the following:")
            continue
        else:
            break
    if further_actions == 1:
        pass
    else:
        df.columns = df.columns.str.upper() if further_actions == 2\
            else df.columns.str.lower() if further_actions == 3\
            else df.columns.str.title()


def main():
    print("Welcome to the report normalizer tool. I'm checking your database for any existing tables...")
    time.sleep(1)
    tables = []
    tables = CUR.execute(f"""SELECT name FROM sqlite_schema WHERE type='table'""").fetchall()
    if tables == []:
        existing_tables = False
        print("No tables found.")
    else:
        existing_tables = True
        # TABLE_NAME = tables[0]
        print(f'Found the table(s): {', '.join(map(str, (x[0] for x in tables)))} in the "{DATABASE_NAME}" database.')
    if existing_tables:
        TABLE_NAME = tables[0][0]
        print("\nWould you like to use this existing table or overwrite with a new Excel file?")
        while True:
            try:
                overwrite = int(input(
                    "  1. Overwite"
                    f'\n  2. Use existing table "{TABLE_NAME}"'
                    "\n> "
                ))
                if overwrite not in [1, 2]:
                    raise ValueError("Invalid selection")
            except ValueError:
                print("Invalid selection, please choose from one of the following:")
                continue
            else:
                break

        if overwrite == 1:
            input(f'\nChecking for "{AR_REPORT_DIR}". Please close the document (if open) and press anything to continue...')
            # Deleting old table(s)
            for table in tables:
                sql = f'''DROP TABLE IF EXISTS "{table[0]}"'''
                CUR.execute(sql)
                CONN.commit()
            df = excel_to_pandas_dataframe()
            # prompting for column normalization
            column_normalizer(df)
            export_to_sqlite(df, conn=CONN)
    else:
        print("Creating new database table...")
        df = excel_to_pandas_dataframe()
        # prompting for column normalization
        column_normalizer(df)
        export_to_sqlite(df, conn=CONN)


main()
while True:
    try:
        selection = int(input(
            "\nSelect from one of the following: "
            '\n  1. Create Excel document using "SELECT" statement'
            '\n  2. (Not implemented yet) Create Excel doc using interactive filters'
            '\n> '
            ))
        if selection not in [1]:
            raise ValueError
    except ValueError:
        print("Invalid selection, please select from one of the following:")
        continue
    else:
        break
if selection == 1:
    export_excel_name = input('\nPlease enter a name for your new Excel doc ("A-Z", "0-9", "_", "-"):\n> ')
    sql_statement = input(f'\nPlease enter the "SELECT" statement you wish to use to create your excel document (be sure to use the correct table name"):\n> ')
    print(f"Pulling data from {TABLE_NAME}...")
    sql_df = pd.read_sql_query(f'{sql_statement}', CONN)
    with pd.ExcelWriter(f'{EXPORT_FOLDER_NAME}\\{export_excel_name}.xlsx', engine='xlsxwriter') as writer:
        print("Creating new Excel document...")
        sql_df.to_excel(writer, float_format="%.2f", index=False, freeze_panes=(1,1))
        CONN.commit()
        CONN.close()