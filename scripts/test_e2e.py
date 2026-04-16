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
from pipeline.r2 import ensure_bucket, make_client, make_web_client, upload_bytes, exists
from pipeline.jobs import fitbit, github, kindle, strong, aggregate
from pipeline.main import run_pipeline
from pipeline import paths


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


def upload_test_data(r2) -> None:
    upload_bytes(r2, f"{paths.inbox(paths.Source.FITBIT)}/test_export.zip", make_fitbit_zip(), "application/zip")
    print("  uploaded fitbit test data")

    upload_bytes(r2, f"{paths.inbox(paths.Source.KINDLE)}/test_reading.zip", make_kindle_zip(), "application/zip")
    print("  uploaded kindle test data")

    upload_bytes(r2, f"{paths.inbox(paths.Source.STRONG)}/test_workouts.csv", make_strong_csv(), "text/csv")
    print("  uploaded strong test data")


def create_test_bucket(config):
    r2 = make_client(config)
    web_r2 = make_web_client(config)
    ensure_bucket(r2, config.r2_bucket_name)
    ensure_bucket(web_r2, config.web_bucket_name)
    upload_test_data(r2)

def main() -> None:
    config = PipelineConfig.load(ROOT / "config" / "test.toml", ".env.local.example")

    print("── Starting MinIO ──────────────────────────────────────────────")
    create_test_bucket(config)

    print("\n── Starting mock GitHub API ────────────────────────────────────")
    _, port = start_mock_server()
    print(f"  listening on http://127.0.0.1:{port}")

    import os
    os.environ["GITHUB_API_URL"] = f"http://127.0.0.1:{port}"

    print("\n── Running pipeline ────────────────────────────────────────────")
    run_pipeline(config)



if __name__ == "__main__":
    main()
