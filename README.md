# years in data (2023, 2024, 2025)

Made this because I was too lazy to use habit tracker apps. 

Instead use data collected about me by big companies (They care so much about me 🥹). 

https://year-in-data.vercel.app/

(old) Preview | (old) Also preview
-|-
![demo](docs/page_1.jpg) | ![demo2](docs/page_2.jpg)



# Info
[How I went about extracting data](docs/GatheringData.md)

## Frontend
* D3.js + Tailwind + DaisyUI + React

## Backend
* Setup is a bit overkill but I wanted to learn more about APIs and hosting them.
* nginx + docker + fastapi 
* Gather data -> pandas dataframe -> apply transformations -> store in sqlite db.
* https://github.com/Aebel-Shajan/yd_backend 
* Hosted on Digital Ocean VPS droplet 
* Cloudflare for domain stuff
* Let's Encrypt (via Certbot) for https

## Todo:
* Dark mode broke
* Mobile broke

## In future
* Remake this with github actions to run pipeline using data from google drive. (Logical, efficient way of doing this :P)
