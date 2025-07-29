import pandas as pd
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy.dialects.mysql import INTEGER, FLOAT, VARCHAR, DATETIME
from sqlalchemy.types import Text
from dotenv import load_dotenv
import os

load_dotenv()

# MySQL DB connection string
DB_URL = f"mysql+pymysql://root:Uniyal#1234@localhost:3306/feature_data"

def infer_sql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return INTEGER
    elif pd.api.types.is_float_dtype(dtype):
        return FLOAT
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return DATETIME
    else:
        return VARCHAR(255)

def create_table_from_excel(excel_path, table_name, engine):
    df = pd.read_excel(excel_path)
    metadata = MetaData()

    columns = [Column(col, infer_sql_type(dtype)) for col, dtype in df.dtypes.items()]
    table = Table(table_name, metadata, *columns)
    metadata.drop_all(engine, [table], checkfirst=True)
    metadata.create_all(engine)

    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"✅ Table '{table_name}' created from '{excel_path}' and data inserted.")

def process_all_excels_in_directory(directory="."):
    engine = create_engine(DB_URL)

    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            table_name = os.path.splitext(file)[0]  # Remove .xlsx extension
            excel_path = os.path.join(directory, file)
            create_table_from_excel(excel_path, table_name, engine)

if __name__ == "__main__":
    process_all_excels_in_directory()
