"""
End-to-end test: starts MinIO, generates fake data, runs the pipeline,
and checks that the expected web JSON files were written.

  uv run python scripts/test_e2e.py
"""

from __future__ import annotations

import io
import json
import sys
import threading
import zipfile
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from random import randint
from botocore.exceptions import ClientError

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.config import PipelineConfig
from pipeline.r2 import make_client, upload_bytes, exists, export_daily_aggregated_json
from pipeline import stages
from pipeline.stages import GOLD_MODELS


def days_back(n: int) -> list[date]:
    today = date.today()
    return [today - timedelta(days=i) for i in range(n)]


# ── Fake data generators ──────────────────────────────────────────────────────

def make_fitbit_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for d in days_back(30):
            ds = d.isoformat()
            prefix = "Takeout/Fitbit/Global Export Data"
            calories = [{"dateTime": f"{ds} {h:02d}:00:00", "value": str(randint(60, 120))} for h in range(24)]
            zf.writestr(f"{prefix}/calories-{ds}.json", json.dumps(calories))
            steps = [{"dateTime": f"{ds} {h:02d}:00:00", "value": str(randint(0, 800))} for h in range(24)]
            zf.writestr(f"{prefix}/steps-{ds}.json", json.dumps(steps))
            zf.writestr(f"{prefix}/sleep-{ds}.json", json.dumps([{"dateOfSleep": ds, "minutesAsleep": randint(300, 480)}]))
            zf.writestr(f"{prefix}/exercise-{ds}.json", json.dumps([{"startTime": f"{ds}T09:00:00", "activeDuration": randint(0, 3_600_000)}]))
    return buf.getvalue()


def make_kindle_zip() -> bytes:
    books = ["Dune", "Project Hail Mary", "The Pragmatic Programmer"]
    lines = ["ASIN,end_time,product_name,reading_marketplace,start_time,total_reading_milliseconds"]
    for d in days_back(30):
        book = books[d.toordinal() % len(books)]
        lines.append(f"B{d.toordinal()},{d.isoformat()}T23:00:00Z,{book},US,{d.isoformat()}T08:00:00Z,{randint(10, 90) * 60_000}")
    csv_bytes = "\n".join(lines).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("Kindle.reading-insights-sessions_with_adjustments.csv", csv_bytes)
    return buf.getvalue()


def make_strong_csv() -> bytes:
    workouts = ["Push Day", "Pull Day", "Leg Day"]
    exercises = ["Bench Press", "Squat"]
    lines = ["Date;Workout Name;Duration (sec);Exercise Name;Set Order;Weight (kg);Reps;RPE;Distance (meters);Seconds;Notes;Workout Notes"]
    for d in days_back(30):
        if d.weekday() < 5:
            workout = workouts[d.toordinal() % len(workouts)]
            for i, ex in enumerate(exercises):
                lines.append(f"{d.isoformat()} 09:00:00;{workout};{randint(45, 90) * 60};{ex};{i+1};{randint(40,100)};{randint(5,12)};;;0;0;")
    return "\n".join(lines).encode()


def make_github_response() -> dict:
    weeks = []
    start = date.today() - timedelta(weeks=52)
    for w in range(52):
        days = []
        for d in range(7):
            day = start + timedelta(weeks=w, days=d)
            days.append({"date": day.isoformat(), "contributionCount": randint(0, 8) if day.weekday() < 5 else randint(0, 2)})
        weeks.append({"contributionDays": days})
    return {"data": {"user": {"contributionsCollection": {"contributionCalendar": {"weeks": weeks}}}}}


# ── Mock GitHub API server ────────────────────────────────────────────────────

class GitHubMockHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        response = json.dumps(make_github_response()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, *_) -> None:
        pass


def start_mock_server() -> tuple[HTTPServer, int]:
    server = HTTPServer(("127.0.0.1", 0), GitHubMockHandler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, port


def ensure_minio_running(endpoint: str) -> None:
    """Ensure MinIO is running and accessible."""
    import urllib.request
    import time
    import subprocess
    
    # Start MinIO with docker-compose
    subprocess.run(["docker", "compose", "up", "-d"], check=True, cwd=ROOT)
    
    print("· Waiting for MinIO", end="", flush=True)
    for _ in range(20):
        try:
            urllib.request.urlopen(f"{endpoint}/minio/health/live", timeout=1)
            print(" ✓")
            return
        except Exception:
            print(".", end="", flush=True)
            time.sleep(1)

    print("\n✗ MinIO did not start. Run: docker compose logs minio")
    sys.exit(1)


def ensure_bucket(r2, bucket: str) -> None:
    """Ensure the bucket exists."""
    try:
        r2.client.head_bucket(Bucket=bucket)
    except ClientError:
        r2.client.create_bucket(Bucket=bucket)
        print(f"✓ Created bucket '{bucket}'")
    print(f"✓ Bucket '{bucket}' ready")


def upload_test_data(r2) -> None:
    """Upload fake test data to the bronze inbox."""
    upload_bytes(r2, "bronze/inbox/fitbit/test_export.zip", make_fitbit_zip(), "application/zip")
    print("  uploaded fitbit test data")
    
    upload_bytes(r2, "bronze/inbox/kindle/test_reading.zip", make_kindle_zip(), "application/zip")
    print("  uploaded kindle test data")
    
    upload_bytes(r2, "bronze/inbox/strong/test_workouts.csv", make_strong_csv(), "text/csv")
    print("  uploaded strong test data")

def main() -> None:
    config = PipelineConfig.load(ROOT / "config" / "test.toml", ".env.local.example")

    print("── Starting MinIO ──────────────────────────────────────────────")

    r2 = make_client(config)
    print(config.endpoint_url)
    ensure_minio_running(config.endpoint_url)
    ensure_bucket(r2, config.r2_bucket_name)

    print("\n── Uploading test data to inbox ────────────────────────────────")
    upload_test_data(r2)

    print("\n── Starting mock GitHub API ────────────────────────────────────")
    _, port = start_mock_server()
    print(f"  listening on http://127.0.0.1:{port}")

    # Set the mock server URL in environment for the pipeline
    import os
    os.environ["GITHUB_API_URL"] = f"http://127.0.0.1:{port}"

    print("\n── Running pipeline ────────────────────────────────────────────")
    failures = []
    failures += stages.run_bronze(r2, config)
    failures += stages.run_silver(r2, config)
    failures += stages.run_gold(r2, config)

    if failures:
        print(f"\nE2E test failed ✗: {', '.join(failures)}")
        sys.exit(1)

    print("\n── Exporting web JSON ──────────────────────────────────────────")
    gold_models = stages._filter(GOLD_MODELS, config)
    for model in gold_models:
        export_daily_aggregated_json(r2, model.output_key, model.unit, model.label)
        _, layer, filename = model.output_key.split("/")
        print(f"  exported web/{layer}/{filename.removesuffix('.parquet')}.json")

    print("\n── Verifying outputs ───────────────────────────────────────────")
    missing = []
    for model in gold_models:
        _, layer, filename = model.output_key.split("/")
        web_key = f"web/{layer}/{filename.removesuffix('.parquet')}.json"
        if not exists(r2, web_key):
            missing.append(web_key)

    print()
    if missing:
        print(f"E2E test failed ✗: missing web files: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("E2E test passed ✓")


if __name__ == "__main__":
    main()
