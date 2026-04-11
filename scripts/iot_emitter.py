#!/usr/bin/env python3
import argparse
import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path

SENSORS = ["TEMP-001", "TEMP-002", "TEMP-003", "TEMP-004"]
ROUTES = ["HAM-BER", "MUC-FRA", "CGN-STR"]


def build_event() -> dict:
    return {
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "sensor_id": random.choice(SENSORS),
        "route_code": random.choice(ROUTES),
        "temperature_c": round(random.uniform(1.0, 12.0), 2),
        "humidity_pct": round(random.uniform(30.0, 95.0), 2),
        "battery_mv": random.randint(3600, 4200),
    }


def write_batch(output_dir: Path, events_per_file: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"iot_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    path = output_dir / filename
    with path.open("w", encoding="utf-8") as f:
        for _ in range(events_per_file):
            f.write(json.dumps(build_event()) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit IoT heartbeat files in JSONL format.")
    parser.add_argument("--output-dir", default="data/iot_landing", help="Directory for emitted files")
    parser.add_argument("--iterations", type=int, default=3, help="Number of files to emit")
    parser.add_argument("--interval-seconds", type=int, default=5, help="Delay between files")
    parser.add_argument("--events-per-file", type=int, default=20, help="Events per output file")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    for i in range(args.iterations):
        path = write_batch(output_dir, args.events_per_file)
        print(f"[{i+1}/{args.iterations}] wrote {path}")
        if i < args.iterations - 1:
            time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
