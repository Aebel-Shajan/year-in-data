import os
import sqlite3
import argparse
import csv
from io import StringIO

knowledge_db = os.path.expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")

def query_knowledge_database():
    # Check if knowledgeC.db exists
    if not os.path.exists(knowledge_db):
        print("Could not find knowledgeC.db at %s." % (knowledge_db))
        exit(1)

    # Check if knowledgeC.db is readable
    if not os.access(knowledge_db, os.R_OK):
        print("The knowledgeC.db at %s is not readable.\nPlease grant full disk access to the application running the script (e.g. Terminal, iTerm, VSCode etc.)." % (knowledge_db))
        exit(1)

    # Connect to the SQLite database
    with sqlite3.connect(knowledge_db) as con:
        cur = con.cursor()

        # Execute the SQL query to fetch data
        # Modified from https://rud.is/b/2019/10/28/spelunking-macos-screentime-app-usage-with-r/
        query = """
        SELECT
            ZOBJECT.ZVALUESTRING AS "app",
            (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "usage",
            (ZOBJECT.ZSTARTDATE + 978307200) as "start_time",
            (ZOBJECT.ZENDDATE + 978307200) as "end_time",
            (ZOBJECT.ZCREATIONDATE + 978307200) as "created_at",
            ZOBJECT.ZSECONDSFROMGMT AS "tz",
            ZSOURCE.ZDEVICEID AS "device_id",
            ZMODEL AS "device_model"
        FROM
            ZOBJECT
            LEFT JOIN
            ZSTRUCTUREDMETADATA
            ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
            LEFT JOIN
            ZSOURCE
            ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
            LEFT JOIN
            ZSYNCPEER
            ON ZSOURCE.ZDEVICEID = ZSYNCPEER.ZDEVICEID
        WHERE
            ZSTREAMNAME = "/app/usage" AND
            (ZOBJECT.ZCREATIONDATE + 978307200) > ?
        ORDER BY
            ZCREATIONDATE DESC
        """
        cur.execute(query, (0.0,))

        # Fetch all rows from the result set
        return cur.fetchall()

def write_to_csv(rows, output, delimiter):
    writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["app", "usage", "start_time", "end_time", "created_at", "tz", "device_id", "device_model"])
    writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="Query knowledge database")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("-d", "--delimiter", default=',', help="Delimiter for output file (default: comma)")
    args = parser.parse_args()

    # Prepare output format
    delimiter = args.delimiter.replace("\\t", "\t")

    # Check if file exists to decide whether to write headers
    file_exists = os.path.isfile(args.output)

    # Query the database and fetch the rows
    rows = query_knowledge_database()

    # Write the output to a file or print to stdout
    if args.output:
        with open(args.output, "a", newline='') as f:
            writer = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                writer.writerow(["app", "usage", "start_time", "end_time", "created_at", "tz", "device_id", "device_model"])
            writer.writerows(rows)
    else:
        output = StringIO()
        write_to_csv(rows, output, delimiter)
        print(output.getvalue())

if __name__ == "__main__":
    main()