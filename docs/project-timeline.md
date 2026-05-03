# Project timeline

> This was meant to be a week long project.

## 1 Pure Python Streamlit app

**Motivation:**
- GitHub activity heatmap is nice to look at, so why not do the same with Strong app workouts
- Didn't want to pay premium on Strong for the pretty graphs

**Result:**
- Built a Python pipeline to ETL Strong workout data
- Built a Streamlit app to handle file upload and display Matplotlib plots

## 2 JS interactivity using cal-heatmap

**Motivation:**
- Wanted the heatmap to have the same interactivity as the GitHub heatmap
- Wanted to visualise more data sources (Fitbit, Kindle)

**Result:**
- Created a static website using Vite + React + TypeScript
- Used the cal-heatmap library for interactive heatmaps
- Ran the Python pipeline manually to generate heatmap data
- Stored heatmap data on the GitHub repo
- Built and hosted the website on Vercel

## 3 FastAPI backend

**Motivation:**
- Wanted to learn FastAPI and VPS hosting
- Thought an API would improve data privacy (no more data on the GitHub repo)

**Result:**
- Site still hosted on Vercel
- Built a FastAPI backend hosted on a DigitalOcean VPS
- API processed input data and stored it on the VPS
- Fetched heatmap data from the API using Axios

## 4 GitHub Actions, D3, Tailwind

**Motivation:**
- Wanted to learn CI/CD
- Wanted to learn D3 and Tailwind
- Realised the API was redundant since the public website exposed the data anyway

**Result:**
- Dropped the API
- Stored raw input data in Google Drive
- Automated the Python pipeline to run every month with GitHub Actions
- Automated deploying the updated static site to GitHub Pages

## 5 Cloudflare R2, structured pipeline 

**Motivation:**
- Wanted easier access to macOS screen time (local file system access useful)
- Wanted a properly structured, testable pipeline
- Wanted to learn more about data lakes and using (proper) cloud storage

**Result:**
- Created local cron job to extract macos screen time and command history
- Replaced Google Drive with Cloudflare R2 free tier (S3-compatible)
- Rewrote pipeline with Polars, seperated pipeline into 2 different jobs
- Added local MinIO dev environment for testing without real R2

