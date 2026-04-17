from db_utils import (
    commit,
    error_response,
    exists,
    get_cursor,
    require_json,
    success_response,
)
from flask import Blueprint, current_app, jsonify, request
from mysql.connector import Error

dashboards_routes = Blueprint("dashboards_routes", __name__)


# -------------------------------------------------------------------
# GET /dashboards
# Retrieve available dashboards (optional filters)
# -------------------------------------------------------------------


@dashboards_routes.route("/dashboards", methods=["GET"])
def get_dashboards():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /dashboards")

        user_id = request.args.get("user_id")
        dashboard_type = request.args.get("dashboard_type")

        query = """
            SELECT
                d.dashboard_id,
                d.user_id,
                d.dashboard_name,
                d.dashboard_type,
                d.created_at,
                d.updated_at
            FROM dashboards d
            WHERE 1=1
        """
        params = []

        if user_id:
            query += " AND d.user_id = %s"
            params.append(user_id)

        if dashboard_type:
            query += " AND d.dashboard_type = %s"
            params.append(dashboard_type)

        query += " ORDER BY d.dashboard_name"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# POST /dashboards
# Create a new dashboard
# -------------------------------------------------------------------


@dashboards_routes.route("/dashboards", methods=["POST"])
def create_dashboard():
    cursor = get_cursor()
    try:
        current_app.logger.info("POST /dashboards")

        data, err = require_json()
        if err:
            return err

        required_fields = ["user_id", "dashboard_name", "dashboard_type"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}")

        cursor.execute(
            """
            INSERT INTO dashboards (user_id, dashboard_name, dashboard_type)
            VALUES (%s, %s, %s)
            """,
            (data["user_id"], data["dashboard_name"], data["dashboard_type"]),
        )
        commit()

        return success_response(
            "Dashboard created successfully.",
            status=201,
            dashboard_id=cursor.lastrowid,
        )

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# GET /dashboards/{dashboardID}/widgets
# Retrieve widgets for a dashboard
# -------------------------------------------------------------------


@dashboards_routes.route("/dashboards/<int:dashboard_id>/widgets", methods=["GET"])
def get_dashboard_widgets(dashboard_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"GET /dashboards/{dashboard_id}/widgets")

        if not exists("dashboards", "dashboard_id", dashboard_id):
            return error_response("Dashboard not found.", 404)

        cursor.execute(
            """
            SELECT
                widget_id,
                dashboard_id,
                widget_name,
                widget_type,
                metric_name,
                x_position,
                y_position
            FROM dashboard_widgets
            WHERE dashboard_id = %s
            ORDER BY y_position, x_position, widget_id
            """,
            (dashboard_id,),
        )

        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# POST /dashboards/{dashboardID}/widgets
# Create a new widget for a dashboard
# -------------------------------------------------------------------


@dashboards_routes.route("/dashboards/<int:dashboard_id>/widgets", methods=["POST"])
def create_dashboard_widget(dashboard_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"POST /dashboards/{dashboard_id}/widgets")

        if not exists("dashboards", "dashboard_id", dashboard_id):
            return error_response("Dashboard not found.", 404)

        data, err = require_json()
        if err:
            return err

        required_fields = ["widget_name", "widget_type", "metric_name"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}")

        cursor.execute(
            """
            INSERT INTO dashboard_widgets (
                dashboard_id,
                widget_name,
                widget_type,
                metric_name,
                x_position,
                y_position
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                dashboard_id,
                data["widget_name"],
                data["widget_type"],
                data["metric_name"],
                data.get("x_position", 0),
                data.get("y_position", 0),
            ),
        )
        commit()

        return success_response(
            "Dashboard widget created successfully.",
            status=201,
            widget_id=cursor.lastrowid,
        )

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
