# Year in Data

Personal activity heatmaps for GitHub contributions, Fitbit, Kindle, and Strong — visualised as annual SVG heatmaps on a GitHub Pages site.

The pipeline runs weekly via GitHub Actions, pulls raw exports from Cloudflare R2, processes them with Polars, and writes aggregated JSON back to R2. The React website fetches that JSON at runtime.

## Data sources

| Source | Export format |
|---|---|
| GitHub | Fetched automatically via GraphQL |
| Fitbit | Google Takeout zip |
| Kindle | Amazon data request zip |
| Strong | Strong app CSV export |

Upload exports to `raw/{source}/inbox/` in R2, or point `DRIVE_SHARE_URL` at a public Google Drive folder and run `make pipeline` to sync automatically.

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
  extractors/    fitbit, kindle, strong, github
  r2.py          storage operations
  main.py        entry point
scripts/
  sync_drive.py  sync Google Drive exports → R2 inbox
  setup_r2.py    one-time R2 bucket setup
  test_e2e.py    end-to-end test against local MinIO
notebooks/       data exploration
website/src/
  App.tsx        sticky navbar with global year selector
  components/    Heatmap, DataSection
config/          config.toml, test.toml, cors.json
```
