from fastapi import FastAPI, Query
from typing import List, Optional
import sqlite3

app = FastAPI()

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('data/output/year_in_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get('/workout-data', response_model=List[dict])
def get_heatmap_data(year: Optional[int] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM workout_data"

    if year:
        query += " WHERE strftime('%Y', date) = ?"
        rows = cursor.execute(query, (str(year),)).fetchall()
    else:
        rows = cursor.execute(query).fetchall()
    
    conn.close()
    
    return [dict(row) for row in rows]