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

data_categories_routes = Blueprint("data_categories_routes", __name__)


# -------------------------------------------------------------------
# GET /data-categories
# Retrieve all data categories
# -------------------------------------------------------------------


@data_categories_routes.route("/data-categories", methods=["GET"])
def get_data_categories():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /data-categories")

        cursor.execute(
            """
            SELECT
                category_id,
                category_name,
                description,
                active_flag,
                updated_at
            FROM data_categories
            ORDER BY category_name
            """
        )

        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# GET /data-categories/{categoryID}
# Retrieve one data category
# -------------------------------------------------------------------


@data_categories_routes.route("/data-categories/<int:category_id>", methods=["GET"])
def get_data_category(category_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"GET /data-categories/{category_id}")

        cursor.execute(
            """
            SELECT
                category_id,
                category_name,
                description,
                active_flag,
                updated_at
            FROM data_categories
            WHERE category_id = %s
            """,
            (category_id,),
        )

        row = cursor.fetchone()
        if not row:
            return error_response("Data category not found.", 404)

        return jsonify(row), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# PUT /data-categories/{categoryID}
# Update category name, description, or active flag
# -------------------------------------------------------------------


@data_categories_routes.route("/data-categories/<int:category_id>", methods=["PUT"])
def update_data_category(category_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"PUT /data-categories/{category_id}")

        if not exists("data_categories", "category_id", category_id):
            return error_response("Data category not found.", 404)

        data, err = require_json()
        if err:
            return err

        allowed_fields = {
            "category_name": "category_name = %s",
            "description": "description = %s",
            "active_flag": "active_flag = %s",
        }

        update_fields = []
        params = []

        for field, clause in allowed_fields.items():
            if field in data:
                update_fields.append(clause)
                params.append(data[field])

        if not update_fields:
            return error_response("No valid category fields provided.")

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(category_id)

        query = f"""
            UPDATE data_categories
            SET {", ".join(update_fields)}
            WHERE category_id = %s
        """
        cursor.execute(query, params)
        commit()

        return success_response("Data category updated successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
