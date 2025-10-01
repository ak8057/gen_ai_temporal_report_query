import streamlit as st

def followup_ui():
    st.subheader("Follow-up Question")
    followup = st.text_input("Ask a follow-up")
    if followup and "last_sql" in st.session_state:
        st.info("Will append context to previous question and call NL2SQL chain")
        # optionally, send combined question to NL2SQL endpoint
