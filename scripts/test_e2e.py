"""
End-to-end test: starts MinIO, generates fake data, runs the pipeline,
and checks that the expected web JSON files were written.

  uv run python scripts/test_e2e.py
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import threading
import time
import tomllib
import urllib.request
import zipfile
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from random import randint, seed

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import dotenv_values

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from setup_local import ensure_bucket, ensure_minio  # noqa: E402

seed(42)

# ── Load config ───────────────────────────────────────────────────────────────

TEST_CONFIG = ROOT / "config" / "test.toml"
env = dotenv_values(ROOT / ".env.local.example")

with open(TEST_CONFIG, "rb") as f:
    toml = tomllib.load(f)

ENDPOINT = env.get("R2_ENDPOINT_URL") or "http://localhost:9000"
BUCKET = toml["r2"]["bucket_name"]

r2 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=env["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def upload(key: str, data: bytes) -> None:
    r2.put_object(Bucket=BUCKET, Key=key, Body=data)
    print(f"  uploaded {key}")


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


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("── Starting MinIO ──────────────────────────────────────────────")
    ensure_minio(ENDPOINT)
    ensure_bucket(r2, BUCKET)

    print("\n── Uploading test data to inbox ────────────────────────────────")
    upload(f"bronze/inbox/fitbit/test_export.zip", make_fitbit_zip())
    upload(f"bronze/inbox/kindle/test_reading.zip", make_kindle_zip())
    upload(f"bronze/inbox/strong/test_workouts.csv", make_strong_csv())

    print("\n── Starting mock GitHub API ────────────────────────────────────")
    server, port = start_mock_server()
    print(f"  listening on http://127.0.0.1:{port}")

    print("\n── Running pipeline ────────────────────────────────────────────")
    result = subprocess.run(
        [sys.executable, "-m", "pipeline.main", "--config", str(TEST_CONFIG)],
        cwd=ROOT,
        env={
            **os.environ,
            "R2_ACCESS_KEY_ID": env["R2_ACCESS_KEY_ID"] or "",
            "R2_SECRET_ACCESS_KEY": env["R2_SECRET_ACCESS_KEY"] or "",
            "R2_ACCOUNT_ID": env.get("R2_ACCOUNT_ID") or "local",
            "R2_ENDPOINT_URL": env.get("R2_ENDPOINT_URL") or "http://localhost:9000",
            "GITHUB_TOKEN": env.get("GITHUB_TOKEN") or "test",
            "GITHUB_API_URL": f"http://127.0.0.1:{port}",
        },
    )

    if result.returncode != 0:
        print("\n✗ Pipeline exited with errors")
        sys.exit(1)

    print("\n── Checking outputs ────────────────────────────────────────────")
    expected = [
        "web/fitbit/daily_calories.json",
        "web/fitbit/daily_sleep.json",
        "web/fitbit/daily_steps.json",
        "web/fitbit/daily_exercise.json",
        "web/kindle/daily_reading.json",
        "web/github/daily_contributions.json",
        "web/strong/daily_workouts.json",
    ]
    all_ok = True
    for key in expected:
        try:
            r2.head_object(Bucket=BUCKET, Key=key)
            print(f"  ✓ {key}")
        except ClientError:
            print(f"  ✗ {key}  ← MISSING")
            all_ok = False

    print()
    if all_ok:
        print("E2E test passed ✓")
    else:
        print("E2E test failed ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
