import streamlit as st
from utils.api import list_databases, list_tables, execute_sql

def sidebar_ui():
    st.sidebar.title("⚙️ Settings")

    # --- Step 1: Select Database ---
    db_response = list_databases()
    databases = db_response.get("databases", [])
    if not databases:
        st.sidebar.warning("No databases found. Please upload a file first.")
        return None

    db_selected = st.sidebar.selectbox("Select Database", databases)

    # --- Step 2: Select Table ---
    table_response = list_tables(db_selected)
    tables = table_response.get("tables", [])
    if not tables:
        st.sidebar.warning(f"No tables found in database '{db_selected}'.")
        return {"db_name": db_selected, "table_name": None}

    table_selected = st.sidebar.selectbox("Select Table", tables)

    # --- Step 3: Optional Table Preview ---
    st.sidebar.markdown("### 🔍 Preview Selected Table")
    if table_selected:
        try:
            preview_sql = f"SELECT * FROM `{table_selected}` LIMIT 5;"
            result = execute_sql(preview_sql, db_selected)

            if result.get("status") == "success":
                st.sidebar.dataframe(result.get("rows"))
            else:
                st.sidebar.error(result.get("detail", "Failed to load preview."))

        except Exception as e:
            st.sidebar.error(f"Error previewing table: {e}")

    # --- Step 4: Return both DB and Table ---
    return {"db_name": db_selected, "table_name": table_selected}
