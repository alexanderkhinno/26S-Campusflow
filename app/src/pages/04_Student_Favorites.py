##################################################
# Student Feature Page: Manage Favorites
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

st.set_page_config(page_title="Student Favorites", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")
USER_ID = st.session_state.get("user_id")


def get_user_favorites(user_id):
    url = f"{API_BASE_URL}/users/{user_id}/favorites"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_locations():
    url = f"{API_BASE_URL}/locations"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def add_favorite(user_id, location_id):
    url = f"{API_BASE_URL}/users/{user_id}/favorites"
    response = requests.post(url, json={"location_id": location_id}, timeout=10)
    response.raise_for_status()
    return response.json()


def delete_favorite(user_id, location_id):
    url = f"{API_BASE_URL}/users/{user_id}/favorites/{location_id}"
    response = requests.delete(url, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Manage Favorite Locations ⭐")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Student')}**. "
    "Use this page to view, add, and remove your saved campus locations."
)

if not USER_ID:
    st.error(
        "No user is selected in the session. Please return to Home and log in again."
    )
    st.stop()

refresh_key = "student_favorites_refresh"
if refresh_key not in st.session_state:
    st.session_state[refresh_key] = 0

try:
    favorites = get_user_favorites(USER_ID)
    locations = get_locations()

    favorites_df = pd.DataFrame(favorites) if favorites else pd.DataFrame()
    locations_df = pd.DataFrame(locations) if locations else pd.DataFrame()

    st.subheader("Your Current Favorites")

    if favorites_df.empty:
        st.info("You do not have any favorite locations saved yet.")
        existing_favorite_ids = set()
    else:
        existing_favorite_ids = set(favorites_df["location_id"].tolist())
        display_columns = [
            col
            for col in [
                "location_name",
                "building_name",
                "campus_zone",
                "status",
                "current_open_flag",
                "saved_at",
            ]
            if col in favorites_df.columns
        ]
        st.dataframe(
            favorites_df[display_columns],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Add a Favorite")

        if locations_df.empty:
            st.warning("No locations are available to add.")
        else:
            available_locations = locations_df[
                ~locations_df["location_id"].isin(existing_favorite_ids)
            ]

            if available_locations.empty:
                st.success("All available locations are already in your favorites.")
            else:
                add_options = {
                    f"{row['location_name']} ({row['building_name']})": row[
                        "location_id"
                    ]
                    for _, row in available_locations.iterrows()
                }

                selected_add_label = st.selectbox(
                    "Choose a location to add",
                    list(add_options.keys()),
                    key="student_add_favorite_select",
                )

                if st.button("Add Favorite", use_container_width=True):
                    try:
                        add_result = add_favorite(
                            USER_ID, add_options[selected_add_label]
                        )
                        st.success(
                            add_result.get("message", "Favorite added successfully.")
                        )
                        st.rerun()
                    except requests.exceptions.RequestException as e:
                        logger.error("Error adding favorite: %s", e)
                        error_message = "Could not add favorite location."
                        if e.response is not None:
                            try:
                                error_message = e.response.json().get(
                                    "error", error_message
                                )
                            except Exception:
                                pass
                        st.error(error_message)

    with col2:
        st.subheader("Remove a Favorite")

        if favorites_df.empty:
            st.warning("You do not have any favorites to remove.")
        else:
            remove_options = {
                f"{row['location_name']} ({row['building_name']})": row["location_id"]
                for _, row in favorites_df.iterrows()
            }

            selected_remove_label = st.selectbox(
                "Choose a favorite to remove",
                list(remove_options.keys()),
                key="student_remove_favorite_select",
            )

            if st.button("Remove Favorite", use_container_width=True):
                try:
                    delete_result = delete_favorite(
                        USER_ID, remove_options[selected_remove_label]
                    )
                    st.success(
                        delete_result.get("message", "Favorite removed successfully.")
                    )
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    logger.error("Error removing favorite: %s", e)
                    error_message = "Could not remove favorite location."
                    if e.response is not None:
                        try:
                            error_message = e.response.json().get(
                                "error", error_message
                            )
                        except Exception:
                            pass
                    st.error(error_message)

except requests.exceptions.RequestException as e:
    logger.error("API error on Student Favorites page: %s", e)
    st.error(
        "Could not connect to the CampusFlow API. Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Student Favorites page: %s", e)
    st.error("Something went wrong while loading favorite locations.")

st.divider()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Back to Student Home", use_container_width=True):
        st.switch_page("pages/00_Student_Home.py")
with nav_col2:
    if st.button("View Crowd Levels", use_container_width=True):
        st.switch_page("pages/01_Student_Crowd.py")
with nav_col3:
    if st.button("Check Location Hours", use_container_width=True):
        st.switch_page("pages/02_Student_Hours.py")
