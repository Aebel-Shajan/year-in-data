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
```

## 2026-01-02
git: afe04c17bf940b4979a86fbf2c38cc53691b2621
Start: 20:18
End: 22:47
Context: Want to build electron app for reviewing my last year in data
What I want to do: 
* Setup boilerplate for electron app
* Create wireframe for what ui should look like
* Process screen time and display it on frontend
What I did:
* watched fcc youtube video for creating electron app
* researched: https://www.react-graph-gallery.com/treemap
* Migrated `heatmap-visual.tsx` from previous project
* Create `screentime.ts` to read last 4 weeks of macos screen time
* Made function `loadScreenTimeToDB` to push data sqlite database. 
* Tried creating sqlite db in electrons proided `userData` folder
What broke : 
* Had to use npm package `electron-rebuild` to fix issue with `better-sqlite` not being able to be built
* Couldn't understand ipc, tried extracting reading data from frontend from backend using ipcRenderer
What I could do next:
* Understand how the renderer interacts with electron main process
* Refactor tooltips in `heatmap-visual.tsx`


