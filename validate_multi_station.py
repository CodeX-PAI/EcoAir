import pandas as pd
from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import datetime


# Define the expected structure and validation rules for one measurement.
class AirQualityRecord(BaseModel):

    location_name: str = Field(min_length=1)
    location_id: int = Field(gt=0)
    sensor_id: int = Field(gt=0)
    parameter: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False)

    datetime_utc: datetime
    datetime_local: datetime
    fetched_at_utc: datetime

    # Validate measurements according to their parameter type.
    @field_validator("value")
    @classmethod
    def validate_parameter_value(cls, value, info):

        parameter = info.data.get("parameter")

        if parameter in ["pm1", "pm25", "um003"]:
            if value < 0:
                raise ValueError(
                    f"{parameter} cannot be negative"
                )

        elif parameter == "relativehumidity":
            if not 0 <= value <= 100:
                raise ValueError(
                    "Relative humidity must be between 0 and 100"
                )

        elif parameter == "temperature":
            if not -50 <= value <= 80:
                raise ValueError(
                    "Temperature must be between -50 and 80"
                )

        return value


def main():

    input_file = "air_quality_multi_station_raw.csv"
    output_file = "air_quality_multi_station_clean.csv"
    error_file = "air_quality_validation_errors.csv"

    # Load the raw dataset.
    df = pd.read_csv(input_file)

    valid_records = []
    invalid_records = []

    duplicate_count = 0

    # Identify duplicate measurements.
    duplicate_columns = [
        "location_id",
        "sensor_id",
        "parameter",
        "datetime_utc",
    ]

    duplicates = df.duplicated(
        subset=duplicate_columns,
        keep="first"
    )

    duplicate_indices = set(df.index[duplicates])

    # Validate each row separately.
    for index, row in df.iterrows():

        # Reject duplicate records.
        if index in duplicate_indices:
            duplicate_count += 1

            invalid_records.append(
                {
                    "row_number": index + 2,
                    "error": "Duplicate measurement record"
                }
            )
            continue

        try:

            # Convert the row into a validated Pydantic model.
            record = AirQualityRecord.model_validate(
                row.to_dict()
            )

            valid_records.append(record.model_dump())

        except (ValidationError, ValueError, TypeError) as error:

            invalid_records.append(
                {
                    "row_number": index + 2,
                    "error": str(error)
                }
            )

    # Save valid records.
    if valid_records:

        clean_df = pd.DataFrame(valid_records)

        clean_df.to_csv(
            output_file,
            index=False
        )

    else:

        print("No valid records were found.")

    # Save validation errors.
    if invalid_records:

        errors_df = pd.DataFrame(invalid_records)

        errors_df.to_csv(
            error_file,
            index=False
        )

    # Display validation summary.
    print("\n" + "=" * 40)
    print("       ECOAIR DATA VALIDATION")
    print("=" * 40)

    print(f"Total input records: {len(df)}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Invalid records: {len(invalid_records)}")
    print(f"Duplicate records: {duplicate_count}")

    print(
        f"Validation success rate: "
        f"{(len(valid_records) / len(df) * 100) if len(df) else 0:.2f}%"
    )

    if valid_records:
        print(f"\nClean dataset saved to: {output_file}")

    if invalid_records:
        print(f"Errors saved to: {error_file}")

        print("\nFirst 10 validation errors:")

        for item in invalid_records[:10]:

            print(
                f"Row {item['row_number']}: "
                f"{item['error']}"
            )

    print("\nValidation process completed.")


if __name__ == "__main__":
    main()