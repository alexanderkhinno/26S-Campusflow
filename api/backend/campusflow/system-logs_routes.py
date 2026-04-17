from db_utils import (
    commit,
    error_response,
    exists,
    get_cursor,
    success_response,
)
from flask import Blueprint, current_app, jsonify, request
from mysql.connector import Error

system_logs_routes = Blueprint("system_logs_routes", __name__)


# -------------------------------------------------------------------
# GET /system-logs
# Retrieve logs with optional filters
# -------------------------------------------------------------------


@system_logs_routes.route("/system-logs", methods=["GET"])
def get_system_logs():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /system-logs")

        level = request.args.get("level")
        component = request.args.get("component")
        start = request.args.get("start")
        end = request.args.get("end")

        query = """
            SELECT
                log_id,
                user_id,
                log_level,
                component_name,
                log_message,
                created_at
            FROM system_logs
            WHERE 1=1
        """
        params = []

        if level:
            query += " AND log_level = %s"
            params.append(level)

        if component:
            query += " AND component_name = %s"
            params.append(component)

        if start:
            query += " AND created_at >= %s"
            params.append(start)

        if end:
            query += " AND created_at <= %s"
            params.append(end)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# DELETE /system-logs/{logID}
# Delete a log record
# -------------------------------------------------------------------


@system_logs_routes.route("/system-logs/<int:log_id>", methods=["DELETE"])
def delete_system_log(log_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"DELETE /system-logs/{log_id}")

        if not exists("system_logs", "log_id", log_id):
            return error_response("System log not found.", 404)

        cursor.execute("DELETE FROM system_logs WHERE log_id = %s", (log_id,))
        commit()

        return success_response("System log deleted successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
