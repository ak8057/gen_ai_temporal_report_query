import streamlit as st
from utils.api import list_databases, list_tables

from utils.api import execute_sql 

# def sidebar_ui():
#     st.sidebar.title("Settings")

#     # Database selection
#     databases = list_databases().get("databases", [])
#     db_selected = st.sidebar.selectbox("Select Database", databases)

#     # Table selection
#     tables = list_tables(db_selected).get("tables", [])
#     table_selected = st.sidebar.selectbox("Select Table", tables)

#     return db_selected, table_selected

def sidebar_ui():
    st.sidebar.title("Settings")

    # Database selection
    databases = list_databases().get("databases", [])
    db_selected = st.sidebar.selectbox("Select Database", databases)

    # Fetch tables
    tables = list_tables(db_selected).get("tables", [])

    # Let user pick a table **only to preview data**, not to restrict queries
    table_preview = st.sidebar.selectbox(
        "Preview Table (optional)",
        ["None"] + tables
    )

    # Show first few rows of the selected table
    if table_preview and table_preview != "None":
         # your frontend API
        preview_sql = f"SELECT * FROM `{table_preview}` LIMIT 5;"
        result = execute_sql(preview_sql, db_selected)
        if result.get("status") == "success":
            st.sidebar.dataframe(result.get("rows"))

    return db_selected

