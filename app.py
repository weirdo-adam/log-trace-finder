import os
from datetime import datetime
from zoneinfo import ZoneInfo

import clickhouse_connect
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)


clickhouse_client = clickhouse_connect.get_client(
    host=os.getenv("CLICKHOUSE_HOST", "localhost"),
    port=os.getenv("CLICKHOUSE_PORT", 8123),
    user=os.getenv("CLICKHOUSE_USER", "default"),
    password=os.getenv("CLICKHOUSE_PASSWORD", ""),
    database=os.getenv("CLICKHOUSE_DATABASE", "otel"),
)

query_log_columns = [
    "serviceName",
    "timestamp",
    "body",
    "level",
    "labels",
    "traceID",
]


def convert_to_utc_timestamp(time_str):
    # 1. 解析成 naive datetime（无时区）
    dt_naive = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    # 2. 手动加上 UTC+8 时区（如 Asia/Shanghai）
    dt_utc8 = dt_naive.replace(tzinfo=ZoneInfo("Asia/Shanghai"))

    # 3. 转换成 UTC（0 时区）
    dt_utc = dt_utc8.astimezone(ZoneInfo("UTC"))

    # 4. 返回时间戳
    return dt_utc.timestamp()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", logs=[])


@app.route("/", methods=["POST"])
def search():
    logs = []
    query_conditions = []
    parameters = {}

    # Get all form parameters
    request_uri = request.form.get("request_uri")
    trace_id = request.form.get("trace_id")
    keyword = request.form.get("keyword")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    # Check if all parameters are empty
    if not any(
        [
            request_uri,
            trace_id,
            keyword,
            start_time,
            end_time,
        ]
    ):
        return render_template("index.html", logs=[])

    # Base query
    query = """
        SELECT
            ServiceName as "serviceName",
            Timestamp as "timestamp",
            Body as "body",
            SeverityText as "level",
            LogAttributes as "labels",
            TraceId as "traceID"
        FROM otel_logs
        WHERE 1=1
    """

    # Add time range condition (default to last 24 hours if no specific range)
    if start_time and end_time:
        try:
            # Convert to ClickHouse compatible format
            start_dt = convert_to_utc_timestamp(start_time)
            end_dt = convert_to_utc_timestamp(end_time)

            query_conditions.append(
                " AND (timestamp >= toDateTime(%(start_time)s) AND timestamp <= toDateTime(%(end_time)s))"
            )
            parameters["start_time"] = start_dt
            parameters["end_time"] = end_dt
        except ValueError:
            # Fallback to default time range if parsing fails
            query_conditions.append(
                " AND (timestamp >= now() - toIntervalHour(1) AND timestamp <= now())"
            )
    else:
        query_conditions.append(
            " AND (timestamp >= now() - toIntervalHour(1) AND timestamp <= now())"
        )

    # Add other conditions if provided
    if trace_id:
        query_conditions.append(" AND TraceId = %(trace_id)s")
        parameters["trace_id"] = trace_id

    if request_uri:
        query_conditions.append(" AND LogAttributes['uri'] = %(request_uri)s")
        parameters["request_uri"] = request_uri

    if keyword:
        query_conditions.append(
            " AND Body LIKE concat('%%', %(keyword)s, '%%') "
        )
        parameters["keyword"] = keyword

    # Build final query
    query += "".join(query_conditions)
    query += " ORDER BY ServiceName DESC, TimestampTime DESC LIMIT 1000"

    # print("Final Query:", query)
    # print("Parameters:", parameters)
    # Execute query
    results = clickhouse_client.query(query, parameters=parameters)
    logs = [dict(zip(query_log_columns, row)) for row in results.result_rows]

    return render_template(
        "index.html",
        logs=logs,
        request_uri=request_uri,
        trace_id=trace_id,
        keyword=keyword,
        start_time=start_time,
        end_time=end_time,
    )


if __name__ == "__main__":
    app.run()
