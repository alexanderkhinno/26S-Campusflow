##################################################
# Student Feature Page: Location Hours
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

st.set_page_config(page_title="Location Hours", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")


def get_locations():
    url = f"{API_BASE_URL}/locations"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_hours(location_id):
    url = f"{API_BASE_URL}/locations/{location_id}/hours"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Check Location Hours ⏰")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Student')}**. "
    "Select a campus location to view its operating hours."
)

try:
    locations = get_locations()

    if not locations:
        st.info("No locations available.")
        st.stop()

    location_df = pd.DataFrame(locations)

    location_options = {
        f"{row['location_name']} ({row['building_name']})": row["location_id"]
        for _, row in location_df.iterrows()
    }

    selected_label = st.selectbox("Select a Location", list(location_options.keys()))
    selected_id = location_options[selected_label]

    st.divider()

    hours_data = get_hours(selected_id)

    if not hours_data:
        st.warning("No hours found for this location.")
    else:
        hours_df = pd.DataFrame(hours_data)

        display_cols = [
            col
            for col in ["day_of_week", "open_time", "close_time", "updated_at"]
            if col in hours_df.columns
        ]

        st.subheader("Operating Hours")
        st.dataframe(hours_df[display_cols], use_container_width=True, hide_index=True)

except requests.exceptions.RequestException as e:
    logger.error("API error: %s", e)
    st.error("Could not connect to the API. Make sure backend is running.")
except Exception as e:
    logger.error("Unexpected error: %s", e)
    st.error("Something went wrong while loading hours.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Student Home", use_container_width=True):
        st.switch_page("pages/00_Student_Home.py")

with col2:
    if st.button("View Crowd Levels", use_container_width=True):
        st.switch_page("pages/01_Student_Crowd.py")
