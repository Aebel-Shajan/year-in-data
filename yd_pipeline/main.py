from yd_pipeline.process_data.strong import (
    process_strong_data, 
    get_distinct_exercises,
    get_distinct_workouts
)
from yd_pipeline.process_data.kindle import process_kindle_data, get_distinct_books
from yd_pipeline.process_data.github import process_github_data, get_distinct_repos
from yd_pipeline.process_data.fitbit import (
    process_sleep_data, 
    process_calorie_data,
    process_steps,
    process_running
)
from pathlib import Path
import os
from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parent

data_file_path = root_dir / "data" / "input"

# ETL strong data
strong_data_filepath = data_file_path / "strong1918192963746116310.csv"
with open(strong_data_filepath) as strong_csv:
    process_strong_data(strong_csv)
    get_distinct_workouts()
    get_distinct_exercises()

# ETL kindle data
kindle_data_filepath = (
    data_file_path
    / "Kindle"
    / "Kindle.ReadingInsights"
    / "datasets"
    / "Kindle.reading-insights-sessions_with_adjustments"
    / "Kindle.reading-insights-sessions_with_adjustments.csv"
)
with open(kindle_data_filepath) as kindle_csv:
    process_kindle_data(kindle_csv)
    get_distinct_books()

# ETL github data
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
load_dotenv()
process_github_data("aebel-shajan", os.getenv("GITHUB_TOKEN"))

# ETL fitbit data
fitbit_data_folderpath = (
    data_file_path 
    / "Takeout" 
    / "Fitbit" 
    / "Global Export Data" 
)
process_sleep_data(fitbit_data_folderpath)
process_calorie_data(fitbit_data_folderpath)
process_steps(fitbit_data_folderpath)
process_running(fitbit_data_folderpath)