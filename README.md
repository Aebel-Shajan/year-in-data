# Year in Data

Made this because I was too lazy to use habit tracker apps, instead using data collected about me by big companies.

Personal activity heatmaps for GitHub contributions, Fitbit, Garmin, Kindle, Strong, Gym Group and macOS screen time, visualised as annual SVG heatmaps on a GitHub Pages site.

The pipeline runs weekly via GitHub Actions, pulls raw exports from Cloudflare R2, processes them with Polars, and writes aggregated JSON back to R2. The React website fetches that JSON at runtime.


## Data sources

| Source | How to get the data | Frequency |
|---|---|---|
| **GitHub** | Fetched automatically via GraphQL API | Automated |
| **Garmin** | Fetched automatically via `garminconnect` Python library | Automated |
| **Gym Group** | Fetched automatically via Gym Group API | Automated |
| **macOS screen time** | Collected automatically via local cron job (`make install-macos-cron`) | Automated |
| **macOS shell history** | Collected automatically via local cron job | Automated |
| **Fitbit** | [Google Takeout](https://takeout.google.com) → select Fitbit → download zip | Manual |
| **Kindle** | [Amazon data request](https://www.amazon.com/hz/privacy-central/data-requests/preview.html) → Reading Insights CSV | Manual |
| **Strong** | Strong app → Settings → Export Data → CSV | Manual |

## Quick start

```sh
cp .env.example .env   # fill in credentials (see below)
uv sync
cd website && npm install

make up       # start local MinIO
make test     # run e2e test with fake data
make dev      # start Vite dev server
```

### Environment variables

| Variable | Description |
|---|---|
| `R2_ENDPOINT_URL` | Cloudflare R2 endpoint URL |
| `R2_ACCESS_KEY_ID` | R2 access key |
| `R2_SECRET_ACCESS_KEY` | R2 secret key |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token (for bucket setup) |
| `PIPELINE_GITHUB_TOKEN` | GitHub personal access token (for contributions) |
| `GARMIN_USERNAME` | Garmin Connect email |
| `GARMIN_PASSWORD` | Garmin Connect password |
| `GYM_GROUP_USERNAME` | Gym Group account email |
| `GYM_GROUP_PASSWORD` | Gym Group account password |

## Deploying

1. Add the environment variables above as GitHub secrets (*Settings → Secrets and variables → Actions*)
2. Run `make setup-r2` once to configure the R2 bucket policy and CORS
3. Run `make sync-secrets` to push your local `.env` to GitHub secrets in one go
4. Enable GitHub Pages from the `gh-pages` branch

The pipeline runs every Monday at 02:00 UTC. The website deploys automatically on push to `main`.

## Project structure

```
pipeline/
  common/      config, r2 client, paths, bucket setup
  extract/     fitbit, garmin, kindle, strong, github, gymgroup, macos
  jobs/        extract, export, daily_aggregation orchestration
  main.py      entry point
scripts/
  sync_api.py      sync API-based sources (Garmin, GitHub, Gym Group) to R2 inbox
  sync_macos.py    sync macOS screen time and shell history to R2 inbox
  sync_secrets.sh  push .env variables to GitHub Actions secrets
  setup_r2.py      one-time R2 bucket setup
  test_e2e.py      end-to-end test against local MinIO
config/
  config.yaml  production config
  test.yaml    local/test config
notebooks/     data exploration (visible in the Docs tab on the website)
website/src/
  App.tsx               sticky navbar, year selector, tab navigation
  components/           Heatmap, DataSection, DocsPage, NotebookViewer
```

## License

GNU General Public License v3.0. Derivative works must also be open source under the same license. See [LICENSE](LICENSE).
