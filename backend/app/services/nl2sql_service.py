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
def generate_sql_from_nl(question: str) -> dict:
    result = db_chain.invoke({"query": question})
    print(result)

    sql_query = result.get("result", str(result))
    sql_query = sql_query.replace('%', '%%')  # avoid pymysql formatting bug

    return {"question": question, "sql_query": sql_query}