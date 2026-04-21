##################################################
# Data Analyst Persona Home Page (Jason Morrison)
##################################################

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Data Analyst Home", layout="wide")

SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

st.title(f"Welcome, {st.session_state.get('first_name', 'Analyst')} 👋")

st.write("### Data Analyst Dashboard")
st.write(
    "Explore historical and predicted crowd data, review categories and sources, "
    "and build analytics dashboards for reporting."
)

st.divider()

st.subheader("Analytics Tools")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Analyze Crowd History", use_container_width=True):
        st.switch_page("pages/21_Analyst_Crowd_History.py")

with col2:
    if st.button("Review Predictions", use_container_width=True):
        st.switch_page("pages/22_Analyst_Predictions.py")

with col3:
    if st.button("Review Locations", use_container_width=True):
        st.switch_page("pages/23_Analyst_Locations.py")

st.divider()

st.subheader("Data Management")

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("View Data Categories", use_container_width=True):
        st.switch_page("pages/24_Analyst_Data_Categories.py")

with col5:
    if st.button("Manage Data Sources", use_container_width=True):
        st.switch_page("pages/25_Analyst_Data_Sources.py")

with col6:
    if st.button("Build Dashboards", use_container_width=True):
        st.switch_page("pages/26_Analyst_Dashboards.py")

st.divider()

st.info(
    "Use these tools to explore trends, maintain data inputs, and create analytics views."
)
