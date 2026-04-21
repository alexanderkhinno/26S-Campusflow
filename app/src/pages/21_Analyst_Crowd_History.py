##################################################
# Data Analyst Feature Page: Crowd History
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

st.set_page_config(page_title="Analyst Crowd History", layout="wide")
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


def get_crowd_history(params=None):
    url = f"{API_BASE_URL}/crowd/history"
    response = requests.get(url, params=params or {}, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Historical Crowd Analysis 📉")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Analyst')}**. "
    "Use filters below to explore historical crowd measurements across campus."
)

try:
    locations = get_locations()
    location_df = pd.DataFrame(locations) if locations else pd.DataFrame()

    st.subheader("Filter Crowd History")
    col1, col2 = st.columns(2)

    with col1:
        location_options = {"All Locations": None}
        if not location_df.empty:
            location_options.update(
                {
                    f"{row['location_name']} ({row['building_name']})": row[
                        "location_id"
                    ]
                    for _, row in location_df.iterrows()
                }
            )

        selected_location_label = st.selectbox(
            "Location",
            list(location_options.keys()),
            key="analyst_history_location_select",
        )
        selected_location_id = location_options[selected_location_label]

        level_options = ["", "Low", "Medium", "High", "Very High"]
        selected_level = st.selectbox(
            "Crowd Level",
            level_options,
            key="analyst_history_level_select",
        )

    with col2:
        start_value = st.text_input(
            "Start Datetime (YYYY-MM-DD HH:MM:SS)",
            value="",
            key="analyst_history_start_input",
        )
        end_value = st.text_input(
            "End Datetime (YYYY-MM-DD HH:MM:SS)",
            value="",
            key="analyst_history_end_input",
        )
        source_value = st.text_input(
            "Source Label (optional)",
            value="",
            key="analyst_history_source_input",
        )

    query_params = {}
    if selected_location_id is not None:
        query_params["location_id"] = selected_location_id
    if selected_level:
        query_params["level"] = selected_level
    if start_value:
        query_params["start"] = start_value
    if end_value:
        query_params["end"] = end_value
    if source_value:
        query_params["source"] = source_value

    history_data = get_crowd_history(query_params)

    st.divider()
    st.subheader("Crowd History Results")

    if not history_data:
        st.info("No historical crowd records matched your filters.")
    else:
        df = pd.DataFrame(history_data)

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Records Returned", len(df))
        with metric_col2:
            if "occupancy_percent" in df.columns:
                st.metric(
                    "Average Occupancy %", round(df["occupancy_percent"].mean(), 1)
                )
        with metric_col3:
            if "crowd_count" in df.columns:
                st.metric("Average Crowd Count", round(df["crowd_count"].mean(), 1))

        display_cols = [
            col
            for col in [
                "location_name",
                "measured_at",
                "crowd_count",
                "crowd_level",
                "occupancy_percent",
                "source_label",
                "is_valid",
            ]
            if col in df.columns
        ]

        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
        )

        if "measured_at" in df.columns and "occupancy_percent" in df.columns:
            chart_df = df[["measured_at", "occupancy_percent"]].copy()
            chart_df["measured_at"] = pd.to_datetime(
                chart_df["measured_at"], errors="coerce"
            )
            chart_df = chart_df.dropna().sort_values("measured_at")
            if not chart_df.empty:
                st.subheader("Occupancy Trend")
                st.line_chart(chart_df.set_index("measured_at"))

except requests.exceptions.RequestException as e:
    logger.error("API error on Analyst Crowd History page: %s", e)
    st.error(
        "Could not connect to the CampusFlow API. Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Analyst Crowd History page: %s", e)
    st.error("Something went wrong while loading crowd history.")

st.divider()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Back to Analyst Home", use_container_width=True):
        st.switch_page("pages/20_Data_Analyst_Home.py")
with nav_col2:
    if st.button("Review Predictions", use_container_width=True):
        st.switch_page("pages/22_Analyst_Predictions.py")
with nav_col3:
    if st.button("Review Locations", use_container_width=True):
        st.switch_page("pages/23_Analyst_Locations.py")
