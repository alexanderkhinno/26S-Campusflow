##################################################
# Student Feature Page: Current Crowd Levels
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

st.set_page_config(page_title="Student Crowd Levels", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")


def get_current_crowd():
    """Fetch current crowd data for all active locations."""
    url = f"{API_BASE_URL}/crowd/current"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def format_open_status(row):
    occupancy = row.get("occupancy_percent")
    if occupancy is None:
        return "Unknown"
    if occupancy < 35:
        return "Great time to go"
    if occupancy < 70:
        return "Moderately busy"
    return "Very busy"


st.title("Current Crowd Levels")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Student')}**. "
    "Use this page to quickly compare crowd conditions across active campus locations."
)

st.markdown("### Live Campus Snapshot")

try:
    crowd_data = get_current_crowd()

    if not crowd_data:
        st.info("No current crowd data is available right now.")
    else:
        df = pd.DataFrame(crowd_data)

        if "occupancy_percent" in df.columns:
            df["student_recommendation"] = df.apply(format_open_status, axis=1)

        display_columns = [
            col
            for col in [
                "location_name",
                "building_name",
                "campus_zone",
                "crowd_count",
                "crowd_level",
                "occupancy_percent",
                "student_recommendation",
                "measured_at",
            ]
            if col in df.columns
        ]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Locations Reporting", len(df))
        with col2:
            if "occupancy_percent" in df.columns and not df.empty:
                avg_occupancy = round(df["occupancy_percent"].mean(), 1)
                st.metric("Average Occupancy %", avg_occupancy)
        with col3:
            if "crowd_level" in df.columns and not df.empty:
                most_common = df["crowd_level"].mode()
                st.metric(
                    "Most Common Crowd Level",
                    most_common.iloc[0] if not most_common.empty else "N/A",
                )

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Locations labeled 'Great time to go' currently have relatively low occupancy."
        )

except requests.exceptions.RequestException as e:
    logger.error("Error fetching current crowd data: %s", e)
    st.error(
        "Could not connect to the CampusFlow API to load crowd data. "
        "Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Student Crowd page: %s", e)
    st.error("Something went wrong while loading current crowd levels.")

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Back to Student Home", use_container_width=True):
        st.switch_page("pages/00_Student_Home.py")

with col_b:
    if st.button("Check Location Hours", use_container_width=True):
        st.switch_page("pages/02_Student_Hours.py")
