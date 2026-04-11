#!/usr/bin/env python3
"""Databricks Autoloader entrypoint for Batch 2.2.

This script is designed to run in a Databricks Python job, notebook, or
Databricks Connect session where Spark is available.

It uses cloudFiles for incremental landing, availableNow for cost-aware
micro-batch execution, and an explicit checkpoint location so repeated runs
only process newly arrived files.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AutoloaderConfig:
    input_path: str
    checkpoint_path: str
    catalog: str
    schema: str
    table: str
    file_format: str
    target_table: str
    available_now: bool


def build_config(args: argparse.Namespace) -> AutoloaderConfig:
    catalog = args.catalog or os.environ.get("DATABRICKS_CATALOG_DEV", "workspace")
    schema = args.schema or os.environ.get("DATABRICKS_SCHEMA_DEV", "bronze")
    table = args.table or "iot_events_raw"
    return AutoloaderConfig(
        input_path=args.input_path,
        checkpoint_path=args.checkpoint_path,
        catalog=catalog,
        schema=schema,
        table=table,
        file_format="json",
        target_table=f"{catalog}.{schema}.{table}",
        available_now=not args.continuous,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch 2.2 Databricks Autoloader Bronze ingestion")
    parser.add_argument(
        "--input-path",
        default="dbfs:/tmp/scr/iot_landing",
        help="Databricks-accessible landing path containing IoT JSONL files.",
    )
    parser.add_argument(
        "--checkpoint-path",
        default="dbfs:/tmp/scr/checkpoints/iot_events_raw",
        help="Checkpoint directory used by the streaming job.",
    )
    parser.add_argument(
        "--catalog",
        default=os.environ.get("DATABRICKS_CATALOG_DEV", "workspace"),
        help="Target catalog (workspace fallback in the cost-constrained track).",
    )
    parser.add_argument(
        "--schema",
        default=os.environ.get("DATABRICKS_SCHEMA_DEV", "bronze"),
        help="Target schema for Bronze ingestion.",
    )
    parser.add_argument(
        "--table",
        default="iot_events_raw",
        help="Target Delta table name.",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Use a continuous trigger instead of availableNow.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved configuration and exit without requiring Spark.",
    )
    return parser.parse_args()


def print_config(config: AutoloaderConfig) -> None:
    print(json.dumps(asdict(config), indent=2, sort_keys=True))


def run_stream(config: AutoloaderConfig) -> None:
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import current_timestamp
    except ImportError as exc:  # pragma: no cover - Databricks runtime dependency
        raise SystemExit(
            "pyspark is not available. Run this script in Databricks or a Spark-enabled runtime."
        ) from exc

    spark = SparkSession.builder.getOrCreate()

    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {config.catalog}.{config.schema}")

    schema_definition = (
        "event_ts STRING, "
        "sensor_id STRING, "
        "route_code STRING, "
        "temperature_c DOUBLE, "
        "humidity_pct DOUBLE, "
        "battery_mv INT"
    )

    source_df = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", config.file_format)
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", f"{config.checkpoint_path}/schema")
        .schema(schema_definition)
        .load(config.input_path)
    )

    target_df = source_df.withColumn("ingested_at", current_timestamp())

    writer = (
        target_df.writeStream.format("delta")
        .option("checkpointLocation", config.checkpoint_path)
        .outputMode("append")
    )

    if config.available_now:
        writer = writer.trigger(availableNow=True)
    else:
        writer = writer.trigger(processingTime="30 seconds")

    query = writer.toTable(config.target_table)
    query.awaitTermination()

    row_count = spark.sql(f"SELECT count(*) AS row_count FROM {config.target_table}").collect()[0]["row_count"]
    print(f"Autoloader completed for {config.target_table}")
    print(f"Current row_count: {row_count}")


def main() -> None:
    args = parse_args()
    config = build_config(args)

    if args.dry_run:
        print_config(config)
        return

    print_config(config)
    run_stream(config)


if __name__ == "__main__":
    main()
