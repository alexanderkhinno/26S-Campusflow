import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.stop()

st.title("Feature Coming Soon 🚧")
st.write("This page is not part of the core demo.")

if st.button("Back to Home"):
    role = st.session_state.get("role")

    if role == "student":
        st.switch_page("pages/00_Student_Home.py")
    elif role == "campus_operations_manager":
        st.switch_page("pages/10_Operations_Manager_Home.py")
    elif role == "data_analyst":
        st.switch_page("pages/20_Data_Analyst_Home.py")
    elif role == "system_administrator":
        st.switch_page("pages/30_System_Admin_Home.py")
