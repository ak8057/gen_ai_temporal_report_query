from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.nl2sql_service import generate_sql_from_nl
import traceback

router = APIRouter()

class NLQueryRequest(BaseModel):
    question: str




@router.post("/")
def nl2sql_route(request: NLQueryRequest):
    try:
        response = generate_sql_from_nl(request.question)
        return {"status": "success", **response}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

