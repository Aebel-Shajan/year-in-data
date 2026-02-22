# Devlog
Capture layer → fast, local, contextual


template:
```
## 2026-01-02
Start:
End:
What I want to do:
What I did:
What broke:
What I could do next:
Links:
```

## 2026-01-02
* git: afe04c17bf940b4979a86fbf2c38cc53691b2621
* Start: 20:18
* End: 22:47
* What I want to do: 
    * Setup boilerplate for electron app
    * Create wireframe for what ui should look like
    * Process screen time and display it on frontend
* What I did:
    * watched fcc youtube video for creating electron app
    * researched: https://www.react-graph-gallery.com/treemap
    * Migrated `heatmap-visual.tsx` from previous project
    * Create `screentime.ts` to read last 4 weeks of macos screen time
    * Made function `loadScreenTimeToDB` to push data sqlite database. 
    * Tried creating sqlite db in electrons proided `userData` folder
* What broke : 
    * Had to use npm package `electron-rebuild` to fix issue with `better-sqlite` not being able to be built
    * Couldn't understand ipc, tried extracting reading data from frontend from backend using ipcRenderer
* What I could do next:
    * Understand how the renderer interacts with electron main process
    * Refactor tooltips in `heatmap-visual.tsx`

## 2026-01-03
* git: af09265c7fa9cebd0f712ebb3725187d20d779b1
* Start: 13:53
* End: 15:45
* What I want to do:
    * Watch fcc tutorial to learn more about ipc messages
* What I did:
    * Created a preload script to expose `ipcRenderer.invoke` instead of calling them directlry from frontend. This fixed the compilation issues I had before.
* What broke: 
    * Syntax error in onclick function for extracting screen time. This wasted a couple mins rip.
* What I could do next: 
    * Fix the tooltips in svgs
    * Think about where to put "action" buttons for each type of data i want to extract/process
    * Add a tree map
* Links:
    * https://www.electronjs.org/docs/latest/tutorial/ipc
    * https://github.com/N-Ziermann-YouTube/electron-course/blob/main/src/electron/preload.cts


* git: 5f2ed61270edc83a050040a0f199c878afcdf12d
* Start: 19:00
* End: 22:04
* What I want to do:
    * Add tree map component to app
    * Move action button to menu bar at top of page instead of sidebar. (Don't abstract yet. Repeat yourself a couple of times to get the gist of what needs repeating and what doesn't.)
* What I did:
    * Installed d3 and created tree map component
    * Created new folder to contain all visualisations.
    * Moved action button to main container which contains title.
    * I installed recharts and added a barplot for montly data.
* What broke:
    * The text kept overflowing from outside the rectangle in the tree map. So I used clip masking to stop that. Also don't display text when rectangle can't contain it.
    * I tried to do a stacked barchart for each category but that adds uneeded complexity to everything
* What I could do next:
    * Add a tooltip to each rectangle.
    * Add a loading indicator and user feedback after user presses `extractScreenTime`
    * Migrate custom treemap component to use recharts version as it also has one with a tooltip.
* Links:
    * for tree map: https://www.react-graph-gallery.com/treemap
    * for clipping stuff contained in svg: https://gsap.com/community/forums/topic/16517-how-to-give-svg-element-overflow-hidden/
    * recharts: https://recharts.github.io/en-US/

## 2026-01-06
* git:caae669fe96e928d9316b447579f74d31e36f10f
* Start: 18:57
* End: 21:00
* What I want to do:
    * Add a new script to the package.json to rebuild sqlite dependency
    * Move logic for screentime into own page screenTimePage.tsx
    * Create new page for processing chatgpt history
* What I did:
    * Added "postInstall" to package.json
    * Updated Readme with a bunch of stuff
    * Researched chatgpt data.
    * watched ig reels
* What broke:  
    * me 
* What I could do next:
    * finish chatgpt processing script
* Links:


## 2026-01-07
* git: 829830892968b15f0f70eac0c7a66925f3cf7b68
* Start: 18:15
* End: 21:19
* What I want to do:
    * Start logging errors
    * Use polars to process chatgpt data
* What I did:
    * Created `docs/error-log.md`
    * Researched using deno for jupyter notebooks
    * Installed deno and the jupyter kernel using `deno jupyter --install`
    * Created `notebooks/chatgpt.ipynb` to play around with my chatgpt export data
* What broke:
    * Couldn't load data into a polars dataframe, because the datatype in one of my columns was whack.
* What next:
    * Investigate how to get intellisense for ts in deno jupyter notebooks. I actually had to look at docs 🥺🤢
    * Move over logic from notebook for chatgpt into its own script
* Links:
    * https://docs.deno.com/runtime/getting_started/installation/
    * https://docs.deno.com/runtime/reference/cli/jupyter/
    * https://marketplace.visualstudio.com/items?itemName=denoland.vscode-deno
    * https://docs.pola.rs/user-guide/expressions/aggregation/#basic-aggregations
    * https://pola-rs.github.io/nodejs-polars/interfaces/pl.DataFrame.html


