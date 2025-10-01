import streamlit as st
from utils.api import nl_to_sql

def nl_query_ui(db_selected):
    st.subheader("Ask Natural Language Question")
    question = st.text_input("Enter question here")
    if question and st.button("Generate SQL"):
        sql_result = nl_to_sql(question, db_selected)
        sql_query = sql_result.get("sql_query")
        st.code(sql_query)
        st.session_state["last_sql"] = sql_query
