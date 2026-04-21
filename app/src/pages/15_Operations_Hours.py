##################################################
# Operations Feature Page: Edit Operating Hours
##################################################

import logging
import os

import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

logging.basicConfig(
    format="%(filename)s:%(lineno)s:%(levelname)s -- %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Edit Operating Hours", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")
USER_ID = st.session_state.get("user_id")
VALID_DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def get_locations():
    url = f"{API_BASE_URL}/locations"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_location_hours(location_id):
    url = f"{API_BASE_URL}/locations/{location_id}/hours"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def update_location_hours(location_id, day_of_week, payload):
    url = f"{API_BASE_URL}/locations/{location_id}/hours/{day_of_week}"
    response = requests.put(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Edit Operating Hours ⏰")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Manager')}**. "
    "Select a location, review its current schedule, and update hours for a specific day."
)

if not USER_ID:
    st.error(
        "No user is selected in the session. Please return to Home and log in again."
    )
    st.stop()

try:
    locations = get_locations()

    if not locations:
        st.info("No locations are available.")
        st.stop()

    locations_df = pd.DataFrame(locations)
    location_options = {
        f"{row['location_name']} ({row['building_name']})": row["location_id"]
        for _, row in locations_df.iterrows()
    }

    selected_location_label = st.selectbox(
        "Choose a location",
        list(location_options.keys()),
        key="ops_hours_location_select",
    )
    selected_location_id = location_options[selected_location_label]

    hours_data = get_location_hours(selected_location_id)

    st.subheader("Current Operating Hours")
    if not hours_data:
        st.warning("No operating hours are stored for this location.")
        hours_df = pd.DataFrame(
            columns=["day_of_week", "open_time", "close_time", "updated_at"]
        )
    else:
        hours_df = pd.DataFrame(hours_data)
        display_cols = [
            col
            for col in ["day_of_week", "open_time", "close_time", "updated_at"]
            if col in hours_df.columns
        ]
        st.dataframe(hours_df[display_cols], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Update Hours")

    selected_day = st.selectbox(
        "Day of week",
        VALID_DAYS,
        key="ops_hours_day_select",
    )

    existing_row = None
    if not hours_df.empty and "day_of_week" in hours_df.columns:
        matches = hours_df[hours_df["day_of_week"] == selected_day]
        if not matches.empty:
            existing_row = matches.iloc[0]

    default_open = "07:00"
    default_close = "22:00"

    if existing_row is not None:
        if "open_time" in existing_row and pd.notna(existing_row["open_time"]):
            default_open = str(existing_row["open_time"])[:5]
        if "close_time" in existing_row and pd.notna(existing_row["close_time"]):
            default_close = str(existing_row["close_time"])[:5]

    col1, col2 = st.columns(2)
    with col1:
        open_time = st.text_input(
            "Open time (HH:MM)",
            value=default_open,
            key="ops_hours_open_time",
        )
    with col2:
        close_time = st.text_input(
            "Close time (HH:MM)",
            value=default_close,
            key="ops_hours_close_time",
        )

    if st.button("Save Updated Hours", type="primary", use_container_width=True):
        payload = {
            "open_time": f"{open_time}:00" if len(open_time) == 5 else open_time,
            "close_time": f"{close_time}:00" if len(close_time) == 5 else close_time,
            "updated_by_user_id": USER_ID,
        }

        try:
            result = update_location_hours(selected_location_id, selected_day, payload)
            st.success(result.get("message", "Operating hours updated successfully."))
            st.rerun()
        except requests.exceptions.RequestException as e:
            logger.error("Error updating operating hours: %s", e)
            error_message = "Could not update operating hours."
            if e.response is not None:
                try:
                    error_message = e.response.json().get("error", error_message)
                except Exception:
                    pass
            st.error(error_message)

except requests.exceptions.RequestException as e:
    logger.error("API error on Operations Hours page: %s", e)
    st.error(
        "Could not connect to the CampusFlow API. Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Operations Hours page: %s", e)
    st.error("Something went wrong while loading or updating operating hours.")

st.divider()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Back to Operations Home", use_container_width=True):
        st.switch_page("pages/10_Operations_Manager_Home.py")
with nav_col2:
    if st.button("View Current Crowd", use_container_width=True):
        st.switch_page("pages/11_Operations_Current_Crowd.py")
with nav_col3:
    if st.button("Open Dashboards", use_container_width=True):
        st.switch_page("pages/16_Operations_Dashboards.py")
