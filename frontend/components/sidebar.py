import streamlit as st
from utils.api import list_databases, list_tables

def sidebar_ui():
    st.sidebar.title("Settings")

    # Database selection
    databases = list_databases().get("databases", [])
    db_selected = st.sidebar.selectbox("Select Database", databases)

    # Table selection
    tables = list_tables(db_selected).get("tables", [])
    table_selected = st.sidebar.selectbox("Select Table", tables)

    return db_selected, table_selected
