
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# EcoAir | Open-Meteo Exploratory Data Analysis
# =========================================================

INPUT_FILE = "air_quality_openmeteo_raw.csv"

OUTPUT_FILES = {
    "statistics": "openmeteo_descriptive_statistics.csv",
    "missing": "openmeteo_missing_values.csv",
    "pm25": "openmeteo_pm25_trend.png",
    "pm10": "openmeteo_pm10_trend.png",
    "correlation": "openmeteo_correlation_matrix.csv",
    "heatmap": "openmeteo_correlation_heatmap.png",
}

POLLUTANTS = [
    "pm10",
    "pm2_5",
    "ozone",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "carbon_dioxide",
]


def print_heading(title):
    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)


def save_trend(df, column, filename, title, color):
    """Create and save a pollutant trend chart."""

    if column not in df.columns:
        print(f"Skipping {column}: column not found.")
        return

    plot_data = df[["time", column]].dropna().sort_values("time")

    if plot_data.empty:
        print(f"Skipping {column}: no valid observations.")
        return

    plt.figure(figsize=(13, 5))

    plt.plot(
        plot_data["time"],
        plot_data[column],
        color=color,
        linewidth=2,
        marker="o",
        markersize=2,
    )

    plt.title(title, fontsize=15, fontweight="bold")
    plt.xlabel("Date and time")
    plt.ylabel(f"{column.upper()} (µg/m³)")
    plt.xticks(rotation=40)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()

    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Chart saved: {filename}")


def main():

    print_heading("ECOAIR - OPEN-METEO DATA ANALYSIS")

    # -----------------------------------------------------
    # 1. Load dataset
    # -----------------------------------------------------

    print("\nLoading Open-Meteo dataset...")

    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} not found. Run extract_openmeteo.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("The Open-Meteo dataset is empty.")

    # Convert Unix timestamps into UTC datetime
    df["time"] = pd.to_datetime(
        df["time"],
        unit="s",
        errors="coerce",
        utc=True,
    )

    print_heading("DATASET INFORMATION")

    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nAvailable columns:")
    print(df.columns.tolist())

    # -----------------------------------------------------
    # 2. Select pollutant columns
    # -----------------------------------------------------

    pollutant_columns = [
        col for col in POLLUTANTS
        if col in df.columns
    ]

    if not pollutant_columns:
        raise ValueError("No pollutant columns were found.")

    for col in pollutant_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print("\nAvailable pollutants:")
    print(pollutant_columns)

    # -----------------------------------------------------
    # 3. Descriptive statistics
    # -----------------------------------------------------

    print_heading("DESCRIPTIVE STATISTICS")

    stats = df[pollutant_columns].describe().T.round(2)

    print(stats)

    stats.to_csv(OUTPUT_FILES["statistics"])

    print("\nStatistics saved:")
    print(OUTPUT_FILES["statistics"])

    # -----------------------------------------------------
    # 4. Missing value analysis
    # -----------------------------------------------------

    print_heading("MISSING VALUE ANALYSIS")

    missing = pd.DataFrame({
        "Missing Values": df.isnull().sum(),
        "Missing Percentage": (
            df.isnull().mean() * 100
        ).round(2),
    })

    print(missing)

    missing.to_csv(OUTPUT_FILES["missing"])

    print("\nMissing-value report saved:")
    print(OUTPUT_FILES["missing"])

    # -----------------------------------------------------
    # 5. PM2.5 trend
    # -----------------------------------------------------

    print_heading("PM2.5 TREND ANALYSIS")

    save_trend(
        df,
        "pm2_5",
        OUTPUT_FILES["pm25"],
        "Lahore PM2.5 Hourly Trend - Open-Meteo",
        "#DC2626",
    )

    # -----------------------------------------------------
    # 6. PM10 trend
    # -----------------------------------------------------

    print_heading("PM10 TREND ANALYSIS")

    save_trend(
        df,
        "pm10",
        OUTPUT_FILES["pm10"],
        "Lahore PM10 Hourly Trend - Open-Meteo",
        "#EA580C",
    )

    # -----------------------------------------------------
    # 7. Correlation analysis
    # -----------------------------------------------------

    print_heading("POLLUTANT CORRELATION ANALYSIS")

    correlation = df[pollutant_columns].corr(
        method="pearson",
        min_periods=2,
    )

    print(correlation.round(2))

    correlation.to_csv(OUTPUT_FILES["correlation"])

    print("\nCorrelation matrix saved:")
    print(OUTPUT_FILES["correlation"])

    # -----------------------------------------------------
    # 8. Correlation heatmap
    # -----------------------------------------------------

    plt.figure(figsize=(11, 8))

    plt.imshow(
        correlation,
        cmap="RdYlBu_r",
        vmin=-1,
        vmax=1,
        interpolation="nearest",
        aspect="auto",
    )

    plt.colorbar(label="Pearson Correlation")

    plt.xticks(
        range(len(correlation.columns)),
        correlation.columns,
        rotation=35,
        ha="right",
    )

    plt.yticks(
        range(len(correlation.index)),
        correlation.index,
    )

    # Display correlation values inside the heatmap
    for i in range(len(correlation.index)):
        for j in range(len(correlation.columns)):
            value = correlation.iloc[i, j]

            if pd.notna(value):
                plt.text(
                    j,
                    i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="black",
                )

    plt.title(
        "Open-Meteo Air Quality Pollutant Correlation",
        fontsize=15,
        fontweight="bold",
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FILES["heatmap"],
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print("\nCorrelation heatmap saved:")
    print(OUTPUT_FILES["heatmap"])

    # -----------------------------------------------------
    # 9. Final report
    # -----------------------------------------------------

    print_heading("ANALYSIS COMPLETED SUCCESSFULLY")

    print(f"Records analyzed: {len(df)}")
    print(f"Pollutants analyzed: {len(pollutant_columns)}")

    print("\nGenerated files:")

    for filename in OUTPUT_FILES.values():
        if Path(filename).exists():
            print(f"[OK] {filename}")
        else:
            print(f"[MISSING] {filename}")

    print("\nEcoAir Open-Meteo EDA completed!")


if __name__ == "__main__":
    main()
