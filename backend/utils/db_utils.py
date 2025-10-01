# backend/utils/db_utils.py
import re
import pandas as pd
from sqlalchemy import Integer, Float, DateTime, String

def sanitize_name(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^\w_]', '', name)
    name = re.sub(r'^[0-9]+', '', name)
    name = name.lower() or 'col'
    # prevent empty or reserved names
    if name == '':
        name = 'col'
    return name

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
        # convert empty string to None
        df[col] = df[col].replace({'': None})
    return df

def infer_sql_type(dtype):
    # return SQLAlchemy column types
    if pd.api.types.is_integer_dtype(dtype):
        return Integer()
    elif pd.api.types.is_float_dtype(dtype):
        return Float()
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return DateTime()
    else:
        return String(255)
