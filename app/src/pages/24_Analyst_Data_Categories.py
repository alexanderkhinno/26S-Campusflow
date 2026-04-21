##################################################
# Data Analyst Feature Page: Data Categories
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

st.set_page_config(page_title="Data Categories", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")


def get_data_categories():
    url = f"{API_BASE_URL}/data-categories"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_data_category(category_id):
    url = f"{API_BASE_URL}/data-categories/{category_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Data Categories 📂")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Analyst')}**. "
    "Explore data category definitions used across the system."
)

try:
    categories = get_data_categories()

    if not categories:
        st.info("No data categories found.")
        st.stop()

    df = pd.DataFrame(categories)

    st.subheader("All Categories")
    display_cols = [
        col
        for col in [
            "category_id",
            "category_name",
            "description",
            "active_flag",
            "updated_at",
        ]
        if col in df.columns
    ]

    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Inspect Category")

    category_options = {
        f"{row['category_name']} (ID {row['category_id']})": row["category_id"]
        for _, row in df.iterrows()
    }

    selected_label = st.selectbox("Select a category", list(category_options.keys()))
    selected_id = category_options[selected_label]

    category_detail = get_data_category(selected_id)

    st.subheader("Category Details")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**ID:** {category_detail.get('category_id')}")
        st.write(f"**Name:** {category_detail.get('category_name')}")
        st.write(f"**Active:** {category_detail.get('active_flag')}")

    with col2:
        st.write(f"**Description:** {category_detail.get('description', 'N/A')}")
        st.write(f"**Last Updated:** {category_detail.get('updated_at', 'N/A')}")

except requests.exceptions.RequestException as e:
    logger.error("API error on Data Categories page: %s", e)
    st.error("Could not load data categories from API.")

except Exception as e:
    logger.error("Unexpected error on Data Categories page: %s", e)
    st.error("Something went wrong while loading categories.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Analyst Home", use_container_width=True):
        st.switch_page("pages/20_Data_Analyst_Home.py")

with col2:
    if st.button("View Crowd History", use_container_width=True):
        st.switch_page("pages/21_Analyst_Crowd_History.py")
