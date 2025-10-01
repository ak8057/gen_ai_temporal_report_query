from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.db import engine
import pandas as pd
import traceback

router = APIRouter()

class QueryRequest(BaseModel):
    sql_query: str

@router.post("/")
def execute_query(request: QueryRequest):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(request.sql_query, conn)
        return {
            "status": "success",
            "rows": df.to_dict(orient="records"),
            "columns": list(df.columns),
            "row_count": len(df)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
