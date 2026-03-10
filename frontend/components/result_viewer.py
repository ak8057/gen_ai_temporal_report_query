import streamlit as st
import requests
import json
import plotly.graph_objects as go

BASE_URL = "http://localhost:8000/api"

def show_result_summary(sql_query, db_selected):
    if "last_summary" not in st.session_state:
        st.session_state.last_summary = None

    if "last_chart" not in st.session_state:
        st.session_state.last_chart = None

    if st.button("🧠 Generate Natural Language Summary"):
        with st.spinner("Generating summary..."):
            payload = {"sql_query": sql_query, "db_name": db_selected["db_name"]}
            res = requests.post(f"{BASE_URL}/summarize/", json=payload)

            if res.status_code == 200:
                data = res.json()
                st.session_state.last_summary = data.get("summary")
                st.session_state.last_chart = data.get("chart_json")
               
    if st.session_state.last_summary:
        st.markdown("### 🧠 Summary")
        st.write(st.session_state.last_summary)           
              
    if st.session_state.last_chart:
        import plotly.graph_objects as go
        import json
        fig = go.Figure(json.loads(st.session_state.last_chart))
        st.markdown("### 📊 Visualization")
        st.plotly_chart(fig, use_container_width=True)