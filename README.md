# years in data (2023, 2024, 2025)

Made this because I was too lazy to use habit tracker apps. 

Instead use data collected about me by big companies. 

https://aebel-shajan.github.io/year-in-data/

(old) Preview | (old) Also preview
-|-
![demo](docs/page_1.jpg) | ![demo2](docs/page_2.jpg)



# Info
[How I went about extracting data](docs/GatheringData.md)

## Frontend
* React Typescript
* D3.js + Tailwind + DaisyUI

## Backend
* Google drive for storage
* python
* pandas + pandera
* github actions to run pipeline every month

## Todo :
- [ ] Mac os screen time
- [ ] Board game matches
- [x] Use github pages instead of vercel
- [ ] Scrape image links into gh-pages branch (no more getting rate limited)
- [ ] Add barcharts back in for more detailed view. (maybe)


## Data assets:
```mermaid
---
config:
  look: classic
  layout: dagre
---
flowchart TD
    n1["multiple amazon zips"] --> n2["kindle reading session csv"] & n3["Digital content ownership jsons"]
    n2 --> n4["raw_kindle_reading"]
    n3 --> n5["raw_asin_map"]
    n4 --> n6["kindle_reading"]
    n9["github graphql api credentials (in env file)"] --> n8["github repo response jsons"]
    n7["multiple google zip"] --> n10["Fitbit calories jsons"] & n11["Fitbit exercise jsons"] & n12["Fitbit sleep jsons"] & n13["Fitbit steps jsons"] & n24["youtube watch history html"]
    n8 --> n14["raw_github_repo_contributions"]
    n14 --> n15["github_repo_contributions"]
    n10 --> n16["raw_fitibit_calories"]
    n16 --> n17["fitbit_calories"]
    n18["raw_fitibit_exercise"] --> n19["fitbit_exercise"]
    n11 --> n18
    n20["raw_fitbit_sleep"] --> n21["fitbit_sleep"]
    n22["raw_fitbit_steps"] --> n23["fitbit_steps"]
    n12 --> n20
    n13 --> n22
    n24 --> n25["raw_youtube_watch_history"]
    n25 --> n26["youtube_watch_history"]
    n27["multiple strong csvs"] --> n31["latest valid strong csv"]
    n31 --> n28["raw_strong_workouts"]
    n32["multiple app usage csvs"] --> n33["app usage activity csv"] & n34["app usage app info csv"]
    n33 --> n35["raw_app_usage_screen_time"]
    n34 --> n36["raw_app_info"]
    n35 --> n37["app_usage_screen_time"]
    n36 --> n38["app_usage_app_info"]
    n37 --> n39["app_usage_screen_time_with_images"]
    n38 --> n39
    n28 --> n29["strong_workouts"] & n30["strong_exercises"]
    n5 --> n41["kindle_asin_map"]
    n6 --> n42["kindle_reading_with_images"]
    n41 --> n42
    n40["Gold should have:<br>* date column<br>* value column (optionally multiple)<br>* category column (optional)<br>* start_time column (optional)<br>* end_time column (optional)<br>* image column (optional)"]
    n1@{ shape: docs}
    n2@{ shape: doc}
    n3@{ shape: docs}
    n4@{ shape: db}
    n5@{ shape: cyl}
    n6@{ shape: cyl}
    n9@{ shape: doc}
    n8@{ shape: docs}
    n7@{ shape: docs}
    n10@{ shape: docs}
    n11@{ shape: docs}
    n12@{ shape: docs}
    n13@{ shape: docs}
    n24@{ shape: doc}
    n14@{ shape: db}
    n15@{ shape: cyl}
    n16@{ shape: cyl}
    n17@{ shape: cyl}
    n18@{ shape: cyl}
    n19@{ shape: cyl}
    n20@{ shape: cyl}
    n21@{ shape: cyl}
    n22@{ shape: cyl}
    n23@{ shape: cyl}
    n25@{ shape: db}
    n26@{ shape: db}
    n27@{ shape: docs}
    n31@{ shape: doc}
    n28@{ shape: cyl}
    n32@{ shape: docs}
    n35@{ shape: cyl}
    n36@{ shape: cyl}
    n37@{ shape: cyl}
    n38@{ shape: cyl}
    n39@{ shape: cyl}
    n29@{ shape: cyl}
    n30@{ shape: cyl}
    n41@{ shape: cyl}
    n42@{ shape: cyl}
    n40@{ shape: text}
     n1:::Bronze
     n2:::Bronze
     n3:::Bronze
     n4:::Silver
     n5:::Silver
     n6:::Gold
     n9:::Bronze
     n8:::Bronze
     n7:::Bronze
     n10:::Bronze
     n11:::Bronze
     n12:::Bronze
     n13:::Bronze
     n24:::Bronze
     n14:::Silver
     n15:::Gold
     n16:::Silver
     n17:::Gold
     n18:::Silver
     n19:::Gold
     n20:::Silver
     n21:::Gold
     n22:::Silver
     n23:::Gold
     n25:::Silver
     n26:::Gold
     n27:::Bronze
     n31:::Bronze
     n28:::Silver
     n32:::Bronze
     n33:::Bronze
     n34:::Bronze
     n35:::Silver
     n36:::Silver
     n37:::Gold
     n38:::Gold
     n38:::Silver
     n39:::Gold
     n29:::Gold
     n30:::Gold
     n41:::Gold
     n41:::Silver
     n42:::Gold
     n40:::Peach
     n40:::Bronze
     n40:::Gold
    classDef Peach stroke-width:1px, stroke-dasharray:none, stroke:#FBB35A, fill:#FFEFDB, color:#8F632D
    classDef Bronze fill:#FFE0B2
    classDef Silver fill:#757575, stroke:#424242, color:#FFFFFF
    classDef Gold fill:#FFD600, stroke:#000000, color:#000000

```
