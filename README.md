# Year in Data

Personal activity heatmaps — GitHub contributions, Fitbit health data, Kindle reading, and Strong workouts visualised as annual SVG heatmaps on a GitHub Pages site.

The pipeline runs weekly via GitHub Actions, reads raw exports from Cloudflare R2, processes them with Polars, and writes aggregated JSON back to R2. The React website fetches that JSON at runtime.

## Data sources

| Source | How to get the data | Format |
|---|---|---|
| **GitHub** | Fetched automatically via GraphQL API | Automated |
| **Fitbit** | [Google Takeout](https://takeout.google.com) → select Fitbit → download zip | `.zip` |
| **Kindle** | Amazon data request → Reading Insights → download zip | `.zip` |
| **Strong** | Strong app → Settings → Export Data → CSV | `.csv` |

Raw exports are either uploaded manually to `raw/{source}/inbox/` in R2, or synced automatically from a public Google Drive folder via `scripts/sync_drive.py`.

## R2 bucket layout

```
raw/{source}/inbox/                             ← drop new files here
raw/{source}/{YYYY-WXX}/                        ← archived after processing
processed/{source}/{metric}/{YYYY-WXX}.parquet  ← weekly Polars partitions
web/{source}/{metric}.json                      ← public JSON consumed by the website
```

## Setup

### 1. Cloudflare R2

1. Create a bucket (e.g. `year-in-data`) in the Cloudflare dashboard
2. Under **Settings → Public access**, enable the public R2.dev subdomain
3. Under **Manage R2 API tokens**, create a token with *Object Read & Write* — note the **Account ID**, **Access Key ID**, and **Secret Access Key**
4. Run `make setup-r2` to apply the public-read bucket policy and CORS config

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

# Optional: public Google Drive folder share link for auto-sync
DRIVE_SHARE_URL=https://drive.google.com/drive/folders/xxxx
```

For the website, copy `website/.env.example` to `website/.env`:

```sh
cp website/.env.example website/.env
```

```env
VITE_R2_PUBLIC_URL=https://pub-xxxx.r2.dev
```

### 3. GitHub repository secrets

Add these under *Settings → Secrets and variables → Actions*:

| Secret | Value |
|---|---|
| `R2_ACCOUNT_ID` | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | R2 API token access key |
| `R2_SECRET_ACCESS_KEY` | R2 API token secret |
| `R2_BUCKET_NAME` | Bucket name (default: `year-in-data`) |
| `R2_PUBLIC_URL` | Public R2 subdomain URL |
| `PIPELINE_GITHUB_TOKEN` | Personal access token (read:user scope) |
| `GITHUB_USERNAME` | Your GitHub username |
| `DRIVE_SHARE_URL` | Public Google Drive folder share link |

### 4. Enable GitHub Pages

In *Settings → Pages*, set the source to the `gh-pages` branch.

## Local development

The pipeline can run against a local [MinIO](https://min.io) instance (S3-compatible, behaves identically to R2).

```sh
# Install dependencies
uv sync
cd website && npm install

# Start MinIO and create the local bucket
make up

# Run the end-to-end test with fake data
make test

# Or sync real data from Drive and run the pipeline
make pipeline
```

Open http://localhost:9001 for the MinIO web console (credentials: `minioadmin` / `minioadmin`).

## Makefile targets

| Target | Description |
|---|---|
| `make up` | Start MinIO and create the local bucket |
| `make down` | Stop MinIO and remove data |
| `make pipeline` | Sync Drive → run pipeline (production) |
| `make test` | Sync Drive + run e2e test with fake data (local) |
| `make setup-r2` | Apply bucket policy and CORS to production R2 |
| `make notebook` | Open Jupyter in the `notebooks/` folder |
| `make dev` | Start the Vite dev server |
| `make build` | Build the website for production |

## How it works

```
                     Manual uploads / Drive sync
Fitbit zip ──────┐
Kindle zip ──────┼──→  raw/{source}/inbox/  (R2)
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
1. **GitHub** — fetches the last 52 weeks of contributions from the GraphQL API
2. **Fitbit / Kindle / Strong** — checks `inbox/` for new files, processes them, archives to a dated folder
3. For each metric, new data is merged into weekly Parquet partitions and the public web JSON is regenerated
4. Extractor failures are isolated — one source failing does not abort the rest

## Project structure

```
├── pipeline/
│   ├── config.py            # Settings (loaded from .env + config/*.toml)
│   ├── r2.py                # R2 client and all storage operations
│   ├── main.py              # Entry point with per-extractor error isolation
│   └── extractors/
│       ├── fitbit.py        # Parses Google Takeout zips (multi-day intraday files)
│       ├── kindle.py        # Parses Kindle Reading Insights zip
│       ├── strong.py        # Parses Strong CSV export
│       └── github.py        # Fetches GitHub contributions via GraphQL
├── scripts/
│   ├── sync_drive.py        # Download exports from public Google Drive → R2 inbox
│   ├── setup_r2.py          # One-time production R2 bucket/policy/CORS setup
│   ├── setup_local.py       # MinIO startup and bucket creation for local dev
│   └── test_e2e.py          # End-to-end test with fake data against local MinIO
├── notebooks/               # Jupyter notebooks for data exploration
├── website/
│   └── src/
│       ├── App.tsx          # Sticky navbar with global year selector
│       ├── components/
│       │   ├── Heatmap.tsx  # SVG heatmap (React + d3-scale, DST-safe)
│       │   └── DataSection.tsx
│       └── hooks/
│           └── useMetricData.ts
├── config/
│   ├── config.toml          # Production config
│   ├── test.toml            # Local/test config
│   └── cors.json            # R2 CORS rules
└── .github/workflows/
    ├── pipeline.yml         # Weekly pipeline (every Monday 02:00 UTC)
    └── deploy.yml           # Deploy website on push to main
```
