#!/usr/bin/env python3
import argparse
import glob
import importlib
import json
import os
from urllib.parse import urlparse


def clean_host(raw_host: str) -> str:
    parsed = urlparse(raw_host)
    return parsed.netloc or raw_host.replace("https://", "").strip("/")


def get_databricks_sql_module():
    try:
        return importlib.import_module("databricks.sql")
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "databricks-sql-connector is not installed. "
            "Run: pip install databricks-sql-connector"
        ) from exc


def load_records(pattern: str) -> list[tuple[str, str, str, float, float, int]]:
    records: list[tuple[str, str, str, float, float, int]] = []
    files = sorted(glob.glob(pattern))
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                records.append(
                    (
                        data["event_ts"],
                        data["sensor_id"],
                        data["route_code"],
                        float(data["temperature_c"]),
                        float(data["humidity_pct"]),
                        int(data["battery_mv"]),
                    )
                )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Load local IoT JSONL files into Databricks Bronze table.")
    parser.add_argument("--input-pattern", default="data/iot_landing/*.jsonl")
    parser.add_argument("--catalog", default=os.environ.get("DATABRICKS_CATALOG_DEV", "workspace"))
    parser.add_argument("--schema", default="bronze")
    parser.add_argument("--table", default="iot_events_raw")
    args = parser.parse_args()

    raw_host = os.environ.get("DATABRICKS_HOST", "")
    http_path = os.environ.get("DATABRICKS_HTTP_PATH", "")
    token = os.environ.get("DATABRICKS_TOKEN", "")

    if not raw_host or not http_path or not token:
        raise SystemExit("Missing one of DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN")

    host = clean_host(raw_host)
    full_table = f"{args.catalog}.{args.schema}.{args.table}"
    sql = get_databricks_sql_module()

    rows = load_records(args.input_pattern)
    if not rows:
        raise SystemExit(f"No records found for pattern: {args.input_pattern}")

    with sql.connect(server_hostname=host, http_path=http_path, access_token=token) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {args.catalog}.{args.schema}")
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {full_table} (
                  event_ts STRING,
                  sensor_id STRING,
                  route_code STRING,
                  temperature_c DOUBLE,
                  humidity_pct DOUBLE,
                  battery_mv INT
                )
                """
            )
            cursor.executemany(
                f"INSERT INTO {full_table} VALUES (?, ?, ?, ?, ?, ?)",
                rows,
            )
            cursor.execute(f"SELECT count(*) FROM {full_table}")
            total = cursor.fetchone()[0]

    print(f"Loaded {len(rows)} rows into {full_table}")
    print(f"Current row_count: {total}")


if __name__ == "__main__":
    main()
