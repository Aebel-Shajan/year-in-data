# Year in data

Electron to visualise a bunch of stuff from last year (2025).

## docs
* [devlog](./docs/devlog.md)
* [wireframe](./docs/wireframe.excalidraw.json)
* notebooks:
  * [chatgpt](./notebooks/chatgpt.ipynb)


## Tech used
q) how many npm packages? </br>
a) yes

Tech | use
-|-
typescript | nicer to work with than js. Has types
react | used to build reusable UI components
vite | build tool used to turn tsx, html + css -> js + html + css. Also hmr + bundling dependencies
tailwind | no css files required, just use class names, good for prototyping. 
nodejs | allows you to run js outside browser
electron | lets you build cross platform desktop application use web tech. has its own version of chrome.

2 places ts runs in: Browser and node.

## Libs used

Libs |use
-|- 
d3 | has alot of functions useful for visualisation, kinda conflicts with react
recharts | built on d3 has prebuilt visualisations
radix | ui component library
shadcn | built on tailwind and radix, nice clean components

Maybe https://pola-rs.github.io/nodejs-polars/


## Setup 
0. Prereqs:
  * node: https://nodejs.org/en/download

1. clone switch to electron app branch 
```
git clone https://github.com/Aebel-Shajan/year-in-data.git
cd ./year-in-data
git checkout 4.0.0-electron-rewrite
```

2. install dependencies
```
npm i
```
3. run postinstall (to fix Electron + native module mismatch)
```
npm run postInstall 
```

4. run dev script 😺
```
npm run dev
```


## Folder structure
```shell
tree -L 2 -I "node_modules" --dirsfirst
.
├── dist-electron # build file
│   ├── etl
│   ├── electron-db.js
│   ├── main.js
│   ├── preload.cjs
│   └── util.js
├── docs # Docs / markdown dump
│   ├── devlog.md
│   └── wireframe.excalidraw.json
├── public # public assets, should probs delete this
│   └── vite.svg
├── src 
│   ├── electron # Where electron ts code is 
│   └── ui # Where frontend react-ts code is
├── README.md 
├── components.json # config for shadcn
├── index.html # entry point for frontend
├── package-lock.json 
├── package.json # dependencies, node project metadata, scripts
├── tsconfig.app.json # ts config for frontend code in ui
├── tsconfig.json  # mostly for IDE
├── tsconfig.node.json # ts config for tooling (vite.config.ts)
└── vite.config.ts # config for vite
```

### `src/electron/`
```bash 
tree -L 2 --dirsfirst src/electron

src/electron
├── etl # ts scripts to etl data into sqlite db
│   └── screentime.ts
├── electron-db.ts 
├── main.ts # main process
├── preload.cts # pre load script
├── tsconfig.json # ts config for project
└── util.ts
```

### `src/ui`
```bash
tree -L 2 --dirsfirst src/ui      

src/ui
├── assets # assets stored
│   └── react.svg
├── components # ui components
│   ├── ui # shadcn components
│   ├── visualisations # year in data components
│   └── dark-mode-toggle.tsx
├── lib # common utils
│   └── utils.ts
├── App.tsx 
├── index.css # tailwind stuff in here
└── main.tsx # tsx entrypoint
```


