import streamlit as st
import pandas as pd
import requests
from utils.api import BASE_URL

# You'll need to update this to the correct endpoint for your API
# This is the endpoint that takes a natural language question and returns a SQL query.
GENERATE_SQL_ENDPOINT = f"{BASE_URL}/"

def followup_ui(db_selected):
    st.subheader("Follow-up Question")

    # --- Robust Session State Initialization ---
    # This pattern guarantees the variables exist before they are accessed.
    if "last_result_df" not in st.session_state:
        st.session_state.last_result_df = pd.DataFrame()

    if "last_sql" not in st.session_state:
        st.session_state.last_sql = ""
        
    if "last_followup_sql" not in st.session_state:
        st.session_state.last_followup_sql = ""

    # --- UI and Logic ---
    # Show previous result only if it exists
    if not st.session_state.last_result_df.empty:
        st.markdown("**Previous Result:**")
        st.dataframe(st.session_state.last_result_df)
    else:
        st.info("No previous result found. Please run a main query first.")

    followup = st.text_input("Ask a follow-up question related to the previous result")

    if st.button("Generate Follow-up SQL") and followup:
        if st.session_state.last_sql == "":
            st.warning("Please run a main query first before asking a follow-up.")
            return

        st.info("Processing follow-up question...")
        
        db_name = st.session_state.get(db_selected)
        
        # --- The Fix: Correct Logical Flow ---
        try:
            # 1. Send the follow-up question to the NL2SQL API to get a NEW SQL query.
            # This is the step that was missing.
            followup_request_body = {
                "question": followup,
                "db_name": db_name,
                "context": st.session_state.last_sql # Provide the previous SQL as context
            }
            
            # Assuming your API endpoint for generating SQL is at GENERATE_SQL_ENDPOINT
            response = requests.post(GENERATE_SQL_ENDPOINT, json=followup_request_body)
            response.raise_for_status() # Raise an exception for bad status codes
            
            followup_sql = response.json().get("sql_query")
            st.session_state.last_followup_sql = followup_sql
            
            st.success("Generated SQL for follow-up:")
            st.code(followup_sql)

            # 2. You can then execute this new query on the database
            # This part is optional but highly recommended to show the result.
            # You would call your 'execute_query' API endpoint here.
            # df_followup = execute_sql(followup_sql)
            # st.session_state.last_result_df = df_followup
            # st.dataframe(df_followup)

        except requests.exceptions.RequestException as e:
            st.error(f"Error generating follow-up SQL: {e}")
            st.code(f"Response: {response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")