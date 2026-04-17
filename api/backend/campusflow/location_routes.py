from db_utils import (
    commit,
    error_response,
    exists,
    get_cursor,
    parse_bool,
    require_json,
    success_response,
)
from flask import Blueprint, current_app, jsonify, request
from mysql.connector import Error

location_routes = Blueprint("location_routes", __name__)


# -------------------------------------------------------------------
# GET /locations
# Retrieve locations with optional filters
# -------------------------------------------------------------------


@location_routes.route("/locations", methods=["GET"])
def get_locations():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /locations")

        name = request.args.get("name")
        location_type = request.args.get("type")
        zone = request.args.get("zone")
        open_flag = request.args.get("open")
        status = request.args.get("status")

        query = """
            SELECT
                l.location_id,
                l.location_name,
                l.building_name,
                l.campus_zone,
                l.capacity,
                l.status,
                l.current_open_flag,
                lt.location_type_id,
                lt.type_name
            FROM locations l
            JOIN location_types lt
                ON l.location_type_id = lt.location_type_id
            WHERE 1=1
        """
        params = []

        if name:
            query += " AND (l.location_name LIKE %s OR l.building_name LIKE %s)"
            like = f"%{name}%"
            params.extend([like, like])

        if location_type:
            query += " AND lt.type_name = %s"
            params.append(location_type)

        if zone:
            query += " AND l.campus_zone = %s"
            params.append(zone)

        if open_flag is not None:
            parsed = parse_bool(open_flag)
            if parsed is None:
                return error_response("Invalid value for 'open'.")
            query += " AND l.current_open_flag = %s"
            params.append(parsed)

        if status:
            query += " AND l.status = %s"
            params.append(status)

        query += " ORDER BY l.location_name"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# POST /locations/{locationID}
# Create a new location (matrix requirement)
# -------------------------------------------------------------------


@location_routes.route("/locations/<int:location_id>", methods=["POST"])
def create_location(location_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"POST /locations/{location_id}")

        data, err = require_json()
        if err:
            return err

        required_fields = [
            "location_type_id",
            "location_name",
            "building_name",
            "capacity",
        ]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}")

        cursor.execute(
            """
            INSERT INTO locations (
                location_type_id,
                location_name,
                building_name,
                campus_zone,
                capacity,
                status,
                current_open_flag,
                added_by_user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["location_type_id"],
                data["location_name"],
                data["building_name"],
                data.get("campus_zone"),
                data["capacity"],
                data.get("status", "active"),
                data.get("current_open_flag", 1),
                data.get("added_by_user_id"),
            ),
        )
        commit()

        return success_response(
            "Location created successfully.",
            status=201,
            location_id=cursor.lastrowid,
        )

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# DELETE /locations/{locationID}
# Soft delete a location
# -------------------------------------------------------------------


@location_routes.route("/locations/<int:location_id>", methods=["DELETE"])
def delete_location(location_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"DELETE /locations/{location_id}")

        if not exists("locations", "location_id", location_id):
            return error_response("Location not found.", 404)

        cursor.execute(
            """
            UPDATE locations
            SET status = 'inactive',
                current_open_flag = 0
            WHERE location_id = %s
            """,
            (location_id,),
        )
        commit()

        return success_response("Location marked inactive successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
