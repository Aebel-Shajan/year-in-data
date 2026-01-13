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

## 2025-01-03
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

## 2025-01-06
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


## 2025-01-07
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


## 2025-01-08
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
    

## 2025-01-09
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


## 2025-01-10
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

## 2025-01-11
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


## 2025-01-13
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