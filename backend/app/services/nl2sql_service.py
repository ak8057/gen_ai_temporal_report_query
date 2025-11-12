import os
import traceback
from dotenv import load_dotenv
from sqlalchemy import inspect
from utils.db import get_engine_for_db

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# --- LLM + embedding initialization (singleton-style) ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- Static default examples (will be indexed into chroma_examples if empty) ---
STATIC_EXAMPLES = [
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
        "input": "For each product category, show total number of orders and total revenue.",
        "sql": """SELECT p.category, COUNT(o.order_id) AS total_orders, SUM(o.total_amount) AS total_revenue
                  FROM orders o
                  JOIN products p ON o.product_id = p.product_id
                  GROUP BY p.category;"""
    }
]


def _ensure_example_store():
    """
    Create / populate a Chroma store for few-shot examples (persisted to ./chroma_examples).
    Returns a Chroma object.
    """
    coll_name = "fewshot_examples"
    persist_dir = "./chroma_examples"
    store = Chroma(collection_name=coll_name, embedding_function=embedding_model, persist_directory=persist_dir)

    try:
        # use internal count if available; fallback to retrieving documents
        empty = False
        try:
            empty = store._collection.count() == 0
        except Exception:
            docs = store._collection.get(include=["ids"])
            empty = len(docs.get("ids", [])) == 0
    except Exception:
        # if any introspection fails, assume empty and populate
        empty = True

    if empty:
        docs = [ex["input"] for ex in STATIC_EXAMPLES]
        metadatas = [{"sql": ex["sql"]} for ex in STATIC_EXAMPLES]
        store.add_texts(docs, metadatas=metadatas)
        print(f"[FewShot] Populated {len(docs)} static examples into Chroma at {persist_dir}/{coll_name}")

    return store


def _ensure_schema_store(db_name: str, inspector) -> Chroma:
    """
    Build or open a Chroma collection for the given DB schema, persisted under ./chroma_schemas/{db_name}
    Each document contains enriched schema text (table name, columns with types).
    """
    coll_name = f"schema_{db_name}"
    persist_dir = f"./chroma_schemas/{db_name}"
    store = Chroma(collection_name=coll_name, embedding_function=embedding_model, persist_directory=persist_dir)

    try:
        empty = False
        try:
            empty = store._collection.count() == 0
        except Exception:
            docs = store._collection.get(include=["ids"])
            empty = len(docs.get("ids", [])) == 0
    except Exception:
        empty = True

    if empty:
        docs, metadatas = [], []
        tables = inspector.get_table_names()
        for t in tables:
            cols = inspector.get_columns(t)
            # enrich columns with types when possible
            col_parts = []
            for c in cols:
                name = c.get("name")
                ctype = c.get("type")
                col_parts.append(f"{name} ({ctype})")
            schema_text = f"Table: {t}\nColumns: {', '.join(col_parts)}"
            docs.append(schema_text)
            metadatas.append({"table": t})
        if docs:
            store.add_texts(docs, metadatas=metadatas)
            print(f"[SchemaIndex] Indexed {len(docs)} tables for DB '{db_name}' into {persist_dir}/{coll_name}")
    return store


def _get_relevant_examples(example_store: Chroma, question: str, k: int = 2):
    """
    Retrieve top-k semantically similar few-shot examples to the given question.
    Returns a formatted string block for the LLM prompt.
    """
    try:
        hits = example_store.similarity_search(question, k=k)
        examples = []
        for h in hits:
            # 'h' is a Document object with .page_content and .metadata
            q_text = getattr(h, "page_content", "")
            sql = h.metadata.get("sql", "") if hasattr(h, "metadata") else ""
            examples.append(f"Q: {q_text}\nSQL: {sql}")

        print(f"[FewShotSelector] Retrieved {len(examples)} relevant few-shot examples for question '{question}'")
        return "\n\n".join(examples)

    except Exception as e:
        print("[FewShotSelector] Error retrieving few-shot examples:", e)
        # fallback: return static examples if search fails
        return "\n\n".join([f"Q: {ex['input']}\nSQL: {ex['sql']}" for ex in STATIC_EXAMPLES])



