##################################################
# System Administrator Persona Home Page (Kevin Brooks)
##################################################

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="System Admin Home", layout="wide")

SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

st.title(f"Welcome, {st.session_state.get('first_name', 'Admin')} 👋")

st.write("### System Administration Dashboard")
st.write(
    "Monitor backend operations, review logs, manage configurations, "
    "and oversee pipeline performance."
)

st.divider()

st.subheader("System Monitoring")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("View Pipeline Runs", use_container_width=True):
        st.switch_page("pages/31_Admin_Pipeline_Runs.py")

with col2:
    if st.button("View System Logs", use_container_width=True):
        st.switch_page("pages/32_Admin_System_Logs.py")

with col3:
    if st.button("View System Configs", use_container_width=True):
        st.switch_page("pages/33_Admin_System_Configs.py")

st.divider()

st.subheader("Maintenance Actions")

col4, col5 = st.columns(2)

with col4:
    if st.button("Clean Up Logs", use_container_width=True):
        st.switch_page("pages/34_Admin_Cleanup_Logs.py")

with col5:
    if st.button("Manage Data Integrity", use_container_width=True):
        st.switch_page("pages/35_Admin_Data_Integrity.py")

st.divider()

st.info(
    "Use these tools to monitor system health, investigate issues, and maintain backend reliability."
)
