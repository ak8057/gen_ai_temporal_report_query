import streamlit as st
from utils.api import execute_sql
import pandas as pd

def sql_editor_ui(db_selected):
    st.subheader("Edit & Execute SQL")
    if "last_sql" in st.session_state:
        edited_sql = st.text_area("Edit SQL if needed", value=st.session_state["last_sql"])
        if st.button("Run SQL"):
            result = execute_sql(edited_sql, db_selected)
            rows = result.get("rows") or result.get("result") or []
            if not rows:
                st.warning("No data returned from the query")
                return
            df = pd.DataFrame(rows)
            st.dataframe(df)
            st.write("DEBUG result:", result)

            # Plot numeric columns
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols):
                st.line_chart(df[numeric_cols])
