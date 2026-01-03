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

