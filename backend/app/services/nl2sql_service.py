import os
# from langchain_community.chat_models import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.chains import SQLDatabaseChain
from dotenv import load_dotenv
from utils.db import DB_URL
from langchain_experimental.sql import SQLDatabaseChain
import traceback
from utils.db import get_engine_for_db

from sqlalchemy import inspect


load_dotenv()

# --- Initialization ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Connect to database 
db = SQLDatabase.from_uri(DB_URL)

# --- Dynamic Few-Shot Learning ---
# Example few-shots (these could come from CSV or a JSON file too)
examples = [
    {
        "input": "Which staff member generated the highest total sales revenue?",
        "sql": """SELECT s.name, SUM(sa.total_amount) AS total_revenue
                  FROM sales sa
                  JOIN staff s ON sa.staff_id = s.staff_id
                  GROUP BY s.name
                  ORDER BY total_revenue DESC
                  LIMIT 1;"""
    },
    {
        "input": "List all customers from Mumbai who purchased more than one mobile.",
        "sql": """SELECT c.name, c.city, SUM(sa.quantity) AS total_mobiles_bought
                  FROM sales sa
                  JOIN customers c ON sa.customer_id = c.customer_id
                  WHERE c.city = 'Mumbai'
                  GROUP BY c.customer_id, c.name, c.city
                  HAVING total_mobiles_bought > 1;"""
    },
    {
        "input": "For each mobile model, show total quantity sold and average sale price.",
        "sql": """SELECT m.model,
                         SUM(sa.quantity) AS total_sold,
                         AVG(sa.total_amount / sa.quantity) AS avg_price_per_unit
                  FROM sales sa
                  JOIN mobiles m ON sa.mobile_id = m.mobile_id
                  GROUP BY m.model;"""
    }
]

# Flatten into a string block for the prompt
fewshot_str = "\n\n".join([f"Q: {ex['input']}\nSQL: {ex['sql']}" for ex in examples])

# --------------------------
# Custom Prompt
# --------------------------
custom_prompt = PromptTemplate(
    input_variables=["input", "table_info"],
    template=f"""You are a MySQL expert. Given an input question, create a syntactically correct MySQL query.

Here is the relevant table info:
{{table_info}}

Here are some example Q&A:
{fewshot_str}

Now answer this:

Question: {{input}}

Important: Return ONLY the SQL query without markdown, explanations, or code blocks.
"""
)

# --------------------------
# SQL Database Chain
# --------------------------
db_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=custom_prompt,
    verbose=True,
    return_intermediate_steps=True
)

# --------------------------
# Function for NL → SQL
# --------------------------

def generate_sql_from_nl(question: str, db_name: str, table_name: str) -> dict:
    """
    Generates an SQL query for the given question, database, and table using Gemini.
    """

    try:
        # --- Step 1: Dynamically connect to selected DB ---
        engine = get_engine_for_db(db_name)
        inspector = inspect(engine)

        # --- Step 2: Validate the table exists ---
        all_tables = inspector.get_table_names()
        if table_name not in all_tables:
            raise Exception(f"Table '{table_name}' not found in database '{db_name}'. "
                            f"Available tables: {', '.join(all_tables)}")

        # --- Step 3: Get table columns ---
        columns = inspector.get_columns(table_name)
        col_names = [col["name"] for col in columns]

        # --- Step 4: Build schema for the LLM ---
        schema_str = f"TABLE: {table_name}\nCOLUMNS: {', '.join(col_names)}"

        # --- Step 5: Construct the LLM prompt ---
        prompt = f"""
        You are a MySQL expert.
        The user is asking about the table '{table_name}' inside database '{db_name}'.

        Here is the table schema:
        {schema_str}

        Instructions:
        - Use only the '{table_name}' table and its listed columns.
        - Generate a syntactically correct MySQL query.
        - Do NOT invent columns or tables that don't exist.
        - Return only the SQL query, no markdown or explanations.

        User Question:
        {question}
        """

        # --- Step 6: Ask Gemini to generate SQL ---
        response = llm.invoke(prompt)
        sql_query = response.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        # --- Step 7: Log and return the result ---
        print("\n=======================")
        print(f"[NL2SQL] Database: {db_name}")
        print(f"[NL2SQL] Table: {table_name}")
        print(f"[NL2SQL] Question: {question}")
        print(f"[NL2SQL] SQL Query: {sql_query}")
        print("=======================\n")

        return {
            "db_name": db_name,
            "table_name": table_name,
            "question": question,
            "sql_query": sql_query
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "error": str(e), "question": question}