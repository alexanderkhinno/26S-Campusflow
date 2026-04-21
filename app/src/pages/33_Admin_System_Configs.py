##################################################
# System Admin Feature Page: System Configs
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

st.set_page_config(page_title="Admin System Configs", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")
USER_ID = st.session_state.get("user_id")


def get_system_configs():
    url = f"{API_BASE_URL}/system-configs"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def update_system_config(config_id, payload):
    url = f"{API_BASE_URL}/system-configs/{config_id}"
    response = requests.put(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("System Configurations ⚙️")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Admin')}**. "
    "View and update system configuration settings."
)

if not USER_ID:
    st.error(
        "No user is selected in the session. Please return to Home and log in again."
    )
    st.stop()

try:
    configs = get_system_configs()
    df = pd.DataFrame(configs) if configs else pd.DataFrame()

    st.subheader("Current Configurations")

    if df.empty:
        st.info("No configuration settings found.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Update a Configuration")

        config_options = {
            f"{row['config_key']} (ID {row['config_id']})": row["config_id"]
            for _, row in df.iterrows()
        }

        selected_label = st.selectbox("Select Config", list(config_options.keys()))
        selected_id = config_options[selected_label]

        with st.form("update_config_form"):
            new_value = st.text_input("New Value")
            new_description = st.text_input("New Description (optional)")

            submitted = st.form_submit_button("Update Config")

            if submitted:
                try:
                    payload = {
                        "config_value": new_value,
                        "config_description": new_description
                        if new_description
                        else None,
                        "updated_by_user_id": USER_ID,
                    }
                    result = update_system_config(selected_id, payload)
                    st.success(result.get("message", "Config updated successfully."))
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    logger.error("Error updating config: %s", e)
                    st.error("Failed to update configuration.")

except requests.exceptions.RequestException as e:
    logger.error("API error on System Configs page: %s", e)
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
    if st.button("System Logs", use_container_width=True):
        st.switch_page("pages/32_Admin_System_Logs.py")
