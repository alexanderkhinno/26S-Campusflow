##################################################
# Operations Feature Page: Current Crowd Comparison
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

st.set_page_config(page_title="Operations Current Crowd", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")


def get_current_crowd():
    url = f"{API_BASE_URL}/crowd/current"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Current Crowd Conditions Across Campus 📊")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Manager')}**. "
    "Use this page to compare current occupancy conditions across active campus locations."
)

try:
    crowd_data = get_current_crowd()

    if not crowd_data:
        st.info("No current crowd data is available right now.")
    else:
        df = pd.DataFrame(crowd_data)

        if "campus_zone" in df.columns:
            zone_filter = st.selectbox(
                "Filter by Campus Zone",
                options=["All"] + sorted(df["campus_zone"].dropna().unique().tolist()),
            )
            if zone_filter != "All":
                df = df[df["campus_zone"] == zone_filter]

        if "crowd_level" in df.columns:
            level_filter = st.multiselect(
                "Filter by Crowd Level",
                options=sorted(df["crowd_level"].dropna().unique().tolist()),
                default=sorted(df["crowd_level"].dropna().unique().tolist()),
            )
            if level_filter:
                df = df[df["crowd_level"].isin(level_filter)]

        if df.empty:
            st.warning("No locations match the selected filters.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Locations Displayed", len(df))
            with col2:
                if "occupancy_percent" in df.columns:
                    st.metric(
                        "Average Occupancy %", round(df["occupancy_percent"].mean(), 1)
                    )
            with col3:
                if "crowd_count" in df.columns:
                    st.metric("Total People Counted", int(df["crowd_count"].sum()))

            if "occupancy_percent" in df.columns:
                df = df.sort_values(by="occupancy_percent", ascending=False)

            display_columns = [
                col
                for col in [
                    "location_name",
                    "building_name",
                    "campus_zone",
                    "crowd_count",
                    "crowd_level",
                    "occupancy_percent",
                    "measured_at",
                ]
                if col in df.columns
            ]

            st.subheader("Current Occupancy Table")
            st.dataframe(
                df[display_columns],
                use_container_width=True,
                hide_index=True,
            )

            if "location_name" in df.columns and "occupancy_percent" in df.columns:
                st.subheader("Occupancy by Location")
                chart_df = df[["location_name", "occupancy_percent"]].set_index(
                    "location_name"
                )
                st.bar_chart(chart_df)

except requests.exceptions.RequestException as e:
    logger.error("Error fetching current crowd data: %s", e)
    st.error(
        "Could not connect to the CampusFlow API to load current crowd data. "
        "Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Operations Current Crowd page: %s", e)
    st.error("Something went wrong while loading current crowd conditions.")

st.divider()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Back to Operations Home", use_container_width=True):
        st.switch_page("pages/10_Operations_Manager_Home.py")
with nav_col2:
    if st.button("View Crowd History", use_container_width=True):
        st.switch_page("pages/12_Operations_Crowd_History.py")
with nav_col3:
    if st.button("Edit Operating Hours", use_container_width=True):
        st.switch_page("pages/15_Operations_Hours.py")
