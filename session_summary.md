# Session History: Global Energy Demand Forecasting Project

**Date:** December 25, 2025
**Role:** Senior Python Developer / Data Scientist / ML Engineer
**Project:** Time Series Pipeline & Scenario Planner

---

## 1. Project Overview
The goal was to build a complete data pipeline to predict global energy demand using historical World Bank data and economic indicators.

### Key Milestones:
- **Data Ingestion:** Automated fetching of WDI features via API.
- **Statistical Analysis:** ADF for stationarity and Granger Causality for feature validation.
- **Modeling:** Comparative analysis between VAR (Statistical) and XGBoost (ML).
- **Deployment:** A Streamlit-based "What-If" scenario planner.

---

## 2. Code Artifacts

### A. Data Loader (`data_loader.py`)
Fetches CO2, GDP, and Industry data from World Bank and merges with local "Wide Format" CSV.
- **Features:** Automated indicator mapping, linear interpolation for missing values.

### B. Exploratory Data Analysis (`eda.py`)
- **Stationarity:** ADF tests on numeric features.
- **Causality:** Validated that GDP Growth Granger-causes Energy Use (lags 1-3).
- **Feature Engineering:** Recursive lag generation (Lag 1 & 2).

### C. Predictive Modeling (`model.py`)
- **Split:** Chronological (1990-2015 Train / 2016-2019 Test).
- **Models:** statsmodels VAR vs. XGBoost Regressor.
- **Evaluation:** MAPE calculation and comparison plotting.

### D. Interactive Dashboard (`app.py`)
- **Framework:** Streamlit + Plotly.
- **Feature:** Recursive forecasting logic allowing users to simulate future Energy Demand by sliding GDP Growth targets.

---

## 3. Environment & Setup
- **OS:** macOS (Apple Silicon)
- **Environment:** `uv` managed Python 3.12.7 venv.
- **Key Fix:** Installed `libomp` via Homebrew to support XGBoost runtime on Mac.
- **Command to Run App:** `streamlit run app.py`

---

## 4. GitHub Readiness
- `requirements.txt`: Consolidated dependencies.
- `.gitignore`: Configured to exclude `.venv`, data artifacts, and system files.
- `README.md`: Professional documentation for the repository.

---
*End of Session Summary*
