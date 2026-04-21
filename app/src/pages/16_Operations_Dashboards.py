##################################################
# Operations Feature Page: Dashboards
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

st.set_page_config(page_title="Operations Dashboards", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")
USER_ID = st.session_state.get("user_id")


def get_dashboards(user_id=None):
    url = f"{API_BASE_URL}/dashboards"
    params = {}
    if user_id:
        params["user_id"] = user_id
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_widgets(dashboard_id):
    url = f"{API_BASE_URL}/dashboards/{dashboard_id}/widgets"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Operations Dashboards 📊")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Manager')}**. "
    "View dashboards and monitor key campus metrics."
)

try:
    dashboards = get_dashboards(USER_ID)

    if not dashboards:
        st.info("No dashboards found for this user.")
        st.stop()

    df = pd.DataFrame(dashboards)

    dashboard_options = {
        f"{row['dashboard_name']} ({row['dashboard_type']})": row["dashboard_id"]
        for _, row in df.iterrows()
    }

    selected_dashboard_label = st.selectbox(
        "Select a dashboard", list(dashboard_options.keys())
    )

    selected_dashboard_id = dashboard_options[selected_dashboard_label]

    st.subheader("Dashboard Details")
    selected_row = df[df["dashboard_id"] == selected_dashboard_id].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {selected_row['dashboard_name']}")
        st.write(f"**Type:** {selected_row['dashboard_type']}")
    with col2:
        st.write(f"**Created:** {selected_row.get('created_at', 'N/A')}")
        st.write(f"**Updated:** {selected_row.get('updated_at', 'N/A')}")

    st.divider()

    st.subheader("Widgets")
    widgets = get_widgets(selected_dashboard_id)

    if not widgets:
        st.warning("No widgets found for this dashboard.")
    else:
        widgets_df = pd.DataFrame(widgets)

        display_cols = [
            col
            for col in [
                "widget_name",
                "widget_type",
                "metric_name",
                "x_position",
                "y_position",
            ]
            if col in widgets_df.columns
        ]

        st.dataframe(
            widgets_df[display_cols], use_container_width=True, hide_index=True
        )

        if "metric_name" in widgets_df.columns:
            st.subheader("Widget Metrics Overview")
            metric_counts = widgets_df["metric_name"].value_counts()
            st.bar_chart(metric_counts)

except requests.exceptions.RequestException as e:
    logger.error("API error on dashboards page: %s", e)
    st.error("Could not load dashboards from API.")

except Exception as e:
    logger.error("Unexpected error on dashboards page: %s", e)
    st.error("Something went wrong while loading dashboards.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back to Operations Home", use_container_width=True):
        st.switch_page("pages/10_Operations_Manager_Home.py")

with col2:
    if st.button("View Current Crowd", use_container_width=True):
        st.switch_page("pages/11_Operations_Current_Crowd.py")

with col3:
    if st.button("Edit Hours", use_container_width=True):
        st.switch_page("pages/15_Operations_Hours.py")
