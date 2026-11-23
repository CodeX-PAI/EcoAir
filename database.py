
import sqlite3
import pandas as pd

INPUT_FILE = "air_quality_multi_station_clean.csv"
DATABASE_FILE = "air_quality.db"


def main():
    # Read the validated dataset
    df = pd.read_csv(INPUT_FILE)

    # Connect to SQLite; create the database if it does not exist
    connection = sqlite3.connect(DATABASE_FILE)

    try:
        # Store the data in a table named measurements
        df.to_sql(
            "measurements",
            connection,
            if_exists="replace",
            index=False,
        )

        # Check how many records were stored
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM measurements")
        total_records = cursor.fetchone()[0]

        print("Data successfully stored in SQLite.")
        print(f"Database: {DATABASE_FILE}")
        print(f"Table: measurements")
        print(f"Records stored: {total_records}")

        # Show the number of records for each pollutant/parameter
        cursor.execute("""
            SELECT parameter, COUNT(*)
            FROM measurements
            GROUP BY parameter
            ORDER BY parameter
        """)

        print("\nRecords by parameter:")
        for parameter, count in cursor.fetchall():
            print(f"{parameter}: {count}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
