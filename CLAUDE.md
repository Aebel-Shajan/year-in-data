# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (required after clone)
npm i
npm run postinstall  # Rebuilds native modules for Electron

# Development - runs Vite + Electron in parallel
npm run dev

# Build
npm run build                    # TypeScript + Vite build
npm run transpile:electron       # Compile only Electron TypeScript
npm run dist:mac                 # Build macOS distribution

# Lint
npm run lint
```

## Architecture

This is an Electron desktop app for visualizing personal data (screentime, ChatGPT messages, zsh history) from 2025. It uses a two-process architecture with IPC communication.

### Process Architecture

**Main Process** (`src/electron/`):
- `main.ts` - Electron entry point, creates BrowserWindow, loads renderer from Vite dev server (port 5123) or bundled files
- `preload.cts` - Exposes `window.electronAPI` to renderer via contextBridge
- `services.ts` - IPC handlers registered via `registerIpcHandlers()`, maps channel names to functions
- `electron-db.ts` - SQLite database initialization using better-sqlite3
- `sharedTypes.ts` - TypeScript types shared between main and renderer (IpcAPI interface)

**Renderer Process** (`src/ui/`):
- React app with Vite, uses `window.electronAPI` for all main process communication
- `App.tsx` - Simple page router using state (no hash router), declares `window.electronAPI` global type
- `pages/` - Dashboard components for each data source
- `components/visualisations/` - Reusable chart components (heatmap, barchart, treemap)
- `components/ui/` - shadcn/ui components

### ETL Pattern

Data sources follow ETL pattern in `src/electron/etl/`:
1. Each data source exports a SQL table creation string and an `etl*` function
2. `TABLE_ETL_MAP` in `services.ts` maps table names to ETL functions
3. ETL functions: extract from source → transform → load to SQLite
4. Tables are created on startup in `electron-db.ts`

### IPC Communication

The `IpcAPI` interface in `sharedTypes.ts` defines the contract:
- `runEtl(tableName, config)` - Run ETL for a data source
- `getDataByYear(tableName, year, dateColumn)` - Query data from SQLite
- `selectFile()` - Open file dialog
- `showDialogError(message)` - Show error dialog

### Path Alias

`@` maps to `src/ui/` in imports (configured in vite.config.ts).
