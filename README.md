# Year in Data

Made this because I was too lazy to use habit tracker apps — instead using data collected about me by big companies.

Personal activity heatmaps for GitHub contributions, Fitbit, Kindle, and Strong — visualised as annual SVG heatmaps on a GitHub Pages site.

The pipeline runs weekly via GitHub Actions, pulls raw exports from Cloudflare R2, processes them with Polars, and writes aggregated JSON back to R2. The React website fetches that JSON at runtime.

## Data sources

| Source | How to get the data | Frequency |
|---|---|---|
| **GitHub** | Fetched automatically via GraphQL API | Automated |
| **Fitbit** | [Google Takeout](https://takeout.google.com) → select Fitbit → download zip | Manual |
| **Kindle** | [Amazon data request](https://www.amazon.com/hz/privacy-central/data-requests/preview.html) → Reading Insights CSV | Manual |
| **Strong** | Strong app → Settings → Export Data → CSV | Manual |

Upload exports to `raw/{source}/inbox/` in R2, or point `DRIVE_SHARE_URL` at a public Google Drive folder and run `make pipeline` to sync automatically.

## R2 bucket layout

```
raw/{source}/inbox/                              ← drop new files here
raw/{source}/{YYYY-WXX}/                         ← archived after processing
processed/{source}/{metric}/{YYYY-WXX}.parquet   ← weekly Polars partitions
web/{source}/{metric}.json                       ← public JSON consumed by the website
```

## Quick start

```sh
cp .env.example .env   # fill in R2 credentials, GitHub token, Drive URL
uv sync
cd website && npm install

make up       # start local MinIO
make test     # run e2e test with fake data
make dev      # start Vite dev server
```

See `.env.example` for all available environment variables.

## Deploying

1. Add secrets to GitHub (*Settings → Secrets and variables → Actions*): `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`, `PIPELINE_GITHUB_TOKEN`, `GITHUB_USERNAME`, `DRIVE_SHARE_URL`
2. Run `make setup-r2` once to configure the R2 bucket policy and CORS
3. Enable GitHub Pages from the `gh-pages` branch

The pipeline runs every Monday at 02:00 UTC. The website deploys automatically on push to `main`.

## Project structure

```
pipeline/
  common/      config, r2 client, paths, bucket setup
  extract/     fitbit, kindle, strong, github, gymgroup, macos
  jobs/        extract, export, daily_aggregation orchestration
  main.py      entry point
scripts/
  sync_api.py            sync API-based sources → R2 inbox
  sync_macos.py          sync macOS exports → R2 inbox
  setup_r2.py            one-time R2 bucket setup
  generate_config_schema.py  regenerate config/schema.json from Pydantic models
  test_e2e.py            end-to-end test against local MinIO
config/
  config.yaml  production config
  test.yaml    local/test config
  schema.json  auto-generated JSON Schema (run generate_config_schema.py to update)
notebooks/     data exploration
website/src/
  App.tsx      sticky navbar with global year selector
  components/  Heatmap, DataSection
```
