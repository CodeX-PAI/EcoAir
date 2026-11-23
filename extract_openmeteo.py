import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_URL = os.getenv("OPENMETEO_API_URL")

def extract_openmeteo():

    if not API_URL:
        raise ValueError(
            "OPENMETEO_API_URL not found in .env file"
        )

    print("Fetching data from Open-Meteo...")

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    # Extract hourly measurements
    hourly = data.get("hourly", {})

    if not hourly or "time" not in hourly:
        raise ValueError("Hourly data is missing from API response.")

    df = pd.DataFrame(hourly)

    # Add location and source metadata
    df["latitude"] = data.get("latitude")
    df["longitude"] = data.get("longitude")
    df["source"] = "Open-Meteo"
    df["fetched_at_utc"] = pd.Timestamp.now(tz="UTC")

    # Save the extracted data
    output_file = "air_quality_openmeteo_raw.csv"

    df.to_csv(output_file, index=False)

    print("\nOpen-Meteo extraction completed!")
    print(f"Records extracted: {len(df)}")
    print(f"Available columns: {list(df.columns)}")
    print(f"File saved: {output_file}")

    print("\nFirst 5 records:")
    print(df.head())


if __name__ == "__main__":
    extract_openmeteo()