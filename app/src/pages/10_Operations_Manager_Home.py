##################################################
# Operations Manager Persona Home Page (Mark Preston)
##################################################

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Operations Manager Home", layout="wide")

SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

st.title(f"Welcome, {st.session_state.get('first_name', 'Manager')} 👋")

st.write("### Campus Operations Dashboard")
st.write(
    "Monitor location conditions, compare facilities, update operating hours, "
    "and review dashboard metrics for campus spaces."
)

st.divider()

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Compare Current Crowd Levels", use_container_width=True):
        st.switch_page("pages/11_Operations_Current_Crowd.py")

with col2:
    if st.button("View Crowd History", use_container_width=True):
        st.switch_page("pages/12_Operations_Crowd_History.py")

with col3:
    if st.button("View Predictions", use_container_width=True):
        st.switch_page("pages/13_Operations_Predictions.py")

st.divider()

st.subheader("Facility Management")

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("Review Locations", use_container_width=True):
        st.switch_page("pages/14_Operations_Locations.py")

with col5:
    if st.button("Edit Operating Hours", use_container_width=True):
        st.switch_page("pages/15_Operations_Hours.py")

with col6:
    if st.button("Open Dashboards", use_container_width=True):
        st.switch_page("pages/16_Operations_Dashboards.py")

st.divider()

st.info(
    "Use the actions above to manage facilities, staffing visibility, and operational planning."
)
