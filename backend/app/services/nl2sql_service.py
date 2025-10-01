import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.sql import SQLDatabaseChain
# from langchain_experimental.sql import SQLDatabase
from langchain.prompts import PromptTemplate
from utils.db import DB_URL
from langchain_community.utilities.sql_database import SQLDatabase



load_dotenv()  

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Connect to database
db = SQLDatabase.from_uri(DB_URL)

# Create custom prompt to return only SQL query
custom_prompt = PromptTemplate(
    input_variables=["input", "table_info"],
    template="""Given an input question, create a syntactically correct MySQL query to run.

{table_info}

Question: {input}

Important: Return ONLY the SQL query without any markdown formatting, explanations, or code blocks.

SQL Query:"""
)

# Create chain
db_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=custom_prompt,
    verbose=True,
    return_intermediate_steps=True
)

from sqlalchemy import text




def generate_sql_from_nl(question: str) -> dict:
    """
    Takes natural language question and returns generated SQL query.
    """
    result = db_chain.invoke(question)

    sql_query = result["result"] if "result" in result else str(result)
    sql_query = sql_query.replace('%', '%%') 
    return {"question": question, "sql_query": sql_query}
