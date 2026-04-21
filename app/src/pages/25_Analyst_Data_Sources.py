##################################################
# Data Analyst Feature Page: Data Sources
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

st.set_page_config(page_title="Analyst Data Sources", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")
USER_ID = st.session_state.get("user_id")


def get_locations():
    url = f"{API_BASE_URL}/locations"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


# Your backend currently exposes POST/DELETE for data sources, not a GET route,
# so this page focuses on creation workflows and uses reference tables from the
# available API endpoints.
def create_data_source(payload):
    url = f"{API_BASE_URL}/data-sources"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def get_data_categories():
    url = f"{API_BASE_URL}/data-categories"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def create_location_data_source(payload):
    url = f"{API_BASE_URL}/location-data-sources"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Manage Data Sources 🔗")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Analyst')}**. "
    "Create new data sources and map them to locations and data categories."
)

if not USER_ID:
    st.error(
        "No user is selected in the session. Please return to Home and log in again."
    )
    st.stop()

try:
    locations = get_locations()
    categories = get_data_categories()

    locations_df = pd.DataFrame(locations) if locations else pd.DataFrame()
    categories_df = pd.DataFrame(categories) if categories else pd.DataFrame()

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Create a New Data Source")

        with st.form("create_data_source_form"):
            source_name = st.text_input("Source Name")
            source_type = st.text_input("Source Type")
            refresh_interval_minutes = st.number_input(
                "Refresh Interval (minutes)",
                min_value=1,
                value=30,
                step=1,
            )
            status = st.selectbox("Status", ["active", "inactive"])

            submitted_source = st.form_submit_button("Create Data Source")

            if submitted_source:
                if not source_name.strip() or not source_type.strip():
                    st.error("Source name and source type are required.")
                else:
                    try:
                        payload = {
                            "source_name": source_name.strip(),
                            "source_type": source_type.strip(),
                            "refresh_interval_minutes": int(refresh_interval_minutes),
                            "status": status,
                            "created_by_user_id": USER_ID,
                        }
                        result = create_data_source(payload)
                        st.success(
                            f"{result.get('message', 'Data source created successfully.')} "
                            f"New ID: {result.get('data_source_id', 'N/A')}"
                        )
                        st.session_state["latest_data_source_id"] = result.get(
                            "data_source_id"
                        )
                    except requests.exceptions.RequestException as e:
                        logger.error("Error creating data source: %s", e)
                        error_message = "Could not create data source."
                        if e.response is not None:
                            try:
                                error_message = e.response.json().get(
                                    "error", error_message
                                )
                            except Exception:
                                pass
                        st.error(error_message)

    with right_col:
        st.subheader("Map Data Source to a Location")

        if locations_df.empty or categories_df.empty:
            st.warning(
                "Locations and categories must exist before mappings can be created."
            )
        else:
            location_options = {
                f"{row['location_name']} ({row['building_name']})": row["location_id"]
                for _, row in locations_df.iterrows()
            }
            category_options = {
                f"{row['category_name']} (ID {row['category_id']})": row["category_id"]
                for _, row in categories_df.iterrows()
            }

            with st.form("create_location_data_source_form"):
                latest_source_id = st.session_state.get("latest_data_source_id")
                data_source_id = st.number_input(
                    "Data Source ID",
                    min_value=1,
                    value=int(latest_source_id) if latest_source_id else 1,
                    step=1,
                )
                selected_location_label = st.selectbox(
                    "Location",
                    list(location_options.keys()),
                )
                selected_category_label = st.selectbox(
                    "Data Category",
                    list(category_options.keys()),
                )

                submitted_mapping = st.form_submit_button("Create Mapping")

                if submitted_mapping:
                    try:
                        payload = {
                            "location_id": location_options[selected_location_label],
                            "data_source_id": int(data_source_id),
                            "category_id": category_options[selected_category_label],
                        }
                        result = create_location_data_source(payload)
                        st.success(
                            result.get(
                                "message",
                                "Location-data-source mapping created successfully.",
                            )
                        )
                    except requests.exceptions.RequestException as e:
                        logger.error(
                            "Error creating location-data-source mapping: %s", e
                        )
                        error_message = "Could not create mapping."
                        if e.response is not None:
                            try:
                                error_message = e.response.json().get(
                                    "error", error_message
                                )
                            except Exception:
                                pass
                        st.error(error_message)

    st.divider()
    st.subheader("Reference Data")

    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.write("**Available Locations**")
        if locations_df.empty:
            st.info("No locations found.")
        else:
            display_location_cols = [
                col
                for col in [
                    "location_id",
                    "location_name",
                    "building_name",
                    "campus_zone",
                ]
                if col in locations_df.columns
            ]
            st.dataframe(
                locations_df[display_location_cols],
                use_container_width=True,
                hide_index=True,
            )

    with ref_col2:
        st.write("**Available Data Categories**")
        if categories_df.empty:
            st.info("No categories found.")
        else:
            display_category_cols = [
                col
                for col in [
                    "category_id",
                    "category_name",
                    "description",
                    "active_flag",
                ]
                if col in categories_df.columns
            ]
            st.dataframe(
                categories_df[display_category_cols],
                use_container_width=True,
                hide_index=True,
            )

except requests.exceptions.RequestException as e:
    logger.error("API error on Analyst Data Sources page: %s", e)
    st.error(
        "Could not connect to the CampusFlow API. Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Analyst Data Sources page: %s", e)
    st.error("Something went wrong while loading the data sources page.")

st.divider()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Back to Analyst Home", use_container_width=True):
        st.switch_page("pages/20_Data_Analyst_Home.py")
with nav_col2:
    if st.button("View Data Categories", use_container_width=True):
        st.switch_page("pages/24_Analyst_Data_Categories.py")
with nav_col3:
    if st.button("Build Dashboards", use_container_width=True):
        st.switch_page("pages/26_Analyst_Dashboards.py")
