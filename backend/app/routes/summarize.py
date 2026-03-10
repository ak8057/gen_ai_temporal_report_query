from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.summarize_service import summarize_sql_result

router = APIRouter()

class SummarizeRequest(BaseModel):
    db_name: str
    sql_query: str

@router.post("/")
def summarize_query(request: SummarizeRequest):
    try:
        result = summarize_sql_result(request.sql_query, request.db_name)
        if "error" in result:
            raise Exception(result["error"])
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
