DROP DATABASE IF EXISTS campusflow;
CREATE DATABASE campusflow;
USE campusflow;

-- =========================================================
-- DROP TABLES IN CHILD-TO-PARENT ORDER
-- =========================================================
DROP TABLE IF EXISTS dashboard_widgets;
DROP TABLE IF EXISTS dashboards;
DROP TABLE IF EXISTS favorite_locations;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS crowd_predictions;
DROP TABLE IF EXISTS crowd_measurements;
DROP TABLE IF EXISTS operating_hours;
DROP TABLE IF EXISTS location_data_sources;
DROP TABLE IF EXISTS pipeline_runs;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS system_configs;
DROP TABLE IF EXISTS data_sources;
DROP TABLE IF EXISTS data_categories;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS location_types;

-- =========================================================
-- CORE REFERENCE TABLES
-- =========================================================
CREATE TABLE location_types (
    location_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role_name VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_type_id INT NOT NULL,
    location_name VARCHAR(100) NOT NULL UNIQUE,
    building_name VARCHAR(100) NOT NULL,
    campus_zone VARCHAR(50),
    capacity INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    current_open_flag TINYINT(1) NOT NULL DEFAULT 1,
    added_by_user_id INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_locations_capacity CHECK (capacity > 0),
    CONSTRAINT chk_locations_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT fk_locations_type
        FOREIGN KEY (location_type_id) REFERENCES location_types(location_type_id),
    CONSTRAINT fk_locations_added_by
        FOREIGN KEY (added_by_user_id) REFERENCES users(user_id)
);

CREATE TABLE operating_hours (
    operating_hours_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    updated_by_user_id INT,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_operating_hours_day
        CHECK (day_of_week IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')),
    CONSTRAINT chk_operating_hours_times
        CHECK (open_time < close_time),
    CONSTRAINT fk_operating_hours_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id),
    CONSTRAINT fk_operating_hours_updated_by
        FOREIGN KEY (updated_by_user_id) REFERENCES users(user_id),
    CONSTRAINT uq_operating_hours UNIQUE (location_id, day_of_week)
);

-- =========================================================
-- CROWD / ANALYTICS TABLES
-- =========================================================
CREATE TABLE crowd_measurements (
    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    measured_at DATETIME NOT NULL,
    crowd_count INT NOT NULL,
    crowd_level VARCHAR(20) NOT NULL,
    occupancy_percent DECIMAL(5,2) NOT NULL,
    source_label VARCHAR(50) NOT NULL,
    is_valid TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_crowd_measurements_count CHECK (crowd_count >= 0),
    CONSTRAINT chk_crowd_measurements_percent CHECK (occupancy_percent >= 0 AND occupancy_percent <= 100),
    CONSTRAINT chk_crowd_measurements_level CHECK (crowd_level IN ('Low', 'Moderate', 'High', 'Full')),
    CONSTRAINT fk_crowd_measurements_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE crowd_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    predicted_for DATETIME NOT NULL,
    predicted_count INT NOT NULL,
    predicted_level VARCHAR(20) NOT NULL,
    confidence_score DECIMAL(4,2),
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_crowd_predictions_count CHECK (predicted_count >= 0),
    CONSTRAINT chk_crowd_predictions_level CHECK (predicted_level IN ('Low', 'Moderate', 'High', 'Full')),
    CONSTRAINT chk_crowd_predictions_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT fk_crowd_predictions_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE data_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    active_flag TINYINT(1) NOT NULL DEFAULT 1,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE data_sources (
    data_source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL,
    refresh_interval_minutes INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_by_user_id INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_data_sources_refresh CHECK (refresh_interval_minutes > 0),
    CONSTRAINT chk_data_sources_status CHECK (status IN ('active', 'inactive', 'error')),
    CONSTRAINT fk_data_sources_created_by
        FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
);

CREATE TABLE location_data_sources (
    location_id INT NOT NULL,
    data_source_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (location_id, data_source_id, category_id),
    CONSTRAINT fk_location_data_sources_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id),
    CONSTRAINT fk_location_data_sources_source
        FOREIGN KEY (data_source_id) REFERENCES data_sources(data_source_id),
    CONSTRAINT fk_location_data_sources_category
        FOREIGN KEY (category_id) REFERENCES data_categories(category_id)
);

-- =========================================================
-- STUDENT PERSONALIZATION TABLES
-- =========================================================
CREATE TABLE user_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    preferred_location_type_id INT,
    notification_opt_in TINYINT(1) NOT NULL DEFAULT 0,
    max_preferred_crowd_percent DECIMAL(5,2),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_preferences_percent
        CHECK (max_preferred_crowd_percent IS NULL OR
               (max_preferred_crowd_percent >= 0 AND max_preferred_crowd_percent <= 100)),
    CONSTRAINT fk_user_preferences_user
        FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_user_preferences_location_type
        FOREIGN KEY (preferred_location_type_id) REFERENCES location_types(location_type_id),
    CONSTRAINT uq_user_preferences_user UNIQUE (user_id)
);

CREATE TABLE favorite_locations (
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    saved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, location_id),
    CONSTRAINT fk_favorite_locations_user
        FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_favorite_locations_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- =========================================================
-- DASHBOARD TABLES
-- =========================================================
CREATE TABLE dashboards (
    dashboard_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dashboard_name VARCHAR(100) NOT NULL,
    dashboard_type VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dashboards_type
        CHECK (dashboard_type IN ('operations', 'analytics', 'system')),
    CONSTRAINT fk_dashboards_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE dashboard_widgets (
    widget_id INT AUTO_INCREMENT PRIMARY KEY,
    dashboard_id INT NOT NULL,
    widget_name VARCHAR(100) NOT NULL,
    widget_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    x_position INT NOT NULL DEFAULT 0,
    y_position INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_dashboard_widgets_positions
        CHECK (x_position >= 0 AND y_position >= 0),
    CONSTRAINT fk_dashboard_widgets_dashboard
        FOREIGN KEY (dashboard_id) REFERENCES dashboards(dashboard_id)
);

-- =========================================================
-- SYSTEM ADMIN TABLES
-- =========================================================
CREATE TABLE pipeline_runs (
    pipeline_run_id INT AUTO_INCREMENT PRIMARY KEY,
    data_source_id INT NOT NULL,
    run_started_at DATETIME NOT NULL,
    run_finished_at DATETIME,
    run_status VARCHAR(20) NOT NULL,
    rows_processed INT NOT NULL DEFAULT 0,
    error_message VARCHAR(255),
    initiated_by_user_id INT,
    CONSTRAINT chk_pipeline_runs_status
        CHECK (run_status IN ('running', 'success', 'failed')),
    CONSTRAINT chk_pipeline_runs_rows CHECK (rows_processed >= 0),
    CONSTRAINT fk_pipeline_runs_source
        FOREIGN KEY (data_source_id) REFERENCES data_sources(data_source_id),
    CONSTRAINT fk_pipeline_runs_initiated_by
        FOREIGN KEY (initiated_by_user_id) REFERENCES users(user_id)
);

CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    log_level VARCHAR(10) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    log_message VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_system_logs_level
        CHECK (log_level IN ('INFO', 'WARN', 'ERROR')),
    CONSTRAINT fk_system_logs_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE system_configs (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value VARCHAR(100) NOT NULL,
    config_description VARCHAR(255),
    updated_by_user_id INT,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_system_configs_updated_by
        FOREIGN KEY (updated_by_user_id) REFERENCES users(user_id)
);