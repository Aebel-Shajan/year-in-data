export interface WorkoutData {
  "date": string,
  "workout_name": string,
  "exercise_name": string,
  "workout_duration_minutes": number,
  "volume": number
}

export interface ReadingData {
  "date": string,
  "total_reading_minutes": number
  "ASIN": string,
}

export interface DistinctBooks {
  "index": number,
  "ASIN": string,
  "total_reading_minutes": number,
  "latest_date": string,
  "book_image":string,
}

export interface GithubData {
  "date": string,
  "repository_name": string,
  "repository_url": string,
  "repository_image": string,
  "total_commits": string,
}

export interface DistinctRepos {
  "index": number,
  "latest_date": string,
  "repository_name": string,
  "repository_url": string,
  "repository_image": string,
}

export interface SleepData {
  "date": string,
  "start_time": string,
  "end_time": string,
  "total_duration_hours": number
}