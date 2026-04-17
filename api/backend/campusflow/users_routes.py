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

users_routes = Blueprint("users_routes", __name__)


# -------------------------------------------------------------------
# GET /users/{userID}/favorites
# Retrieve user's favorite locations
# -------------------------------------------------------------------


@users_routes.route("/users/<int:user_id>/favorites", methods=["GET"])
def get_user_favorites(user_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"GET /users/{user_id}/favorites")

        if not exists("users", "user_id", user_id):
            return error_response("User not found.", 404)

        cursor.execute(
            """
            SELECT
                fl.user_id,
                fl.location_id,
                fl.saved_at,
                l.location_name,
                l.building_name,
                l.campus_zone,
                l.status,
                l.current_open_flag
            FROM favorite_locations fl
            JOIN locations l
                ON fl.location_id = l.location_id
            WHERE fl.user_id = %s
            ORDER BY fl.saved_at DESC
            """,
            (user_id,),
        )

        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# POST /users/{userID}/favorites
# Add a favorite location
# -------------------------------------------------------------------


@users_routes.route("/users/<int:user_id>/favorites", methods=["POST"])
def add_user_favorite(user_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"POST /users/{user_id}/favorites")

        if not exists("users", "user_id", user_id):
            return error_response("User not found.", 404)

        data, err = require_json()
        if err:
            return err

        location_id = data.get("location_id")
        if not location_id:
            return error_response("location_id is required.")

        if not exists("locations", "location_id", location_id):
            return error_response("Location not found.", 404)

        cursor.execute(
            """
            INSERT INTO favorite_locations (user_id, location_id)
            VALUES (%s, %s)
            """,
            (user_id, location_id),
        )
        commit()

        return success_response("Favorite location added successfully.", 201)

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# DELETE /users/{userID}/favorites/{locationID}
# Remove a favorite location
# -------------------------------------------------------------------


@users_routes.route(
    "/users/<int:user_id>/favorites/<int:location_id>", methods=["DELETE"]
)
def delete_user_favorite(user_id, location_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"DELETE /users/{user_id}/favorites/{location_id}")

        cursor.execute(
            """
            DELETE FROM favorite_locations
            WHERE user_id = %s AND location_id = %s
            """,
            (user_id, location_id),
        )

        if cursor.rowcount == 0:
            return error_response("Favorite location not found.", 404)

        commit()
        return success_response("Favorite location removed successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# GET /users/{userID}/preferences
# Retrieve user preferences
# -------------------------------------------------------------------


@users_routes.route("/users/<int:user_id>/preferences", methods=["GET"])
def get_user_preferences(user_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"GET /users/{user_id}/preferences")

        if not exists("users", "user_id", user_id):
            return error_response("User not found.", 404)

        cursor.execute(
            """
            SELECT
                up.preference_id,
                up.user_id,
                up.preferred_location_type_id,
                lt.type_name AS preferred_location_type,
                up.notification_opt_in,
                up.max_preferred_crowd_percent,
                up.updated_at
            FROM user_preferences up
            LEFT JOIN location_types lt
                ON up.preferred_location_type_id = lt.location_type_id
            WHERE up.user_id = %s
            """,
            (user_id,),
        )

        row = cursor.fetchone()
        if not row:
            return error_response("Preferences not found.", 404)

        return jsonify(row), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# PUT /users/{userID}/preferences
# Update user preferences
# -------------------------------------------------------------------


@users_routes.route("/users/<int:user_id>/preferences", methods=["PUT"])
def update_user_preferences(user_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"PUT /users/{user_id}/preferences")

        if not exists("users", "user_id", user_id):
            return error_response("User not found.", 404)

        data, err = require_json()
        if err:
            return err

        allowed_fields = {
            "preferred_location_type_id": "preferred_location_type_id = %s",
            "notification_opt_in": "notification_opt_in = %s",
            "max_preferred_crowd_percent": "max_preferred_crowd_percent = %s",
        }

        update_fields = []
        params = []

        for field, clause in allowed_fields.items():
            if field in data:
                update_fields.append(clause)
                params.append(data[field])

        if not update_fields:
            return error_response("No valid preference fields provided.")

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)

        query = f"""
            UPDATE user_preferences
            SET {", ".join(update_fields)}
            WHERE user_id = %s
        """

        cursor.execute(query, params)

        if cursor.rowcount == 0:
            return error_response("Preferences not found.", 404)

        commit()
        return success_response("User preferences updated successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