## 2026-01-08
* git: 5b873aa797e3e7a55ad33462275c6fb2f9d74a0d
* Start: 20:22
* End: 23:35
* What I want to do:
    * Let the user pick a file from the file browser in electron
    * Process chatgpt zip in electron
* What I did:
    * Experimented using db migrations and failed.
    * Watch youtube shorts 
    * I seperated out the dashboards into their own components based on the data being displayed (No dry zone)
    * For the chatgpt message dashboard I added a button to open up a dialog and select a file. (much more complicated than i thought)
* What broke:
    * I realised doing `npm run transpile:electron` didn't also move the `.sql` files to the `dist-electron` folder, that put a stop in my plan to store sql schemas in `sql` files. Also stopped me from writing my own db migration scripts to version track schema changes for the sqlite db.
* What next:
    * finish etl script for chatgpt messages
    * add dashboards visuals to chatgpt message dashboard
    * maybe use drizzle / zod or something in the futre. cba now
* Links:
    * https://orm.drizzle.team/docs/get-started/sqlite-new
    * https://ui.shadcn.com/docs/components/dialog
    

## 2026-01-09
* git: e7698603b31e9344d2895911d388131b6c127202
* Start: 19:12
* End: 22:20
* What I want to do:
    * Dry `runEtl`, `getDataForYear` and `selectFile` functions in electron backend
    * Create interface `IpcApi` inside common types folder so it can be used by both frontend and backend.
    * Finish chatgpt etl script.
* What I did:
    * Created a framework (almost) for setting functions which are use by ipcMain and ipcRenderer.
    * Changed location of db to enable easier debugging
    * Created a shared types in `src/electron/sharedType.ts`
    * Used `dialog.showErrorBox` in main process to emulate `alert` in frontend.
    * Installed Electron fiddle, good for replicating behaviour from docs. 
* What broke:
    * When I tried to put the shared types in `src/sharedTypes.ts` the folder structure of the transpiled electron changes. As a result I had to update the `"main"` key in `package.json`. The next time i ran `npm run dev` I was not getting any electron logs in the terminal. I have no idea what caused this so I decided not to mess with the folder structure of the output electron js code in `dist-electron`.
* What next:
    * Finish chatgpt etl script.
* Links:
    * https://stackoverflow.com/questions/70552056/window-alert-for-electron-on-main-js
    * https://www.electronjs.org/fiddle


## 2026-01-10
* git: 5c4a61b133d113ffc1bc01a1f03f43ab8f026862
* Start: 14:46
* End: 18:39
* What I want to do:
    * Finish off etl script for chatgpt messages, add visuals to dashboard.
* What I did:
    * Finshed etl script for chatgpt messages
    * Realised the heatmap visual is not generic, it was tightly coupled to the screen time so this needs updating
    * had lunch (steak)
    * overthink architecture 
* What broke:
    * kept running into this error in frontend chatgpt-message-dashboard:
    ```
    Error invoking remote method 'runEtl': Error: An object could not be cloned.
    ```
    I don't know how to resolve this
* What next:
    * Refactor visuals to be more generic. make them accept data only in certain formats.
    * reduce complexity
    * Make unit tests for etl functions.
* Links:

## 2026-01-11
* git: 8c4c4edb0f8828a3de57902fccf4d6bc6441cfb6
* Start: 12:21
* End: 14:15
* What I want to do:
    * make heatmap generic. 
    * add tooltip to heatmap.
    * create functions to transform data from original format to format required by visuals.
    * save the logs from etl runs into a file/db.
    * render logs in real time to ui when run is initiated.
    * add filters
    * add a page to frontend to go through previous etl runs
    * decide if error log is worth it
* What I did:
    * make heatmap less generic
    * installed visx for heatmap. (yay another dependency!)
* What broke:
    * react dependency issue when installing visx
* What next:
    * add context to heatmap to get rid of prop drilling.
* Links:
    * https://visx.airbnb.tech/docs/tooltip


* git: 3732a99222da9de5620e8760fe094a4d90c7ed47
* Start: 17:36
* End: 20:17
* What I want to do:
    * add context to heatmap
* What I did:
    * Simplified nesting in heatmap-visual. using react context is overkill.
    * added tooltip to heatmap using visx
    * tried using recharts for treemap, but i couldn't get it to look colourful. It looked bland af. also the recharts tooltip kinda sucks.
    * was able to replicate the auto sizing i wanted from recharts treemap with `@visx/responsive`. visx > recharts
    * add a tooltip which follows the mouse.
    * watched a tonne of ig reels
* What broke:  
    * my attention span
* What next:
    * make heatmap responsive too
    * add zsh history etl
    * add etl logs (this can wait cus its boring)
