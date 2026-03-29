# Year in Data

Personal activity heatmaps — GitHub contributions, Fitbit health data, Kindle reading, and Strong workouts visualised as annual SVG heatmaps on a GitHub Pages site.

The pipeline runs weekly via GitHub Actions, reads raw exports from Cloudflare R2, processes them with Polars, and writes aggregated JSON back to R2. The React website fetches that JSON at runtime.

## Data sources

| Source | How to get the data | Frequency |
|---|---|---|
| **GitHub** | Fetched automatically via GraphQL API | Automated |
| **Fitbit** | [Google Takeout](https://takeout.google.com) → select Fitbit → download zip | Manual |
| **Kindle** | [Amazon data request](https://www.amazon.com/hz/privacy-central/data-requests/preview.html) → Reading Insights CSV (takes 1–2 days) | Manual |
| **Strong** | Strong app → Settings → Export Data → CSV | Manual |

## R2 bucket layout

```
raw/{source}/inbox/                       ← drop new files here
raw/{source}/{YYYY-WXX}/                  ← archived after processing
processed/{source}/{metric}/{YYYY-WXX}.parquet  ← weekly Polars partitions
web/{source}/{metric}.json                ← public JSON consumed by the website
```

## Setup

### 1. Cloudflare R2

1. In the Cloudflare dashboard, create a bucket (e.g. `year-in-data`)
2. Under **Settings → Public access**, enable the public R2.dev subdomain
3. Under **Manage R2 API tokens**, create an API token with *Object Read & Write* on your bucket — note the **Account ID**, **Access Key ID**, and **Secret Access Key**

### 2. Environment variables

Copy `.env.example` to `.env` and fill in your values:

```sh
cp .env.example .env
```

```env
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key_id
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_BUCKET_NAME=year-in-data
R2_PUBLIC_URL=https://pub-xxxx.r2.dev

GITHUB_TOKEN=ghp_xxxx
GITHUB_USERNAME=your_github_username
```

For the website, copy `website/.env.example` to `website/.env`:

```sh
cp website/.env.example website/.env
```

```env
VITE_R2_PUBLIC_URL=https://pub-xxxx.r2.dev
```

### 3. GitHub repository secrets

Add these secrets under *Settings → Secrets and variables → Actions*:

| Secret | Value |
|---|---|
| `R2_ACCOUNT_ID` | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | R2 API token access key |
| `R2_SECRET_ACCESS_KEY` | R2 API token secret |
| `R2_BUCKET_NAME` | Bucket name (default: `year-in-data`) |
| `R2_PUBLIC_URL` | Public R2 subdomain URL |
| `PIPELINE_GITHUB_TOKEN` | Personal access token (read:user scope) |
| `GITHUB_USERNAME` | Your GitHub username |

### 4. Enable GitHub Pages

In *Settings → Pages*, set the source to the `gh-pages` branch.

## Local development (without real R2)

The pipeline can run against a local [MinIO](https://min.io) instance, which is S3-compatible and behaves identically to R2.

```sh
# Start MinIO
docker compose up -d

# Use the local env (minioadmin / minioadmin)
cp .env.local.example .env
```

Open http://localhost:9001 to access the MinIO web console. Create a bucket named `year-in-data` there (or via the AWS CLI: `aws s3 mb s3://year-in-data --endpoint-url http://localhost:9000`), then upload raw files into `raw/{source}/inbox/` as you normally would.

## Running locally

Install Python dependencies:

```sh
uv sync
```

Upload raw exports to `raw/{source}/inbox/` in your R2 bucket, then run:

```sh
uv run python -m pipeline.main
```

To skip a source:

```sh
RUN_FITBIT=false uv run python -m pipeline.main
```

Run the website locally:

```sh
cd website
npm install
npm run dev
```

## How it works

```
                     Manual uploads
Fitbit zip ──────┐
Kindle CSV ──────┼──→  raw/{source}/inbox/  (R2)
Strong CSV ──────┘              │
                                │  weekly GitHub Actions
GitHub API ─────────────────────┤
                                ↓
                     Polars processing
                                │
                 ┌──────────────┴──────────────┐
                 ↓                             ↓
    processed/{source}/{metric}/        web/{source}/{metric}.json
         {YYYY-WXX}.parquet             (aggregated, public)
         (data lake)                           │
                                              ↓
                                       React website
                                       (GitHub Pages)
```

Each weekly run:
1. **GitHub** — fetches the last 52 weeks of contributions from the API
2. **Fitbit / Kindle / Strong** — checks `inbox/` for new files, processes them, archives to a dated folder
3. For each metric, new data is merged into weekly Parquet partitions and the public web JSON is regenerated

## Project structure

```
├── pipeline/
│   ├── config.py            # Pydantic settings
│   ├── r2.py                # R2 client and storage operations
│   ├── main.py              # Entry point
│   └── extractors/
│       ├── fitbit.py
│       ├── kindle.py
│       ├── github.py
│       └── strong.py
├── website/
│   └── src/
│       ├── App.tsx
│       ├── components/
│       │   ├── Heatmap.tsx  # SVG heatmap (React + d3-scale)
│       │   └── DataSection.tsx
│       └── hooks/
│           └── useMetricData.ts
├── .github/workflows/
│   ├── pipeline.yml         # Weekly pipeline (every Monday 02:00 UTC)
│   └── deploy.yml           # Deploy website on push to main
└── pyproject.toml
```
