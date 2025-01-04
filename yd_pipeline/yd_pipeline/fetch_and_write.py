import sqlite3
import json
import os

def fetch_data_from_db(db_path, output_dir):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        # Query to fetch all data from the table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Convert to JSON
        data = [dict(zip(column_names, row)) for row in rows]

        # Write to a JSON file
        output_file = os.path.join(output_dir, f"{table_name}.json")
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
