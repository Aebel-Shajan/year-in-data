# Gathering data
For this app we will collect from different places. This document contains information
on how the data was collected.

## Github data
The github data was collected from the github graphql api. The query I used is in 
`yd_pipeline/yd_pipeline/graphql/github_user_contributions`.

You could also use the REST api too, but I found you had to make multiple requests to 
get the same results. 

Links:
* [REST api](https://docs.github.com/en/rest?apiVersion=2022-11-28)
* [GRAPHQL api](https://docs.github.com/en/graphql)
* [GRAPHQL Explorer](https://docs.github.com/en/graphql/overview/explorer)


## Workout data
This was the easiest data to collect. I used the [strong app](https://www.strong.app/)
to track my workouts. In the app theres an option to download my workout data as a csv.
After downloading the csv I sent an email to my laptop. I tried looking online for an 
api I could use, but there doesn't currently seem to be one. However I found that the
HEVY app has one, so I might use that to track my workouts next year.

## Kindle data
The kindle app already had an activity tracker thing in app, so I assumed the process of
looking through my data would be simple enough. However I could not find an api I could 
use to extract key data like reading minutes and book asins.

Instead I had to request my kindle data manually and wait around 1 or 2 days to download.
The data came in a zip file which I had to extract. There was a lot of data I had to sift
through to get what I wanted, but in the end I was able to get the reading sessions/activity
over the last year. I tried getting the progress of each book I had read, but I couldn't
find a way to do this.

Links:
* [Request kindle data](https://www.amazon.co.uk/hz/privacy-central/data-requests/preview.html)

## Fitbit data
The fitbit app also has an in app activity tracker. Fitbit does have an api but it requires
oauth2 authorisation and I couldn't be bothered to do all that. Instead I requested my 
data from google. This again came in a zip file containing csvs and jsons. 

From the fitbit data I can extract the following:
* sleep
* calories
* steps
* heart rate
* running activity
* oxygen saturation (I have no idea what this is used for??)

Links:
* [Request fitbit data](https://takeout.google.com/)

## MacOs screen time
This was the hardest peice of data to collect. The screen time page in the settings shows
app and website usage with charts and bars. Trying to get the data in csv was painful, 
I lookedonline for an answer but I found most answers to be out of date. So I resorted 
to using chatgpt which recommended I do a grep command to find all files ending in `.db`
to find all the sqlite3 files on my mac. I had some success with this but I couldn't 
decipher which tables where useful in a given database.

Then, after surfing the web for a couple hours, I came across this article:
https://felixkohlhas.com/projects/screentime/

which had I exactly what I was looking for.

Apparently the screen data was stored in the following database:

`~/Library/Application Support/Knowledge/knowledgeC.db`.

One limitation, is that macOS only stores the last 4 weeks worth of data. So its pretty
useless to do an annual heatmap for this years data. In the article it said something
about setting up a cron job every day to extract and store the data in a db. I might do
this to get data for next year.

Although tbf I got my Macbook at the end of October so there would have only been 3 months
worth of data to analyse. I might look into seeing if I can get screen time from my old
windows laptop.

Links:
* [Python code to extract screen time](https://github.com/FelixKohlhas/ScreenFlux)