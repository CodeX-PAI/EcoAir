# 🌱 EcoAir — Air Quality & Environmental Analytics Dashboard

An environmental data analytics project that collects, validates, analyzes, and visualizes air pollution data from multiple sources. EcoAir combines air quality measurements, multi-station comparisons, statistical analysis, and interactive visualizations to help explore pollution patterns and environmental conditions.

Built as a **Programming for AI — ETL + EDA Pipeline Project**.

---

## 📌 Project Overview

Air pollution is a significant environmental and public health concern. Monitoring pollutants such as PM2.5, PM10, ozone, nitrogen dioxide, and sulfur dioxide helps understand environmental conditions and identify pollution patterns.

EcoAir provides a data-driven approach to air quality analysis by integrating datasets from OpenAQ and Open-Meteo. The project applies data extraction, cleaning, validation, storage, exploratory data analysis (EDA), and interactive visualization through a Streamlit dashboard.

The dashboard allows users to explore pollution trends, compare monitoring stations, examine statistical summaries, and investigate environmental data interactively.

---

## 🎯 Project Objectives

- Collect environmental and air quality data through APIs.
- Implement an ETL pipeline for data extraction, transformation, validation, and storage.
- Validate data quality using **Pydantic**.
- Process and analyze datasets using **Pandas**.
- Store structured air quality measurements in an SQLite database.
- Perform exploratory data analysis (EDA) to identify trends, distributions, missing values, and relationships between environmental variables.
- Compare air quality measurements across monitoring stations.
- Build an interactive dashboard using Streamlit and Plotly.

---

## 📡 Data Sources

### 1. OpenAQ