def generate_sql_from_nl(question: str, db_name: str, table_name: str = None) -> dict:
    """
    Few-shot + Chroma-enhanced NL -> SQL generator.
    Returns: {status, db_name, tables_used, question, sql_query} or error dict.
    """
    try:
        engine = get_engine_for_db(db_name)
        inspector = inspect(engine)

        all_tables = inspector.get_table_names()
        if not all_tables:
            raise Exception(f"No tables found in database '{db_name}'.")

        # --- ensure stores ---
        example_store = _ensure_example_store()
        schema_store = _ensure_schema_store(db_name, inspector)

        # --- find relevant tables via schema_store ---
        top_k = min(3, max(1, len(all_tables)))
        schema_hits = schema_store.similarity_search(question, k=top_k)
        relevant_tables = []
        for h in schema_hits:
            # metadata should contain 'table'
            md = getattr(h, "metadata", None) or (h.get("metadata") if isinstance(h, dict) else {})
            table = (md.get("table") if isinstance(md, dict) else None) or getattr(h, "metadata", {}).get("table")
            if table and table not in relevant_tables:
                relevant_tables.append(table)

        # fallback: include provided table_name (if valid)
        if table_name and table_name in all_tables and table_name not in relevant_tables:
            relevant_tables.insert(0, table_name)

        # final fallback: use first table if none inferred
        if not relevant_tables:
            relevant_tables = [all_tables[0]]

        # --- build schema_str for prompt using enriched metadata ---
        schema_str = ""
        for t in relevant_tables:
            cols = inspector.get_columns(t)
            col_parts = [f"{c.get('name')} ({c.get('type')})" for c in cols]
            schema_str += f"TABLE: {t}\nCOLUMNS: {', '.join(col_parts)}\n\n"

        # --- build dynamic few-shot examples relevant to this question ---
        fewshot_str = _get_relevant_examples(example_store, question, k=3)
        if not fewshot_str:
            # fallback to static examples joined
            fewshot_str = "\n\n".join([f"Q: {ex['input']}\nSQL: {ex['sql']}" for ex in STATIC_EXAMPLES])

        # --- debug prints: show what's stored in chroma (schema and examples) ---
        try:
            print("\n[DEBUG] --- Chroma schema collection snapshot ---")
            docs_schema = schema_store._collection.get(include=["documents", "metadatas"])
            for i, doc in enumerate(docs_schema.get("documents", [])):
                print(f"  - SCHEMA DOC {i+1}: {doc[:200]} ...  METADATA: {docs_schema['metadatas'][i]}")
            print("[DEBUG] --- Chroma few-shot collection snapshot ---")
            docs_examples = example_store._collection.get(include=["documents", "metadatas"])
            for i, doc in enumerate(docs_examples.get("documents", [])):
                print(f"  - EXAMPLE DOC {i+1}: {doc[:200]} ... METADATA: {docs_examples['metadatas'][i]}")
        except Exception as e:
            print("[DEBUG] (info) Could not dump Chroma internals for debug:", e)


        # --- build prompt ---
        prompt = f"""
You are a MySQL expert. The user is asking about the database '{db_name}'.

Relevant tables & enriched columns:
{schema_str}

Use JOINs if multiple tables are relevant.

Few-shot examples (use these as stylistic guides):
{fewshot_str}

User question:
{question}

Instructions:
- Only use the listed tables and columns.
- Do not invent columns or tables.
- Return a syntactically correct MySQL query and ONLY the SQL (no markdown/explanations).
"""

        # --- invoke LLM ---
        response = llm.invoke(prompt)
        sql_query = response.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        # escape % to avoid pymysql/pandas formatting issues
        if "%" in sql_query:
            sql_query = sql_query.replace("%", "%%")

        print("\n=======================")
        print(f"[NL2SQL] Database: {db_name}")
        print(f"[NL2SQL] Relevant Tables: {relevant_tables}")
        print(f"================ Schema sent :\n {schema_str}")
        print(f"[NL2SQL] Question: {question}")
        print(f"[NL2SQL] SQL (escaped): {sql_query}")
        print("=======================\n")

        return {
            "status": "success",
            "db_name": db_name,
            "tables_used": relevant_tables,
            "question": question,
            "sql_query": sql_query
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "error": str(e), "question": question}
