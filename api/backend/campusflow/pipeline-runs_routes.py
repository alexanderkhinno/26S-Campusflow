from db_utils import (
    commit,
    error_response,
    exists,
    get_cursor,
    require_json,
    success_response,
)
from flask import Blueprint, current_app, jsonify
from mysql.connector import Error

pipeline_runs_routes = Blueprint("pipeline_runs_routes", __name__)


# -------------------------------------------------------------------
# GET /pipeline-runs
# Retrieve pipeline runs with optional filters
# -------------------------------------------------------------------


@pipeline_runs_routes.route("/pipeline-runs", methods=["GET"])
def get_pipeline_runs():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /pipeline-runs")

        from flask import request

        run_status = request.args.get("run_status")
        data_source_id = request.args.get("data_source_id")

        query = """
            SELECT
                pr.pipeline_run_id,
                pr.data_source_id,
                ds.source_name,
                pr.run_started_at,
                pr.run_finished_at,
                pr.run_status,
                pr.rows_processed,
                pr.error_message,
                pr.initiated_by_user_id
            FROM pipeline_runs pr
            JOIN data_sources ds
                ON pr.data_source_id = ds.data_source_id
            WHERE 1=1
        """
        params = []

        if run_status:
            query += " AND pr.run_status = %s"
            params.append(run_status)

        if data_source_id:
            query += " AND pr.data_source_id = %s"
            params.append(data_source_id)

        query += " ORDER BY pr.run_started_at DESC"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# POST /pipeline-runs
# Start or register a new pipeline run
# -------------------------------------------------------------------


@pipeline_runs_routes.route("/pipeline-runs", methods=["POST"])
def create_pipeline_run():
    cursor = get_cursor()
    try:
        current_app.logger.info("POST /pipeline-runs")

        data, err = require_json()
        if err:
            return err

        if "data_source_id" not in data:
            return error_response("Missing required field: data_source_id")

        cursor.execute(
            """
            INSERT INTO pipeline_runs (
                data_source_id,
                run_started_at,
                run_finished_at,
                run_status,
                rows_processed,
                error_message,
                initiated_by_user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["data_source_id"],
                data.get("run_started_at"),
                data.get("run_finished_at"),
                data.get("run_status", "running"),
                data.get("rows_processed", 0),
                data.get("error_message"),
                data.get("initiated_by_user_id"),
            ),
        )
        commit()

        return success_response(
            "Pipeline run created successfully.",
            status=201,
            pipeline_run_id=cursor.lastrowid,
        )

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# PUT /pipeline-runs/{pipelineRunID}
# Update a pipeline run's fields
# -------------------------------------------------------------------


@pipeline_runs_routes.route("/pipeline-runs/<int:pipeline_run_id>", methods=["PUT"])
def update_pipeline_run(pipeline_run_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"PUT /pipeline-runs/{pipeline_run_id}")

        if not exists("pipeline_runs", "pipeline_run_id", pipeline_run_id):
            return error_response("Pipeline run not found.", 404)

        data, err = require_json()
        if err:
            return err

        allowed_fields = {
            "run_started_at": "run_started_at = %s",
            "run_finished_at": "run_finished_at = %s",
            "run_status": "run_status = %s",
            "rows_processed": "rows_processed = %s",
            "error_message": "error_message = %s",
            "initiated_by_user_id": "initiated_by_user_id = %s",
        }

        update_fields = []
        params = []

        for field, clause in allowed_fields.items():
            if field in data:
                update_fields.append(clause)
                params.append(data[field])

        if not update_fields:
            return error_response("No valid pipeline run fields provided.")

        params.append(pipeline_run_id)

        query = f"""
            UPDATE pipeline_runs
            SET {", ".join(update_fields)}
            WHERE pipeline_run_id = %s
        """
        cursor.execute(query, params)
        commit()

        return success_response("Pipeline run updated successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
