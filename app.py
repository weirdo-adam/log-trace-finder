import os

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

query_log_columns = ["timestamp", "body", "level", "labels", "traceID"]


@app.route("/", methods=["GET", "POST"])
def index():
    trace_id = ""
    logs = []

    if request.method == "POST":
        trace_id = request.form.get("trace_id", trace_id)

    if trace_id:
        query = """
        SELECT
            Timestamp as "timestamp",
            Body as "body",
            SeverityText as "level",
            LogAttributes as "labels",
            TraceId as "traceID"
        FROM "otel"."otel_logs"
        WHERE LogAttributes['trace_id'] = %(trace_id)s
          and (timestamp >= now() - toIntervalHour(1) AND timestamp <= now())
        ORDER BY timestamp DESC
        LIMIT 1000
        """
        parameters = {"trace_id": trace_id}
        results = clickhouse_client.query(query, parameters=parameters)
        logs = [
            dict(zip(query_log_columns, row)) for row in results.result_rows
        ]

    return render_template("index.html", logs=logs, trace_id=trace_id)


if __name__ == "__main__":
    app.run(debug=True)
