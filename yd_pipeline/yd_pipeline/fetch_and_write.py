import sqlite3
import json
import os

endpoints = {
    "workout_data_daily": "/workout-data",
    "workout_distinct_workouts": "/distinct-workouts",
    "workout_distinct_exercises": "/distinct-exercises",
    "kindle_data_daily": "/kindle-data",
    "kindle_distinct_books": "/distinct-kindle-books",
    "github_data_daily": "/github-data",
    "github_distinct_repos": "/distinct-github-repos",
    "fitbit_sleep_data_processed": "/sleep-data",
    "fitbit_calorie_data_processed": "/calorie-data",
    "fitbit_steps_data_processed": "/steps-data",
    "fitbit_running_data_processed": "/running-data"
}

def fetch_data_from_db(db_path, output_dir):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for table_name in endpoints.keys():
        # Query to fetch all data from the table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Convert to JSON
        data = [dict(zip(column_names, row)) for row in rows]
        
        # Only get values for distinct categories.
        if ("latest_date" in column_names):  
            data = [row for row in data if row["latest_date"].startswith("2024")]

        # Write to a JSON file
        output_file = os.path.join(output_dir, f"{endpoints[table_name].replace("/","")}.json")
        with open(output_file, "w") as json_file:
            json.dump(data, json_file, indent=4)

    conn.close()

if __name__ == "__main__":
    # Path to your SQLite database
    db_path = "data/output/year_in_data.db"
    # Output directory for JSON files
    output_dir = "./data/output/"
    os.makedirs(output_dir, exist_ok=True)
    fetch_data_from_db(db_path, output_dir)
