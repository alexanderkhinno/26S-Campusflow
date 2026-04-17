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

system_configs_routes = Blueprint("system_configs_routes", __name__)


# -------------------------------------------------------------------
# GET /system-configs
# Retrieve all system configuration settings
# -------------------------------------------------------------------


@system_configs_routes.route("/system-configs", methods=["GET"])
def get_system_configs():
    cursor = get_cursor()
    try:
        current_app.logger.info("GET /system-configs")

        cursor.execute(
            """
            SELECT
                config_id,
                config_key,
                config_value,
                config_description,
                updated_by_user_id,
                updated_at
            FROM system_configs
            ORDER BY config_key
            """
        )

        return jsonify(cursor.fetchall()), 200

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()


# -------------------------------------------------------------------
# PUT /system-configs/{configID}
# Update a configuration value
# -------------------------------------------------------------------


@system_configs_routes.route("/system-configs/<int:config_id>", methods=["PUT"])
def update_system_config(config_id):
    cursor = get_cursor()
    try:
        current_app.logger.info(f"PUT /system-configs/{config_id}")

        if not exists("system_configs", "config_id", config_id):
            return error_response("System config not found.", 404)

        data, err = require_json()
        if err:
            return err

        allowed_fields = {
            "config_key": "config_key = %s",
            "config_value": "config_value = %s",
            "config_description": "config_description = %s",
            "updated_by_user_id": "updated_by_user_id = %s",
        }

        update_fields = []
        params = []

        for field, clause in allowed_fields.items():
            if field in data:
                update_fields.append(clause)
                params.append(data[field])

        if not update_fields:
            return error_response("No valid config fields provided.")

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(config_id)

        query = f"""
            UPDATE system_configs
            SET {", ".join(update_fields)}
            WHERE config_id = %s
        """

        cursor.execute(query, params)
        commit()

        return success_response("System config updated successfully.")

    except Error as e:
        return error_response(str(e), 500)
    finally:
        cursor.close()
