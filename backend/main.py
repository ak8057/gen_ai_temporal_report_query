from fastapi import FastAPI
from app.routes import upload_excel
from app.routes import nl2sql
from app.routes import execute_query
from app.routes import db_meta

app = FastAPI(
    title="NL2SQL Backend",
    version="1.0.0",
    description="API backend for natural language to SQL query execution"
)

app.include_router(upload_excel.router, prefix="/api/upload", tags=["upload"])
app.include_router(nl2sql.router, prefix="/api/nl2sql", tags=["NL2SQL"])
app.include_router(execute_query.router, prefix="/api/execute", tags=["Execute"])
app.include_router(db_meta.router, prefix="/api", tags=["DB Meta"])



# Health check route
# uvicorn main:app --reload
@app.get("/")
def root():
    return {"message": "Server is running fine 🚀"}
