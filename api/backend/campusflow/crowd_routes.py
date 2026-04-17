from db_utils import (
    commit,
    error_response,
    exists,
    get_cursor,
    parse_bool,
    success_response,
)
from flask import Blueprint, current_app, jsonify, request
from mysql.connector import Error

crowd_routes = Blueprint("crowd_routes", __name__)


# -------------------------------------------------------------------
# 1. GET /locations/{locationId}/crowd/current
# -------------------------------------------------------------------


@crowd_routes.route("/locations/<int:location_id>/crowd/current", methods=["GET"])
def get_location_current_crowd(location_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"GET /locations/{location_id}/crowd/current")

        if not exists("locations", "location_id", location_id):
            return error_response("Location not found.", 404)

        cursor.execute(
            """
            SELECT
                cm.measurements_id,
                cm.location_id,
                cm.measured_at,
                cm.crowd_count,
                cm.crowd_level,
                cm.occupancy_percent
            FROM crowd_measurements cm
            WHERE cm.location_id = %s
              AND cm.is_valid = 1
            ORDER BY cm.measured_at DESC
            LIMIT 1
        """,
            (location_id,),
        )

        row = cursor.fetchone()
        if not row:
            return error_response("No current crowd data found.", 404)

        return jsonify(row), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# 2. GET /crowd/current
# -------------------------------------------------------------------


@crowd_routes.route("/crowd/current", methods=["GET"])
def get_all_current_crowd():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /crowd/current")

        cursor.execute(
            """
            SELECT
                l.location_id,
                l.location_name,
                cm.crowd_count,
                cm.crowd_level,
                cm.occupancy_percent,
                cm.measured_at
            FROM locations l
            JOIN (
                SELECT cm1.*
                FROM crowd_measurements cm1
                JOIN (
                    SELECT location_id, MAX(measured_at) AS latest
                    FROM crowd_measurements
                    WHERE is_valid = 1
                    GROUP BY location_id
                ) latest_cm
                ON cm1.location_id = latest_cm.location_id
                AND cm1.measured_at = latest_cm.latest
            ) cm ON l.location_id = cm.location_id
            WHERE l.status = 'active'
            ORDER BY l.location_name
        """
        )

        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# 3. GET /crowd/history
# -------------------------------------------------------------------


@crowd_routes.route("/crowd/history", methods=["GET"])
def get_crowd_history():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /crowd/history")

        location_id = request.args.get("location_id")
        start = request.args.get("start")
        end = request.args.get("end")
        level = request.args.get("level")
        source = request.args.get("source")
        is_valid = request.args.get("is_valid")

        query = """
            SELECT
                cm.measurements_id,
                cm.location_id,
                cm.measured_at,
                cm.crowd_count,
                cm.crowd_level,
                cm.occupancy_percent,
                cm.source_label,
                cm.is_valid
            FROM crowd_measurements cm
            WHERE 1=1
        """
        params = []

        if location_id:
            query += " AND cm.location_id = %s"
            params.append(location_id)
        if start:
            query += " AND cm.measured_at >= %s"
            params.append(start)
        if end:
            query += " AND cm.measured_at <= %s"
            params.append(end)
        if level:
            query += " AND cm.crowd_level = %s"
            params.append(level)
        if source:
            query += " AND cm.source_label = %s"
            params.append(source)
        if is_valid is not None:
            parsed = parse_bool(is_valid)
            if parsed is None:
                return error_response("Invalid is_valid value.")
            query += " AND cm.is_valid = %s"
            params.append(parsed)

        query += " ORDER BY cm.measured_at DESC"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# 4. GET /crowd/predictions
# -------------------------------------------------------------------


@crowd_routes.route("/crowd/predictions", methods=["GET"])
def get_crowd_predictions():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /crowd/predictions")

        location_id = request.args.get("location_id")
        start = request.args.get("start")
        end = request.args.get("end")

        query = """
            SELECT
                prediction_id,
                location_id,
                predicted_for,
                predicted_count,
                predicted_level,
                confidence_score
            FROM crowd_predictions
            WHERE 1=1
        """
        params = []

        if location_id:
            query += " AND location_id = %s"
            params.append(location_id)
        if start:
            query += " AND predicted_for >= %s"
            params.append(start)
        if end:
            query += " AND predicted_for <= %s"
            params.append(end)

        query += " ORDER BY predicted_for"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# 5. GET /locations/{locationID}/predictions
# -------------------------------------------------------------------


@crowd_routes.route("/locations/<int:location_id>/predictions", methods=["GET"])
def get_location_predictions(location_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"GET /locations/{location_id}/predictions")

        if not exists("locations", "location_id", location_id):
            return error_response("Location not found.", 404)

        cursor.execute(
            """
            SELECT
                prediction_id,
                location_id,
                predicted_for,
                predicted_count,
                predicted_level,
                confidence_score
            FROM crowd_predictions
            WHERE location_id = %s
            ORDER BY predicted_for
        """,
            (location_id,),
        )

        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# 6. DELETE /crowd/measurements/{measurementsID}
# -------------------------------------------------------------------


@crowd_routes.route("/crowd/measurements/<int:measurements_id>", methods=["DELETE"])
def delete_measurements_matrix(measurements_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"DELETE /crowd/measurements/{measurements_id}")

        if not exists("crowd_measurements", "measurements_id", measurements_id):
            return error_response("Measurements not found.", 404)

        cursor.execute(
            """
            UPDATE crowd_measurements
            SET is_valid = 0
            WHERE measurements_id = %s
        """,
            (measurements_id,),
        )
        commit()

        return success_response("Measurements marked invalid.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
