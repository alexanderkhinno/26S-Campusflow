import logging
import os

from backend.campusflow.crowd_routes import crowd_routes
from backend.campusflow.dashboards_routes import dashboards_routes
from backend.campusflow.data_categories_routes import data_categories_routes
from backend.campusflow.data_sources_routes import data_sources_routes
from backend.campusflow.location_routes import location_routes
from backend.campusflow.pipeline_runs_routes import pipeline_runs_routes
from backend.campusflow.system_configs_routes import system_configs_routes
from backend.campusflow.system_logs_routes import system_logs_routes
from backend.campusflow.users_routes import users_routes
from backend.db_connection import init_app as init_db
from dotenv import load_dotenv
from flask import Flask


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info("API startup")

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(crowd_routes)
    app.register_blueprint(dashboards_routes)
    app.register_blueprint(data_categories_routes)
    app.register_blueprint(data_sources_routes)
    app.register_blueprint(location_routes)
    app.register_blueprint(pipeline_runs_routes)
    app.register_blueprint(system_configs_routes)
    app.register_blueprint(system_logs_routes)
    app.register_blueprint(users_routes)

    return app
