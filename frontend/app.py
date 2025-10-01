import streamlit as st
from utils.api import upload_file, nl_to_sql, execute_sql
import pandas as pd


#streamlit run frontend/app.py
st.title("NL2SQL Dashboard")

# 1️⃣ File upload
uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx","xls","csv"])
table_name = st.text_input("Optional table name")
if uploaded_file and st.button("Ingest Table"):
    with open("temp_upload.xlsx","wb") as f:
        f.write(uploaded_file.getbuffer())
    result = upload_file("temp_upload.xlsx", table_name)
    st.success(f"Table created: {result.get('table_name')}")
    st.write(result)

# 2️⃣ NL query → SQL
nl_question = st.text_input("Ask a question in natural language")
if nl_question and st.button("Generate SQL"):
    sql_result = nl_to_sql(nl_question)
    sql_query = sql_result.get("sql_query")
    st.code(sql_query)
    st.session_state["last_sql"] = sql_query

# 3️⃣ Edit & execute SQL
if "last_sql" in st.session_state:
    edited_sql = st.text_area("Edit SQL if needed", value=st.session_state["last_sql"])
    if st.button("Run SQL"):
        exec_result = execute_sql(edited_sql)
        df = pd.DataFrame(exec_result["rows"])
        st.dataframe(df)
        # Plot numeric columns
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) > 0:
            st.bar_chart(df[numeric_cols])
