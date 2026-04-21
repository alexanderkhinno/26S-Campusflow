##################################################
# CampusFlow main landing / mock login page
##################################################

import logging

import streamlit as st
from modules.nav import SideBarLinks

logging.basicConfig(
    format="%(filename)s:%(lineno)s:%(levelname)s -- %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="CampusFlow", page_icon="🏫", layout="wide")

# Visiting Home means user is logged out until they choose a persona/user
st.session_state["authenticated"] = False

SideBarLinks(show_home=True)


# --------------------------------------------------
# Mock users by persona
# --------------------------------------------------
PERSONA_OPTIONS = {
    "student": {
        "label": "Student",
        "title": "Sarah Johnson",
        "description": "Check crowd levels, hours, predictions, favorites, and preferences.",
        "users": [
            {"user_id": 1, "name": "Sarah Johnson"},
            {"user_id": 5, "name": "Roy Smith"},
            {"user_id": 7, "name": "Sheryl Howard"},
            {"user_id": 8, "name": "Brandi Hansen"},
            {"user_id": 9, "name": "Nicole Navarro"},
        ],
        "home_page": "pages/00_Student_Home.py",
    },
    "campus_operations_manager": {
        "label": "Campus Operations Manager",
        "title": "Mark Preston",
        "description": "Monitor facilities, compare locations, edit hours, and review dashboards.",
        "users": [
            {"user_id": 2, "name": "Mark Preston"},
            {"user_id": 6, "name": "Melissa Daniels"},
            {"user_id": 22, "name": "Lisa Gonzalez"},
            {"user_id": 23, "name": "Kenneth Jacobs"},
            {"user_id": 24, "name": "Anna Ford"},
        ],
        "home_page": "pages/10_Operations_Manager_Home.py",
    },
    "data_analyst": {
        "label": "Data Analyst",
        "title": "Jason Morrison",
        "description": "Explore historical and predicted data, dashboards, categories, and sources.",
        "users": [
            {"user_id": 3, "name": "Jason Morrison"},
            {"user_id": 12, "name": "Erin Gonzalez"},
            {"user_id": 21, "name": "Patricia Church"},
            {"user_id": 34, "name": "Spencer Wade"},
            {"user_id": 37, "name": "Courtney Jenkins"},
        ],
        "home_page": "pages/20_Data_Analyst_Home.py",
    },
    "system_administrator": {
        "label": "System Administrator",
        "title": "Kevin Brooks",
        "description": "Track pipeline runs, inspect logs, and manage system configuration.",
        "users": [
            {"user_id": 4, "name": "Kevin Brooks"},
            {"user_id": 11, "name": "Fred Johnson"},
            {"user_id": 15, "name": "Jerry Harris"},
        ],
        "home_page": "pages/30_System_Admin_Home.py",
    },
}


# --------------------------------------------------
# Page content
# --------------------------------------------------
logger.info("Loading CampusFlow Home page")

st.title("CampusFlow")
st.write("### Select a persona and mock user to log in")
st.write(
    "Choose one of the project personas below. Each dropdown is populated "
    "with mock users from that role, and the button simulates logging in."
)

col1, col2 = st.columns(2)

persona_items = list(PERSONA_OPTIONS.items())
column_cycle = [col1, col2, col1, col2]

for (role_key, config), col in zip(persona_items, column_cycle):
    with col:
        st.subheader(config["label"])
        st.caption(config["description"])

        display_options = {
            f"{user['name']} (User ID: {user['user_id']})": user
            for user in config["users"]
        }

        selected_label = st.selectbox(
            f"Choose a {config['label']} user",
            options=list(display_options.keys()),
            key=f"select_{role_key}",
        )

        selected_user = display_options[selected_label]
        first_name = selected_user["name"].split()[0]

        if st.button(
            f"Log in as {first_name}",
            type="primary",
            use_container_width=True,
            key=f"login_{role_key}",
        ):
            st.session_state["authenticated"] = True
            st.session_state["role"] = role_key
            st.session_state["user_id"] = selected_user["user_id"]
            st.session_state["first_name"] = first_name
            st.session_state["full_name"] = selected_user["name"]

            logger.info(
                "Mock login as %s (user_id=%s, role=%s)",
                selected_user["name"],
                selected_user["user_id"],
                role_key,
            )
            st.switch_page(config["home_page"])

st.divider()
st.info(
    "This project uses mock login only. No password or account creation is required."
)
