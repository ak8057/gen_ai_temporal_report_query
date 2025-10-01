import streamlit as st
from components.sidebar import sidebar_ui
from components.file_upload import upload_ui
from components.nl_query import nl_query_ui
from components.sql_editor import sql_editor_ui
from components.followup import followup_ui

st.set_page_config(
    page_title="NL2SQL Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("NL2SQL Dashboard")

# Sidebar
db_selected, table_selected = sidebar_ui()

# Two columns for query & results
col1, col2 = st.columns([1,1])

with col1:
    upload_ui(db_selected)
    nl_query_ui(db_selected)
    followup_ui()

with col2:
    sql_editor_ui(db_selected)
