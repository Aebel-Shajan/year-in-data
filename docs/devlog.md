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

