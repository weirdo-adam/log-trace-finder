import os
from datetime import datetime

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


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", logs=[])


@app.route("/", methods=["POST"])
def search():
    logs = []
    query_conditions = []
    parameters = {}

    # Get all form parameters
    company_id = request.form.get("company_id")
    request_uri = request.form.get("request_uri")
    trace_id = request.form.get("trace_id")
    keyword = request.form.get("keyword")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    # Check if all parameters are empty
    if not any(
        [
            company_id,
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
            start_dt = datetime.strptime(
                start_time, "%Y-%m-%dT%H:%M"
            ).timestamp()
            end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M").timestamp()

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

    if company_id:
        query_conditions.append(
            " AND LogAttributes['company_id'] = %(company_id)s"
        )
        parameters["company_id"] = company_id

    if request_uri:
        query_conditions.append(" AND LogAttributes['uri'] = %(request_uri)s")
        parameters["request_uri"] = request_uri

    if keyword:
        query_conditions.append(
            " AND Body LIKE concat('%%', %(keyword)s, '%%') "
        )
        parameters["keyword"] = keyword

    # Service name condition (as per original query)
    query_conditions.append(" AND ServiceName = 'standard-out-api'")

    # Build final query
    query += "".join(query_conditions)
    query += (
        " ORDER BY `ServiceName`,`TimestampTime`,`Timestamp` DESC LIMIT 100"
    )

    # print("Final Query:", query)
    # print("Parameters:", parameters)
    # Execute query
    results = clickhouse_client.query(query, parameters=parameters)
    logs = [dict(zip(query_log_columns, row)) for row in results.result_rows]

    return render_template(
        "index.html",
        logs=logs,
        company_id=company_id,
        request_uri=request_uri,
        trace_id=trace_id,
        keyword=keyword,
        start_time=start_time,
        end_time=end_time,
    )


if __name__ == "__main__":
    app.run()
