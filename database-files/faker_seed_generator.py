from __future__ import annotations

import random
from datetime import datetime, time, timedelta

from faker import Faker

fake = Faker()
Faker.seed(3200)
random.seed(3200)


def esc(value: str) -> str:
    return value.replace("'", "''")


def q(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(value, time):
        return f"'{value.strftime('%H:%M:%S')}'"
    return f"'{esc(str(value))}'"


def insert_stmt(table: str, columns: list[str], rows: list[tuple]) -> str:
    vals = []
    for row in rows:
        vals.append("(" + ", ".join(q(v) for v in row) + ")")
    cols = ", ".join(columns)
    return f"INSERT INTO {table} ({cols}) VALUES\n" + ",\n".join(vals) + ";\n"


ROLE_MAP = {
    "student": "Student",
    "ops": "Campus Operations Manager",
    "analyst": "Data Analyst",
    "admin": "System Administrator",
}

LOCATION_TYPES = [
    ("Library", "Study and academic space"),
    ("Gym", "Fitness and recreation facility"),
    ("Dining Hall", "Campus dining location"),
    ("Study Lounge", "Quiet study area with seating"),
    ("Computer Lab", "Shared computing and printing resources"),
    ("Student Center", "Multipurpose student activity space"),
    ("Maker Space", "Creative build and prototype space"),
    ("Cafe", "Light food and coffee service"),
]

DATA_CATEGORIES = [
    ("Crowd Metrics", "Live and historical crowd data", 1),
    ("Operations", "Hours, staffing, and facility operations data", 1),
    ("System Health", "Logs, uptime, and backend monitoring data", 1),
    ("Events", "Special event and campus programming data", 1),
    ("Facilities", "Maintenance and room availability data", 1),
    ("Dining Services", "Menu and dining throughput data", 1),
    ("Recreation", "Fitness center and recreation data", 1),
    ("Academic Services", "Tutoring, study, and academic support data", 1),
]

SYSTEM_CONFIGS = [
    (
        "prediction_refresh_minutes",
        "15",
        "How often crowd predictions are recalculated",
        40,
    ),
    ("max_sensor_delay_seconds", "120", "Maximum allowed delay for sensor data", 40),
    (
        "default_capacity_alert_percent",
        "90",
        "Threshold for crowded location alerts",
        40,
    ),
    ("history_retention_days", "180", "How long crowd history is retained", 40),
    ("dashboard_cache_seconds", "60", "Dashboard query cache lifetime", 40),
    (
        "preferred_source_priority",
        "sensor>manual>upload",
        "Priority order for source trust",
        40,
    ),
    ("pipeline_batch_size", "500", "Default batch size for ingestion jobs", 40),
    (
        "prediction_confidence_floor",
        "0.60",
        "Minimum confidence to display predictions",
        40,
    ),
    ("low_crowd_threshold", "0.35", "Max occupancy ratio for low crowd", 40),
    ("moderate_crowd_threshold", "0.70", "Max occupancy ratio for moderate crowd", 40),
]

buildings = [
    "Snell Library",
    "Marino Recreation Center",
    "International Village",
    "Curry Student Center",
    "Shillman Hall",
    "Ell Hall",
    "Richards Hall",
    "ISEC",
    "EXP",
    "West Village H",
    "Dodge Hall",
    "Hayden Hall",
    "Mugar Life Sciences",
    "Behrakis Health Sciences Center",
    "Forsyth Building",
    "Raytheon Amphitheater",
    "Ryder Hall",
    "Robinson Hall",
    "Churchill Hall",
    "Meserve Hall",
    "Lake Hall",
    "Kariotis Hall",
]

zones = ["West Campus", "Central Campus", "East Campus", "North Campus", "South Campus"]

location_name_templates = {
    1: [
        "Quiet Study Floor",
        "Reference Commons",
        "Research Hub",
        "Stacks Reading Room",
        "Learning Commons",
    ],
    2: [
        "Cardio Center",
        "Strength Studio",
        "Indoor Courts",
        "Fitness Zone",
        "Training Loft",
    ],
    3: ["Dining Pavilion", "Fresh Kitchen", "Marketplace", "Campus Eats", "Food Court"],
    4: [
        "Collaborative Lounge",
        "Late Night Study Lounge",
        "Commons Lounge",
        "Peer Study Lounge",
    ],
    5: ["Open Computing Lab", "Innovation Lab", "Printing Lab", "Data Lab"],
    6: ["Student Hub", "Community Center", "Engagement Center", "Activity Forum"],
    7: ["Prototype Studio", "Design Garage", "Build Lab", "Fabrication Room"],
    8: ["Coffee Corner", "Campus Cafe", "Brew Bar", "Quick Bites Cafe"],
}


def unique_location_names(
    n: int,
) -> list[tuple[int, str, str, str, int, str, int, int]]:
    rows = []
    used = set()
    for i in range(1, n + 1):
        type_id = random.randint(1, len(LOCATION_TYPES))
        building = random.choice(buildings)
        base = random.choice(location_name_templates[type_id])
        name = f"{building} {base}"
        k = 2
        while name in used:
            name = f"{building} {base} {k}"
            k += 1
        used.add(name)
        capacity = random.randint(80, 900)
        rows.append(
            (
                type_id,
                name,
                building,
                random.choice(zones),
                capacity,
                "active" if random.random() < 0.9 else "inactive",
                1 if random.random() < 0.8 else 0,
                random.randint(31, 40),
            )
        )
    return rows


def crowd_level_from_ratio(r: float) -> str:
    if r < 0.35:
        return "Low"
    if r < 0.70:
        return "Moderate"
    if r < 0.95:
        return "High"
    return "Full"


def main() -> None:
    out = []
    out.append("USE campusflow;\n\n")

    # location types
    out.append(
        insert_stmt(
            "location_types",
            ["location_type_id", "type_name", "description"],
            [(i + 1, *row) for i, row in enumerate(LOCATION_TYPES)],
        )
    )

    # users: 40 strong-entity rows
    users = []
    emails = set()
    fixed = [
        (1, "Sarah", "Johnson", "sarah.johnson@northeastern.edu", ROLE_MAP["student"]),
        (2, "Mark", "Preston", "mark.preston@northeastern.edu", ROLE_MAP["ops"]),
        (
            3,
            "Jason",
            "Morrison",
            "jason.morrison@northeastern.edu",
            ROLE_MAP["analyst"],
        ),
        (4, "Kevin", "Brooks", "kevin.brooks@northeastern.edu", ROLE_MAP["admin"]),
    ]
    for row in fixed:
        users.append((*row, fake.date_time_between(start_date="-180d", end_date="now")))
        emails.add(row[3])
    for uid in range(5, 41):
        role_key = random.choices(
            ["student", "ops", "analyst", "admin"], weights=[24, 6, 6, 4]
        )[0]
        first = fake.first_name()
        last = fake.last_name()
        email = f"{first.lower()}.{last.lower()}{uid}@northeastern.edu"
        while email in emails:
            email = f"{first.lower()}.{last.lower()}{uid}{random.randint(1, 9)}@northeastern.edu"
        emails.add(email)
        users.append(
            (
                uid,
                first,
                last,
                email,
                ROLE_MAP[role_key],
                fake.date_time_between(start_date="-180d", end_date="now"),
            )
        )
    out.append(
        insert_stmt(
            "users",
            ["user_id", "first_name", "last_name", "email", "role_name", "created_at"],
            users,
        )
    )

    # locations: 36 strong-entity rows
    locations = []
    for lid, row in enumerate(unique_location_names(36), start=1):
        locations.append(
            (lid, *row, fake.date_time_between(start_date="-180d", end_date="now"))
        )
    out.append(
        insert_stmt(
            "locations",
            [
                "location_id",
                "location_type_id",
                "location_name",
                "building_name",
                "campus_zone",
                "capacity",
                "status",
                "current_open_flag",
                "added_by_user_id",
                "created_at",
            ],
            locations,
        )
    )

    # operating hours: 36*7 = 252 weak rows
    weekday_hours = {
        "Monday": (time(7, 0), time(23, 0)),
        "Tuesday": (time(7, 0), time(23, 0)),
        "Wednesday": (time(7, 0), time(23, 0)),
        "Thursday": (time(7, 0), time(23, 0)),
        "Friday": (time(7, 0), time(22, 0)),
        "Saturday": (time(9, 0), time(20, 0)),
        "Sunday": (time(9, 0), time(21, 0)),
    }
    hours = []
    oh_id = 1
    for lid in range(1, 37):
        for day, (open_t, close_t) in weekday_hours.items():
            open_adj = (
                datetime.combine(datetime.today(), open_t)
                + timedelta(minutes=random.choice([0, 0, 30]))
            ).time()
            close_adj = (
                datetime.combine(datetime.today(), close_t)
                - timedelta(minutes=random.choice([0, 0, 30]))
            ).time()
            hours.append(
                (
                    oh_id,
                    lid,
                    day,
                    open_adj,
                    close_adj,
                    random.randint(31, 40),
                    fake.date_time_between(start_date="-60d", end_date="now"),
                )
            )
            oh_id += 1
    out.append(
        insert_stmt(
            "operating_hours",
            [
                "operating_hours_id",
                "location_id",
                "day_of_week",
                "open_time",
                "close_time",
                "updated_by_user_id",
                "updated_at",
            ],
            hours,
        )
    )

    # crowd_measurements: 360 weak rows
    measurements = []
    m_id = 1
    start_dt = datetime(2026, 4, 1, 8, 0, 0)
    for lid in range(1, 37):
        capacity = locations[lid - 1][5]
        for k in range(10):
            measured_at = start_dt + timedelta(
                hours=k * 4 + random.randint(0, 2), days=random.randint(0, 9)
            )
            ratio = max(0.02, min(1.0, random.betavariate(2.2, 2.8)))
            crowd_count = max(0, min(capacity, int(round(capacity * ratio))))
            occ = round((crowd_count / capacity) * 100, 2)
            measurements.append(
                (
                    m_id,
                    lid,
                    measured_at,
                    crowd_count,
                    crowd_level_from_ratio(crowd_count / capacity),
                    occ,
                    random.choice(["sensor", "manual", "camera", "turnstile"]),
                    0 if random.random() < 0.04 else 1,
                    fake.date_time_between(
                        start_date=measured_at,
                        end_date=measured_at + timedelta(hours=1),
                    ),
                )
            )
            m_id += 1
    out.append(
        insert_stmt(
            "crowd_measurements",
            [
                "measurement_id",
                "location_id",
                "measured_at",
                "crowd_count",
                "crowd_level",
                "occupancy_percent",
                "source_label",
                "is_valid",
                "created_at",
            ],
            measurements,
        )
    )

    # crowd_predictions: 180 weak rows
    predictions = []
    p_id = 1
    pred_base = datetime(2026, 4, 10, 9, 0, 0)
    for lid in range(1, 37):
        capacity = locations[lid - 1][5]
        for step in range(5):
            predicted_for = pred_base + timedelta(hours=step * 3)
            ratio = max(0.05, min(1.0, random.betavariate(2.5, 2.4)))
            predicted_count = max(0, min(capacity, int(round(capacity * ratio))))
            predictions.append(
                (
                    p_id,
                    lid,
                    predicted_for,
                    predicted_count,
                    crowd_level_from_ratio(predicted_count / capacity),
                    round(random.uniform(0.62, 0.97), 2),
                    fake.date_time_between(
                        start_date=pred_base - timedelta(days=2), end_date=pred_base
                    ),
                )
            )
            p_id += 1
    out.append(
        insert_stmt(
            "crowd_predictions",
            [
                "prediction_id",
                "location_id",
                "predicted_for",
                "predicted_count",
                "predicted_level",
                "confidence_score",
                "generated_at",
            ],
            predictions,
        )
    )

    # data categories
    out.append(
        insert_stmt(
            "data_categories",
            [
                "category_id",
                "category_name",
                "description",
                "active_flag",
                "updated_at",
            ],
            [
                (
                    i + 1,
                    cat,
                    desc,
                    active,
                    fake.date_time_between(start_date="-90d", end_date="now"),
                )
                for i, (cat, desc, active) in enumerate(DATA_CATEGORIES)
            ],
        )
    )

    # data sources: 32 strong rows
    source_types = ["API", "CSV Upload", "Agent", "Webhook", "Manual Entry"]
    source_rows = []
    used_source_names = set()
    for sid in range(1, 33):
        if sid == 1:
            name = "Campus Sensors API"
        elif sid == 2:
            name = "Manual Staff Upload"
        elif sid == 3:
            name = "System Monitoring Agent"
        else:
            name = f"{fake.company()} {random.choice(['Feed', 'Connector', 'Sync', 'Gateway', 'Importer'])}"
        while name in used_source_names:
            name = f"{name} {sid}"
        used_source_names.add(name)
        source_rows.append(
            (
                sid,
                name,
                random.choice(source_types),
                random.choice([1, 5, 10, 15, 30, 60, 120]),
                random.choices(["active", "inactive", "error"], weights=[24, 6, 2])[0],
                random.randint(31, 40),
                fake.date_time_between(start_date="-120d", end_date="now"),
            )
        )
    out.append(
        insert_stmt(
            "data_sources",
            [
                "data_source_id",
                "source_name",
                "source_type",
                "refresh_interval_minutes",
                "status",
                "created_by_user_id",
                "created_at",
            ],
            source_rows,
        )
    )

    # location_data_sources bridge: 140 rows
    lds_rows = set()
    while len(lds_rows) < 140:
        lds_rows.add(
            (
                random.randint(1, 36),
                random.randint(1, 32),
                random.randint(1, len(DATA_CATEGORIES)),
            )
        )
    out.append(
        insert_stmt(
            "location_data_sources",
            ["location_id", "data_source_id", "category_id"],
            sorted(lds_rows),
        )
    )

    # user_preferences: 35 rows
    pref_rows = []
    pref_id = 1
    users_with_prefs = random.sample(range(1, 41), 35)
    for uid in sorted(users_with_prefs):
        pref_rows.append(
            (
                pref_id,
                uid,
                random.randint(1, len(LOCATION_TYPES))
                if random.random() < 0.8
                else None,
                1 if random.random() < 0.55 else 0,
                round(random.uniform(35, 95), 2) if random.random() < 0.9 else None,
                fake.date_time_between(start_date="-60d", end_date="now"),
            )
        )
        pref_id += 1
    out.append(
        insert_stmt(
            "user_preferences",
            [
                "preference_id",
                "user_id",
                "preferred_location_type_id",
                "notification_opt_in",
                "max_preferred_crowd_percent",
                "updated_at",
            ],
            pref_rows,
        )
    )

    # favorite_locations bridge: 150 rows
    fav_rows = set()
    while len(fav_rows) < 150:
        fav_rows.add(
            (
                random.randint(1, 40),
                random.randint(1, 36),
                fake.date_time_between(start_date="-120d", end_date="now"),
            )
        )
    out.append(
        insert_stmt(
            "favorite_locations",
            ["user_id", "location_id", "saved_at"],
            sorted(fav_rows, key=lambda x: (x[0], x[1])),
        )
    )

    # dashboards: 34 strong-ish rows
    d_rows = []
    dashboard_types = ["operations", "analytics", "system"]
    names = {
        "operations": [
            "Operations Overview",
            "Facility Comparison",
            "Hours and Availability",
            "Crowding Hotspots",
        ],
        "analytics": [
            "Campus Analytics Trends",
            "Usage Forecasts",
            "Occupancy Analysis",
            "Data Quality Review",
        ],
        "system": [
            "System Health Monitor",
            "Pipeline Watch",
            "Service Reliability",
            "Alert Triage",
        ],
    }
    used = set()
    for did in range(1, 35):
        dtype = random.choice(dashboard_types)
        name = random.choice(names[dtype])
        if name in used:
            name = f"{name} {did}"
        used.add(name)
        created = fake.date_time_between(start_date="-90d", end_date="now")
        updated = created + timedelta(
            days=random.randint(0, 20), hours=random.randint(0, 12)
        )
        d_rows.append((did, random.randint(1, 40), name, dtype, created, updated))
    out.append(
        insert_stmt(
            "dashboards",
            [
                "dashboard_id",
                "user_id",
                "dashboard_name",
                "dashboard_type",
                "created_at",
                "updated_at",
            ],
            d_rows,
        )
    )

    # dashboard_widgets: 102 rows
    widget_types = ["bar_chart", "line_chart", "metric_card", "table", "heatmap"]
    metric_names = [
        "peak_occupancy_percent",
        "hourly_crowd_count",
        "failed_pipeline_runs",
        "avg_prediction_confidence",
        "active_locations",
        "crowd_by_zone",
        "sensor_latency_seconds",
        "daily_visits",
        "favorites_by_location",
        "alert_count",
        "status_breakdown",
        "utilization_rate",
    ]
    dw_rows = []
    wid = 1
    for did in range(1, 35):
        for pos in range(random.randint(2, 4)):
            dw_rows.append(
                (
                    wid,
                    did,
                    f"{random.choice(['Overview', 'Trend', 'Status', 'Snapshot', 'Breakdown'])} Widget {wid}",
                    random.choice(widget_types),
                    random.choice(metric_names),
                    pos % 2,
                    pos // 2,
                )
            )
            wid += 1
    out.append(
        insert_stmt(
            "dashboard_widgets",
            [
                "widget_id",
                "dashboard_id",
                "widget_name",
                "widget_type",
                "metric_name",
                "x_position",
                "y_position",
            ],
            dw_rows,
        )
    )

    # pipeline_runs: 96 rows
    pr_rows = []
    run_id = 1
    for dsid in range(1, 33):
        for _ in range(3):
            start = fake.date_time_between(start_date="-30d", end_date="now")
            status = random.choices(
                ["success", "failed", "running"], weights=[20, 5, 2]
            )[0]
            end = (
                None
                if status == "running"
                else start + timedelta(minutes=random.randint(1, 18))
            )
            err = (
                None
                if status != "failed"
                else random.choice(
                    [
                        "Timeout while fetching source data",
                        "Malformed input rows detected",
                        "Authentication token expired",
                        "Schema validation failed",
                    ]
                )
            )
            rows_processed = 0 if status == "running" else random.randint(50, 2500)
            pr_rows.append(
                (
                    run_id,
                    dsid,
                    start,
                    end,
                    status,
                    rows_processed,
                    err,
                    random.randint(31, 40),
                )
            )
            run_id += 1
    out.append(
        insert_stmt(
            "pipeline_runs",
            [
                "pipeline_run_id",
                "data_source_id",
                "run_started_at",
                "run_finished_at",
                "run_status",
                "rows_processed",
                "error_message",
                "initiated_by_user_id",
            ],
            pr_rows,
        )
    )

    # system_logs: 160 rows
    components = [
        "PipelineService",
        "PredictionEngine",
        "DataCleaner",
        "APIGateway",
        "DashboardService",
        "Scheduler",
    ]
    messages = {
        "INFO": [
            "Pipeline completed successfully",
            "Dashboard cache refreshed",
            "Prediction batch generated",
            "Heartbeat check passed",
        ],
        "WARN": [
            "Prediction confidence below threshold",
            "Source latency above expected range",
            "Retry triggered for API request",
        ],
        "ERROR": [
            "Invalid crowd measurement detected and flagged",
            "Pipeline authentication failed",
            "Database write conflict encountered",
        ],
    }
    log_rows = []
    for log_id in range(1, 161):
        level = random.choices(["INFO", "WARN", "ERROR"], weights=[100, 40, 20])[0]
        log_rows.append(
            (
                log_id,
                random.randint(31, 40) if random.random() < 0.8 else None,
                level,
                random.choice(components),
                random.choice(messages[level]),
                fake.date_time_between(start_date="-14d", end_date="now"),
            )
        )
    out.append(
        insert_stmt(
            "system_logs",
            [
                "log_id",
                "user_id",
                "log_level",
                "component_name",
                "log_message",
                "created_at",
            ],
            log_rows,
        )
    )

    # system_configs
    out.append(
        insert_stmt(
            "system_configs",
            [
                "config_id",
                "config_key",
                "config_value",
                "config_description",
                "updated_by_user_id",
                "updated_at",
            ],
            [
                (i + 1, *row, fake.date_time_between(start_date="-90d", end_date="now"))
                for i, row in enumerate(SYSTEM_CONFIGS)
            ],
        )
    )

    with open("02_mock_data.sql", "w") as f:
        f.write("".join(out))


if __name__ == "__main__":
    main()
