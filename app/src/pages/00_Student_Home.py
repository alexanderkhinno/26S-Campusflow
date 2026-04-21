##################################################
# Student Persona Home Page (Sarah Johnson)
##################################################

import streamlit as st
from modules.nav import SideBarLinks

# Page config
st.set_page_config(page_title="Student Home", layout="wide")

# Sidebar navigation
SideBarLinks()

# Authentication check
if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

# Page content
st.title(f"Welcome, {st.session_state.get('first_name', 'Student')} 👋")

st.write("### Student Dashboard")
st.write(
    "Use CampusFlow to check crowd levels, find open locations, "
    "and manage your favorite study spots."
)

st.divider()

# Quick actions section
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("View Current Crowd Levels", use_container_width=True):
        st.switch_page("pages/01_Student_Crowd.py")

with col2:
    if st.button("Check Location Hours", use_container_width=True):
        st.switch_page("pages/02_Student_Hours.py")

with col3:
    if st.button("View Predictions", use_container_width=True):
        st.switch_page("pages/03_Student_Predictions.py")

st.divider()

# Favorites / preferences shortcuts
st.subheader("Your Tools")

col4, col5 = st.columns(2)

with col4:
    if st.button("Manage Favorites", use_container_width=True):
        st.switch_page("pages/04_Student_Favorites.py")

with col5:
    if st.button("Update Preferences", use_container_width=True):
        st.switch_page("pages/05_Student_Preferences.py")

st.divider()

st.info(
    "This is your personalized student dashboard. Select an option above to get started."
)
