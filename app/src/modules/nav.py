# CampusFlow sidebar navigation

import streamlit as st

# ---- General ----------------------------------------------------------------


def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/99_About.py", label="About", icon="🧠")


# ---- Role: student -----------------------------------------------------------


def student_home_nav():
    st.sidebar.page_link("pages/00_Student_Home.py", label="Student Home", icon="🎓")


def student_crowd_nav():
    st.sidebar.page_link("pages/01_Student_Crowd.py", label="Current Crowd", icon="📊")


def student_hours_nav():
    st.sidebar.page_link("pages/02_Student_Hours.py", label="Location Hours", icon="⏰")


def student_predictions_nav():
    st.sidebar.page_link(
        "pages/03_Student_Predictions.py", label="Predictions", icon="📈"
    )


def student_favorites_nav():
    st.sidebar.page_link("pages/04_Student_Favorites.py", label="Favorites", icon="⭐")


def student_preferences_nav():
    st.sidebar.page_link(
        "pages/05_Student_Preferences.py", label="Preferences", icon="⚙️"
    )


# ---- Role: operations manager ------------------------------------------------


def ops_home_nav():
    st.sidebar.page_link(
        "pages/10_Operations_Manager_Home.py", label="Operations Home", icon="🏢"
    )


def ops_current_crowd_nav():
    st.sidebar.page_link(
        "pages/11_Operations_Current_Crowd.py", label="Current Crowd", icon="📊"
    )


def ops_history_nav():
    st.sidebar.page_link(
        "pages/12_Operations_Crowd_History.py", label="Crowd History", icon="📉"
    )


def ops_predictions_nav():
    st.sidebar.page_link(
        "pages/13_Operations_Predictions.py", label="Predictions", icon="📈"
    )


def ops_locations_nav():
    st.sidebar.page_link(
        "pages/14_Operations_Locations.py", label="Locations", icon="📍"
    )


def ops_hours_nav():
    st.sidebar.page_link("pages/15_Operations_Hours.py", label="Edit Hours", icon="⏰")


def ops_dashboards_nav():
    st.sidebar.page_link(
        "pages/16_Operations_Dashboards.py", label="Dashboards", icon="📋"
    )


# ---- Role: data analyst ------------------------------------------------------


def analyst_home_nav():
    st.sidebar.page_link(
        "pages/20_Data_Analyst_Home.py", label="Analyst Home", icon="📊"
    )


def analyst_history_nav():
    st.sidebar.page_link(
        "pages/21_Analyst_Crowd_History.py", label="Crowd History", icon="📉"
    )


def analyst_predictions_nav():
    st.sidebar.page_link(
        "pages/22_Analyst_Predictions.py", label="Predictions", icon="📈"
    )


def analyst_locations_nav():
    st.sidebar.page_link("pages/23_Analyst_Locations.py", label="Locations", icon="📍")


def analyst_categories_nav():
    st.sidebar.page_link(
        "pages/24_Analyst_Data_Categories.py", label="Data Categories", icon="🗂️"
    )


def analyst_sources_nav():
    st.sidebar.page_link(
        "pages/25_Analyst_Data_Sources.py", label="Data Sources", icon="🔗"
    )


def analyst_dashboards_nav():
    st.sidebar.page_link(
        "pages/26_Analyst_Dashboards.py", label="Dashboards", icon="📋"
    )


# ---- Role: system administrator ---------------------------------------------


def admin_home_nav():
    st.sidebar.page_link("pages/30_System_Admin_Home.py", label="Admin Home", icon="🖥️")


def admin_pipeline_nav():
    st.sidebar.page_link(
        "pages/31_Admin_Pipeline_Runs.py", label="Pipeline Runs", icon="⚙️"
    )


def admin_logs_nav():
    st.sidebar.page_link(
        "pages/32_Admin_System_Logs.py", label="System Logs", icon="📜"
    )


def admin_configs_nav():
    st.sidebar.page_link("pages/33_Admin_System_Configs.py", label="Configs", icon="🛠️")


def admin_cleanup_nav():
    st.sidebar.page_link(
        "pages/34_Admin_Cleanup_Logs.py", label="Cleanup Logs", icon="🧹"
    )


def admin_integrity_nav():
    st.sidebar.page_link(
        "pages/35_Admin_Data_Integrity.py", label="Data Integrity", icon="🔍"
    )


# ---- Sidebar assembly --------------------------------------------------------


def SideBarLinks(show_home=False):
    """Render sidebar based on the authenticated user's role."""

    st.sidebar.image("assets/logo.png", width=150)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state.get("authenticated"):
        role = st.session_state.get("role")

        if role == "student":
            student_home_nav()
            student_crowd_nav()
            student_hours_nav()
            student_predictions_nav()
            student_favorites_nav()
            student_preferences_nav()

        elif role == "campus_operations_manager":
            ops_home_nav()
            ops_current_crowd_nav()
            ops_history_nav()
            ops_predictions_nav()
            ops_locations_nav()
            ops_hours_nav()
            ops_dashboards_nav()

        elif role == "data_analyst":
            analyst_home_nav()
            analyst_history_nav()
            analyst_predictions_nav()
            analyst_locations_nav()
            analyst_categories_nav()
            analyst_sources_nav()
            analyst_dashboards_nav()

        elif role == "system_administrator":
            admin_home_nav()
            admin_pipeline_nav()
            admin_logs_nav()
            admin_configs_nav()
            admin_cleanup_nav()
            admin_integrity_nav()

    about_page_nav()

    if st.session_state.get("authenticated"):
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.switch_page("Home.py")
