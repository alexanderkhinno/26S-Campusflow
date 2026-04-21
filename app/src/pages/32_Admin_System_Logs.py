##################################################
# System Admin Feature Page: System Logs
##################################################

import logging
import os

import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

logging.basicConfig(
    format="%(filename)s:%(lineno)s:%(levelname)s -- %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Admin System Logs", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")


def get_system_logs(params=None):
    url = f"{API_BASE_URL}/system-logs"
    response = requests.get(url, params=params or {}, timeout=10)
    response.raise_for_status()
    return response.json()


def delete_log(log_id):
    url = f"{API_BASE_URL}/system-logs/{log_id}"
    response = requests.delete(url, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("System Logs 📜")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Admin')}**. "
    "View, filter, and remove system logs to maintain system health."
)

try:
    st.subheader("Filter Logs")
    col1, col2, col3 = st.columns(3)

    with col1:
        level = st.selectbox(
            "Log Level",
            ["All", "INFO", "WARNING", "ERROR"],
        )
    with col2:
        component = st.text_input("Component Name")
    with col3:
        start = st.text_input("Start Date (YYYY-MM-DD)")

    end = st.text_input("End Date (YYYY-MM-DD)")

    params = {}
    if level != "All":
        params["level"] = level
    if component.strip():
        params["component"] = component.strip()
    if start.strip():
        params["start"] = start.strip()
    if end.strip():
        params["end"] = end.strip()

    logs = get_system_logs(params)
    df = pd.DataFrame(logs) if logs else pd.DataFrame()

    st.divider()
    st.subheader("System Logs")

    if df.empty:
        st.info("No logs found for selected filters.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Delete a Log")

        selected_log_id = st.number_input(
            "Log ID to Delete",
            min_value=1,
            step=1,
        )

        if st.button("Delete Log", type="primary"):
            try:
                result = delete_log(int(selected_log_id))
                st.success(result.get("message", "Log deleted successfully."))
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error("Error deleting log: %s", e)
                st.error("Failed to delete log.")

except requests.exceptions.RequestException as e:
    logger.error("API error on System Logs page: %s", e)
    st.error("Could not connect to backend API.")

except Exception as e:
    logger.error("Unexpected error: %s", e)
    st.error("Something went wrong.")

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("Back to Admin Home", use_container_width=True):
        st.switch_page("pages/30_System_Admin_Home.py")
with col2:
    if st.button("Pipeline Runs", use_container_width=True):
        st.switch_page("pages/31_Admin_Pipeline_Runs.py")
