import os

import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()


clickhouse_client = clickhouse_connect.get_client(
    host=os.getenv("CLICKHOUSE_HOST", "localhost"),
    port=os.getenv("CLICKHOUSE_PORT", 8123),
    user=os.getenv("CLICKHOUSE_USER", "default"),
    password=os.getenv("CLICKHOUSE_PASSWORD", ""),
    database=os.getenv("CLICKHOUSE_DATABASE", "otel"),
)


def query(trace_id):
    query = """
        SELECT
            Timestamp as "timestamp",
            Body as "body",
            SeverityText as "level",
            LogAttributes as "labels",
            TraceId as "traceID"
        FROM otel_logs
        WHERE LogAttributes['trace_id'] = %(trace_id)s
          and (timestamp >= now() - toIntervalHour(1) AND timestamp <= now())
        ORDER BY timestamp DESC
        LIMIT 1000
        """
    parameters = {"trace_id": trace_id}
    results = clickhouse_client.query(query, parameters=parameters)
    return results.result_rows


if __name__ == "__main__":
    trace_id = "d456d9d0af1d055137073033fdddb559"
    query_results = query(trace_id)
    columns = ["timestamp", "body", "level", "labels", "traceID"]
    logs = [dict(zip(columns, row)) for row in query_results]
    print(logs)
