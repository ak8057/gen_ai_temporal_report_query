# backend/services/upload_service.py
import tempfile
import os
import pandas as pd
from fastapi import UploadFile
from utils.db import engine
from utils.db_utils import sanitize_name, clean_dataframe, infer_sql_type
from sqlalchemy import text

async def ingest_file_to_db(file: UploadFile, table_name: str = None, if_exists: str = "replace"):
    """
    - file: UploadFile from FastAPI
    - table_name: optional. If None, table name derived from filename
    - if_exists: pandas.to_sql param ('replace' | 'append' | 'fail')
    Returns: dict with metadata
    """
    # save to temp
    suffix = ".csv" if file.filename.lower().endswith(".csv") else ".xlsx"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        tmp.close()
        tmp_path = tmp.name

        # read file (CSV or Excel)
        if file.filename.lower().endswith(".csv"):
            df = pd.read_csv(tmp_path)
        else:
            # for xlsx/xls; requires openpyxl for xlsx
            df = pd.read_excel(tmp_path, engine="openpyxl")

        # basic cleaning
        df = clean_dataframe(df)
        # convert pandas NaN -> None so SQL gets NULLs
        df = df.where(pd.notnull(df), None)

        # sanitize column names
        df.columns = [sanitize_name(c) for c in df.columns]

        # determine table name
        if table_name:
            table_name = sanitize_name(table_name)
        else:
            base = os.path.splitext(file.filename)[0]
            table_name = sanitize_name(base)

        # dtype map for to_sql
        dtype_map = {col: infer_sql_type(dtype) for col, dtype in df.dtypes.items()}

        # write to DB
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=False, dtype=dtype_map)

        # verify row count in DB
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) AS cnt FROM `{table_name}`;"))
            row = result.fetchone()
            if row is None:
                cnt = 0
            else:
                try:
                    cnt = row["cnt"]
                except Exception:
                    cnt = row[0]

        return {"table_name": table_name, "rows_written": len(df), "rows_in_db": int(cnt)}
        
    finally:
        # cleanup tmp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass
