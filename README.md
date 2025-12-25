# Macro-Economic Energy Demand Sensing Engine

A Time Series analysis project that predicts future global energy demand based on macroeconomic indicators (primarily GDP Growth) using statistical (VAR) and machine learning (XGBoost) approaches. Includes an interactive scenario-planning dashboard.

## Features

- **Data Pipeline:** Fetches and merges World Bank indicators and local datasets.
- **EDA & Stats:** Stationarity (ADF), Granger causality, and correlation analyses.
- **Modeling:** Compares VAR baseline and XGBoost regressor for forecasting.

## Project Structure

- `data_loader.py`: Ingests raw data and fetches missing indicators.
- `eda.py`: Performs exploratory analysis and feature engineering (lags).
- `model.py`: Trains and evaluates VAR and XGBoost models; saves outputs.

## Results

- **VAR Model MAPE:** (see `model.py` output)
- **XGBoost Model MAPE:** (see `model.py` output)
 - See `img/model_comparison.svg` for a visual comparison of forecasts.

## Figures

- **Landing Page:** ![Landing Page](img/landing.png) — First look at the app: interactive energy-forecasting dashboard UI where users can adjust GDP scenarios and view predicted Energy Use.

- **Heatmap (Correlation):** ![Correlation Heatmap](img/heatmap.png) — Correlation matrix and lag relationships used in EDA.

- **Model Comparison:** ![Model Comparison](img/model_comparison.png) — Forecast comparison between VAR and XGBoost.

- **CO2 Forecast:** ![CO2 Forecast](img/CO2-Forecast.png)

  The "straight line" is happening because the model is relying almost entirely (~98%) on `CO2_Emissions` to predict `Energy_Use`. Since the app holds CO2 emissions constant for the future, the Energy prediction remains constant, regardless of the GDP slider.