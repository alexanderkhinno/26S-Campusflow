from db_utils import (
    commit,
    error_response,
    exists,
    get_cursor,
    require_json,
    success_response,
)
from flask import Blueprint, current_app
from mysql.connector import Error

data_sources_routes = Blueprint("data_sources_routes", __name__)


# -------------------------------------------------------------------
# POST /data-sources
# Register a new data source in the system
# -------------------------------------------------------------------


@data_sources_routes.route("/data-sources", methods=["POST"])
def create_data_source():
    cursor = get_cursor()
    try:
        current_app.logger.info("POST /data-sources")

        data, err = require_json()
        if err:
            return err

        required_fields = ["source_name", "source_type", "refresh_interval_minutes"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}")

        cursor.execute(
            """
            INSERT INTO data_sources (
                source_name,
                source_type,
                refresh_interval_minutes,
                status,
                created_by_user_id
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["source_name"],
                data["source_type"],
                data["refresh_interval_minutes"],
                data.get("status", "active"),
                data.get("created_by_user_id"),
            ),
        )
        commit()

        return success_response(
            "Data source created successfully.",
            status=201,
            data_source_id=cursor.lastrowid,
        )

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# DELETE /data-sources/{dataSourceID}
# Soft delete a data source by marking it inactive
# -------------------------------------------------------------------


@data_sources_routes.route("/data-sources/<int:data_source_id>", methods=["DELETE"])
def delete_data_source(data_source_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"DELETE /data-sources/{data_source_id}")

        if not exists("data_sources", "data_source_id", data_source_id):
            return error_response("Data source not found.", 404)

        cursor.execute(
            """
            UPDATE data_sources
            SET status = 'inactive'
            WHERE data_source_id = %s
            """,
            (data_source_id,),
        )
        commit()

        return success_response("Data source marked inactive successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# POST /location-data-sources
# Map a data source to a location and category
# -------------------------------------------------------------------


@data_sources_routes.route("/location-data-sources", methods=["POST"])
def create_location_data_source():
    cursor = get_cursor()
    try:
        current_app.logger.info("POST /location-data-sources")

        data, err = require_json()
        if err:
            return err

        required_fields = ["location_id", "data_source_id", "category_id"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}")

        if not exists("locations", "location_id", data["location_id"]):
            return error_response("Location not found.", 404)

        if not exists("data_sources", "data_source_id", data["data_source_id"]):
            return error_response("Data source not found.", 404)

        if not exists("data_categories", "category_id", data["category_id"]):
            return error_response("Data category not found.", 404)

        cursor.execute(
            """
            INSERT INTO location_data_sources (location_id, data_source_id, category_id)
            VALUES (%s, %s, %s)
            """,
            (
                data["location_id"],
                data["data_source_id"],
                data["category_id"],
            ),
        )
        commit()

        return success_response(
            "Location-data-source mapping created successfully.",
            status=201,
        )

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
