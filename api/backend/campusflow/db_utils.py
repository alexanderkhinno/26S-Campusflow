from backend.db_connection import get_db
from flask import jsonify, request


def get_cursor():
    return get_db().cursor(dictionary=True)


def commit():
    get_db().commit()


def error_response(message, status=400):
    return jsonify({"error": message}), status


def success_response(message, status=200, **kwargs):
    payload = {"message": message}
    payload.update(kwargs)
    return jsonify(payload), status


def exists(table, pk_name, pk_value):
    cursor = get_cursor()
    try:
        cursor.execute(
            f"SELECT {pk_name} FROM {table} WHERE {pk_name} = %s",
            (pk_value,),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()


def parse_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    value = str(value).lower()
    if value in ("true", "1", "yes"):
        return 1
    if value in ("false", "0", "no"):
        return 0
    return None


def require_json():
    data = request.get_json(silent=True)
    if not data:
        return None, error_response("Request body must be valid JSON.")
    return data, None