* Links:
    * https://react.dev/learn/passing-data-deeply-with-context
    * https://visx.airbnb.tech/docs/responsive


## 2026-01-13
* git: 60f85885b78ae06643d90d7a47c7423585f42490
* Start: 21:06
* End: 22:56
* What I want to do:
    * create etl script to extract zsh history
* What I did:
    * made ts notebook to investigate zsh history data
* What broke:
    * coulnd't get plots to display
* What next:
    * try and get plots in ts notebook.
* Links:
    * https://deno.com/blog/exploring-art-with-typescript-and-jupyter
    * https://jsr.io/@manzt/jupyter-helper


## 2026-01-14
* git: 9aba048099d997210b27b615cd416a5b5fd95c81
* Start: 21:03
* End: 22:01
* What I want to do:
    * get plots in notebook
* What I did:
    * setup deno environment just for notebooks, no more polluting my project dependencies.
    * Doing this also fixed lack of intellisense in the notebooks. vscode detected deno.json wooo.
* What broke:
    * I couldn't figure out plotly so just asked claude instead
    * found out that on `Tuesday, 18 November 2025 19:26:08` I ran like 1000 commands at once. either that or an update mustve messed with my `.zsh_history` 😡
    * messed around with a bunch of plots
* What next:
    * move zsh history into own etl script
    * investigate if you can etl gym group api
* Links:
    * https://docs.deno.com/runtime/getting_started/first_project/
    * https://github.com/luke0x90/thegymgroup-api


## 2026-01-16
* git: 27f96059152bf9e95d167001d6b19aad2f918049
* Start: 17:12
* End: 18:07
* What I want to do:
    * move zsh history into own etl script
    * investigate if you can etl gym group api
* What I did:
    * Created dashboard page for zsh history
    * Found a way to use gym groups api from github 🤭. probably won't include this tho 
* What broke:
    * deno was installing packages into parent node module folder. Had to turn on `"nodeModulesDir": "manual"` to fix this
* What next:
    * macos battery?
    * resize heatmap
* Links:
    * https://github.com/luke0x90/thegymgroup-api/blob/main/example.py


## 2026-01-17
* git: aba6ee095931c2af940c5d61587669677f1ce31d
* Start: 19:45
* End: 22:03
* What I want to do:
    * make heatmap resizable using visx
* What I did:
    * made heatmap responsive, made it have a minimum width above which it resizes
    * made the barchart component abstract
    * added barcharts for hourly view
* What broke:
    * nothing 
* What next:
    * claude, gemini data?
    * fix dark mode 
* Links:


## 2026-01-18
* git: 1eb5d4431d3c5a043408fbea98391d9a890fcb6a
* Start:12:19
* End: 15:10
* What I want to do:
    * Etl hsbc bank statements
* What I did:
    * Shell out £180 😭 for personal Claude subscription and add `Claude.md`. 
    * Tried using pdf-parse
    * 
* What broke:
    * My bank account
    * `pdf-parse` extracted text but not in a structured way.
* What next:
    * Find an alternative to `pdf-parse`. maybe `pdf-dist` legacy
* Links:
    * https://dev.to/drsimplegraffiti/extract-texts-from-pdfs-383g
    * https://github.com/adrienjoly/HsbcStatementParser


* git: 9602dbf6b4d123a9cc9ef8adcff827486963e19e
* Start:17:00
* End: 21:37 
* What I want to do:
    * Try parsing hsbc statements.
    * Try using `pdf-dist` or `pdf2json`
* What I did:
    * pdf parsing is harder than i thought it would be. I was able to get text content out along with their x and y positions on the page. the statements came as tables, so i was able to leverage the column positions to get transaction date, type, detail and amount.
* What broke:
    * my bank account x2 (found out i have no money there). Could be because statement start in the middle of the month?? (why hsbc???)
    * I tried using `pdf2json` but the output was in a weird format.
    * `pdf-dist` is built for the browser, disabling workers meant i could get around and run on node. but i still get warnings which is pretty annoying.
* What next:
    * convert notebook to etl script
* Links:
    * https://www.npmjs.com/package/pdf2json
    * https://community.palantir.com/t/parsing-pdf-blob-with-pdfjs-dist/1195
    * https://github.com/mozilla/pdfjs-dist


## 2026-01-23
* git:?
* Start: 21:20
* End: 22:00
* What I want to do:
    * Try getting some good visuals for hsbc transactions
    * Make an abstract function for grouping by categories
* What I did:
    * did some transformations on frontend to map transactions into certain categories
    * converted to notebook into etl script
    * Cloned other dashboard to show hsbc transactions
* What broke:
* What next:
* Links:

## 2026-02-22 
* git: ba55d136f4ac9a695500d5f910186fcd2e7d8429
* Start: 11:00
* End:
* What I want to do:
    * Use claude code to wrap this project up 😔
    * Read kindle data
    * Claude data?
    * Record etl logs
* What I did:
    * Claude code


