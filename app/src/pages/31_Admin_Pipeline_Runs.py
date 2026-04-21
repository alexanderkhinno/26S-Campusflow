##################################################
# System Admin Feature Page: Pipeline Runs
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

st.set_page_config(page_title="Admin Pipeline Runs", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.warning("Please log in from the Home page.")
    st.stop()

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")
USER_ID = st.session_state.get("user_id")


def get_pipeline_runs(params=None):
    url = f"{API_BASE_URL}/pipeline-runs"
    response = requests.get(url, params=params or {}, timeout=10)
    response.raise_for_status()
    return response.json()


# Used to populate valid data_source_id values when creating runs.
def get_data_categories():
    url = f"{API_BASE_URL}/data-categories"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def create_pipeline_run(payload):
    url = f"{API_BASE_URL}/pipeline-runs"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def update_pipeline_run(pipeline_run_id, payload):
    url = f"{API_BASE_URL}/pipeline-runs/{pipeline_run_id}"
    response = requests.put(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Pipeline Runs ⚙️")
st.write(
    f"Welcome, **{st.session_state.get('first_name', 'Admin')}**. "
    "Monitor recent pipeline activity, register new runs, and update run statuses."
)

if not USER_ID:
    st.error(
        "No user is selected in the session. Please return to Home and log in again."
    )
    st.stop()

try:
    # Main filter controls for GET /pipeline-runs
    st.subheader("Filter Pipeline Runs")
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        selected_status = st.selectbox(
            "Run Status",
            ["All", "running", "completed", "failed"],
            key="admin_pipeline_status_filter",
        )
    with filter_col2:
        data_source_filter = st.text_input(
            "Data Source ID (optional)",
            value="",
            key="admin_pipeline_source_filter",
        )

    query_params = {}
    if selected_status != "All":
        query_params["run_status"] = selected_status
    if data_source_filter.strip():
        query_params["data_source_id"] = data_source_filter.strip()

    runs = get_pipeline_runs(query_params)
    runs_df = pd.DataFrame(runs) if runs else pd.DataFrame()

    st.divider()
    st.subheader("Current Pipeline Runs")

    if runs_df.empty:
        st.info("No pipeline runs matched the selected filters.")
    else:
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Runs Displayed", len(runs_df))
        with metric_col2:
            if "run_status" in runs_df.columns:
                completed_count = int((runs_df["run_status"] == "completed").sum())
                st.metric("Completed Runs", completed_count)
        with metric_col3:
            if "run_status" in runs_df.columns:
                failed_count = int((runs_df["run_status"] == "failed").sum())
                st.metric("Failed Runs", failed_count)

        display_cols = [
            col
            for col in [
                "pipeline_run_id",
                "data_source_id",
                "source_name",
                "run_started_at",
                "run_finished_at",
                "run_status",
                "rows_processed",
                "error_message",
                "initiated_by_user_id",
            ]
            if col in runs_df.columns
        ]
        st.dataframe(
            runs_df[display_cols],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Register a New Pipeline Run")

        with st.form("create_pipeline_run_form"):
            data_source_id = st.number_input(
                "Data Source ID",
                min_value=1,
                value=1,
                step=1,
            )
            run_status = st.selectbox(
                "Initial Run Status",
                ["running", "completed", "failed"],
                key="admin_create_pipeline_status",
            )
            rows_processed = st.number_input(
                "Rows Processed",
                min_value=0,
                value=0,
                step=1,
            )
            error_message = st.text_input("Error Message (optional)")

            submitted_create = st.form_submit_button("Create Pipeline Run")

            if submitted_create:
                try:
                    payload = {
                        "data_source_id": int(data_source_id),
                        "run_status": run_status,
                        "rows_processed": int(rows_processed),
                        "error_message": error_message
                        if error_message.strip()
                        else None,
                        "initiated_by_user_id": USER_ID,
                    }
                    result = create_pipeline_run(payload)
                    st.success(
                        f"{result.get('message', 'Pipeline run created successfully.')} "
                        f"New Run ID: {result.get('pipeline_run_id', 'N/A')}"
                    )
                    st.session_state["latest_pipeline_run_id"] = result.get(
                        "pipeline_run_id"
                    )
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    logger.error("Error creating pipeline run: %s", e)
                    error_text = "Could not create pipeline run."
                    if e.response is not None:
                        try:
                            error_text = e.response.json().get("error", error_text)
                        except Exception:
                            pass
                    st.error(error_text)

    with right_col:
        st.subheader("Update an Existing Pipeline Run")

        update_default_id = 1
        if not runs_df.empty and "pipeline_run_id" in runs_df.columns:
            update_default_id = int(runs_df.iloc[0]["pipeline_run_id"])
        elif st.session_state.get("latest_pipeline_run_id"):
            update_default_id = int(st.session_state["latest_pipeline_run_id"])

        with st.form("update_pipeline_run_form"):
            pipeline_run_id = st.number_input(
                "Pipeline Run ID",
                min_value=1,
                value=update_default_id,
                step=1,
            )
            updated_status = st.selectbox(
                "Updated Status",
                ["running", "completed", "failed"],
                key="admin_update_pipeline_status",
            )
            updated_rows_processed = st.number_input(
                "Updated Rows Processed",
                min_value=0,
                value=0,
                step=1,
            )
            updated_error_message = st.text_input("Updated Error Message (optional)")

            submitted_update = st.form_submit_button("Update Pipeline Run")

            if submitted_update:
                try:
                    payload = {
                        "run_status": updated_status,
                        "rows_processed": int(updated_rows_processed),
                        "error_message": (
                            updated_error_message
                            if updated_error_message.strip()
                            else None
                        ),
                        "initiated_by_user_id": USER_ID,
                    }
                    result = update_pipeline_run(int(pipeline_run_id), payload)
                    st.success(
                        result.get("message", "Pipeline run updated successfully.")
                    )
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    logger.error("Error updating pipeline run: %s", e)
                    error_text = "Could not update pipeline run."
                    if e.response is not None:
                        try:
                            error_text = e.response.json().get("error", error_text)
                        except Exception:
                            pass
                    st.error(error_text)

except requests.exceptions.RequestException as e:
    logger.error("API error on Admin Pipeline Runs page: %s", e)
    st.error(
        "Could not connect to the CampusFlow API. Please make sure the backend is running."
    )
except Exception as e:
    logger.error("Unexpected error on Admin Pipeline Runs page: %s", e)
    st.error("Something went wrong while loading pipeline runs.")

st.divider()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("Back to Admin Home", use_container_width=True):
        st.switch_page("pages/30_System_Admin_Home.py")
with nav_col2:
    if st.button("View System Logs", use_container_width=True):
        st.switch_page("pages/32_Admin_System_Logs.py")
with nav_col3:
    if st.button("View System Configs", use_container_width=True):
        st.switch_page("pages/33_Admin_System_Configs.py")