[OpenAQ](https://openaq.org/) provides air quality data collected from monitoring stations.

EcoAir uses OpenAQ data for multi-station air quality analysis.

**Parameters included in the collected dataset:**

- PM1
- PM2.5
- Temperature
- Relative Humidity
- UM003

**Monitoring stations included:**

- ARC
- IEEE – Punjab University
- Sandha Road
- Gulberg III

The collected multi-station dataset contains **940 records** from four monitoring stations.

### 2. Open-Meteo Air Quality API

[Open-Meteo](https://open-meteo.com/) provides atmospheric and air quality data through its API.

EcoAir uses this dataset for pollutant analysis and environmental trend exploration.

**Pollutants analyzed:**

- PM10
- PM2.5
- Ozone (O₃)
- Nitrogen Dioxide (NO₂)
- Sulphur Dioxide (SO₂)
- Carbon Dioxide (CO₂)

The Open-Meteo dataset contains **336 records** and 11 columns, including timestamps, pollutant measurements, geographic coordinates, and data source information.

---

## ⚙️ ETL Pipeline

EcoAir implements an Extract, Transform, and Load (ETL) workflow to process environmental data.

### 1. Extract

Data is collected from API sources.

- Retrieve air quality measurements from OpenAQ.
- Retrieve pollutant data from Open-Meteo.
- Store the extracted data in raw CSV files for further processing.

### 2. Transform & Validate

The collected data is processed using Pandas and validated using Pydantic.

The transformation and validation process includes:

- Structuring raw API responses.
- Checking data types and required fields.
- Validating measurement records.
- Identifying invalid values and inconsistencies.
- Processing timestamps.
- Preparing cleaned datasets for analysis and storage.

### 3. Load

Validated OpenAQ data is stored in an SQLite database.

- Database: `air_quality.db`
- Table: `measurements`

The database currently contains **940 validated records**.

Cleaned datasets are also exported to CSV files for analysis and reuse.

---

## 🧹 Data Validation

EcoAir uses **Pydantic** to validate collected air quality records.

Validation helps ensure that data conforms to the expected structure and types before it is used for analysis.

The validation pipeline checks data records and separates valid data from invalid records where applicable.

### OpenAQ validation results

| Metric | Result |
|---|---:|
| Total records processed | 940 |
| Valid records | 940 |
| Invalid records | 0 |
| Duplicate records | 0 |
| Validation success | 100% |

The validated records are exported into a cleaned CSV dataset and loaded into SQLite.

Data validation is important because environmental datasets may contain missing values, inconsistent formats, unexpected readings, or invalid measurements that can affect analytical results.

---

## 📊 Exploratory Data Analysis (EDA)

EcoAir performs structured exploratory data analysis using Pandas and visualization libraries.

### OpenAQ Analysis

The multi-station dataset is used to investigate:

- Air quality variations across monitoring stations.
- PM2.5 measurement distributions.
- Differences in pollution levels between locations.
- Pollution trends over time.
- Station-level descriptive statistics.
- Comparison of environmental measurements across stations.

### Open-Meteo Analysis

The Open-Meteo dataset is used to explore:

- Pollutant distributions.
- PM2.5 trends.
- PM10 trends.
- Missing data patterns.
- Correlations between pollutant measurements.
- Relationships between different atmospheric pollutants.

### Statistical Analysis

The project calculates descriptive statistics such as:

- Mean
- Median
- Minimum
- Maximum
- Standard deviation
- Missing-value counts
- Correlation values

### Key OpenAQ PM2.5 Station Statistics

| Monitoring Station | Mean PM2.5 |
|---|---:|
| Sandha Road | 60.00 |
| IEEE – Punjab University | 70.66 |
| ARC | 73.80 |
| Gulberg III | 79.99 |

These statistics provide a comparison of PM2.5 measurements across the selected monitoring stations within the collected dataset.

---

## 📈 Dashboard Features

EcoAir provides an interactive dashboard built using **Streamlit** and **Plotly**.

The dashboard is organized into five main sections:

### 1. Overview

- Project overview.
- Environmental data summary.
- Key statistical metrics.
- Main dashboard visualizations.

### 2. OpenAQ Trends

- Multi-station air quality analysis.
- PM2.5 trends.
- Station-level exploration.
- Pollution data visualizations.

### 3. Open-Meteo Analysis

- Pollutant data exploration.
- PM2.5 and PM10 trends.
- Atmospheric pollutant comparisons.
- Statistical analysis.

### 4. Compare Stations

- Compare air quality measurements across monitoring stations.
- Explore differences in station-level pollution statistics.
- Visual comparison of available measurements.

### 5. Data Explorer

- Interactive data exploration.
- Filter available measurements.
- Inspect collected records.
- Explore the underlying datasets.

Additional dashboard functionality includes interactive charts, filters, statistical summaries, and data exploration.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data cleaning, transformation, and analysis |
| NumPy | Numerical operations |
| Pydantic | Data validation and schema enforcement |
| SQLite | Structured data storage |
| Streamlit | Interactive dashboard development |
| Plotly | Interactive data visualizations |
| Matplotlib | Exploratory data visualizations |
| Requests | API data retrieval |
| OpenAQ API | Multi-station air quality data |
| Open-Meteo API | Atmospheric pollution data |
| Git & GitHub | Version control and project hosting |

---

## 📁 Project Structure

```text
air-quality-tracker/
│
├── app.py
│
├── extract.py
├── extract_openmeteo.py
│
├── validate.py
├── validate_multi_station.py
│
├── database.py
│
├── analyze.py
├── analyze_multi_station.py
├── analyze_openmeteo.py
│
├── discover_pollutants.py
├── check_latest.py
│
├── air_quality_raw.csv
├── air_quality_clean.csv
│
├── air_quality_multi_station_raw.csv
├── air_quality_multi_station_clean.csv
│
├── air_quality_openmeteo_raw.csv
│
├── air_quality.db
│
├── openmeteo_descriptive_statistics.csv
├── openmeteo_missing_values.csv
├── openmeteo_correlation_matrix.csv
│
├── pm25_station_comparison.png
├── pm25_multi_station_trends.png
├── openmeteo_pm25_trend.png
├── openmeteo_pm10_trend.png
├── openmeteo_correlation_heatmap.png
│
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: The exact files may vary depending on the latest generated datasets and analysis outputs.*

---

## 🚀 Installation & Setup

### Prerequisites

- Python installed
- Git
- Internet connection for API data collection

### 1. Clone the repository

```bash
git clone https://github.com/your-username/EcoAir-Air-Quality-Tracker.git
```

### 2. Navigate to the project folder

```bash
cd EcoAir-Air-Quality-Tracker
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
.venv\Scripts\activate.bat
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the dashboard

```bash
streamlit run app.py
```

The dashboard will open locally in your browser.

---

## 📦 Dependencies

Project dependencies are listed in `requirements.txt`.

The main libraries include:

```text
pandas
numpy
pydantic
requests
streamlit
plotly
matplotlib
```

---

## 📷 Dashboard Preview

The dashboard provides interactive visualizations for air quality analysis, pollutant trends, monitoring station comparisons, and environmental data exploration.

![EcoAir Dashboard](dashboard_screenshot.png)

---

## 🎥 Project Demo

A short demonstration video showcases the EcoAir dashboard and its main features, including visualizations, station comparisons, and interactive data exploration.

---

## 🌍 Project Significance

EcoAir demonstrates how data science and programming techniques can be applied to environmental monitoring.

By combining API-based data collection, validation, structured storage, statistical analysis, and interactive visualization, the project provides a practical workflow for exploring air quality data.

It also highlights the importance of data quality, exploratory analysis, and visualization in making environmental datasets more understandable.

---

## 👩‍💻 Academic Project

**Course:** Programming for AI  
**Project:** ETL + EDA Pipeline  
**Project Theme:** Air Quality & Public Health Tracker (Eco-Tech)  
**Focus:** Sensor Data Validation & Geospatial Analysis

---

## 📄 License

This project was developed for academic and educational purposes.
