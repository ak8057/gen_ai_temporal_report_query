import streamlit as st
from components.sidebar import sidebar_ui


from components.file_upload import upload_ui
from components.nl_query import nl_query_ui
from components.sql_editor import sql_editor_ui
from components.followup import followup_ui
from components.result_viewer import show_result_summary

st.set_page_config(
    page_title="NL2SQL Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("NL2SQL Dashboard")


# Sidebar
db_selected = sidebar_ui()

# Two columns for query & results
col1, col2 = st.columns([1,1])

with col1:
    upload_ui(db_selected)
    nl_query_ui(db_selected)
    followup_ui(db_selected)

with col2:
    sql_editor_ui(db_selected)
    if "last_sql" in st.session_state and st.session_state["last_sql"]:
        sql_query = st.session_state["last_sql"]
        show_result_summary(sql_query, db_selected)
